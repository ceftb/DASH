/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.detergent;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintStream;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;

import jpl.Compound;
import jpl.Query;
import jpl.Term;
import jpl.Variable;

/**
 * Basic Deter agent
 * @author blythe
 * 
 * NOTE: to run from eclipse, edit the native library location of your jpl.jar library file to point to the same place as the library path below.
 * otherwise do java -cp lib/jpl.jar -Djava.library.path=/opt/local/lib/swipl-5.10.4/lib/i386-darwin10.7.0 edu.isi.detergent.Detergent
 *
 */
public class Detergent {
	
	public String name = "top";
	public String prologRoot = "lib/logic";
	public String[] prologFiles = {"agentGeneral.pl", "agentWorker.pl", "agentWorker_bootStrap.pl"};  // usually over-written by command line arguments
	public String commsHost = "localhost";
	public int commsPort = 4789;
	public long stepPause = 10, minStepPause = 10, maxStepPause = 2000; // pause 1/100 second between actions
	public List<String>output = new LinkedList<String>(), actions = new LinkedList<String>();
		
	// List of any agents that are spawned by this one. They currently live in the same image.
	public List<Agent>children = new ArrayList<Agent>();
	
	Cognition cognition = null;
	Comms comms = null;
	int id = -1;
	DFrame dFrame = null;
	public DAgent dAgent = null;
	public String currentState = null;
	public int maxSteps = -1; // if > 0, agent will be run for this many steps and then quit.
	
	public static PrintStream out = System.out;
	
	public Detergent(String[] arguments) {
		List<String>files = new LinkedList<String>(), facts = new LinkedList<String>();
		for (int i = 0; i < arguments.length; i++) {
			String arg = arguments[i];
			if (arg.equals("-gfx")) {
				printOut("Starting graphics");
				dFrame = new DFrame(this);
			} else if (arg.equals("-id")) {
				facts.add("id("+arguments[++i]+")");
			} else if (arg.equals("-maxSteps")) {
				maxSteps = Integer.parseInt(arguments[++i]);   // throw the exception so the agent bombs rather than running forever for a malformed number.
			} else {  // anything unrecognized is assumed to be the name of a prolog file sent to the cognitive module
				files.add(arg);
			}
		}
		if (arguments == null || arguments.length == 0)
			arguments = this.prologFiles; // default if none given
		cognition = new Cognition(prologRoot, files, facts);
		comms = new Comms();
	}
	
	public static void main(String[] args) {
		new Detergent(args).run();
	}

	/**
	 * Run a basic action loop for the agent
	 */
	void run() {
		id = -1;
		try {
			cognition.getInt("id");
		} catch (Exception pe) {
			printOut("Agent prolog does not specify an id. Using " + id);
		}
		try {
			commsHost = cognition.getString("commsHost");
		} catch (jpl.PrologException pe) {
			printOut("Agent prolog does not specify a comms host. Using " + commsHost);
		}
		println("Connecting to " + commsHost + " with id " + id);  // If this wording is changed the reader for sub-process agents must also be changed
		comms.connect(id, commsHost, commsPort);  // pass in the user id to announce it to the central server
		if (!comms.isConnected)
			printOut("Unable to connect to communications host, continuing without communication with other agents.");
		// Get the next action, pretend to perform it, sleep.
		int step = 0, internalTick = 0;
		while (maxSteps <= 0 || maxSteps >= step) {
			step++;
			// Print the state out only if it changes, to reduce printout
			String state = null;
			try {
				state = cognition.getString("state");
			} catch (jpl.PrologException pe) {
				// don't crash if the agent doesn't set a state
			}
			if (state != null && !state.equals(currentState)) {  // state is null if the agent doesn't set a state
				currentState = state;
				if (dAgent != null)
					dAgent.setState(state);
				else
					println("state is " + state);
			}
			// Find out the variables the cognitive part wants to report (inside loop since might change)
			try {
			Term vars = cognition.getQueryResult(new Query("uIPredicates", new Term[] {new Variable("X")}), "X");
			Term[] terms = jpl.Util.listToTermArray(vars);
			//printOut("UI Predicate vars are " + vars + ", first is " + (terms != null && terms.length > 0 ? terms[0] : "none"));
			showPredicates(terms);
			} catch (jpl.PrologException pe) {
				// don't crash if there are no ui predicates
			}
			Action a = cognition.getNextAction();
			// Adjust step pause to sleep longer if there's no action, less time if there is action
			if (a == null || a.name.equals("doNothing")) {
				if (stepPause * 2 < maxStepPause)
					stepPause *= 2;
			} else if (a.name.equals("pause")) {
				stepPause = Integer.parseInt(a.arguments[0]);
				printOut("Pausing " + stepPause + " milliseconds");
			} else {
				println("Got action " + a);
				actions.add(a.toString());
				if (dAgent != null) {
					dAgent.updateLastAction(actions.size(), a.toString());
				}
				if (stepPause > 2 * minStepPause)
					stepPause /= 2;
			} 
			if (dAgent != null) {
				// Read the S1 and S2 data if any, since this is not a sub-agent
				Query q = new Query("allFiredRules", new Term[] {new Variable("Rules")});
				Term lineTerm = cognition.getQueryResult(q, "Rules");
				if (lineTerm != null)
					dAgent.showS1Rules(lineTerm.name());
				q = new Query("modelSummary", new Term[] { new Variable("Summary") } );
				lineTerm = cognition.getQueryResult(q, "Summary");
				if (lineTerm != null) {
					//System.out.println("Sending " + lineTerm + " to S2 processing");
					//dAgent.showS2Conclusion(lineTerm.name());
					dAgent.processS2Messages(lineTerm.name());
				}
			}
			try {
				Thread.sleep(stepPause);
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
			if (a == null) {
				println("Null action returned, entering trace");
				cognition.setTrace();
				cognition.getNextAction();
			}
			Object result = -1;
			if (a != null) {
				result = a.perform(this);
				if (!a.name.equals("doNothing"))
					println("Result from performing " + a + " is " + result);
			}
			int time = comms.isConnected ? comms.getTick() : internalTick++;  // keep ticking forward if we do not have the central server
			// Check for messages
			String[] messages = comms.checkMessages();
			if (messages != null) {
				for (int i = 1; i < messages.length; i++) {  // first element is the number of messages
					// Should really record that this is a message and allow the agent
					// to process the contents as beliefs, but just surgically inserting the fact for now.
					println("Got message: " + messages[i]);
					cognition.addFact(messages[i]);
				}
			}
			// tell the cognitive part how the action went.
			if (a != null)
				cognition.addFact("result", new Object[] {a.t, result, time});
		}
	}

	private void println(String string) {
		// TODO Auto-generated method stub
		printOut(string);
		output.add(string);
		if (dAgent != null) dAgent.updateOutputs();
	}
	
	/**
	 * Simple printing, to be subclassed
	 * @param string
	 */
	void printOut(String string) {
		out.println(string);
	}

	/**
	 * Get the values and show them on the dashboard.
	 * This is done by printing them out, since the agent runs in a separate process from the dashboard unless it is the top agent.
	 * @param terms
	 */
	String predicateString = "";
	public void showPredicates(Term[] terms) {
		String currentPredicateString = "", separator = "||";
		for (Term t: terms) { // each term is a compound of predicate and arity.
			Term[] args = ((Compound)t).args();
			String pred = args[0].name();
			int arity = args[1].intValue();
			if (t.name().equals("slider")) {
				Term valueTerm = cognition.getTerm(pred);
				if (!"".equals(currentPredicateString))
					currentPredicateString += separator;
				currentPredicateString += t + "%" + valueTerm;
			} else if (arity == 1) { 			// Just deal with arity 1 for now
				Term valueTerm = cognition.getTerm(pred);
				//values.setText(pred + " = " + valueTerm);
				if (!"".equals(currentPredicateString))
					currentPredicateString += separator;
				// detect a list and print appropriately
				try {
					Term[] elements = valueTerm.toTermArray();
					currentPredicateString += pred + " = [";
					for (int i = 0; i < elements.length; i++) {
						currentPredicateString += elements[i] + (i == elements.length - 1 ? "" : ", ");
					}
					currentPredicateString += "]";
				} catch (Exception e) {  // Not sure what the exception looks like yet.
					printOut("Show predicates list exception: " + e);
					currentPredicateString += pred + " = " + valueTerm;
				}
			} else {
				printOut("Term " + t + " has pred " + pred + " with arity " + arity);
			}
		}
		// Only print the current predicate string if it has changed, to reduce chatter.
		if (!currentPredicateString.equals(predicateString)) {
			if (dAgent == null)
				printOut("ShowPred: " + currentPredicateString);
			else
				dAgent.setPreds(currentPredicateString);
			predicateString = currentPredicateString;
		}
	}


	static class StreamGobbler extends Thread
	{
		InputStream is;
		String type;
		OutputStream os;
		String[] filters = null;
		public boolean filterMatched = false;
		public List<String>output = new LinkedList<String>();

		StreamGobbler(InputStream is, String type)
		{
			this(is, type, null, null);
		}
		
		StreamGobbler(InputStream is, String type, String[] filters)
		{
			this(is, type, null, filters);
		}
		
		StreamGobbler(InputStream is, String type, OutputStream redirect, String[] filters)
		{
			this.is = is;
			this.type = type;
			this.os = redirect;
			this.filters = filters;
		}

	    public void run()  {
	    	try {
	    		PrintWriter pw = null;
	    		if (os != null)
	    			pw = new PrintWriter(os);

	    		InputStreamReader isr = new InputStreamReader(is);
	    		BufferedReader br = new BufferedReader(isr);
	    		String line=null;
	    		while ( (line = br.readLine()) != null) {
	    			// check it matches a filter
	    			boolean matched = false;
	    			if (filters == null) 
	    				matched = true;
	    			else 
	    				for (String filter: filters) {
	    					if (line.contains(filter)) {
	    						matched = true;
	    						break;
	    					}
	    				}
	    			if (matched) {
	    				filterMatched = true;
	    				if (pw != null)
	    					pw.println(line);
	    				System.out.println(type + "> " + line);
	    				output.add(line);
	    				agentAction(line);
	    			}
	    		}
	    		if (pw != null)
	    			pw.flush();
	    	} catch (IOException ioe)
	    	{
	    		ioe.printStackTrace();  
	    	}
	    }
	    
	    // Dummy method to be overwritten.
	    public void agentAction(String line) {}
	}
	
	/*
	 * For sub-agents.
	 */
	static class Agent {
		Detergent parent;
		StreamGobbler error, output;
		Process process;
		public String name;
		public int id = -1;  // id for comms
		public DAgent dAgent = null;
		List<String>actions = new LinkedList<String>();
		
		Agent(String name, Process process, Detergent detergent) {
			this.name = name;
			this.process = process;
			parent = detergent;
		}
		
		public void updateLastAction(String substring) {
			actions.add(substring);
			dAgent.updateLastAction(actions.size(), substring);
		}
		
		public void updateNewOutput() {
			dAgent.updateOutputs();
		}
	}

	// Can be called from an action allowing an agent to spawn a new agent.
	// Generally should only be used by the group agent.
	// NB. Cannot run a new agent in the same java image because we can only control one prolog instance and the
	// prolog code wasn't set up to run multiple agents.
	public void spawnChild(String agentFileName)  {
		String[] args = new String[1];
		args[0] = agentFileName + ".pl"; 
		//final Detergent child = new Detergent(args);
		//child.name = agentFileName;
		// Needs to be in a separate thread
		Runtime r = Runtime.getRuntime();
		String bash = "/bin/bash";
		String[] command = {bash, "-l", "-c", "./bot.sh " + agentFileName};

		try {

			Process p = r.exec(command);
			final Agent child = new Agent(agentFileName, p, this);
			children.add(child);
			if (dFrame != null) dFrame.addChild(child);
			
			StreamGobbler errorGobbler = new StreamGobbler(p.getErrorStream(), agentFileName + "(e) ");  
			child.error = errorGobbler;
			// any output?
			//String[] filters = {"parse error"};
			StreamGobbler outputGobbler = new StreamGobbler(p.getInputStream(), agentFileName + " ", null) {
				public void agentAction(String line) {
					// Look for lines about actions and keep track of them
					if (line.startsWith("Got action")) {
						child.updateLastAction(line.substring(11));
					} else if (line.contains("state is")) {
						child.dAgent.setState(line.substring(line.indexOf("state is")+9));
					} else if (line.startsWith("ShowPred:")) {
						child.dAgent.setPreds(line.substring(10));
					} else if (line.startsWith("Connecting to") && line.contains("with id")) {  // read the id of the child agent so we can send messages
						child.id = Integer.parseInt(line.substring(line.indexOf("with id") + 8));
					} else if (line.startsWith("All fired rules"))
						child.dAgent.showS1Rules(line);
					else if (line.startsWith("S2:"))
						child.dAgent.showS2Conclusion(line);
					else if (line.startsWith("Derived"))
						child.dAgent.processS1Conclusion(line);
					else if (line.startsWith("Utility"))
						child.dAgent.addUtility(line);
					else if (line.contains("comparing"))
						child.dAgent.clearUtilities();
					else if (line.contains("Project"))
						child.dAgent.processProject(line);
					else if (line.contains("Trigger"))
						child.dAgent.processProject(line);
					child.updateNewOutput();
				}

			}; // show all output 
			child.output = outputGobbler;
			
			// kick them off
			errorGobbler.start();
			outputGobbler.start();
			
			// any error??? Don't wait for the end in this version (this code was from blackboard)
			/*
			int exitVal = p.waitFor();
			printOut("ExitValue: " + exitVal);
			if (outputGobbler.filterMatched) {
				printOut("Error matched");
				for (String line: errorGobbler.output)
					printOut(line);
			}
			//return processOutputToKP(outputGobbler.output, ex);
			//return outputGobbler.output;
           */

		} catch (IOException e) {
			printOut("Problem running sub agent");
			e.printStackTrace();
		} 
	}

	
}

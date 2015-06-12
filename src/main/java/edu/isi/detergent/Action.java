/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.detergent;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;

import jpl.Atom;
import jpl.Compound;
import jpl.Term;
import jpl.Util;

/**
 * An action that the agent can take
 * @author blythe
 *
 */
public class Action {
	public String name = null;
	public String[] arguments = {};
	public Term t = null;
	public static String lastActionName = null;
	
	public Action(String name, String[] arguments, Term t) {
		this.name = name;
		this.arguments = arguments;
		this.t = t;
	}
	
	public String toString() {
		String result = name + "(";
		for (String arg: arguments)
			result += arg + ",";
		return result + ")";
	}

	public Object perform(Detergent detergent) {
		// Do predefined tasks
		if ("startAgent".equals(name)) {
			detergent.printOut("Starting agent " + arguments[0]);
			detergent.spawnChild(arguments[0]);
		} else if (name.equals("commPhone_outCall")) {
			detergent.printOut("Phoning " + arguments[0] + " with message " + arguments[1]);
			String result = detergent.comms.sendMessage(Integer.parseInt(arguments[0]), arguments[1]);
			lastActionName = "commPhone_outCall";
			if (result.equals("ok"))
				return 1;
			else
				return 0;
		} else if (name.equals("commGet")) {
			String value = detergent.comms.getValue(arguments[0]);
			detergent.printOut("Querying shared variable " + arguments[0] + ": value is " + value);
			return value;
		} else if (name.equals("commSet")) {
			detergent.printOut("Setting shared variable " + arguments[0] + " to " + arguments[1]);
			return detergent.comms.setValue(arguments[0], arguments[1]);
		} else if ("doNothing".equals(name)) {
			detergent.printOut(".");
		} else if ("computer_applicationOpen".equals(name)) {  // make this fail the first time to test the resilience of the planning code
			if ("computer_applicationOpen".equals(lastActionName) ) {
				detergent.printOut("Succeeding at " + this);
				return 1;
			} else {
				detergent.printOut("Failing at " + this);
				lastActionName = "computer_applicationOpen";
				return 0;
			}
		} else if ("ms".equals(name)) {  // a wrapper to be sent eventually to a metasplot interface, for now simulated
			// The first argument should be another prolog term with the actual action
			Term action = t.args()[0];
			System.out.println("Running metasploit action on " + action);
			// For now, say bannerGrabber succeeds on any machine with windows xp sp2 and hPOpenView also succeeds.
			if ("bannerGrabber".equals(action.name())) {
				return "macOS10"; // since a simple string. I'll convert the windows example to be the same.
			} else
				return 1;
		} else if ("check".equals(name)) {
			return simulatorCheckStub();
		} else if ("set".equals(name)) {
			return simulatorSetStub();
		} else if ("checkSystem1".equals(name)) {
			return emoCogWrapper();
//		} else if ("logIn".equals(name) || (name != null && name.contains("Password"))) {  // dumb hack
//			return 1;   // avoid the generic result to delete 'loggedIn'.
		} else {
            String value = detergent.comms.submitAction(jpl.Term.toString(new Term[] {this.t}));
			detergent.printOut("Performing " + jpl.Term.toString(new Term[] {this.t}));
			detergent.printOut("Also, submitting action to server so that it may generate appropriate observables.\n");
            return value;
		}
		lastActionName = name;
		//return successValue();
		// Test out adding changes to the world by returning a list of commands including to delete that the agent is logged in. 
		// This is currently specific to the 
		// BCMA agent and we either need a way to either test for the agent involved or should make this the general approach
		return Util.termArrayToList(new Term[]{new Compound("del", new Term[]{new Atom("loggedIn")})});
		// can we return the empty list? Yup.
		//return Util.termArrayToList(new Term[]{});
	}
	
	
	/**
	 * This stub simulator has values specific to Spraragen's nuclear plant example.
	 */
	Object[][] values = {{"coolantTemperature", 800},
			 {"waterPressure", 8},
			 {"emergencySealantSpray", "off"}
	};
	static HashMap<String,Object> simulatorValue = new HashMap<String,Object>();
	
	public Object simulatorCheckStub() {
		//System.out.println("Running stub code to check a value from the simulator");
		// Index into a set of pre-stored values
		runSimulatorStub();
		if (simulatorValue.containsKey(arguments[0]))
			return simulatorValue.get(arguments[0]);
		return -1;
	}
	
	public int simulatorSetStub() {
		//System.out.println("Running stub code to set a value in the simulator");
		runSimulatorStub();
		simulatorValue.put(arguments[0], arguments[1]);  // WARNING - THIS WILL ALWAYS SET THE VALUE AS A STRING
		// 1 means success, 0 means failure. The object being set is given by the string arguments[0].
		return 1;
	}
	
	/**
	 * Gets called once for every set or check action and maintains some basic evolution.
	 */
	public void runSimulatorStub() {
		// Initialize the values if necessary
		if (simulatorValue.isEmpty())
			for (Object[] pair: values)	
				simulatorValue.put((String)pair[0], pair[1]);
		else
			simulatorValue.put("empty", "no");
		// If the temperature is high but either the emergency pump or the emergency bypass pump are on, set the temperature to normal.
		if ("on".equals(simulatorValue.get("emergencyBypassPump")) ||  "on".equals(simulatorValue.get("emergencyPump")))
			simulatorValue.put("coolantTemperature", 375);
		System.out.println("Stub simulator values are " + simulatorValue);
	}
	
	private Term emoCogWrapper() {
		// emo Cog returns an alternating list of terms and strengths as java doubles. This wrapper
		// packages them into a linked-list-structured prolog predicate, because I'm having trouble passing prolog lists.
		List<Object>wms = emoCogStub();
		Term result = new Atom("end");
		if (wms != null)
			for (int i = 0;	 i < wms.size(); i += 2)
				result = new Compound("nodeList", new Term[]{(Term)wms.get(i), new jpl.Float((Double) wms.get(i+1)), result});
		return result;
	}
	
	private List<Object> emoCogStub() {
		// The current goal is available as arguments[0]. Emocog should return a list of alternating terms and strengths.
		List<Object>result = new LinkedList<Object>();
		result.add(new Atom("pipeRupture"));
		result.add(0.6);    // try 0.4 to get different behavior from the cognitive part.
		return result;
	}


	
	/**
	 * If we are running this action as a stub, compute whether it succeeds. This allows testing random or other failures and testing
	 * the resilience of the agent.
	 * @return
	 */
	public int successValue() {
		// Just say it succeeded for now.
		return 1;
	}
}

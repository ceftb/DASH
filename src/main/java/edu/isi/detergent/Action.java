/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.detergent;

import jpl.Atom;
import jpl.Compound;
import jpl.Term;

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
		}  else if ("check".equals(name)) {
			return simulatorStub();
		} else if ("checkSystem1".equals(name)) {
			return emoCogStub();
		} else {
			detergent.printOut("Performing " + this);
		}
		lastActionName = name;
		return successValue();
	}
	
	public Object simulatorStub() {
		System.out.println("Running stub code to check a value from the simulator");
		// Index into a set of pre-stored values
		Object[][] values = {{"coolantTemperature", 800},
							 {"waterPressure", 8},
		};
		for (Object[] pair: values)
			if (pair[0].equals(arguments[0]))
				return pair[1];
		return -1;
	}
	
	private Object emoCogStub() {
		// For now, emoCog ignores the input (which will be a goal but is not yet) and returns a list of 'node' terms
		Term fact = new Atom("pipeRupture"), node = new Compound("node", new Term[]{fact, new jpl.Float(0.6)});
		return new Term[]{fact};
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

/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.detergent;

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
		} else {
			detergent.printOut("Performing " + this);
		}
		lastActionName = name;
		return successValue();
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

/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.detergent;

import java.util.Hashtable;
import java.util.List;

import jpl.Atom;
import jpl.Compound;
import jpl.Integer;
import jpl.Query;
import jpl.Term;
import jpl.Variable;
import jpl.Util;

public class Cognition {

	public Cognition(String prologRoot, List<String>prologFiles, List<String> facts) {
		loadFiles(prologRoot, prologFiles, facts);
	}

	private void loadFiles(String prologRoot, List<String> files, List<String>facts) {
		// First load the files
		for (String file: files) {
			Query q = new Query("consult", new Term[] {new Atom(prologRoot + "/" + file)});
			System.out.println( "consult " + (q.hasSolution() ? "succeeded" : "failed"));
			q.rewind();
		}
		// Then add the dynamic facts, e.g. id(<n>), being loaded into the initial cognitive state
		for (String fact: facts)
			addFact(fact);
	}
	
	/**
	 * Read the value of the predicate and assumes it is an integer.
	 * Isolates the rest of the code from prolog terms and integers.
	 * @param predicate The name of the predicate
	 * @return integer value
	 * Throws an error if the term is not defined or is not an integer.
	 */
	protected int getInt(String predicate) {
		jpl.Integer t = (jpl.Integer)getTerm(predicate);
		return t.intValue();
	}
	
	/**
	 * Read a string from a prolog predicate.
	 * Currently used for comms host.
	 * @param predicate
	 * @return
	 */
	protected String getString(String predicate) {
		Term t = getTerm(predicate);
		if (t == null)
			return null;
		return t.name();
	}
	
	protected Term getTerm(String predicate) {
		Query idQuery = new Query(predicate, new Term[] {new Variable("X")});
		return getQueryResult(idQuery, "X");
	}
	
	/**
	 * Get the next action for the agent. Encapsulates the prolog piece.
	 * @return
	 */
	protected Action getNextAction() {
		Query doQuery = new Query("do", new Term[] {new Variable("Action")});
		Term t = getQueryResult(doQuery, "Action");
		if (t != null) {
			String[] args = new String[t.args().length];
			for (int i = 0; i < args.length; i++)
				args[i] = t.args()[i].toString();
			return new Action(t.name(), args, t);  // The action stores the prolog term mainly so we can pass it back with the result.
		}
		else {
			return null;
		}
	}
	
	protected Term getQueryResult(Query query, String varName) {
		/*Term result = null;
		while (query.hasMoreSolutions() ) {
			Hashtable solution = query.nextSolution();
			if (result == null)  // bind to the first result returned from prolog, but go through all the others to finish off the query.
				result = (Term)solution.get(varName);
		}
		return result;*/
		// Replaced with simpler approach that doesn't force prolog to backtrack, which sometimes made the cognitive part
		// assume there had been a failure.
		@SuppressWarnings("rawtypes")
		Hashtable solution = query.oneSolution();
		if (solution == null)
			return null;
		return (Term)solution.get(varName);
	}
	
	/**
	 * Add a fact to the prolog database. Compound arguments currently use prolog terms as arguments, which beaks the encapsulation.
	 * @param predicate
	 * @param args
	 * @return
	 */
	protected void addFact(String predicate, Object[] args) {
		Term[] termArgs = new Term[args.length];
		for (int i = 0; i < args.length; i++) {
			if (args[i] instanceof String)
				termArgs[i] = new Atom((String)args[i]);
			else if (args[i] instanceof java.lang.Integer) {
				termArgs[i] = new Integer(((java.lang.Integer)args[i]).longValue());
			} else if (args[i] instanceof Term) 
				termArgs[i] = (Term)args[i];
			else {
				termArgs[i] = new Atom(args[i].toString());
			}
		}
		addFact(new Compound(predicate, termArgs));
	}

	protected void addFact(String string) {
		addFact(Util.textToTerm(string));
	}

	private void addFact(Term term) {
		Query assertQuery = new Query("assert", new Term[]{term});
		//System.out.println("asserting:   " + assertQuery); // leaving out for now
		assertQuery.allSolutions();
		assertQuery.rewind();
	}

	public boolean setTrace() {
		Query q = new Query("trace");
		return !(q.oneSolution() == null);
	}

}

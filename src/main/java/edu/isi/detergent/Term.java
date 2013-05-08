/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.detergent;

import java.util.LinkedList;
import java.util.List;

// Some classes for parsing prolog terms. Atoms are terms with arity 0.
public class Term {
	String predicate;
	int arity;
	boolean infix = false;
	List<Term>subTerms = null;
	
	String[] infixOps = {"<", ">", "<=", ">=", "is"};  // The parser needs to know some infix operators
	
	public Term(String predicate, List<Term>subTerms) {
		this.predicate = predicate;
		this.subTerms = subTerms;
		arity = (subTerms == null ? 0 : subTerms.size());
	}
	
	/**
	 * Parse the subgoal string into a list of subgoals. A subparse consists of a character length and a set of terms.
	 */
	static class SubParse {
		int charLength = 0;
		Term term = null;
		List<Term>subgoals = null;
		public SubParse(int l, Term t) {charLength = l; term = t;}
		public SubParse(int l, List<Term> ts) {charLength = l; subgoals = ts;}
		public Term lastGoal() {  // convenience
			if (subgoals != null && !subgoals.isEmpty())
				return subgoals.get(subgoals.size()-1);
			else
				return null;
		}
	}
	
	public static List<Term> parseTerms(String data) {
		SubParse s = parseTermListInt(data, "");
		return s.subgoals;
	}
	
	static SubParse parseTermListInt(String data, String indent) {
		// recursively call parseTermInt on a list of terms separated by commas and string together
		//System.out.println(indent + "Parsing list " + data);
		SubParse result = new SubParse(0,new LinkedList<Term>()), sub = parseTermInt(data, indent + "  ");
		//String original = data;
		while (sub != null) {
			result.charLength += sub.charLength;
			result.subgoals.add(sub.term);

			int start = sub.charLength;
			// walk past spaces and commas to the next predicate (or the end)
			while (start < data.length() && (data.charAt(start) == ' ' || data.charAt(start) == ',' || data.charAt(start) == ')'))
				start++;
			if (start < data.length()) {
				data = data.substring(start);  // will need some adjustment for internal spaces
				sub = parseTermInt(data, indent + "  ");
			} else {
				sub = null;
			}
		}
		//System.out.println(indent + "Parsed list " + original + " into " + result.subgoals);
		return result;
	}
	
	private boolean isInfixOp() {
		if (infix)
			return true;
		for (String infixOp: infixOps)
			if (infixOp.equals(predicate))
				return true;
		return false;
	}

	public static Term parseTerm(String data) {
		SubParse s = parseTermInt(data, "");
		return s.term;
	}
	
	static SubParse parseTermInt(String data, String indent) {
		// parse a term from the string
		if (data == null || data.length() == 0)
			return null;
		//System.out.println(indent + "Parsing term " + data);
		int predStart = 0;
		while (predStart < data.length() && data.charAt(predStart) == ' ')
			predStart++;  // move past any space.
		int predEnd = predStart;
		while (predEnd < data.length() && data.charAt(predEnd) != '(' && data.charAt(predEnd) != ')' && data.charAt(predEnd) != ',' && data.charAt(predEnd) != ' ')
			predEnd++;
		String predicate = data.substring(predStart,predEnd);
		SubParse firstTerm;
		if (predEnd < data.length() && data.charAt(predEnd) == '(') {
			SubParse args = parseTermListInt(data.substring(predEnd+1, findCloseParen(data,predEnd)), indent + "  ");
			if (args != null) {
				Term t = new Term(predicate, args.subgoals);
				//System.out.println(indent + "Parsed term " + data + " into " + t);
				firstTerm = new SubParse(data.indexOf(')',predEnd+1), t);
			} else {
				firstTerm = new SubParse(predEnd + 1, new Term(predicate, null));
			}
		} else {
			firstTerm = new SubParse(predEnd + 1, new Term(predicate, null));
		}
		if (predEnd < data.length() && data.charAt(predEnd) == ' ') {  // See if the next term is an infix operator.
			//System.out.println(indent + " checking for infix at " + data);
			SubParse next = parseTermInt(data.substring(predEnd+1), indent + " ");
			if (next != null && next.term.isInfixOp()) {
				// try to gather up the second term and return the whole parse
				SubParse secondTerm = parseTermInt(data.substring(predEnd+1+next.charLength), indent + "  ");
				if (secondTerm != null) {
					// fix up the second term with the first and third as subterms
					next.term.infix = true;
					next.term.arity = 2;
					next.term.subTerms = new LinkedList<Term>();
					next.term.subTerms.add(firstTerm.term);
					next.term.subTerms.add(secondTerm.term);
					//System.out.println(indent + "Parsed term " + data + " into " + next.term);
					return new SubParse(predEnd + 1 + next.charLength + secondTerm.charLength, next.term);
				}
			}
		}
		//System.out.println(indent + "Parsed term " + data + " into " + firstTerm.term);
		return firstTerm;
	}

	
	private static int findCloseParen(String data, int predEnd) {
		int depth = 0;
		for (int i = predEnd + 1; i < data.length(); i++) {
			if (data.charAt(i) == ')') {
				if (depth == 0)
					return i;
				else
					depth--;
			} else if (data.charAt(i) == '(') {
				depth++;
			}
		}
		return data.length();
	}

	public String toString() {
		String result = "";
		if (subTerms != null && (!infix || arity != 2)) {
			for (int i = 0; i < subTerms.size(); i++) {
				result += subTerms.get(i) + (i + 1 < subTerms.size() ? "," : "");
			}
			return predicate + "(" + result + ")";
		} else if (subTerms != null && infix) {
			return subTerms.get(0) + " " + predicate + " " + subTerms.get(1);
		} else {
			return predicate;
		}
	}
	
	public String signature() {
		return predicate + "/" + arity;
	}

	public Term variablize() {
		if (arity == 0)
			return this;
		boolean hasNonVariableArg = false;
		Term result = this;
		for (Term sub: subTerms)
			if (sub.arity != 0 || !Character.isUpperCase(sub.predicate.charAt(0))) {
				hasNonVariableArg = true;
				break;
			}
		if (hasNonVariableArg) {
			result = new Term(predicate, new LinkedList<Term>(subTerms));
			for (int i = 0; i < result.arity; i++) {
				if (result.subTerms.get(i).arity != 0 || !Character.isUpperCase(result.subTerms.get(i).predicate.charAt(0)))
					result.subTerms.set(i, new Term("V" + (i+1), null));
			}
		}
		return result;
	}
}


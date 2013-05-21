/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.detergent;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Component;
import java.awt.GridLayout;
import java.awt.event.ActionListener;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.NoSuchElementException;

import javax.swing.JButton;
import javax.swing.JFileChooser;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTabbedPane;
import javax.swing.JTextArea;
import javax.swing.JTree;
import javax.swing.event.TreeModelEvent;
import javax.swing.event.TreeModelListener;
import javax.swing.filechooser.FileFilter;
import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.DefaultTreeCellRenderer;
import javax.swing.tree.TreeNode;



/**
 * A JFrame that allows viewing and editing the agent's goal and rule structures.
 * Saves and maintains a .agent file and from it a .pl file.
 * @author blythe
 *
 */
public class Wizard {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	String name = "top";
	String prologRoot = "lib/logic";
	List<GoalLink>goalLinks = new LinkedList<GoalLink>();
	List<Rule>rules = new LinkedList<Rule>();
	JPanel goalPanel = null, rulePanel = null, modelPanel = null;
	GoalTree goalTree = null;
	DynamicTree ruleTree = null, modelTree = null;
	String baseRules = "";  // not processed yet, so a string
	HashMap<String,Goal>goals = new HashMap<String,Goal>();
	HashMap<String,PrologGoal>prologGoals = new HashMap<String,PrologGoal>();
	String[] mentalModels = null;
	HashMap<String, List<ModelOperator>>addSets = new HashMap<String, List<ModelOperator>>();
	List<UtilityRule>utilityRules = new LinkedList<UtilityRule>();
	private Detergent agent = null;
	
	
	class Goal {
		String name = null;
		int arity = 0;
		boolean executable = false, primitive = false, topLevel = true;
		List<GoalLink>links = new LinkedList<GoalLink>();
		List<BeliefUpdateRule>beliefUpdateRules = new LinkedList<BeliefUpdateRule>();
		public Goal(String name, int arity) {
			if (name.endsWith("*")) {
				executable = true;
				name = name.substring(0,name.length()-1);
			}
			this.name = name;
			this.arity = arity;
		}
		public String toString() {
			if (arity == 0)
				return name;
			String result = name + "(";
			for (int i = 0; i < arity; i++) {
				result += "V" + (i+1);
				if (i + 1 < arity)
					result += ",";
			}
			return result + ")";
		}
		public String anonymize() {  // return a string that replaces named prolog variable with unnamed "_", to reduce load warnings.
			if (arity == 0)
				return name;
			String result = name + "(";
			for (int i = 0; i < arity; i++) {
				result += "_";
				if (i + 1 < arity)
					result += ",";
			}
			return result + ")";
		}
	}
	
	/**
	 * Makes 
	 * @author blythe
	 *
	 */
	class BeliefUpdateRule {
		Goal goal;
		Object value;
		String code;
		public BeliefUpdateRule(Goal g, Object v, String r) {
			goal = g;
			value = v;
			code = r;
		}
		public String toString() { return "On " + (value.toString().equals("1") ? "success" : (value.toString().equals("0") ? "failure" : value)) + ": " + code; }
		public String toData() { return goal + ":" + value + ":" + code; }
	}
	
	class GoalLink {
		Goal goal;
		String condition = null;
		String subGoals = null;
		List<Term>subGoalList = null;
		String executionCode = null;
		public GoalLink(Goal goal) {
			this.goal = goal;
		}
		public String toString() {  // This is used in the label renderer for the tree
			return (condition == null ? "": condition + " ? ") + subGoals;
		}
		String toData() {  // used to store the data file
			return goal + (goal.executable? "*" : "") + ":" + (condition == null ? "": condition + "->") + subGoals;
		}
	}
	
	class PrologGoal {
		Term term;
		List<Term>constants = new LinkedList<Term>();
		List<List<Term>>clauses = new LinkedList<List<Term>>();
		public DefaultMutableTreeNode goalTreeNode = null;
		public PrologGoal(Term term) {
			this.term = term.variablize();  // a prolog goal is always variablized.
		}
		public Term addConstant() {
			List<Term>args = new ArrayList<Term>(term.arity);
			Term arg = new Term("1", null);
			for (int i = 0; i < term.arity; i++) {
				args.add(arg);
			}
			Term result = new Term(term.predicate, args);
			constants.add(result);
			return result;
		}
		public List<Term> addClause() {
			List<Term>res = new LinkedList<Term>();
			clauses.add(res);  // adds an empty list of clauses.
			return res;
		}
		public String toString() {
			return term == null ? "null" : term.toString();
		}
		/**
		 * Write with a variable for each place in the terms that is not a variable
		 * @return
		 */
		public String variablize() {
			return term == null ? "null" : term.variablize().toString();
		}
	}
	
	class Rule {
		String conclusion = null, body = null;
		double strength = 0;
		public String toString() {
			return conclusion + ":" + body + ":" + strength;
		}
	}
	
	/**
	 * Encodes either an add-delete rule for an action taken or a trigger based on a precondition.
	 * @author blythe
	 *
	 */
	class ModelOperator {
		String[] models = null; // the models this operator is appropriate for
		List<Term>precondition = null;  // currently addsets  have actions and triggers have preconditions, although I guess both could have both
		String action = null;
		class Pair {public Pair(Double p2, Term parseTerm) {
				p = p2;
				t = parseTerm;
			}
		Double p;Term t;};
		List<Pair>next = null;
		public ModelOperator(String action, String[] models, String[] next, int nextOffset) {  // an 'addset'
			this.action = action;
			this.models = models;
			parseNext(next, nextOffset);
		}
		public ModelOperator(List<Term>precond, String[] models, String[] next, int nextOffset) {  // a trigger
			this.precondition = precond;
			this.models = models;
			parseNext(next, nextOffset);
		}
		void parseNext(String[] nextData, int nextOffset) {
			next = new LinkedList<Pair>();
			for (int i = nextOffset; i < nextData.length; i++) {
				String alternative = nextData[i];
				String first = alternative.split(",")[0];
				Double p = null;
				try {
					p = Double.parseDouble(first);
				} catch (Exception e ) {}
				if (p != null) {
					alternative = alternative.substring(alternative.indexOf(",")+1);
				}
				next.add(new Pair(p, Term.parseTerm(alternative)));
			}
		}
		// Should distinguish whether the action should be shown. Doesn't show the model, since in the modelTree that is the parent node.
		public String toString() {
			String res = "";
			if (precondition != null && !precondition.isEmpty()) {
				for (Term t: precondition)
					res += (res == "" ? "" : ", ") + t;
				res += ": ";
			}
			if (next != null)
				for (Pair pair: next) {
					res += pair.p + ": " + pair.t + ", ";
				}
			return res;
		}
	}
	
	class UtilityRule {
		public UtilityRule(List<Term> terms, String utilityString) {
			precondition = terms;
			utility = Double.parseDouble(utilityString);
		}
		List<Term>precondition = null;
		double utility = 0;
		public String toString() {
			String res = "";
			if (precondition != null && !precondition.isEmpty()) {
				for (Term t: precondition)
					res += (res == "" ? "" : ", ") + t;
				res += ": ";
			}
			return res + utility;
		}
	}
	
	public Wizard(String name) {
		this.name = name;
		if(!name.isEmpty())
			loadAgentFile(prologRoot + "/" + name + ".agent");
		makeWidgets();
		//setVisible(true);
	}
	
	void makeWidgets() {
		//getContentPane().removeAll();
		//setTitle("Agent wizard for agent '" + name + "'");
		JTabbedPane tabbedPane = new JTabbedPane();
		updateGoalTree();
		//goalPanel = new JPanel(new BorderLayout());
		//goalPanel.add(goalTree, BorderLayout.CENTER);
		//JPanel buttonPanel = new JPanel();
		//makeButtons(commands, buttonPanel, goalTree);
		//goalPanel.add(buttonPanel, BorderLayout.SOUTH);
		goalPanel = new ButtonedPanel(goalTree);
		tabbedPane.addTab("Rational goals", goalPanel);
		updateRuleTree();
		updateModelTree();
		modelPanel = new ButtonedPanel(new DynamicTree("model", null));
		tabbedPane.addTab("Mental models", modelPanel);
		//rulePanel = new JPanel(new BorderLayout());
		//rulePanel.add(ruleTree, BorderLayout.CENTER);
		//buttonPanel = new JPanel();
		//makeButtons(commands, buttonPanel, ruleTree);
		//rulePanel.add(buttonPanel, BorderLayout.SOUTH);
		rulePanel = new ButtonedPanel(ruleTree);
		tabbedPane.addTab("Instinctive rules", rulePanel);
		//add(tabbedPane);
		//pack();
	}
	
	public class ButtonedPanel extends JPanel {
		private static final long serialVersionUID = 1L;
		String commands[] = {"add", "remove", "new", "open", "save", "save & run"};
		
		public ButtonedPanel(DynamicTree c) {
			super(new BorderLayout());
			if (c != null)
				add(c, BorderLayout.CENTER);
			makeButtons(c);
		}

		void makeButtons(ActionListener listener) {
			JPanel buttonPanel = new JPanel();
			for (String command: commands) {
				JButton b = new JButton(command);
				if (listener != null)
					b.addActionListener(listener);
				buttonPanel.add(b);
			}
			add(buttonPanel, BorderLayout.SOUTH);
		}
	}
	
	Color executableGoalColor = Color.red, primitiveGoalColor = Color.green.darker().darker().darker(), prologGoalColor = Color.blue.darker().darker().darker();
	
	class GoalTreeCellRenderer extends DefaultTreeCellRenderer {
		private static final long serialVersionUID = 1L;

		public Component getTreeCellRendererComponent(JTree tree,
				Object value,
				boolean sel,
				boolean expanded,
				boolean leaf,
				int row,
				boolean hasFocus) {

			super.getTreeCellRendererComponent(
					tree, value, sel,
					expanded, leaf, row,
					hasFocus);
			
			/*Dimension size = getSize();
			size.width = 1000;
			setSize(size);  // make it wide enough to read text that is entered
			*/
			
			// Executable nodes could have red text, others black text
			DefaultMutableTreeNode node = (DefaultMutableTreeNode)value;
			if (node.getUserObject() instanceof String) {
				String text = (String)node.getUserObject();
				if (text.endsWith("*"))
					setForeground(executableGoalColor);
			} else if (node.getUserObject() instanceof GoalLink) {
				if (((GoalLink)node.getUserObject()).goal.executable)
					setForeground(executableGoalColor);
			} else if (node.getUserObject() instanceof Goal) {
				if (((Goal)node.getUserObject()).executable)
					setForeground(executableGoalColor);
				else if (((Goal)node.getUserObject()).primitive)  { // Note there shouldn't be any goal links for a primitive goal
					setForeground(primitiveGoalColor);
					setIcon(null);
				}
			} else if (node.getUserObject() instanceof PrologGoal) {
				setForeground(prologGoalColor);
			} 
			return this;
		}
	}

	/**
	 * I'm using a tree to help open and close all the expansions related to one goal.
	 * So each goal would be a top-level node and its expansions would be children.
	 */
	protected void updateGoalTree() {
		List<Goal>goals = new LinkedList<Goal>();  // preserve the order of appearance in the file
		for (GoalLink gl: goalLinks) {
			if (!goals.contains(gl.goal))
				goals.add(gl.goal);
		}
		goalTree = new GoalTree("goals", this);

		GoalTreeCellRenderer r = new GoalTreeCellRenderer();
		goalTree.setTreeCellRenderer(r);
		for (Goal goal: goals) {
			if (goal.name != null && !goal.name.equals("doNothing")) {
				DefaultMutableTreeNode goalNode = goalTree.addObject(null, goal);
				// quadratic time complexity when it could be linear, but initially there won't be many decompositions.
				for (GoalLink gl: goalLinks) {
					if (gl.goal.equals(goal)) {
						goalTree.addObject(goalNode, gl);
						goalTree.addPrimitivesForGoalLink(gl);
					}
				}
			}
		}
		
		// Add belief update nodes for primitive goals.
		for (String goalName: this.goals.keySet()) {
			Goal goal = this.goals.get(goalName);
			if ((goal.primitive || goal.links.isEmpty()) && goal.beliefUpdateRules != null) {
				for (BeliefUpdateRule bur: goal.beliefUpdateRules) {
					DefaultMutableTreeNode n = goalTree.addObject(goalTree.rootNode, goal);
					goalTree.addObject(n, bur);
				}
			}
		}
		
		// Add nodes for prolog goals where facts or code can be stored. Should be in a different tree.
		for (PrologGoal prologGoal: computePrologGoalsUsed()) {
			prologGoal.goalTreeNode = goalTree.addObject(null, prologGoal);
			if (prologGoal.clauses != null)
				for (List<Term> body: prologGoal.clauses)
					goalTree.addObject(prologGoal.goalTreeNode, body);
			if (prologGoal.constants != null)
				for (Term constant: prologGoal.constants)
					goalTree.addObject(prologGoal.goalTreeNode, constant);
		}
		
	}

	
	protected void updateRuleTree() {
		List<String>conclusions = new LinkedList<String>();  // preserve the order of appearance in the file
		for (Rule r: rules) {
			if (!conclusions.contains(r.conclusion))
				conclusions.add(r.conclusion);
		}
		ruleTree = new DynamicTree("patterns", this);
		for (String conclusion: conclusions) {
			DefaultMutableTreeNode conclusionNode = ruleTree.addObject(null, conclusion);
			// quadratic when it could be linear, but initially there won't be many decompositions.
			for (Rule r: rules) {
				if (r.conclusion.equals(conclusion)) {
					ruleTree.addObject(conclusionNode, r.body + ":" + r.strength);
				}
			}
		}
	}
	
	protected void updateModelTree() {
		modelTree = new DynamicTree("mental models", this);
		for (String action: addSets.keySet()) {
			DefaultMutableTreeNode actionNode = modelTree.addObject(null, action);
			HashMap<String,DefaultMutableTreeNode>modelNodes = new HashMap<String,DefaultMutableTreeNode>();
			for (ModelOperator o: addSets.get(action)) {
				if (o.models == null) {
					addNodeToModelNode("*", modelNodes, actionNode, o);
				} else {
					for (String model: o.models)
						addNodeToModelNode(model, modelNodes, actionNode, o);
				}
			}
		}
		DefaultMutableTreeNode utility = null;
		if (utilityRules != null && !utilityRules.isEmpty())
			utility = modelTree.addObject(null, "utilities");
		for (UtilityRule uRule: utilityRules) {
			modelTree.addObject(utility, uRule);
		}
		// Print out to test
		printDynamicTree(modelTree.rootNode, "");
	}
	
	protected void addNodeToModelNode(String modelNodeName, HashMap<String,DefaultMutableTreeNode>modelNodeMap, DefaultMutableTreeNode actionNode, ModelOperator operator) {
		if (!modelNodeMap.containsKey(modelNodeName))
			modelNodeMap.put(modelNodeName, modelTree.addObject(actionNode, modelNodeName));
		DefaultMutableTreeNode modelNode = modelNodeMap.get(modelNodeName);
		modelTree.addObject(modelNode, operator);
	}

	private void printDynamicTree(TreeNode node, String indent) {
		System.out.println(indent + node);
		try {
			TreeNode child = ((DefaultMutableTreeNode) node).getFirstChild();
			while (child != null) {
				printDynamicTree(child, "  " + indent);
				child = ((DefaultMutableTreeNode) child).getNextSibling();
			}
		} catch (NoSuchElementException e) {}
	}

	class MyTreeModelListener implements TreeModelListener {

	public void treeNodesChanged(TreeModelEvent e) {
			DefaultMutableTreeNode node;
	        node = (DefaultMutableTreeNode)
	                 (e.getTreePath().getLastPathComponent());

	        /*
	         * If the event lists children, then the changed
	         * node is the child of the node we have already
	         * gotten.  Otherwise, the changed node and the
	         * specified node are the same.
	         */
	        try {
	            int index = e.getChildIndices()[0];
	            node = (DefaultMutableTreeNode)
	                   (node.getChildAt(index));
	        } catch (NullPointerException exc) {}

	        System.out.println("The user has finished editing the node.");
	        System.out.println("New value: " + node.getUserObject());
		}

		@Override
		public void treeNodesInserted(TreeModelEvent e) {
			
		}

		@Override
		public void treeNodesRemoved(TreeModelEvent e) {
			
		}

		@Override
		public void treeStructureChanged(TreeModelEvent e) {
			
		}
		
	}
	
	 protected JPanel makeTextPanel(String text) {
	        JPanel panel = new JPanel(false);
	        JLabel filler = new JLabel(text);
	        filler.setHorizontalAlignment(JLabel.CENTER);
	        panel.setLayout(new GridLayout(1, 1));
	        panel.add(filler);
	        return panel;
	    }
	
	static int readingGoals = 0, readingRules = 1, readingBaseRules = 2, readingBeliefUpdates = 3, 
			readingConstants = 4, readingClauses = 5, readingMentalModelAdd= 6, readingMentalModelTrigger= 7, readingMentalModelUtility = 8;
	void loadAgentFile(String filename) {
		loadAgentFile(new File(filename));
	}
	
	void loadAgentFile(File file) {
		try {
			BufferedReader br = new BufferedReader(new FileReader(file));
			int state = -1;
			goalLinks.clear();
			utilityRules.clear();
			for (String line = br.readLine(); line != null; line = br.readLine()) {
				if (line.contains("%"))
					line = line.substring(0,line.indexOf("%"));
				if (line.startsWith("Rules:")) {
					state = readingRules;
				} else if (line.startsWith("Goals:")) {
					state = readingGoals;
				} else if (line.startsWith("BaseRules:")) {
					state = readingBaseRules;
				} else if (line.startsWith("Belief Updates:")) {
					state = readingBeliefUpdates;
				} else if (line.startsWith("Constants:")) {
					state = readingConstants;
				} else if (line.startsWith("Clauses:")) {
					state = readingClauses;
				} else if (line.startsWith("MentalModels:")) {
					mentalModels = line.substring(line.indexOf(":")+1).split(":");
				} else if (line.startsWith("MentalModelAdd:")) {
					state = readingMentalModelAdd;
				} else if (line.startsWith("MentalModelTrigger:")) {
					state = readingMentalModelTrigger;
				} else if (line.startsWith("MentalModelUtility:")) {
					state = readingMentalModelUtility;
				} else if (state == readingGoals && line.contains(":")) {
					addGoalLink(line);
				} else if (state == readingRules && line.contains(":")) {
					addRule(line);
				} else if (state == readingBaseRules) {
					baseRules += line;
				} else if (state == readingBeliefUpdates && line.contains(":")) {
					String data[] = line.split(":");
					Term goalTerm = Term.parseTerm(data[0]);
					Goal goal = findOrCreateGoal(goalTerm);
					goal.beliefUpdateRules.add(new BeliefUpdateRule(goal, data[1], data[2]));
				} else if (state == readingConstants && line.contains(":")) {
					String[] data = line.split(":");
					Term goalTerm = Term.parseTerm(data[0]);
					PrologGoal pg = findOrCreatePrologGoal(goalTerm);
					pg.constants.add(Term.parseTerm(data[1]));
				} else if (state == readingClauses && line.contains(":")) {
					System.out.println("Read clause line " + line);
					String[] data = line.split(":");
					Term goalTerm = Term.parseTerm(data[0]);
					PrologGoal pg = findOrCreatePrologGoal(goalTerm);
					List<Term>tl = Term.parseTerms(data[1]);
					System.out.println("Adding " + tl + " to " + pg);
					pg.clauses.add(tl);
				} else if (state == readingMentalModelAdd && line.contains(":")) {
					String[] data = line.split(":");
					storeAddSet(new ModelOperator(data[0], data[1].split("\\|"), data, 2));
				} else if (state == readingMentalModelTrigger && line.contains(":")) {
					String[] data = line.split(":");
					storeAddSet(new ModelOperator(Term.parseTerms(data[1]), data[0].split("\\|"), data, 2));
				} else if (state == readingMentalModelUtility && line.contains(":")) {
					String[] data = line.split(":");
					utilityRules.add(new UtilityRule(Term.parseTerms(data[0]), data[1]));
				}
			}
		}
		catch (FileNotFoundException e) { 
			System.out.println(e); 
		}
		catch(IOException e) { 
			System.out.println(e); 
		}
		System.out.println("Loaded " + goalLinks.size() + " goal decompositions and " + rules.size() + " rules.");
	}
	

	private void storeAddSet(ModelOperator modelOperator) {
		String action = modelOperator.action;
		if (action == null || "".equals(action))  // an empty action signifies a trigger
			action = "trigger";
		if (!addSets.containsKey(action))
			addSets.put(action, new LinkedList<ModelOperator>());
		addSets.get(action).add(modelOperator);
	}

	private void addRule(String line) {
		Rule r = new Rule();
		String[] bits = line.split(":");
		r.conclusion = bits[0];
		r.body = bits[1];
		r.strength = Double.parseDouble(bits[2]);
		rules.add(r);
	}

	private void addGoalLink(String line) {
		String[] nameSub = line.split(":");
		Term goalTerm = Term.parseTerm(nameSub[0]);
		Goal goal = findOrCreateGoal(goalTerm);
		GoalLink gl = new GoalLink(goal);
		if (nameSub[1].contains("->")) {
			String[] condSub = nameSub[1].split("->");
			gl.condition = condSub[0];
			gl.subGoals = condSub[1];
		} else {
			gl.subGoals = nameSub[1];
		}
		goalLinks.add(gl);
	}

	Goal findOrCreateGoal(Term goalTerm) {
		return findOrCreateGoal(goalTerm.predicate, goalTerm.arity);
	}
	
	Goal findOrCreateGoal(String predicate, int arity) {
		if (!goals.containsKey(predicate + "/" + arity)) {
			Goal goal = new Goal(predicate, arity);
			goals.put(predicate + "/" + arity, goal);
		}
		return goals.get(predicate + "/" + arity);			
	}
	
	Goal findGoal(Term t) {
		return findGoal(t.predicate, t.arity);
	}
	
	Goal findGoal(String predicate, int arity) {
		if (!goals.containsKey(predicate + "/" + arity)) {
			return null;
		}
		return goals.get(predicate + "/" + arity);			
	}
	
	PrologGoal findOrCreatePrologGoal(Term goalTerm) {
		String sig = goalTerm.signature();
		if (!prologGoals.containsKey(sig)) {
			prologGoals.put(sig, new PrologGoal(goalTerm));
		}
		return prologGoals.get(sig);
	}
	
	public void newDomain() {
		goals.clear();
		goalLinks.clear();
		rules.clear();
		prologGoals.clear();
		name = "New agent";
		makeWidgets();
		getNameToSave = true;  // ask for a new name before saving.
	}
	
	public void loadDomain() {
		JFileChooser fc = new JFileChooser(prologRoot);
		fc.setFileFilter(new FileFilter() {

			@Override
			public String getDescription() {
				return "Only agent files";
			}

			@Override
			public boolean accept(File f) {
				if (f.isDirectory()) 
					return true;
				String name = f.getName();
				int i = name.lastIndexOf('.');
				if (i > -1 && name.substring(i+1).equals("agent"))
					return true;
				return false;
			}
			
		});
		int returnVal=0;
		//int returnVal = fc.showDialog(this, "Open agent file");
		if (returnVal == JFileChooser.APPROVE_OPTION) {
			goals.clear();
			goalLinks.clear();
			rules.clear();
			prologGoals.clear();
			loadAgentFile(fc.getSelectedFile());
			name = fc.getSelectedFile().getName();
			if (name.contains("."))
				name = name.substring(0,name.indexOf("."));   // set agent name to the file name without the extension
			getNameToSave = false;
			makeWidgets();
		} else {
			System.out.println("Load cancelled");
		}
	}
	
	boolean getNameToSave = false;
	
	

	List<PrologGoal>computePrologGoalsUsed() {
		HashSet<String>signatures = new HashSet<String>();  // keep track of signatures so we don't count goals twice. Used separately from the prologGoals map for when goals are removed.
		List<PrologGoal>result = new LinkedList<PrologGoal>();
		for (GoalLink gl: goalLinks) {
			if (!gl.goal.executable) {
				addPrologGoalsUsed(result, signatures, gl.condition);
			} else {
				addPrologGoalsUsed(result, signatures, gl.subGoals);
			}
		}			
		for (String goalName: goals.keySet()) {
			Goal goal = goals.get(goalName);
			if (goal.beliefUpdateRules != null && !goal.beliefUpdateRules.isEmpty()) {
				for (BeliefUpdateRule bur: goal.beliefUpdateRules)
					addPrologGoalsUsed(result, signatures, bur.code);
			}
		}
		for (String pgName: new LinkedList<String>(prologGoals.keySet())) {  // create a new list to avoid concurrent modification issues. The new clauses won't have clauses of their own.
			PrologGoal pg = prologGoals.get(pgName);
			if (pg.clauses != null) {
				for (List<Term>body: pg.clauses) {
					for (Term el: body)
						addPrologGoalUsed(result, signatures, el);
				}
			}
		}
		return result;
	}
	
	void addPrologGoalsUsed(List<PrologGoal>goals, HashSet<String>signatures, String code) {
		List<Term>conditions = Term.parseTerms(code);
		for (Term condition: conditions)
			addPrologGoalUsed(goals, signatures, condition);
	}
	
	private void addPrologGoalUsed(List<PrologGoal> goals, HashSet<String> signatures, Term condition) {
		// Don't add goals for unary terms, i.e. free variables or constants in the expression
		if (condition.arity == 0)
			return;
		boolean builtin = false;
		for (String name: new String[]{"assert","retract","not","retractall"})
			if (name.equals(condition.predicate))
				builtin = true;
		if (!builtin && !signatures.contains(condition.signature())) {  // ignore builtins
			String signature = condition.signature();
			signatures.add(signature);
			if (!prologGoals.containsKey(signature)) {
				prologGoals.put(signature, new PrologGoal(condition));
			}
			goals.add(prologGoals.get(signature));
		}
		// recursively add goals for any subterms
		if (condition.subTerms != null)
			for (Term sub: condition.subTerms)
				addPrologGoalUsed(goals, signatures, sub);
	}

	public static void main(String[] args) {
		String name = "NewAgent", loadFile = "C:\\Documents and Settings\\mariam\\My Documents\\Dash\\lib\\logic\\NewAgent.agent";
		if (args != null && args.length > 0)
			name = args[0];
		if (args != null && args.length > 1)
			loadFile = args[1];
		Wizard w = new Wizard(name);
		w.loadAgentFile(loadFile);
		String json = w.getJsonTree();
		System.out.println("JSON="+json);
		System.out.println("Model tree: " + w.modelTree);
	}

	public void runAgentOrig() {
		JFrame frame = new JFrame();
		final JTextArea jt = new JTextArea(10,20); 
		frame.add(jt);
		frame.setVisible(true);
		String[] tmp = {"-maxSteps", "10", "agentGeneral.pl", name + "_agent.pl"};
		agent = new Detergent(tmp) {
			void printOut(String s) {
				jt.append(s + "\n");
			}
		};
		agent.run();
	}

	public Term addConstant(PrologGoal pg) {
		return pg.addConstant();
	}

	public List<Term> addClause(PrologGoal pg) {
		return pg.addClause();
	}

	//MariaM
	public void addGoal(String id){
		goalTree.nodeAdded(id);
	}
	
	public void removeNode(String id){
		goalTree.removeNode(id);
	}

	public void makePrimitive(String id){
		goalTree.makePrimitive(id);
	}

	public void makeExecutable(String id){
		goalTree.makeExecutable(id);
	}

	public void addUpdateRule(String id){
		goalTree.addUpdateRule(id);
	}

	public void addConstant(String id){
		goalTree.addConstant(id);
	}

	public void addClause(String id){
		goalTree.addClause(id);
	}
	public void renameNode(String id, String newName){
		goalTree.nodeChanged(id, newName);
	}

	public String getJsonTree(){
		return goalTree.getJson(goalTree.rootNode).toString();
	}
	
	public String getJsonForMentalTree(){
		return goalTree.getJsonForMentalTree(modelTree.rootNode).toString();
	}

	public void loadDomain(String filename) {
		goals.clear();
		goalLinks.clear();
		rules.clear();
		prologGoals.clear();
		loadAgentFile(prologRoot+"/"+filename);
		name = filename;
		if (name.contains("."))
			name = name.substring(0,name.indexOf("."));   // set agent name to the file name without the extension
		getNameToSave = false;
		makeWidgets();
	}

	public String runAgent() {
		String[] tmp = {"-maxSteps", "10", "agentGeneral.pl", name + "_agent.pl"};
		final StringBuffer jt = new StringBuffer();
		agent = new Detergent(tmp) {
			void printOut(String s) {
				//use @@@ instead of newline, so json doesn't complain
				jt.append(s + "@@@");
			}
		};
		agent.run();
		//System.out.println("end agent run");
		return jt.toString();
	}

	public void saveData(String agentName) {
		System.out.println("In save data. " + agentName);
		name=agentName;
		try {
			PrintStream ps = new PrintStream(new FileOutputStream(prologRoot + "/" + name + ".agent", false));
			System.out.println("Save in:"+ ps.toString());
			ps.println("% Saved automatically by the Wizard");
			// Print the goal data
			ps.println("Goals:");
			for (GoalLink gl: goalLinks) {
				ps.println(gl.toData());
			}
			ps.println("\nBelief Updates:");
			for (String name: goals.keySet()) {
				Goal g = goals.get(name);
				for (BeliefUpdateRule b: g.beliefUpdateRules) {
					ps.println(b.toData());
				}
			}
			ps.println("\nConstants:");
			for (String sig: prologGoals.keySet()) {
				PrologGoal pg = prologGoals.get(sig);
				if (pg.constants != null)
					for (Term constant: pg.constants)
						ps.println(pg + ":" + constant);
			}
			ps.println("\nClauses:");
			for (String sig: prologGoals.keySet()) {
				PrologGoal pg = prologGoals.get(sig);
				if (pg.clauses != null)
					for (List<Term> clause: pg.clauses) {
						ps.print(pg + ":");
						// print the clause without the square brackets.
						for (int i = 0; i < clause.size(); i++)
							ps.print(clause.get(i) + (i < clause.size() - 1 ? "," : ""));
						ps.println();
					}
			}
			ps.println("\nRules:");
			for (Rule r: rules)
				ps.println(r);
			ps.println("\nBaseRules:");
			ps.println(baseRules);
			ps.close();
			
			// Now save the prolog version
			PrintStream prolog = new PrintStream(new FileOutputStream(prologRoot + "/" + name + "_agent.pl", false));
			prolog.println("% -*- Mode: Prolog -*-");  // set file to prolog mode in editors
			prolog.println("% Agent file created automatically by the wizard.");
			prolog.println(":-style_check(-singleton).");
			prolog.println(":-style_check(-discontiguous).");

			for (GoalLink gl: goalLinks) {
				if (!gl.goal.executable) {
					prolog.println("goalRequirements("+gl.goal+",["+gl.subGoals+"])" + (gl.condition == null ? "" : (" :- " + gl.condition)) + ".");
				} else {
					prolog.println("execute(" + gl.goal + ") :- " + gl.subGoals + ".");
				}
			}
			// Marking goals primitive is fine, but here assume anything without a decomposition is primitive
			for (String goalName: goals.keySet()) {
				Goal goal = goals.get(goalName);
				goal.links.clear();
				goal.topLevel = true;
			}
			for (GoalLink gl: goalLinks) {
				gl.goal.links.add(gl);
				// find subgoals
				gl.subGoalList = Term.parseTerms(gl.subGoals);
				for (Term subgoalTerm: gl.subGoalList) {
					findGoal(subgoalTerm).topLevel = false;
				}
			}
			for (String goalName: goals.keySet()) {
				Goal goal = goals.get(goalName);
				String anon = goal.anonymize();
				if (goal.executable)
					prolog.println("executable(" + anon + ").");
				else if (goal.links.isEmpty())
					prolog.println("primitiveAction(" + anon + ").");
				else if (goal.topLevel)
					prolog.println("goal(" + anon + ").\ngoalWeight(" + anon + ", 1).");
				else
					prolog.println("subGoal(" + anon + ").");  // will split into goal() and subgoal() when the parsing works properly.
			}
			// update rules
			prolog.println("\n");
			for (String goalName: goals.keySet()) {
				Goal goal = goals.get(goalName);
				if (goal.beliefUpdateRules != null && !goal.beliefUpdateRules.isEmpty()) {
					for (BeliefUpdateRule bur: goal.beliefUpdateRules) {
						prolog.println("updateBeliefs("+ goal + "," + bur.value + ") :- " + bur.code + ".");
					}
				}
			}
			prolog.println("% Generic update rule\nupdateBeliefs(_,_).");
			
			// Some definitions for prolog goals
			for (PrologGoal prologGoal: computePrologGoalsUsed()) {
				prolog.println(":-dynamic(" + prologGoal.term.signature() + ").");
				if (prologGoal.constants != null)
					for (Term constant: prologGoal.constants)
						prolog.println(constant + ".");
				if (prologGoal.clauses != null)
					for (List<Term> body: prologGoal.clauses) {
						prolog.print(prologGoal + " :- ");
						for (int i = 0; i < body.size(); i++)
							prolog.print(body.get(i) + (i < body.size() - 1 ? ", " : ".\n"));
					}
			}
			
			// Should probably be updated by the developer, or we need a simple protocol to negotiate the id
			prolog.println("id(1).");
			prolog.close();
		} catch (IOException ioe) {
			System.out.println(ioe);
		}
		System.out.println("End save data.");
	}

	//End MariaM

}

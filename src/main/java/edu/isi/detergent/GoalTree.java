/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.detergent;

import java.awt.event.ActionEvent;
import java.awt.event.MouseEvent;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;

import javax.swing.JMenuItem;
import javax.swing.JPopupMenu;
import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.TreePath;

import org.json.JSONArray;
import org.json.JSONObject;

import edu.isi.detergent.Wizard.Goal;
import edu.isi.detergent.Wizard.GoalLink;
import edu.isi.detergent.Wizard.PrologGoal;

public class GoalTree extends DynamicTree {

	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;

	public GoalTree(String rootName, Wizard wizard) {
		super(rootName, wizard);
	}

	
	void nodeAdded() {
		DefaultMutableTreeNode parentNode = null;
		TreePath parentPath = tree.getSelectionPath();

		if (parentPath == null) {
			parentNode = rootNode;
		} else {
			parentNode = (DefaultMutableTreeNode)
			(parentPath.getLastPathComponent());
		}
		Object userObject = parentNode.getUserObject();
		
		// Create the template based on the parent node
		if (parentNode == rootNode)
			addObject(parentNode, wizard.findOrCreateGoal("New goal " + newNodeSuffix++, 0), true);
		else if (userObject instanceof Goal) {
			Wizard.GoalLink goalLink = wizard.new GoalLink((Goal)userObject);
			addObject(parentNode, goalLink, true);
			wizard.goalLinks.add(goalLink);
			((Goal)userObject).primitive = false; // would be primitive by default if added by the wizard.
		}
		// Nothing gets added below that level.
	}

	void nodeChanged(DefaultMutableTreeNode node) {
		// We lost the original user object. Recover it from the node
		Object oldObject = objects.get(node);
		if (oldObject instanceof Wizard.Goal) {  // modify the goal with the string and replace it as the object
			Goal goal= (Goal)oldObject;
			goal.name = (String)node.getUserObject();
			node.setUserObject(goal);
		} else if (oldObject instanceof Wizard.GoalLink) {  // create a new link with the new information
			Wizard.GoalLink goalLink = (Wizard.GoalLink)oldObject;
			String line = (String)node.getUserObject();
			if (line.contains(" ? ")) {
				String[]data = line.split(" \\? ");
				System.out.println("Data has length " + data.length);
				for(String s: data)
					System.out.println(" > " + s);
				goalLink.condition = data[0];
				goalLink.subGoals = data[1];
			} else {
				goalLink.condition = null;
				goalLink.subGoals = line;
			}
			addPrimitivesForGoalLink(goalLink);
			addPrologGoalsForGoalLink(goalLink);
			node.setUserObject(goalLink);
		} else if (oldObject instanceof Wizard.BeliefUpdateRule) {
			Wizard.BeliefUpdateRule b = (Wizard.BeliefUpdateRule)oldObject;
			String parts[] = ((String)node.getUserObject()).split(":");
			if (parts[0].equals("On success"))
				b.value = 1;
			else if (parts[0].equals("On failure"))
				b.value = 0;
			else
				b.value = parts[0].substring(3);
			b.code = parts[1];
		} else if (node.getParent() != null && ((DefaultMutableTreeNode)node.getParent()).getUserObject() instanceof Wizard.PrologGoal) {
			DefaultMutableTreeNode parent = (DefaultMutableTreeNode)node.getParent();
			Wizard.PrologGoal pg = (Wizard.PrologGoal)parent.getUserObject();
			// Figure out which child this is. Assume we show clauses first, then constants
			int i = 0;
			for (; i < parent.getChildCount(); i++)
				if (parent.getChildAt(i).equals(node))
					break;
			if (i < parent.getChildCount() && i < pg.clauses.size())
				pg.clauses.set(i, Term.parseTerms((String)node.getUserObject()));
			else if (i < parent.getChildCount() && i < pg.clauses.size() + pg.constants.size()) {
				pg.constants.set(i - pg.clauses.size(), Term.parseTerm((String)node.getUserObject()));
			}
		} else {
			System.out.println("Left as string: " + node.getUserObject());
		}
	}
	
	public void addPrimitivesForGoalLink(Wizard.GoalLink gl) {
		// Parse the new subgoals and update primitives as needed
		gl.subGoalList = Term.parseTerms(gl.subGoals);
		for (Term sub: gl.subGoalList) {
			// Add a node and goal (as a primitive) if none is found.
			Goal g = wizard.findGoal(sub);
			if (g == null) {
				g = wizard.findOrCreateGoal(sub);
				g.primitive = true;
				addObject(rootNode, g);
			}
		}
	}
	
	private void addPrologGoalsForGoalLink(GoalLink goalLink) {
		List<Wizard.PrologGoal>goals = new LinkedList<PrologGoal>();
		HashSet<String>sigs = new HashSet<String>();
		wizard.addPrologGoalsUsed(goals, sigs, goalLink.condition);
		for (PrologGoal pg: goals) {
			if (pg.goalTreeNode == null)
				pg.goalTreeNode = addObject(rootNode, pg);
		}
	}

	DefaultMutableTreeNode menuNode = null; 
    void showNodePopUp(DefaultMutableTreeNode n, MouseEvent e) {
    	menuNode = n;
    	Object userObject = n.getUserObject();
    	JPopupMenu popup = new JPopupMenu();
    	if (userObject instanceof Wizard.Goal) {
    		Wizard.Goal g = (Wizard.Goal)userObject;
    		if (g.primitive)
    			setItem(popup, "Add update rule");
    		else
    			setItem(popup,"Make primitive");
    		if (!g.executable)
    			setItem(popup,"Make executable");
    		popup.show(e.getComponent(), e.getX(), e.getY());
    	} else if (userObject instanceof Wizard.GoalLink) {
    		// Currently no menu needed for links
    	} else if (userObject instanceof Wizard.PrologGoal) {
    		setItem(popup, "Add a constant value");
    		setItem(popup, "Add a clause");
    		popup.show(e.getComponent(), e.getX(), e.getY());
    	} else if ("goals".equals(userObject)) {
    		setItem(popup,"Add a goal");
    		popup.show(e.getComponent(), e.getX(), e.getY());
    	}
    }
    
    void setItem(JPopupMenu popup, String label) {
    	JMenuItem item = new JMenuItem(label);
    	item.addActionListener(this);
    	popup.add(item);
    }
    
    
    public void actionPerformed(ActionEvent e) {
    	String command = e.getActionCommand();
    	Object userObject = menuNode != null ? menuNode.getUserObject() : null;
    	if ("Make primitive".equals(command)) {
    		((Goal)userObject).primitive = true;
    	} else if ("Make executable".equals(command)) {
    		((Goal)userObject).executable = true;
    	} else if ("Add update rule".equals(command)) {
    		Goal g = (Goal)userObject;
    		Wizard.BeliefUpdateRule gur = wizard.new BeliefUpdateRule(g, "1", "");
    		g.beliefUpdateRules.add(gur);
    		addObject(gur);
    	} else if ("Add a constant value".equals(command)) {
    		Term newConstant = wizard.addConstant((Wizard.PrologGoal)userObject);
    		addObject(newConstant);
    	} else if ("Add a clause".equals(command)) {
    		List<Term> clause = wizard.addClause((Wizard.PrologGoal)userObject);
    		addObject(clause);
    	} else {
    		super.actionPerformed(e);
    	}
    }

	//MariaM
	private void addToJSONObject(JSONObject obj, String key, Object value){
		try{
			obj.put(key, value);
		}catch(Exception e){
			System.out.println("Error occured while adding to a JSON object." + e);
		}
	}

	/**
	 * Returns this GoalTree as JSON object
	 * @param n 
	 * 		start with the root of the tree
	 * @return this tree as JSON object
	 */
	/**
	 * @return
	 */
	JSONObject getJson(DefaultMutableTreeNode n){
		Object userObject = n.getUserObject();
		JSONObject childGoal = new JSONObject();
		JSONObject childAttr = new JSONObject();
		addToJSONObject(childGoal,"attr", childAttr);
		JSONArray childGoalChildren = new JSONArray();
		addToJSONObject(childGoal,"children", childGoalChildren);

		addToJSONObject(childGoal,"data", n.toString());
		addToJSONObject(childAttr,"id", String.valueOf(n.hashCode()));
	
		//System.out.println("ON1:" + n.getUserObject().getClass());
		
	   	if (userObject instanceof Wizard.Goal) {
    		Wizard.Goal g = (Wizard.Goal)userObject;
			addToJSONObject(childAttr,"type", "Goal");
			addToJSONObject(childAttr,"primitive", new Boolean(g.primitive).toString());
			addToJSONObject(childAttr,"executable", new Boolean(g.executable).toString());
			//System.out.println("for " + g.name + "links= " + g.links.isEmpty() + " rules= " + g.beliefUpdateRules);
			if(g.executable)
				addToJSONObject(childAttr,"class", "Executable");
			else if(g.primitive){
				addToJSONObject(childAttr,"class", "Primitive");
			}
			else if (g.links.isEmpty() && !g.beliefUpdateRules.isEmpty()){
				addToJSONObject(childAttr,"class", "Primitive");
			}
			
    	} else if (userObject instanceof Wizard.GoalLink) {
    		Wizard.Goal g = ((Wizard.GoalLink)userObject).goal;
			addToJSONObject(childAttr,"type", "GoalLink");
			addToJSONObject(childAttr,"primitive", new Boolean(g.primitive).toString());
			addToJSONObject(childAttr,"executable", new Boolean(g.executable).toString());
			if(g.executable)
				addToJSONObject(childAttr,"class", "Executable");
			else if(g.primitive)
				addToJSONObject(childAttr,"class", "Primitive");
    	} else if (userObject instanceof Wizard.PrologGoal) {
    		Wizard.PrologGoal g = (Wizard.PrologGoal)userObject;
			addToJSONObject(childAttr,"type", "PrologGoal");
			addToJSONObject(childAttr,"class", "Prolog");
    	} else if (n.toString().equals("goals")) {
			addToJSONObject(childAttr,"type", "Root");
    	} else{
    		//System.out.println("ON:" + n.toString());
			addToJSONObject(childAttr,"type", "OtherNode");    		
    	}

			Enumeration<DefaultMutableTreeNode> children = n.children();
			while(children.hasMoreElements()){
				DefaultMutableTreeNode child = children.nextElement();
				JSONObject childJson = getJson(child);
				childGoalChildren.put(childJson);
			}
			
			return childGoal;
		}

	public void makePrimitive(String id){
		DefaultMutableTreeNode n = getNode(id);
		
		Object o = n.getUserObject();
		if(o instanceof Goal){
			((Goal) o).primitive=true;
		}
	}

	public void makeExecutable(String id){
		DefaultMutableTreeNode n = getNode(id);
		
		Object o = n.getUserObject();
		if(o instanceof Goal){
			((Goal) o).executable=true;
		}
	}

	public void addUpdateRule(String id){
		DefaultMutableTreeNode n = getNode(id);
		
		Object o = n.getUserObject();
		if(o instanceof Goal){
			Goal g = (Goal) o;
			System.out.println("add rule to:"+g.name);
    		Wizard.BeliefUpdateRule gur = wizard.new BeliefUpdateRule(g, "1", "");
    		g.beliefUpdateRules.add(gur);
    		addObject(gur, n);
		}
	}

	public void addConstant(String id){
		DefaultMutableTreeNode n = getNode(id);
		
		Object o = n.getUserObject();
		if(o instanceof Wizard.PrologGoal){
			Wizard.PrologGoal g = (Wizard.PrologGoal) o;
	   		Term newConstant = wizard.addConstant(g);
    		addObject(newConstant, n);
 		}
	}

	public void addClause(String id){
		DefaultMutableTreeNode n = getNode(id);
		
		Object o = n.getUserObject();
		if(o instanceof Wizard.PrologGoal){
			Wizard.PrologGoal g = (Wizard.PrologGoal) o;
	   		List<Term> clause = wizard.addClause(g);
    		addObject(clause, n);
 		}
	}
	
	void nodeAdded(String id) {
		DefaultMutableTreeNode parentNode = getNode(id);
				
		Object userObject = parentNode.getUserObject();
		
		// Create the template based on the parent node
		if (parentNode == rootNode)
			addObject(parentNode, wizard.findOrCreateGoal("New goal " + newNodeSuffix++, 0), true);
		else if (userObject instanceof Goal) {
			Wizard.GoalLink goalLink = wizard.new GoalLink((Goal)userObject);
			addObject(parentNode, goalLink, true);
			wizard.goalLinks.add(goalLink);
			((Goal)userObject).primitive = false; // would be primitive by default if added by the wizard.
		}	 
	}

	void nodeChanged(String id, String newName) {
		System.out.println("node changed .....");
		DefaultMutableTreeNode n = getNode(id);
		Object oldObject = n.getUserObject();
		if(newName.equals(oldObject.toString())){
			//do nothing, the name didn't change
		}
		if (oldObject instanceof Wizard.Goal) {  // modify the goal with the string and replace it as the object
			System.out.println("Goal ...");
			Goal goal= (Goal)oldObject;
			goal.name = newName;
			n.setUserObject(goal);
		} else if (oldObject instanceof Wizard.GoalLink) {  // create a new link with the new information
			System.out.println("GoalLink ...");
			Wizard.GoalLink goalLink = (Wizard.GoalLink)oldObject;
			String line = newName;
			if (line.contains(" ? ")) {
				String[]data = line.split(" \\? ");
				System.out.println("Data has length " + data.length);
				for(String s: data)
					System.out.println(" > " + s);
				goalLink.condition = data[0];
				goalLink.subGoals = data[1];
			} else {
				goalLink.condition = null;
				goalLink.subGoals = line;
			}
			addPrimitivesForGoalLink(goalLink);
			addPrologGoalsForGoalLink(goalLink);
			n.setUserObject(goalLink);
		} else if (oldObject instanceof Wizard.BeliefUpdateRule) {
			System.out.println("BeliefUpdateRule ...");
			Wizard.BeliefUpdateRule b = (Wizard.BeliefUpdateRule)oldObject;
			String parts[] = newName.split(":");
			if (parts[0].equals("On success"))
				b.value = 1;
			else if (parts[0].equals("On failure"))
				b.value = 0;
			else
				b.value = parts[0].substring(3);
			b.code = parts[1];
		} else if (n.getParent() != null && ((DefaultMutableTreeNode)n.getParent()).getUserObject() instanceof Wizard.PrologGoal) {
			DefaultMutableTreeNode parent = (DefaultMutableTreeNode)n.getParent();
			Wizard.PrologGoal pg = (Wizard.PrologGoal)parent.getUserObject();
			// Figure out which child this is. Assume we show clauses first, then constants
			int i = 0;
			for (; i < parent.getChildCount(); i++)
				if (parent.getChildAt(i).equals(n))
					break;
			if (i < parent.getChildCount() && i < pg.clauses.size())
				pg.clauses.set(i, Term.parseTerms(newName));
			else if (i < parent.getChildCount() && i < pg.clauses.size() + pg.constants.size()) {
				pg.constants.set(i - pg.clauses.size(), Term.parseTerm(newName));
			}
			n.setUserObject(newName);
		} else if (oldObject instanceof Wizard.PrologGoal) {
			//do nothing - don't allow changes on PrologGoals
		} else {
			//if it's a constant or clause it is handles above (the parent is a PrologGoal)
			System.out.println("Left as string: " + n.getUserObject());
		}
	}
	//End MariaM

}

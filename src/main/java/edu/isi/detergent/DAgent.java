/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.detergent;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Container;
import java.awt.Dimension;
import java.awt.Graphics;
import java.awt.Point;
import java.awt.Rectangle;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Hashtable;
import java.util.LinkedList;
import java.util.List;

import javax.swing.BorderFactory;
import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JSlider;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;

import edu.isi.detergent.Detergent.Agent;

/**
 * This is a single agent in the graphics framework. May connect to a Detergent class
 * or the Agent class of one of its children. Is represented on screen through the 'draw' method.
 * @author blythe
 *
 */
public class DAgent extends JPanel implements ActionListener, MouseListener, ChangeListener {
	
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	
	Detergent detergent = null;
	Agent agent = null;
	String name = "default";
	JLabel lastAction = new JLabel(""), stateLabel = new JLabel("STATE"), values = new JLabel();
	JTextArea output = new JTextArea(5, 20);
	JButton startButton = new JButton("start");
	JPanel controls = new JPanel(), wme = new JPanel(), s1 = new JPanel(), s2 = new RationalPanel();
	JScrollPane s2Scroll = null;
	int agentOutputIndex = 0;
	DFrame df = null;
	Color backgroundColor = Color.white;
	
	static int lastTop = 0, lastLeft = 100;
	int top = 0, left = 100;

	public DAgent(Detergent d, DFrame df) {
		detergent = d;
		name = d.name;
		// Put them all in a column for now
		lastTop = top = lastTop + 100;
		d.dAgent = this;
		this.df = df;
		makeWidgets();
	}

	public DAgent(Agent child, DFrame df) {
		agent = child;
		name = agent.name;
		lastTop = top = lastTop + 100;
		child.dAgent = this;
		this.df = df;
		makeWidgets();
	}
	
	public class RationalPanel extends JPanel {
		private static final long serialVersionUID = 1L;

		public void paintComponent(Graphics g) {
			super.paintComponent(g);
			paintS2(g);
		}
		
		protected void paintS2(Graphics g) {
			int x = 10, y = 30, maxX = 100, maxY = 30;
			HashSet<String>drawn = new HashSet<String>();
			for (String state: stateMap.keySet()) {
				if (!accessible.contains(state)) {
					Point p = drawTransitions(state, g, x, y, drawn);
					y = p.y;
					if (p.x > maxX) maxX = p.x;
					if (p.y > maxY) maxY = p.y;
				}
			}
			//System.out.println(name + " max S2: " + maxX + ", S1: " + s1.getSize().width);
			if (s1.getSize().width > maxX) 
				maxX = s1.getSize().width;
			if (getSize().width < maxX || getSize().height < maxY-10) {
				setPreferredSize(new Dimension(maxX, maxY-10));
				revalidate();
				//Rectangle bounds = getBounds();
				//setBounds(bounds.x, bounds.y, maxX, maxY + 50);
			}
		}

		protected Point drawTransitions(String state, Graphics g, int x, int y, HashSet<String>drawn) {
			drawn.add(state);
			g.drawString(state, x, y);
			x += g.getFontMetrics().getStringBounds(state, g).getWidth();
			g.drawLine(x, y - 5, x + 15, y - 5);
			Transition t = stateMap.get(state);
			int maxX = x + 15;
			if (t != null) {
				g.drawString(t.action, x + 15, y);
				double width = g.getFontMetrics().getStringBounds(t.action, g).getWidth();
				g.drawOval(x + 15, y - 15, (int)width, 20);
				x += 15 + width;
				g.drawLine(x, y - 5, x + 15, y - 5);
				y -= 30;
				x += 15;
				maxX = x;
				for (String newState: t.nextStates) {
					y += 30;
					if (!drawn.contains(newState)) {
						Point p = drawTransitions(newState, g, x, y, drawn);
						y = p.y;
						if (p.x > maxX) maxX = p.x;
					} else {
						g.drawString(newState, x, y);
						width = g.getFontMetrics().getStringBounds(newState, g).getWidth();
						if (x + width > maxX)
							maxX = x + (int)width;
					}
				}
			}
			return new Point(maxX, y);
		}
	}

	/**
	 * Create the buttons etc for this agent.
	 */
	private void makeWidgets() {
		Container pane = this; //getContentPane();  // use 'this' if changing class back to a JPanel
		pane.setBackground(backgroundColor);
		setBorder(BorderFactory.createLineBorder(Color.black));
		pane.setLayout(new BoxLayout(this, BoxLayout.PAGE_AXIS));
		//pane.setLayout(new GridBagLayout());
		//GridBagConstraints c = new GridBagConstraints();
		JPanel top = new JPanel();  // Top has the name, last action and to the right state information
		top.setLayout(new BorderLayout());
		top.setBackground(backgroundColor);
		JPanel box = new JPanel();
		box.setLayout(new BoxLayout(box, BoxLayout.PAGE_AXIS));
		box.add(new JLabel("DASHBoard: " + name));
		box.add(lastAction);
		top.add(box, BorderLayout.LINE_START);
		controls.setBackground(backgroundColor);
		startButton.setActionCommand("start");
		startButton.addActionListener(this);
		controls.add(startButton);
		controls.add(values);
		values.addMouseListener(this);
		//top.add(controls, BorderLayout.CENTER);    // In general should read available buttons from the agent
		top.add(stateLabel, BorderLayout.LINE_END);
		/*c.fill = GridBagConstraints.HORIZONTAL;
		c.gridx = 0;
		c.gridy = 0;
		pane.add(top, c);*/
		pane.add(top);
		/*c.gridx = 0;
		c.gridy = 1;
		c.weightx = 0.5;
		pane.add(controls, c);*/
		pane.add(controls);
		s2.setLayout(new BoxLayout(s2, BoxLayout.PAGE_AXIS));
		s2.add(new JLabel("Rational"));
		s2.setBorder(BorderFactory.createLineBorder(Color.black));
		s2.setBackground(backgroundColor);
		//s2.setSize(1000,1000);   // see if we can make scrollbars appear.
		s2Scroll = new JScrollPane(s2); //, JScrollPane.VERTICAL_SCROLLBAR_ALWAYS, JScrollPane.HORIZONTAL_SCROLLBAR_ALWAYS);
		s2Scroll.setPreferredSize(new Dimension(200,200));
		/*c.gridx = 0;
		c.gridy = 2;
		c.fill = GridBagConstraints.BOTH;
		c.weightx = 0.5;
		c.weighty = 1;
		pane.add(s2Scroll, c);*/
		pane.add(s2Scroll);
		wme.setLayout(new BorderLayout());
		wme.add(new JLabel("Mem"), BorderLayout.LINE_START);
		/*c.gridx = 0;
		c.gridy = 3;
		c.fill = GridBagConstraints.HORIZONTAL;
		c.weightx = 0.5;
		pane.add(wme, c);*/
		pane.add(wme);
		s1.setLayout(new BoxLayout(s1, BoxLayout.PAGE_AXIS));
		s1.add(new JLabel("Instinctive"));
		s1.setBorder(BorderFactory.createLineBorder(Color.black));
		//s1.setSize(new Dimension(pane.getPreferredSize().width, 500));
		s1.setBackground(Color.white); //new Color(255,255,204);
		/*c.gridx = 0;
		c.gridy = 4;
		c.fill = GridBagConstraints.HORIZONTAL;
		c.weightx = 0.5;
		pane.add(s1, c);*/
		pane.add(s1);
		//pane.add(new JScrollPane(output));
		setSize(getPreferredSize());
		Rectangle abounds = getBounds();
		Rectangle fbounds = df.getContentPane().getBounds();
		df.getContentPane().setBounds(Math.min(abounds.x, fbounds.x), Math.min(abounds.y, fbounds.y),
				Math.max(abounds.width, fbounds.width), Math.max(abounds.height, fbounds.height));  // not everything but should help
		df.validate();
	}
	
	public void updateLastAction(int n, String name) {
		if (name.length() > 10)
			name = name.substring(0,10);
		lastAction.setText(n + ": " + name);
		setSize(getPreferredSize());
		//df.pack();
	}
	
	public void updateOutputs() {
		// May not be efficient - set up a long string with the new.
		String outputString = output.getText();
		List<String>agentOutput = detergent == null ? agent.output.output : detergent.output; 
		for ( ; agentOutputIndex < agentOutput.size(); agentOutputIndex++)
			outputString += agentOutput.get(agentOutputIndex) + "\n";
		output.setText(outputString);
		setSize(getPreferredSize());
	}
	
	public void setState(String description) {
		stateLabel.setText(description);
		setSize(getPreferredSize());
	}
	
	double sliderMax = 0, sliderMin = 0;
	String sliderPred = "";
	public void setPreds(String preds) {
		String[] descriptions = preds.split("\\|\\|");
		for (String description: descriptions) {
			System.out.println("One pred string is " + description);
			if (description.contains("slider")) {
				String[] data = description.substring(description.indexOf("(")+1,description.indexOf(")")).split(",");
				sliderPred = data[0];
				String valueString = description.split("%")[1];
				//controls.remove(values);
				sliderMin = Double.parseDouble(data[2]);
				sliderMax = Double.parseDouble(data[3]);
				double value = Double.parseDouble(valueString);
				// Re-jig so values go from 0 to 100.
				int intVal = (int)(((value-sliderMin)/(sliderMax-sliderMin))*100);
				//System.out.println("Min: " + min + ", max: " + max + ", val: " + value + ", rejigged: " + intVal);
				JSlider slider = new JSlider(JSlider.HORIZONTAL, 0, 100, intVal);
				slider.setMajorTickSpacing(50);
				slider.setMinorTickSpacing(25);
				slider.setPaintTicks(true);
				Hashtable<Integer,JLabel> labelTable = new Hashtable<Integer,JLabel>();
				labelTable.put(new Integer(0), new JLabel("fatigue:low"));  // Need a per-variable solution or leave out
				labelTable.put(new Integer(100), new JLabel("high"));
				slider.setLabelTable(labelTable);
				slider.setPaintLabels(true);
				slider.addChangeListener(this);
				if (sliderPred.equals("fatigue"))
					s2Threshold = 1 - value;
				controls.add(slider);
			} else {
				values.setText(description);
			}
		}
		setSize(getPreferredSize());
	}

	/**
	 * Graphics display for agent - not currently called, using widgets instead.
	 * @param g
	 */
	/*
	public void draw(Graphics g) {
		// For now, a basic string with the name, number of lines, and last line for the agent.
		String lastLine = "", lastAction = "";
		int numberOfActions = 0;
		List<String>output = null, actions = null;
		if (detergent != null) {
			output = detergent.output;
			actions = detergent.actions;
		} else {  // assume agent != null
			output = agent.output.output;
			actions = agent.actions;
		}
		if (output != null) {
			lastLine = output.size() > 0 ? output.get(output.size()-1) : "";
			numberOfActions = actions.size();
			lastAction = actions.size() > 0 ? actions.get(actions.size()-1) : "";
		}
		g.drawString(name + "(" + numberOfActions + "): " + lastAction, left, top);
		g.drawString(lastLine, left + 30, top + 30);
	}
	*/

	@Override
	public void actionPerformed(ActionEvent e) {
		if (e.getActionCommand().equals("start")) {
			System.out.println("Clicking start on " + name);
			if (detergent != null)
				detergent.cognition.addFact("started");  // This is the agent in control of this cognition process
			else  // This is a sub-agent with a separate process, so we communicate through the comms server
				agent.parent.comms.sendMessage(agent.id, "started");
			startButton.setEnabled(false);
		} else if (tf.equals(e.getSource())) {
			// User pressed enter in the value text field. Send a message with the new value
			addFact(curPred + "(" + tf.getText() + ")");
			// Then set back to show all predicates:
			controls.remove(tf);
			controls.add(values);
			setSize(getPreferredSize());
		}
	}
	
	void addFact(String fact) {
		if (detergent != null)
			detergent.cognition.addFact(fact);
		else
			agent.parent.comms.sendMessage(agent.id, fact);
	}

	JTextField tf = null;
	String curPred = "";
	@Override
	public void mouseClicked(MouseEvent e) {
		if (values.equals(e.getComponent())) {
			// Add textfields to change the values of the predicate clicked. Have to parse the predicates from the text
			String[] predVals = values.getText().split(",");
			for (String predVal: predVals) {
				String cpts[] = predVal.split(" = ");
				if (cpts != null && cpts.length > 1) {
					System.out.println("Pred is " + cpts[0] + " and value is " + cpts[1]);
					values.setText(cpts[0] + " = ");
					tf = new JTextField(4);
					tf.setText(cpts[1]);
					tf.addActionListener(this);
					curPred = cpts[0];
					controls.add(tf);
					setSize(getPreferredSize());
				}
			}
		}
	}

	@Override
	public void mouseEntered(MouseEvent arg0) {
	}

	@Override
	public void mouseExited(MouseEvent arg0) {
	}

	@Override
	public void mousePressed(MouseEvent arg0) {
	}

	@Override
	public void mouseReleased(MouseEvent arg0) {
	}

	/**
	 * Show the rules that just fired in the S1 window
	 * @param line
	 */
	public void showS1Rules(String line) {
		s1.removeAll();
		s1.add(new JLabel("Instinctive Layer                                                                                            "));
		double strength = 0;
		String postcond = line.substring(20,line.indexOf(":"));
		List<String>labels = new LinkedList<String>();
		for (String rule: line.substring(line.indexOf(":") + 1).split("\\|")) {
			String[] ruleStrength = rule.split("%");
			String[] preconds = ruleStrength[0].split("and ");
			try {
				strength += Double.parseDouble(ruleStrength[1]);
			} catch (NumberFormatException e) {}
			String label =  "   " + ruleStrength[1] + ":";
			for (String precond: preconds)
				if (!precond.contains("greater") && !precond.contains("attention"))
					label += precond + ", ";
			labels.add(label);
			//s1.setSize(s1.getPreferredSize());
		}
		s1.add(new JLabel(postcond + ", " + strength));
		for (String label: labels)
			s1.add(new JLabel(label));
		s1.revalidate();
		Dimension preferredSize = s1.getPreferredSize();
		if (preferredSize.width < s2.getPreferredSize().width)
			preferredSize.width = s2.getPreferredSize().width;  // keep stretching S1 across the width of the agent.
		//s1.setPreferredSize(preferredSize);
		setSize(getPreferredSize());
	}

	/**
	 * Show some reasoning output from S2.
	 * @param line
	 */
	public void showS2Conclusion(String line) {
		s2.add(new JLabel(line.substring(4)));  // lose the 'S2: ' prefix
		setSize(getPreferredSize());
	}

	@Override
	public void stateChanged(ChangeEvent e) {
		JSlider s = (JSlider)e.getSource();
		if (!s.getValueIsAdjusting()) {
			int intVal = (int)s.getValue();
			double realVal = sliderMin + intVal * (sliderMax-sliderMin) / 100;
			System.out.println("Setting " + sliderPred + " to " + realVal);
			addFact(sliderPred + "(" + realVal + ")");
			if (sliderPred.equals("fatigue"))
				s2Threshold = 1 - realVal;
		}
	}

	/** Decide whether to show a conclusion from S1 in the WM
	 * 
	 * @param line
	 */
	double s2Threshold = 0.4;
	public void processS1Conclusion(String line) {
		String[] factStrength = line.substring(8,line.indexOf("from")).split(",");
		Double strength = 0d;
		try {
			strength = Double.parseDouble(factStrength[1]);
		} catch (NumberFormatException e) {}
		System.out.println("Fact " + factStrength[0] + ", strength " + factStrength[1] + " read as " + strength);
		if (strength > s2Threshold)
			wme.add(new JLabel("    " + factStrength[0]), BorderLayout.CENTER);
	}
	
	/**
	 * Take a series of lines from the prolog cognitive agent, that have been smushed into one line
	 * @param name2
	 */
	public void processS2Messages(String line) {
		for (String s2Line: line.split("\\|")) {
			if (s2Line.startsWith("Project") || s2Line.startsWith("Trigger"))
				processProject(s2Line);
			else 
				System.out.println("Don't recognize S2 line: " + s2Line);
		}
	}

	/** Add the line to the S2 output for the model
	 * 
	 * @param line
	 */
	public void addUtility(String line) {
		String state = line.substring(line.indexOf("["), line.indexOf("]")+1),
			 utility = line.substring(line.lastIndexOf(" ")+1);
		//s2.add(new JLabel("Utility of " + state + " is " + utility));
		// To keep the height reasonable
		s2.add(new JLabel("                                                                                                                                                                           "));
	}

	public void clearUtilities() {
		s2.removeAll();
		s2.add(new JLabel("Rational:"));
	}

	class Transition {
		String action;
		List<String>nextStates;
		public String toString() { return action + "->" + nextStates; }
	}
	HashMap<String,Transition>stateMap = new HashMap<String,Transition>();
	HashSet<String>accessible = new HashSet<String>();
	
	/**
	 * Records the result of projecting an action or trigger. 
	 * States are combined using the map from states to actions and lists of next states 
	 * @param line
	 */
	public void processProject(String line) {
		//System.out.println("Doing process Project on " + line);
		String words[] = line.split(" ");
		Transition t = new Transition();
		String oldWorld = words[3];
		t.action = words[1];
		t.nextStates = new LinkedList<String>();
		String worlds = words[5];
		while (worlds.contains(",")) {
			worlds = worlds.substring(worlds.indexOf(",")+1); // start of state
			String nextState = worlds.substring(0,worlds.indexOf("]")+1);
			worlds = worlds.substring(worlds.indexOf("]")+1);
			if (worlds.contains(","))
				worlds = worlds.substring(worlds.indexOf(",")+1); // get past start of next pair.
			t.nextStates.add(nextState);
			accessible.add(nextState);
		}
		//System.out.println("new worlds are " + words[5] + ", transition is " + t);
		stateMap.put(oldWorld, t);
		repaint();
	}
	

}

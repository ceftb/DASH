/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.detergent;

import java.awt.Container;
import java.awt.Dimension;
import java.awt.Insets;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

import javax.swing.JFrame;

import edu.isi.detergent.Detergent.Agent;

/**
 * Runs a detergent agent within a JFrame, capturing output history and
 * optionally displaying a graphical representation of state. Child agents
 * spawned by the agent are shown in the same frame.
 * @author blythe
 *
 */
public class DFrame extends JFrame {

	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	
	Detergent detergent = null;
	public List<DAgent>agents = new CopyOnWriteArrayList<DAgent>();
	Container top = null;
	int width = 800, height = 800;
	
	static public void main(String[] args){
		new DFrame(null);
	}
	
	public DFrame(Detergent d) {
		this.detergent = d;
		addChild(new DAgent(d, this));
		/*
		Container c = getContentPane();
		c.add(new JPanel(){
			public void paintComponent(Graphics g) {
				paintAgents(g);
			}
		});
		*/
		// Originally stacked the agents. Now would like to set them out according to a clock layout
		//getContentPane().setLayout(new BoxLayout(getContentPane(), BoxLayout.PAGE_AXIS));
		top = getContentPane();
		top.setLayout(null);
		Insets insets = top.getInsets();
		top.setSize(width + insets.left + insets.right, height + insets.top + insets.bottom);
		pack();
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setVisible(true);
	}
	
	/*
	public void paintAgents(Graphics g) {
		for(DAgent dAgent: agents)
			dAgent.draw(g);
	}
	*/

	public void addChild(Agent child) {
		addChild(new DAgent(child, this));
	}
	
	public void addChild(final DAgent dchild) {
		agents.add(dchild);
		// Recompute bounds (on the paint thread to avoid conflicts with paint)
		javax.swing.SwingUtilities.invokeLater(new Runnable() {
			public void run() {
				/*int maxWidth = 0, maxHeight = 0;
				for (DAgent a: agents) {
					if (a.left + 400 > maxWidth)
						maxWidth = a.left + 400;
					if (a.top + 200 > maxHeight)
						maxHeight = a.top + 200;
				}
				setSize(maxWidth, maxHeight);*/
				top.add(dchild);

				Insets insets = top.getInsets();
				Dimension size = dchild.getPreferredSize();
				int[] xs = {width/2, width - size.width, width/2, 0};
				int[] ys = {0, height/2, height - size.height, height/2};
				int x = xs[(agents.size()-1)%4], y = ys[(agents.size()-1)%4];
				dchild.setBounds(x + insets.left, y + insets.top, size.width, size.height);
				//top.add(Box.createRigidArea(new Dimension(0,50))); // This was used with the BoxLayout.
				validate();
				pack();
			}});
	}

}

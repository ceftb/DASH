/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.detergent;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Graphics;
import java.awt.Rectangle;
import java.util.LinkedList;
import java.util.List;

import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;

public class TestScrollPane extends JFrame {
	
	private List<Rectangle>circles = new LinkedList<Rectangle>();
	
	public TestScrollPane() {
		JPanel testPanel = new JPanel(new BorderLayout());
		JPanel top = new JPanel();
		JLabel testLabel = new JLabel("Test");
		top.add(testLabel);
		JPanel drawingPane = new DrawingPane();
		drawingPane.setBackground(Color.white);
		JScrollPane scroller = new JScrollPane(drawingPane);
		scroller.setPreferredSize(new Dimension(200,200));
		testPanel.add(top, BorderLayout.PAGE_START);
		testPanel.add(drawingPane, BorderLayout.CENTER);
		testPanel.setOpaque(true);
		setContentPane(testPanel);
	}
	
	public class DrawingPane extends JPanel {
		private static final long serialVersionUID = 1L;
		protected void paintComponent(Graphics g) {
			super.paintComponent(g);
			for (Rectangle r: circles)
				g.fillOval(r.x, r.y, r.width, r.height);
		}
	}

	public static void main(String[] args) {
		javax.swing.SwingUtilities.invokeLater(new Runnable() {
            public void run() {
                createAndShowGUI();
            }
        });
	}

	protected static void createAndShowGUI() {
		TestScrollPane tsp = new TestScrollPane();
		tsp.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		tsp.pack();
		tsp.setVisible(true);
	}
}

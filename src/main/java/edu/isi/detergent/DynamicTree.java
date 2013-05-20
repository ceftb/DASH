/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
/*
 * Copyright (c) 1995, 2008, Oracle and/or its affiliates. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *   - Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *
 *   - Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in the
 *     documentation and/or other materials provided with the distribution.
 *
 *   - Neither the name of Oracle or the names of its
 *     contributors may be used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */ 

//package components;

/*
 * This code is based on an example provided by Richard Stanford, 
 * a tutorial reader.
 */
package edu.isi.detergent;
import java.awt.GridLayout;
import java.awt.Toolkit;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.List;

import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTree;
import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.DefaultTreeModel;
import javax.swing.tree.MutableTreeNode;
import javax.swing.tree.TreeCellRenderer;
import javax.swing.tree.TreePath;
import javax.swing.tree.TreeSelectionModel;
import javax.swing.event.TreeModelEvent;
import javax.swing.event.TreeModelListener;

public class DynamicTree extends JPanel implements ActionListener {
    /**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	protected DefaultMutableTreeNode rootNode;
    protected DefaultTreeModel treeModel;
    protected JTree tree;
    private Toolkit toolkit = Toolkit.getDefaultToolkit();
    Wizard wizard;
    HashMap<DefaultMutableTreeNode,Object>objects = new HashMap<DefaultMutableTreeNode,Object>();  // keep track because they are lost in editing (should fix this)

    public DynamicTree(String rootName, Wizard wizard) {
    	super(new GridLayout(1,0));
    	
    	this.wizard = wizard;
    	
        rootNode = new DefaultMutableTreeNode(rootName);
        treeModel = new DefaultTreeModel(rootNode);
        treeModel.addTreeModelListener(new MyTreeModelListener());
        tree = new JTree(treeModel);
        tree.setEditable(true);
        tree.getSelectionModel().setSelectionMode
        (TreeSelectionModel.SINGLE_TREE_SELECTION);
        tree.setShowsRootHandles(true);
        
        MouseListener ml = new MouseAdapter() {
            public void mousePressed(MouseEvent e) {
                int selRow = tree.getRowForLocation(e.getX(), e.getY());
                TreePath selPath = tree.getPathForLocation(e.getX(), e.getY());
                if (selRow != -1) {
                    if (e.isPopupTrigger()) {
                    	showNodePopUp((DefaultMutableTreeNode)selPath.getLastPathComponent(), e);
                    }
                }
            }
        };
        tree.addMouseListener(ml);

        JScrollPane scrollPane = new JScrollPane(tree);
        add(scrollPane);
    }

    /** Remove all nodes except the root node. */
    public void clear() {
        rootNode.removeAllChildren();
        treeModel.reload();
    }

	
    /** Remove the currently selected node. */
    public void removeCurrentNode() {
        TreePath currentSelection = tree.getSelectionPath();
        if (currentSelection != null) {
            DefaultMutableTreeNode currentNode = (DefaultMutableTreeNode)
                         (currentSelection.getLastPathComponent());
            MutableTreeNode parent = (MutableTreeNode)(currentNode.getParent());
            if (parent != null) {
                treeModel.removeNodeFromParent(currentNode);
                return;
            }
        } 

        // Either there was no selection, or the root was selected.
        toolkit.beep();
    }

    /** Add child to the currently selected node. */
    public DefaultMutableTreeNode addObject(Object child) {
        DefaultMutableTreeNode parentNode = null;
        TreePath parentPath = tree.getSelectionPath();

        if (parentPath == null) {
            parentNode = rootNode;
        } else {
            parentNode = (DefaultMutableTreeNode)
                         (parentPath.getLastPathComponent());
        }

        return addObject(parentNode, child, true);
    }

    public DefaultMutableTreeNode addObject(DefaultMutableTreeNode parent,
                                            Object child) {
        return addObject(parent, child, false);
    }

    public DefaultMutableTreeNode addObject(DefaultMutableTreeNode parent,
                                            Object child, 
                                            boolean shouldBeVisible) {
        DefaultMutableTreeNode childNode = 
                new DefaultMutableTreeNode(child);

        if (parent == null) {
            parent = rootNode;
        }
	
	//It is key to invoke this on the TreeModel, and NOT DefaultMutableTreeNode
        treeModel.insertNodeInto(childNode, parent, 
                                 parent.getChildCount());

        //Make sure the user can see the lovely new node.
        if (shouldBeVisible) {
            tree.scrollPathToVisible(new TreePath(childNode.getPath()));
        }
        objects.put(childNode, child);
        return childNode;
    }
    
    void showNodePopUp(DefaultMutableTreeNode n, MouseEvent e) {
    }

    class MyTreeModelListener implements TreeModelListener {
        public void treeNodesChanged(TreeModelEvent e) {
        	DefaultMutableTreeNode node;
        	node = (DefaultMutableTreeNode)(e.getTreePath().getLastPathComponent());

        	/*
        	 * If the event lists children, then the changed
        	 * node is the child of the node we've already
        	 * gotten.  Otherwise, the changed node and the
        	 * specified node are the same.
        	 */

        	int index = e.getChildIndices()[0];
        	node = (DefaultMutableTreeNode)(node.getChildAt(index));
        	nodeChanged(node);

        }
        public void treeNodesInserted(TreeModelEvent e) {
        }
        public void treeNodesRemoved(TreeModelEvent e) {
        }
        public void treeStructureChanged(TreeModelEvent e) {
        }
    }

    int newNodeSuffix = 1;
	@Override
	public void actionPerformed(ActionEvent e) {
		String command = e.getActionCommand();
		if ("add".equals(command)) {
			//Add button clicked
			nodeAdded();
		} else if ("remove".equals(command)) {
			//Remove button clicked
			removeCurrentNode();
		} else if ("save".equals(command)) {
			wizard.saveData("a");
		} else if ("save & run".equals(command)) {
			System.out.println("Called save & run");
			wizard.saveData("a");
			wizard.runAgent();
		} else if ("new".equals(command)) {
			wizard.newDomain();
		} else if ("open".equals(command)) {
			wizard.loadDomain();
		} else {
			System.out.println("Command is " + command);
		}
	}
	
	void nodeAdded() {
		addObject("You can edit this node " + newNodeSuffix++);
	}
	
	void nodeChanged(DefaultMutableTreeNode node) {
        System.out.println("Default editor: The user has finished editing the node.");
        System.out.println("New value: " + node.getUserObject());
	}
	
	// Allow some control
	public void setTreeCellRenderer(TreeCellRenderer r) {
		tree.setCellRenderer(r);
	}
	
	public String toString() {
		return nodeAndChildrenToString(rootNode);
	}
	
    private String nodeAndChildrenToString(DefaultMutableTreeNode n) {
    	String result = "";
    	Enumeration<DefaultMutableTreeNode> children = n.children();
    	while (children.hasMoreElements())
    		result += nodeAndChildrenToString(children.nextElement()) + ", ";
    	return n + "{" + result + "}";
	}

	//MariaM
    public DefaultMutableTreeNode addObject(Object child, DefaultMutableTreeNode parentNode) {

        return addObject(parentNode, child, true);
    }

	/**
	 * Returns the node identified by nodeId
	 * @param nodeId
	 * 		the node id (hashCode())
	 */
	DefaultMutableTreeNode getNode(String nodeId){
		List<DefaultMutableTreeNode> n =new ArrayList<DefaultMutableTreeNode>();
		getNode(rootNode,nodeId,n);
		
		DefaultMutableTreeNode foundNode = n.get(0);
		return foundNode;
	}

	/**
	 * Returns the node identified by nodeId
	 * @param n
	 * 		start from the root "rootNode"
	 * @param nodeId
	 * 		the node id (hashCode())
	 * @param foundNode
	 * 		the node with id=nodeId
	 */
	private void getNode(DefaultMutableTreeNode n, String nodeId, List<DefaultMutableTreeNode> foundNode){
		int id = Integer.valueOf(nodeId).intValue();
		//System.out.println("find node");
		if(n.hashCode()==id){
			foundNode.add(n);
			//System.out.println("found");
			return;
		}
		else{
			Enumeration<DefaultMutableTreeNode> children = n.children();
			while(children.hasMoreElements() && foundNode.isEmpty()){
				DefaultMutableTreeNode child = children.nextElement();
				getNode(child,nodeId,foundNode);
			}
		}
	}

    public void removeNode(String id) {
		
		DefaultMutableTreeNode removeThisNode = getNode(id);

        MutableTreeNode parent = (MutableTreeNode)(removeThisNode.getParent());
        if (parent != null) {
                treeModel.removeNodeFromParent(removeThisNode);
                return;
        }
    }
    //End MariaM
}

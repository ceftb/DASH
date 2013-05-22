/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.dash.command;

import javax.servlet.http.HttpServletRequest;

import edu.isi.detergent.Wizard;

public class RenameMentalNodeCommand extends Command{

	Wizard wizard;
	String nodeId;
	String newName;
	public RenameMentalNodeCommand(HttpServletRequest request, Wizard wizard){
		super(request);
		this.wizard=wizard;
		this.nodeId=request.getParameter("nodeId");
		this.newName=request.getParameter("newName");
	}

	@Override
	public String invoke() {
		
		wizard.renameMentalNode(nodeId, newName);
    	String jsonMentalTree = wizard.getJsonForMentalTree();
		
		System.out.println("JT="+ "{ \"json_tree\" : "+ jsonMentalTree+"}");
		
		//return JSON
		return "{ \"json_mental_tree\" : "+ jsonMentalTree+"}";
	}

}

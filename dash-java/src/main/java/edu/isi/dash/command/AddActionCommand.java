/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.dash.command;

import javax.servlet.http.HttpServletRequest;

import edu.isi.detergent.Wizard;

public class AddActionCommand extends Command{

	Wizard wizard;
	String nodeId;
	public AddActionCommand(HttpServletRequest request, Wizard wizard){
		super(request);
		this.wizard=wizard;
		this.nodeId=request.getParameter("nodeId");
	}

	@Override
	public String invoke() {
		
		wizard.addAction(nodeId);
    	String jsonMentalTree = wizard.getJsonForMentalTree();
		
		System.out.println("JT="+ "{ \"json_tree\" : "+ jsonMentalTree+"}");
		
		//return JSON
		return "{ \"json_mental_tree\" : "+ jsonMentalTree+"}";

	}

}

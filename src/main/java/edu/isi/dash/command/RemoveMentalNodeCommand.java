/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.dash.command;

import javax.servlet.http.HttpServletRequest;

import edu.isi.detergent.Wizard;

public class RemoveMentalNodeCommand extends Command{

	Wizard wizard;
	String nodeId;
	public RemoveMentalNodeCommand(HttpServletRequest request, Wizard wizard){
		super(request);
		this.wizard=wizard;
		this.nodeId=request.getParameter("nodeId");
	}

	@Override
	public String invoke() {
		
		wizard.removeMentalNode(nodeId);
		String jsonTree = wizard.getJsonForMentalTree();
		
		System.out.println("JT="+ "{ \"json_mental_tree\" : "+ jsonTree+"}");
		
		//return JSON
		return "{ \"json_mental_tree\" : "+ jsonTree+"}";
		//return "{ \"message\":\""+ "mes"+"\"}";

	}

}

/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.dash.command;

import javax.servlet.http.HttpServletRequest;

import edu.isi.detergent.Wizard;

public class AddConstantCommand extends Command{

	Wizard wizard;
	String nodeId;
	public AddConstantCommand(HttpServletRequest request, Wizard wizard){
		super(request);
		this.wizard=wizard;
		this.nodeId=request.getParameter("nodeId");
	}

	@Override
	public String invoke() {
		
		wizard.addConstant(nodeId);
		String jsonTree = wizard.getJsonTree();
		
		System.out.println("JT="+ "{ \"json_tree\" : "+ jsonTree+"}");
		
		//return JSON
		return "{ \"json_tree\" : "+ jsonTree+"}";
		//return "{ \"message\":\""+ "mes"+"\"}";

	}

}

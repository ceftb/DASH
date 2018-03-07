/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.dash.command;

import javax.servlet.http.HttpServletRequest;

import edu.isi.detergent.Wizard;

public class RenameCommand extends Command{

	Wizard wizard;
	String nodeId;
	String newName;
	public RenameCommand(HttpServletRequest request, Wizard wizard){
		super(request);
		this.wizard=wizard;
		this.nodeId=request.getParameter("nodeId");
		this.newName=request.getParameter("newName");
	}

	@Override
	public String invoke() {
		
		wizard.renameNode(nodeId, newName);
		String jsonTree = wizard.getJsonTree();
		
		System.out.println("JT="+ "{ \"json_tree\" : "+ jsonTree+"}");
		
		//return JSON
		return "{ \"json_tree\" : "+ jsonTree+"}";
		//return "{ \"message\":\""+ "mes"+"\"}";

	}

}

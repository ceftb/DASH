/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.dash.command;

import javax.servlet.http.HttpServletRequest;

import edu.isi.detergent.Wizard;

public class SaveCommand extends Command{

	Wizard wizard;
	String agentName;
	public SaveCommand(HttpServletRequest request, Wizard wizard){
		super(request);
		this.wizard=wizard;
		this.agentName = request.getParameter("agentName");
	}

	@Override
	public String invoke() {
		
		//save agent on server
		wizard.saveData(agentName);
		
		//return JSON
		return "{ \"command_name\":\""+ request.getParameter("command")+"\"}";
	}

}

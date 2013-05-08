/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.dash.command;

import javax.servlet.http.HttpServletRequest;

import edu.isi.detergent.Wizard;

public class NewCommand extends Command{

	Wizard wizard;
	public NewCommand(HttpServletRequest request, Wizard wizard){
		super(request);
		this.wizard=wizard;
	}

	@Override
	public String invoke() {
		
		//save agent on server
		wizard.newDomain();
		
		return "{ \"command_name\":\""+ request.getParameter("command")+"\"}";
	}

}

/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.dash.command;

import javax.servlet.http.HttpServletRequest;

import edu.isi.detergent.Wizard;

public class RunCommand extends Command{

	Wizard wizard;
	public RunCommand(HttpServletRequest request, Wizard wizard){
		super(request);
		this.wizard=wizard;
	}

	@Override
	public String invoke() {
		
		String result = wizard.runAgent();
		
		//return JSON
		return "{ \"run_result\":\""+ result+"\"}";
	}

}

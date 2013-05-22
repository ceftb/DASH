/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.dash.command;

import javax.servlet.http.HttpServletRequest;

import edu.isi.detergent.Wizard;

public class NewMentalCommand extends Command{

	Wizard wizard;
	public NewMentalCommand(HttpServletRequest request, Wizard wizard){
		super(request);
		this.wizard=wizard;
	}

	@Override
	public String invoke() {
		
		//save agent on server
		wizard.newMentalDomain();
		String jsonMentalTree = wizard.getJsonForMentalTree();
				
		System.out.println("JT="+ "{ \"json_mental_tree\" : "+ jsonMentalTree+"}");
		
		//return JSON
		return "{ \"json_mental_tree\" : "+ jsonMentalTree+"}";
	}

}

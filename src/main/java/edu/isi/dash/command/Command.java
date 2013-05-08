/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.dash.command;

import javax.servlet.http.HttpServletRequest;

abstract public class Command {

	HttpServletRequest request;

	public Command(HttpServletRequest request){
		this.request=request;
	}
	
	public abstract String invoke();
}

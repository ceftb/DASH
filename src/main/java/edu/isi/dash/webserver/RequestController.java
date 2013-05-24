/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.dash.webserver;

import java.io.IOException;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import edu.isi.dash.command.AddActionCommand;
import edu.isi.dash.command.AddClauseCommand;
import edu.isi.dash.command.AddConstantCommand;
import edu.isi.dash.command.AddGoalCommand;
import edu.isi.dash.command.AddModelCommand;
import edu.isi.dash.command.AddOperatorCommand;
import edu.isi.dash.command.AddOutcomeCommand;
import edu.isi.dash.command.AddUpdateRuleCommand;
import edu.isi.dash.command.Command;
import edu.isi.dash.command.MakeExecutableCommand;
import edu.isi.dash.command.MakePrimitiveCommand;
import edu.isi.dash.command.NewCommand;
import edu.isi.dash.command.NewMentalCommand;
import edu.isi.dash.command.OpenCommand;
import edu.isi.dash.command.RemoveMentalNodeCommand;
import edu.isi.dash.command.RemoveNodeCommand;
import edu.isi.dash.command.RenameCommand;
import edu.isi.dash.command.RenameMentalNodeCommand;
import edu.isi.dash.command.RunCommand;
import edu.isi.dash.command.SaveCommand;
import edu.isi.detergent.Wizard;


public class RequestController extends HttpServlet{

	private static final long serialVersionUID = 1L;
	
	Wizard wizard;
	
	public void init() throws ServletException {
		wizard = new Wizard("");
	}		

	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {

		//String data1 = request.getParameter("data1");
		//System.out.println("data1="+data1);
		
		String responseString = "{ \"data\" : \"My Agent\" }";
		
		responseString = invokeCommand(request);
			
		response.setCharacterEncoding("UTF-8");
		response.setContentType("application/json");
		response.getWriter().write(responseString);
		response.flushBuffer();
	}

	private String invokeCommand(HttpServletRequest request) {

		String commandName=request.getParameter("command");
		Command cmd = null;
		if(commandName.equals("AddGoalCommand"))
			cmd = new AddGoalCommand(request,wizard);
		if(commandName.equals("AddUpdateRuleCommand"))
			cmd = new AddUpdateRuleCommand(request,wizard);
		if(commandName.equals("AddConstantCommand"))
			cmd = new AddConstantCommand(request,wizard);
		if(commandName.equals("AddClauseCommand"))
			cmd = new AddClauseCommand(request,wizard);
		if(commandName.equals("RenameCommand"))
			cmd = new RenameCommand(request,wizard);
		if(commandName.equals("RemoveNodeCommand"))
			cmd = new RemoveNodeCommand(request,wizard);
		if(commandName.equals("RemoveMentalNodeCommand"))
			cmd = new RemoveMentalNodeCommand(request,wizard);
		if(commandName.equals("MakePrimitiveCommand"))
			cmd = new MakePrimitiveCommand(request,wizard);
		if(commandName.equals("MakeExecutableCommand"))
			cmd = new MakeExecutableCommand(request,wizard);
		if(commandName.equals("SaveCommand"))
			cmd = new SaveCommand(request, wizard);
		if(commandName.equals("OpenCommand"))
			cmd = new OpenCommand(request, wizard);
		if(commandName.equals("NewCommand"))
			cmd = new NewCommand(request, wizard);
		if(commandName.equals("NewMentalCommand"))
			cmd = new NewMentalCommand(request, wizard);
		if(commandName.equals("RunCommand"))
			cmd = new RunCommand(request, wizard);
		if(commandName.equals("RenameMentalNodeCommand"))
			cmd = new RenameMentalNodeCommand(request,wizard);
		if(commandName.equals("AddOutcomeCommand"))
			cmd = new AddOutcomeCommand(request, wizard);
		if(commandName.equals("AddModelCommand"))
			cmd = new AddModelCommand(request, wizard);
		if(commandName.equals("AddOperatorCommand"))
			cmd = new AddOperatorCommand(request, wizard);
		if(commandName.equals("AddActionCommand"))
			cmd = new AddActionCommand(request, wizard);
		
		return cmd.invoke();
	}

}

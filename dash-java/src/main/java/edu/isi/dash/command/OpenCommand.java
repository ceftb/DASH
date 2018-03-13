/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.dash.command;

import java.io.File;

import javax.servlet.http.HttpServletRequest;

import edu.isi.detergent.Wizard;

public class OpenCommand extends Command{

	Wizard wizard;
	String fileName;
	File uploadedFile;
	public OpenCommand(HttpServletRequest request, Wizard wizard){
		super(request);
		this.wizard=wizard;
		this.uploadedFile=FileUtil.downloadFileFromHTTPRequest(request);
		this.fileName = uploadedFile.getName();
	}

	@Override
	public String invoke() {
		
		wizard.newDomain();
		wizard.newMentalDomain();
		wizard.loadDomain(fileName);
		String jsonTree = wizard.getJsonTree();
		String jsonMentalTree = wizard.getJsonForMentalTree();
		
		System.out.println("JT="+ "{ \"json_tree\" : "+ jsonTree+ ",\"json_mental_tree\" : "+ jsonMentalTree+"}");
		
		//return JSON
		return "{ \"json_tree\" : "+ jsonTree+ ",\"json_mental_tree\" : "+ jsonMentalTree+"}";
		//return "{ \"message\":\""+ "mes"+"\"}";
	}

}

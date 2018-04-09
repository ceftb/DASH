/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.dash.command;

import java.io.File;
import java.util.Iterator;
import java.util.List;

import javax.servlet.http.HttpServletRequest;

import org.apache.commons.fileupload.FileItem;
import org.apache.commons.fileupload.FileUploadException;
import org.apache.commons.fileupload.disk.DiskFileItemFactory;
import org.apache.commons.fileupload.servlet.ServletFileUpload;


public class FileUtil {
	private static String DESTINATION_DIR_PATH = "lib/logic/";
	
	static public File downloadFileFromHTTPRequest (HttpServletRequest request) {
		// Download the file to the upload file folder
		File destinationDir = new File(DESTINATION_DIR_PATH);
		if(!destinationDir.isDirectory()) {
			destinationDir.mkdir();
		}
		
		DiskFileItemFactory  fileItemFactory = new DiskFileItemFactory ();

		// Set the size threshold, above which content will be stored on disk.
		fileItemFactory.setSizeThreshold(1*1024*1024); //1 MB

		//Set the temporary directory to store the uploaded files of size above threshold.
		fileItemFactory.setRepository(destinationDir);
 
		ServletFileUpload uploadHandler = new ServletFileUpload(fileItemFactory);
		
		File uploadedFile = null;
		try {
			// Parse the request
			@SuppressWarnings("rawtypes")
			List items = uploadHandler.parseRequest(request);
			@SuppressWarnings("rawtypes")
			Iterator itr = items.iterator();
			while(itr.hasNext()) {
				FileItem item = (FileItem) itr.next();

				// Ignore Form Fields.
				if(item.isFormField()) {
					// Do nothing
				} else {
					//Handle Uploaded files. Write file to the ultimate location.
					uploadedFile = new File(destinationDir,item.getName());
					item.write(uploadedFile);
				}
			}
		} catch(FileUploadException ex) {
			System.out.println("Error encountered while parsing the request"+ex.toString());
		} catch(Exception ex) {
			System.out.println("Error encountered while uploading file"+ex.toString());
		}
		return uploadedFile;
	}

}

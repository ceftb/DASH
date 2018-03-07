/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.dash.webserver;

import java.util.ArrayList;
import java.util.Enumeration;

import javax.servlet.ServletContext;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;

public class ServerStart extends HttpServlet {
	private static final long serialVersionUID = 1L;

	// private static Logger logger = LoggerFactory.getLogger(ServerStart.class);

	public void init() throws ServletException {
		// Populate the ServletContextParameterMap data structure
		// Only the parameters that are specified in the
		// ServletContextParameterMap are valid. So, to use a context init
		// parameter, add it to the ServletContextParameterMap
		ServletContext ctx = getServletContext();
		Enumeration<?> params = ctx.getInitParameterNames();

		System.out.println("************");
		System.out.println("Server start servlet initialized successfully..");
		System.out.println("***********");

	}		
}

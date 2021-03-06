/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.detergent;

import java.net.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.io.*;

/**
 * This is not part of an agent, but forms a central point
 * for communications. It also keeps central time.
 * @author blythe
 *
 */
public class CommServer {
	public static int port = 4789;
	public static boolean listening = true;
	static HashMap<Integer,List<String>>messages = new HashMap<Integer,List<String>>();
	static HashMap<String,String>variables = new HashMap<String,String>();
	static long startTime = System.currentTimeMillis();
	
    public static WorldLogic worldLogic = null;
    
	/**
	 * Each connection is served in a ClientThread
	 * @author blythe
	 *
	 */
	static class ClientThread extends Thread {
		Socket clientSocket = null;
		Integer id = null;
		
		public ClientThread(Socket socket) {
            System.out.println("Constructor called for ClientThread.\n");
			clientSocket = socket;
		}
		
		public void run() {
	        try {
	        	PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true);
	        	BufferedReader in = new BufferedReader(
	        			new InputStreamReader(clientSocket.getInputStream()));
	        	String inputLine;
	        	
	        	while ((inputLine = in.readLine()) != null && !inputLine.equals("bye") && !inputLine.equals("die")) {
	        		out.println(processInput(inputLine));
	        	}
	        	if (inputLine != null && inputLine.equals("die"))
	        		listening = false;
	        	out.close();
	        	in.close();
	        	clientSocket.close();
	        } catch (IOException e) {
				e.printStackTrace();
			}
			
		}
		
		private String processInput(String inputLine) {
			// First line usually tells us who the agent is on this socket
			if (inputLine.startsWith("id")) {
                System.out.println("Line starting with id received.\n");
				id = Integer.parseInt(inputLine.substring(3));
				if (!messages.containsKey(id))
					messages.put(id, new ArrayList<String>());
                System.out.println("Adding agent " + id + " to world logic.\n");
                worldLogic.addAgent(id);
                System.out.println("Added agent " + id + " to world logic.\n");
				return "ok";
            } else if (inputLine.startsWith("action")) {
				System.out.println(id + ": " + inputLine);
 
                String action = inputLine.substring(7);
				return worldLogic.processAction(action, id);
			} else if (inputLine.startsWith("send")) {
				// queue a message for another agent
				System.out.println(id + ": " + inputLine);
				Integer recipient = Integer.parseInt(inputLine.substring(5, inputLine.indexOf(" ",5)));
				if (!messages.containsKey(recipient))
					messages.put(recipient, new ArrayList<String>());
				messages.get(recipient).add(inputLine.substring(inputLine.indexOf(" ", 5)+1));
				return "ok";
			} else if (inputLine.startsWith("check")) {
				// send any messages queued for this agent
				List<String>myMessages = messages.get(id);
                
                // query prolog for unprocessed observations
                String observations = worldLogic.getObservations(id);
                System.out.println("Got observations: " + observations + ".\n");
                
                if (observations != null)
                    myMessages.add(observations);
                else
                    System.out.println("Uhoh! getObservations returned null. This should never happen!\n");
                
				if (myMessages == null || myMessages.isEmpty())
					return "0";
				else {
					String messageString = "" + myMessages.size() + "|";
					for (String message: myMessages) {
						messageString += message + "|";
					}
					myMessages.clear();
					System.out.println("Check from " + id + ": " + messageString);
					return messageString;
				}
			} else if (inputLine.equals("getTime")) {
				return "" + (System.currentTimeMillis() - startTime);
			} else if (inputLine.startsWith("set")) {    // The next two commands implement a variable where agents can communicate behavior
				String[] words = inputLine.split(" ");
				variables.put(words[1], words[2]);
				return "1";
			} else if (inputLine.startsWith("get")) {
				String[] words = inputLine.split(" ");
				if (variables.containsKey(words[1]))
					return variables.get(words[1]);
				else
					return "NoVal";
			} else
				return "what?";
		}

	}

	/**
	 * The main loop waits for connections and spawns ClientThreads.
	 * @param args
	 */
	public static void main(String[] args) {
		ServerSocket serverSocket = null;
        
        worldLogic = new WorldLogic(args);  // pass remaining args as files to load into WorldLogic
        
		try {
			serverSocket = new ServerSocket(port);
		} catch (IOException e) {
			System.err.println("Could not listen on port: " + port + ".");
			System.exit(1);
		}
		
        
		System.out.println("Detergent server version 0.1, listening on " + port);
		try {
			while (listening)
				new ClientThread(serverSocket.accept()).start();
			serverSocket.close();
		} catch (IOException e) {
			System.err.println("Accept failed.");
		}

	}

}

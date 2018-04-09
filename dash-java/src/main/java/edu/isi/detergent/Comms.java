/*******************************************************************************
 * Copyright University of Southern California
 ******************************************************************************/
package edu.isi.detergent;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;

/**
 * This is the part of the agent that handles communication with other agents via the CommServer
 * @author blythe
 *
 */
public class Comms {
	public String hostname = "localhost";
	public int port = 4789;
	private Socket socket = null;
	private PrintWriter out = null;
	private BufferedReader in = null;
	public boolean isConnected = false;
	
	public void connect(int id, String hostname, int port) {
		this.hostname = hostname;
		this.port = port;
		try {
			socket = new Socket(hostname, port);
			out = new PrintWriter(socket.getOutputStream());
			in = new BufferedReader(new InputStreamReader(socket.getInputStream()));
			sendAndRead("id " + id);
			isConnected = true;
		} catch (UnknownHostException e) {
			System.out.println("Unknown host for communication: " + hostname);
		} catch (IOException e) {
			System.out.println("IO exception looking for communications host");
		}
	}
	
	/**
	 * Check the server for messages.
	 * @return
	 */
	public String[] checkMessages() {
		String messageData = sendAndRead("check");
		if (!"0".equals(messageData) && messageData != null) {
			//System.out.println("Got a message: " + messageData);
			return messageData.split("\\|");
		} else {
			return null;
		}

	}
    
    /**
     * Submits chosen action to the server. The server can then
     * generate an appropriate result for the action and also
     * generate the appropriate observables that are relayed to
     * agents via checkMessages.
     *
     * @param action
     * @return
     */
    public String submitAction(String actionString) {
        System.out.println("Submitting action " + actionString + " to server.\n");
        return sendAndRead("action " + actionString);
    }
    
	
	/**
	 * Sends a message to another agent with the given id. This is logged
	 * in the server and picked up when the recipient does a 'check'.
	 * @param id
	 * @param message
	 * @return
	 */
	public String sendMessage(int id, String message) {
		return sendAndRead("send " + id + " " + message);
	}
	
	public String getValue(String variable) {
		return sendAndRead("get " + variable);
	}
	
	public String setValue(String variable, String value) {
		return sendAndRead("set " + variable + " " + value);
	}
	
	private String sendAndRead(String message) {
		//System.out.println("Sending message '" + message + "'");
		if (out == null)
			return null;
		out.println(message);
		out.flush();
		try {
			return in.readLine();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			return null;
		}
	}
	
	public void shutdown() {
		out.close();
		try {
			in.close();
			socket.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	/**
	 * To test connections without the whole agent
	 * @param args
	 */
	public static void main(String[] args) {
		String host = args[0];
		int port = Integer.parseInt(args[1]);
		System.out.println("Connecting to " + host + " on port " + port);
		Comms c = new Comms();
		c.connect(56, host, port);
		c.checkMessages();
		c.sendMessage(56, "hello me");
		try {
			Thread.sleep(1000);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		c.checkMessages();
	}

	public int getTick() {
		String data = sendAndRead("getTime");
		if (data != null)
			return Integer.parseInt(data);
		return -1;
	}
}

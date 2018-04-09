package edu.isi.detergent;

import jpl.Atom;
import jpl.Compound;
import jpl.Integer;
import jpl.Query;
import jpl.Term;
import jpl.Variable;
import jpl.Util;
import java.util.Hashtable;

public class WorldLogic {
	
	public static String worldLogicFile = "worldLogic.pl";
	public static String prologRoot = "lib/logic";
    
    // calls the general constructor with a default filename (currently, we assume lib/logic as default directory)
    public WorldLogic() {
        this(worldLogicFile);
    }
    
    public WorldLogic(String[] files) {
    	this(worldLogicFile);
    	if (files != null) {
    		for (String file: files) {
    			loadFile(file);
    		}
    	}
    }
    
    // consults the specified file
    public WorldLogic(String filename) {
    	loadFile(filename);
    }
    
    private void loadFile(String filename) {
        //Query consultQuery = new Query("consult('logic.pl')");
        Query consultQuery = new Query("consult", new Term[] {new Atom(prologRoot + "/" + filename)});
        
        if (!consultQuery.hasSolution()) {
            System.out.println("Failed to consult logic file " + filename + ". Exiting.\n");
            System.exit(1);
        } else {
            System.out.println("Successfully consulted " + filename + ".\n");
        }
    }
    
    // adds agent to the knowledge base
    public synchronized int addAgent(int id) {
        System.out.println("WorldLogic: addAgent: Attempting to add agent " + id + " to knowledge base.\n");

        try {
            Term assertTerm = jpl.Util.textToTerm("assert(id(" + id + "))");
            Query assertQuery = new Query(assertTerm);
            
            if (assertQuery.hasSolution()) {
                assertQuery.close();
                System.out.println("WorldLogic: addAgent: successfully added agent " + id + "'s id to knowledge base.\n");
            } else {
                assertQuery.close();
                System.out.println("WorldLogic: addAgent: error: could not add agent " + id + "'s id state to knowledge base.\n");
                return 1;
            }
        } catch (Exception E) {
            System.out.println("WorldLogic: addAgent: error: could not add agent " + id + "'s state to knowledge base.\n");
            return 1;
        } /*catch (Exception e) {
        	System.out.println("WorldLogic: addAgent: non-prolog error: could not add agent " + id + " to knowledge base.\n");
        	e.printStackTrace();
        	return 1;
        }*/
        
        try {
            
            Term assertTerm = jpl.Util.textToTerm("assert(observations(" + id + ", []))");
            Query assertQuery = new Query(assertTerm);
            
            if (assertQuery.hasSolution()) {
                assertQuery.close();
                System.out.println("WorldLogic: addAgent: successfully added agent " + id + "'s state to knowledge base.\n");
                return 0;
            } else {
                assertQuery.close();
                System.out.println("WorldLogic: addAgent: error: could not add agent " + id + "'s state to knowledge base.\n");
                return 1;
            }
        } catch (jpl.PrologException E) {
            System.out.println("WorldLogic: addAgent: error: could not add agent " + id + "'s state to knowledge base.\n");
            return 1;
        }
    }
    
    // processes the given action, generating a result and appropriate observations
    public synchronized String processAction(String action, java.lang.Integer id) {
        System.out.println("WorldLogic: processAction called with action " + action + " and id " + id + "\n");

        try {
            // generate processQuery here to process the action and return a result
            Term processTerm = jpl.Util.textToTerm("processAction" + "(" + action + "," + id + "," + "R)");
            Query processQuery = new Query(processTerm);
        
            if (processQuery.hasMoreElements()) {
                Term result = ((Term) ((Hashtable) processQuery.nextElement()).get("R"));
                processQuery.close();
                return jpl.Term.toString(new Term[] {result});
            } else {
                processQuery.close();
                System.out.println("WorldLogic: processAction: error: could not process action " + action + " by agent " + id + ".\n");
                return "fail";
            }
        } catch (Exception E) {
            System.out.println("WorldLogic: processAction: error: could not process action " + action + " by agent " + id + ".\n");
            return "fail";
        }
    }
    
    public synchronized String getObservations(java.lang.Integer id) {
        System.out.println("WorldLogic: getObservations called with id " + id + "\n.");
        
        try {
            Term obsTerm = jpl.Util.textToTerm("getObservations(" + id + ", Obs)");
            Query obsQuery = new Query(obsTerm);
        
            if (obsQuery.hasMoreElements()) {
                Term result = ((Term) ((Hashtable) obsQuery.nextElement()).get("Obs"));
                obsQuery.close();
                return jpl.Term.toString(new Term[] {result});
            } else {
                obsQuery.close();
                System.out.println("WorldLogic: getObservations: error: could not get observations for agent " + id + ".\n");
                return null;
            }
        } catch (Exception E) {
            System.out.println("WorldLogic: getObservations: error: could not get observations for agent " + id + ".\n");
            return null;
        }
    }

}
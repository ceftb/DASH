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
    
    // calls the general constructor with a default filename (currently, we assume lib/logic as defualt directory)
    public WorldLogic() {
        this("worldLogic.pl");
    }
    
    // consults the specified file
    public WorldLogic(String filename) {
        String prologRoot = "lib/logic";

        //Query consultQuery = new Query("consult('logic.pl')");
        Query consultQuery = new Query("consult", new Term[] {new Atom(prologRoot + "/" + filename)});
        
        if (!consultQuery.hasSolution()) {
            System.out.println("Failed to consult worldLogic.pl. Exiting.\n");
            System.exit(1);
        } else {
            System.out.println("Successfully consulted worldLogic.pl.\n");
        }
    }
    
    // adds agent to the knowledge base
    public synchronized int addAgent(int id) {
        System.out.println("WorldLogic: addAgent: Attempting to add agent " + id + " to knowledge base.\n");
        try {
            Term assertTerm = jpl.Util.textToTerm("assert(id(" + id + "))");
            Query assertQuery = new Query(assertTerm);
            
            if (!assertQuery.hasSolution()) {
                System.out.println("WorldLogic: addAgent: error: could not add agent " + id + " to knowledge base.\n");
                return 1;
            }
        } catch (jpl.PrologException E) {
            System.out.println("WorldLogic: addAgent: error: could not add agent " + id + " to knowledge base.\n");
            return 1;
        }
        
        System.out.println("WorldLogic: addAgent: cp1.\n");
        
        try {
            Term assertTerm = jpl.Util.textToTerm("assert(observations(" + id + ", []))");
            Query assertQuery = new Query(assertTerm);
            
            if (assertQuery.hasSolution()) {
                System.out.println("WorldLogic: addAgent: successfully added agent " + id + " to knowledge base.\n");
                return 0;
            } else {
                System.out.println("WorldLogic: addAgent: error: could not add agent " + id + " to knowledge base.\n");
                return 1;
            }
        } catch (jpl.PrologException E) {
            System.out.println("WorldLogic: addAgent: error: could not add agent " + id + " to knowledge base.\n");
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
                return jpl.Term.toString(new Term[] {result});
            } else {
                System.out.println("WorldLogic: processAction: error: could not process action " + action + " by agent " + id + ".\n");
                return "fail";
            }
        } catch (jpl.PrologException E) {
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
                return jpl.Term.toString(new Term[] {result});
            } else {
                System.out.println("WorldLogic: getObservations: error: could not get observations for agent " + id + ".\n");
                return null;
            }
        } catch (jpl.PrologException E) {
            System.out.println("WorldLogic: getObservations: error: could not get observations for agent " + id + ".\n");
            return null;
        }
    }

}
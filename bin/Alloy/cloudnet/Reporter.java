/* Copyright (c) 2019, Orange
 *
 * Software Name : Cloudnet TOSCA toolbox 
 * Version: 1.0
 *
 * SPDX-FileCopyrightText: Copyright (c) 2020 Orange
 * SPDX-License-Identifier: MIT License
 *
 * This software is distributed under the Apache Licen
 * the text of which is available at https://mit-license.org
 * or see the "MIT-LICENSE.txt" file for more details.
 *
 * Author: Philippe Merle <philippe.merle@inria.fr>
 * Software description: TOSCA to Cloudnet Translator
 *
 */

package cloudnet;

import edu.mit.csail.sdg.alloy4.A4Reporter;
import edu.mit.csail.sdg.alloy4.ErrorWarning;
import edu.mit.csail.sdg.ast.Command;

// Alloy4 sends diagnostic messages and progress reports to the A4Reporter.
public final class Reporter extends A4Reporter {

    static public String RED = "\33[31m";
    static public String BLACK = "\33[0m";

    void trace(String method, String msg) {
        //                System.out.println("[" + method + "] " + msg);
        System.out.println("  " + msg);
    }

    @Override
    public void debug(String msg) {
        //                trace("debug", msg);
    }

    @Override
    public void parse(String msg) {
        //                trace("parse", msg);
    }

    @Override
    public void typecheck(String msg) {
        //                trace("typecheck", msg);
    }

    @Override public void warning(ErrorWarning msg) {
        System.err.print("Relevance Warning:\n"+(msg.toString().trim())+"\n\n");
        System.err.flush();
    }

    @Override
    public void scope(String msg) {
        //                trace("scope", msg);
    }

    @Override
    public void bound(String msg) {
        //                trace("bound", msg);
    }

    @Override
    public void translate(String solver, int bitwidth, int maxseq, int skolemDepth, int symmetry) {
        trace("translate", "Solver=" + solver + " Bitwidth=" + bitwidth + " MaxSeq=" + maxseq + " SkolemDepth=" + skolemDepth + " Symmetry=" + (symmetry > 0 ? ("" + symmetry) : "OFF"));
    }

    @Override
    public void solve(int primaryVars, int totalVars, int clauses) {
        trace("solve", totalVars + " vars. " + primaryVars + " primary vars. " + clauses + " clauses.");
    }

    @Override
    public void resultCNF(String filename) {}

    @Override
    public void resultSAT(Object command, long solvingTime, Object solution) {
        if (!(command instanceof Command))
            return;
        Command cmd = (Command) command;
        StringBuffer sb = new StringBuffer();
        if (cmd.expects == 0)
            sb.append(RED);
        sb.append(cmd.check ? "Counterexample found. " : "Instance found. ");
        if (cmd.check)
            sb.append("Assertion is invalid");
        else
            sb.append("Predicate is consistent");
        if (cmd.expects == 0)
            sb.append(", contrary to expectation");
        else if (cmd.expects == 1)
            sb.append(", as expected");
        sb.append(". " + solvingTime + "ms.");
        if (cmd.expects == 0)
            sb.append(BLACK);
        trace("resultSAT", sb.toString());
    }

    @Override
    public void resultUNSAT(Object command, long solvingTime, Object solution) {
        if (!(command instanceof Command))
            return;
        Command cmd = (Command) command;
        StringBuffer sb = new StringBuffer();
        if (cmd.expects == 1)
            sb.append(RED);
        sb.append(cmd.check ? "No counterexample found." : "No instance found.");
        if (cmd.check)
            sb.append(" Assertion may be valid");
        else
            sb.append(" Predicate may be inconsistent");
        if (cmd.expects == 1)
            sb.append(", contrary to expectation");
        else if (cmd.expects == 0)
            sb.append(", as expected");
        sb.append(". " + solvingTime + "ms.");
        if (cmd.expects == 1)
            sb.append(BLACK);
        trace("resultUNSAT", sb.toString());
    }
}

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
import edu.mit.csail.sdg.ast.Command;
import edu.mit.csail.sdg.ast.Module;
import edu.mit.csail.sdg.translator.A4Options;
import edu.mit.csail.sdg.translator.A4Options.SatSolver;
import edu.mit.csail.sdg.translator.A4Solution;
import edu.mit.csail.sdg.translator.TranslateAlloyToKodkod;

/** This class executes all commands of all given Alloy files. */
public final class BenchmarkSolver extends Parse {

    /*
     * Execute every command in every file.
     *
     * This method parses every file, then execute every command.
     */
    public static void main(String[] args) {

        SatSolver solvers[] = {
            SatSolver.MiniSatJNI,
//            SatSolver.MiniSatProverJNI, // Too very slow!
//            SatSolver.LingelingJNI, // Too very slow!
//            SatSolver.PLingelingJNI, // Cannot run program "plingeling"!
            SatSolver.GlucoseJNI,
            SatSolver.Glucose41JNI
//            SatSolver.CryptoMiniSatJNI, // Could not load the library libcryptominisat.dylib
//            SatSolver.SAT4J // Too very slow!
        };
        A4Reporter reporter = new A4Reporter();

        for(String filename: args) {
            Module world = parse(filename);
            if (world != null) {
                for (Command command: world.getAllCommands()) {
                    System.out.println("Executing " + ( command.check ? "check" : "run" ) + " " + command.label + "...");
                    for (SatSolver solver: solvers) {
                        // Choose some default options for how you want to execute the commands
                        A4Options options = new A4Options();
                        options.solver = solver;
                        options.skolemDepth=1;
                        options.symmetry=20;

                        // Execute the command
                        System.out.print("  - with " + solver.id());
                        long tb = java.lang.System.currentTimeMillis();
                        A4Solution ans = TranslateAlloyToKodkod.execute_command(reporter, world.getAllReachableSigs(), command, options);
                        long te = java.lang.System.currentTimeMillis();
                        System.out.println(" in " + (te-tb) + " milliseconds");
                        if (ans.satisfiable()) {
                        // TODO
                        } else {
                        // TODO
                        }
                    }
                }
            }
        }
    }
}

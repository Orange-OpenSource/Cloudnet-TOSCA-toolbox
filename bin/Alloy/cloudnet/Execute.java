/* Copyright (c) 2019-21, Orange
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

import edu.mit.csail.sdg.alloy4.Pair;
import edu.mit.csail.sdg.alloy4.Pos;
import edu.mit.csail.sdg.ast.Command;
import edu.mit.csail.sdg.ast.Module;
import edu.mit.csail.sdg.translator.A4Options;
import edu.mit.csail.sdg.translator.A4Solution;
import edu.mit.csail.sdg.translator.TranslateAlloyToKodkod;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.Set;
import java.util.regex.Pattern;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;

/** This class executes all commands of all given Alloy files. */
public final class Execute extends Parse {

    /*
     * Execute every command in every file.
     *
     * This method parses every file, then execute every command.
     */
    public static void main(String[] args) {

        Options options = new Options();
        options.addOption("c", "commands", true, "commands to execute, expressed as a regular expression, default is .*");
        CommandLineParser parser = new DefaultParser();
        CommandLine cmd;
        try {
            cmd = parser.parse( options, args);
        } catch( ParseException exp ) {
            // oops, something went wrong
            System.err.println( "Parsing failed.  Reason: " + exp.getMessage() );
            return;
        }
        String commands = cmd.getOptionValue("c", ".*");

        // Choose some default options for how you want to execute the commands
        A4Options a4options = new A4Options();
        a4options.solver = A4Options.SatSolver.Glucose41JNI;
        a4options.skolemDepth=1;
        a4options.symmetry=20;

        for(String filename: cmd.getArgs()) {
            Module world = parse(filename);
            if (world != null) {
                for (Command command: world.getAllCommands()) {
                    if (Pattern.matches(commands, command.label)) {
                        // Execute the command
                        System.out.println("Executing " + ( command.check ? "check" : "run" ) + " " + command.label + "...");
                        A4Solution ans = TranslateAlloyToKodkod.execute_command(reporter, world.getAllReachableSigs(), command, a4options);
                        if (! reporter.is_solved) {
                          System.err.println(Reporter.RED);
                          System.err.println("  Execution failed because the scope is certainly too small!");
                          System.err.println(Reporter.BLACK);
                          continue; // go to next command
                        }
                        if (! ans.satisfiable()) {
                            A4Options a4options_unsat = new A4Options();
                            a4options_unsat.solver = A4Options.SatSolver.MiniSatProverJNI;
                            a4options_unsat.skolemDepth=1;
                            a4options_unsat.symmetry=20;
                            a4options_unsat.coreMinimization=0;
                            a4options_unsat.coreGranularity=3;
                            ans = TranslateAlloyToKodkod.execute_command(reporter, world.getAllReachableSigs(), command, a4options_unsat);
                            System.err.println(Reporter.RED + "  Unsat core:");
                            Pair<Set<Pos>,Set<Pos>> highLevelCore = ans.highLevelCore();
                            for(Pos pos : highLevelCore.a) {
                                System.err.println("  - " + pos.filename + " from line " + pos.y + " column " + pos.x + " to line " + pos.y2 + " column " + pos.x2);
                                display_text_file(pos.filename, pos.y, pos.y2);
                            }
                            for(Pos pos : highLevelCore.b) {
                                System.err.println("  - " + pos.filename + " from line " + pos.y + " column " + pos.x + " to line " + pos.y2 + " column " + pos.x2);
                                display_text_file(pos.filename, pos.y, pos.y2);
                            }
                            System.err.println(Reporter.BLACK);
                        }
                    }
                }
            }
        }
    }

    static void display_text_file(String filename, int start, int end) {
        try {
            InputStream is = null;
            if(filename.startsWith("/$alloy4$/")) {
                is = Execute.class.getClassLoader().getResourceAsStream(filename.substring("/$alloy4$/".length()));
            } else {
                is = new FileInputStream(filename);
            }
            InputStreamReader isr = new InputStreamReader(is);
            BufferedReader br = new BufferedReader(isr);
            for (int i=1; i<start; i++) {
                br.readLine();
            }
            for (int i=start; i<=end; i++) {
                String line = br.readLine();
                System.out.println("    " + line);
            }
            br.close();
            isr.close();
            is.close();
        } catch (Exception e){
            e.printStackTrace();
        }
    }
}

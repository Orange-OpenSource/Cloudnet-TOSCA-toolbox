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

import edu.mit.csail.sdg.alloy4.Err;
import edu.mit.csail.sdg.ast.Module;
import edu.mit.csail.sdg.parser.CompUtil;

/** This class parses Alloy files. */
public class Parse {
    // Alloy4 sends diagnostic messages and progress reports to the A4Reporter.
    static public Reporter reporter = new Reporter();

    /*
     * Parse one file.
     *
     * This method parses one file.
     */
    public static Module parse(String filename) {

        // Parse+typecheck the model
        System.out.println("Parsing and typechecking " + filename + "...");
        try {
            return CompUtil.parseEverything_fromFile(reporter, null, filename);
        } catch(Err err) {
            System.err.println(reporter.RED + err.toString() + reporter.BLACK);
            return null;
        }
    }

    /*
     * Parse every file.
     *
     * This method parses every file.
     */
    public static void main(String[] args) {
        for(String filename: args) {
            parse(filename);
        }
    }
}

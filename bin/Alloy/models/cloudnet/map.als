/******************************************************************************
 *
 * Software Name : Cloudnet TOSCA toolbox 
 * Version: 1.0
 * SPDX-FileCopyrightText: Copyright (c) 2020 Orange
 * SPDX-License-Identifier: Apache-2.0
 *
 * This software is distributed under the Apache License 2.0
 * the text of which is available at http://www.apache.org/licenses/LICENSE-2.0
 * or see the "LICENSE-2.0.txt" file for more details.
 *
 * Author: Philippe Merle (INRIA) <philippe.merle@inria.fr>
 *
 * Specification of map.
 *
*******************************************************************************/

module map[VALUE]

sig Map {
  entries:  String -> lone VALUE
}

fun Map.keys[] : set String
{
  this.entries.VALUE
}

fun Map.elems[] : set VALUE
{
  String.(this.entries)
}

fun Map.entry[key: one String] : one VALUE
{
  (this.entries[key])
}

pred Map.empty[]
{
  no this.entries
}

pred Map.size[size : one Int]
{
  // ISSUE: Currently commented as SAT solving takes too time :-(
  // #this.entries = size
}

pred Map.min_length[length : one Int]
{
  // ISSUE: Currently commented as SAT solving takes too time :-(
//  #this.entries >= length
}

pred Map.entry_schema_type[type: set VALUE]
{
  // ISSUE: Currently commented as generating CNF takes too time :-(
  // this.elems in type
}

pred Map.one_entry[key: one String]
{
  one this.entry[key]
}

pred Map.keys[k: set String]
{
  this.keys = k
}

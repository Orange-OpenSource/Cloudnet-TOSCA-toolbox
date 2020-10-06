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
 * Authors:
 * - Philippe Merle (INRIA) <philippe.merle@inria.fr>
 * - Jean-Bernard Stefani (INRIA) <jean-bernard.stefani@inria.fr>
 *
 * A formal specification of Location Graphs in Alloy.
 *
*******************************************************************************/

module LocationGraphs

/*******************************************************************************
 * Location graphs: elements
 ******************************************************************************/

sig LocationGraph {
  locations : set Location
}

sig Location {
  name : one Name,
  process : one Process,
  sort : one Sort,
  provided : set Role,
  required : set Role
}
{ no ( provided & required ) } // In a location, provided roles and required roles are disjoint.

sig Value {}
sig Name extends Value {} 
sig Role extends Value {}


sig Process extends Value {
   patoms : set Name + Role
}

sig Sort extends Value {
  satoms : set Name + Role 
}


one sig Null extends LocationGraph {}

fact NullHasNoLocations {
  no Null.locations
}



/*******************************************************************************
 * Location graphs: static semantics
 ******************************************************************************/

/** Locations in a location graph are uniquely named. */

pred UniquelyNamedLocations[c : set Location] {
  no disj c1, c2 : c | c1.name = c2.name
}


/** A role is provided by a single location. */

pred UniquelyProvidedRoles[c : set Location] {
  no disj l, h : c | some l.provided & h.provided
}


/** A role is required by a single location. */

pred UniquelyRequiredRoles[c : set Location] {
  no disj l, h : c | some l.required & h.required
}


/** Well-formedness for  location graphs */

pred WellFormedLocationSet[c : set Location] {
  UniquelyNamedLocations[c]
  and 
  UniquelyProvidedRoles[c]
  and
  UniquelyRequiredRoles[c]
}


pred WellFormedLocationGraph[g: LocationGraph] {
   WellFormedLocationSet[g.locations]
}


/** Axiom for  Location Graphs */

fact All_LocationGraph_Are_Well_Formed {
  all g: LocationGraph |  WellFormedLocationGraph[g]
}



/*******************************************************************************
 * Some checks.
 ******************************************************************************/

/** Model means that there exist some well-formed location graphs. */


pred Model {
  some g: LocationGraph | #(g.locations) > 2 and #(g.locations.required) > 2 and #(g.locations.provided) > 3
} 

run Model for 10

/** In a well-formed location set, a role is provided and required by two distinct locations. */
assert RoleIsProvidedAndRequiredByTwoDistinctLocations
{
  all lg : set Location, r : Role, l, h : Location |
    WellFormedLocationSet[lg] implies
    l in lg and h in lg and r in l.provided and r in h.required implies l != h
}

check RoleIsProvidedAndRequiredByTwoDistinctLocations for 40 expect 0


/** In a well-formed location set, a role binds at most two distinct locations. */
assert ARoleBindsAtMostTwoLocations
{
  all lg : set Location, r : Role |
     WellFormedLocationSet[lg] implies
    all ls : set lg | (all h : ls | r in h.required + h.provided) implies #ls < 3
}

check ARoleBindsAtMostTwoLocations for 40 expect 0



######################################################################
#
# Software Name : Cloudnet TOSCA toolbox
# Version: 1.0
# SPDX-FileCopyrightText: Copyright (c) 2020-21 Orange
# SPDX-License-Identifier: Apache-2.0
#
# This software is distributed under the Apache License 2.0
# the text of which is available at http://www.apache.org/licenses/LICENSE-2.0
# or see the "LICENSE-2.0.txt" file for more details.
#
# Author: Yves Berthollet <yves.berthollet@orange.com>
# Software description: TOSCA to Cloudnet Translator
######################################################################

import json
import re

import yaml
from yaml.resolver import BaseResolver

BaseResolver.add_implicit_resolver(
    "tag:yaml.org,2002:bool",
    re.compile(r'''^(?:true|false)$''', re.X),
    list("yYnNtTfFoO"),
)

BaseResolver.add_implicit_resolver(
    "tag:yaml.org,2002:float",
    re.compile(
        r'''^(?:[-+]?(?:[0-9][0-9_]*)\.[0-9_]*(?:[eE][-+][0-9]+)?
                    |\.[0-9_]+(?:[eE][-+][0-9]+)?
                    |[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\.[0-9_]*
                    |[-+]?\.(?:inf|Inf|INF)
                    |\.(?:nan|NaN|NAN))$''',
        re.X,
    ),
    list("-+0123456789.")
)

BaseResolver.add_implicit_resolver(
    "tag:yaml.org,2002:int",
    re.compile(
         r'''^(?:[-+]?0b[0-1_]+
                    |[-+]?0[0-7_]+
                    |[-+]?(?:0|[1-9][0-9_]*)
                    |[-+]?0x[0-9a-fA-F_]+
                    |[-+]?[1-9][0-9_]*(?::[0-5]?[0-9])+)$''',
         re.X,
    ),
    list("-+0123456789"),
)

BaseResolver.add_implicit_resolver(
    "tag:yaml.org,2002:merge", re.compile(r'^(?:<<)$'), ["<"]
)

BaseResolver.add_implicit_resolver(
    "tag:yaml.org,2002:null",
    re.compile(
         r'''^(?: ~
                    |null|Null|NULL
                    | )$''',
         re.X,
    ),
    ["~", "n", "N", ""],
)

BaseResolver.add_implicit_resolver(
    "tag:yaml.org,2002:timestamp",
    re.compile(
        r'''^(?:[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]
                    |[0-9][0-9][0-9][0-9] -[0-9][0-9]? -[0-9][0-9]?
                     (?:[Tt]|[ \t]+)[0-9][0-9]?
                     :[0-9][0-9] :[0-9][0-9] (?:\.[0-9]*)?
                     (?:[ \t]*(?:Z|[-+][0-9][0-9]?(?::[0-9][0-9])?))?)$''',
        re.X,
    ),
    list("0123456789"),
)

BaseResolver.add_implicit_resolver(
    "tag:yaml.org,2002:value", re.compile(r'^(?:=)$'), ["="]
)


def isTrue(b):
    return b == "true"

class Coord():
    pass


class StrCoord(str, Coord):
    def __new__(cls, value, line=0, column=0):
        obj = super().__new__(cls, value)
        obj.line = line
        obj.column = column
        return obj


class IntCoord(int, Coord):
    def __new__(cls, value, line=0, column=0):
        obj = super().__new__(cls, value)
        obj.line = line
        obj.column = column
        return obj


class FloatCoord(int, Coord):
    def __new__(cls, value, line=0, column=0):
        obj = super().__new__(cls, value)
        obj.line = line
        obj.column = column
        return obj


class DictCoord(dict, Coord):
    def __init__(self, value, line=0, column=0):
        dict.__init__(self, value)
        self.line = line
        self.column = column


class ListCoord(list, Coord):
    def __init__(self, value, line=0, column=0):
        list.__init__(self, value)
        self.line = line
        self.column = column


class SafeLineLoader(yaml.BaseLoader):
    def construct_mapping(self, node, deep=False):
        mapping = super(SafeLineLoader, self).construct_mapping(node, deep=deep)
        return DictCoord(
            mapping, line=node.start_mark.line + 1, column=node.start_mark.column + 1
        )

    def construct_document(self, node):
        mapping = super(SafeLineLoader, self).construct_document(node)
        return DictCoord(
            mapping, line=node.start_mark.line + 1, column=node.start_mark.column + 1
        )

    def construct_object(self, node, deep=False):
        mapping = super(SafeLineLoader, self).construct_object(node, deep=deep)
        if node.tag == "tag:yaml.org,2002:bool":
            # can't heritate from bool because. No line can be managed for this type
            return isTrue(mapping)
        if node.tag == "tag:yaml.org,2002:float":
            return FloatCoord(
                float(mapping),
                line=node.start_mark.line + 1,
                column=node.start_mark.column + 1,
            )
        if node.tag == "tag:yaml.org,2002:int":
            return IntCoord(
                int(mapping),
                line=node.start_mark.line + 1,
                column=node.start_mark.column + 1,
            )
        if node.tag == "tag:yaml.org,2002:str":
            return StrCoord(
                mapping,
                line=node.start_mark.line + 1,
                column=node.start_mark.column + 1,
            )
        if node.tag == "tag:yaml.org,2002:seq" or isinstance(mapping, list):
            return ListCoord(
                mapping,
                line=node.start_mark.line + 1,
                column=node.start_mark.column + 1,
            )
        if node.tag == "tag:yaml.org,2002:map" or isinstance(mapping, dict):
            return DictCoord(
                mapping,
                line=node.start_mark.line + 1,
                column=node.start_mark.column + 1,
            )
        # default is mapped to str
        return StrCoord(
            mapping, line=node.start_mark.line + 1, column=node.start_mark.column + 1
        )

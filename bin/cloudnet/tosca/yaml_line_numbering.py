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

import datetime
import re
import yaml

class Coord():
    def init(self, line=0, column=0):
        self.line = line
        self.column = column

class StrCoord(str, Coord):
    def __new__(cls, value, line=0, column=0):
        obj = super().__new__(cls, value)
        Coord.init(obj, line, column)
        return obj

class IntCoord(int, Coord):
    def __new__(cls, value, line=0, column=0):
        obj = super().__new__(cls, value)
        Coord.init(obj, line, column)
        return obj

class FloatCoord(float, Coord):
    def __new__(cls, value, line=0, column=0):
        obj = super().__new__(cls, value)
        Coord.init(obj, line, column)
        return obj

class DictCoord(dict, Coord):
    def __init__(self, line=0, column=0):
        dict.__init__(self)
        Coord.init(self, line, column)

class ListCoord(list, Coord):
    def __init__(self, line=0, column=0):
        list.__init__(self)
        Coord.init(self, line, column)

class DatetimeCoord(datetime.datetime, Coord):
    pass

class SafeLineLoader(yaml.SafeLoader):

    def construct_yaml_int(self, node):
        result = super().construct_yaml_int(node)
        return IntCoord(
                    result,
                    line=node.start_mark.line + 1,
                    column=node.start_mark.column + 1,
                )

    def construct_yaml_float(self, node):
        result = super().construct_yaml_float(node)
        return FloatCoord(
                    result,
                    line=node.start_mark.line + 1,
                    column=node.start_mark.column + 1,
                )

    def construct_yaml_timestamp(self, node):
        dt = super().construct_yaml_timestamp(node)
        result = DatetimeCoord(
                      dt.year,
                      dt.month,
                      dt.day,
                      dt.hour,
                      dt.minute,
                      dt.second,
                      dt.microsecond,
                      dt.tzinfo,
                      fold=dt.fold)
        Coord.init(result,
                    line=node.start_mark.line + 1,
                    column=node.start_mark.column + 1
                )
        return result

    def construct_yaml_str(self, node):
        result = super().construct_yaml_str(node)
        return StrCoord(
                    result,
                    line=node.start_mark.line + 1,
                    column=node.start_mark.column + 1,
                )

    def construct_yaml_seq(self, node):
# PM: don't understand how to use the result of super().construct_yaml_seq()
#        result = super().construct_yaml_seq(node)
# PM: so I duplicate the code
        result = ListCoord(
                   line=node.start_mark.line + 1,
                   column=node.start_mark.column + 1,
                )
        result.extend(self.construct_sequence(node))
        return result

    def construct_yaml_map(self, node):
# PM: don't understand how to use the result of super().construct_yaml_map()
#        result = super().construct_yaml_map(node)
# PM: so I duplicate the code
        result = DictCoord(
                        line=node.start_mark.line + 1,
                        column=node.start_mark.column + 1,
                    )
        result.update(self.construct_mapping(node))
        return result

SafeLineLoader.add_constructor(
        'tag:yaml.org,2002:int',
        SafeLineLoader.construct_yaml_int)

SafeLineLoader.add_constructor(
        'tag:yaml.org,2002:float',
        SafeLineLoader.construct_yaml_float)

SafeLineLoader.add_constructor(
        'tag:yaml.org,2002:timestamp',
        SafeLineLoader.construct_yaml_timestamp)

SafeLineLoader.add_constructor(
        'tag:yaml.org,2002:str',
        SafeLineLoader.construct_yaml_str)

SafeLineLoader.add_constructor(
        'tag:yaml.org,2002:seq',
        SafeLineLoader.construct_yaml_seq)

SafeLineLoader.add_constructor(
        'tag:yaml.org,2002:map',
        SafeLineLoader.construct_yaml_map)

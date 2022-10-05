######################################################################
#
# Software Name : Cloudnet TOSCA toolbox
# Version: 1.0
# SPDX-FileCopyrightText: Copyright (c) 2020-22 Orange
# SPDX-License-Identifier: Apache-2.0
#
# This software is distributed under the Apache License 2.0
# the text of which is available at http://www.apache.org/licenses/LICENSE-2.0
# or see the "LICENSE-2.0.txt" file for more details.
#
# Author: Yves Berthollet <yves.berthollet@orange.com>
# Software description: TOSCA to Cloudnet Translator
######################################################################

import collections.abc
import datetime
import re
import yaml
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode


class Coord:
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
            fold=dt.fold,
        )
        Coord.init(
            result, line=node.start_mark.line + 1, column=node.start_mark.column + 1
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
        data = DictCoord(
            line=node.start_mark.line + 1,
            column=node.start_mark.column + 1,
        )
        # PM: Following is copied from PyYAML code base
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        # PM: Following is copied from PyYAML code base
        if not isinstance(node, MappingNode):
            raise ConstructorError(None, None,
                    "expected a mapping node, but found %s" % node.id,
                    node.start_mark)
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, collections.abc.Hashable):
                raise ConstructorError("while constructing a mapping", node.start_mark,
                        "found unhashable key", key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            # PM: Following check was added to detect duplicate keys
            if key in mapping:
                raise ConstructorError("while constructing a mapping", node.start_mark,
                        "%s - duplicate map key" % key, key_node.start_mark)
            mapping[key] = value
        return mapping

SafeLineLoader.add_constructor(
    "tag:yaml.org,2002:int", SafeLineLoader.construct_yaml_int
)

SafeLineLoader.add_constructor(
    "tag:yaml.org,2002:float", SafeLineLoader.construct_yaml_float
)

SafeLineLoader.add_constructor(
    "tag:yaml.org,2002:timestamp", SafeLineLoader.construct_yaml_timestamp
)

SafeLineLoader.add_constructor(
    "tag:yaml.org,2002:str", SafeLineLoader.construct_yaml_str
)

SafeLineLoader.add_constructor(
    "tag:yaml.org,2002:seq", SafeLineLoader.construct_yaml_seq
)

SafeLineLoader.add_constructor(
    "tag:yaml.org,2002:map", SafeLineLoader.construct_yaml_map
)

yaml.SafeDumper.add_representer(
    StrCoord, yaml.SafeDumper.represent_str
)

yaml.SafeDumper.add_representer(
    IntCoord, yaml.SafeDumper.represent_int
)

yaml.SafeDumper.add_representer(
    FloatCoord, yaml.SafeDumper.represent_float
)

yaml.SafeDumper.add_representer(
    ListCoord, yaml.SafeDumper.represent_list
)

yaml.SafeDumper.add_representer(
    DictCoord, yaml.SafeDumper.represent_dict
)

yaml.SafeDumper.add_representer(
    DatetimeCoord, yaml.SafeDumper.represent_datetime
)

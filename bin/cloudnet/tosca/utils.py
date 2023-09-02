######################################################################
#
# Software Name : Cloudnet TOSCA toolbox
# Version: 1.0
# SPDX-FileCopyrightText: Copyright (c) 2020 Orange
# SPDX-License-Identifier: Apache-2.0
#
# This software is distributed under the Apache License 2.0
# the text of which is available at http://www.apache.org/licenses/LICENSE-2.0
# or see the "LICENSE-2.0.txt" file for more details.
#
# Author: Philippe Merle <philippe.merle@inria.fr>
# Software description: TOSCA to Cloudnet Translator
######################################################################

import re

SCALAR_UNIT_RE = re.compile("^([0-9]+(\.[0-9]+)?)( )*([A-Za-z]+)$")


def split_scalar_unit(scalar):
    match = SCALAR_UNIT_RE.fullmatch(scalar)
    if match == None:
        raise ValueError("<scalar> <unit> expected instead of %s" % scalar)
    return int(match.group(1)), match.group(4)


"""
    Compute a short type name, i.e., remove the dotted prefix.
"""


def short_type_name(type_name):
    idx = type_name.rfind(".")
    if type_name[idx + 1].isdigit():
        return short_type_name(type_name[:idx]) + type_name[idx:]
    return type_name[idx + 1 :]


"""
    Normalize a name, i.e.
      - '.', '-', ' ' and ':' characters are replaced by '_'
      - If first character is a digit then prefix '_' is added
"""


def normalize_name(label):
    for character in [".", "-", " ", ":", "[", "]"]:
        label = label.replace(character, "_")
    if label[0].isdigit():
        label = "_" + label
    return label


"""
    Merge two dictionaries.
"""


def merge_dict(d, u):
    from copy import deepcopy

    d = deepcopy(d)
    for k, v in u.items():
        if isinstance(v, dict):
            dv = d.get(k)
            if dv is None:
                dv = {}
            if not isinstance(dv, dict):
                dv = {"_old_value_": dv}
            d[k] = merge_dict(dv, v)
        else:
            if v is not None:
                old_v = d.get(k)
                if old_v is not None and isinstance(old_v, dict):
                    # Avoid to lose the previous dictionary.
                    old_v[
                        "value"
                    ] = v  # Keep 'value' as key because this has a wanted side effect, find a better way to do that.
                else:
                    d[k] = v

            else:
                d[k] = None

    return d


def normalize_dict(data):
    if isinstance(data, dict):
        return data
    elif isinstance(data, list):
        result = dict()
        for item in data:
            if not isinstance(item, dict):
                continue
            for (key, value) in item.items():
                result[key] = value
        return result
    else:
        raise ValueError("not a dict or list")


def get_path(a_dict, *path, default=None):
    result = a_dict
    for p in path:
        if isinstance(result, dict):
            result = result.get(p)
        else:
            return default
        if result is None:
            return default
    return result

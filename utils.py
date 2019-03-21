# MB-Lab

# MB-Lab fork website : https://github.com/animate1978/MB-Lab

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import logging
from functools import wraps
import time
import bpy
import json

logger = logging.getLogger(__name__)


def get_object_parent(obj):
    if not obj:
        return None
    return getattr(obj, "parent", None)


def get_deforming_armature(obj):
    if obj.type == 'MESH':
        for modf in obj.modifiers:
            if modf.type == 'ARMATURE':
                return modf.object
    return None


def get_active_armature():
    active_obj = bpy.context.view_layer.objects.active
    parent_object = get_object_parent(active_obj)
    if active_obj:
        if active_obj.type == 'ARMATURE':
            return active_obj
        if active_obj.type == 'MESH':
            if parent_object:
                if parent_object.type == 'ARMATURE':
                    return parent_object
            else:
                deforming_armature = get_deforming_armature(active_obj)
                if deforming_armature:
                    return deforming_armature
    return None


def is_ik_armature(armature=None):
    if not armature:
        armature = get_active_armature()
        if armature and armature.type == 'ARMATURE':
            for b in armature.data.bones:
                if 'IK' in b.name:
                    return True
        elif armature and armature.type != 'ARMATURE':
            logger.warning("Cannot get the bones because the obj is not an armature")
            return False
    return False


def mergedict(dict1, dict2, path=[]):
    for key in dict2:
        if key in dict1:
            if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                mergedict(dict1[key], dict2[key], path + [str(key)])
            elif dict1[key] == dict2[key]:
                pass
            elif isinstance(dict1[key], list) and isinstance(dict2[key], list):
                dict1[key] = mergelist(dict1[key], dict2[key])
            else:
                raise Exception('Conflict')
        else:
            dict1[key] = dict2[key]
    return dict1


def mergelist(list1, list2):
    for i in range(len(list2)):
        list1.append(list2[i])
    logger.debug(list1)
    return list1


def methodtimer(f):
    """
    A wrapper that logs the execution time of function f
    Usage:
    @methodtimer
    def function_name(args)
    """

    @wraps(f)
    def wrap(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        logger.info("{0} took {1}s to run".format(f.__name__, te - ts))
        return result

    # if f:
    #     return _timing(f)
    return wrap


def logjson(f):
    """
    A wrapper that logs what a function returns for debugging purposes
    Usage:
    @logjson
    def function_name(args)
    """

    @wraps(f)
    def wrap(*args, **kwargs):
        result = f(*args, **kwargs)
        logger.debug("{0} returned JSON:\n{1}".format(
            f.__name__,
            json.dumps(result, sort_keys=True, indent=4, separators=(',', ': '))
        ))
        return result

    return wrap


def logreturn(f):
    """
    A wrapper that logs what a function returns
    Usage:
    @logreturn
    def function_name(args)
    """

    @wraps(f)
    def wrap(*args, **kwargs):
        result = f(*args, **kwargs)
        logger.debug("{0} returned {1} of type {2}".format(
            f.__name__,
            str(result),
            type(result)
        ))
        return result

    return wrap


def logreturnlistindic(f):
    """
    A wrapper that logs items in a list that the function returned
        Usage:
    @logreturnlistindic
    def function_name(args)
    """

    @wraps(f)
    def wrap(*args, **kwargs):
        result = f(*args, **kwargs)
        logger.debug("== logreturnlistindic of {0} ==:".format(f.__name__))
        if result is not None:
            for x in result:
                logger.debug("{0}".format(x))
                for y in result[x]:
                    logger.debug("    {0}".format(y))
        else:
            logger.error("RESULT FOR {0} IS NONE".format(f.__name__))
        logger.debug("++ logreturnlistindic of {0} END ++\n:".format(f.__name__))
        return result

    return wrap

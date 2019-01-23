import bpy
import os
from . import algorithms as a
from . import settings as s
from pathlib import Path, PurePath

dr = s.data_path


def namesofallconfig(configtype, inproject = "", seconddir = ""): # lists all json files in a specified project
    return namesofallfile("json", PurePath(inproject, configtype, seconddir))


def namesofallfile(thefiletype, thepath="", filename="*"):
    thepath = dr.glob('**/' + str(thepath) + '/' + filename + '.' + thefiletype)
    return thepath


# TODO create projmodule config file reading?
'''
Would primarily be used to check that prerequisite projmods are installed stuff to allow for legacy versions to work
'''
# TODO projmod cache?
'''
Creates a JSON file that contains already indexed info. May allow for faster loading w/ big libraries.
Projmod config should be able to override this for testing purposes

Is not a priority
'''
import bpy
import os
from . import algorithms as a
from . import settings as s
from . import utils as ut
import logging
from pathlib import Path, PurePath
import json

dr = s.data_path

logger = logging.getLogger(__name__)


class projectlisting:
    def __init__(self, name):
        self.name = name
        self.configs = []


def getallofconfig(configname):
    return list(s.data_path.glob('**/{0}'.format(str(configname))))


def legacylike(old_path):
    if type(old_path) is str:
        old_path = Path(old_path)
    try:
        searchpath = old_path.relative_to(s.data_path)
    except ValueError:
        searchpath = old_path.relative_to(s.data_path_legacy)
    finally:
        return getallofconfig(searchpath)


def projmodmerge(projlist):
    logger.debug(projlist)
    merged = {}
    for i in range(0, len(projlist)):
        temp = a.load_json_data(str(projlist[i]), "Characters definition")
        merged = ut.mergedict(merged, temp)
    return merged


def loadprojectnames():
    if s.project_folders is None:
        for file in s.data_path.iterdir():
            if file.is_dir():
                s.project_folders.append(file.name)
        logger.info("s.project_folders has been populated   : {0}".format(s.project_folders))
    else:
        logger.info("s.project_folders was already populated: {0}".format(s.project_folders))


def namesofallconfig(configtype, inproject="", seconddir=""): # lists all json files in a specified project
    return namesofallfile("json", PurePath(inproject, configtype, seconddir))


def namesofallfile(thefiletype, thepath=s.data_path, filename="*"):
    thepath = dr.glob(str(thepath) + '/' + filename + '.' + thefiletype)
    return thepath


def filetypeexistin(configtype,thepath=s.data_path,filename="*.json"):
    return


# @ut.logjson
def check_configuration():
    """
    Effectively merges all the json configurations
    """
    logger.info("Getting Configurations via loading.py")
    if s.characters_config is None:
        s.characters_config = projmodmerge(getallofconfig("characters_config.json"))
    else:
        logger.warning("You can just use settings.characters_config (usually s.characters_config).")
    return s.characters_config



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
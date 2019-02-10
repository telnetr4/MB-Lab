# import bpy
# from bpy_extras.io_utils import ExportHelper, ImportHelper
# from bpy.app.handlers import persistent
from pathlib import Path
import logging
# from . import humanoid, animationengine, proxyengine
# from . import bl_info

# mblab_humanoid = 0
# mblab_retarget = animationengine.RetargetEngine()
# mblab_shapekeys = animationengine.ExpressionEngineShapeK()
# mblab_proxy = proxyengine.ProxyEngine()

logger = logging.getLogger(__name__)

settings_path = Path(__file__)

data_path_legacy = settings_path.parents[0] / "data_legacy"

data_path = settings_path.parents[0] / "data"

project_folders = []

characters_config = None


def init(context):
    from . import humanoid, animationengine, proxyengine
    from . import loading as ml
    from . import algorithms as a

    # global mblab_humanoid
    # global mblab_retarget
    # global mblab_shapekeys
    # global mblab_proxy
    #
    # mblab_humanoid = humanoid.Humanoid(context["version"])
    # mblab_retarget = animationengine.RetargetEngine()
    # mblab_shapekeys = animationengine.ExpressionEngineShapeK()
    # mblab_proxy = proxyengine.ProxyEngine()

    global loadedlib
    loadedlib = ml.PathDirectory()
    morphlist = ml.namesofallconfig("morphs")
    logger.info(morphlist)
    logger.info(ml.namesofallconfig("morphs", "Core"))
    logger.info(ml.namesofallconfig("morphs", "Anime"))
    logger.info(ml.namesofallconfig("anthropometry"))
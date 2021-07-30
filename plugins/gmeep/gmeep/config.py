"""Package configuration.
"""

__all__ = ["PATH"]
import os
import pathlib
import sys
from loguru import logger
import meep as mp
import pp

__version__ = "0.0.2"
home = pathlib.Path.home()
cwd = pathlib.Path.cwd()
cwd_config = cwd / "config.yml"
module_path = pathlib.Path(__file__).parent.absolute()
repo_path = module_path.parent
sparameters = repo_path / "sparameters"
sparameters.mkdir(exist_ok=True, parents=True)

gmeep_home = home / ".gmeep"
gmeep_home.mkdir(exist_ok=True)

logpath = cwd / "gmeep.log"

logger.info(f"gdsfactory {pp.__version__}")
logger.info(f"gmeep {__version__}")
logger.info(f"meep {mp.__version__}")
logger.add(sink=logpath)


class Path:
    module = module_path
    repo = repo_path
    sparameters = gmeep_home / "sparameters"
    modes = gmeep_home / "modes"


PATH = Path()

PATH.sparameters.mkdir(exist_ok=True)
PATH.modes.mkdir(exist_ok=True)


def disable_print():
    sys.stdout = open(os.devnull, "w")


def enable_print():
    sys.stdout = sys.__stdout__


if __name__ == "__main__":
    print(PATH.repo)

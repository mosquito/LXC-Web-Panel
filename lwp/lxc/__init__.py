import logging
import os

log = logging.getLogger("lxc")

if os.geteuid():
    BASE_PATH = os.path.expanduser("~/.local/share/lxc/")
else:
    BASE_PATH = '/var/lib/lxc'

from lwp.lxc.container import exists, info
from lwp.lxc.exceptions import (
    ContainerAlreadyExists,
    ContainerDoesntExists,
    ContainerAlreadyRunning,
    ContainerNotRunning
)
from lwp.lxc.run import run

"""Mock of pineapple.helpers.opkg_helpers — OpkgJob + check_if_installed."""
from typing import List, Union

from pineapple.jobs import Job

# Toggleable by tests to simulate an installed/absent package.
INSTALLED = False


def check_if_installed(package: str, logger=None) -> bool:
    return INSTALLED


class OpkgJob(Job):
    def __init__(self, package: Union[str, List[str]], install: bool):
        super().__init__()
        self.package = package
        self.install = install

    def do_work(self, logger):
        return True

    def stop(self):
        pass

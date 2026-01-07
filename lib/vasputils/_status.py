from enum import Enum


class Status(Enum):
    NOT_FOUND = "Not found"
    IS_DIRECTORY = "This is directory"
    LOAD_FAILED = "Failed to load vasprun.xml"
    ELECTRONIC_NOT_CONVERGED = "Electronic loop is not converged"
    IONIC_NOT_CONVERGED = "Ionic loop is not converged"
    CONVERGED = "Converged"

    def __str__(self):
        return self.value

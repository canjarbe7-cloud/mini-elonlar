#!/usr/bin/env python3
"""Django boshqaruv skripti."""
import os
import sys
from pathlib import Path


if __name__ == "__main__":
    # This repository is the ``elonlar`` app itself, so expose its parent as
    # the import root when commands are run from this directory.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elonlar.project_settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

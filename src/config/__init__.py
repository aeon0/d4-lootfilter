import sys
from pathlib import Path


def get_base_dir(bundled: bool = False) -> Path:
    if getattr(sys, "frozen", False) and not bundled:
        return Path(sys.executable).parent
    return Path(__file__).parent.parent.parent


BASE_DIR = get_base_dir(False)

import os
import traceback

import keyboard
from beautifultable import BeautifulTable
from cam import Cam
from item.filter import Filter
from logger import Logger
from overlay import Overlay
from PIL import Image  # noqa #  Note: Somehow needed, otherwise the binary has an issue with tesserocr
from utils.importer.maxroll import import_build
from utils.misc import wait
from utils.ocr.read import load_api
from utils.process_handler import safe_exit
from utils.window import WindowSpec, start_detecting_window
from version import __version__

from config.loader import IniConfigLoader


def main():
    Logger.init(IniConfigLoader().advanced_options.log_lvl)
    # Create folders for logging stuff
    config_dir = IniConfigLoader().user_dir
    for dir_name in ["log/screenshots", config_dir, config_dir / "profiles"]:
        os.makedirs(dir_name, exist_ok=True)

    Logger.init("info")

    print(f"============ D4 Loot Filter {__version__} ============")
    table = BeautifulTable()
    table.set_style(BeautifulTable.STYLE_BOX_ROUNDED)
    table.rows.append([IniConfigLoader().advanced_options.import_build, "Import Build"])
    table.rows.append([IniConfigLoader().advanced_options.run_scripts, "Run/Stop Vision Filter"])
    table.rows.append([IniConfigLoader().advanced_options.run_filter, "Run/Stop Auto Filter"])
    table.rows.append([IniConfigLoader().advanced_options.exit_key, "Exit"])
    table.columns.header = ["hotkey", "action"]
    print(table)
    print("\n")

    keyboard.add_hotkey(IniConfigLoader().advanced_options.import_build, lambda: import_build())

    win_spec = WindowSpec(IniConfigLoader().advanced_options.process_name)
    start_detecting_window(win_spec)
    while not Cam().is_offset_set():
        wait(0.2)

    load_api()

    Logger.info(f"Adapt your custom configs in: {config_dir}")

    Filter().load_files()
    overlay = None

    keyboard.add_hotkey(IniConfigLoader().advanced_options.run_scripts, lambda: overlay.run_scripts() if overlay is not None else None)
    keyboard.add_hotkey(IniConfigLoader().advanced_options.run_filter, lambda: overlay.filter_items() if overlay is not None else None)
    keyboard.add_hotkey(IniConfigLoader().advanced_options.exit_key, lambda: safe_exit())

    overlay = Overlay()
    overlay.run()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        print("Press Enter to exit ...")
        input()

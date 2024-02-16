from typing import Optional
import numpy as np
import cv2
from dataclasses import dataclass
from cam import Cam
from config import Config
from ui.menu import Menu
from utils.image_operations import crop, threshold
from utils.roi_operations import get_center, to_grid
from utils.custom_mouse import mouse
from utils.misc import wait
from template_finder import search


@dataclass
class ItemSlot:
    bounding_box: list[int] = None
    center: list[int] = None
    is_fav: bool = False
    is_junk: bool = False


class InventoryBase(Menu):
    """
    Base class for all menus with a grid inventory
    Provides methods for identifying occupied and empty slots, item operations, etc.
    """

    def __init__(self, rows: int = 3, columns: int = 11, is_stash: bool = False):
        super().__init__()
        self.rows = rows
        self.columns = columns
        self.slots_roi = Config().ui_roi[f"slots_{self.rows}x{self.columns}"]
        if is_stash:
            self.junk_template = "junk_stash"
        else:
            self.junk_template = "junk_inv"

    def get_item_slots(self, img: Optional[np.ndarray] = None) -> tuple[list[ItemSlot], list[ItemSlot], list[ItemSlot], list[ItemSlot]]:
        """
        Identifies occupied and empty slots in a grid of slots within a given rectangle of interest (ROI).
        :param roi: The rectangle to consider, represented as (x_min, y_min, width, height).
        :param rows: The number of rows in the grid.
        :param columns: The number of columns in the grid.
        :param img: An optional image (as a numpy array) to use for identifying empty slots.
        :return: Four sets of coordinates.
            - Centers of the occupied slots
            - Centers of the empty slots
        """
        if img is None:
            img = Cam().grab()
        grid = to_grid(self.slots_roi, self.rows, self.columns)
        occupied_slots = []
        empty_slots = []

        for _, slot_roi in enumerate(grid):
            item_slot = ItemSlot(bounding_box=slot_roi, center=get_center(slot_roi))
            slot_img = crop(img, slot_roi)

            hsv_img = cv2.cvtColor(slot_img, cv2.COLOR_BGR2HSV)
            mean_value_overall = np.mean(hsv_img[:, :, 2])
            fav_flag_crop = crop(hsv_img, Config().ui_roi["rel_fav_flag"])
            mean_value_fav = cv2.mean(fav_flag_crop)[2]

            res_junk = search(self.junk_template, slot_img, threshold=0.7)

            if mean_value_fav > 205:
                item_slot.is_fav = True
                occupied_slots.append(item_slot)
            elif res_junk.success:
                item_slot.is_junk = True
                occupied_slots.append(item_slot)
            elif mean_value_overall > 37:
                occupied_slots.append(item_slot)
            else:
                empty_slots.append(item_slot)

        return occupied_slots, empty_slots

    def hover_item(self, item: ItemSlot):
        mouse.move(*Cam().window_to_monitor(item.center), randomize=15, delay_factor=(1.1, 1.3))

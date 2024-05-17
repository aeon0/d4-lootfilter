import numpy as np

from config.data import COLORS
from dataloader import Dataloader
from item.models import Item, ItemRarity, ItemType
from template_finder import TemplateMatch
from utils.image_operations import crop, color_filter
from utils.ocr.read import image_to_text


def read_item_type(
    item: Item,
    img_item_descr: np.ndarray,
    sep_short_match: TemplateMatch,
    do_pre_proc: bool = True,
) -> tuple[Item | None, str]:
    # Item Type and Item Power
    # =====================================
    # start_power = time.time()
    rarity = item.rarity
    _, img_width, _ = img_item_descr.shape
    roi_top = [0, 0, int(img_width * 0.74), sep_short_match.center[1]]
    crop_top = crop(img_item_descr, roi_top)
    concatenated_str = image_to_text(crop_top, do_pre_proc=do_pre_proc).text.lower().replace("\n", " ")
    for error, correction in Dataloader().error_map.items():
        concatenated_str = concatenated_str.replace(error, correction)

    # TODO: Language specific
    if "sigil" in concatenated_str and Dataloader().tooltips["ItemTier"] in concatenated_str:
        # process sigil
        item.item_type = ItemType.Sigil
    elif rarity in [ItemRarity.Common, ItemRarity.Legendary]:
        # We check if it is a material
        mask, _ = color_filter(crop_top, COLORS.material_color, False)
        mean_val = np.mean(mask)
        if mean_val > 2.0:
            item.item_type = ItemType.Material
            return item, concatenated_str
        elif rarity == ItemRarity.Common:
            return item, concatenated_str

    if item.item_type == ItemType.Sigil:
        item.power = _find_sigil_tier(concatenated_str)
    else:
        item = _find_item_power_and_type(item, concatenated_str)
        if item.item_type is None:
            masked_red, _ = color_filter(crop_top, COLORS.unusable_red, False)
            crop_top[masked_red == 255] = [235, 235, 235]
            concatenated_str = image_to_text(crop_top).text.lower().replace("\n", " ")
            item = _find_item_power_and_type(item, concatenated_str)

    non_magic_or_sigil = item.rarity != ItemRarity.Magic or item.item_type == ItemType.Sigil
    power_or_type_bad = (item.power is None and item.item_type not in [ItemType.Elixir, ItemType.TemperManual]) or item.item_type is None
    if non_magic_or_sigil and power_or_type_bad:
        return None, concatenated_str

    return item, concatenated_str
    # print("Runtime (start_power): ", time.time() - start_power)


def _find_item_power_and_type(item: Item, concatenated_str: str) -> Item:
    idx = None
    if Dataloader().tooltips["ItemPower"] in concatenated_str:
        idx = concatenated_str.index(Dataloader().tooltips["ItemPower"])
    if idx is not None:
        preceding_word = concatenated_str[:idx].split()[-1]
        if preceding_word.isdigit():
            item.power = int(preceding_word)
        elif "+" in preceding_word:
            item_power_numbers = preceding_word.split("+")
            if item_power_numbers[0].isdigit() and item_power_numbers[1].isdigit():
                item.power = int(item_power_numbers[0]) + int(item_power_numbers[1])

    max_length = 0
    last_char_idx = 0
    for item_type in ItemType:
        if (found_idx := concatenated_str.rfind(item_type.value)) != -1:
            tmp_idx = found_idx + len(item_type.value)
            if tmp_idx >= last_char_idx and ("two-handed" not in item_type.value or len(item_type.value) > max_length):
                item.item_type = item_type
                last_char_idx = tmp_idx
                max_length = len(item_type.value)
    # common mistake is that "Armor" is on a seperate line and can not be detected properly
    # TODO: Language specific
    if item.item_type is None:
        if "chest" in concatenated_str or "armor" in concatenated_str:
            item.item_type = ItemType.ChestArmor
    if "two-handed" in concatenated_str or "two- handed" in concatenated_str:
        if item.item_type == ItemType.Sword:
            item.item_type = ItemType.Sword2H
        elif item.item_type == ItemType.Mace:
            item.item_type = ItemType.Mace2H
        elif item.item_type == ItemType.Scythe:
            item.item_type = ItemType.Scythe2H
        elif item.item_type == ItemType.Axe:
            item.item_type = ItemType.Axe2H
    return item


def _find_sigil_tier(concatenated_str: str) -> int:
    for error, correction in Dataloader().error_map.items():
        concatenated_str = concatenated_str.replace(error, correction)
    if Dataloader().tooltips["ItemTier"] in concatenated_str:
        idx = concatenated_str.index(Dataloader().tooltips["ItemTier"])
        split_words = concatenated_str[idx:].split()
        if len(split_words) == 2:
            following_word = split_words[1]
            if following_word.isdigit():
                return int(following_word)
    return None

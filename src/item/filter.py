import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from config.loader import IniConfigLoader
from dataloader import Dataloader
from item.data.affix import Affix
from item.data.aspect import Aspect
from item.data.item_type import ItemType
from item.data.rarity import ItemRarity
from item.models import Item
from logger import Logger


@dataclass
class MatchedFilter:
    profile: str
    matched_affixes: list[str] = field(default_factory=list)
    did_match_aspect: bool = False


@dataclass
class FilterResult:
    keep: bool
    matched: list[MatchedFilter]


class Filter:
    affix_filters = dict()
    aspect_filters = dict()
    unique_filters = dict()
    sigil_filters = dict()

    files_loaded = False
    all_file_pathes = []
    last_loaded = None

    _initialized: bool = False
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Filter, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def _check_item_types(filters):
        for filter_dict in filters:
            for filter_name, filter_data in filter_dict.items():
                user_item_types = [filter_data["itemType"]] if isinstance(filter_data["itemType"], str) else filter_data["itemType"]
                if user_item_types is None:
                    Logger.warning(f"Warning: Missing itemtype in {filter_name}")
                    continue
                invalid_types = []
                for val in user_item_types:
                    try:
                        ItemType(val)
                    except ValueError:
                        invalid_types.append(val)
                if invalid_types:
                    Logger.warning(f"Warning: Invalid ItemTypes in filter {filter_name}: {', '.join(invalid_types)}")

    @staticmethod
    def _check_affix_pool(affix_pool, affix_dict, filter_name):
        user_affix_pool = affix_pool
        invalid_affixes = []
        if user_affix_pool is None:
            return
        for affix in user_affix_pool:
            if isinstance(affix, dict) and "any_of" in affix:
                affix_list = affix["any_of"] if affix["any_of"] is not None else []
            else:
                affix_list = [affix]
            for a in affix_list:
                affix_name = a if isinstance(a, str) else a[0]
                if affix_name not in affix_dict:
                    invalid_affixes.append(affix_name)
        if invalid_affixes:
            Logger.warning(f"Warning: Invalid Affixes in filter {filter_name}: {', '.join(invalid_affixes)}")

    def load_files(self):
        self.files_loaded = True
        self.affix_filters = dict()
        self.aspect_filters = dict()
        self.unique_filters = dict()
        profiles: list[str] = IniConfigLoader().general.profiles

        user_dir = os.path.expanduser("~")
        custom_profile_path = Path(f"{user_dir}/.d4lf/profiles")
        params_profile_path = Path(f"config/profiles")
        self.all_file_pathes = []

        for profile_str in profiles:
            custom_file_path = custom_profile_path / f"{profile_str}.yaml"
            params_file_path = params_profile_path / f"{profile_str}.yaml"
            if custom_file_path.is_file():
                profile_path = custom_file_path
            elif params_file_path.is_file():
                profile_path = params_file_path
            else:
                Logger.error(f"Could not load profile {profile_str}. Checked: {custom_file_path}, {params_file_path}")
                continue

            self.all_file_pathes.append(profile_path)
            with open(profile_path, encoding="utf-8") as f:
                try:
                    config = yaml.safe_load(f)
                except yaml.YAMLError as e:
                    if hasattr(e, "problem_mark"):
                        mark = e.problem_mark
                        Logger.error(f"Error in the YAML file {profile_path} at position: (line {mark.line + 1}, column {mark.column + 1})")
                    else:
                        Logger.error(f"Error in the YAML file {profile_path}: {e}")
                    continue
                except Exception as e:
                    Logger.error(f"An unexpected error occurred loading YAML file {profile_path}: {e}")
                    continue

                info_str = f"Loading profile {profile_str}: "

                if config is not None and "Affixes" in config:
                    info_str += "Affixes "
                    if config["Affixes"] is None:
                        Logger.error(f"Empty Affixes section in {profile_str}. Remove it")
                        return
                    self.affix_filters[profile_str] = config["Affixes"]
                    # Sanity check on the item types
                    self._check_item_types(self.affix_filters[profile_str])
                    # Sanity check on the affixes
                    for filter_dict in self.affix_filters[profile_str]:
                        for filter_name, filter_data in filter_dict.items():
                            if "affixPool" in filter_data:
                                self._check_affix_pool(filter_data["affixPool"], Dataloader().affix_dict, filter_name)
                            else:
                                filter_data["affixPool"] = []
                            if "inherentPool" in filter_data:
                                self._check_affix_pool(filter_data["inherentPool"], Dataloader().affix_dict, filter_name)

                if config is not None and "Sigils" in config:
                    info_str += "Sigils "
                    if config["Sigils"] is None:
                        Logger.error(f"Empty Sigils section in {profile_str}. Remove it")
                        return
                    self.sigil_filters[profile_str] = config["Sigils"]
                    # Sanity check on the sigil affixes
                    if "blacklist" not in self.sigil_filters[profile_str]:
                        self.sigil_filters[profile_str]["blacklist"] = []
                    if "whitelist" not in self.sigil_filters[profile_str]:
                        self.sigil_filters[profile_str]["whitelist"] = []
                    self._check_affix_pool(
                        self.sigil_filters[profile_str]["blacklist"], Dataloader().affix_sigil_dict, f"{profile_str}.Sigils"
                    )
                    self._check_affix_pool(
                        self.sigil_filters[profile_str]["whitelist"], Dataloader().affix_sigil_dict, f"{profile_str}.Sigils"
                    )
                    if items_in_both := set(self.sigil_filters[profile_str]["blacklist"]).intersection(
                        set(self.sigil_filters[profile_str]["whitelist"])
                    ):
                        Logger.error(f"Sigil blacklist and whitelist have overlapping items: {items_in_both}")
                        return

                if config is not None and "Aspects" in config:
                    info_str += "Aspects "
                    if config["Aspects"] is None:
                        Logger.error(f"Empty Aspects section in {profile_str}. Remove it")
                        return
                    self.aspect_filters[profile_str] = config["Aspects"]
                    invalid_aspects = []
                    for aspect in self.aspect_filters[profile_str]:
                        aspect_name = aspect if isinstance(aspect, str) else aspect[0]
                        if aspect_name not in Dataloader().aspect_dict:
                            invalid_aspects.append(aspect_name)
                    if invalid_aspects:
                        Logger.warning(f"Warning: Invalid Aspect: {', '.join(invalid_aspects)}")

                if config is not None and "Uniques" in config:
                    info_str += "Uniques"
                    if config["Uniques"] is None:
                        Logger.error(f"Empty Uniques section in {profile_str}. Remove it")
                        return
                    self.unique_filters[profile_str] = config["Uniques"]
                    # Sanity check for unique aspects
                    invalid_uniques = []
                    for unique in self.unique_filters[profile_str]:
                        if "aspect" not in unique:
                            Logger.warning(f"Warning: Unique missing mandatory 'aspect' field in {profile_str} profile")
                            continue
                        unique_name = unique["aspect"] if isinstance(unique["aspect"], str) else unique["aspect"][0]
                        if unique_name not in Dataloader().aspect_unique_dict:
                            invalid_uniques.append(unique_name)
                        elif "affixPool" in unique:
                            self._check_affix_pool(unique["affixPool"], Dataloader().affix_dict, unique_name)
                    if invalid_uniques:
                        Logger.warning(f"Warning: Invalid Unique: {', '.join(invalid_uniques)}")

                Logger.info(info_str)

        self.last_loaded = time.time()

    def _did_files_change(self) -> bool:
        if self.last_loaded is None:
            return True
        return any(os.path.getmtime(file_path) > self.last_loaded for file_path in self.all_file_pathes)

    @staticmethod
    def _check_item_aspect(filter_data: dict[str, Any], aspect: Aspect) -> bool:
        # TODO: really should add configuration schema and validate it once on load so all of these checks in code are not necessary
        if "aspect" not in filter_data:
            return True
        if isinstance(filter_data["aspect"], str):
            filter_data["aspect"] = [filter_data["aspect"]]
        # check type
        if aspect.type != filter_data["aspect"][0]:
            return False
        # check value
        if len(filter_data["aspect"]) > 1:
            if aspect.value is None:
                return False
            threshold = filter_data["aspect"][1]
            condition = filter_data["aspect"][2] if len(filter_data["aspect"]) > 2 else "larger"
            if not (
                threshold is None
                or (isinstance(condition, str) and condition == "larger" and aspect.value >= threshold)
                or (isinstance(condition, str) and condition == "smaller" and aspect.value <= threshold)
            ):
                return False
        return True

    @staticmethod
    def _check_item_power(filter_data: dict[str, Any], power: int, min_key: str = "minPower", max_key: str = "maxPower") -> bool:
        # TODO: really should add configuration schema and validate it once on load so all of these checks in code are not necessary
        min_power = filter_data[min_key] if min_key in filter_data and filter_data[min_key] is not None else 1
        if not isinstance(min_power, int):
            Logger.warning(f"{min_key} ({min_power}) is not an integer!")
            return False
        max_power = filter_data[max_key] if max_key in filter_data and filter_data[max_key] is not None else 9999
        if not isinstance(max_power, int):
            Logger.warning(f"{max_key} ({max_power}) is not an integer!")
            return False
        return min_power <= power <= max_power

    @staticmethod
    def _check_item_type(filter_data: dict[str, Any], item_type: ItemType) -> bool:
        # TODO: really should add configuration schema and validate it once on load so all of these checks in code are not necessary
        if "itemType" not in filter_data:
            return True
        filter_item_type_list = [
            ItemType(val) for val in ([filter_data["itemType"]] if isinstance(filter_data["itemType"], str) else filter_data["itemType"])
        ]
        return item_type in filter_item_type_list

    def _match_affixes(self, filter_affix_pool: list, item_affix_pool: list[Affix]) -> list:
        item_affix_pool = item_affix_pool[:]
        matched_affixes = []
        if filter_affix_pool is None:
            return matched_affixes
        filter_affix_pool = [filter_affix_pool] if isinstance(filter_affix_pool, str) else filter_affix_pool

        for affix in filter_affix_pool:
            if isinstance(affix, dict) and "any_of" in affix:
                any_of_matched = self._match_affixes(affix["any_of"], item_affix_pool)
                if len(any_of_matched) > 0:
                    name = any_of_matched[0]
                    item_affix_pool = [a for a in item_affix_pool if a.type != name]
                    matched_affixes.append(name)
            else:
                name, *rest = affix if isinstance(affix, list) else [affix]
                threshold = rest[0] if rest else None
                condition = rest[1] if len(rest) > 1 else "larger"

                item_affix_value = next((a.value for a in item_affix_pool if a.type == name), None)
                if item_affix_value is not None:
                    if (
                        threshold is None
                        or (isinstance(condition, str) and condition == "larger" and item_affix_value >= threshold)
                        or (isinstance(condition, str) and condition == "smaller" and item_affix_value <= threshold)
                    ):
                        item_affix_pool = [a for a in item_affix_pool if a.type != name]
                        matched_affixes.append(name)
                elif any(a.type == name for a in item_affix_pool):
                    item_affix_pool = [a for a in item_affix_pool if a.type != name]
                    matched_affixes.append(name)
        return matched_affixes

    def _check_non_unique_item(self, item: Item) -> FilterResult:
        # TODO replace me next league
        res = FilterResult(False, [])
        if item.rarity != ItemRarity.Unique and item.type != ItemType.Sigil:
            for profile_str, affix_filter in self.affix_filters.items():
                for filter_dict in affix_filter:
                    for filter_name, filter_data in filter_dict.items():
                        filter_min_affix_count = (
                            filter_data["minAffixCount"]
                            if "minAffixCount" in filter_data and filter_data["minAffixCount"] is not None
                            else 0
                        )
                        power_ok = self._check_item_power(filter_data, item.power)
                        type_ok = self._check_item_type(filter_data, item.type)
                        if not power_ok or not type_ok:
                            continue
                        matched_affixes = self._match_affixes(filter_data["affixPool"], item.affixes)
                        affixes_ok = filter_min_affix_count is None or len(matched_affixes) >= filter_min_affix_count
                        inherent_ok = True
                        matched_inherent = []
                        if "inherentPool" in filter_data:
                            matched_inherent = self._match_affixes(filter_data["inherentPool"], item.inherent)
                            inherent_ok = len(matched_inherent) > 0
                        if affixes_ok and inherent_ok:
                            all_matched_affixes = matched_affixes + matched_inherent
                            affix_debug_msg = [name for name in all_matched_affixes]
                            Logger.info(f"Matched {profile_str}.Affixes.{filter_name}: {affix_debug_msg}")
                            res.keep = True
                            res.matched.append(MatchedFilter(f"{profile_str}.{filter_name}", all_matched_affixes))

            if item.aspect:
                for profile_str, aspect_filter in self.aspect_filters.items():
                    for filter_data in aspect_filter:
                        aspect_name, *rest = filter_data if isinstance(filter_data, list) else [filter_data]
                        threshold = rest[0] if rest else None
                        condition = rest[1] if len(rest) > 1 else "larger"

                        if item.aspect.type == aspect_name:
                            if (
                                threshold is None
                                or item.aspect.value is None
                                or (isinstance(condition, str) and condition == "larger" and item.aspect.value >= threshold)
                                or (isinstance(condition, str) and condition == "smaller" and item.aspect.value <= threshold)
                            ):
                                Logger.info(f"Matched {profile_str}.Aspects: [{item.aspect.type}, {item.aspect.value}]")
                                res.keep = True
                                res.matched.append(MatchedFilter(f"{profile_str}.Aspects", did_match_aspect=True))
        return res

    def _check_sigil(self, item: Item) -> FilterResult:
        res = FilterResult(False, [])
        if len(self.sigil_filters.items()) == 0:
            res.keep = True
            res.matched.append(MatchedFilter(""))
        for profile_name, profile_filter in self.sigil_filters.items():
            # check item power
            if not self._check_item_power(profile_filter, item.power, min_key="minTier", max_key="maxTier"):
                continue
            # check affix
            if "blacklist" in profile_filter and self._match_affixes(profile_filter["blacklist"], item.affixes + item.inherent):
                continue
            if "whitelist" in profile_filter and not self._match_affixes(profile_filter["whitelist"], item.affixes + item.inherent):
                continue
            Logger.info(f"Matched {profile_name}.Sigils")
            res.keep = True
            res.matched.append(MatchedFilter(f"{profile_name}"))
        return res

    def _check_unique_item(self, item: Item) -> FilterResult:
        # TODO: really should add configuration schema and validate it once on load so all of these checks in code are not necessary
        res = FilterResult(False, [])
        for profile_name, profile_filter in self.unique_filters.items():
            for filter_item in profile_filter:
                # check item type
                if not self._check_item_type(filter_item, item.type):
                    continue
                # check item power
                if not self._check_item_power(filter_item, item.power):
                    continue
                # check aspect
                if item.aspect is None or not self._check_item_aspect(filter_item, item.aspect):
                    continue
                # check affixes
                filter_item.setdefault("affixPool", [])
                matched_affixes = self._match_affixes([] if "affixPool" not in filter_item else filter_item["affixPool"], item.affixes)
                if len(matched_affixes) != len(filter_item["affixPool"]):
                    continue
                Logger.info(f"Matched {profile_name}.Uniques: {item.aspect.type}")
                res.keep = True
                res.matched.append(MatchedFilter(f"{profile_name}.{item.aspect.type}", did_match_aspect=True))
        return res

    def should_keep(self, item: Item) -> FilterResult:
        if not self.files_loaded or self._did_files_change():
            self.load_files()

        res = FilterResult(False, [])

        if item.type is None or item.power is None:
            return res

        if item.type == ItemType.Sigil:
            return self._check_sigil(item)

        if item.rarity != ItemRarity.Unique and item.type != ItemType.Sigil:
            return self._check_non_unique_item(item)

        if item.rarity == ItemRarity.Unique:
            return self._check_unique_item(item)

        return res

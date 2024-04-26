from item.data.affix import Affix
from item.data.item_type import ItemType
from item.data.rarity import ItemRarity
from item.models import Item


class TestItem(Item):
    def __init__(self, rarity=ItemRarity.Rare, power=910, **kwargs):
        super().__init__(rarity=rarity, power=power, **kwargs)


affixes = [
    ("wrong type", [], TestItem(item_type=ItemType.Amulet)),
    ("power too low", [], TestItem(item_type=ItemType.Helm, power=724)),
    (
        "res boots 4 res",
        [],
        TestItem(
            item_type=ItemType.Boots,
            affixes=[
                Affix(type="cold_resistance", value=5),
                Affix(type="fire_resistance", value=5),
                Affix(type="poison_resistance", value=5),
                Affix(type="shadow_resistance", value=5),
            ],
        ),
    ),
    (
        "res boots 3 res",
        [],
        TestItem(
            item_type=ItemType.Boots,
            affixes=[
                Affix(type="cold_resistance", value=5),
                Affix(type="fire_resistance", value=5),
                Affix(type="shadow_resistance", value=5),
            ],
        ),
    ),
    (
        "res boots 3 res+ms",
        ["test.ResBoots"],
        TestItem(
            item_type=ItemType.Boots,
            affixes=[
                Affix(type="cold_resistance", value=5),
                Affix(type="movement_speed", value=5),
                Affix(type="fire_resistance", value=5),
                Affix(type="shadow_resistance", value=5),
            ],
        ),
    ),
    (
        "res boots 2 res",
        [],
        TestItem(
            item_type=ItemType.Boots,
            affixes=[
                Affix(type="cold_resistance", value=5),
                Affix(type="shadow_resistance", value=5),
            ],
        ),
    ),
    (
        "res boots 2 res+ms",
        ["test.ResBoots"],
        TestItem(
            item_type=ItemType.Boots,
            affixes=[
                Affix(type="cold_resistance", value=5),
                Affix(type="movement_speed", value=5),
                Affix(type="shadow_resistance", value=5),
            ],
        ),
    ),
    (
        "helm life",
        [],
        TestItem(
            item_type=ItemType.Helm,
            affixes=[
                Affix(type="maximum_life", value=5),
                Affix(type="movement_speed", value=5),
                Affix(type="fire_resistance", value=5),
                Affix(type="shadow_resistance", value=5),
            ],
        ),
    ),
    (
        "boots inherent",
        ["test.GreatBoots", "test.ResBoots"],
        TestItem(
            item_type=ItemType.Boots,
            affixes=[
                Affix(type="movement_speed", value=5),
                Affix(type="cold_resistance", value=5),
                Affix(type="lightning_resistance", value=5),
            ],
            inherent=[Affix(type="maximum_evade_charges", value=5)],
        ),
    ),
    (
        "boots no inherent",
        ["test.ResBoots"],
        TestItem(
            item_type=ItemType.Boots,
            affixes=[
                Affix(type="movement_speed", value=5),
                Affix(type="cold_resistance", value=5),
                Affix(type="lightning_resistance", value=5),
            ],
            inherent=[Affix(type="maximum_fury", value=5)],
        ),
    ),
    (
        "boots exact values",
        ["test.ResBoots", "test.ResBootsExact"],
        TestItem(
            item_type=ItemType.Boots,
            affixes=[
                Affix(type="movement_speed", value=4),
                Affix(type="cold_resistance", value=4),
                Affix(type="lightning_resistance", value=4),
            ],
            inherent=[Affix(type="maximum_fury", value=5)],
        ),
    ),
]

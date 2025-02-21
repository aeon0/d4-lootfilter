import pytest

import src.tts
from src.item.data.affix import AffixType
from src.item.data.aspect import Aspect
from src.item.data.item_type import ItemType
from src.item.data.rarity import ItemRarity
from src.item.descr.read_descr_tts import read_descr
from src.item.models import Affix, Item

items = [
    (
        [
            "BLOOD BOILING LOOP OF BALEFUL INTENT",
            "Legendary Ring",
            "750 Item Power",
            "+10.0% Resistance to All Elements",
            "+10.0% Cold Resistance",
            "+97 Dexterity",
            "+261 Maximum Life",
            "+54.0% Overpower Damage",
            "When your Core Skills Overpower an enemy, you spawn 3 Volatile Blood Drops. Collecting a Volatile Blood Drop causes it to explode, dealing 813 Physical damage around you.. Every 20 seconds, your next Skill is guaranteed to Overpower.",
            "Empty Socket",
            "Requires Level 60",
            "Sell Value: 45,145 Gold",
            "Tempers: 5/5",
            "Mousewheel scroll down",
            "Scroll Down",
            "Right mouse button",
        ],
        Item(
            affixes=[
                Affix(name="dexterity", type=AffixType.greater, value=97),
                Affix(name="maximum_life", type=AffixType.greater, value=261),
                Affix(name="overpower_damage", type=AffixType.greater, value=54),
            ],
            inherent=[
                Affix(name="resistance_to_all_elements", type=AffixType.inherent, value=10),
                Affix(name="cold_resistance", type=AffixType.inherent, value=10),
            ],
            name="blood_boiling_loop_of_baleful_intent",
            item_type=ItemType.Ring,
            power=750,
            rarity=ItemRarity.Legendary,
        ),
    ),
    (
        [
            "TORMENTORS GOLDEN QUARTERSTAFF",
            "Legendary Quarterstaff",
            "750 Item Power",
            "523 Damage Per Second  (-73)",
            "[381 - 571] Damage per Hit",
            "1.10 Attacks per Second (Fast)",
            "40% Block Chance",
            "+182 Dexterity",
            "+544 Maximum Life",
            "+112.0% Damage Over Time",
            "Enemies who move while Poisoned by you additionally take 160% of your Thorns damage per second.",
            "Empty Socket",
            "Empty Socket",
            "Requires Level 60. Spiritborn. Vessel of Hatred Item",
            "Sell Value: 82,765 Gold",
            "Durability: 100/100. Tempers: 5/5",
            "Right mouse button",
        ],
        Item(
            affixes=[
                Affix(name="dexterity", type=AffixType.greater, value=182),
                Affix(name="maximum_life", type=AffixType.greater, value=544),
                Affix(name="damage_over_time", type=AffixType.greater, value=112),
            ],
            inherent=[Affix(name="block_chance", type=AffixType.inherent, value=40)],
            name="tormentors_golden_quarterstaff",
            item_type=ItemType.Quarterstaff,
            power=750,
            rarity=ItemRarity.Legendary,
        ),
    ),
    (
        [
            "TORMENTORS ELEGANT POLEARM",
            "Legendary Polearm",
            "750 Item Power",
            "Armory Loadout",
            "523 Damage Per Second",
            "[466 - 698] Damage per Hit",
            "0.90 Attacks per Second (Slow)",
            "+76.5% Vulnerable Damage [76.5]%",
            "+185 Dexterity +[178 - 198]",
            "+2 Vigor On Kill +[2]",
            "+72.0% Vulnerable Damage [70.0 - 90.0]%",
            "Enemies who move while Poisoned by you additionally take 280% [100 - 380]% of your Thorns damage per second.",
            "Empty Socket",
            "Empty Socket",
            "Requires Level 60. Spiritborn. Vessel of Hatred Item",
            "Sell Value: 82,765 Gold",
            "Durability: 100/100. Tempers: 5/5",
            "Right mouse button",
        ],
        Item(
            affixes=[
                Affix(max_value=198.0, min_value=178.0, name="dexterity", type=AffixType.normal, value=185.0),
                Affix(max_value=2.0, min_value=2.0, name="vigor_on_kill", type=AffixType.normal, value=2.0),
                Affix(max_value=90.0, min_value=70.0, name="vulnerable_damage", type=AffixType.normal, value=72.0),
            ],
            inherent=[Affix(max_value=76.5, min_value=76.5, name="vulnerable_damage", type=AffixType.inherent, value=76.5)],
            name="tormentors_elegant_polearm",
            item_type=ItemType.Polearm,
            power=750,
            rarity=ItemRarity.Legendary,
        ),
    ),
    # Unique with an abnormal amount of inherents (1, normally pants have 0).
    # Also, equipped, so affixes don't have a (+x.xx) at the end
    (
        [
            "KESSIMES LEGACY",
            "Unique Pants",
            "750 Item Power",
            "150 Armor",
            "Casting Blood Wave Fortifies You For +70.0% Maximum Life [70.0]%",
            "+215.0% Ultimate Damage [187.0 - 250.0]%",
            "13.5% Damage Reduction while Fortified [9.5 - 14.5]%",
            "+23.5% Chance for Blood Wave to Deal Double Damage [23.5 - 32.5]%",
            "20.0% Blood Wave Cooldown Reduction [16.0 - 25.0]%",
            "Blood Wave now forms a wave on each side of you. Both waves converge at your feet, Pulling In all surrounding enemies and exploding for 1,548 [794 - 1,588] damage.. Each wave hit causes enemies to take 9.75% [5.00 - 10.00]% more damage from your Blood Waves, up to 292.5% [150.0 - 300.0]%.",
            "+30 Intelligence",
            "+30 Intelligence",
            "Too soon she was taken, yet Rathma let Kessime rest in death - for they both had found peace in the cycle. Upon the hill where she lay, Rathma poured forth his blood and no evil trod thereafter...",
            "Requires Level 60. Account BoundNecromancer. Only. Unique Equipped",
            "Sell Value: 150,482 Gold",
            "Durability: 50/100",
            "Right mouse button",
        ],
        Item(
            affixes=[
                Affix(
                    max_value=250.0,
                    min_value=187.0,
                    name="ultimate_damage",
                    type=AffixType.normal,
                    value=215.0,
                ),
                Affix(
                    max_value=14.5,
                    min_value=9.5,
                    name="damage_reduction_while_fortified",
                    type=AffixType.normal,
                    value=13.5,
                ),
                Affix(
                    max_value=32.5,
                    min_value=23.5,
                    name="chance_for_blood_wave_to_deal_double_damage",
                    type=AffixType.normal,
                    value=23.5,
                ),
                Affix(
                    max_value=25.0,
                    min_value=16.0,
                    name="blood_wave_cooldown_reduction",
                    type=AffixType.normal,
                    value=20.0,
                ),
            ],
            aspect=Aspect(
                name="kessimes_legacy",
                text="Blood Wave now forms a wave on each side of you. Both waves converge at your feet, Pulling In all surrounding enemies and exploding for 1,548 [794 - 1,588] damage.. Each wave hit causes enemies to take 9.75% [5.00 - 10.00]% more damage from your Blood Waves, up to 292.5% [150.0 - 300.0]%.",
                value=1548.0,
            ),
            inherent=[
                Affix(
                    max_value=70.0,
                    min_value=70.0,
                    name="casting_blood_wave_fortifies_you_for_maximum_life",
                    type=AffixType.inherent,
                    value=70.0,
                )
            ],
            item_type=ItemType.Legs,
            name="kessimes_legacy",
            power=750,
            rarity=ItemRarity.Unique,
        ),
    ),
    # Unique with no greater affixes and weird inherents
    (
        [
            "THE MORTACRUX",
            "Unique Dagger",
            "750 Item Power",
            "261 Damage Per Second  (-334)",
            "[174 - 262] Damage per Hit",
            "1.20 Attacks per Second (Very Fast) (+0.30)",
            "+85.0% Macabre Damage [85.0]% (+85.0%)",
            "+85.0% Corpse Damage [85.0]% (+85.0%)",
            "+78 Intelligence +[73 - 83] (-157)",
            "+45.5% Chance for Corpse Explosion to Deal Double Damage [36.5 - 50.0]% (+45.5%)",
            "Hewed Flesh Grants 7.0% Maximum Life as Barrier for 4 Seconds [7.0 - 9.0]% (+7.0%)",
            "+2 to Hewed Flesh [2 - 4] (+2)",
            "When consuming a Corpse, there is a 26% [20 - 40]% chance to also create a decaying Skeletal Simulacrum that seeks enemies but cannot attack. When it dies, it explodes for 2,382 Shadow damage. . This effect is treated as a Macabre Skill.",
            "Empty Socket",
            "Properties lost when equipped:",
            "+874 Maximum Life",
            "+2 to Finality",
            "+512.7% Overpower Damage",
            "+205.0% Damage while Fortified",
            "Legendary Power",
            "Socket (1)",
            "One of a pair of twin daggers, forbidden from ever meeting. Nearby corpses shudder in its presence.",
            "Requires Level 60Necromancer. Only. Unique Equipped",
            "Unlocks new look on salvage",
            "Sell Value: 184,341 Gold",
            "Durability: 100/100",
            "Right mouse button",
        ],
        Item(
            affixes=[
                Affix(
                    max_value=83,
                    min_value=73,
                    name="intelligence",
                    text="+78 Intelligence +[73 - 83] (-157)",
                    type=AffixType.normal,
                    value=78.0,
                ),
                Affix(
                    max_value=50.0,
                    min_value=36.5,
                    name="chance_for_corpse_explosion_to_deal_double_damage",
                    text="+45.5% Chance for Corpse Explosion to Deal Double Damage [36.5 - 50.0]% (+45.5%)",
                    type=AffixType.normal,
                    value=45.5,
                ),
                Affix(
                    max_value=9.0,
                    min_value=7.0,
                    name="hewed_flesh_grants_maximum_life_as_barrier_for_seconds",
                    text="Hewed Flesh Grants 7.0% Maximum Life as Barrier for 4 Seconds [7.0 - 9.0]% (+7.0%)",
                    type=AffixType.normal,
                    value=7.0,
                ),
                Affix(
                    max_value=4,
                    min_value=2,
                    name="to_hewed_flesh",
                    text="+2 to Hewed Flesh [2 - 4] (+2)",
                    type=AffixType.normal,
                    value=2.0,
                ),
            ],
            aspect=Aspect(
                name="the_mortacrux",
                text="When consuming a Corpse, there is a 26% [20 - 40]% chance to also create a decaying Skeletal Simulacrum that seeks enemies but cannot attack. When it dies, it explodes for 2,382 Shadow damage. . This effect is treated as a Macabre Skill.",
                value=26,
            ),
            codex_upgrade=False,
            inherent=[
                Affix(
                    max_value=85,
                    min_value=85,
                    name="macabre_damage",
                    text="+85.0% Macabre Damage [85.0]% (+85.0%)",
                    type=AffixType.inherent,
                    value=85.0,
                ),
                Affix(
                    max_value=85,
                    min_value=85,
                    name="corpse_damage",
                    text="+85.0% Corpse Damage [85.0]% (+85.0%)",
                    type=AffixType.inherent,
                    value=85.0,
                ),
            ],
            item_type=ItemType.Dagger,
            name="the_mortacrux",
            power=750,
            rarity=ItemRarity.Unique,
        ),
    ),
    # Unique with GA
    (
        [
            "SHARD OF VERATHIEL",
            "Ancestral Unique Sword",
            "800 Item Power",
            "298 Damage Per Second  (-297)",
            "[217 - 325] Damage per Hit",
            "1.10 Attacks per Second (Fast) (+0.20)",
            "+50.0% Damage [50.0]% (+50.0%)",
            "+56 All Stats +[51 - 65] (+56)",
            "+24 Maximum Resource (+24)",
            "+18.0% Basic Attack Speed [16.0 - 25.0]% (+18.0%)",
            "+2 to Basic Skills [1 - 2] (+2)",
            "Basic Skills deal 133%[x] [50 - 200]% increased damage but additionally cost 25 Primary Resource.",
            "Empty Socket",
            "Properties lost when equipped:",
            "+874 Maximum Life",
            "+2 to Finality",
            "+512.7% Overpower Damage",
            "+205.0% Damage while Fortified",
            "+235 Intelligence",
            "Legendary Power",
            "Socket (1)",
            "This blade once bore divine purpose wielded by the angel Verathiel. Like its keeper, the sword fell to Infernal depths. Yet beneath this corruption, is a heartbeat of a past memory, holding steadfast.",
            "Requires Level 60. Unique Equipped",
            "Sell Value: 206,382 Gold",
            "Durability: 100/100",
            "Right mouse button",
        ],
        Item(
            affixes=[
                Affix(
                    max_value=65.0,
                    min_value=51.0,
                    name="all_stats",
                    text="+56 All Stats +[51 - 65] (+56)",
                    type=AffixType.normal,
                    value=56.0,
                ),
                Affix(
                    max_value=None,
                    min_value=None,
                    name="maximum_resource",
                    text="+24 Maximum Resource (+24)",
                    type=AffixType.greater,
                    value=24.0,
                ),
                Affix(
                    max_value=25.0,
                    min_value=16.0,
                    name="basic_attack_speed",
                    text="+18.0% Basic Attack Speed [16.0 - 25.0]% (+18.0%)",
                    type=AffixType.normal,
                    value=18.0,
                ),
                Affix(
                    max_value=2.0,
                    min_value=1.0,
                    name="to_basic_skills",
                    text="+2 to Basic Skills [1 - 2] (+2)",
                    type=AffixType.normal,
                    value=2.0,
                ),
            ],
            aspect=Aspect(
                name="shard_of_verathiel",
                text="Basic Skills deal 133%[x] [50 - 200]% increased damage but additionally cost 25 Primary Resource.",
                value=133.0,
            ),
            codex_upgrade=False,
            inherent=[
                Affix(
                    max_value=50.0,
                    min_value=50.0,
                    name="damage",
                    text="+50.0% Damage [50.0]% (+50.0%)",
                    type=AffixType.inherent,
                    value=50.0,
                )
            ],
            item_type=ItemType.Sword,
            name="shard_of_verathiel",
            power=800,
            rarity=ItemRarity.Unique,
        ),
    ),
    # Another unique incorrectly parsing a GA
    (
        [
            "FROSTBURN",
            "Unique Gloves",
            "750 Item Power",
            "60 Armor",
            "+7.0% Lucky Hit Chance [7.0]%",
            "+12.0% Attack Speed [8.0 - 12.5]% (+12.0%)",
            "+124.0% Fire and Cold Damage [124.0 - 160.0]% (+124.0%)",
            "Lucky Hit: Up to a 40% Chance to Deal +650 Fire Damage [600 - 1,000] (+650)",
            "Lucky Hit: Up to a 40% Chance to Deal +1,000 Cold Damage [600 - 1,000] (+1,000)",
            "Lucky Hit: Up to a 40% [20 - 60]% chance to Freeze enemies for 3 seconds.",
            "Properties lost when equipped:",
            "+144.5% Blood Overpower Damage",
            "+35.5% Corpse Tendrils Size",
            "+98 Intelligence",
            "+6.8% Critical Strike Chance",
            "Legendary Power",
            "A touch so frigid it stops the heart and chills the very soul.",
            "Requires Level 60. Unique Equipped",
            "Sell Value: 90,289 Gold",
            "Durability: 100/100",
            "Right mouse button",
        ],
        Item(
            affixes=[
                Affix(
                    max_value=12.5,
                    min_value=8.0,
                    name="attack_speed",
                    text="+12.0% Attack Speed [8.0 - 12.5]% (+12.0%)",
                    type=AffixType.normal,
                    value=12.0,
                ),
                Affix(
                    max_value=160.0,
                    min_value=124.0,
                    name="fire_and_cold_damage",
                    text="+124.0% Fire and Cold Damage [124.0 - 160.0]% (+124.0%)",
                    type=AffixType.normal,
                    value=124.0,
                ),
                Affix(
                    max_value=1000,
                    min_value=600,
                    name="lucky_hit_up_to_a_chance_to_deal_fire_damage",
                    text="Lucky Hit: Up to a 40% Chance to Deal +650 Fire Damage [600 - 1,000] (+650)",
                    type=AffixType.normal,
                    value=650.0,
                ),
                Affix(
                    max_value=1000,
                    min_value=600,
                    name="lucky_hit_up_to_a_chance_to_deal_cold_damage",
                    text="Lucky Hit: Up to a 40% Chance to Deal +1,000 Cold Damage [600 - 1,000] (+1,000)",
                    type=AffixType.normal,
                    value=1000.0,
                ),
            ],
            aspect=Aspect(name="frostburn", text="Lucky Hit: Up to a 40% [20 - 60]% chance to Freeze enemies for 3 seconds.", value=40.0),
            codex_upgrade=False,
            inherent=[
                Affix(
                    max_value=7.0,
                    min_value=7.0,
                    name="lucky_hit_chance",
                    text="+7.0% Lucky Hit Chance [7.0]%",
                    type=AffixType.inherent,
                    value=7.0,
                )
            ],
            item_type=ItemType.Gloves,
            name="frostburn",
            power=750,
            rarity=ItemRarity.Unique,
        ),
    ),
    # Another with misidentified affix
    (
        [
            "APHOTIC DOOM CASQUE",
            "Legendary Helm",
            "750 Item Power",
            "120 Armor",
            "+255 Maximum Life [244 - 272] (-58)",
            "+173 Life per 5 Seconds [147 - 213] (+173)",
            "+2 to Skeletal Warrior Mastery [1 - 2] (+2)",
            "Skeletal Priests empower your Skeletal Warriors attacks to deal Shadow damage and have a 12.0% [5.0 - 20.0]% chance to Stun enemies for 1.5 seconds.",
            "Empty Socket",
            "Empty Socket",
            "Properties lost when equipped:",
            "Lucky Hit: Up to a +17.8% Chance to Stun for 2 Seconds",
            "9.7% Cooldown Reduction",
            "+15.4% Total Armor",
            "+107 Intelligence",
            "Legendary Power",
            "Requires Level 60. Account Bound",
            "Sell Value: 33,859 Gold",
            "Durability: 100/100. Tempers: 5/5",
            "Right mouse button",
        ],
        Item(
            affixes=[
                Affix(
                    max_value=272.0,
                    min_value=244.0,
                    name="maximum_life",
                    text="+255 Maximum Life [244 - 272] (-58)",
                    type=AffixType.normal,
                    value=255.0,
                ),
                Affix(
                    max_value=213,
                    min_value=147,
                    name="life_per_seconds",
                    text="+173 Life per 5 Seconds [147 - 213] (+173)",
                    type=AffixType.normal,
                    value=173.0,
                ),
                Affix(
                    max_value=2.0,
                    min_value=1.0,
                    name="to_skeletal_warrior_mastery",
                    text="+2 to Skeletal Warrior Mastery [1 - 2] (+2)",
                    type=AffixType.normal,
                    value=2.0,
                ),
            ],
            aspect=None,
            codex_upgrade=False,
            inherent=[],
            item_type=ItemType.Helm,
            name="aphotic_doom_casque",
            power=750,
            rarity=ItemRarity.Legendary,
        ),
    ),
    # Test for lucky hit chance to make enemies vulnerable
    (
        [
            "ADVENTURERS GLOVES OF ULTIMATE SHADOW",
            "Legendary Gloves",
            "750 Item Power",
            "60 Armor",
            "+272 Maximum Life [244 - 272]",
            "Lucky Hit: Up to a +43.8% Chance to Make Enemies Vulnerable for 2 Seconds [43.3 - 47.2]%[2]",
            "+2 to Core Skills [1 - 2]",
            "Bone Storm and Blood Wave are also Darkness Skills, deal Shadow damage, and gain additional effects: . Enemies damaged by Bone Storm take 873 [635 - 1,429] Shadow damage over 2 seconds. . Blood Wave creates Desecrated Ground as it travels, dealing 13,974 [10,163 - 22,867] Shadow damage over 4 seconds",
            "Requires Level 60",
            "Sell Value: 22,572 Gold",
            "Durability: 100/100. Tempers: 5/5",
            "Right mouse button",
        ],
        Item(
            affixes=[
                Affix(
                    max_value=272.0,
                    min_value=244.0,
                    name="maximum_life",
                    text="+272 Maximum Life [244 - 272]",
                    type=AffixType.normal,
                    value=272.0,
                ),
                Affix(
                    max_value=47.2,
                    min_value=43.3,
                    name="lucky_hit_up_to_a_chance_to_make_enemies_vulnerable_for_seconds",
                    text="Lucky Hit: Up to a +43.8% Chance to Make Enemies Vulnerable for 2 Seconds [43.3 - 47.2]%[2]",
                    type=AffixType.normal,
                    value=43.8,
                ),
                Affix(
                    max_value=2.0,
                    min_value=1.0,
                    name="to_core_skills",
                    text="+2 to Core Skills [1 - 2]",
                    type=AffixType.normal,
                    value=2.0,
                ),
            ],
            aspect=None,
            codex_upgrade=False,
            inherent=[],
            item_type=ItemType.Gloves,
            name="adventurers_gloves_of_ultimate_shadow",
            power=750,
            rarity=ItemRarity.Legendary,
        ),
    ),
    (
        [
            "BLOOD ARTISANS CUIRASS",
            "Unique Chest Armor",
            "750 Item Power",
            "210 Armor",
            "+305 Maximum Life [305 - 340]",
            "+125.0% Damage for 4 Seconds After Picking Up a Blood Orb [98.0 - 125.0]%[4]",
            "Blood Orbs Restore +9 Essence [8 - 12]",
            "+3 to Bone Spirit [2 - 3]",
            "When you pick up 5 [10 - 3] Blood Orbs, a free Bone Spirit is spawned, dealing bonus damage based on your current Life percent.",
            "Empty Socket",
            "The infamous Necromancer Gaza-Thuls mastery over blood magic was indisputable. Many suspect that upon his death, his skin was used to fashion this eldritch armor.. - Barretts Book of Implements",
            "Requires Level 60Necromancer. Only. Unique Equipped",
            "Sell Value: 184,341 Gold",
            "Durability: 100/100",
            "Right mouse button",
        ],
        Item(
            affixes=[
                Affix(
                    max_value=340.0,
                    min_value=305.0,
                    name="maximum_life",
                    text="+305 Maximum Life [305 - 340]",
                    type=AffixType.normal,
                    value=305.0,
                ),
                Affix(
                    max_value=125.0,
                    min_value=98.0,
                    name="damage_for_seconds_after_picking_up_a_blood_orb",
                    text="+125.0% Damage for 4 Seconds After Picking Up a Blood Orb [98.0 - 125.0]%[4]",
                    type=AffixType.normal,
                    value=125.0,
                ),
                Affix(
                    max_value=12.0,
                    min_value=8.0,
                    name="blood_orbs_restore_essence",
                    text="Blood Orbs Restore +9 Essence [8 - 12]",
                    type=AffixType.normal,
                    value=9.0,
                ),
                Affix(
                    max_value=3.0,
                    min_value=2.0,
                    name="to_bone_spirit",
                    text="+3 to Bone Spirit [2 - 3]",
                    type=AffixType.normal,
                    value=3.0,
                ),
            ],
            aspect=Aspect(
                name="blood_artisans_cuirass",
                text="When you pick up 5 [10 - 3] Blood Orbs, a free Bone Spirit is spawned, dealing bonus damage based on your current Life percent.",
                value=5.0,
            ),
            codex_upgrade=False,
            inherent=[],
            item_type=ItemType.ChestArmor,
            name="blood_artisans_cuirass",
            power=750,
            rarity=ItemRarity.Unique,
        ),
    ),
]


@pytest.mark.parametrize(("input_item", "expected_item"), items)
def test_items(input_item: list[str], expected_item: Item):
    src.tts.LAST_ITEM = input_item
    item = read_descr()
    assert item == expected_item

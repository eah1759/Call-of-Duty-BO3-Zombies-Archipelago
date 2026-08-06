import string
import math
import os
import json

from BaseClasses import Location, MultiWorld, Region, Item, ItemClassification
from worlds.generic.Rules import set_rule, add_rule
from . import rules

from worlds.AutoWorld import World, WebWorld

from rule_builder.rules import Has, HasAll, HasGroupUnique

from . import Locations, Items, Options, Weapons
from .Options import BO3ZombiesOptions, bo3_option_groups
from .Names import ItemName, LocationName, RegionName, Maps
from .Locations import LocationData
from .Weapons import weapon_data_set, WeaponData, WeaponDistribution
from .Items import ItemData, BO3ZombiesItemCategory

class BO3ZombiesWeb(WebWorld):
    theme = "ocean"
    option_groups = bo3_option_groups

class BO3ZombiesLocation(Location):
    game: str = "Black Ops 3 - Zombies"

    @staticmethod
    def get_name_to_id(base_id) -> dict:
        return {loc_data.name: loc_data.code + base_id for loc_data in Locations.all_locations}

class BO3ZombiesWorld(World):
    """
    TODO: Game Description
    """
    game: str = "Black Ops 3 - Zombies"
    web = BO3ZombiesWeb()

    options_dataclass = BO3ZombiesOptions
    options: BO3ZombiesOptions

    required_client_version = (0, 6, 0)

    topology_present = True
    # Game's SteamID
    base_id = 311210
    item_name_to_id = Items.BO3ZombiesItem.get_name_to_id(base_id)
    location_name_to_id = BO3ZombiesLocation.get_name_to_id(base_id)

    item_name_groups = Items.item_groups

    # Full Remote Items
    items_handling = 0b111

    # Enable to log the location lua data
    write_lua_locations = False

    # Generate GSC scripts to apply AP item names to ingame console names
    def generate_gsc_code(self):
        """Generate GSC code for weapon mappings with table separation and fallback."""
        lines = [
            'function init_weapon_item_names()',
            '{',
            '    level.archi.weapon_item_names = [];',
            '    level.archi.weapon_item_names["vanilla"] = [];',
            '    level.archi.weapon_item_names["zm_westernz"] = [];',
            ''
        ]
        
        for key in weapon_data_set.keys():
            data_set = weapon_data_set[key]
            for console_name, weapon_data in data_set.items():
                item_name = weapon_data.item_name.replace("ItemName.", "")
                lines.append(f'    level.archi.weapon_item_names["{key}"]["{console_name}"] = "{item_name}";')
            lines.append('')

        lines.append('}')
        lines.append('')
        
        # Add lookup function with fallback
        lines.extend([
            'function get_weapon_item_name(console_name, table)',
            '{',
            '    // Try specified table first',
            '    if(isdefined(level.archi.weapon_item_names[table]) && isdefined(level.archi.weapon_item_names[table][console_name]))',
            '    {',
            '        return level.archi.weapon_item_names[table][console_name];',
            '    }',
            '    ',
            '    // Fallback to vanilla',
            '    if(isdefined(level.archi.weapon_item_names["vanilla"][console_name]))',
            '    {',
            '        return level.archi.weapon_item_names["vanilla"][console_name];',
            '    }',
            '    ',
            '    return undefined;',
            '}'
        ])
        
        # Usage
        gsc_code = '\n'.join(lines)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(script_dir, 'archi_mappings.gsc'), 'w') as f:
            f.write(gsc_code)

    def generate_early(self) -> None:
        if self.write_lua_locations:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            with open(os.path.join(script_dir, 'Locations.lua'), 'w', encoding='utf-8') as f:
                f.write("local LocationToID = {}\n")
                f.write("local IDToLocation = {}\n")
                for location in Locations.all_locations:
                    f.write("LocationToID[\"{}\"] = {}\n".format(location.name, location.code))
                    f.write("IDToLocation[{}] = \"{}\"\n".format(location.code, location.name))
                f.write("local locations = { LocationToID = LocationToID, IDToLocation = IDToLocation }\n")
                f.write("return locations\n")

            self.generate_gsc_code()

        # At least one map has to be enabled
        if (not self.options.map_shadows_enabled and not self.options.map_castle_enabled
            and not self.options.map_zetsubou_enabled and not self.options.map_gorod_enabled
            and not self.options.map_revelations_enabled and not self.options.map_the_giant_enabled
            and not self.options.map_kino_enabled and not self.options.map_moon_enabled
            and not self.options.map_origins_enabled and not self.options.map_nacht_enabled):
            self.options.map_shadows_enabled.value = True

        map_list = []
        if self.options.map_shadows_enabled:
            map_list.append(Maps.Shadows_Map_String)
        if self.options.map_castle_enabled:
            map_list.append(Maps.Castle_Map_String)
        if self.options.map_zetsubou_enabled:
            map_list.append(Maps.Zetsubou_Map_String)
        if self.options.map_gorod_enabled:
            map_list.append(Maps.GorodKrovi_Map_String)
        if self.options.map_revelations_enabled:
            map_list.append(Maps.Revelations_Map_String)
        if self.options.map_the_giant_enabled:
            map_list.append(Maps.The_Giant_Map_String)

        if self.options.map_nacht_enabled:
            map_list.append(Maps.Nacht_Map_String)
        if self.options.map_kino_enabled:
            map_list.append(Maps.Kino_Map_String)
        if self.options.map_moon_enabled:
            map_list.append(Maps.Moon_Map_String)
        if self.options.map_origins_enabled:
            map_list.append(Maps.Origins_Map_String)

        if self.options.map_workshop_wanted_enabled:
            map_list.append(Maps.Wanted_Map_String)

        # Add weapons to pool
        self.weapon_unlocks = []
        seen_weaps = set()
        # Wallbuys
        for map in map_list:
            Weapons.add_wallbuy_weapon_items(self.weapon_unlocks, seen_weaps, map)
        # Mystery Box
        if self.options.mystery_box_regular_items:
            for map in map_list:
                Weapons.add_mystery_box_weapon_items(self.weapon_unlocks, seen_weaps, map, self.options.mystery_box_expanded.value)

        # Add mystery box special weapons to pool
        self.mystery_box_special_items: list[str] = []
        if self.options.mystery_box_special_items:
            for map in map_list:
                if map in Weapons.map_weapon_data_sets:
                    for weapon_key, weapon_data in Weapons.map_weapon_data_sets[map].special.items():
                        self.mystery_box_special_items.append(Weapons.special_weapon_name(map, weapon_data.item_name))

        self.rolled_bows = []
        self.rolled_masks = []
        self.weapon_quest_items = []
        pass

    def create_regions(self):
        is_ut = getattr(self.multiworld, "generation_is_fake", False)

        # Create list of already unlocked maps
        locked_maps = []
        if self.options.map_shadows_enabled:
            locked_maps.append(ItemName.Map_Shadows)
        if self.options.map_castle_enabled:
            locked_maps.append(ItemName.Map_Castle)
        if self.options.map_zetsubou_enabled:
            locked_maps.append(ItemName.Map_Zetsubou)
        if self.options.map_gorod_enabled:
            locked_maps.append(ItemName.Map_GorodKrovi)
        if self.options.map_revelations_enabled:
            locked_maps.append(ItemName.Map_Revelations)
        if self.options.map_the_giant_enabled:
            locked_maps.append(ItemName.Map_The_Giant)

        if self.options.map_nacht_enabled:
            locked_maps.append(ItemName.Map_Nacht)
        if self.options.map_kino_enabled:
            locked_maps.append(ItemName.Map_Kino)
        if self.options.map_moon_enabled:
            locked_maps.append(ItemName.Map_Moon)
        if self.options.map_origins_enabled:
            locked_maps.append(ItemName.Map_Origins)

        if self.options.map_workshop_wanted_enabled:
            locked_maps.append(ItemName.Map_Wanted)

        self.num_maps = len(locked_maps)

        # Randomly picked selected starting maps
        starting_maps_unlocked = min(self.options.starting_maps_unlocked.value, len(locked_maps))
        if starting_maps_unlocked > 0:
            starting_maps = []
            left_to_pick = starting_maps_unlocked
            # Collect from starting inventory first
            for item in self.options.start_inventory:
                if item in locked_maps:
                    left_to_pick -= 1
                    starting_maps.append(item)
                    locked_maps.remove(item)
            # Fill rest of starting maps randomly
            if left_to_pick > 0:
                self.random.shuffle(locked_maps)
                starting_maps.extend(locked_maps[:left_to_pick])
                locked_maps = locked_maps[left_to_pick:]
            # Precollect starting maps
            for item in map(self.create_item, starting_maps):
                self.push_precollected(item)
        else:
            for item in map(self.create_item, locked_maps):
                self.push_precollected(item)
            locked_maps = []

        # Auto-hint map unlocks based on setting, letting players spend hints on things they really want, not what they desperately need
        if self.options.start_map_hints:
            for item in locked_maps:
                self.options.start_hints.value.add(item)
        self.cod_locked_maps = locked_maps

        universal_locations = [
            LocationName.RepairWindows_5
        ]
        menu_region = self.create_region(self.multiworld, self.player, 'Menu', universal_locations)
        add_ee_checks = self.options.goal_condition == 0 or self.options.easter_egg_checks_enabled
        
        # Default Balancing, Make sure you get to every region
        # TODO: Randomize this a bit/weight it
        
        if self.options.map_shadows_enabled:
            all_locations = [Locations.Shadows_Quest_MainQuest_Locations[0].name]
            if self.options.radio_ee_enabled:
                all_locations.extend([loc.name for loc in Locations.Shadows_Quest_Radio_Locations[0:1]])

            main_region = self.create_region(self.multiworld, self.player, RegionName.Shadows_Alleyway, all_locations)
            self.create_entrance(menu_region, main_region, Has(ItemName.Map_Shadows))

            self.add_stat_regions(main_region, Maps.Shadows_Map_String, self.options.round_location_max.value)

            open_locations = []
            open_locations.extend([loc.name for loc in Locations.Shadows_Craftable_Locations])
            open_locations.extend([loc.name for loc in Locations.Shadows_Quest_Locations])
            if self.options.shadows_tripmines_enabled or self.options.goal_condition == 1:
                open_locations.extend([loc.name for loc in Locations.Shadows_Doughnut_Locations])
            open_locations.extend([loc.name for loc in Locations.Shadows_Quest_MainQuest_Locations][1:])
            open_locations.append(LocationName.Shadows_Quest_ApothiconSword_EnterCode)
            open_locations.append(LocationName.Shadows_Craftable_ApothiconServant_MargwaHeart)
            if self.options.music_ee_enabled:
                open_locations.extend([loc.name for loc in Locations.Shadows_Quest_Music_Locations])
            if self.options.radio_ee_enabled:
                open_locations.extend([loc.name for loc in Locations.Shadows_Quest_Radio_Locations[2:]])
            map_open_region = self.create_region(self.multiworld, self.player, RegionName.Shadows_Open, open_locations)
            self.create_entrance(main_region, map_open_region, lambda state: rules.can_open_map(state, self.player, self.options, Maps.Shadows_Map_String))

            if self.options.shadows_margwa_head_enabled:
                margwa_head_region = self.create_region(self.multiworld, self.player, RegionName.Shadows_Margwa_Head, [
                    LocationName.Shadows_Quest_MargwaHead
                ])
                self.create_entrance(
                    map_open_region,
                    margwa_head_region,
                    lambda state: (
                        rules.check_round_logic(state, self.player, self.options, 16, Maps.Shadows_Map_String) and
                        rules.has_special_weapon(state, self.player, self.options, Maps.Shadows_Map_String, ItemName.Weapon_Raygun)
                    )
                )

            # Sword regions
            early_sword_region = self.create_region(self.multiworld, self.player, RegionName.Shadows_Sword_Early, [
                LocationName.Shadows_Quest_ApothiconSword_Egg1,
                LocationName.Shadows_Quest_ApothiconSword_CollectSword
            ])
            self.create_entrance(map_open_region, early_sword_region, lambda state: 
                (
                    rules.check_round_logic(state, self.player, self.options, 12, Maps.Shadows_Map_String) and
                    rules.has_weapon_of_strength(state, self.player, self.options, Maps.Shadows_Map_String, 3, 2)
                )
            )

            late_sword_region = self.create_region(self.multiworld, self.player, RegionName.Shadows_Sword_Late, [
                LocationName.Shadows_Quest_ApothiconSword_Egg2,
                LocationName.Shadows_Quest_ApothiconSword_CollectUpgradedSword
            ])
            self.create_entrance(early_sword_region, late_sword_region, lambda state: 
                (
                    rules.check_round_logic(state, self.player, self.options, 18, Maps.Shadows_Map_String) and
                    rules.has_weapon_of_strength(state, self.player, self.options, Maps.Shadows_Map_String, 3, 3)
                )
            )


            # Late found apothicon servant parts
            servant_region = self.create_region(self.multiworld, self.player, RegionName.Shadows_Servant, [
                LocationName.Shadows_Craftable_ApothiconServant_MargwaTentacle,
                LocationName.Shadows_Craftable_ApothiconServant_Xenomatter
            ])
            rule = lambda state: rules.check_round_logic(state, self.player, self.options, 12, Maps.Shadows_Map_String)
            self.create_entrance(map_open_region, servant_region, rule)

            # All of SoE true 'Main EE' locs are really late
            ee_locs = []
            if add_ee_checks:
                ee_locs = [loc.name for loc in Locations.Shadows_Quest_MainEE_Locations]

            main_ee_region = self.create_region(self.multiworld, self.player, RegionName.Shadows_MainEE, ee_locs)
            self.create_entrance(
                late_sword_region,
                main_ee_region,
                lambda state: (
                        rules.check_round_logic(state, self.player, self.options, 18, Maps.Shadows_Map_String) and
                        rules.has_weapon_of_strength(state, self.player, self.options, Maps.Shadows_Map_String, 3, 4) and
                        state.has_all([
                            ItemName.Shadows_Craftable_ApothiconServant_Heart,
                            ItemName.Shadows_Craftable_ApothiconServant_Skeleton,
                            ItemName.Shadows_Craftable_ApothiconServant_Xenomatter
                        ], self.player)
                )
            )

            upgraded_arnies_locs = [loc.name for loc in Locations.Shadows_LilArnies_Locations]
            upgraded_arnies_region = self.create_region(self.multiworld, self.player, RegionName.Shadows_Arnies, upgraded_arnies_locs)
            self.create_entrance(
                map_open_region, 
                upgraded_arnies_region, 
                lambda state:
                (
                    rules.has_special_weapon(state, self.player, self.options, Maps.Shadows_Map_String, ItemName.Weapon_LilArnies) and
                    rules.has_weapon_percentage(state, self.player, self.options, Maps.Shadows_Map_String, 2/3)
                )
            )

        if self.options.map_the_giant_enabled:
            all_locations = [Locations.TheGiant_Quest_Locations[0].name]
            if self.options.radio_ee_enabled:
                all_locations = [Locations.TheGiant_Quest_Radio_Locations[3]]

            main_region = self.create_region(self.multiworld, self.player, RegionName.TheGiant_Courtyard, all_locations)
            self.create_entrance(menu_region, main_region, Has(ItemName.Map_The_Giant))

            self.add_stat_regions(main_region, Maps.The_Giant_Map_String, self.options.round_location_max.value)

            open_locations = []
            open_locations.extend([loc.name for loc in Locations.TheGiant_Quest_Locations[1:]])
            if self.options.music_ee_enabled:
                open_locations.extend([loc.name for loc in Locations.TheGiant_Quest_Music_Locations])
            if self.options.radio_ee_enabled:
                open_locations.extend([loc.name for loc in (Locations.TheGiant_Quest_Radio_Locations[:3] + Locations.TheGiant_Quest_Radio_Locations[4:])])
            map_open_region = self.create_region(self.multiworld, self.player, RegionName.TheGiant_Open, open_locations)
            self.create_entrance(main_region, map_open_region, lambda state: rules.can_open_map(state, self.player, self.options, Maps.The_Giant_Map_String))

            pap_region = self.create_region(self.multiworld, self.player, RegionName.TheGiant_Pap, [loc.name for loc in Locations.TheGiant_Pap])
            self.create_entrance(map_open_region, pap_region, lambda state: state.has(ItemName.Progressive_PackAPunch, self.player))

            monkeybomb_region = self.create_region(self.multiworld, self.player, RegionName.TheGiant_MonkeyBombs, [loc.name for loc in Locations.TheGiant_MonkeyBomb])
            self.create_entrance(
                map_open_region,
                monkeybomb_region, 
                lambda state: rules.has_special_weapon(state, self.player, self.options, Maps.The_Giant_Map_String, ItemName.Weapon_MonkeyBombs))

        if self.options.map_castle_enabled:
            all_locations = []
            main_region = self.create_region(self.multiworld, self.player, RegionName.Castle_Gondola, all_locations)
            # self.create_entrance(menu_region, main_region, Has(ItemName.Map_Castle))
            self.create_entrance(menu_region, main_region, lambda state: state.has(ItemName.Map_Castle, self.player))

            self.add_stat_regions(main_region, Maps.Castle_Map_String, self.options.round_location_max.value)

            open_locations = []
            open_locations.extend([loc.name for loc in Locations.Castle_Craftable_Locations])
            open_locations.extend([loc.name for loc in Locations.Castle_Quest_Locations])
            if self.options.music_ee_enabled:
                open_locations.extend([loc.name for loc in Locations.Castle_Quest_Music_Locations])
            if self.options.radio_ee_enabled:
                open_locations.extend([loc.name for loc in Locations.Castle_Quest_Radio_Locations])
            map_open_region = self.create_region(self.multiworld, self.player, RegionName.Castle_Open, open_locations)
            self.create_entrance(main_region, map_open_region, lambda state: rules.can_open_map(state, self.player, self.options, Maps.Castle_Map_String))

            bow_pairs: list[tuple[list[LocationData], str]] = []
            if self.options.castle_bow_storm:
                bow_pairs.append((Locations.Castle_Quest_ElementalBow_Storm_Locations, ItemName.Castle_Victory_ElementalBow_Storm))
            if self.options.castle_bow_wolf:
                bow_pairs.append((Locations.Castle_Quest_ElementalBow_Wolf_Locations, ItemName.Castle_Victory_ElementalBow_Wolf))
            if self.options.castle_bow_fire:
                bow_pairs.append((Locations.Castle_Quest_ElementalBow_Fire_Locations, ItemName.Castle_Victory_ElementalBow_Fire))
            if self.options.castle_bow_void:
                bow_pairs.append((Locations.Castle_Quest_ElementalBow_Void_Locations, ItemName.Castle_Victory_ElementalBow_Void))

            easy_bow_locations = []
            hard_bow_locations = []
            bow_count = min(self.options.castle_bow_count.value, len(bow_pairs))
            # Make sure universal tracker sees all 4 location groups
            if not is_ut:
                bow_pairs = self.random.sample(bow_pairs, bow_count)
            for bow in bow_pairs:
                self.weapon_quest_items.append(bow[1])
                if bow[1] == ItemName.Castle_Victory_ElementalBow_Storm:
                    easy_bow_locations.extend([loc.name for loc in bow[0][:-1]])
                    hard_bow_locations.extend([loc.name for loc in bow[0][-1:]])
                    self.rolled_bows.append("storm")
                if bow[1] == ItemName.Castle_Victory_ElementalBow_Wolf:
                    easy_bow_locations.extend([loc.name for loc in bow[0][:-1]])
                    hard_bow_locations.extend([loc.name for loc in bow[0][-1:]])
                    self.rolled_bows.append("wolf")
                if bow[1] == ItemName.Castle_Victory_ElementalBow_Fire:
                    easy_bow_locations.extend([loc.name for loc in bow[0][:2]])
                    hard_bow_locations.extend([loc.name for loc in bow[0][2:]])
                    self.rolled_bows.append("fire")
                if bow[1] == ItemName.Castle_Victory_ElementalBow_Void:
                    easy_bow_locations.extend([loc.name for loc in bow[0][:3]])
                    hard_bow_locations.extend([loc.name for loc in bow[0][3:]])
                    self.rolled_bows.append("void")

            easy_bow_region = self.create_region(self.multiworld, self.player, RegionName.Castle_Bow_Easy, easy_bow_locations)
            self.create_entrance(
                map_open_region,
                easy_bow_region,
                lambda state: (
                    rules.check_round_logic(state, self.player, self.options, 8, Maps.Castle_Map_String)
                )
            )
            
            hard_bow_region = self.create_region(self.multiworld, self.player, RegionName.Castle_Bow_Hard, hard_bow_locations)
            self.create_entrance(
                easy_bow_region,
                hard_bow_region,
                lambda state: (
                    rules.check_round_logic(state, self.player, self.options, 12, Maps.Castle_Map_String) and
                    rules.has_weapon_of_strength(state, self.player, self.options, Maps.Castle_Map_String, 3, 2)
                )
            )

            dg4_locations = []
            dg4_locations.extend([loc.name for loc in Locations.Castle_DG4_Locations])
            dg4_region = self.create_region(self.multiworld, self.player, RegionName.Castle_DG4, dg4_locations)
            rule = lambda state: rules.check_round_logic(state, self.player, self.options, 12, Maps.Castle_Map_String)
            self.create_entrance(map_open_region, dg4_region, rule)

            ee_locs = []
            mid_ee_locs = []
            if add_ee_checks:
                ee_locs = [loc.name for loc in Locations.Castle_Quest_MainEE_Locations[:2]]
                mid_ee_locs = [loc.name for loc in Locations.Castle_Quest_MainEE_Locations[2:4]]

            main_ee_region = self.create_region(self.multiworld, self.player, RegionName.Castle_MainEE, ee_locs)
            self.create_entrance(
                map_open_region,
                main_ee_region, 
                lambda state: (
                    rules.check_round_logic(state, self.player, self.options, 12, Maps.Castle_Map_String)
                )
            )

            main_ee_midgame_region = self.create_region(self.multiworld, self.player, RegionName.Castle_MainEE + " Midgame", mid_ee_locs)
            self.create_entrance(
                main_ee_region,
                main_ee_midgame_region,
                lambda state: (
                    rules.check_round_logic(state, self.player, self.options, 14, Maps.Castle_Map_String) and
                    rules.has_shield(state, self.player, Maps.Castle_Map_String) and
                    state.has(ItemName.Progressive_PackAPunch, self.player) and
                    rules.has_weapon_of_strength(state, self.player, self.options, Maps.Castle_Map_String, 3, 4)
                )
            )

            # Weapon Quest - Add available bows
            if self.options.goal_condition == 1:
                for bow in bow_pairs:
                    self.multiworld.get_location(bow[0][-1].name, self.player).place_locked_item(self.create_item(bow[1]))
            
            boss_fight_locations = []
            if add_ee_checks:
                boss_fight_locations = [loc.name for loc in Locations.Castle_Quest_MainEE_Locations[4:]]
            boss_region = self.create_region(self.multiworld, self.player, RegionName.Castle_BossFight, boss_fight_locations)
            self.create_entrance(
                main_ee_midgame_region,
                boss_region,
                lambda state:
                (
                    rules.check_round_logic(state, self.player, self.options, 16, Maps.Castle_Map_String) and
                    rules.has_special_weapon(state, self.player, self.options, Maps.Castle_Map_String, ItemName.Weapon_MonkeyBombs) and
                    state.has_all([
                        ItemName.Castle_Craftable_GravitySpikes_Body,
                        ItemName.Castle_Craftable_GravitySpikes_Guards,
                        ItemName.Castle_Craftable_GravitySpikes_Handle
                    ], self.player) and
                    rules.has_weapon_of_strength(state, self.player, self.options, Maps.Castle_Map_String, 3, 5)
                )
            )

        if self.options.map_zetsubou_enabled:
            all_locations = [Locations.Zetsubou_Quest_MainQuest_Locations[0].name]

            main_region = self.create_region(self.multiworld, self.player, RegionName.Zetsubou_Beach, all_locations)
            self.create_entrance(menu_region, main_region, Has(ItemName.Map_Zetsubou))

            self.add_stat_regions(main_region, Maps.Zetsubou_Map_String, self.options.round_location_max.value)

            open_locations = []
            open_locations.extend([loc.name for loc in Locations.Zetsubou_Quest_MainQuest_Locations[1:]])
            open_locations.extend([loc.name for loc in Locations.Zetsubou_Craftable_Locations])
            open_locations.extend([loc.name for loc in Locations.Zetsubou_Quest_KT4_Locations])
            open_locations.extend([loc.name for loc in Locations.Zetsubou_Quest_Skull_Locations])
            if self.options.music_ee_enabled:
                open_locations.extend([loc.name for loc in Locations.Zetsubou_Quest_Music_Locations])
            if self.options.radio_ee_enabled:
                open_locations.extend([loc.name for loc in Locations.Zetsubou_Quest_Radio_Locations])
            map_open_region = self.create_region(self.multiworld, self.player, RegionName.Zetsubou_Open, open_locations)
            self.create_entrance(main_region, map_open_region, lambda state: rules.can_open_map(state, self.player, self.options, Maps.Zetsubou_Map_String,))

            early_challenge_region = self.create_region(self.multiworld, self.player, RegionName.Zetsubou_Challenges_Early, [LocationName.Zetsubou_Quest_Challenge_1, LocationName.Zetsubou_Quest_Challenge_2])
            self.create_entrance(
                map_open_region,
                early_challenge_region,
                lambda state:
                (
                    rules.check_round_logic(state, self.player, self.options, 10, Maps.Zetsubou_Map_String)
                )
            )

            late_challenge_region = self.create_region(self.multiworld, self.player, RegionName.Zetsubou_Challenges_Late, [LocationName.Zetsubou_Quest_Challenge_3, LocationName.Zetsubou_Quest_Challenge_All])
            self.create_entrance(
                early_challenge_region,
                late_challenge_region,
                lambda state:
                (
                    rules.check_round_logic(state, self.player, self.options, 14, Maps.Zetsubou_Map_String) and
                    rules.has_weapon_of_strength(state, self.player, self.options, Maps.Zetsubou_Map_String, 3, 2)
                )
            )

            masamune_locs = [loc.name for loc in Locations.Zetsubou_Quest_Masamune_Locations]
            masamune_region = self.create_region(self.multiworld, self.player, RegionName.Zetsubou_Masamune, masamune_locs)
            self.create_entrance(
                late_challenge_region,
                masamune_region,
                lambda state: (
                    rules.check_round_logic(state, self.player, self.options, 16, Maps.Zetsubou_Map_String) and
                    rules.has_shield(state, self.player, Maps.Zetsubou_Map_String) and
                    rules.has_weapon_of_strength(state, self.player, self.options, Maps.Zetsubou_Map_String, 3, 3)
                )
            )

            ee_locs = []
            if add_ee_checks:
                ee_locs = [loc.name for loc in Locations.Zetsubou_Quest_MainEE_Locations]

            main_ee_region = self.create_region(self.multiworld, self.player, RegionName.Zetsubou_MainEE, ee_locs)
            self.create_entrance(
                masamune_region,
                main_ee_region, 
                lambda state: (
                    rules.check_round_logic(state, self.player, self.options, 18, Maps.Zetsubou_Map_String) and
                    rules.has_special_weapon(state, self.player, self.options, Maps.Zetsubou_Map_String, ItemName.Weapon_MonkeyBombs) and
                    rules.has_weapon_of_strength(state, self.player, self.options, Maps.Zetsubou_Map_String, 3, 4)
                    and state.has_all([
                        ItemName.Zetsubou_Craftable_Gasmask_Filter,
                        ItemName.Zetsubou_Craftable_Gasmask_Strap,
                        ItemName.Zetsubou_Craftable_Gasmask_Visor
                    ], self.player)
                )
            )



        if self.options.map_gorod_enabled:
            all_locations = []
            main_region = self.create_region(self.multiworld, self.player, RegionName.Gorod_Trenches, all_locations)
            self.create_entrance(menu_region, main_region, Has(ItemName.Map_GorodKrovi))

            self.add_stat_regions(main_region, Maps.GorodKrovi_Map_String, self.options.round_location_max.value)

            open_locations = []
            open_locations.extend([loc.name for loc in Locations.GorodKrovi_Quest_MainQuest_Locations])
            open_locations.extend([loc.name for loc in Locations.GorodKrovi_Craftable_Locations])
            if self.options.music_ee_enabled:
                open_locations.extend([loc.name for loc in Locations.GorodKrovi_Quest_Music_Locations])
            if self.options.radio_ee_enabled:
                open_locations.extend([loc.name for loc in Locations.GorodKrovi_Quest_Radio_Locations])
            map_open_region = self.create_region(self.multiworld, self.player, RegionName.Gorod_Open, open_locations)
            self.create_entrance(main_region, map_open_region,
                            lambda state: rules.can_open_map(state, self.player, self.options, Maps.GorodKrovi_Map_String))
            
            if self.options.gorod_challenges_enabled:
                early_challenge_region = self.create_region(self.multiworld, self.player, RegionName.Gorod_Challenges_Early, [LocationName.GorodKrovi_Quest_Challenges_1, LocationName.GorodKrovi_Quest_Challenges_2])
                self.create_entrance(
                    map_open_region,
                    early_challenge_region,
                    lambda state:
                    (
                        # Various shield challenges
                        rules.has_shield(state, self.player, Maps.GorodKrovi_Map_String) and
                        rules.check_round_logic(state, self.player, self.options, 12, Maps.GorodKrovi_Map_String) and
                        rules.has_weapon_of_strength(state, self.player, self.options, Maps.GorodKrovi_Map_String, 3, 2)
                    )
                )

                late_challenge_region = self.create_region(self.multiworld, self.player, RegionName.Gorod_Challenges_Late, [LocationName.GorodKrovi_Quest_Challenges_3])
                self.create_entrance(
                    early_challenge_region,
                    late_challenge_region,
                    lambda state:
                    (
                        rules.check_round_logic(state, self.player, self.options, 16, Maps.GorodKrovi_Map_String) and
                        # Upgrade monkey bombs
                        rules.has_special_weapon(state, self.player, self.options, Maps.GorodKrovi_Map_String, ItemName.Weapon_MonkeyBombs) and
                        rules.has_weapon_of_strength(state, self.player, self.options, Maps.GorodKrovi_Map_String, 3, 3)
                    )
                )

            if self.options.gorod_monkeybombs_upgrade_enabled or self.options.goal_condition == 1:
                monkey_region = self.create_region(self.multiworld, self.player, RegionName.Gorod_MonkeyBombs, [LocationName.GorodKrovi_Quest_UpgradeMonkeyBombs])
                self.create_entrance(
                    map_open_region,
                    monkey_region,
                    lambda state:
                    (
                        rules.check_round_logic(state, self.player, self.options, 16, Maps.GorodKrovi_Map_String) and
                        # Upgrade monkey bombs
                        rules.has_special_weapon(state, self.player, self.options, Maps.GorodKrovi_Map_String, ItemName.Weapon_MonkeyBombs) and
                        rules.has_weapon_of_strength(state, self.player, self.options, Maps.GorodKrovi_Map_String, 3, 3)
                    )
                )

            if self.options.gorod_helmets_enabled:
                valkyrie_locs = [LocationName.GorodKrovi_Quest_SideEE_ValkyrieHelm]
                valkyrie_region = self.create_region(self.multiworld, self.player, RegionName.Gorod_Valkyrie, valkyrie_locs)
                self.create_entrance(
                    map_open_region,
                    valkyrie_region,
                    lambda state:
                    (
                        rules.check_round_logic(state, self.player, self.options, 14, Maps.GorodKrovi_Map_String) and
                        rules.has_weapon_of_strength(state, self.player, self.options, Maps.GorodKrovi_Map_String, 3, 2)
                    )
                )

            early_dragon_locs = [loc.name for loc in Locations.GorodKrovi_Quest_DragonGauntlets_Early]
            early_dragon_region = self.create_region(self.multiworld, self.player, RegionName.Gorod_EarlyDragon, early_dragon_locs)
            self.create_entrance(
                map_open_region,
                early_dragon_region,
                lambda state:
                (
                    rules.check_round_logic(state, self.player, self.options, 10, Maps.GorodKrovi_Map_String) and
                    rules.has_weapon_of_strength(state, self.player, self.options, Maps.GorodKrovi_Map_String, 3, 2)
                )
            )

            bunker_locs = [loc.name for loc in Locations.GorodKrovi_Quest_DragonStrikes]
            if self.options.gorod_helmets_enabled:
                bunker_locs.append(LocationName.GorodKrovi_Quest_SideEE_ManglerHelm)
            bunker_region = self.create_region(self.multiworld, self.player, RegionName.Gorod_Bunker, bunker_locs)
            self.create_entrance(
                map_open_region,
                bunker_region,
                lambda state:
                (
                    rules.has_special_weapon(state, self.player, self.options, Maps.GorodKrovi_Map_String, ItemName.Weapon_RaygunMk3) or
                    (
                        rules.has_special_weapon(state, self.player, self.options, Maps.GorodKrovi_Map_String, ItemName.Weapon_Raygun) and
                        rules.has_perk(state, self.player, self.options, Maps.GorodKrovi_Map_String, ItemName.Machine_PhdFlopper)
                    ) or
                    rules.has_weapon_of_strength(state, self.player, self.options, Maps.GorodKrovi_Map_String, 4, 1)
                )
            )
            
            wing_locs = []
            # Exclude wing loc if already given wings
            if not self.options.difficulty_gorod_dragon_wings:
                wing_locs.append(LocationName.GorodKrovi_Quest_SideEE_DragonWings)
            wing_region = self.create_region(self.multiworld, self.player, RegionName.Gorod_Wings, wing_locs)
            self.create_entrance(
                bunker_region,
                wing_region,
                lambda state:
                (
                    rules.check_round_logic(state, self.player, self.options, 14, Maps.GorodKrovi_Map_String) and
                    rules.has_shield(state, self.player, Maps.GorodKrovi_Map_String)
                )
            )

            ee_locs = []
            if add_ee_checks:
                ee_locs = [loc.name for loc in Locations.GorodKrovi_Quest_MainEE_Locations]
            # Toss in most late requirements because they fit the same rules anyway
            ee_locs.extend([loc.name for loc in Locations.GorodKrovi_Quest_DragonGauntlets_Late])
            ee_locs.extend([loc.name for loc in Locations.GorodKrovi_Quest_DragonStrikes_Upgraded])

            main_ee_region = self.create_region(self.multiworld, self.player, RegionName.Gorod_MainEE, ee_locs)
            self.create_entrance(
                bunker_region, 
                main_ee_region, 
                lambda state: (
                    rules.check_round_logic(state, self.player, self.options, 18, Maps.GorodKrovi_Map_String) and
                    rules.has_shield(state, self.player, Maps.GorodKrovi_Map_String) and
                    rules.has_sniper(state, self.player, self.options, Maps.GorodKrovi_Map_String) and
                    rules.has_weapon_of_strength(state, self.player, self.options, Maps.GorodKrovi_Map_String, 3, 4) and
                    rules.has_special_weapon(state, self.player, self.options, Maps.GorodKrovi_Map_String, ItemName.Weapon_RaygunMk3)
                )
            )

            # Shield upgrade
            shield_locations = [loc.name for loc in Locations.GorodKrovi_Quest_TiamatsMaw]
            shield_region = self.create_region(self.multiworld, self.player, RegionName.Gorod_Shield, shield_locations)
            self.create_entrance(bunker_region, shield_region, HasAll(*(item.name for item in Items.GorodKrovi_Shield)))

        if self.options.map_revelations_enabled:
            all_locations = [Locations.Revelations_Quest_MainQuest_Locations[0].name]
 
            main_region = self.create_region(self.multiworld, self.player, RegionName.Revelations_House, all_locations)
            self.create_entrance(menu_region, main_region, Has(ItemName.Map_Revelations))

            self.add_stat_regions(main_region, Maps.Revelations_Map_String, self.options.round_location_max.value)

            open_locations = []
            open_locations.extend([loc.name for loc in Locations.Revelations_Quest_MainQuest_Locations[1:]])
            open_locations.extend([loc.name for loc in Locations.Revelations_Craftable_Locations])
            open_locations.extend([loc.name for loc in Locations.Revelations_Quest_SideEE_Locations])
            if self.options.music_ee_enabled:
                open_locations.extend([loc.name for loc in Locations.Revelations_Quest_Music_Locations])
            if self.options.radio_ee_enabled:
                open_locations.extend([loc.name for loc in Locations.Revelations_Quest_Radio_Locations])

            map_open_region = self.create_region(self.multiworld, self.player, RegionName.Revelations_Open, open_locations)
            self.create_entrance(main_region, map_open_region,
                            lambda state: rules.can_open_map(state, self.player, self.options, Maps.Revelations_Map_String))

            # Add wisp location groups to rando
            if self.options.revelations_wisp_enabled:
                #special round 1
                wisps_early = [loc.name for loc in Locations.Revelations_Quest_Wisp_Locations[0:4]]
                wisps_early.append(Locations.Revelations_Quest_Wisp_Locations[20].name)
                #boss round 1
                wisps_mid = [loc.name for loc in Locations.Revelations_Quest_Wisp_Locations[12:16]]
                wisps_mid.extend([loc.name for loc in Locations.Revelations_Quest_Wisp_Locations[21:]])
                #special round 2 + boss round 2
                wisps_mid2 = [loc.name for loc in Locations.Revelations_Quest_Wisp_Locations[4:8]]
                wisps_mid2.extend([loc.name for loc in Locations.Revelations_Quest_Wisp_Locations[8:12]])
                #special round 3
                wisps_late = [loc.name for loc in Locations.Revelations_Quest_Wisp_Locations[16:20]]

                early_wisp_region = self.create_region(self.multiworld, self.player, RegionName.Revelations_Wisps_Early, wisps_early)
                self.create_entrance(
                    map_open_region,
                    early_wisp_region,
                    lambda state: rules.check_round_logic(state, self.player, self.options, 10, Maps.Revelations_Map_String)
                )
                mid_wisp_region = self.create_region(self.multiworld, self.player, RegionName.Revelations_Wisps_Mid, wisps_mid)
                self.create_entrance(
                    map_open_region,
                    mid_wisp_region,
                    lambda state: rules.check_round_logic(state, self.player, self.options, 16, Maps.Revelations_Map_String)
                )
                mid2_wisp_region = self.create_region(self.multiworld, self.player, RegionName.Revelations_Wisps_Mid2, wisps_mid2)
                self.create_entrance(
                    map_open_region,
                    mid2_wisp_region,
                    lambda state: rules.check_round_logic(state, self.player, self.options, 24, Maps.Revelations_Map_String)
                )
                late_wisp_region = self.create_region(self.multiworld, self.player, RegionName.Revelations_Wisps_Late, wisps_late)
                self.create_entrance(
                    map_open_region,
                    late_wisp_region,
                    lambda state: rules.check_round_logic(state, self.player, self.options, 30, Maps.Revelations_Map_String)
                )
            
                
            # Add mask location groups to rando
            mask_locs: list[tuple[list[LocationData], str, int]] = []
            if self.options.revelations_mask_enabled_dire_wolf:
                mask_locs.append((Locations.Revelations_Quest_Mask_Wolf_Locations, "wolf", 0))
            if self.options.revelations_mask_enabled_siegfried:
                mask_locs.append((Locations.Revelations_Quest_Mask_Siegfried_Locations, "siegfried", 0))
            if self.options.revelations_mask_enabled_king:
                mask_locs.append((Locations.Revelations_Quest_Mask_King_Locations, "king", 1))
            if self.options.revelations_mask_enabled_fury:
                mask_locs.append((Locations.Revelations_Quest_Mask_Fury_Locations, "fury", 2))
            if self.options.revelations_mask_enabled_keeper_skull:
                mask_locs.append((Locations.Revelations_Quest_Mask_Keeper_Locations, "keeper", 1))
            if self.options.revelations_mask_enabled_margwa:
                mask_locs.append((Locations.Revelations_Quest_Mask_Margwa_Locations, "margwa", 1))
            if self.options.revelations_mask_enabled_apothicon:
                mask_locs.append((Locations.Revelations_Quest_Mask_Apothigod_Locations, "apothigod", 2))

            # Sort masks by difficulty
            self.random.shuffle(mask_locs)
            max_mask_locs = min(self.options.revelations_mask_count.value, len(mask_locs))
            mask_loc_groups: list[list[str]] = [[], [], []]
            if max_mask_locs > 0:
                if is_ut:
                    max_mask_locs = len(mask_locs)
                for locations, mask_name, difficulty in mask_locs[:max_mask_locs]:
                    mask_loc_groups[difficulty].extend([loc.name for loc in locations])
                    self.rolled_masks.append(mask_name)

            easy_mask_region = self.create_region(self.multiworld, self.player, RegionName.Revelations_Masks_Easy, mask_loc_groups[0])
            self.create_entrance(
                map_open_region,
                easy_mask_region,
                lambda state: rules.check_round_logic(state, self.player, self.options, 10, Maps.Revelations_Map_String)
            )
            medium_mask_region = self.create_region(self.multiworld, self.player, RegionName.Revelations_Masks_Medium, mask_loc_groups[1])
            self.create_entrance(
                map_open_region,
                medium_mask_region,
                lambda state: (
                    rules.check_round_logic(state, self.player, self.options, 20, Maps.Revelations_Map_String) and
                    # Margwa mask requires a sniper
                    rules.has_sniper(state, self.player, self.options, Maps.Revelations_Map_String) and
                    rules.has_weapon_of_strength(state, self.player, self.options, Maps.Revelations_Map_String, 3, 2)
                )
            )
            hard_mask_region = self.create_region(self.multiworld, self.player, RegionName.Revelations_Masks_Hard, mask_loc_groups[2])
            self.create_entrance(
                map_open_region,
                hard_mask_region,
                lambda state: 
                (
                    rules.check_round_logic(state, self.player, self.options, 28, Maps.Revelations_Map_String) and
                    rules.has_shield(state, self.player, Maps.Revelations_Map_String) and
                    rules.has_weapon_of_strength(state, self.player, self.options, Maps.Revelations_Map_String, 3, 5) and
                    rules.has_weapon_of_strength(state, self.player, self.options, Maps.Revelations_Map_String, 5, 2)
                )
            )

            if self.options.revelations_challenges_enabled:
                early_challenge_locations = [LocationName.Revelations_Quest_Challenges_1]
                early_challenge_region = self.create_region(self.multiworld, self.player, RegionName.Revelations_Challenges_Early, early_challenge_locations)
                rule = lambda state: (
                    rules.check_round_logic(state, self.player, self.options, 10, Maps.Revelations_Map_String) and
                    rules.has_shield(state, self.player, Maps.Revelations_Map_String) and
                    rules.has_weapon_of_strength(state, self.player, self.options, Maps.Revelations_Map_String, 3, 2)
                )
                self.create_entrance(map_open_region, early_challenge_region, rule)

                # Round 20 logic for the panzer/margwa challenges and shield for the possible shield challenge
                late_challenge_locations = [LocationName.Revelations_Quest_Challenges_2, LocationName.Revelations_Quest_Challenges_3, LocationName.Revelations_Quest_Challenges_All]
                late_challenge_region = self.create_region(self.multiworld, self.player, RegionName.Revelations_Challenges_Late, late_challenge_locations)
                rule = lambda state: (
                    rules.check_round_logic(state, self.player, self.options, 20, Maps.Revelations_Map_String) and
                    rules.has_shield(state, self.player, Maps.Revelations_Map_String) and
                    rules.has_weapon_of_strength(state, self.player, self.options, Maps.Revelations_Map_String, 3, 4)
                )
                self.create_entrance(early_challenge_region, late_challenge_region, rule)

            ee_locs = []
            mid_ee_locs = []
            late_ee_locs = []
            if add_ee_checks:
                ee_locs = [loc.name for loc in Locations.Revelations_Quest_MainEE_Locations[:2]]
                mid_ee_locs = [loc.name for loc in Locations.Revelations_Quest_MainEE_Locations[2:5]]
                late_ee_locs = [loc.name for loc in Locations.Revelations_Quest_MainEE_Locations[5:]]

            main_ee_region = self.create_region(self.multiworld, self.player, RegionName.Revelations_MainEE, ee_locs)
            self.create_entrance(
                map_open_region,
                main_ee_region, 
                lambda state: (
                    rules.check_round_logic(state, self.player, self.options, 10, Maps.Revelations_Map_String)
                )
            )

            main_ee_midgame_region = self.create_region(self.multiworld, self.player, RegionName.Revelations_MainEE + " Midgame", mid_ee_locs)
            self.create_entrance(
                main_ee_region,
                main_ee_midgame_region,
                lambda state: (
                    rules.has_special_weapon(state, self.player, self.options, Maps.Revelations_Map_String, ItemName.Weapon_ApothiconServant) and
                    rules.has_special_weapon(state, self.player, self.options, Maps.Revelations_Map_String, ItemName.Weapon_LilArnies) and
                    state.has(ItemName.Progressive_PackAPunch, self.player) and
                    rules.has_shield(state, self.player, Maps.Revelations_Map_String) and
                    rules.check_round_logic(state, self.player, self.options, 15, Maps.Revelations_Map_String) and
                    rules.has_weapon_of_strength(state, self.player, self.options, Maps.Revelations_Map_String, 3, 3)
                )
            )

            main_ee_lategame_region = self.create_region(self.multiworld, self.player, RegionName.Revelations_MainEE + " Lategame", late_ee_locs)
            self.create_entrance(
                main_ee_midgame_region,
                main_ee_lategame_region,
                lambda state: (
                    rules.has_special_weapon(state, self.player, self.options, Maps.Revelations_Map_String, ItemName.Weapon_Ragnaroks) and
                    rules.has_special_weapon(state, self.player, self.options, Maps.Revelations_Map_String, ItemName.Weapon_Ragnaroks) and
                    rules.check_round_logic(state, self.player, self.options, 20, Maps.Revelations_Map_String) and
                    rules.has_weapon_of_strength(state, self.player, self.options, Maps.Revelations_Map_String, 3, 6)
                )
            )

            apothicon_ugprade_region = self.create_region(self.multiworld, self.player, RegionName.Revelations_Apothicon_Upgrade, [Locations.Revelations_Quest_Weapons[0].name])
            self.create_entrance(
                map_open_region, 
                apothicon_ugprade_region,
                lambda state: rules.has_special_weapon(state, self.player, self.options, Maps.Revelations_Map_String, ItemName.Weapon_ApothiconServant)
)

            arnies_ugprade_region = self.create_region(self.multiworld, self.player, RegionName.Revelations_Arnies_Upgrade, [Locations.Revelations_Quest_Weapons[1].name])
            self.create_entrance(
                map_open_region, 
                arnies_ugprade_region, 
                lambda state: rules.has_special_weapon(state, self.player, self.options, Maps.Revelations_Map_String, ItemName.Weapon_LilArnies))

        if self.options.map_nacht_enabled:
            all_locations = []
            main_region = self.create_region(self.multiworld, self.player, RegionName.Nacht_Entrance, all_locations)
            self.create_entrance(menu_region, main_region, Has(ItemName.Map_Nacht))

            self.add_stat_regions(main_region, Maps.Nacht_Map_String, self.options.round_location_max.value)

            open_locations = []
            open_locations.extend([loc.name for loc in Locations.Nacht_Quest_Locations])
            if self.options.music_ee_enabled:
                open_locations.extend([loc.name for loc in Locations.Nacht_Quest_Music_Locations])
            if self.options.radio_ee_enabled:
                open_locations.extend([loc.name for loc in Locations.Nacht_Quest_Radio_Locations])

            map_open_region = self.create_region(self.multiworld, self.player, RegionName.Nacht_Open, open_locations)
            self.create_entrance(main_region, map_open_region,
                            lambda state: rules.can_open_map(state, self.player, self.options, Maps.Nacht_Map_String))

        if self.options.map_kino_enabled:
            all_locations = []
            main_region = self.create_region(self.multiworld, self.player, RegionName.Kino_Entrance, all_locations)
            self.create_entrance(menu_region, main_region, Has(ItemName.Map_Kino))

            self.add_stat_regions(main_region, Maps.Kino_Map_String, self.options.round_location_max.value)

            open_locations = []
            open_locations.extend([loc.name for loc in Locations.Kino_Quest_Locations])
            if self.options.music_ee_enabled:
                open_locations.extend([loc.name for loc in Locations.Kino_Quest_Music_Locations])
            if self.options.radio_ee_enabled:
                open_locations.extend([loc.name for loc in Locations.Kino_Quest_Radio_Locations])

            map_open_region = self.create_region(self.multiworld, self.player, RegionName.Kino_Open, open_locations)
            self.create_entrance(main_region, map_open_region,
                            lambda state: rules.can_open_map(state, self.player, self.options, Maps.Kino_Map_String))
                
        if self.options.map_moon_enabled:
            all_locations = []
            if self.options.radio_ee_enabled:
                all_locations.extend([Locations.Moon_Quest_Radio_Locations[0].name, Locations.Moon_Quest_Radio_Locations[5].name])

            main_region = self.create_region(self.multiworld, self.player, RegionName.Moon_Entrance, all_locations)
            self.create_entrance(menu_region, main_region, Has(ItemName.Map_Moon))

            self.add_stat_regions(main_region, Maps.Moon_Map_String, self.options.round_location_max.value)

            open_locations = []
            open_locations.extend([loc.name for loc in Locations.Moon_Universal_Locations])
            open_locations.extend([loc.name for loc in Locations.Moon_Hacker_Locations])
            if self.options.music_ee_enabled:
                open_locations.extend([loc.name for loc in Locations.Moon_Quest_Music_Locations])
            if self.options.radio_ee_enabled:
                open_locations.extend([loc.name for loc in Locations.Moon_Quest_Radio_Locations[1:5]])
            if self.options.moon_audio_reel_enabled:
                open_locations.extend([loc.name for loc in Locations.Moon_Quest_Reel_Locations])
            
            map_open_region = self.create_region(self.multiworld, self.player, RegionName.Moon_Open, open_locations)
            self.create_entrance(main_region, map_open_region,
                            lambda state: rules.can_open_map(state, self.player, self.options, Maps.Moon_Map_String))
            
            space_dog_locs = [loc.name for loc in Locations.Moon_Quest_SpaceDog_Locations]
            space_dog_region = self.create_region(self.multiworld, self.player, RegionName.Moon_SpaceDog, space_dog_locs)
            self.create_entrance(
                map_open_region,
                space_dog_region,
                lambda state: (
                    rules.check_round_logic(state, self.player, self.options, 12, Maps.Moon_Map_String) and
                    rules.has_special_weapon(state, self.player, self.options, Maps.Moon_Map_String, ItemName.Weapon_WaveGun) and
                    rules.has_weapon_of_strength(state, self.player, self.options, Maps.Moon_Map_String, 3, 3)
                )
            )

            ee_locs = []
            mid_ee_locs = []
            ee_computer_locs = []
            late_ee_locs = []
            if add_ee_checks:
                ee_locs = [loc.name for loc in Locations.Moon_Quest_MainEE_Part1_Locations]
                mid_ee_locs = [loc.name for loc in Locations.Moon_Quest_MainEE_Part2_Locations]
                mid_ee_locs = [loc.name for loc in Locations.Moon_Quest_MainEE_Computer_Locations]
                late_ee_locs = [loc.name for loc in Locations.Moon_Quest_MainEE_Part3_Locations]

            main_ee_region = self.create_region(self.multiworld, self.player, RegionName.Moon_MainEE, ee_locs)
            self.create_entrance(
                map_open_region,
                main_ee_region, 
                lambda state: (
                    rules.check_round_logic(state, self.player, self.options, 10, Maps.Moon_Map_String)
                )
            )

            main_ee_midgame_region = self.create_region(self.multiworld, self.player, RegionName.Moon_MainEE + " Midgame", mid_ee_locs)
            self.create_entrance(
                main_ee_region,
                main_ee_midgame_region,
                lambda state: (
                    rules.has_special_weapon(state, self.player, self.options, Maps.Moon_Map_String, ItemName.Weapon_WaveGun) and
                    state.has(ItemName.Progressive_PackAPunch, self.player) and
                    rules.check_round_logic(state, self.player, self.options, 14, Maps.Moon_Map_String) and
                    rules.has_weapon_of_strength(state, self.player, self.options, Maps.Moon_Map_String, 3, 3)
                )
            )

            main_ee_computer_region = self.create_region(self.multiworld, self.player, RegionName.Moon_MainEE + " Computer", ee_computer_locs)
            self.create_entrance(
                map_open_region,
                main_ee_computer_region,
                lambda state: (
                    rules.has_special_weapon(state, self.player, self.options, Maps.Moon_Map_String, ItemName.Weapon_GershDevice) and
                    rules.has_special_weapon(state, self.player, self.options, Maps.Moon_Map_String, ItemName.Weapon_QEDs)
                )
            )

            main_ee_lategame_region = self.create_region(self.multiworld, self.player, RegionName.Moon_MainEE + " Lategame", late_ee_locs)
            self.create_entrance(
                main_ee_midgame_region,
                main_ee_lategame_region,
                lambda state: (
                    rules.has_special_weapon(state, self.player, self.options, Maps.Moon_Map_String, ItemName.Weapon_GershDevice) and
                    rules.has_special_weapon(state, self.player, self.options, Maps.Moon_Map_String, ItemName.Weapon_QEDs) and
                    rules.check_round_logic(state, self.player, self.options, 20, Maps.Moon_Map_String) and
                    rules.has_weapon_of_strength(state, self.player, self.options, Maps.Moon_Map_String, 3, 5)
                )
            )

        if self.options.map_origins_enabled:
            all_locations = [LocationName.Origins_Generators_Any]
            all_locations += [loc.name for loc in Locations.Origins_Craftable_Locations_Early]
            if self.options.radio_ee_enabled:
                all_locations.extend([loc.name for loc in (Locations.Origins_Radio_Locations[0:2] + [Locations.Origins_Radio_Locations[6]])])
            main_region = self.create_region(self.multiworld, self.player, RegionName.Origins_Entrance, all_locations)
            self.create_entrance(menu_region, main_region, Has(ItemName.Map_Origins))

            self.add_stat_regions(main_region, Maps.Origins_Map_String, self.options.round_location_max.value)

            open_locations = [LocationName.Origins_Generators_Three, LocationName.Origins_Generators_All]
            open_locations += [loc.name for loc in Locations.Origins_Craftable_Locations]
            if self.options.music_ee_enabled:
                open_locations.extend([LocationName.Origins_Quest_Music_Archangel, LocationName.Origins_Quest_Music_Aether])
            if self.options.radio_ee_enabled:
                open_locations.extend([loc.name for loc in Locations.Origins_Radio_Locations[2:6]])

            map_open_region = self.create_region(self.multiworld, self.player, RegionName.Origins_Open, open_locations)
            self.create_entrance(main_region, map_open_region,
                            lambda state: rules.can_open_map(state, self.player, self.options, Maps.Origins_Map_String))
            
            if self.options.music_ee_enabled:
                crazy_place_locations = [LocationName.Origins_Quest_Music_ShepherdOfFire]
                crazy_place_region = self.create_region(self.multiworld, self.player, RegionName.Origins_Crazy_Place, crazy_place_locations)
                self.create_entrance(
                    map_open_region,
                    crazy_place_region,
                    lambda state: (
                        state.has(ItemName.Origins_Craftable_Gramophone_WindDisc, self.player) or
                        state.has(ItemName.Origins_Craftable_Gramophone_FireDisc, self.player) or
                        state.has(ItemName.Origins_Craftable_Gramophone_LightningDisc, self.player) or
                        state.has(ItemName.Origins_Craftable_Gramophone_IceDisc, self.player)
                    )
                )

            if not (self.options.goal_condition == 2 and not self.options.origins_staff_upgrade_checks):
                wind_staff_upgrade_region = self.create_region(self.multiworld, self.player, RegionName.Origins_Staff_Upgrades + " Wind", [loc.name for loc in Locations.Origins_Staff_Wind])
                self.create_entrance(
                    map_open_region,
                    wind_staff_upgrade_region,
                    lambda state: (
                        state.has(ItemName.Origins_Craftable_Gramophone_WindDisc, self.player) and
                        rules.check_round_logic(state, self.player, self.options, 12, Maps.Origins_Map_String) and
                        rules.has_weapon_of_strength(state, self.player, self.options, Maps.Origins_Map_String, 3, 3)
                    )
                )

            if not (self.options.goal_condition == 2 and not self.options.origins_staff_upgrade_checks):
                fire_staff_upgrade_region = self.create_region(self.multiworld, self.player, RegionName.Origins_Staff_Upgrades + " Fire", [loc.name for loc in Locations.Origins_Staff_Fire])
                self.create_entrance(
                    map_open_region,
                    fire_staff_upgrade_region,
                    lambda state: (
                        state.has(ItemName.Origins_Craftable_Gramophone_FireDisc, self.player) and
                        rules.check_round_logic(state, self.player, self.options, 12, Maps.Origins_Map_String) and
                        rules.has_weapon_of_strength(state, self.player, self.options, Maps.Origins_Map_String, 3, 3)
                    )
                )

            if not (self.options.goal_condition == 2 and not self.options.origins_staff_upgrade_checks):
                lightning_staff_upgrade_region = self.create_region(self.multiworld, self.player, RegionName.Origins_Staff_Upgrades + " Lightning", [loc.name for loc in Locations.Origins_Staff_Lightning])
                self.create_entrance(
                    map_open_region,
                    lightning_staff_upgrade_region,
                    lambda state: (
                        state.has(ItemName.Origins_Craftable_Gramophone_LightningDisc, self.player) and
                        rules.check_round_logic(state, self.player, self.options, 12, Maps.Origins_Map_String) and
                        rules.has_weapon_of_strength(state, self.player, self.options, Maps.Origins_Map_String, 3, 3)
                    )
                )

            if not (self.options.goal_condition == 2 and not self.options.origins_staff_upgrade_checks):
                ice_staff_upgrade_region = self.create_region(self.multiworld, self.player, RegionName.Origins_Staff_Upgrades + " Ice", [loc.name for loc in Locations.Origins_Staff_Ice])
                self.create_entrance(
                    map_open_region,
                    ice_staff_upgrade_region,
                    lambda state: (
                            state.has(ItemName.Origins_Craftable_Gramophone_IceDisc, self.player) and
                        rules.check_round_logic(state, self.player, self.options, 12, Maps.Origins_Map_String) and
                        rules.has_weapon_of_strength(state, self.player, self.options, Maps.Origins_Map_String, 3, 3)
                    )
                )
            
            ee_locs = []
            if add_ee_checks:
                ee_locs = [loc.name for loc in Locations.Origins_MainEE_Locations]

            main_ee_region = self.create_region(self.multiworld, self.player, RegionName.Origins_MainEE, ee_locs)
            self.create_entrance(
                map_open_region,
                main_ee_region, 
                lambda state: (
                    state.has(ItemName.Origins_Craftable_Gramophone_WindDisc, self.player) and
                    state.has(ItemName.Origins_Craftable_Gramophone_IceDisc, self.player) and
                    state.has(ItemName.Origins_Craftable_Gramophone_FireDisc, self.player) and
                    state.has(ItemName.Origins_Craftable_Gramophone_LightningDisc, self.player) and
                    rules.check_round_logic(state, self.player, self.options, 18, Maps.Origins_Map_String) and
                    rules.has_shield(state, self.player, Maps.Origins_Map_String) and
                    rules.has_weapon_of_strength(state, self.player, self.options, Maps.Origins_Map_String, 3, 4)
                )
            )

            soul_box_region = self.create_region(self.multiworld, self.player, RegionName.Origins_SoulBoxAny, [LocationName.Origins_SoulBox_One])
            self.create_entrance(
                map_open_region,
                soul_box_region, 
                lambda state: (
                    rules.check_round_logic(state, self.player, self.options, 8, Maps.Origins_Map_String)
                )
            )

            soul_box_all_region = self.create_region(self.multiworld, self.player, RegionName.Origins_SoulBoxAll, [LocationName.Origins_SoulBox_All])
            self.create_entrance(
                soul_box_region,
                soul_box_all_region, 
                lambda state: (
                    rules.check_round_logic(state, self.player, self.options, 16, Maps.Origins_Map_String)
                )
            )
        

        # == Modded Maps ==

        if self.options.map_workshop_wanted_enabled:
            all_locations = []
            main_region = self.create_region(self.multiworld, self.player, RegionName.Wanted_Town, all_locations)
            self.create_entrance(menu_region, main_region, Has(ItemName.Map_Wanted))

            self.add_stat_regions(main_region, Maps.Wanted_Map_String, self.options.round_location_max.value)

            open_locations = []
            open_locations.extend([loc.name for loc in Locations.Wanted_Quest_MainQuest_Locations])
            open_locations.extend([loc.name for loc in Locations.Wanted_Quest_Weapons])
            open_locations.extend([loc.name for loc in Locations.Wanted_Craftable_Locations])
            map_open_region = self.create_region(self.multiworld, self.player, RegionName.Wanted_Open, open_locations)
            self.create_entrance(main_region, map_open_region,
                            lambda state: rules.can_open_map(state, self.player, self.options, Maps.Wanted_Map_String))

            ee_locs = []
            if add_ee_checks:
                ee_locs = [loc.name for loc in Locations.Wanted_Quest_MainEE_Locations]

            main_ee_region = self.create_region(self.multiworld, self.player, RegionName.Wanted_MainEE, ee_locs)
            self.create_entrance(
                map_open_region,
                main_ee_region, 
                lambda state: (
                    rules.check_round_logic(state, self.player, self.options, 18, Maps.Wanted_Map_String) and
                    rules.has_shield(state, self.player, Maps.Wanted_Map_String) and
                    rules.has_special_weapon(state, self.player, self.options, Maps.Wanted_Map_String, ItemName.Weapon_Modded_Blundergat) and
                    rules.has_weapon_of_strength(state, self.player, self.options, Maps.Wanted_Map_String, 3, 3)
                )
            )

    def create_region(self, world: MultiWorld, player: int, name: str, locations=None):
        ret = Region(name, player, world)
        if locations:
            for location in locations:
                location = BO3ZombiesLocation(player, location, self.location_name_to_id[location], ret)
                ret.locations.append(location)

        self.multiworld.regions.append(ret)
        return ret

    def create_item(self, name: str) -> Item:
        data = self.item_name_to_id[name]

        useful_categories = {
            Items.BO3ZombiesItemCategory.MACHINE,
            Items.BO3ZombiesItemCategory.SPECIAL_WEAPON,
            Items.BO3ZombiesItemCategory.CRAFTABLE,
            Items.BO3ZombiesItemCategory.MAP_UNLOCK,
            Items.BO3ZombiesItemCategory.SHOP_ITEMS,
        }

        # TODO: do a getProgressiveItems list instead
        progression_categories = {
            Items.BO3ZombiesItemCategory.MACHINE,
            Items.BO3ZombiesItemCategory.PROGRESSIVE,
            Items.BO3ZombiesItemCategory.REGULAR_WEAPON,
            Items.BO3ZombiesItemCategory.SPECIAL_WEAPON,
            Items.BO3ZombiesItemCategory.CRAFTABLE,
            Items.BO3ZombiesItemCategory.BLOCKER,
            Items.BO3ZombiesItemCategory.POWER,
            Items.BO3ZombiesItemCategory.EASTER_EGG,
            Items.BO3ZombiesItemCategory.VICTORY,
            Items.BO3ZombiesItemCategory.MAP_UNLOCK,
        }

        if Items.all_items_dict[name].category in progression_categories:
            item_classification = ItemClassification.progression
        elif Items.all_items_dict[name].category in useful_categories:
            item_classification = ItemClassification.useful
        elif Items.all_items_dict[name].category == Items.BO3ZombiesItemCategory.TRAP:
            item_classification = ItemClassification.trap
        else:
            item_classification = ItemClassification.filler

        return Items.BO3ZombiesItem(name, item_classification, data, self.player)

    def create_filler_gift(self) -> Item:
        if not hasattr(self, '_gift_bag') or not self._gift_bag:
            self._gift_bag = list(Items.Gift_Items)
            self.random.shuffle(self._gift_bag)

        gift = self._gift_bag.pop()
        return self.create_item(gift[0])
    
    def create_filler_trap(self) -> Item:
        if not hasattr(self, '_trap_bag') or not self._trap_bag:
            self._trap_bag = list(Items.Trap_Items)
            self.random.shuffle(self._trap_bag)

        gift = self._trap_bag.pop()
        return self.create_item(gift[0])

    def create_filler(self) -> Item:
        # TODO make a proper filler item
        return self.create_item(ItemName.Points200)

    def create_items(self) -> None:
        enabled_items: list[ItemData] = [
            Items.Points_1500,
            Items.Points_1500,
        ]

        # Add locked map items
        enabled_items += [ItemData(map, BO3ZombiesItemCategory.MAP_UNLOCK) for map in self.cod_locked_maps]

        # Add progressive starting items
        if self.options.progressive_starting_points > 0:
            num_items = math.floor(self.options.progressive_starting_points / 500)
            for i in range(num_items):
                enabled_items.append(Items.Progressive_StartingPoints500)

        # 2 Progressive Pap items (turn on + alternate ammo types)
        enabled_items.extend([Items.Progressive_PackAPunch, Items.Progressive_PackAPunch])

        # Add progressive perk limits to pool
        if self.options.progressive_perk_limit_increase > 0:
            for i in range(self.options.progressive_perk_limit_increase):
                enabled_items += [Items.Progressive_PerkLimitIncrease]

        # Add shop items
        if self.options.shop_perk_tokens > 0:
            for i in range(self.options.shop_perk_tokens):
                enabled_items.append(Items.Shop_Items[0])
        if self.options.shop_mega_gums > 0:
            for i in range(self.options.shop_mega_gums):
                enabled_items.append(Items.Shop_Items[1])
        if self.options.shop_rare_gums > 0:
            for i in range(self.options.shop_rare_gums):
                enabled_items.append(Items.Shop_Items[2])
        if self.options.shop_legendary_gums > 0:
            for i in range(self.options.shop_legendary_gums):
                enabled_items.append(Items.Shop_Items[3])
        if self.options.shop_additional_checkpoint_tokens > 0:
            for i in range(self.options.shop_additional_checkpoint_tokens):
                enabled_items.append(Items.Shop_Items[4])

        if self.options.shop_starting_checkpoint_tokens > 0:
            for i in range(self.options.shop_starting_checkpoint_tokens):
                self.push_precollected(self.create_item(ItemName.Shop_CheckpointToken))

        # Add machines to pool
        if self.options.map_specific_machines:
            # Add map specific machines for each, remove quick revive if we're starting with it
            if self.options.map_shadows_enabled:
                enabled_items += Items.Shadows_Machines_Specific
            if self.options.map_the_giant_enabled:
                enabled_items += Items.The_Giant_Machines_Specific
            if self.options.map_castle_enabled:
                enabled_items += Items.Castle_Machines_Specific
            if self.options.map_zetsubou_enabled:
                enabled_items += Items.Zetsubou_Machines_Specific
            if self.options.map_gorod_enabled:
                enabled_items += Items.GorodKrovi_Machines_Specific
            if self.options.map_revelations_enabled:
                enabled_items += Items.Revelations_Machines_Specific
            
            if self.options.map_nacht_enabled:
                enabled_items += Items.Nacht_Machines_Specific
            if self.options.map_kino_enabled:
                enabled_items += Items.Kino_Machines_Specific
            if self.options.map_moon_enabled:
                enabled_items += Items.Moon_Machines_Specific
            if self.options.map_origins_enabled:
                enabled_items += Items.Origins_Machines_Specific

            if self.options.map_workshop_wanted_enabled:
                enabled_items += Items.Wanted_Machines_Specific

        else:
            # Only add one instance per machine
            seen = set()
            if self.options.map_shadows_enabled:
                add_universal_items(enabled_items, seen, Items.Shadows_Machines)
            if self.options.map_the_giant_enabled:
                add_universal_items(enabled_items, seen, Items.The_Giant_Machines)
            if self.options.map_castle_enabled:
                add_universal_items(enabled_items, seen, Items.Castle_Machines)
            if self.options.map_zetsubou_enabled:
                add_universal_items(enabled_items, seen, Items.Zetsubou_Machines)
            if self.options.map_gorod_enabled:
                add_universal_items(enabled_items, seen, Items.GorodKrovi_Machines)
            if self.options.map_revelations_enabled:
                add_universal_items(enabled_items, seen, Items.Revelations_Machines)

            if self.options.map_nacht_enabled:
                add_universal_items(enabled_items, seen, Items.Nacht_Machines)
            if self.options.map_kino_enabled:
                add_universal_items(enabled_items, seen, Items.Kino_Machines)
            if self.options.map_moon_enabled:
                add_universal_items(enabled_items, seen, Items.Moon_Machines)
            if self.options.map_origins_enabled:
                add_universal_items(enabled_items, seen, Items.Origins_Machines)

            if self.options.map_workshop_wanted_enabled:
                add_universal_items(enabled_items, seen, Items.Wanted_Machines)

        # We're starting with quick revive, remove from pool
        if self.options.start_quick_revive:
            for item in enabled_items:
                if "Quick Revive" in item.name:
                    enabled_items.remove(item)
            self.push_precollected(self.create_item(ItemName.Machine_QuickRevive))

        map_list = []
        if self.options.map_shadows_enabled:
            map_list.append((Maps.Shadows_Map_String, RegionName.Shadows_Alleyway, RegionName.Shadows_Round_Regions, Locations.Shadows_Round_Locations))
            if self.options.randomized_shield_parts:
                enabled_items += Items.Shadows_Shield
            else:
                self.multiworld.get_location(LocationName.Shadows_Craftable_ShieldPartDoor, self.player).place_locked_item(self.create_item(Items.Shadows_Shield[0].name))
                self.multiworld.get_location(LocationName.Shadows_Craftable_ShieldPartDolly, self.player).place_locked_item(self.create_item(Items.Shadows_Shield[1].name))
                self.multiworld.get_location(LocationName.Shadows_Craftable_ShieldPartClamp, self.player).place_locked_item(self.create_item(Items.Shadows_Shield[2].name))
            enabled_items += Items.Shadows_Craftables
        if self.options.map_the_giant_enabled:
            map_list.append((Maps.The_Giant_Map_String, RegionName.TheGiant_Courtyard, RegionName.TheGiant_Round_Regions, Locations.TheGiant_Round_Locations))
        if self.options.map_castle_enabled:
            map_list.append((Maps.Castle_Map_String, RegionName.Castle_Gondola, RegionName.Castle_Round_Regions, Locations.Castle_Round_Locations))
            if self.options.randomized_shield_parts:
                enabled_items += Items.Castle_Shield
            else:
                self.multiworld.get_location(LocationName.Castle_Craftable_ShieldPartDoor, self.player).place_locked_item(self.create_item(Items.Castle_Shield[0].name))
                self.multiworld.get_location(LocationName.Castle_Craftable_ShieldPartDolly, self.player).place_locked_item(self.create_item(Items.Castle_Shield[1].name))
                self.multiworld.get_location(LocationName.Castle_Craftable_ShieldPartClamp, self.player).place_locked_item(self.create_item(Items.Castle_Shield[2].name))
            enabled_items += Items.Castle_Craftables
        if self.options.map_zetsubou_enabled:
            map_list.append((Maps.Zetsubou_Map_String, RegionName.Zetsubou_Beach, RegionName.Zetsubou_Round_Regions, Locations.Zetsubou_Round_Locations))
            if self.options.randomized_shield_parts:
                enabled_items += Items.Zetsubou_Shield
            else:
                self.multiworld.get_location(LocationName.Zetsubou_Craftable_ShieldPartDoor, self.player).place_locked_item(self.create_item(Items.Zetsubou_Shield[0].name))
                self.multiworld.get_location(LocationName.Zetsubou_Craftable_ShieldPartDolly, self.player).place_locked_item(self.create_item(Items.Zetsubou_Shield[1].name))
                self.multiworld.get_location(LocationName.Zetsubou_Craftable_ShieldPartClamp, self.player).place_locked_item(self.create_item(Items.Zetsubou_Shield[2].name))
            enabled_items += Items.Zetsubou_Craftables_Gasmask
        if self.options.map_gorod_enabled:
            map_list.append((Maps.GorodKrovi_Map_String, RegionName.Gorod_Trenches, RegionName.Gorod_Round_Regions, Locations.GorodKrovi_Round_Locations))
            if self.options.randomized_shield_parts:
                enabled_items += Items.GorodKrovi_Shield
            else:
                self.multiworld.get_location(LocationName.GorodKrovi_Craftable_ShieldPartDoor, self.player).place_locked_item(self.create_item(Items.GorodKrovi_Shield[0].name))
                self.multiworld.get_location(LocationName.GorodKrovi_Craftable_ShieldPartDolly, self.player).place_locked_item(self.create_item(Items.GorodKrovi_Shield[1].name))
                self.multiworld.get_location(LocationName.GorodKrovi_Craftable_ShieldPartClamp, self.player).place_locked_item(self.create_item(Items.GorodKrovi_Shield[2].name))
            # if self.options.randomized_gorod_dragonride_parts:
            #     enabled_items += Items.GorodKrovi_Craftables_Dragonride
            # else:
            #     self.multiworld.get_location(LocationName.GorodKrovi_Quest_MainQuest_Dragonride_Transmitter, self.player).place_locked_item(self.create_item(ItemName.GorodKrovi_Craftable_Dragonride_Transmitter))
            #     self.multiworld.get_location(LocationName.GorodKrovi_Quest_MainQuest_Dragonride_Codes, self.player).place_locked_item(self.create_item(ItemName.GorodKrovi_Craftable_Dragonride_Codes))
            #     self.multiworld.get_location(LocationName.GorodKrovi_Quest_MainQuest_Dragonride_Map, self.player).place_locked_item(self.create_item(ItemName.GorodKrovi_Craftable_Dragonride_Map))
        if self.options.map_revelations_enabled:
            map_list.append((Maps.Revelations_Map_String, RegionName.Revelations_House, RegionName.Revelations_Round_Regions, Locations.Revelations_Round_Locations))
            if self.options.randomized_shield_parts:
                enabled_items += Items.Revelations_Shield
            else:
                self.multiworld.get_location(LocationName.Revelations_Craftable_ShieldPartDoor, self.player).place_locked_item(self.create_item(Items.Revelations_Shield[0].name))
                self.multiworld.get_location(LocationName.Revelations_Craftable_ShieldPartDolly, self.player).place_locked_item(self.create_item(Items.Revelations_Shield[1].name))
                self.multiworld.get_location(LocationName.Revelations_Craftable_ShieldPartClamp, self.player).place_locked_item(self.create_item(Items.Revelations_Shield[2].name))
        
        if self.options.map_nacht_enabled:
            map_list.append((Maps.Nacht_Map_String, RegionName.Nacht_Entrance, RegionName.Nacht_Round_Regions, Locations.Nacht_Round_Locations))

        if self.options.map_kino_enabled:
            map_list.append((Maps.Kino_Map_String, RegionName.Kino_Entrance, RegionName.Kino_Round_Regions, Locations.Kino_Round_Locations))
        
        if self.options.map_moon_enabled:
            map_list.append((Maps.Moon_Map_String, RegionName.Moon_Entrance, RegionName.Moon_Round_Regions, Locations.Moon_Round_Locations))

        if self.options.map_origins_enabled:
            map_list.append((Maps.Origins_Map_String, RegionName.Origins_Entrance, RegionName.Origins_Round_Regions, Locations.Origins_Round_Locations))
            if self.options.randomized_shield_parts:
                enabled_items += Items.Origins_Shield
            else:
                self.multiworld.get_location(LocationName.Origins_Craftable_ShieldPartDoor, self.player).place_locked_item(self.create_item(Items.Origins_Shield[0].name))
                self.multiworld.get_location(LocationName.Origins_Craftable_ShieldPartDolly, self.player).place_locked_item(self.create_item(Items.Origins_Shield[1].name))
                self.multiworld.get_location(LocationName.Origins_Craftable_ShieldPartClamp, self.player).place_locked_item(self.create_item(Items.Origins_Shield[2].name))
            enabled_items += Items.Origins_Discs
            enabled_items += Items.Origins_MaxisDrone

        if self.options.map_workshop_wanted_enabled:
            map_list.append((Maps.Wanted_Map_String, RegionName.Wanted_Town, RegionName.Wanted_Round_Regions, Locations.Wanted_Round_Locations))
            if self.options.randomized_shield_parts:
                enabled_items += Items.Wanted_Shield
            else:
                self.multiworld.get_location(LocationName.Wanted_Craftable_ShieldPartDoor, self.player).place_locked_item(self.create_item(Items.Wanted_Shield[0].name))
                self.multiworld.get_location(LocationName.Wanted_Craftable_ShieldPartDolly, self.player).place_locked_item(self.create_item(Items.Wanted_Shield[1].name))
                self.multiworld.get_location(LocationName.Wanted_Craftable_ShieldPartClamp, self.player).place_locked_item(self.create_item(Items.Wanted_Shield[2].name))
            enabled_items += Items.Wanted_Craftable_Acidgat

        enabled_items += [ItemData(item, BO3ZombiesItemCategory.SPECIAL_WEAPON) for item in self.mystery_box_special_items]

        distribution = WeaponDistribution()
        distribution.num_of_group = [
            self.options.starting_weapons_1.value,
            self.options.starting_weapons_2.value,
            self.options.starting_weapons_3.value,
            self.options.starting_weapons_4.value,
            self.options.starting_weapons_5.value,
        ]
        precollected_weapons = self.preselect_weapons([map[0] for map in map_list], distribution)
        precollected_names = [data.item_name for data in precollected_weapons.values()]
        for weapon_key, weapon_data in precollected_weapons.items():
            self.multiworld.push_precollected(self.create_item(weapon_data.item_name))
        self.weapon_unlocks: list[str] = [
            item for item in self.weapon_unlocks 
            if item not in precollected_names
        ]

        enabled_items += [ItemData(item, BO3ZombiesItemCategory.REGULAR_WEAPON) for item in self.weapon_unlocks]

        # Easter Egg Hunt
        if self.options.goal_condition == 0:
            # Get list of compatible enabled maps
            ee_pairs = []
            if self.options.map_shadows_enabled:
                ee_pairs.append((LocationName.Shadows_Quest_MainEE_Victory, Maps.Shadows_Map_String + ItemName.EE_Victory))
            if self.options.map_castle_enabled:
                ee_pairs.append((LocationName.Castle_Quest_MainEE_Victory, Maps.Castle_Map_String + ItemName.EE_Victory))
            if self.options.map_zetsubou_enabled:
                ee_pairs.append((LocationName.Zetsubou_Quest_MainEE_Victory, Maps.Zetsubou_Map_String + ItemName.EE_Victory))
            if self.options.map_gorod_enabled:
                ee_pairs.append((LocationName.GorodKrovi_Quest_MainEE_Victory, Maps.GorodKrovi_Map_String + ItemName.EE_Victory))
            if self.options.map_revelations_enabled:
                ee_pairs.append((LocationName.Revelations_Quest_MainEE_Victory, Maps.Revelations_Map_String + ItemName.EE_Victory))
            if self.options.map_moon_enabled:
                ee_pairs.append((LocationName.Moon_Quest_MainEE_Victory, Maps.Moon_Map_String + ItemName.EE_Victory))
            ## TODO: Add victory loc properly
            if self.options.map_origins_enabled:
                ee_pairs.append((LocationName.Origins_Quest_MainEE_Samantha, Maps.Origins_Map_String + ItemName.EE_Victory))
            if self.options.map_workshop_wanted_enabled:
                ee_pairs.append((LocationName.Wanted_Quest_MainEE_Victory, Maps.Wanted_Map_String + ItemName.EE_Victory))

            if len(ee_pairs) == 0:
                if self.options.map_the_giant_enabled:
                    ee_pairs.append((LocationName.TheGiant_Quest_FlyTrap, Maps.The_Giant_Map_String + ItemName.EE_Victory))
                else:
                    self.options.goal_condition.value = 2
                    print(f"Black Ops 3 - Zombies: (Player {self.player}) No easter egg map enabled, swapping to goal round")

            # Get bounds for number of victory items to add
            ee_allow_any = not self.options.goal_ee_random
            ee_count = min(self.options.goal_ee_count.value, len(ee_pairs))
            self.ee_goal_items = []

            # Preselect the list of required maps, if random selection is enabled
            if not ee_allow_any:
                ee_pairs = self.random.sample(ee_pairs, ee_count)

            # Fill victory items at their victory locations
            for pair in ee_pairs:
                item = self.create_item(pair[1])
                self.multiworld.get_location(pair[0], self.player).place_locked_item(item)
                self.ee_goal_items.append(pair[1])

        # Weapon Quest
        if self.options.goal_condition == 1:
            if self.options.map_shadows_enabled:
                goal_items = list(map(self.create_item, [
                    ItemName.Shadows_Victory_ApothiconSwordLvl2,
                    ItemName.Shadows_Victory_Upgraded_LilArnies,
                    ItemName.Shadows_Victory_Upgraded_DoughnutMines,
                ]))
                self.weapon_quest_items.extend([item.name for item in goal_items])
                self.multiworld.get_location(LocationName.Shadows_Quest_ApothiconSword_CollectUpgradedSword, self.player).place_locked_item(goal_items[0]) 
                self.multiworld.get_location(LocationName.Shadows_Quest_LilArnies_Upgrade, self.player).place_locked_item(goal_items[1])
                self.multiworld.get_location(LocationName.Shadows_Quest_DoughnutMines, self.player).place_locked_item(goal_items[2])

            if self.options.map_castle_enabled:
                # Handled in create_regions
                pass
            
            if self.options.map_zetsubou_enabled:
                goal_items = list(map(self.create_item, [
                    ItemName.Zetsubou_Victory_Masamune,
                    ItemName.Zetsubou_Victory_Skull,
                ]))
                self.weapon_quest_items.extend([item.name for item in goal_items])
                self.multiworld.get_location(LocationName.Zetsubou_Quest_Masamune_Acquired, self.player).place_locked_item(goal_items[0])
                self.multiworld.get_location(LocationName.Zetsubou_Quest_Skull_Survive, self.player).place_locked_item(goal_items[1])
            
            if self.options.map_gorod_enabled:
                goal_items = list(map(self.create_item, [
                    ItemName.GorodKrovi_Victory_DragonGauntlets,
                    ItemName.GorodKrovi_Victory_Upgraded_Dragonstrikes,
                    ItemName.GorodKrovi_Victory_Upgraded_MonkeyBombs,
                    ItemName.GorodKrovi_Victory_TiamatsMaw
                ]))
                self.weapon_quest_items.extend([item.name for item in goal_items])
                self.multiworld.get_location(Locations.GorodKrovi_Quest_DragonGauntlets_Late[-1].name, self.player).place_locked_item(goal_items[0])
                self.multiworld.get_location(Locations.GorodKrovi_Quest_DragonStrikes_Upgraded[-1].name, self.player).place_locked_item(goal_items[1])
                self.multiworld.get_location(Locations.GorodKrovi_Quest_Challenges[3].name, self.player).place_locked_item(goal_items[2])
                self.multiworld.get_location(Locations.GorodKrovi_Quest_TiamatsMaw[-1].name, self.player).place_locked_item(goal_items[3])

            if self.options.map_workshop_wanted_enabled:
                goal_items = list(map(self.create_item, [
                    ItemName.Wanted_Victory_Magmagat,
                    ItemName.Wanted_Victory_GreatScott,
                ]))
                self.weapon_quest_items.extend([item.name for item in goal_items])
                self.multiworld.get_location(Locations.Wanted_Quest_Weapons[0].name, self.player).place_locked_item(goal_items[0])
                self.multiworld.get_location(Locations.Wanted_Quest_Weapons[1].name, self.player).place_locked_item(goal_items[1])

        is_goal_cond = self.options.goal_condition == 2

        base_locations_left = len(self.multiworld.get_unfilled_locations(self.player))
        # Account for locked goal rounds
        if self.options.goal_condition == 2:
            base_locations_left -= len(map_list)
        locations_left = base_locations_left + self.calc_round_locations(len(map_list), is_goal_cond)

        if len(enabled_items) > locations_left:
            print(f"Black Ops 3 - Zombies: (Player {self.player}) Too few locations, increasing round frequency and maximum")

        # Adjust round freq downwards to try and generate enough locations
        while self.options.round_location_freq.value > 1 and len(enabled_items) > locations_left:
            self.options.round_location_freq.value -= 1
            locations_left = base_locations_left + self.calc_round_locations(len(map_list), is_goal_cond)

        # Still not enough locations, adjust max round
        while self.options.round_location_max.value < 99 and len(enabled_items) > locations_left :
            self.options.round_location_max.value += 1
            # if self.options.goal_round.value <= self.options.round_location_max.value:
            #     self.options.goal_round.value = self.options.round_location_max.value + 1
            # if self.options.round_location_max.value > self.options.goal_round.value:
            #     self.options.goal_round.value = self.options.round_location_max.value
            locations_left = base_locations_left + self.calc_round_locations(len(map_list), is_goal_cond)

        # Add round locations
        round_max = self.options.round_location_max.value
        goal_round = self.options.goal_round.value

        for str_map, str_main_region, list_round_regions, round_locations in map_list:
            round_locs = add_round_locations(round_locations, round_max, self.options.round_location_freq.value, is_goal_cond, goal_round)
            main_region = self.multiworld.get_region(str_main_region, self.player)
            for location_name in round_locs[0]:
                location = BO3ZombiesLocation(self.player, location_name, self.location_name_to_id[location_name], main_region)
                main_region.locations.append(location)
            for region in range(len(list_round_regions)):
                # (Starting Region, Region Being connected, Locations corresponding to region)
                self.add_round_region(main_region, list_round_regions[region], round_locs[region+1])

        # Goal Round Condition
        if self.options.goal_condition == 2:
            self.goal_round_items = []
            for m in map_list:
                # Victory round item on every map
                goal_location = Locations.get_map_victory_location(m[0], self.options.goal_round)
                goal_item = self.create_item(m[0] + " Victory")
                self.goal_round_items.append(m[0] + " Victory")
                self.multiworld.get_location(goal_location, self.player).place_locked_item(goal_item)

        locations_left = len(self.multiworld.get_unfilled_locations(self.player))

        for item_data in enabled_items:
            self.multiworld.itempool.append(self.create_item(item_data.name))
            locations_left -= 1

        if locations_left > 0:
            gift_filler_weight = self.options.gift_weight / 100
            trap_filler_weight = self.options.trap_weight / 100
            total_weight = gift_filler_weight + trap_filler_weight
            if total_weight > 1:
                gift_filler_weight *= 1 / total_weight
                trap_filler_weight *= 1 / total_weight
            trap_filler_count = math.floor(locations_left * trap_filler_weight)
            gift_filler_count = math.floor(locations_left * gift_filler_weight)
            filler_count = locations_left - (gift_filler_count + trap_filler_count)

            # Creates filler in remaining slots
            self.multiworld.itempool.extend([self.create_filler_trap() for _ in range(trap_filler_count)])
            self.multiworld.itempool.extend([self.create_filler_gift() for _ in range(gift_filler_count)])
            self.multiworld.itempool.extend([self.create_filler() for _ in range(filler_count)])

    def calc_round_locations(self, num_maps, is_goal_cond) -> int:
        round_freq = self.options.round_location_freq.value
        round_max = self.options.round_location_max.value
        goal_round = self.options.goal_round.value
        
        if round_freq == 0:
            return 0
        
        count = 0
        i = round_freq
        
        # Match the logic in add_round_locations
        while i <= round_max:
            # Skip round 1
            if i != 1:
                count += 1
            i += round_freq
        
        # Account for goal round being added separately if not already included
        if is_goal_cond and goal_round is not None:
            if goal_round > round_max or goal_round % round_freq != 0:
                count += 1
        
        return count * num_maps

    def generate_basic(self) -> None:
        # for debugging purposes, you may want to visualize the layout of your world. Uncomment the following code to
        # write a PlantUML diagram to the file "my_world.puml" that can help you see whether your regions and locations
        # are connected and placed as desired
        #from Utils import visualize_regions
        #visualize_regions(self.multiworld.get_region("Menu", self.player), "my_world.puml")
        pass

    def set_rules(self) -> None:
        self.slot_goal_items_required = 0
        self.slot_goal_items = []
        # Goal Conditions

        # Easter Egg Hunt
        if self.options.goal_condition == 0:
            self.slot_goal_items = self.ee_goal_items
            # Whether or not we require *all* selected goal items (Randomised goal selection)
            ee_allow_any = not self.options.goal_ee_random
            if not ee_allow_any:
                self.slot_goal_items_required = len(self.slot_goal_items)
                self.multiworld.completion_condition[self.player] = lambda state: state.has_all(self.ee_goal_items, self.player)
            else:
                self.slot_goal_items_required = self.options.goal_ee_count.value
                self.multiworld.completion_condition[self.player] = lambda state: state.has_from_list(self.ee_goal_items, self.player, min(self.options.goal_ee_count.value, len(self.ee_goal_items))) 
            
        # Weapon Quest
        if self.options.goal_condition == 1:
            self.slot_goal_items = self.weapon_quest_items
            self.slot_goal_items_required = len(self.slot_goal_items)
            self.multiworld.completion_condition[self.player] = lambda state: state.has_all(self.weapon_quest_items, self.player)

        # Goal Round
        if self.options.goal_condition == 2:
            self.slot_goal_items = self.goal_round_items
            self.slot_goal_items_required = min(len(self.slot_goal_items), self.options.goal_round_count.value)
            self.multiworld.completion_condition[self.player] = lambda state: state.has_all(self.goal_round_items, self.player)

    def add_stat_regions(self, main_region: Region, map_name: str, max_round_in_logic: int):
        last_region = main_region
        for i in range(len(Locations.MAP_STAT_ROUNDS)):
            round_num = Locations.MAP_STAT_ROUNDS[i]
            if round_num > max_round_in_logic:
                return
            round_locs = []
            if self.options.kill_checks_enabled:
                round_locs.append(f"{map_name} {Locations.MAP_STAT_KILLS[i]} Kills")
            if self.options.headshot_checks_enabled:
                round_locs.append(f"{map_name} {Locations.MAP_STAT_HEADSHOTS[i]} Headshots")
            round_region = self.create_region(self.multiworld, self.player, f"{map_name} Stat Round {round_num}", round_locs)
            self.create_entrance(
                last_region,
                round_region,
                (lambda round_num: lambda state: (
                    rules.check_round_logic(state, self.player, self.options, round_num, map_name) and
                    (rules.has_perk(state, self.player, self.options, map_name, ItemName.Machine_DoubleTap) if (round_num >= 20 and self.options.headshot_checks_enabled.value) else True)
                ))(round_num)
            )
            last_region = round_region

    def fill_slot_data(self) -> dict:
        options = self.options
        
        slot_data = {
            'seed': "".join(
                self.random.choice(string.ascii_letters) for _ in range(16)),
            'base_id': str(self.base_id),
            "slot": self.multiworld.player_name[self.player],
            "map_specific_machines": bool(options.map_specific_machines),
            "special_rounds_enabled": bool(options.special_rounds_enabled),
            "perk_limit_default_modifier": int(options.perk_limit_default_modifier),
            "super_ee_reward": bool(options.super_ee_reward),
            "mystery_box_special_items": bool(options.mystery_box_special_items),
            "mystery_box_regular_items": bool(options.mystery_box_regular_items),
            "mystery_box_expanded": bool(options.mystery_box_expanded),
            "difficulty_rng_moon_digger": bool(options.difficulty_rng_moon_digger),
            "difficulty_rng_moon_box": bool(options.difficulty_rng_moon_box),
            "difficulty_gorod_egg_cooldown": bool(options.difficulty_gorod_egg_cooldown),
            "difficulty_gorod_dragon_wings": bool(options.difficulty_gorod_dragon_wings),
            "difficulty_ee_checkpoints": options.difficulty_ee_checkpoints.value,
            "difficulty_round_checkpoints": options.difficulty_round_checkpoints.value,
            "rolled_bows": self.rolled_bows,
            "rolled_masks": self.rolled_masks,
            "attachments_randomized": bool(options.attachments_randomized),
            "attachments_sight_weight": int(options.attachments_sight_weight),
            "camo_randomized": bool(options.camo_randomized),
            "camo_mixed": bool(options.camo_mixed),
            "camo_pap_randomized": bool(options.camo_pap_randomized),
            "camo_pap_mixed": bool(options.camo_pap_mixed),
            "camo_joined": bool(options.camo_joined),
            "reticle_randomized": bool(options.reticle_randomized),
            "reticle_pap_randomized": bool(options.reticle_pap_randomized),
            "reticle_joined": bool(options.reticle_joined),
            "deathlink_enabled": bool(options.deathlink_enabled),
            "deathlink_send_mode": int(options.deathlink_send_mode),
            "deathlink_recv_mode": int(options.deathlink_recv_mode),
            "goal_items_required": int(self.slot_goal_items_required),
            "goal_items": self.slot_goal_items,
        }

        return slot_data

    def add_round_region(self, main_region, new_region_name, round_locs):
        round_num = new_region_name[-2:]
        # Get the round number from the location name
        if round_num == "00":  # if the last two characters in the string are 00 we know it's really round 100
            round_num = 100
        else:
            round_num = int(round_num)
        # This gets the map name from our location name
        map_name = new_region_name.split(")")[0] + ")"
        region = self.create_region(self.multiworld, self.player, new_region_name, round_locs)
        rule = lambda state: rules.check_round_logic(state, self.player, self.options, round_num, map_name)
        self.create_entrance(main_region, region, rule)

    def preselect_weapons(self, map_list: list[str], distribution: WeaponDistribution):
        # Sets for strength 1 to 5
        precollected_weapons: dict[str, WeaponData] = {}

        shuffled_maps = map_list.copy()
        self.random.shuffle(shuffled_maps)

        for map in shuffled_maps:
            # Get list of available weapons
            weapon_data_set = Weapons.map_weapon_data_sets[map]
            weapon_list = weapon_data_set.vanilla
            if self.options.mystery_box_expanded.value:
                weapon_list = {**weapon_data_set.vanilla, **weapon_data_set.expanded}

            # Filter weapon set by strength
            filtered_sets: list[list[tuple[str, WeaponData]]] = [[], [], [], [], []]

            for weapon_key, weapon_data in weapon_list.items():
                if weapon_data.strength >= 1 and weapon_data.strength <= 5:
                    filtered_sets[weapon_data.strength - 1].append((weapon_key, weapon_data))

            # Check which weapons have already been added to the pool
            map_weapons: list[list[tuple[str, WeaponData]]] = [[], [], [], [], []]
            for weapon_key, weapon_data in precollected_weapons.items():
                if weapon_key in weapon_list:
                    map_weapons[weapon_data.strength - 1].append((weapon_key, weapon_data))

            # Add based on distribution asked for
            for i in range(len(distribution.num_of_group)):
                if i >= 0 and i < 5:
                    cur_set = map_weapons[i]
                    # Add weapons for this map until we reach the required amount
                    while len(filtered_sets[i]) > 0 and len(cur_set) < distribution.num_of_group[i]:
                        weap_tuple = self.random.choice(filtered_sets[i])
                        map_weapons[i].append(weap_tuple)
                        filtered_sets[i].remove(weap_tuple)

            # Add any new weapons into precollected
            for i in range(len(map_weapons)):
                for weapon_key, weapon_data in map_weapons[i]:
                    if weapon_key not in precollected_weapons:
                        precollected_weapons[weapon_key] = weapon_data

        return precollected_weapons
        

def add_universal_items(enabled_items, seen, items):
    for item in items:
        if item[0] not in seen:
            enabled_items.append(item)
            seen.add(item[0])


def add_round_locations(round_locations, round_max, round_freq, is_goal_cond, goal_round):
    round_locs_early = []
    round_locs_10 = []
    round_locs_15 = []
    round_locs_20 = []
    round_locs_25 = []
    round_locs_30 = []
    round_locs_35 = []
    round_locs_40 = []

    if round_freq > 0:
        i = round_freq
        # Add rounds into pool
        while i <= round_max:
            # Never assign to round 1
            if i == 1:
                i += round_freq
                continue
            elif i <= 6:
                round_locs_early.append(round_locations[i - 2].name)
            elif i <= 10:
                round_locs_10.append(round_locations[i - 2].name)
            elif i <= 15:
                round_locs_15.append(round_locations[i - 2].name)
            elif i <= 20:
                round_locs_20.append(round_locations[i - 2].name)
            elif i <= 25:
                round_locs_25.append(round_locations[i - 2].name)
            elif i <= 30:
                round_locs_30.append(round_locations[i - 2].name)
            elif i <= 35:
                round_locs_35.append(round_locations[i - 2].name)
            else:
                round_locs_40.append(round_locations[i - 2].name)
            i += round_freq
        # Make sure the Goal Round is always included
        if is_goal_cond:
            if goal_round > round_max or goal_round % round_freq != 0:
                if goal_round <= 5:
                    round_locs_early.append(round_locations[goal_round - 2].name)
                elif goal_round <= 10:
                    round_locs_10.append(round_locations[goal_round - 2].name)
                elif goal_round <= 15:
                    round_locs_15.append(round_locations[goal_round - 2].name)
                elif goal_round <= 20:
                    round_locs_20.append(round_locations[goal_round - 2].name)
                elif goal_round <= 25:
                    round_locs_25.append(round_locations[goal_round - 2].name)
                elif goal_round <= 30:
                    round_locs_30.append(round_locations[goal_round - 2].name)
                elif goal_round <= 35:
                    round_locs_35.append(round_locations[goal_round - 2].name)
                else:
                    round_locs_40.append(round_locations[goal_round - 2].name)
    return [round_locs_early, round_locs_10, round_locs_15, round_locs_20, round_locs_25, round_locs_30, round_locs_35, round_locs_40]

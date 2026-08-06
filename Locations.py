import typing
from enum import IntEnum
from .Names import LocationName, Maps

MAP_STAT_ROUNDS = [8, 12, 16, 22, 30]
MAP_STAT_KILLS = [75, 150, 300, 500, 1000]
MAP_STAT_HEADSHOTS = [25, 50, 100, 175, 300]

BaseMapIds = {
    Maps.The_Giant_Map_String: 1000,
    Maps.Castle_Map_String: 2000,
    Maps.Shadows_Map_String: 3000,
    Maps.GorodKrovi_Map_String: 4000,
    Maps.Zetsubou_Map_String: 5000,
    Maps.Revelations_Map_String: 6000,
    Maps.Kino_Map_String: 11000,
    Maps.Moon_Map_String: 12000,
    Maps.Origins_Map_String: 13000,
    Maps.Nacht_Map_String: 14000,
    # === Modded Maps ===
    Maps.Wanted_Map_String: 20000,
}

class BO3ZombiesLocationCategory(IntEnum):
    ROUND = 0
    MISC = 10
    CRAFTABLE_PART = 20
    QUEST = 30

class LocationData(typing.NamedTuple):
    name: str
    category: BO3ZombiesLocationCategory
    code: int

def gen_map_round_locations(map_string, count):
    if map_string not in BaseMapIds:
        raise Exception("round location gen - Map string not in base map ids?")
    base_map_id = BaseMapIds[map_string]
    locations = []
    # Start on round 2
    for i in range(2, count + 2):
        location_name = f"{map_string} Round {i:02d}"
        locations.append(LocationData(location_name, BO3ZombiesLocationCategory.ROUND, base_map_id + (i - 1)))
    return locations

def get_map_victory_location(map_string, goal_round):
    converted = int(goal_round)
    if map_string not in BaseMapIds:
        raise Exception("victory gen - Map string not in base map ids?")
    base_map_id = BaseMapIds[map_string]
    location_name = f"{map_string} Round {converted:02d}"
    return location_name

def gen_map_stat_locations(map_string):

    base_map_id = BaseMapIds[map_string]
    locations = []

    for i in range(len(MAP_STAT_KILLS)):
        locations.append(LocationData(f"{map_string} {MAP_STAT_KILLS[i]} Kills", BO3ZombiesLocationCategory.MISC, base_map_id + 900 + i))

    for i in range(len(MAP_STAT_HEADSHOTS)):
        locations.append(LocationData(f"{map_string} {MAP_STAT_HEADSHOTS[i]} Headshots", BO3ZombiesLocationCategory.MISC, base_map_id + 950 + i))
    
    return locations

# Location IDs
# The Giant - 1000 to 1100 rounds, 1100+ to map specific checks
# Castle - 2000 to 2100 rounds, 2100+ to map specific checks
# Shadows of Evil - 3000 to 3100 rounds, 3100+ to map specific checks
# Universal - 9000 to 9999

# The Giant zm_giant

TheGiant_Round_Locations = gen_map_round_locations(Maps.The_Giant_Map_String, 99)

TheGiant_Quest_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.TheGiant_Quest_LinkAnyTeleporter, 1101),
    (LocationName.TheGiant_Quest_LinkAllTeleporters, 1102),
    (LocationName.TheGiant_Quest_Power, 1108),
    (LocationName.TheGiant_Quest_AllSpareChangeCollected, 1109),
]]

TheGiant_Pap = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.TheGiant_Quest_FlyTrap, 1110),
]]

TheGiant_MonkeyBomb = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.TheGiant_Quest_SecretPerk, 1120),
]]

TheGiant_Quest_Music_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.TheGiant_Quest_Music_BeautyOfAnnihilation, 1201),
]]

TheGiant_Quest_Radio_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.TheGiant_Quest_Radio_LabCCatwalk, 1211),
    (LocationName.TheGiant_Quest_Radio_Bridge, 1212),
    (LocationName.TheGiant_Quest_Radio_Furnace, 1213),
    (LocationName.TheGiant_Quest_Radio_Spawn, 1214),
    (LocationName.TheGiant_Quest_Radio_OutsideLabA, 1215),
    (LocationName.TheGiant_Quest_Radio_LabA, 1221),
    (LocationName.TheGiant_Quest_Radio_LabB, 1222),
    (LocationName.TheGiant_Quest_Radio_LabC, 1223),
]]

# Castle zm_castle

Castle_Round_Locations = gen_map_round_locations(Maps.Castle_Map_String, 99)

Castle_Craftable_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.CRAFTABLE_PART, row[1]) for row in [
    (LocationName.Castle_Craftable_ShieldPartDolly, 2200),
    (LocationName.Castle_Craftable_ShieldPartDoor, 2201),
    (LocationName.Castle_Craftable_ShieldPartClamp, 2202),
]]

Castle_DG4_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.CRAFTABLE_PART, row[1]) for row in [
    (LocationName.Castle_Craftable_RagnarokDG4PartBody, 2210),
    (LocationName.Castle_Craftable_RagnarokDG4PartGuards, 2211),
    (LocationName.Castle_Craftable_RagnarokDG4PartHandle, 2212),
]]

Castle_Quest_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Castle_Quest_AllSpareChange, 2300),
    (LocationName.Castle_Quest_FeedDragonheads, 2301),
    (LocationName.Castle_Quest_TurnOnLandingPads, 2302),
]]

Castle_Quest_Music_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Castle_Quest_Music_DeadAgain, 2400),
    (LocationName.Castle_Quest_Music_Requiem, 2401),
]]

Castle_Quest_Radio_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Castle_Quest_Radio_ArmoryWindow, 2410),
    (LocationName.Castle_Quest_Radio_Church, 2411),
    (LocationName.Castle_Quest_Radio_Projector, 2412),
    (LocationName.Castle_Quest_Radio_Lab, 2413),
    (LocationName.Castle_Quest_Radio_ClockTower, 2414),
]]

Castle_Quest_ElementalBow_Storm_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Castle_Quest_ElementalBow_Storm_TakeArrow, 2500),
    (LocationName.Castle_Quest_ElementalBow_Storm_LightBeacons, 2501),
    (LocationName.Castle_Quest_ElementalBow_Storm_Wallrun, 2502),
    (LocationName.Castle_Quest_ElementalBow_Storm_Batteries, 2503),
    (LocationName.Castle_Quest_ElementalBow_Storm_ChargeBeacons, 2504),
    (LocationName.Castle_Quest_ElementalBow_Storm_RepairArrow, 2505),
    (LocationName.Castle_Quest_ElementalBow_Storm_ForgeBow, 2506),
]]

Castle_Quest_ElementalBow_Wolf_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Castle_Quest_ElementalBow_Wolf_Paintings, 2510),
    (LocationName.Castle_Quest_ElementalBow_Wolf_TakeArrow, 2511),
    (LocationName.Castle_Quest_ElementalBow_Wolf_CollectSkull, 2512),
    (LocationName.Castle_Quest_ElementalBow_Wolf_Escort, 2513),
    (LocationName.Castle_Quest_ElementalBow_Wolf_RepairArrow, 2514),
    (LocationName.Castle_Quest_ElementalBow_Wolf_ForgeBow, 2515),
]]

Castle_Quest_ElementalBow_Fire_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Castle_Quest_ElementalBow_Fire_TakeArrow, 2520),
    (LocationName.Castle_Quest_ElementalBow_Fire_ShootOrb, 2521),
    (LocationName.Castle_Quest_ElementalBow_Fire_ChargeCircles, 2522),
    (LocationName.Castle_Quest_ElementalBow_Fire_MagmaBall, 2523),
    (LocationName.Castle_Quest_ElementalBow_Fire_RepairArrow, 2524),
    (LocationName.Castle_Quest_ElementalBow_Fire_ForgeBow, 2525),
]]

Castle_Quest_ElementalBow_Void_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Castle_Quest_ElementalBow_Void_TakeArrow, 2530),
    (LocationName.Castle_Quest_ElementalBow_Void_RitualSacrifice, 2531),
    (LocationName.Castle_Quest_ElementalBow_Void_CollectSkulls, 2532),
    (LocationName.Castle_Quest_ElementalBow_Void_SacrificeCrawlers, 2533),
    (LocationName.Castle_Quest_ElementalBow_Void_RunePuzzle, 2534),
    (LocationName.Castle_Quest_ElementalBow_Void_RepairArrow, 2535),
    (LocationName.Castle_Quest_ElementalBow_Void_ForgeBow, 2536),
]]

Castle_Quest_MainEE_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Castle_Quest_MainEE_ActivateTeleporter, 2600),
    (LocationName.Castle_Quest_MainEE_UnlockSafe, 2601),
    (LocationName.Castle_Quest_MainEE_RecoverRocket, 2602),
    (LocationName.Castle_Quest_MainEE_OpenMPD, 2603),
    (LocationName.Castle_Quest_MainEE_BossFight, 2604),
    (LocationName.Castle_Quest_MainEE_BlowUpMoon, 2605),
    (LocationName.Castle_Quest_MainEE_Victory, 2606),
]]

# Shadows of Evil zm_zod
Shadows_Round_Locations = gen_map_round_locations(Maps.Shadows_Map_String, 99)

Shadows_Quest_MainQuest_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Shadows_Quest_MainQuest_MagicianRitual, 3100),
    (LocationName.Shadows_Quest_MainQuest_BoxerRitual, 3101),
    (LocationName.Shadows_Quest_MainQuest_DetectivesRitual, 3102),
    (LocationName.Shadows_Quest_MainQuest_FemmeFataleRitual, 3103),
    (LocationName.Shadows_Quest_MainQuest_OpenPortal, 3104),
]]

Shadows_Quest_ApothiconSword_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Shadows_Quest_ApothiconSword_EnterCode, 3110),
    (LocationName.Shadows_Quest_ApothiconSword_CollectSword, 3111),
    (LocationName.Shadows_Quest_ApothiconSword_Egg1, 3120),

]]

Shadows_Quest_ApothiconSword_Upgrade_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Shadows_Quest_ApothiconSword_CollectUpgradedSword, 3112),
    (LocationName.Shadows_Quest_ApothiconSword_Egg2, 3121),
]]


Shadows_Quest_MainEE_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Shadows_Quest_MainEE_FindNerosBook, 3200),
    (LocationName.Shadows_Quest_MainEE_DefeatShadowman, 3201),
    (LocationName.Shadows_Quest_MainEE_DefeatGiantSpaceSquid, 3202),
    (LocationName.Shadows_Quest_MainEE_Victory, 3203),
]]

Shadows_Quest_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Shadows_Quest_AllSpareChangeCollected, 3500),
    (LocationName.Shadows_Quest_LaundryTicket, 3501),
]]

Shadows_Doughnut_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Shadows_Quest_DoughnutMines, 3513),
]]

# Shadows_Widows_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
#     (LocationName.Shadows_Quest_GrowGum, 3510),
# ]]

Shadows_RayGun_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Shadows_Quest_MargwaHead, 3511),
]]

Shadows_LilArnies_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Shadows_Quest_LilArnies_Upgrade, 3512),
]]

Shadows_Craftable_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.MISC, row[1]) for row in [
    (LocationName.Shadows_Craftable_CivilProtector_Fuse1, 3310),
    (LocationName.Shadows_Craftable_CivilProtector_Fuse2, 3311),
    (LocationName.Shadows_Craftable_CivilProtector_Fuse3, 3312),
    (LocationName.Shadows_Craftable_ShieldPartDolly, 3320),
    (LocationName.Shadows_Craftable_ShieldPartDoor, 3321),
    (LocationName.Shadows_Craftable_ShieldPartClamp, 3322),
]]

Shadows_ApothiconServant_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.MISC, row[1]) for row in [
    (LocationName.Shadows_Craftable_ApothiconServant_MargwaHeart, 3300),
    (LocationName.Shadows_Craftable_ApothiconServant_MargwaTentacle, 3301),
    (LocationName.Shadows_Craftable_ApothiconServant_Xenomatter, 3302),
]]

Shadows_Quest_Music_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Shadows_Quest_Music_SnakeskinBoots, 3400),
    (LocationName.Shadows_Quest_Music_ColdHardCash, 3401),
]]

Shadows_Quest_Radio_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Shadows_Quest_Radio_Staminup, 3410),
    (LocationName.Shadows_Quest_Radio_MagicianRitual, 3411),
    (LocationName.Shadows_Quest_Radio_CanalsPerk, 3412),
    (LocationName.Shadows_Quest_Radio_DetectiveRitual, 3413),
    (LocationName.Shadows_Quest_Radio_FootlightBuildableTable, 3414),
    (LocationName.Shadows_Quest_Radio_FemmeFataleRitual, 3415),
    (LocationName.Shadows_Quest_Radio_WaterfrontPerk, 3416),
    (LocationName.Shadows_Quest_Radio_BoxerRitual, 3417),
    (LocationName.Shadows_Quest_Radio_CanalsTrain, 3420),
    (LocationName.Shadows_Quest_Radio_FootlightTrain, 3421),
    (LocationName.Shadows_Quest_Radio_WaterfrontTrain, 3422),
    (LocationName.Shadows_Quest_Radio_RiftPortal, 3425),
]]

# Zetsubou No Shima

Zetsubou_Round_Locations = gen_map_round_locations(Maps.Zetsubou_Map_String, 99)

Zetsubou_Quest_MainQuest_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Zetsubou_Quest_MainQuest_Bucket, 5100),
    (LocationName.Zetsubou_Quest_MainQuest_Bunker, 5101),
    (LocationName.Zetsubou_Quest_MainQuest_Power, 5102),
    (LocationName.Zetsubou_Quest_MainQuest_Pap, 5103),
    (LocationName.Zetsubou_Quest_AllSpareChangeCollected, 5109),
]]

Zetsubou_Quest_MainEE_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Zetsubou_Quest_MainEE_AirplaneAmmo, 5110),
    (LocationName.Zetsubou_Quest_MainEE_AirplaneDown, 5111),
    (LocationName.Zetsubou_Quest_MainEE_Gear2, 5112),
    (LocationName.Zetsubou_Quest_MainEE_Gear3, 5113),
    (LocationName.Zetsubou_Quest_MainEE_FreeTakeo, 5114),
    (LocationName.Zetsubou_Quest_MainEE_Victory, 5115),
]]

Zetsubou_Quest_KT4_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Zetsubou_Quest_KT4_Vial, 5120),
    (LocationName.Zetsubou_Quest_KT4_Flower, 5121),
    (LocationName.Zetsubou_Quest_KT4_Spider, 5122),
]]

Zetsubou_Quest_Masamune_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Zetsubou_Quest_Masamune_Vial, 5123),
    (LocationName.Zetsubou_Quest_Masamune_Flower, 5124),
    (LocationName.Zetsubou_Quest_Masamune_Spider, 5125),
    (LocationName.Zetsubou_Quest_Masamune_Acquired, 5126),
]]

Zetsubou_Quest_Skull_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Zetsubou_Quest_Skull_Cleanse, 5130),
    (LocationName.Zetsubou_Quest_Skull_CleanseAll, 5131),
    (LocationName.Zetsubou_Quest_Skull_Survive, 5132),
]]

Zetsubou_Quest_Challenges_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Zetsubou_Quest_Challenge_1, 5140),
    (LocationName.Zetsubou_Quest_Challenge_2, 5141),
    (LocationName.Zetsubou_Quest_Challenge_3, 5142),
    (LocationName.Zetsubou_Quest_Challenge_All, 5143),
]]

Zetsubou_Craftable_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Zetsubou_Craftable_Gasmask_Visor, 5200),
    (LocationName.Zetsubou_Craftable_Gasmask_Filter, 5201),
    (LocationName.Zetsubou_Craftable_Gasmask_Strap, 5202),
    (LocationName.Zetsubou_Craftable_ShieldPartDolly, 5203),
    (LocationName.Zetsubou_Craftable_ShieldPartDoor, 5204),
    (LocationName.Zetsubou_Craftable_ShieldPartClamp, 5205),
]]

Zetsubou_Quest_Music_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Zetsubou_Quest_Music_DeadFlowers, 5300),
]]

Zetsubou_Quest_Radio_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Zetsubou_Quest_Radio_LabA, 5310),
    (LocationName.Zetsubou_Quest_Radio_LabB, 5311),
    (LocationName.Zetsubou_Quest_Radio_Docks, 5312),
    (LocationName.Zetsubou_Quest_Radio_KT4Station, 5313),
    (LocationName.Zetsubou_Quest_Radio_PurpleWater, 5314),
]]

# Gorod Krovi

GorodKrovi_Round_Locations = gen_map_round_locations(Maps.GorodKrovi_Map_String, 99)

GorodKrovi_Quest_MainQuest_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.GorodKrovi_Quest_MainQuest_Dragonride_Transmitter, 4100),
    (LocationName.GorodKrovi_Quest_MainQuest_Dragonride_Codes, 4101),
    (LocationName.GorodKrovi_Quest_MainQuest_Dragonride_Map, 4102),
    (LocationName.GorodKrovi_Quest_MainQuest_Dragonride_Repaired, 4103),
    (LocationName.GorodKrovi_Quest_MainQuest_Power, 4104),
    (LocationName.GorodKrovi_Quest_AllSpareChangeCollected, 4109),
]]

GorodKrovi_Quest_MainEE_Locations =  [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.GorodKrovi_Quest_MainEE_CollectTrophies, 4110),
    (LocationName.GorodKrovi_Quest_MainEE_ChargeGenerator, 4111),
    (LocationName.GorodKrovi_Quest_MainEE_PnuematicTubes, 4112),
    (LocationName.GorodKrovi_Quest_MainEE_EnterSophiasPassword, 4113),
    (LocationName.GorodKrovi_Quest_MainEE_CompleteScenarios, 4114),
    (LocationName.GorodKrovi_Quest_MainEE_DeliverPowerCore, 4115),
    (LocationName.GorodKrovi_Quest_MainEE_SlayDragon, 4116),
    (LocationName.GorodKrovi_Quest_MainEE_DefeatNikolai, 4117),
    (LocationName.GorodKrovi_Quest_MainEE_Victory, 4118),
]]

GorodKrovi_Quest_DragonStrikes = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.GorodKrovi_Quest_Dragonstrikes_Acquire, 4120),
]]

GorodKrovi_Quest_DragonStrikes_Upgraded = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.GorodKrovi_Quest_Dragonstrikes_Upgrade, 4121),
]]

GorodKrovi_Quest_DragonGauntlets_Early = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.GorodKrovi_Quest_DragonGauntlets_AcquireEgg, 4130),
    (LocationName.GorodKrovi_Quest_DragonGauntlets_WarmEgg, 4131),
    (LocationName.GorodKrovi_Quest_DragonGauntlets_C1Napalm, 4132),
]]

GorodKrovi_Quest_DragonGauntlets_Late = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.GorodKrovi_Quest_DragonGauntlets_C2Collatoral, 4133),
    (LocationName.GorodKrovi_Quest_DragonGauntlets_C3Knife, 4134),
    (LocationName.GorodKrovi_Quest_DragonGauntlets_IncubateEgg, 4135),
    (LocationName.GorodKrovi_Quest_DragonGauntlets_HatchEgg, 4136),
]]


GorodKrovi_Quest_TiamatsMaw = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.GorodKrovi_Quest_TiamatsMaw_Kills, 4140),
    (LocationName.GorodKrovi_Quest_TiamatsMaw_Bathe, 4141),
    (LocationName.GorodKrovi_Quest_TiamatsMaw_Runes, 4142),
    (LocationName.GorodKrovi_Quest_TiamatsMaw_Upgrade, 4143),
]]

GorodKrovi_Quest_SideEE = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.GorodKrovi_Quest_SideEE_DragonWings, 4150),
    (LocationName.GorodKrovi_Quest_SideEE_ManglerHelm, 4151),
    (LocationName.GorodKrovi_Quest_SideEE_ValkyrieHelm, 4152),
]]

GorodKrovi_Quest_Challenges = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.GorodKrovi_Quest_Challenges_1, 4160),
    (LocationName.GorodKrovi_Quest_Challenges_2, 4161),
    (LocationName.GorodKrovi_Quest_Challenges_3, 4162),
    (LocationName.GorodKrovi_Quest_UpgradeMonkeyBombs, 4163),
]]

GorodKrovi_Craftable_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.MISC, row[1]) for row in [
    (LocationName.GorodKrovi_Craftable_ShieldPartDoor, 4200),
    (LocationName.GorodKrovi_Craftable_ShieldPartDolly, 4201),
    (LocationName.GorodKrovi_Craftable_ShieldPartClamp, 4202),
]]

GorodKrovi_Quest_Music_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.GorodKrovi_Quest_Music_DeadEnded, 4300),
    (LocationName.GorodKrovi_Quest_Music_AceOfSpades, 4301),
]]

GorodKrovi_Quest_Radio_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.GorodKrovi_Quest_Radio_Bunker, 4310),
    (LocationName.GorodKrovi_Quest_Radio_Hatchery, 4311),
    (LocationName.GorodKrovi_Quest_Radio_SupplyDepot, 4312),
    (LocationName.GorodKrovi_Quest_Radio_DragonCommand, 4313),
    (LocationName.GorodKrovi_Quest_Radio_TankFactory, 4314),
]]

# Revelations

Revelations_Round_Locations = gen_map_round_locations(Maps.Revelations_Map_String, 99)

Revelations_Quest_MainQuest_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Revelations_Quest_MainQuest_Portal, 6100),
    (LocationName.Revelations_Quest_MainQuest_AllPortals, 6101),
    (LocationName.Revelations_Quest_MainQuest_PackAPunch, 6102),
    (LocationName.Revelations_Quest_AllSpareChangeCollected, 6109),
]]

Revelations_Quest_MainEE_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Revelations_Quest_MainEE_Stones, 6200),
    (LocationName.Revelations_Quest_MainEE_Reel1, 6201),
    (LocationName.Revelations_Quest_MainEE_Reel2, 6202),
    (LocationName.Revelations_Quest_MainEE_Reel3, 6203),
    (LocationName.Revelations_Quest_MainEE_Sophia, 6204),
    (LocationName.Revelations_Quest_MainEE_Book, 6205),
    (LocationName.Revelations_Quest_MainEE_Eggs, 6206),
    (LocationName.Revelations_Quest_MainEE_Runes, 6207),
    (LocationName.Revelations_Quest_MainEE_Gauntlet, 6208),
    (LocationName.Revelations_Quest_MainEE_SummoningKey, 6209),
    (LocationName.Revelations_Quest_MainEE_BossFight, 6210),
    (LocationName.Revelations_Quest_MainEE_Victory, 6211),
]]

Revelations_Quest_Mask_Wolf_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Revelations_Quest_SideEE_HatWolf, 6600),
]]

Revelations_Quest_Mask_Siegfried_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Revelations_Quest_SideEE_HatSiegfried, 6610),
]]

Revelations_Quest_Mask_King_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Revelations_Quest_SideEE_HatKing, 6620),
    (LocationName.Revelations_Quest_SideEE_HatKing2, 6621),
]]

Revelations_Quest_Mask_Fury_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Revelations_Quest_SideEE_HatFury, 6630),
]]

Revelations_Quest_Mask_Keeper_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Revelations_Quest_SideEE_HatKeeper, 6640),
    (LocationName.Revelations_Quest_SideEE_HatKeeper2, 6641),
]]

Revelations_Quest_Mask_Margwa_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Revelations_Quest_SideEE_HatMargwa, 6650),
    (LocationName.Revelations_Quest_SideEE_HatMargwa2, 6651),
]]

Revelations_Quest_Mask_Apothigod_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Revelations_Quest_SideEE_HatApothigod, 6660),
    (LocationName.Revelations_Quest_SideEE_HatApothigod2, 6661),
    (LocationName.Revelations_Quest_SideEE_HatApothigod3, 6662),
]]

Revelations_Quest_Masks_Locations = (Revelations_Quest_Mask_Wolf_Locations + Revelations_Quest_Mask_Siegfried_Locations
    + Revelations_Quest_Mask_King_Locations + Revelations_Quest_Mask_Fury_Locations
    + Revelations_Quest_Mask_Keeper_Locations + Revelations_Quest_Mask_Margwa_Locations
    + Revelations_Quest_Mask_Apothigod_Locations)

Revelations_Craftable_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.CRAFTABLE_PART, row[1]) for row in [
    (LocationName.Revelations_Craftable_ShieldPartDolly, 6310),
    (LocationName.Revelations_Craftable_ShieldPartDoor, 6311),
    (LocationName.Revelations_Craftable_ShieldPartClamp, 6312),
    (LocationName.Revelations_Craftable_KeeperProtector_Totem, 6313),
    (LocationName.Revelations_Craftable_KeeperProtector_Head, 6314),
    (LocationName.Revelations_Craftable_KeeperProtector_Gem, 6315),
]]

Revelations_Quest_Challenges = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Revelations_Quest_Challenges_1, 6320),
    (LocationName.Revelations_Quest_Challenges_2, 6321),
    (LocationName.Revelations_Quest_Challenges_3, 6322),
    (LocationName.Revelations_Quest_Challenges_All, 6323),
]]

Revelations_Quest_Weapons = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Revelations_Quest_ApothiconServant, 6330),
    (LocationName.Revelations_Quest_Arnies, 6331),
]]

Revelations_Quest_SideEE_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Revelations_Quest_SideEE_Writing, 6500),
]]

Revelations_Quest_Music_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Revelations_Quest_Music_TheGift, 6400),
]]

Revelations_Quest_Radio_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Revelations_Quest_Radio_MobCafereria, 6410),
    (LocationName.Revelations_Quest_Radio_MobDesk, 6411),
    (LocationName.Revelations_Quest_Radio_MobBed, 6412),
    (LocationName.Revelations_Quest_Radio_OriginsShelf, 6413),
    (LocationName.Revelations_Quest_Radio_VerrucktTubes, 6414),
    (LocationName.Revelations_Quest_Radio_VerrucktShelf, 6415),
    (LocationName.Revelations_Quest_Radio_VerrucktTree, 6416),
    (LocationName.Revelations_Quest_Radio_KinoShelf, 6417),
    (LocationName.Revelations_Quest_Radio_CastleCasket, 6418),
    (LocationName.Revelations_Quest_Radio_ShangStatue, 6419),
    (LocationName.Revelations_Quest_Radio_ShangPillar, 6420),
    (LocationName.Revelations_Quest_Radio_ShangStaminup, 6421),
    (LocationName.Revelations_Quest_Radio_ShangStairs, 6422),
]]

Revelations_Quest_Wisp_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Revelations_Quest_Wisp_Monty1_Spawn, 6450),
    (LocationName.Revelations_Quest_Wisp_Monty1_Origins, 6451),
    (LocationName.Revelations_Quest_Wisp_Monty1_Castle, 6452),
    (LocationName.Revelations_Quest_Wisp_Monty1_Verruckt, 6453),
    (LocationName.Revelations_Quest_Wisp_Monty2_Spawn, 6454),
    (LocationName.Revelations_Quest_Wisp_Monty2_Origins, 6455),
    (LocationName.Revelations_Quest_Wisp_Monty2_Castle, 6456),
    (LocationName.Revelations_Quest_Wisp_Monty2_Verruckt, 6457),
    (LocationName.Revelations_Quest_Wisp_Monty3_Spawn, 6458),
    (LocationName.Revelations_Quest_Wisp_Monty3_Origins, 6459),
    (LocationName.Revelations_Quest_Wisp_Monty3_Castle, 6460),
    (LocationName.Revelations_Quest_Wisp_Monty3_Verruckt, 6461),
    (LocationName.Revelations_Quest_Wisp_Shadow1_Spawn, 6462),
    (LocationName.Revelations_Quest_Wisp_Shadow1_Origins, 6463),
    (LocationName.Revelations_Quest_Wisp_Shadow1_Castle, 6464),
    (LocationName.Revelations_Quest_Wisp_Shadow1_Verruckt, 6465),
    (LocationName.Revelations_Quest_Wisp_Shadow2_Spawn, 6466),
    (LocationName.Revelations_Quest_Wisp_Shadow2_Origins, 6467),
    (LocationName.Revelations_Quest_Wisp_Shadow2_Castle, 6468),
    (LocationName.Revelations_Quest_Wisp_Shadow2_Verruckt, 6469),
    (LocationName.Revelations_Quest_Wisp_Player0, 6470),
    (LocationName.Revelations_Quest_Wisp_Player1, 6471),
    (LocationName.Revelations_Quest_Wisp_Player2, 6472),
    (LocationName.Revelations_Quest_Wisp_Player3, 6473),
    (LocationName.Revelations_Quest_Wisp_Player4, 6474),
    (LocationName.Revelations_Quest_Wisp_Player5, 6475),
    (LocationName.Revelations_Quest_Wisp_Player6, 6476),
    # (LocationName.Revelations_Quest_Wisp_Player7, 6477), #* only dempsey and nikolai
]]

# == Zombie Chronicles ==

# Nacht der Untoten
Nacht_Round_Locations = gen_map_round_locations(Maps.Nacht_Map_String, 99)

Nacht_Quest_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Nacht_Quest_Sam, 14100),
    (LocationName.Nacht_Achi_Closed, 14101),
]]

Nacht_Quest_Music_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Nacht_Quest_Music_Undone, 14200),
]]

Nacht_Quest_Radio_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Nacht_Quest_Radio_Monty, 14210),
]]

# Kino der Toten
Kino_Round_Locations = gen_map_round_locations(Maps.Kino_Map_String, 99)

Kino_Quest_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Kino_Quest_Power, 11100),
    (LocationName.Kino_Quest_Movie, 11102),
    # (LocationName.Kino_Quest_Sorrow, 11103),
    (LocationName.Kino_Quest_AllSpareChangeCollected, 11104),
    (LocationName.Kino_Quest_ToyRocket, 11105),
]]

Kino_Quest_Music_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Kino_Quest_Music_115, 11200),
]]

Kino_Quest_Radio_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Kino_Quest_Radio_Alley, 11210),
    (LocationName.Kino_Quest_Radio_Chandelier, 11211),
    (LocationName.Kino_Quest_Radio_Balcony, 11212),
]]

# Moon
Moon_Round_Locations = gen_map_round_locations(Maps.Moon_Map_String, 99)

Moon_Universal_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Moon_Quest_Power, 12100),
    (LocationName.Moon_SafeLanding, 12101),
    (LocationName.Moon_Quest_AllSpareChangeCollected, 12102),
]]

Moon_Hacker_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Moon_Hacker_Excavator, 12200),
    (LocationName.Moon_Hacker_Window, 12201),
    (LocationName.Moon_Hacker_MysteryBox, 12202),
    (LocationName.Moon_Hacker_PackAPunch, 12203),
]]

Moon_Quest_MainEE_Part1_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Moon_Quest_MainEE_SamanthaSays, 12300),
    (LocationName.Moon_Quest_MainEE_Buttons, 12301),
]]

Moon_Quest_MainEE_Part2_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Moon_Quest_MainEE_VrilSphere, 12310),
    (LocationName.Moon_Quest_MainEE_OpenMPD, 12311),
]]

Moon_Quest_MainEE_Computer_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Moon_Quest_MainEE_PlatesComputer, 12320),
    (LocationName.Moon_Quest_MainEE_PlugComputer, 12321),
]]

Moon_Quest_MainEE_Part3_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Moon_Quest_MainEE_RichtofenComputer, 12322),
    (LocationName.Moon_Quest_MainEE_FillMPD, 12323),
    (LocationName.Moon_Quest_MainEE_SwapSouls, 12324),
    (LocationName.Moon_Quest_MainEE_NukeTheEarth, 12325),
    (LocationName.Moon_Quest_MainEE_Victory, 12326),
]]

Moon_Quest_SpaceDog_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Moon_Quest_SpaceDog_WaveGun, 12400),
    (LocationName.Moon_Quest_SpaceDog_WaveGun2, 12401),
    (LocationName.Moon_Quest_SpaceDog_WaveGun3, 12402),
    (LocationName.Moon_Quest_SpaceDog_Zombies, 12403),
    (LocationName.Moon_Quest_SpaceDog_Hellhounds, 12404),
]]

Moon_Quest_Music_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Moon_Quest_Music_ComingHome, 12500),
    (LocationName.Moon_Quest_Music_ComingHome8Bit, 12501),
    (LocationName.Moon_Quest_Music_ReDamned, 12502),
    (LocationName.Moon_Quest_Music_Pareidolia8Bit, 12503),
]]

Moon_Quest_Radio_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Moon_Quest_Radio_OutsideReceivingBay, 12510),
    (LocationName.Moon_Quest_Radio_Lab, 12511),
    (LocationName.Moon_Quest_Radio_Tunnel6, 12512),
    (LocationName.Moon_Quest_Radio_Crane, 12513),
    (LocationName.Moon_Quest_Radio_Biodome, 12514),
    (LocationName.Moon_Quest_Radio_ReceivingBay, 12515),
]]

Moon_Quest_Reel_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Moon_Quest_Reel1, 12520),
    (LocationName.Moon_Quest_Reel2, 12521),
    (LocationName.Moon_Quest_Reel3, 12522),
    (LocationName.Moon_Quest_Reel4, 12523),
    (LocationName.Moon_Quest_Reel5, 12524),
    (LocationName.Moon_Quest_Reel6, 12525),
]]

# Origins
Origins_Round_Locations = gen_map_round_locations(Maps.Origins_Map_String, 99)

Origins_Craftable_Locations_Early = [LocationData(row[0], BO3ZombiesLocationCategory.CRAFTABLE_PART, row[1]) for row in [
    (LocationName.Origins_Craftable_MaxisDronePart_Brain, 13110),
]]

Origins_Craftable_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.CRAFTABLE_PART, row[1]) for row in [
    (LocationName.Origins_Craftable_ShieldPartDolly, 13100),
    (LocationName.Origins_Craftable_ShieldPartClamp, 13101),
    (LocationName.Origins_Craftable_ShieldPartDoor, 13102),
    (LocationName.Origins_Craftable_GramophonePart_Player, 13103),
    (LocationName.Origins_Craftable_GramophonePart_BlankDisc, 13104),
    (LocationName.Origins_Craftable_GramophonePart_FireDisc, 13105),
    (LocationName.Origins_Craftable_GramophonePart_WindDisc, 13106),
    (LocationName.Origins_Craftable_GramophonePart_IceDisc, 13107),
    (LocationName.Origins_Craftable_GramophonePart_LightningDisc, 13108),
    (LocationName.Origins_Craftable_MaxisDronePart_Body, 13109),
    (LocationName.Origins_Craftable_MaxisDronePart_Engine, 13111),
]]

Origins_Generators = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Origins_Generators_Any, 13200),
    (LocationName.Origins_Generators_Three, 13201),
    (LocationName.Origins_Generators_All, 13202),
]]

Origins_Staff_Wind = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Origins_Staff_Wind_Craft, 13300),
    (LocationName.Origins_Staff_Wind_Puzzle1, 13301),
    (LocationName.Origins_Staff_Wind_Puzzle2, 13302),
    (LocationName.Origins_Staff_Wind_Upgrade, 13304),
]]

Origins_Staff_Fire = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Origins_Staff_Fire_Craft, 13310),
    (LocationName.Origins_Staff_Fire_Puzzle1, 13311),
    (LocationName.Origins_Staff_Fire_Puzzle2, 13312),
    (LocationName.Origins_Staff_Fire_Upgrade, 13314),
]]

Origins_Staff_Lightning = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Origins_Staff_Lightning_Craft, 13320),
    (LocationName.Origins_Staff_Lightning_Puzzle1, 13321),
    (LocationName.Origins_Staff_Lightning_Puzzle2, 13322),
    (LocationName.Origins_Staff_Lightning_Upgrade, 13324),
]]

Origins_Staff_Ice = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Origins_Staff_Ice_Craft, 13330),
    (LocationName.Origins_Staff_Ice_Puzzle1, 13331),
    (LocationName.Origins_Staff_Ice_Puzzle2, 13332),
    (LocationName.Origins_Staff_Ice_Upgrade, 13334),
]]

Origins_MainEE_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Origins_Quest_MainEE_Upgraded, 13400),
    (LocationName.Origins_Quest_MainEE_Placed, 13401),
    (LocationName.Origins_Quest_MainEE_OpenHole, 13402),
    (LocationName.Origins_Quest_MainEE_InvisZombie, 13403),
    (LocationName.Origins_Quest_MainEE_Punch, 13404),
    (LocationName.Origins_Quest_MainEE_Samantha, 13405),
]]

Origins_SoulBoxes = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Origins_SoulBox_One, 13500),
    (LocationName.Origins_SoulBox_All, 13501),
]]

Origins_Music_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Origins_Quest_Music_Archangel, 13600),
    (LocationName.Origins_Quest_Music_Aether, 13601),
    (LocationName.Origins_Quest_Music_ShepherdOfFire, 13602),
]]

Origins_Radio_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Origins_Quest_Radio_ShivaTable, 13610),
    (LocationName.Origins_Quest_Radio_RK5Table, 13611),
    (LocationName.Origins_Quest_Radio_Workshop, 13612),
    (LocationName.Origins_Quest_Radio_Odin, 13613),
    (LocationName.Origins_Quest_Radio_Thor, 13614),
    (LocationName.Origins_Quest_Radio_Freya, 13615),
    (LocationName.Origins_Quest_Radio_ShivaShelf, 13616),
]]

Origins_Quest_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Origins_Quest_AllSpareChangeCollected, 13709),
]]

# == Workshop ==
# Wanted

Wanted_Round_Locations = gen_map_round_locations(Maps.Wanted_Map_String, 99)

Wanted_Quest_MainQuest_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Wanted_Quest_MainQuest_CollectSkulls, 20100),
    (LocationName.Wanted_Quest_MainQuest_WeaponSafe, 20102),
]]

Wanted_Quest_MainEE_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Wanted_Quest_MainEE_Church, 20200),
    (LocationName.Wanted_Quest_MainEE_TotemPole, 20201),
    (LocationName.Wanted_Quest_MainEE_Leroy, 20202),
    (LocationName.Wanted_Quest_MainEE_Victory, 20203),
]]

Wanted_Quest_Weapons = [LocationData(row[0], BO3ZombiesLocationCategory.QUEST, row[1]) for row in [
    (LocationName.Wanted_Weapon_Magmagat, 20300),
    (LocationName.Wanted_Weapon_GreatScott, 20301),
]]

Wanted_Craftable_Locations = [LocationData(row[0], BO3ZombiesLocationCategory.CRAFTABLE_PART, row[1]) for row in [
    (LocationName.Wanted_Craftable_ShieldPartDolly, 20400),
    (LocationName.Wanted_Craftable_ShieldPartDoor, 20401),
    (LocationName.Wanted_Craftable_ShieldPartClamp, 20402),
    (LocationName.Wanted_Craftable_AcidgatUpgradePartEngine, 20403),
    (LocationName.Wanted_Craftable_AcidgatUpgradePartAcid, 20404),
]]

early_locations =  [LocationData(row[0], row[1], row[2]) for row in [
    (LocationName.RepairWindows_5, BO3ZombiesLocationCategory.MISC, 9001),
]]

Stat_Locations = []
for map_name in Maps.all_maps:
    Stat_Locations.extend(gen_map_stat_locations(map_name))

all_locations = (
    # The Giant
    TheGiant_Round_Locations + TheGiant_Quest_Locations + TheGiant_Pap + TheGiant_MonkeyBomb + TheGiant_Quest_Music_Locations
    # Castle
    + Castle_Round_Locations + Castle_Quest_Locations + Castle_Quest_Music_Locations + Castle_Craftable_Locations + Castle_DG4_Locations
    + Castle_Quest_ElementalBow_Fire_Locations + Castle_Quest_ElementalBow_Void_Locations + Castle_Quest_ElementalBow_Storm_Locations + Castle_Quest_ElementalBow_Wolf_Locations
    + Castle_Quest_MainEE_Locations
    # Shadows
    + Shadows_Round_Locations + Shadows_Quest_Locations + Shadows_Doughnut_Locations + Shadows_Craftable_Locations + Shadows_ApothiconServant_Locations + Shadows_Quest_Music_Locations + Shadows_LilArnies_Locations
    + Shadows_Quest_MainQuest_Locations + Shadows_Quest_ApothiconSword_Locations + Shadows_Quest_ApothiconSword_Upgrade_Locations + Shadows_RayGun_Locations
    + Shadows_Quest_MainEE_Locations
    # Zetsubou
    + Zetsubou_Round_Locations + Zetsubou_Craftable_Locations + Zetsubou_Quest_Music_Locations
    + Zetsubou_Quest_MainQuest_Locations + Zetsubou_Quest_MainEE_Locations + Zetsubou_Quest_Challenges_Locations
    + Zetsubou_Quest_KT4_Locations + Zetsubou_Quest_Masamune_Locations + Zetsubou_Quest_Skull_Locations
    # Gorod Krovi
    + GorodKrovi_Round_Locations + GorodKrovi_Craftable_Locations + GorodKrovi_Quest_MainEE_Locations + GorodKrovi_Quest_SideEE + GorodKrovi_Quest_Music_Locations
    + GorodKrovi_Quest_DragonStrikes + GorodKrovi_Quest_DragonStrikes_Upgraded + GorodKrovi_Quest_DragonGauntlets_Early + GorodKrovi_Quest_DragonGauntlets_Late + GorodKrovi_Quest_Challenges + GorodKrovi_Quest_TiamatsMaw
    + GorodKrovi_Quest_MainQuest_Locations
    # Revelations
    + Revelations_Round_Locations + Revelations_Craftable_Locations + Revelations_Quest_Music_Locations
    + Revelations_Quest_MainQuest_Locations + Revelations_Quest_MainEE_Locations + Revelations_Quest_Challenges
    + Revelations_Quest_SideEE_Locations + Revelations_Quest_Masks_Locations + Revelations_Quest_Weapons
    # Nacht der Untoten
    + Nacht_Round_Locations
    + Nacht_Quest_Locations + Nacht_Quest_Music_Locations
    # Kino der Toten
    + Kino_Round_Locations
    + Kino_Quest_Locations + Kino_Quest_Music_Locations
    # Moon
    + Moon_Round_Locations
    + Moon_Universal_Locations + Moon_Hacker_Locations + Moon_Quest_Music_Locations
    + Moon_Quest_MainEE_Part1_Locations + Moon_Quest_MainEE_Part2_Locations + Moon_Quest_MainEE_Computer_Locations + Moon_Quest_MainEE_Part3_Locations
    + Moon_Quest_SpaceDog_Locations
    # Origins
    + Origins_Round_Locations + Origins_Craftable_Locations + Origins_Craftable_Locations_Early
    + Origins_Generators + Origins_SoulBoxes + Origins_Music_Locations
    + Origins_Staff_Fire + Origins_Staff_Ice + Origins_Staff_Lightning + Origins_Staff_Wind
    + Origins_MainEE_Locations
    # === Modded Maps ===
    # Wanted
    + Wanted_Round_Locations + Wanted_Craftable_Locations
    + Wanted_Quest_MainQuest_Locations + Wanted_Quest_Weapons + Wanted_Quest_MainEE_Locations
    + early_locations + Stat_Locations)

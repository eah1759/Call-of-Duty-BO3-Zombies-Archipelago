from . import Maps

def gen_round_regions(map):
  # Rounds 10 to 40 in groups of 5
  return [f"{map} Round {i+5}" for i in range(5, 40, 5)]

TheGiant_Courtyard  = "(The Giant) Courtyard"
TheGiant_Open  = "(The Giant) Open the Map"
TheGiant_Pap = "(The Giant) Pack a Punch"
TheGiant_MonkeyBombs = "(The Giant) Monkey Bombs"
TheGiant_Round_Regions = gen_round_regions(Maps.The_Giant_Map_String)

Castle_Gondola = "(Der Eisendrache) Gondola"
Castle_Open  = "(Der Eisendrache) Open the Map"
Castle_MainEE = "(Der Eisendrache) Main Easter Egg"
Castle_DG4 = "(Der Eisendrache) DG4 Parts"
Castle_Upgraded = "(Der Eisendrache) Upgraded Weapons"
Castle_BossFight = "(Der Eisendrache) Boss Fight"
Castle_Bow_Easy = "(Der Eisendrache) Bow Easy"
Castle_Bow_Hard = "(Der Eisendrache) Bow Hard"
Castle_Round_Regions = gen_round_regions(Maps.Castle_Map_String)

Shadows_Alleyway = "(Shadows of Evil) Alleyway"
Shadows_Open  = "(Shadows of Evil) Open the Map"
Shadows_Servant = "(Shadows of Evil) Apothican Servant - Late Drops"
Shadows_Widows = "(Shadows of Evil) Widows Wine Required"
Shadows_RayGun = "(Shadows of Evil) Ray Gun Required"
Shadows_Arnies = "(Shadows of Evil) Li'l Arnies Required"
Shadows_Upgraded = "(Shadows of Evil) Upgraded Weapons"
Shadows_MainEE = "(Shadows of Evil) Main Easter Egg"
Shadows_Sword_Early = "(Shadows of Evil) Early Sword"
Shadows_Sword_Late = "(Shadows of Evil) Late Sword"
Shadows_Margwa_Head = "(Shadows of Evil) Margwa Head"
Shadows_Round_Regions = gen_round_regions(Maps.Shadows_Map_String)

Zetsubou_Beach = "(Zetsubou No Shima) Beach"
Zetsubou_Open  = "(Zetsubou No Shima) Open the Map"
Zetsubou_Masamune = "(Zetsubou No Shima) Masamune"
Zetsubou_MainEE = "(Zetsubou No Shima) Main Easter Egg"
Zetsubou_Challenges_Early = "(Zetsubou No Shima) Challenges Early"
Zetsubou_Challenges_Late = "(Zetsubou No Shima) Challenges Late"
Zetsubou_Round_Regions = gen_round_regions(Maps.Zetsubou_Map_String)

Gorod_Trenches = "(Gorod Krovi) Trenches"
Gorod_Bunker = "(Gorod Krovi) Bunker"
Gorod_Wings = "(Gorod Krovi) Dragon Wings"
Gorod_Valkyrie = "(Gorod Krovi) Valkyrie Helm"
Gorod_EarlyDragon = "(Gorod Krovi) Early Dragon Gauntlets"
Gorod_Open  = "(Gorod Krovi) Open the Map"
Gorod_Shield = "(Gorod Krovi) Shield Required"
Gorod_Upgraded = "(Gorod Krovi) Upgraded Weapons"
Gorod_MonkeyBombs = "(Gorod Krovi) Monkey Bombs Required"
Gorod_MainEE = "(Gorod Krovi) Main Easter Egg"
Gorod_Challenges_Early = "(Gorod Krovi) Challenges Early"
Gorod_Challenges_Late = "(Gorod Krovi) Challenges Late"
Gorod_Round_Regions = gen_round_regions(Maps.GorodKrovi_Map_String)

Revelations_House = "(Revelations) House"
Revelations_Open  = "(Revelations) Open the Map"
Revelations_MainEE = "(Revelations) Main Easter Egg"
Revelations_Upgraded = "(Revelations) Upgraded Weapons"
Revelations_Challenges = "(Revelations) Complete Challenges"
Revelations_Apothicon_Upgrade = "(Revelations) Apothicon Upgrade"
Revelations_Arnies_Upgrade = "(Revelations) Arnies Upgrade"
Revelations_Wisps_Early = "(Revelations) Wisps Early"
Revelations_Wisps_Mid = "(Revelations) Wisps Middle 1"
Revelations_Wisps_Mid2 = "(Revelations) Wisps Middle 2"
Revelations_Wisps_Late = "(Revelations) Wisps Late"
Revelations_Masks_Easy = "(Revelations) Masks Easy"
Revelations_Masks_Medium = "(Revelations) Masks Medium"
Revelations_Masks_Hard = "(Revelations) Masks Hard"
Revelations_Challenges_Early = "(Revelations) Challenges Early"
Revelations_Challenges_Late = "(Revelations) Challenges Late"
Revelations_Round_Regions = gen_round_regions(Maps.Revelations_Map_String)

# == Zombie Chronicles ==

Nacht_Entrance = "(Nacht der Toten) Entrance"
Nacht_Open = "(Nacht der Toten) Open the Map"
Nacht_Round_Regions = gen_round_regions(Maps.Nacht_Map_String)

Kino_Entrance = "(Kino der Toten) Entrance"
Kino_Open = "(Kino der Toten) Open the Map"
Kino_Round_Regions = gen_round_regions(Maps.Kino_Map_String)

Moon_Entrance = "(Moon) Groom Lake"
Moon_Open = "(Moon) Open the Map"
Moon_MainEE = "(Moon) Main Easter Egg"
Moon_SpaceDog = "(Moon) Space Dog"
Moon_Round_Regions = gen_round_regions(Maps.Moon_Map_String)

Origins_Entrance = "(Origins) Entrance"
Origins_Open = "(Origins) Open the Map"
Origins_Crazy_Place = "(Origins) Crazy Place"
Origins_Staff_Upgrades = "(Origins) Staff Upgrade"
Origins_MainEE = "(Origins) Main Easter Egg"
Origins_SoulBoxAny = "(Origins) Any Soul Box"
Origins_SoulBoxAll = "(Origins) All 4 Soul Boxes"
Origins_Round_Regions = gen_round_regions(Maps.Origins_Map_String)

# == Modded Maps ==

Wanted_Town = "(Wanted) Town"
Wanted_Open  = "(Wanted) Open the Map"
Wanted_MainEE = "(Wanted) Main Easter Egg"
Wanted_Round_Regions = gen_round_regions(Maps.Wanted_Map_String)

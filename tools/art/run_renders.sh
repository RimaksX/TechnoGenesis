#!/bin/bash
cd /tmp/claude-0/-home-user-TechnoGenesis/1448b555-5a64-51cc-a74a-13054d98acab/scratchpad/art_tools
export PYTHONHASHSEED=0
python3 render_all.py jaw_crusher washing_drum magnetic_separator settling_tank tailings_mill acid_plant leaching_reactor &
python3 render_all.py filter_press precipitation_reactor acid_regeneration_column extractor electrolyzer solvent_regenerator attritor &
python3 render_all.py steam_generator autoclave plasma_generator plasma_furnace vacuum_caster solid_fuel_generator steam_turbine &
python3 render_all.py thermal_generator water_pump carbon_capacitor wind_rotor miner solar_panel solar_panel_advanced solar_farm water_splitter &
wait
echo ALLDONE > ../renders/DONE.txt

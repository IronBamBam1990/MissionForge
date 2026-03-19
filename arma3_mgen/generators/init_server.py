"""Generates initServer.sqf — clean, modular, tested.

Uses IBC_fnc_* helper functions from sqf_modules.py.
Every SQF pattern verified working in ARMA 3.
"""

import re
from ..config_schema import MissionConfig, EnemyPosition
from .sqf_modules import helpers as sqf_helpers

DEFAULT_COMPS = {
    "fireteam": ["O_Soldier_TL_F", "O_Soldier_F", "O_Soldier_AR_F", "O_Soldier_GL_F"],
    "squad": ["O_Soldier_SL_F", "O_Soldier_TL_F", "O_Soldier_F", "O_Soldier_AR_F",
              "O_Soldier_GL_F", "O_Soldier_TL_F", "O_Soldier_F", "O_medic_F"],
    "section": ["O_Soldier_SL_F", "O_Soldier_TL_F", "O_Soldier_F", "O_Soldier_F",
                "O_Soldier_AR_F", "O_Soldier_GL_F", "O_Soldier_TL_F", "O_Soldier_F",
                "O_Soldier_F", "O_Soldier_AR_F", "O_soldier_M_F", "O_medic_F"],
}
FORT_CLASSES = {
    "sandbag": "Land_BagFence_Long_F", "barrier": "Land_HBarrier_5_F",
    "bunker": "Land_BagBunker_Small_F", "hesco": "Land_HBarrier_Big_F",
    "razorwire": "Land_Razorwire_F", "concrete": "Land_CncWall4_F",
    "road_barrier": "Land_RoadBarrier_F",
}


def _r(v):
    return str(round(v, 1)) if isinstance(v, float) else str(v)


def _sqf(pos):
    """Config [east, alt, north] → SQF [east, north, 0]"""
    return f"[{round(pos[0], 1)}, {round(pos[2], 1)}, 0]"


def _sqf2d(pos):
    """Config [east, alt, north] → SQF 2D [east, north] (for markers)"""
    return f"[{round(pos[0], 1)}, {round(pos[2], 1)}]"


def _sv(name):
    v = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    return re.sub(r'_+', '_', v).strip('_')


def _get_units(pos: EnemyPosition, fd) -> list[str]:
    if pos.custom_units: return pos.custom_units
    if pos.type == "sniper": return ["O_sniper_F", "O_spotter_F"]
    if pos.type == "mg_nest": return ["O_Soldier_F", "O_Soldier_F"]
    if fd:
        comps = fd.get("compositions", {}).get(pos.composition, {})
        if pos.size in comps:
            u = comps[pos.size]
            return u if isinstance(u, list) else u.get("dismounts", DEFAULT_COMPS.get(pos.size, []))
    return DEFAULT_COMPS.get(pos.size, DEFAULT_COMPS["fireteam"])


def _arr(units):
    return "[" + ",".join(f'"{u}"' for u in units) + "]"


def generate_init_server(config: MissionConfig, enemy_faction_data=None) -> str:
    L = []
    L.append("// IBC ARMA 3 Mission Generator")
    L.append("if (!isServer) exitWith {};")
    L.append("sleep 3;")
    L.append("")

    # ── 1. HELPER FUNCTIONS (must be first — other code depends on them) ──
    L.append(sqf_helpers())
    L.append("")

    # ── 2. TERRAIN SNAP + WATER SAFETY (all units from SQM) ──
    L.append("// Terrain snap all SQM units + move out of water")
    L.append("private _snappedCount = 0; private _waterCount = 0;")
    L.append("{ private _safePos = [getPosATL _x] call IBC_fnc_findSafePos; _x setPosATL [_safePos select 0, _safePos select 1, 0]; _snappedCount = _snappedCount + 1; if !(_safePos isEqualTo (getPosATL _x)) then { _waterCount = _waterCount + 1 }; } forEach allUnits;")
    L.append('diag_log format ["IBC: %1 units snapped, %2 moved from water", _snappedCount, _waterCount];')
    L.append("")

    # ── 3. RADIO SYSTEM ──
    radio_sys = config.radio.system.lower()
    if radio_sys in ("acre2", "acre"):
        L.append("// === ACRE2 Radio System ===")
        L.append("[] spawn { sleep 5; [] call IBC_fnc_setupACRE2; };")
        if config.radio.channels:
            channels_sqf = "[" + ",".join(f'["{ch.get("name","")}", {ch.get("frequency",1)}]' for ch in config.radio.channels) + "]"
            L.append(f"[] spawn {{ sleep 8; {channels_sqf} call IBC_fnc_setACRE2Channels; }};")
        L.append("")
    elif radio_sys in ("tfar", "tf"):
        L.append("// === TFAR Radio System ===")
        L.append("[] spawn { sleep 5; [] call IBC_fnc_setupTFAR; };")
        L.append("")

    sk_min, sk_max = config.opfor.skill_range
    sk_range = round(sk_max - sk_min, 2)

    # ── 4. PLAYER VEHICLES ──
    if config.player_vehicles:
        L.append("// === Player Vehicles ===")
        for vi, pv in enumerate(config.player_vehicles):
            is_air = any(k in pv.vehicle_class.lower() for k in ["heli", "plane", "jet", "vtol"])
            is_armor = any(k in pv.vehicle_class.lower() for k in ["mbt", "apc", "tank", "armor"])
            p = _sqf(pv.position)
            vn = f"_pv{vi}"

            if is_air:
                # Helicopters → find helipad
                L.append(f"// {pv.callsign or pv.vehicle_class} (aircraft → helipad)")
                L.append(f'private _padPos{vi} = [{p}] call IBC_fnc_findHelipad;')
                L.append(f'private {vn} = ["{pv.vehicle_class}", _padPos{vi}, 0, false] call IBC_fnc_spawnVehicle;')
            elif pv.spawn_area == "garage":
                # Cars/trucks → find garage
                L.append(f"// {pv.callsign or pv.vehicle_class} (ground → garage)")
                L.append(f'private _gPos{vi} = [{p}] call IBC_fnc_findGarage;')
                L.append(f'private {vn} = ["{pv.vehicle_class}", _gPos{vi}, 0, false] call IBC_fnc_spawnVehicle;')
            elif pv.spawn_area == "road":
                # On road
                L.append(f"// {pv.callsign or pv.vehicle_class} (ground → road)")
                L.append(f'private {vn} = ["{pv.vehicle_class}", {p}, 200, false] call IBC_fnc_spawnVehicleOnRoad;')
            else:
                # Default: flat terrain
                L.append(f"// {pv.callsign or pv.vehicle_class}")
                L.append(f'private {vn} = ["{pv.vehicle_class}", {p}, 0, false] call IBC_fnc_spawnVehicle;')

            if pv.callsign:
                L.append(f'createMarker ["m_pv{vi}", {_sqf2d(pv.position)}] setMarkerType "mil_dot"; "m_pv{vi}" setMarkerColor "ColorBlue"; "m_pv{vi}" setMarkerText "{pv.callsign}";')
        L.append("")

    # ── 5. AIR SUPPORT ──
    if config.air_support.enabled:
        L.append("// === Air Support ===")
        for i, ac in enumerate(config.air_support.aircraft):
            p = _sqf(ac.position)
            if ac.spawn_type == "fly":
                L.append(f'private _cas{i} = ["{ac.vehicle_class}", {p}, {_r(ac.direction)}] call IBC_fnc_spawnAircraft;')
            else:
                is_air = any(k in ac.vehicle_class.lower() for k in ["heli", "plane", "jet", "vtol"])
                if is_air:
                    L.append(f'private _padPos{i} = [{p}] call IBC_fnc_findHelipad;')
                    L.append(f'private _cas{i} = ["{ac.vehicle_class}", _padPos{i}, {_r(ac.direction)}, false] call IBC_fnc_spawnVehicle;')
                else:
                    L.append(f'private _cas{i} = ["{ac.vehicle_class}", {p}, {_r(ac.direction)}, false] call IBC_fnc_spawnVehicle;')
            L.append(f'createMarker ["m_cas{i}", {_sqf2d(ac.position)}] setMarkerType "b_air"; "m_cas{i}" setMarkerColor "ColorBlue"; "m_cas{i}" setMarkerText "{ac.callsign}";')
        L.append("")

    # ── 6. OPFOR ──
    L.append("// === OPFOR ===")
    gc = 0
    for zone in config.opfor.zones:
        L.append(f"// ---- {zone.name} ----")
        for pos in zone.positions:
            gc += 1
            g = _sv(f"g_{zone.name}_{pos.id}")
            units = _get_units(pos, enemy_faction_data)
            p = _sqf(pos.position)

            L.append(f"// {pos.type}: {pos.id}")
            route = pos.patrol_route
            route_sqf = "[" + ",".join(_sqf(wp) for wp in route) + "]" if route else "[]"

            if pos.type == "vehicle_patrol" and pos.vehicle_class:
                if route:
                    L.append(f'private _vp = ["{pos.vehicle_class}", {route_sqf}, east, "{pos.speed}"] call IBC_fnc_vehiclePatrol;')
                else:
                    # SMART: auto-generate route from road network
                    L.append(f'private _vp = ["{pos.vehicle_class}", {p}, 400, "{pos.speed}"] call IBC_fnc_smartVehiclePatrol;')
                L.append(f"{g} = group driver _vp;")
                L.append(f"[{g}, {_r(sk_min)}, {_r(sk_range)}] call IBC_fnc_setSkills;")
            elif pos.type == "air_patrol" and pos.vehicle_class:
                if route:
                    L.append(f'private _ap = ["{pos.vehicle_class}", {route_sqf}, east, {_r(pos.altitude)}] call IBC_fnc_aircraftPatrol;')
                else:
                    # Auto-generate circular patrol route around position
                    alt = pos.altitude or 300
                    radius = 1500
                    L.append(f"// Auto air patrol route (circle r={radius}m)")
                    cx, cy = round(pos.position[0], 1), round(pos.position[2], 1)
                    L.append(f'private _apRoute = [];')
                    L.append(f'for "_i" from 0 to 5 do {{ _apRoute pushBack [{cx} + {radius} * sin (_i * 60), {cy} + {radius} * cos (_i * 60), 0] }};')
                    L.append(f'private _ap = ["{pos.vehicle_class}", _apRoute, east, {_r(alt)}] call IBC_fnc_aircraftPatrol;')
                L.append(f"{g} = group driver _ap;")
                L.append(f"[{g}, {_r(sk_min)}, {_r(sk_range)}] call IBC_fnc_setSkills;")
            elif pos.type == "sad_patrol" and route:
                L.append(f"{g} = [{_arr(units)}, {route_sqf}, east] call IBC_fnc_sadPatrol;")
                L.append(f"[{g}, {_r(sk_min)}, {_r(sk_range)}] call IBC_fnc_setSkills;")
            elif pos.type == "guard_route" and route:
                L.append(f"{g} = [{_arr(units)}, {route_sqf}, east] call IBC_fnc_guardRoute;")
                L.append(f"[{g}, {_r(sk_min)}, {_r(sk_range)}] call IBC_fnc_setSkills;")
            elif pos.type == "convoy" and pos.vehicle_class:
                vc = pos.vehicle_class
                if "," in vc:
                    va = "[" + ",".join(f'"{v.strip()}"' for v in vc.split(",")) + "]"
                else:
                    va = f'["{vc}"]'
                if route and len(route) >= 2:
                    # Manual route
                    L.append(f'[{va}, {route_sqf}, east, "{pos.speed}"] call IBC_fnc_convoy;')
                else:
                    # SMART: find road path from position to 1km away
                    L.append(f'[{va}, {p}, {p} getPos [1000, random 360], "{pos.speed}"] call IBC_fnc_smartConvoy;')
            elif pos.type == "garrison":
                L.append(f"{g} = [{p}, east, {_arr(units)}] call IBC_fnc_spawnGroup;")
                L.append(f"[{g}, {_r(sk_min)}, {_r(sk_range)}] call IBC_fnc_setSkills;")
                L.append(f"[{g}, {p}, {_r(pos.garrison_radius)}] call IBC_fnc_garrison;")
            elif pos.type == "patrol":
                if route:
                    # Manual route provided
                    L.append(f'{g} = [{_arr(units)}, {route_sqf}, east, "{pos.speed}", "SAFE", "{pos.formation}"] call IBC_fnc_infantryPatrol;')
                else:
                    # SMART: auto-generate patrol from road network / terrain
                    L.append(f'{g} = [{_arr(units)}, {p}, east, 300, "{pos.speed}", "{pos.formation}"] call IBC_fnc_smartInfantryPatrol;')
                L.append(f"[{g}, {_r(sk_min)}, {_r(sk_range)}] call IBC_fnc_setSkills;")
            elif pos.type == "sniper":
                L.append(f"{g} = [{p}, east, {_arr(units)}] call IBC_fnc_spawnGroup;")
                L.append(f'{g} setBehaviour "STEALTH"; {g} setCombatMode "RED";')
                L.append(f"{{ _x setSkill ['aimingAccuracy', 0.9]; _x setSkill ['spotDistance', 0.95] }} forEach units {g};")
            elif pos.type == "mg_nest":
                L.append(f"{g} = [{p}, east, {_arr(units)}] call IBC_fnc_spawnGroup;")
                L.append(f"[{g}, {_r(sk_min)}, {_r(sk_range)}] call IBC_fnc_setSkills;")
                sw = pos.static_weapon or "O_HMG_01_high_F"
                L.append(f'private _sw = ["{sw}", {p}] call IBC_fnc_spawnObject;')
                L.append(f"(units {g} select 0) moveInGunner _sw;")
                L.append(f'{g} setBehaviour "AWARE"; {g} setCombatMode "RED";')
            elif pos.type == "checkpoint":
                L.append(f"{g} = [{p}, east, {_arr(units)}] call IBC_fnc_spawnGroup;")
                L.append(f"[{g}, {_r(sk_min)}, {_r(sk_range)}] call IBC_fnc_setSkills;")
                L.append(f'{g} setBehaviour "AWARE"; {g} setCombatMode "YELLOW";')
                L.append(f'["Land_RoadBarrier_F", [{p}] call IBC_fnc_findRoadPos] call IBC_fnc_spawnObject;')
            elif pos.type == "qrf":
                L.append(f"{g} = [{p}, east, {_arr(units)}] call IBC_fnc_spawnGroup;")
                L.append(f"[{g}, {_r(sk_min)}, {_r(sk_range)}] call IBC_fnc_setSkills;")
                L.append(f'{g} setBehaviour "AWARE"; {g} setCombatMode "RED";')
            else:
                L.append(f"{g} = [{p}, east, {_arr(units)}] call IBC_fnc_spawnGroup;")
                L.append(f"[{g}, {_r(sk_min)}, {_r(sk_range)}] call IBC_fnc_setSkills;")
                L.append(f'{g} setBehaviour "AWARE"; {g} setCombatMode "RED";')

            # Vehicle for motorized/mechanized (non-pathing types)
            if pos.vehicle_class and pos.composition in ("motorized", "mechanized") and pos.type not in ("vehicle_patrol", "air_patrol", "convoy"):
                vp = _sqf([pos.position[0] + 10, pos.position[1], pos.position[2]])
                L.append(f'private _v = ["{pos.vehicle_class}", {vp}] call IBC_fnc_spawnVehicle;')
                L.append(f"(crew _v) joinSilent {g};")
            L.append("")

        for fort in zone.fortifications:
            cls = FORT_CLASSES.get(fort.get("type", "sandbag"), "Land_BagFence_Long_F")
            fp = fort.get("position", zone.center)
            L.append(f'["{cls}", {_sqf(fp)}, {_r(fort.get("direction", 0))}] call IBC_fnc_spawnObject;')
        for mp in zone.mines:
            L.append(f'createMine ["ATMine", {_sqf(mp)}, [], 0];')

    L.append(f'diag_log "IBC: {gc} OPFOR groups spawned";')
    L.append("")

    # ── 7. HOSTAGES ──
    if config.hostages.enabled:
        L.append("// === Hostages ===")
        L.append('private _civCls = ["C_man_1","C_Man_casual_1_F","C_Man_casual_2_F","C_Man_casual_3_F"];')
        for h in config.hostages.hostages:
            for ci in range(h.count):
                hp = _sqf([h.position[0] + ci * 2, h.position[1], h.position[2]])
                L.append(f"private _hRoom = [{hp}, 150] call IBC_fnc_indoorPos;")
                L.append(f'private _hG = createGroup [civilian, true];')
                L.append(f'private _hU = _hG createUnit [_civCls select ({ci} mod 4), _hRoom, [], 0, "NONE"];')
                L.append(f"_hU setPosATL _hRoom;")
                L.append(f'_hU setCaptive true; _hU disableAI "MOVE"; _hU disableAI "PATH"; _hU disableAI "FSM";')
                L.append(f"_hU setUnitPos \"MIDDLE\";")
                L.append(f"_hU setVariable ['ibc_hostage', true, true];")
                L.append(f"_hU setVariable ['ibc_hostage_id', '{h.id}', true];")
            L.append(f'createMarker ["m_h_{h.id}", {_sqf2d(h.position)}] setMarkerType "hd_pickup"; "m_h_{h.id}" setMarkerColor "ColorGreen"; "m_h_{h.id}" setMarkerText "{h.id}";')
        L.append("")

    # ── 8. CIVILIANS ──
    if config.civilians.enabled:
        dens = {"low": 3, "medium": 6, "high": 10}.get(config.civilians.density, 3)
        L.append("// === Civilians ===")
        L.append('private _civPool = ["C_man_1","C_Man_casual_1_F","C_Man_casual_2_F","C_Man_casual_3_F"];')
        for cz in config.civilians.zones:
            c = cz.get("center", [0, 0, 0])
            r = cz.get("radius", 100)
            L.append(f'for "_i" from 1 to {dens} do {{')
            L.append(f"\tprivate _cp = {_sqf(c)} getPos [random {r}, random 360];")
            L.append(f'\tprivate _cG = createGroup [civilian, true];')
            L.append(f'\tprivate _cv = _cG createUnit [selectRandom _civPool, _cp, [], 0, "NONE"];')
            L.append(f"\t_cv setPosATL [getPosATL _cv select 0, getPosATL _cv select 1, 0];")
            L.append(f'\t_cv setCaptive true; _cv setBehaviour "SAFE"; _cv disableAI "MOVE";')
            L.append(f"}};")
        L.append("")

    # ── 9. RESUPPLY & GEAR CRATES ──
    if config.resupply:
        L.append("// === Resupply & Gear Crates ===")
        for crate in config.resupply:
            cp = _sqf(crate.position)
            if crate.type == "arsenal":
                # Virtual Arsenal — full gear selection
                L.append(f'[{cp}] call IBC_fnc_spawnArsenal;')
                L.append(f'createMarker ["m_arsenal", {_sqf2d(crate.position)}] setMarkerType "mil_dot"; "m_arsenal" setMarkerColor "ColorBlue"; "m_arsenal" setMarkerText "ARSENAL";')
            else:
                # Pre-loaded crate (ammo, medical, explosives, at, special)
                L.append(f'[{cp}, "{crate.type}"] call IBC_fnc_spawnGearCrate;')
        L.append("")

    # ── 10. FORTIFICATIONS ──
    if config.fortifications:
        L.append("// === Fortifications ===")
        for fort in config.fortifications:
            cls = FORT_CLASSES.get(fort.type, "Land_BagFence_Long_F")
            L.append(f'["{cls}", {_sqf(fort.position)}, {_r(fort.direction)}] call IBC_fnc_spawnObject;')
        L.append("")

    # ── 11. TASKS ──
    L.append("// === Tasks ===")
    tids = []
    for i, obj in enumerate(config.markers.objectives):
        tid = _sv(obj.name)
        tids.append(tid)
        text = obj.text or obj.name
        L.append(f'[west, "{tid}", ["{text}", "{text}", ""], {_sqf(obj.position)}, "CREATED", {max(1,10-i)}, true, "attack"] call BIS_fnc_taskCreate;')

    if config.hostages.enabled:
        for hi, h in enumerate(config.hostages.hostages):
            tid = _sv(h.task_name or f"rescue_{h.id}")
            tids.append(tid)
            text = h.task_text or f"Uratuj zakladnikow ({h.id})"
            L.append(f'[west, "{tid}", ["{text}", "{text}", ""], {_sqf(h.position)}, "CREATED", {max(1,5-hi)}, true, "interact"] call BIS_fnc_taskCreate;')

    if tids:
        L.append(f'["{tids[0]}"] call BIS_fnc_taskSetCurrent;')
    L.append("")

    # ── 12. HOSTAGE RESCUE MONITOR ──
    if config.hostages.enabled:
        L.append("// === Hostage Rescue Monitor ===")
        L.append("[] spawn { while {true} do { sleep 5;")
        L.append('\tprivate _remaining = allUnits select {_x getVariable ["ibc_hostage",false] && alive _x && !(_x getVariable ["ibc_rescued",false])};')
        L.append('\tif (count _remaining == 0) exitWith { diag_log "IBC: All hostages resolved, monitor stopped"; };')
        L.append("\t{")
        L.append('\t\tprivate _hp = getPos _x;')
        L.append('\t\tprivate _friendlies = _hp nearEntities ["SoldierWB", 10];')
        L.append('\t\tprivate _enemies = (_hp nearEntities ["Man", 50]) select {side _x == east && alive _x};')
        L.append("\t\tif (count _friendlies > 0 && count _enemies == 0) then {")
        L.append('\t\t\t_x setVariable ["ibc_rescued",true,true]; _x setCaptive false; _x enableAI "MOVE";')
        L.append('\t\t\t[format ["rescue_%1", _x getVariable ["ibc_hostage_id",""]], "SUCCEEDED"] call BIS_fnc_taskSetState;')
        L.append('\t\t\thint format ["Zakladnik %1 uratowany!", _x getVariable ["ibc_hostage_id",""]];')
        L.append("\t\t};")
        L.append("\t} forEach _remaining;")
        L.append("}; };")
        L.append("")

    # ── 13. MISSION MONITOR (zone clear, QRF, win/lose) ──
    L.append("// === Mission Monitor ===")
    L.append("[] spawn { sleep 15;")

    qrfs = []
    for zone in config.opfor.zones:
        for pos in zone.positions:
            if pos.type == "qrf":
                qrfs.append((zone.name, zone.center, pos.position, pos.trigger_radius))
    for i in range(len(qrfs)):
        L.append(f"\tprivate _qrf{i} = false;")

    L.append("\twhile {true} do { sleep 8;")

    # Zone clear by side check
    for zone in config.opfor.zones:
        for obj in config.markers.objectives:
            ol = obj.name.lower().replace("_", " ")
            zl = zone.name.lower().replace("_", " ")
            if zl in ol or ol in zl or obj.text.lower() in zl or zl in obj.text.lower():
                tid = _sv(obj.name)
                L.append(f'\t\tif !("{tid}" call BIS_fnc_taskCompleted) then {{')
                L.append(f"\t\t\tif (({_sqf(zone.center)} nearEntities [\"Man\", 300]) select {{side _x == east && alive _x}} isEqualTo []) then {{")
                L.append(f'\t\t\t\t["{tid}", "SUCCEEDED"] call BIS_fnc_taskSetState;')
                L.append(f'\t\t\t\thint "{obj.text or obj.name} - cel zrealizowany!";')
                L.append(f"\t\t\t}};")
                L.append(f"\t\t}};")
                break

    # QRF activation
    for i, (zn, zc, qp, qr) in enumerate(qrfs):
        L.append(f"\t\tif (!_qrf{i}) then {{")
        L.append(f"\t\t\tprivate _near = {_sqf(zc)} nearEntities [\"SoldierWB\", {_r(qr)}];")
        L.append(f"\t\t\tif (count _near > 0) then {{ _qrf{i} = true;")
        L.append(f"\t\t\t\t{{ if (getPos leader _x distance {_sqf(qp)} < 80) then {{")
        L.append(f'\t\t\t\t\t_x setCombatMode "RED"; _x setBehaviour "COMBAT";')
        L.append(f'\t\t\t\t\t(_x addWaypoint [getPos (selectRandom _near), 50]) setWaypointType "SAD";')
        L.append(f"\t\t\t\t}} }} forEach allGroups;")
        L.append(f'\t\t\t\thint "QRF aktywowany!";')
        L.append(f"\t\t\t}};")
        L.append(f"\t\t}};")

    # Win
    if tids:
        check = " && ".join(f'("{t}" call BIS_fnc_taskCompleted)' for t in tids)
        L.append(f"\t\tif ({check}) exitWith {{ hint \"Misja zakonczona sukcesem!\"; sleep 3; [\"end1\",true] call BIS_fnc_endMission }};")

    # Lose
    L.append("\t\tif (({alive _x} count allPlayers) == 0 && time > 30) exitWith { sleep 3; [\"Lose\",false] call BIS_fnc_endMission };")

    L.append("\t};")
    L.append("};")
    L.append("")

    # ── 14. ALERT SYSTEM ──
    if config.alert_system.enabled:
        L.append("// === Alert System ===")
        L.append(f'IBC_alertState = "{config.alert_system.initial_state}";')
        L.append("IBC_allEnemyGroups = allGroups select {side _x == east};")
        L.append(f"[{_r(config.alert_system.combat_radius)}, {_r(config.alert_system.alert_radius)}] call IBC_fnc_startAlertMonitor;")
        L.append('diag_log format ["IBC: Alert system active, state: %1, groups: %2", IBC_alertState, count IBC_allEnemyGroups];')
        L.append("")

    # ── 15. COUNTERATTACK ──
    if config.counterattack.enabled:
        L.append("// === Counterattack ===")
        sp = _sqf(config.counterattack.spawn_position)
        tp = _sqf(config.counterattack.target_position)
        units_arr = _arr(config.counterattack.units)
        vc = config.counterattack.vehicle_class
        delay = config.counterattack.delay_seconds

        if config.counterattack.trigger == "alert_combat":
            L.append(f'[] spawn {{ waitUntil {{ sleep 5; IBC_alertState == "COMBAT" }}; sleep {delay};')
            L.append(f'\t[{tp}, {sp}, {units_arr}, 0, "{vc}"] call IBC_fnc_counterattack;')
            L.append(f'}};')
        elif config.counterattack.trigger == "timer":
            L.append(f'[] spawn {{ sleep {delay};')
            L.append(f'\t[{tp}, {sp}, {units_arr}, 0, "{vc}"] call IBC_fnc_counterattack;')
            L.append(f'}};')
        else:  # obj_complete
            tids_sqf = "[" + ",".join(f'"{t}"' for t in tids) + "]"
            L.append(f'[] spawn {{ waitUntil {{ sleep 10; {{_x call BIS_fnc_taskCompleted}} count {tids_sqf} > 0 }};')
            L.append(f'\tsleep {delay};')
            L.append(f'\t[{tp}, {sp}, {units_arr}, 0, "{vc}"] call IBC_fnc_counterattack;')
            L.append(f'}};')
        L.append("")

    # ── 16. CONVOYS ──
    for ci, convoy in enumerate(config.convoys):
        L.append(f"// === Convoy {ci} ===")
        veh_arr = "[" + ",".join(f'"{v}"' for v in convoy.vehicles) + "]"
        route_arr = "[" + ",".join(_sqf(wp) for wp in convoy.route) + "]"
        side = "east" if convoy.side == "east" else "west"
        L.append(f'[{veh_arr}, {route_arr}, {side}, "{convoy.speed}"] call IBC_fnc_spawnConvoy;')
        L.append("")

    # ── 17. IED ──
    if config.ied.enabled:
        L.append("// === IEDs ===")
        if config.ied.positions:
            for ied_pos in config.ied.positions:
                L.append(f'[{_sqf(ied_pos)}, {_r(config.ied.radius)}, {config.ied.count_per_zone}] call IBC_fnc_spawnIED;')
        else:
            # Place IEDs near OPFOR zones
            for zone in config.opfor.zones:
                L.append(f'[{_sqf(zone.center)}, {_r(config.ied.radius)}, {config.ied.count_per_zone}] call IBC_fnc_spawnIED;')
        L.append("")

    # ── 18. HOLD POSITION ──
    if config.hold_position.enabled:
        L.append("// === Hold Position ===")
        hp = _sqf(config.hold_position.position)
        L.append(f'[{hp}, {config.hold_position.duration_seconds}, {_r(config.hold_position.radius)}] call IBC_fnc_holdPosition;')
        L.append("")

    # ── 19. EXTRACTION ──
    if config.extraction.enabled:
        L.append("// === Extraction ===")
        ep = _sqf(config.extraction.position)
        if config.extraction.condition == "all_objectives":
            check = " && ".join(f'("{t}" call BIS_fnc_taskCompleted)' for t in tids) if tids else "true"
            L.append(f'[] spawn {{ waitUntil {{ sleep 10; {check} }}; [{ep}, {_r(config.extraction.radius)}] call IBC_fnc_createExtraction }};')
        else:
            L.append(f'[{ep}, {_r(config.extraction.radius)}] call IBC_fnc_createExtraction;')
        L.append("")

    # ── 20. MORTAR ──
    if config.mortar.enabled:
        L.append("// === Mortar ===")
        mp = _sqf(config.mortar.target_position)
        if config.mortar.delay_trigger == "alert_combat":
            L.append(f'[] spawn {{ waitUntil {{ sleep 5; IBC_alertState == "COMBAT" }}; sleep 30;')
            L.append(f'\t[{mp}, {config.mortar.rounds}, {_r(config.mortar.spread)}] call IBC_fnc_mortarBarrage;')
            L.append(f'}};')
        else:
            L.append(f'[] spawn {{ sleep 120; [{mp}, {config.mortar.rounds}, {_r(config.mortar.spread)}] call IBC_fnc_mortarBarrage }};')
        L.append("")

    # ── 21. INTEL OBJECTS ──
    for intel in config.intel_objects:
        ipos = _sqf(intel.get("position", [0,0,0]))
        itid = intel.get("task_id", "")
        icls = intel.get("class", "Land_Laptop_unfolded_F")
        if itid:
            L.append(f'[{ipos}, "{itid}", "{icls}"] call IBC_fnc_spawnIntel;')
            if itid not in tids:
                tids.append(itid)
                L.append(f'[west, "{itid}", ["Zbierz intel", "INTEL", ""], {ipos}, "CREATED", 3, true, "search"] call BIS_fnc_taskCreate;')
    if config.intel_objects:
        L.append("")

    # ── 22. DESTROY TARGETS ──
    for dt in config.destroy_targets:
        dpos = _sqf(dt.get("position", [0,0,0]))
        dtid = dt.get("task_id", "")
        dcls = dt.get("class", "Land_CanisterFuel_F")
        if dtid:
            L.append(f'[{dpos}, "{dtid}", "{dcls}"] call IBC_fnc_spawnDestroyTarget;')
            if dtid not in tids:
                tids.append(dtid)
                L.append(f'[west, "{dtid}", ["Zniszcz cel", "DESTROY", ""], {dpos}, "CREATED", 4, true, "destroy"] call BIS_fnc_taskCreate;')
    if config.destroy_targets:
        L.append("")

    # ── 23. REINFORCEMENT WAVES ──
    if config.reinforcement_waves:
        L.append("// === Reinforcement Waves ===")
        waves_sqf = "["
        for wi, wave in enumerate(config.reinforcement_waves):
            wpos = _sqf(wave.get("position", [0,0,0]))
            wdelay = wave.get("delay", 300)
            wunits = wave.get("units", ["O_Soldier_F","O_Soldier_F","O_Soldier_F","O_Soldier_F"])
            wveh = wave.get("vehicle", "")
            units_str = "[" + ",".join(f'"{u}"' for u in wunits) + "]"
            waves_sqf += f'[{wdelay}, {wpos}, {units_str}, "{wveh}"]'
            if wi < len(config.reinforcement_waves) - 1:
                waves_sqf += ","
        waves_sqf += "]"
        L.append(f'{waves_sqf} call IBC_fnc_reinforcementWaves;')
        L.append("")

    # ── 24. SUPPLY DROPS ──
    for sd in config.supply_drops:
        sdpos = _sqf(sd.get("position", [0,0,0]))
        sdtype = sd.get("type", "ammo")
        sddelay = sd.get("delay", 0)
        L.append(f'[{sdpos}, "{sdtype}", {sddelay}] call IBC_fnc_supplyDrop;')
    if config.supply_drops:
        L.append("")

    # ── 25. WEATHER TRANSITIONS ──
    for wt in config.weather_transitions:
        L.append(f'[{wt.get("delay",300)}, {wt.get("overcast",0.5)}, {wt.get("rain",0)}, {wt.get("fog",0)}] call IBC_fnc_weatherTransition;')
    if config.weather_transitions:
        L.append("")

    # ── 26. NIGHT OPS (flares) ──
    if config.flare_illumination:
        fi = config.flare_illumination
        fipos = _sqf(fi.get("position", [0,0,0]))
        L.append(f'[{fipos}, {fi.get("interval",60)}, {fi.get("count",10)}] call IBC_fnc_flareIllum;')
        L.append("")

    # ── 27. AMBIENT COMBAT ──
    if config.ambient_combat:
        ac = config.ambient_combat
        acpos = _sqf(ac.get("position", [0,0,0]))
        L.append(f'[{acpos}, {ac.get("interval",30)}, {ac.get("duration",1800)}] call IBC_fnc_ambientCombat;')
        L.append("")

    # ── 28. TIME LIMIT ──
    if config.time_limit > 0:
        L.append(f'[] spawn {{ sleep {config.time_limit * 60}; hint "Czas misji uplynal!"; sleep 5; ["end1",true] call BIS_fnc_endMission }};')
        L.append("")

    # ── 29. PLAYER TRANSPORT ──
    if not config.player_vehicles:
        L.append("// Default player MRAP")
        L.append('["B_MRAP_01_F", player getPos [15, getDir player + 90], 0, false] call IBC_fnc_spawnVehicle;')
        L.append("")

    # ── SUMMARY ──
    zones = ", ".join(z.name for z in config.opfor.zones)
    features = []
    if config.alert_system.enabled: features.append("ALERT")
    if config.counterattack.enabled: features.append("KONTRATAK")
    if config.convoys: features.append(f"CONVOY x{len(config.convoys)}")
    if config.ied.enabled: features.append("IED")
    if config.hold_position.enabled: features.append("HOLD")
    if config.extraction.enabled: features.append("EXFIL")
    if config.mortar.enabled: features.append("MORTAR")
    feat_str = ", ".join(features) if features else "standard"

    L.append(f'hint "IBC MISSION READY\\n\\nOPFOR: {gc} grup\\nTasks: {len(tids)}\\nZones: {zones}\\nMechaniki: {feat_str}\\n\\nM=mapa, J=taski";')
    L.append(f'diag_log "IBC: READY - {gc} OPFOR, {len(tids)} tasks, mechanics: {feat_str}";')
    return "\n".join(L) + "\n"

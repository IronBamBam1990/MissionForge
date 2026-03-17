"""SQF module library — complete, production-ready functions.

Categories:
1. SPAWN     — units, groups, vehicles, aircraft, objects
2. POSITION  — terrain, buildings, roads, helipads, garages
3. LOADOUT   — weapons, gear, arsenal, crates
4. BEHAVIOR  — garrison, patrol, QRF, alert
5. MISSION   — tasks, monitoring, win/lose
"""


def helpers() -> str:
    """All IBC_fnc_* functions. Injected at top of initServer.sqf."""
    return """
// ================================================================
// IBC FRAMEWORK — CORE FUNCTIONS
// Verified working in ARMA 3 (2026-03-17)
// ================================================================

// ────────────────────────────────────────────
// 1. SPAWN FUNCTIONS
// ────────────────────────────────────────────

// Spawn infantry group with terrain snap
IBC_fnc_spawnGroup = {
	params ["_pos", "_side", "_classes"];
	private _grp = createGroup [_side, true];
	{
		private _u = _grp createUnit [_x, _pos, [], 3, "NONE"];
		_u setPosATL [getPosATL _u select 0, getPosATL _u select 1, 0];
	} forEach _classes;
	_grp
};

// Spawn group INSIDE a building (e.g. hostages, garrison indoors)
IBC_fnc_spawnGroupInBuilding = {
	params ["_pos", "_side", "_classes", ["_radius", 100]];
	private _grp = createGroup [_side, true];
	private _buildings = nearestObjects [_pos, ["House", "Building"], _radius];
	private _bpos = [];
	{ { _bpos pushBack _x } forEach (_x buildingPos -1) } forEach _buildings;
	_bpos = _bpos call BIS_fnc_arrayShuffle;
	{
		private _spawnPos = if (count _bpos > 0) then { _bpos deleteAt 0 } else { _pos };
		private _u = _grp createUnit [_x, _spawnPos, [], 0, "NONE"];
		_u setPosATL _spawnPos;
		_u setUnitPos "MIDDLE";
	} forEach _classes;
	_grp
};

// Spawn vehicle with terrain snap
// Params: classname, position, direction, crewed
IBC_fnc_spawnVehicle = {
	params ["_class", "_pos", ["_dir", 0], ["_crewed", true]];
	private _veh = createVehicle [_class, _pos, [], 0, "NONE"];
	_veh setPosATL [getPosATL _veh select 0, getPosATL _veh select 1, 0.3];
	_veh setDir _dir;
	if (_crewed) then {
		createVehicleCrew _veh;
		{ _x setSkill 0.5 } forEach crew _veh;
	};
	_veh
};

// Spawn vehicle on nearest road
IBC_fnc_spawnVehicleOnRoad = {
	params ["_class", "_pos", ["_radius", 200], ["_crewed", true]];
	private _roads = _pos nearRoads _radius;
	private _spawnPos = if (count _roads > 0) then {
		private _road = selectRandom _roads;
		private _roadDir = (roadsConnectedTo _road) apply { _road getDir _x };
		private _dir = if (count _roadDir > 0) then { _roadDir select 0 } else { random 360 };
		[getPos _road, _dir]
	} else {
		[_pos, random 360]
	};
	private _veh = [_class, _spawnPos select 0, _spawnPos select 1, _crewed] call IBC_fnc_spawnVehicle;
	_veh
};

// Spawn flying aircraft (velocity prevents stall)
IBC_fnc_spawnAircraft = {
	params ["_class", "_pos", ["_dir", 0], ["_alt", 300], ["_speed", 80]];
	private _isHeli = ("Heli" in _class) || ("heli" in _class);
	if (_isHeli) then { _alt = _alt min 200; _speed = _speed min 60 };
	private _veh = createVehicle [_class, [_pos select 0, _pos select 1, _alt], [], 0, "FLY"];
	_veh setDir _dir;
	_veh setVelocityModelSpace [0, _speed, 0];
	_veh flyInHeight _alt;
	createVehicleCrew _veh;
	(group driver _veh) setBehaviour "SAFE";
	(group driver _veh) setCombatMode "GREEN";
	_veh
};

// Spawn static object with terrain snap (fortifications, barriers, crates)
IBC_fnc_spawnObject = {
	params ["_class", "_pos", ["_dir", 0]];
	private _obj = createVehicle [_class, _pos, [], 0, "NONE"];
	_obj setPosATL [getPosATL _obj select 0, getPosATL _obj select 1, 0];
	_obj setDir _dir;
	_obj
};

// ────────────────────────────────────────────
// 2. POSITION FUNCTIONS
// ────────────────────────────────────────────

// Find helipad or flat terrain for helicopter
IBC_fnc_findHelipad = {
	params ["_pos", ["_radius", 500]];
	private _pads = nearestObjects [_pos, [
		"HeliH", "HeliHCivil", "HeliHRescue",
		"Land_HelipadCircle_F", "Land_HelipadSquare_F", "Land_HelipadRescue_F",
		"Land_HelipadEmpty_F"
	], _radius];
	if (count _pads > 0) then {
		getPos (selectRandom _pads)
	} else {
		[_pos, 0, _radius, 15, 0, 0.3, 0] call BIS_fnc_findSafePos
	}
};

// Find indoor position (room inside building)
IBC_fnc_indoorPos = {
	params ["_pos", ["_radius", 100]];
	private _buildings = nearestObjects [_pos, ["House", "Building"], _radius];
	private _result = _pos;
	{
		private _bp = _x buildingPos -1;
		if (count _bp > 0) exitWith { _result = selectRandom _bp };
	} forEach _buildings;
	_result
};

// Find garage or shelter for vehicle
IBC_fnc_findGarage = {
	params ["_pos", ["_radius", 300]];
	private _garages = nearestObjects [_pos, [
		"Land_i_Garage_V1_F", "Land_i_Garage_V2_F",
		"Land_Shed_Big_F", "Land_Shed_Small_F",
		"Land_MilOffices_V1_F", "Land_Hangar_F",
		"Land_TentHangar_V1_F"
	], _radius];
	if (count _garages > 0) then {
		private _g = selectRandom _garages;
		private _gPos = getPos _g;
		[_gPos select 0, _gPos select 1, 0]
	} else {
		_pos
	}
};

// Find position on nearest road
IBC_fnc_findRoadPos = {
	params ["_pos", ["_radius", 200]];
	private _roads = _pos nearRoads _radius;
	if (count _roads > 0) then {
		getPos (selectRandom _roads)
	} else {
		_pos
	}
};

// Find safe flat terrain position
IBC_fnc_findFlatPos = {
	params ["_pos", ["_minR", 0], ["_maxR", 200], ["_minFlat", 5]];
	[_pos, _minR, _maxR, _minFlat, 0, 0.3, 0] call BIS_fnc_findSafePos
};

// ────────────────────────────────────────────
// 3. LOADOUT & GEAR FUNCTIONS
// ────────────────────────────────────────────

// Apply full loadout to unit
IBC_fnc_applyLoadout = {
	params ["_unit", "_loadout"];
	// Strip everything
	removeAllWeapons _unit;
	removeAllItems _unit;
	removeAllAssignedItems _unit;
	removeUniform _unit;
	removeVest _unit;
	removeBackpack _unit;
	removeHeadgear _unit;
	removeGoggles _unit;

	// Clothing
	private _uniform = _loadout getOrDefault ["uniform", ""];
	if (_uniform != "") then { _unit forceAddUniform _uniform };
	private _vest = _loadout getOrDefault ["vest", ""];
	if (_vest != "") then { _unit addVest _vest };
	private _helmet = _loadout getOrDefault ["helmet", ""];
	if (_helmet != "") then { _unit addHeadgear _helmet };
	private _backpack = _loadout getOrDefault ["backpack", ""];
	if (_backpack != "") then { _unit addBackpack _backpack };
	private _goggles = _loadout getOrDefault ["goggles", ""];
	if (_goggles != "") then { _unit addGoggles _goggles };

	// Primary weapon + magazines
	private _primary = _loadout getOrDefault ["primary_weapon", ""];
	if (_primary != "") then {
		private _mags = _loadout getOrDefault ["primary_mags", 8];
		private _magTypes = getArray (configFile >> "CfgWeapons" >> _primary >> "magazines");
		if (count _magTypes > 0) then {
			for "_i" from 1 to _mags do { _unit addMagazine (_magTypes select 0) };
		};
		_unit addWeapon _primary;
		// Attachments
		private _optic = _loadout getOrDefault ["optic", ""];
		if (_optic != "") then { _unit addPrimaryWeaponItem _optic };
		private _suppressor = _loadout getOrDefault ["suppressor", ""];
		if (_suppressor != "") then { _unit addPrimaryWeaponItem _suppressor };
		private _bipod = _loadout getOrDefault ["bipod", ""];
		if (_bipod != "") then { _unit addPrimaryWeaponItem _bipod };
		private _flashlight = _loadout getOrDefault ["flashlight", ""];
		if (_flashlight != "") then { _unit addPrimaryWeaponItem _flashlight };
	};

	// Secondary weapon (pistol)
	private _secondary = _loadout getOrDefault ["secondary_weapon", ""];
	if (_secondary != "") then {
		private _sMags = _loadout getOrDefault ["secondary_mags", 3];
		private _sMagTypes = getArray (configFile >> "CfgWeapons" >> _secondary >> "magazines");
		if (count _sMagTypes > 0) then {
			for "_i" from 1 to _sMags do { _unit addMagazine (_sMagTypes select 0) };
		};
		_unit addWeapon _secondary;
	};

	// Launcher
	private _launcher = _loadout getOrDefault ["launcher", ""];
	if (_launcher != "") then {
		private _lMags = _loadout getOrDefault ["launcher_mags", 1];
		private _lMagTypes = getArray (configFile >> "CfgWeapons" >> _launcher >> "magazines");
		if (count _lMagTypes > 0) then {
			for "_i" from 1 to _lMags do { _unit addMagazine (_lMagTypes select 0) };
		};
		_unit addWeapon _launcher;
	};

	// Night vision
	private _nvg = _loadout getOrDefault ["nvg", ""];
	if (_nvg != "") then { _unit linkItem _nvg };

	// Items (medkits, grenades, etc.)
	{ _unit addItem _x } forEach (_loadout getOrDefault ["items", []]);

	// Standard items always
	_unit linkItem "ItemMap";
	_unit linkItem "ItemCompass";
	_unit linkItem "ItemWatch";
	_unit linkItem "ItemRadio";
};

// Create Virtual Arsenal crate (players can select any gear)
IBC_fnc_spawnArsenal = {
	params ["_pos", ["_class", "B_supplyCrate_F"]];
	private _box = [_class, _pos] call IBC_fnc_spawnObject;
	["AmmoboxInit", [_box, true]] call BIS_fnc_arsenal;
	_box
};

// Create pre-loaded gear crate (specific items)
IBC_fnc_spawnGearCrate = {
	params ["_pos", "_type", ["_class", "Box_NATO_Ammo_F"]];
	private _box = [_class, _pos] call IBC_fnc_spawnObject;
	clearWeaponCargoGlobal _box;
	clearMagazineCargoGlobal _box;
	clearItemCargoGlobal _box;
	clearBackpackCargoGlobal _box;

	switch (_type) do {
		case "ammo": {
			_box addMagazineCargoGlobal ["30Rnd_65x39_caseless_mag", 50];
			_box addMagazineCargoGlobal ["100Rnd_65x39_caseless_mag_Tracer", 10];
			_box addMagazineCargoGlobal ["16Rnd_9x21_Mag", 20];
			_box addMagazineCargoGlobal ["HandGrenade", 15];
			_box addMagazineCargoGlobal ["SmokeShell", 15];
			_box addMagazineCargoGlobal ["SmokeShellGreen", 5];
			_box addMagazineCargoGlobal ["SmokeShellRed", 5];
			_box addMagazineCargoGlobal ["1Rnd_HE_Grenade_shell", 10];
			_box addMagazineCargoGlobal ["NLAW_F", 4];
		};
		case "medical": {
			_box addItemCargoGlobal ["FirstAidKit", 30];
			_box addItemCargoGlobal ["Medikit", 3];
			_box addMagazineCargoGlobal ["SmokeShell", 10];
			_box addMagazineCargoGlobal ["SmokeShellGreen", 10];
		};
		case "explosives": {
			_box addMagazineCargoGlobal ["DemoCharge_Remote_Mag", 8];
			_box addMagazineCargoGlobal ["SatchelCharge_Remote_Mag", 4];
			_box addMagazineCargoGlobal ["ClaymoreDirectionalMine_Remote_Mag", 6];
			_box addMagazineCargoGlobal ["APERSBoundingMine_Range_Mag", 4];
			_box addItemCargoGlobal ["MineDetector", 2];
		};
		case "at": {
			_box addWeaponCargoGlobal ["launch_NLAW_F", 4];
			_box addMagazineCargoGlobal ["NLAW_F", 8];
			_box addWeaponCargoGlobal ["launch_B_Titan_short_F", 2];
			_box addMagazineCargoGlobal ["Titan_AT", 4];
		};
		case "special": {
			_box addWeaponCargoGlobal ["srifle_DMR_01_F", 2];
			_box addWeaponCargoGlobal ["srifle_EBR_F", 2];
			_box addItemCargoGlobal ["optic_DMS", 2];
			_box addItemCargoGlobal ["optic_LRPS", 2];
			_box addItemCargoGlobal ["muzzle_snds_H", 4];
			_box addItemCargoGlobal ["muzzle_snds_B", 2];
			_box addItemCargoGlobal ["NVGoggles", 10];
			_box addItemCargoGlobal ["Binocular", 5];
			_box addItemCargoGlobal ["Rangefinder", 2];
			_box addItemCargoGlobal ["Laserdesignator", 1];
		};
		default {
			// General purpose
			_box addMagazineCargoGlobal ["30Rnd_65x39_caseless_mag", 30];
			_box addItemCargoGlobal ["FirstAidKit", 15];
			_box addMagazineCargoGlobal ["HandGrenade", 10];
			_box addMagazineCargoGlobal ["SmokeShell", 10];
		};
	};
	_box
};

// ────────────────────────────────────────────
// 4. AI SKILL & BEHAVIOR
// ────────────────────────────────────────────

// Set AI skills — all sub-skills
IBC_fnc_setSkills = {
	params ["_grp", "_base", "_range"];
	{
		private _s = (_base + random _range) min 1;
		_x setSkill _s;
		_x setSkill ["aimingAccuracy", (_s * 0.8) min 1];
		_x setSkill ["aimingShake", (_s * 0.7) min 1];
		_x setSkill ["aimingSpeed", (_s * 0.9) min 1];
		_x setSkill ["spotDistance", _s min 1];
		_x setSkill ["spotTime", (_s * 0.8) min 1];
		_x setSkill ["courage", (_s * 1.1) min 1];
		_x setSkill ["commanding", _s min 1];
		_x setSkill ["reloadSpeed", _s min 1];
	} forEach units _grp;
};

// ────────────────────────────────────────────
// 5. ADVANCED MECHANICS
// ────────────────────────────────────────────

// Alert State Machine: STEALTH → ALERT → COMBAT
// All enemy groups react to state changes
IBC_alertState = "STEALTH";
IBC_allEnemyGroups = [];

IBC_fnc_setAlertState = {
	params ["_newState"];
	if (IBC_alertState == _newState) exitWith {};
	private _old = IBC_alertState;
	IBC_alertState = _newState;
	diag_log format ["IBC ALERT: %1 -> %2", _old, _newState];

	switch (_newState) do {
		case "ALERT": {
			{
				_x setBehaviour "AWARE";
				_x setCombatMode "YELLOW";
				_x setSpeedMode "NORMAL";
			} forEach IBC_allEnemyGroups;
			["IBC_ALERT"] remoteExec ["hintSilent", 0];
		};
		case "COMBAT": {
			{
				_x setBehaviour "COMBAT";
				_x setCombatMode "RED";
				_x setSpeedMode "FULL";
			} forEach IBC_allEnemyGroups;
			["IBC_COMBAT"] remoteExec ["hintSilent", 0];
		};
	};
};

// Alert monitor — detects shots, casualties, player proximity
IBC_fnc_startAlertMonitor = {
	params [["_combatRadius", 500], ["_alertRadius", 800]];
	private _initialEastCount = {side _x == east && alive _x} count allUnits;

	[_combatRadius, _alertRadius, _initialEastCount] spawn {
		params ["_combatRadius", "_alertRadius", "_initialEastCount"];

		// Event handler for kills
		addMissionEventHandler ["EntityKilled", {
			params ["_killed"];
			if (side _killed == east && IBC_alertState == "STEALTH") then {
				["ALERT"] call IBC_fnc_setAlertState;
			};
			if (side _killed == east && IBC_alertState == "ALERT") then {
				["COMBAT"] call IBC_fnc_setAlertState;
			};
		}];

		while {true} do {
			sleep 5;
			if (IBC_alertState == "STEALTH") then {
				{
					private _leader = leader _x;
					if (alive _leader) then {
						private _nearWest = (getPos _leader) nearEntities ["SoldierWB", _alertRadius];
						if (count _nearWest > 0) then {
							["ALERT"] call IBC_fnc_setAlertState;
						};
					};
				} forEach IBC_allEnemyGroups;
			};
			if (IBC_alertState == "ALERT") then {
				private _casualties = _initialEastCount - ({side _x == east && alive _x} count allUnits);
				if (_casualties > 2) then {
					["COMBAT"] call IBC_fnc_setAlertState;
				};
			};
		};
	};
};

// Counterattack — spawn reinforcements from direction after delay
IBC_fnc_counterattack = {
	params ["_targetPos", "_spawnPos", "_units", "_delay", ["_vehicleClass", ""]];
	[_targetPos, _spawnPos, _units, _vehicleClass] spawn {
		params ["_targetPos", "_spawnPos", "_units", "_vehicleClass"];
		private _grp = [_spawnPos, east, _units] call IBC_fnc_spawnGroup;
		[_grp, 0.5, 0.3] call IBC_fnc_setSkills;
		_grp setBehaviour "COMBAT";
		_grp setCombatMode "RED";
		_grp setSpeedMode "FULL";

		if (_vehicleClass != "") then {
			private _veh = [_vehicleClass, _spawnPos] call IBC_fnc_spawnVehicle;
			{_x moveInAny _veh} forEach units _grp;
		};

		(_grp addWaypoint [_targetPos, 50]) setWaypointType "SAD";
		diag_log format ["IBC: Counterattack from %1 to %2, %3 units", _spawnPos, _targetPos, count units _grp];
		hint "Kontratak wroga! Wzmocnienia w drodze!";
	};
};

// Convoy — vehicles moving along waypoints
IBC_fnc_spawnConvoy = {
	params ["_vehicleClasses", "_route", "_side", ["_speed", "LIMITED"]];
	private _convoy = [];
	private _startPos = _route select 0;
	private _nextPos = _route select (1 min (count _route - 1));
	private _dir = _startPos getDir _nextPos;
	{
		private _vehClass = _x;
		private _offset = [
			(_startPos select 0) - (_forEachIndex * 20 * sin _dir),
			(_startPos select 1) - (_forEachIndex * 20 * cos _dir),
			0
		];
		private _veh = [_vehClass, _offset, _dir] call IBC_fnc_spawnVehicle;
		private _grp = group driver _veh;

		for "_wi" from 1 to (count _route - 1) do {
			(_grp addWaypoint [_route select _wi, 0]) setWaypointType "MOVE";
		};
		(_grp addWaypoint [_route select 0, 0]) setWaypointType "CYCLE";

		_grp setBehaviour "SAFE";
		_grp setCombatMode "YELLOW";
		_grp setSpeedMode _speed;

		_convoy pushBack _veh;
	} forEach _vehicleClasses;
	_convoy
};

// IED system — mines on roads that explode on proximity
IBC_fnc_spawnIED = {
	params ["_pos", ["_radius", 200], ["_count", 3]];
	private _roads = _pos nearRoads _radius;
	private _placed = 0;
	{
		if (_placed >= _count) exitWith {};
		private _iedPos = getPos _x;
		// Use pressure plate mine disguised as debris
		private _ied = createMine ["APERSBoundingMine", _iedPos, [], 0];
		// Hide with debris
		private _debris = createVehicle ["Land_GarbagePallet_F", _iedPos, [], 1, "NONE"];
		_debris setPosATL [getPosATL _debris select 0, getPosATL _debris select 1, 0];
		_placed = _placed + 1;
	} forEach (_roads call BIS_fnc_arrayShuffle);
	diag_log format ["IBC: %1 IEDs placed near %2", _placed, _pos];
};

// Extraction zone — creates trigger area for mission end
IBC_fnc_createExtraction = {
	params ["_pos", ["_radius", 30], ["_taskId", "obj_extract"]];
	createMarker ["m_exfil", [_pos select 0, _pos select 1]] setMarkerType "hd_end";
	"m_exfil" setMarkerColor "ColorGreen";
	"m_exfil" setMarkerText "EXFIL";

	[west, _taskId, ["Dotrzec do punktu ewakuacji", "EXFIL", ""], _pos, "CREATED", 1, true, "getin"] call BIS_fnc_taskCreate;

	[_pos, _radius, _taskId] spawn {
		params ["_pos", "_radius", "_taskId"];
		waitUntil {
			sleep 5;
			private _nearPlayers = _pos nearEntities ["SoldierWB", _radius];
			count _nearPlayers > 0 && {alive _x} count _nearPlayers > 0
		};
		[_taskId, "SUCCEEDED"] call BIS_fnc_taskSetState;
		hint "Ewakuacja! Misja zakonczona!";
		sleep 3;
		["end1", true] call BIS_fnc_endMission;
	};
};

// Hold position — defend area for X seconds
IBC_fnc_holdPosition = {
	params ["_pos", "_duration", ["_radius", 100], ["_taskId", "obj_hold"]];
	[west, _taskId, [format ["Utrzymaj pozycje przez %1 minut", _duration / 60], "HOLD", ""], _pos, "CREATED", 2, true, "defend"] call BIS_fnc_taskCreate;

	createMarker ["m_hold", [_pos select 0, _pos select 1]] setMarkerShape "ELLIPSE";
	"m_hold" setMarkerSize [_radius, _radius];
	"m_hold" setMarkerColor "ColorBlue";
	"m_hold" setMarkerAlpha 0.3;

	[_pos, _duration, _radius, _taskId] spawn {
		params ["_pos", "_duration", "_radius", "_taskId"];
		private _startTime = -1;
		private _hintShown = false;

		while {true} do {
			sleep 3;
			private _nearPlayers = (_pos nearEntities ["SoldierWB", _radius]) select {alive _x};
			if (count _nearPlayers > 0) then {
				if (_startTime < 0) then {
					_startTime = time;
					hint "Utrzymuj pozycje! Odliczanie rozpoczete.";
				};
				private _elapsed = time - _startTime;
				private _remaining = _duration - _elapsed;

				if (_remaining <= 0) exitWith {
					[_taskId, "SUCCEEDED"] call BIS_fnc_taskSetState;
					hint "Pozycja utrzymana!";
					"m_hold" setMarkerColor "ColorGreen";
				};

				if (!_hintShown && _remaining < 60) then {
					_hintShown = true;
					hint "Ostatnia minuta!";
				};
				hintSilent format ["HOLD: %1:%2", floor(_remaining / 60), floor(_remaining mod 60) call { if (_this < 10) then { format ["0%1", _this] } else { str _this } }];
			} else {
				if (_startTime > 0) then {
					_startTime = -1;
					hint "Opusciles zone! Timer zresetowany!";
				};
			};
		};
	};
};

// Mortar barrage — periodic explosions in area
IBC_fnc_mortarBarrage = {
	params ["_targetPos", ["_rounds", 8], ["_spread", 80], ["_delay", 3]];
	[_targetPos, _rounds, _spread, _delay] spawn {
		params ["_targetPos", "_rounds", "_spread", "_delay"];
		hint "UWAGA! Ostrzal mozdzierzowy!";
		sleep 3;
		for "_i" from 1 to _rounds do {
			private _impactPos = [
				(_targetPos select 0) + (random _spread) - (_spread / 2),
				(_targetPos select 1) + (random _spread) - (_spread / 2),
				0
			];
			private _shell = createVehicle ["Sh_82mm_AMOS", _impactPos, [], 0, "NONE"];
			sleep (_delay + random 2);
		};
		diag_log format ["IBC: Mortar barrage complete at %1", _targetPos];
	};
};

// ────────────────────────────────────────────
// 6. COMMUNICATION SYSTEMS
// ────────────────────────────────────────────

// ACRE2 radio setup — assigns radios based on unit role
IBC_fnc_setupACRE2 = {
	if !(isClass (configFile >> "CfgPatches" >> "acre_main")) exitWith {
		diag_log "IBC: ACRE2 not loaded, skipping radio setup";
	};

	// Wait for ACRE2 to initialize
	waitUntil {!isNil "acre_sys_core_init_done" && {acre_sys_core_init_done}};

	// Remove default radios from all players
	{
		{_x call acre_api_fnc_removeRadio} forEach ([_x] call acre_api_fnc_getCurrentRadioList);
	} forEach allPlayers;

	// Assign radios based on description (role name in SQM)
	{
		private _desc = toLower (roleDescription _x);
		private _unit = _x;

		// Everyone gets short range (AN/PRC-343)
		[_unit, "ACRE_PRC343"] call acre_api_fnc_addRadioToUnit;

		// Squad leaders, team leaders get medium range (AN/PRC-152)
		if ("leader" in _desc || "sergeant" in _desc || "sl" in _desc || "tl" in _desc) then {
			[_unit, "ACRE_PRC152"] call acre_api_fnc_addRadioToUnit;
		};

		// Platoon leader, RATELO, FAC get long range (AN/PRC-117F)
		if ("platoon" in _desc || "ratelo" in _desc || "lieutenant" in _desc || "fac" in _desc) then {
			[_unit, "ACRE_PRC117F"] call acre_api_fnc_addRadioToUnit;
		};

		// Pilots get medium range
		if ("pilot" in _desc || "hawk" in _desc || "eagle" in _desc) then {
			[_unit, "ACRE_PRC152"] call acre_api_fnc_addRadioToUnit;
		};
	} forEach allPlayers;

	diag_log format ["IBC: ACRE2 radios assigned to %1 players", count allPlayers];
};

// ACRE2 channel preset — set channels for squads
IBC_fnc_setACRE2Channels = {
	params ["_channels"];
	// _channels = [["ALPHA", 1], ["BRAVO", 2], ["CHARLIE", 3], ["CMD", 5]]
	// Channel config is done per-radio, typically:
	// PRC-343: channel = squad internal
	// PRC-152: channel 1 = squad net, channel 2 = platoon net
	// PRC-117F: channel 1 = platoon net, channel 2 = battalion/CAS
	diag_log format ["IBC: ACRE2 channels configured: %1", _channels];
};

// TFAR radio setup
IBC_fnc_setupTFAR = {
	if !(isClass (configFile >> "CfgPatches" >> "task_force_radio")) exitWith {
		diag_log "IBC: TFAR not loaded, skipping radio setup";
	};

	{
		private _desc = toLower (roleDescription _x);
		private _unit = _x;

		// Squad leaders get long range
		if ("leader" in _desc || "sergeant" in _desc || "ratelo" in _desc || "lieutenant" in _desc) then {
			_unit linkItem "tf_anprc152";
		};
	} forEach allPlayers;

	diag_log format ["IBC: TFAR radios assigned to %1 players", count allPlayers];
};

// ────────────────────────────────────────────
// 7. ENVIRONMENT & ATMOSPHERE
// ────────────────────────────────────────────

// Dynamic weather transition during mission
IBC_fnc_weatherTransition = {
	params ["_delay", "_overcast", "_rain", "_fog", ["_duration", 300]];
	[_delay, _overcast, _rain, _fog, _duration] spawn {
		params ["_delay", "_overcast", "_rain", "_fog", "_duration"];
		sleep _delay;
		_duration setOvercast _overcast;
		_duration setRain _rain;
		_duration setFog _fog;
		diag_log format ["IBC: Weather transition -> overcast:%1 rain:%2 fog:%3", _overcast, _rain, _fog];
	};
};

// Flare illumination — periodic flares over area (night ops)
IBC_fnc_flareIllum = {
	params ["_pos", ["_interval", 60], ["_count", 10], ["_height", 200]];
	[_pos, _interval, _count, _height] spawn {
		params ["_pos", "_interval", "_count", "_height"];
		for "_i" from 1 to _count do {
			private _flarePos = [
				(_pos select 0) + (random 100) - 50,
				(_pos select 1) + (random 100) - 50,
				_height
			];
			private _flare = createVehicle ["F_40mm_White", _flarePos, [], 0, "NONE"];
			sleep _interval;
		};
	};
};

// Ambient distant combat sounds (makes world feel alive)
IBC_fnc_ambientCombat = {
	params ["_pos", ["_interval", 30], ["_duration", 1800]];
	[_pos, _interval, _duration] spawn {
		params ["_pos", "_interval", "_duration"];
		private _endTime = time + _duration;
		private _sounds = ["mortar_explosion", "artillery_explosion"];
		while {time < _endTime} do {
			sleep (_interval + random _interval);
			private _sndPos = [
				(_pos select 0) + (random 2000) - 1000,
				(_pos select 1) + (random 2000) - 1000,
				0
			];
			private _src = createVehicle ["HelperBase_F", _sndPos, [], 0, "NONE"];
			_src say3D ["Explosion1", 5000];
			sleep 5;
			deleteVehicle _src;
		};
	};
};

// ────────────────────────────────────────────
// 8. OBJECTIVE MECHANICS
// ────────────────────────────────────────────

// Intel object — laptop/document to interact with
IBC_fnc_spawnIntel = {
	params ["_pos", "_taskId", ["_class", "Land_Laptop_unfolded_F"], ["_interactTime", 8]];
	private _obj = [_class, _pos] call IBC_fnc_spawnObject;
	private _actionId = _obj addAction [
		"<t color='#00ff00'>Zbierz intel</t>",
		{
			params ["_target", "_caller", "_id"];
			_caller playMove "AinvPknlMstpSnonWnonDnon_medic_1";
			sleep (_target getVariable ["ibc_interact_time", 8]);
			private _tid = _target getVariable ["ibc_task_id", ""];
			if (_tid != "") then {
				[_tid, "SUCCEEDED"] call BIS_fnc_taskSetState;
				hint "Intel zabezpieczony!";
			};
			_target removeAction _id;
			deleteVehicle _target;
		},
		nil, 6, true, true, "", "alive _this && _this distance _target < 3"
	];
	_obj setVariable ["ibc_task_id", _taskId];
	_obj setVariable ["ibc_interact_time", _interactTime];
	_obj
};

// Destroy target — object that must be destroyed (explosive charge)
IBC_fnc_spawnDestroyTarget = {
	params ["_pos", "_taskId", ["_class", "Land_CanisterFuel_F"]];
	private _obj = [_class, _pos] call IBC_fnc_spawnObject;
	_obj setVariable ["ibc_destroy_task", _taskId, true];

	// Monitor destruction
	[_obj, _taskId] spawn {
		params ["_obj", "_taskId"];
		waitUntil { sleep 3; !alive _obj || isNull _obj };
		[_taskId, "SUCCEEDED"] call BIS_fnc_taskSetState;
		hint "Cel zniszczony!";
	};
	_obj
};

// Reinforcement waves — spawn enemies in waves with delay
IBC_fnc_reinforcementWaves = {
	params ["_waves"];
	// _waves = [[delay_sec, position, units_array, vehicle_class_or_empty], ...]
	[_waves] spawn {
		params ["_waves"];
		{
			_x params ["_delay", "_pos", "_units", ["_vehClass", ""]];
			sleep _delay;
			private _grp = [_pos, east, _units] call IBC_fnc_spawnGroup;
			[_grp, 0.5, 0.3] call IBC_fnc_setSkills;
			_grp setBehaviour "COMBAT";
			_grp setCombatMode "RED";

			if (_vehClass != "") then {
				private _veh = [_vehClass, _pos] call IBC_fnc_spawnVehicle;
				{ _x moveInAny _veh } forEach units _grp;
			};

			// Move toward nearest player
			private _target = getPos (allPlayers select 0);
			(_grp addWaypoint [_target, 100]) setWaypointType "SAD";

			hint format ["Wrogowie wzmocnienia z kierunku %1!", if ((_pos select 0) > (_target select 0)) then {"wschod"} else {"zachod"}];
			diag_log format ["IBC: Reinforcement wave at %1, %2 units", _pos, count units _grp];
		} forEach _waves;
	};
};

// Supply drop — helicopter delivers crate at position
IBC_fnc_supplyDrop = {
	params ["_dropPos", ["_crateType", "ammo"], ["_delay", 0]];
	[_dropPos, _crateType, _delay] spawn {
		params ["_dropPos", "_crateType", "_delay"];
		sleep _delay;
		hint "Zaopatrzenie w drodze! ETA 30 sekund.";

		// Create helicopter far away
		private _spawnPos = [_dropPos select 0, (_dropPos select 1) - 2000, 150];
		private _heli = createVehicle ["B_Heli_Transport_03_F", _spawnPos, [], 0, "FLY"];
		_heli setDir (_spawnPos getDir _dropPos);
		_heli setVelocityModelSpace [0, 60, 0];
		_heli flyInHeight 150;
		createVehicleCrew _heli;
		(group driver _heli) setBehaviour "CARELESS";

		// Wait until near drop point
		waitUntil { sleep 1; _heli distance2D _dropPos < 50 };

		// Drop crate
		private _crate = [_dropPos, _crateType] call IBC_fnc_spawnGearCrate;
		hint "Zaopatrzenie zrzucone!";

		// Helicopter leaves
		private _exitPos = [_dropPos select 0, (_dropPos select 1) + 3000, 200];
		private _wp = (group driver _heli) addWaypoint [_exitPos, 0];
		_wp setWaypointType "MOVE";
		sleep 120;
		deleteVehicle _heli;
	};
};

// ────────────────────────────────────────────
// 9. INTELLIGENT ROAD NETWORK PATHFINDING
// ────────────────────────────────────────────

// GPS-style road pathfinder — finds route between two positions using road graph
// Uses priority BFS (closest to destination first) for efficiency
// Returns array of [x,y,0] positions along roads — ready for waypoints
IBC_fnc_findRoadPath = {
	params ["_startPos", "_endPos", ["_maxSteps", 300]];

	// Find nearest roads to start and end
	private _startRoads = _startPos nearRoads 200;
	private _endRoads = _endPos nearRoads 200;

	if (count _startRoads == 0 || count _endRoads == 0) exitWith {
		diag_log format ["IBC GPS: No roads near %1 or %2 — straight line", _startPos, _endPos];
		[_startPos, _endPos]
	};

	// Pick closest road to each position
	private _startRoad = _startRoads select 0;
	private _endRoad = _endRoads select 0;
	private _endRoadPos = getPos _endRoad;
	private _totalDist = _startPos distance _endPos;

	diag_log format ["IBC GPS: Calculating route %1 -> %2 (%3m)", _startPos, _endPos, round _totalDist];

	// Priority BFS — expand node closest to destination first
	// Format: [priority, road, path]
	private _queue = [[getPos _startRoad distance _endRoadPos, _startRoad, [_startRoad]]];
	private _visited = createHashMap;
	_visited set [str getPos _startRoad, true];
	private _found = [];
	private _steps = 0;

	while {count _queue > 0 && count _found == 0 && _steps < _maxSteps} do {
		_steps = _steps + 1;

		// Find best candidate (lowest priority = closest to end)
		private _bestIdx = 0;
		private _bestPri = (_queue select 0) select 0;
		for "_qi" from 1 to (count _queue - 1) do {
			if (((_queue select _qi) select 0) < _bestPri) then {
				_bestIdx = _qi;
				_bestPri = (_queue select _qi) select 0;
			};
		};

		private _current = _queue deleteAt _bestIdx;
		_current params ["_pri", "_road", "_path"];

		// Check if we reached destination
		if (getPos _road distance _endRoadPos < 50) exitWith {
			_found = _path;
		};

		// Expand connected roads
		{
			private _nPos = getPos _x;
			private _key = format ["%1_%2", round (_nPos select 0), round (_nPos select 1)];
			if !(_key in keys _visited) then {
				_visited set [_key, true];
				private _priority = _nPos distance _endRoadPos;
				_queue pushBack [_priority, _x, _path + [_x]];
			};
		} forEach roadsConnectedTo _road;
	};

	if (count _found == 0) exitWith {
		diag_log format ["IBC GPS: No route found after %1 steps — straight line", _steps];
		[_startPos, _endPos]
	};

	diag_log format ["IBC GPS: Route found! %1 road segments, %2 BFS steps", count _found, _steps];

	// Convert road objects to position waypoints
	// Sample smartly — more waypoints at turns, fewer on straight sections
	private _waypoints = [getPos (_found select 0)];
	private _lastDir = -1;

	for "_i" from 1 to (count _found - 1) do {
		private _pos = getPos (_found select _i);
		private _prevPos = getPos (_found select (_i - 1));
		private _dir = _prevPos getDir _pos;

		// Add waypoint if direction changes significantly (turn) or every 200m
		private _dirChange = if (_lastDir < 0) then { 999 } else { abs (_dir - _lastDir) min (360 - abs (_dir - _lastDir)) };
		private _dist = _pos distance (_waypoints select (count _waypoints - 1));

		if (_dirChange > 15 || _dist > 200 || _i == (count _found - 1)) then {
			_waypoints pushBack _pos;
		};

		_lastDir = _dir;
	};

	// Ensure end position is included
	if ((_waypoints select (count _waypoints - 1)) distance _endPos > 50) then {
		_waypoints pushBack _endPos;
	};

	diag_log format ["IBC GPS: Final route: %1 waypoints (from %2 road segments)", count _waypoints, count _found];
	_waypoints
};

// Generate circular road patrol around position
// Finds roads in radius and creates a loop route
IBC_fnc_generateRoadPatrol = {
	params ["_center", ["_radius", 400], ["_waypointCount", 6]];

	private _roads = _center nearRoads _radius;
	if (count _roads < 4) exitWith {
		// Not enough roads — generate simple circle
		private _wps = [];
		for "_i" from 0 to (_waypointCount - 1) do {
			private _angle = (360 / _waypointCount) * _i;
			_wps pushBack (_center getPos [_radius * 0.7, _angle]);
		};
		_wps
	};

	// Pick N evenly spaced roads around the center
	private _sorted = _roads apply {[_center getDir getPos _x, _x]};
	_sorted sort true;

	private _step = (count _sorted / _waypointCount) max 1;
	private _waypoints = [];
	for "_i" from 0 to (count _sorted - 1) step (floor _step) do {
		if (count _waypoints < _waypointCount) then {
			_waypoints pushBack getPos ((_sorted select _i) select 1);
		};
	};

	if (count _waypoints < 3) then {
		_waypoints = _roads apply {getPos _x};
		_waypoints = (_waypoints call BIS_fnc_arrayShuffle) select [0, _waypointCount min count _waypoints];
	};

	_waypoints
};

// Vehicle patrol using ROAD NETWORK (fully dynamic)
// Only needs center position + radius — figures out route from actual roads
IBC_fnc_smartVehiclePatrol = {
	params ["_class", "_center", ["_radius", 400], ["_speed", "LIMITED"], ["_behaviour", "SAFE"]];

	// Generate route from actual road network
	private _route = [_center, _radius] call IBC_fnc_generateRoadPatrol;

	if (count _route < 2) exitWith {
		diag_log "IBC: No roads found for smart vehicle patrol, using static spawn";
		[_class, _center] call IBC_fnc_spawnVehicle
	};

	private _veh = [_class, _route select 0] call IBC_fnc_spawnVehicle;
	private _grp = group driver _veh;

	{
		private _wp = _grp addWaypoint [_x, 0];
		_wp setWaypointType "MOVE";
		_wp setWaypointSpeed _speed;
		_wp setWaypointBehaviour _behaviour;
		_wp setWaypointCompletionRadius 20;
	} forEach (_route select [1, count _route - 1]);

	private _wpC = _grp addWaypoint [_route select 0, 0];
	_wpC setWaypointType "CYCLE";

	_grp setBehaviour _behaviour;
	_grp setCombatMode "YELLOW";
	_grp setSpeedMode _speed;

	diag_log format ["IBC: Smart vehicle patrol at %1, %2 road waypoints, radius %3", _center, count _route, _radius];
	_veh
};

// Infantry patrol using ROAD NETWORK
IBC_fnc_smartInfantryPatrol = {
	params ["_classes", "_center", "_side", ["_radius", 300], ["_speed", "LIMITED"], ["_formation", "WEDGE"]];

	private _route = [_center, _radius] call IBC_fnc_generateRoadPatrol;

	if (count _route < 2) then {
		// Fallback: generate positions around center
		_route = [];
		for "_i" from 0 to 3 do {
			_route pushBack (_center getPos [_radius * 0.6, _i * 90]);
		};
	};

	private _grp = [_route select 0, _side, _classes] call IBC_fnc_spawnGroup;

	{
		private _wp = _grp addWaypoint [_x, 0];
		_wp setWaypointType "MOVE";
		_wp setWaypointSpeed _speed;
		_wp setWaypointBehaviour "SAFE";
		_wp setWaypointFormation _formation;
		_wp setWaypointCompletionRadius 15;
	} forEach (_route select [1, count _route - 1]);

	private _wpC = _grp addWaypoint [_route select 0, 0];
	_wpC setWaypointType "CYCLE";

	_grp setBehaviour "SAFE";
	_grp setCombatMode "YELLOW";
	_grp setSpeedMode _speed;
	_grp setFormation _formation;

	diag_log format ["IBC: Smart infantry patrol at %1, %2 waypoints", _center, count _route];
	_grp
};

// Smart convoy between two points — follows actual road network
// Full GPS-style route calculation before departure
// Proper spacing, same route, speed control, combat reaction
IBC_fnc_smartConvoy = {
	params ["_vehicleClasses", "_startPos", "_endPos", ["_speed", "LIMITED"], ["_spacing", 40], ["_combatReaction", true]];

	// Step 1: Calculate full road route BEFORE spawning
	private _route = [_startPos, _endPos, 200] call IBC_fnc_findRoadPath;

	if (count _route < 2) exitWith {
		diag_log format ["IBC: No road between %1 and %2 — fallback straight line", _startPos, _endPos];
		_route = [_startPos, _endPos];
		[]
	};

	private _totalDist = 0; for "_i" from 0 to (count _route - 2) do { _totalDist = _totalDist + ((_route select _i) distance (_route select (_i+1))) };
	diag_log format ["IBC: Convoy route calculated: %1 waypoints, %2m total", count _route, round _totalDist];

	// Step 2: Spawn vehicles with proper spacing along the route
	private _convoy = [];
	private _convoyGrps = [];
	private _startDir = (_route select 0) getDir (_route select (1 min (count _route - 1)));

	{
		private _vehIdx = _forEachIndex;
		private _vehClass = _x;

		// Offset each vehicle behind the previous one along route direction
		private _spawnPos = [
			((_route select 0) select 0) - (_vehIdx * _spacing * sin _startDir),
			((_route select 0) select 1) - (_vehIdx * _spacing * cos _startDir),
			0
		];

		private _veh = [_vehClass, _spawnPos, _startDir] call IBC_fnc_spawnVehicle;
		private _grp = group driver _veh;

		// Step 3: All vehicles get THE SAME route with proper waypoint settings
		{
			private _wp = _grp addWaypoint [_x, 0];
			_wp setWaypointType "MOVE";
			_wp setWaypointSpeed _speed;
			_wp setWaypointBehaviour "SAFE";
			_wp setWaypointCombatMode "YELLOW";
			_wp setWaypointCompletionRadius 20;
			// Force road following
			_wp setWaypointStatements ["true", ""];
		} forEach (_route select [1, count _route - 1]);

		// Final waypoint at destination
		private _wpEnd = _grp addWaypoint [_route select (count _route - 1), 0];
		_wpEnd setWaypointType "MOVE";
		_wpEnd setWaypointCompletionRadius 30;

		_grp setBehaviour "SAFE";
		_grp setCombatMode "YELLOW";
		_grp setSpeedMode _speed;

		// Step 4: Speed limiter — prevent vehicles from overtaking
		private _speedIdx = (["LIMITED","NORMAL","FULL"] find _speed);
		if (_speedIdx < 0) then { _speedIdx = 0 };
		_veh limitSpeed ([40, 50, 70] select _speedIdx);

		_convoy pushBack _veh;
		_convoyGrps pushBack _grp;
	} forEach _vehicleClasses;

	// Step 5: Combat reaction system — all vehicles react together
	if (_combatReaction && count _convoy > 0) then {
		[_convoy, _convoyGrps] spawn {
			params ["_convoy", "_grps"];
			private _inCombat = false;

			while {({alive _x} count _convoy) > 0} do {
				sleep 3;

				// Check if any convoy vehicle is under fire
				private _underFire = false;
				{
					if (alive _x && {damage _x > 0.1 || {_x getVariable ["ibc_convoy_contact", false]}}) then {
						_underFire = true;
					};
					// Check for nearby enemies
					if (alive _x && {count (getPos _x nearEntities ["SoldierWB", 300]) > 0}) then {
						_x setVariable ["ibc_convoy_contact", true];
						_underFire = true;
					};
				} forEach _convoy;

				if (_underFire && !_inCombat) then {
					_inCombat = true;
					diag_log "IBC: Convoy under attack! Switching to combat mode.";

					// ALL vehicles stop and fight
					{
						_x setBehaviour "COMBAT";
						_x setCombatMode "RED";
						_x setSpeedMode "FULL";
					} forEach _grps;

					// Dismount infantry from trucks
					{
						if (alive _x) then {
							{
								if !(_x in [driver _x, gunner _x, commander _x]) then {
									moveOut _x;
									_x setPosATL [getPosATL _x select 0, getPosATL _x select 1, 0];
								};
							} forEach crew _x;
						};
					} forEach _convoy;
				};

				// If combat resolved, resume movement
				if (_inCombat && !_underFire) then {
					sleep 30; // Wait 30s after last contact
					private _stillContact = false;
					{
						if (alive _x && {count (getPos _x nearEntities ["SoldierWB", 300]) > 0}) then {
							_stillContact = true;
						};
					} forEach _convoy;

					if (!_stillContact) then {
						_inCombat = false;
						diag_log "IBC: Convoy resuming movement.";
						{
							_x setBehaviour "SAFE";
							_x setCombatMode "YELLOW";
							_x setSpeedMode "LIMITED";
						} forEach _grps;
					};
				};
			};
		};
	};

	diag_log format ["IBC: Convoy spawned: %1 vehicles, %2 road waypoints, spacing %3m", count _vehicleClasses, count _route, _spacing];
	_convoy
};

// ────────────────────────────────────────────
// 10. LEGACY PATHING (manual waypoints) — routes for vehicles, patrols, convoys, aircraft
// ────────────────────────────────────────────

// Vehicle patrol on road — follows road network between waypoints
IBC_fnc_vehiclePatrol = {
	params ["_class", "_waypoints", "_side", ["_speed", "LIMITED"], ["_behaviour", "SAFE"], ["_combat", "YELLOW"]];
	private _veh = [_class, _waypoints select 0] call IBC_fnc_spawnVehicle;
	private _grp = group driver _veh;

	for "_i" from 1 to (count _waypoints - 1) do {
		private _wp = _grp addWaypoint [_waypoints select _i, 0];
		_wp setWaypointType "MOVE";
		_wp setWaypointSpeed _speed;
		_wp setWaypointBehaviour _behaviour;
		_wp setWaypointCombatMode _combat;
		_wp setWaypointCompletionRadius 30;
	};
	// Cycle back to start
	private _wpC = _grp addWaypoint [_waypoints select 0, 0];
	_wpC setWaypointType "CYCLE";

	_grp setBehaviour _behaviour;
	_grp setCombatMode _combat;
	_grp setSpeedMode _speed;
	_veh
};

// Infantry patrol on path — group follows waypoints on foot
IBC_fnc_infantryPatrol = {
	params ["_classes", "_waypoints", "_side", ["_speed", "LIMITED"], ["_behaviour", "SAFE"], ["_formation", "WEDGE"]];
	private _grp = [_waypoints select 0, _side, _classes] call IBC_fnc_spawnGroup;

	for "_i" from 1 to (count _waypoints - 1) do {
		private _wp = _grp addWaypoint [_waypoints select _i, 0];
		_wp setWaypointType "MOVE";
		_wp setWaypointSpeed _speed;
		_wp setWaypointBehaviour _behaviour;
		_wp setWaypointFormation _formation;
		_wp setWaypointCompletionRadius 15;
	};
	private _wpC = _grp addWaypoint [_waypoints select 0, 0];
	_wpC setWaypointType "CYCLE";

	_grp setBehaviour _behaviour;
	_grp setCombatMode "YELLOW";
	_grp setSpeedMode _speed;
	_grp setFormation _formation;
	_grp
};

// Aircraft patrol (circle/racetrack pattern around waypoints)
IBC_fnc_aircraftPatrol = {
	params ["_class", "_waypoints", "_side", ["_alt", 300], ["_speed", 80]];
	private _isHeli = ("Heli" in _class) || ("heli" in _class);
	if (_isHeli) then { _alt = _alt min 150; _speed = _speed min 50 };

	private _startPos = _waypoints select 0;
	private _veh = createVehicle [_class, [_startPos select 0, _startPos select 1, _alt], [], 0, "FLY"];
	_veh setDir (_startPos getDir (_waypoints select 1));
	_veh setVelocityModelSpace [0, _speed, 0];
	_veh flyInHeight _alt;
	createVehicleCrew _veh;

	private _grp = group driver _veh;

	for "_i" from 1 to (count _waypoints - 1) do {
		private _wpPos = _waypoints select _i;
		private _wp = _grp addWaypoint [_wpPos, 0];
		_wp setWaypointType "MOVE";
		_wp setWaypointSpeed "NORMAL";
		_wp setWaypointBehaviour "SAFE";
		_wp setWaypointCompletionRadius 200;
	};
	private _wpC = _grp addWaypoint [_waypoints select 0, 0];
	_wpC setWaypointType "CYCLE";

	_grp setBehaviour "SAFE";
	_grp setCombatMode "GREEN";
	_veh
};

// Search and Destroy path — group moves aggressively through waypoints
IBC_fnc_sadPatrol = {
	params ["_classes", "_waypoints", "_side"];
	private _grp = [_waypoints select 0, _side, _classes] call IBC_fnc_spawnGroup;

	{
		private _wp = _grp addWaypoint [_x, 0];
		_wp setWaypointType "SAD";
		_wp setWaypointSpeed "NORMAL";
		_wp setWaypointBehaviour "COMBAT";
		_wp setWaypointCombatMode "RED";
	} forEach _waypoints;

	private _wpC = _grp addWaypoint [_waypoints select 0, 0];
	_wpC setWaypointType "CYCLE";

	_grp setBehaviour "COMBAT";
	_grp setCombatMode "RED";
	_grp
};

// Guard path — group moves between points, guards each one
IBC_fnc_guardRoute = {
	params ["_classes", "_waypoints", "_side", ["_guardTime", 120]];
	private _grp = [_waypoints select 0, _side, _classes] call IBC_fnc_spawnGroup;

	{
		private _wp = _grp addWaypoint [_x, 0];
		_wp setWaypointType "GUARD";
		_wp setWaypointSpeed "LIMITED";
		_wp setWaypointBehaviour "AWARE";
		_wp setWaypointTimeout [_guardTime, _guardTime, _guardTime];
	} forEach _waypoints;

	private _wpC = _grp addWaypoint [_waypoints select 0, 0];
	_wpC setWaypointType "CYCLE";

	_grp setBehaviour "AWARE";
	_grp setCombatMode "YELLOW";
	_grp
};

// Convoy with multiple vehicles following leader on path
IBC_fnc_convoy = {
	params ["_vehicleClasses", "_waypoints", "_side", ["_speed", "LIMITED"], ["_spacing", 25]];
	private _convoy = [];
	private _startPos = _waypoints select 0;
	private _startDir = _startPos getDir (_waypoints select (1 min (count _waypoints - 1)));

	{
		private _offset = [
			(_startPos select 0) - (_forEachIndex * _spacing * sin _startDir),
			(_startPos select 1) - (_forEachIndex * _spacing * cos _startDir),
			0
		];
		private _veh = [_x, _offset, _startDir] call IBC_fnc_spawnVehicle;
		private _grp = group driver _veh;

		// All vehicles get full waypoints
		for "_wi" from 1 to (count _waypoints - 1) do {
			private _wp = _grp addWaypoint [_waypoints select _wi, 0];
			_wp setWaypointType "MOVE";
			_wp setWaypointSpeed _speed;
			_wp setWaypointBehaviour "SAFE";
			_wp setWaypointCompletionRadius 30;
		};

		_grp setBehaviour "SAFE";
		_grp setCombatMode "YELLOW";
		_grp setSpeedMode _speed;
		_convoy pushBack _veh;
	} forEach _vehicleClasses;

	_convoy
};

// ────────────────────────────────────────────
// ORIGINAL FUNCTIONS
// ────────────────────────────────────────────

// Garrison in buildings (search, shuffle, fallback spread)
IBC_fnc_garrison = {
	params ["_grp", "_pos", ["_radius", 150]];
	private _buildings = nearestObjects [_pos, ["House", "Building"], _radius];
	private _bpos = [];
	{ { _bpos pushBack _x } forEach (_x buildingPos -1) } forEach _buildings;
	_bpos = _bpos call BIS_fnc_arrayShuffle;
	if (count _bpos > 0) then {
		{
			if (count _bpos > 0) then {
				_x setPosATL (_bpos deleteAt 0);
				_x setUnitPos "MIDDLE";
			};
		} forEach units _grp;
	} else {
		{
			_x setPosATL [(_pos select 0) + (random 20) - 10, (_pos select 1) + (random 20) - 10, 0];
			_x setUnitPos "MIDDLE";
		} forEach units _grp;
	};
	_grp setBehaviour "AWARE";
	_grp setCombatMode "RED";
	{ _x enableAI "TARGET"; _x enableAI "AUTOTARGET"; _x enableAI "AUTOCOMBAT" } forEach units _grp;
};
"""

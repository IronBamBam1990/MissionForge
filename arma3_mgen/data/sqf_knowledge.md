# ARMA 3 SQF Knowledge Base - Mission Generator Reference

## Kluczowe komendy do inteligentnego rozmieszczania

### BIS_fnc_findSafePos - Bezpieczna pozycja na ladzie
```sqf
// [center, minDist, maxDist, objDist, waterMode, maxGrad, shoreMode, blacklistPos, defaultPos]
_safePos = [_center, 50, 200, 5, 0, 0.3] call BIS_fnc_findSafePos;
// waterMode: 0=only land, 1=only water, 2=both
// objDist: min distance from objects
// maxGrad: max terrain steepness (0.1=6deg, 0.5=27deg)
```

### buildingPos - Pozycje w budynku (garnizon)
```sqf
_positions = _building buildingPos -1;  // -1 = all positions
_pos = _building buildingPos 3;          // specific index
// Returns [] if no positions
```

### nearestObjects - Szukanie budynkow, obiektow
```sqf
_buildings = nearestObjects [_pos, ["House", "Building"], 200];
_roads = nearestObjects [_pos, ["Road"], 100];
_helipads = nearestObjects [_pos, ["HeliH", "HeliHCivil", "HeliHRescue"], 500];
```

### nearRoads - Szukanie drog
```sqf
_roads = _pos nearRoads 100;  // roads within 100m
```

### isFlatEmpty - Sprawdzenie plaskiej powierzchni (helikoptery)
```sqf
// position isFlatEmpty [minDistance, mode, maxGradient, maxGradientRadius, overLandOrWater, shoreLine, ignoreObject]
_flatPos = _pos isFlatEmpty [10, -1, 0.1, 10, 0];
// Returns [] if not flat enough, or position if OK
```

### setVehiclePosition - Ustawienie pojazdu bezpiecznie
```sqf
_veh setVehiclePosition [_pos, [], 50, "CAN_COLLIDE"];
// Uses createVehicle placement algorithm - finds safe spot
```

### createVehicle - specjalny placement
```sqf
// "NONE" = exact position, "CAN_COLLIDE" = allow collisions, "FLY" = in air
_veh = createVehicle ["B_Heli_Transport_01_F", _pos, [], 0, "NONE"];
_veh setDir 180;
_veh setPos (getPos _veh);  // snap to terrain
```

## Inteligentne rozmieszczanie - wzorce

### Garnizon w budynkach
```sqf
IBC_fnc_garrisonBuildings = {
    params ["_grp", "_pos", "_radius"];
    private _buildings = nearestObjects [_pos, ["House"], _radius];
    private _allBPos = [];
    {
        private _bpos = _x buildingPos -1;
        { _allBPos pushBack _x } forEach _bpos;
    } forEach _buildings;

    {
        if (count _allBPos > 0) then {
            private _idx = floor random count _allBPos;
            _x setPos (_allBPos select _idx);
            _allBPos deleteAt _idx;
            _x disableAI "PATH";
            doStop _x;
        };
    } forEach units _grp;
};
```

### Pojazdy na drogach
```sqf
IBC_fnc_spawnOnRoad = {
    params ["_vehClass", "_pos", "_radius"];
    private _roads = _pos nearRoads _radius;
    if (count _roads > 0) then {
        private _roadPos = getPos (_roads select 0);
        private _veh = createVehicle [_vehClass, _roadPos, [], 0, "NONE"];
        private _roadDir = _roads select 0 call BIS_fnc_dirTo;
        _veh setDir _roadDir;
        _veh
    } else {
        createVehicle [_vehClass, _pos, [], 10, "NONE"]
    };
};
```

### Helikopter na ladowisku/plaskim terenie
```sqf
IBC_fnc_spawnHeli = {
    params ["_heliClass", "_pos", "_radius"];
    // Szukaj helipada
    private _helipads = nearestObjects [_pos, ["HeliH", "HeliHCivil", "HeliHRescue"], _radius];
    if (count _helipads > 0) then {
        private _pad = _helipads select 0;
        private _heli = createVehicle [_heliClass, getPos _pad, [], 0, "NONE"];
        _heli setDir (getDir _pad);
        _heli
    } else {
        // Szukaj plaskiego terenu
        private _flatPos = [_pos, 10, _radius, 15, 0, 0.1] call BIS_fnc_findSafePos;
        private _heli = createVehicle [_heliClass, _flatPos, [], 0, "NONE"];
        _heli
    };
};
```

### Rozrzut jednostek wokol punktu
```sqf
IBC_fnc_spreadUnits = {
    params ["_grp", "_center", "_radius"];
    {
        private _safePos = [_center, 5, _radius, 3, 0, 0.3] call BIS_fnc_findSafePos;
        _x setPos _safePos;
    } forEach units _grp;
};
```

### Checkpoint na drodze
```sqf
IBC_fnc_spawnCheckpoint = {
    params ["_pos", "_radius", "_grp"];
    private _roads = _pos nearRoads _radius;
    if (count _roads > 0) then {
        private _roadPos = getPos (_roads select 0);
        // Barrier
        private _barrier = createVehicle ["Land_RoadBarrier_F", _roadPos, [], 0, "NONE"];
        // Units around checkpoint
        [_grp, _roadPos, 15] call IBC_fnc_spreadUnits;
    };
};
```

## Respawn System
```
// description.ext
respawn = 3;              // BASE
respawnDelay = 600;        // 10 minutes
respawnTemplates[] = {"Wave", "MenuPosition"};
respawnOnStart = -1;

// Markers for respawn positions:
// respawn_west, respawn_west1, respawn_westBase etc.
```

## Briefing (createDiaryRecord)
```sqf
// Sections added in REVERSE order (last added = first shown)
player createDiaryRecord ["Diary", ["V. COMMAND", "text..."]];
player createDiaryRecord ["Diary", ["IV. LOGISTICS", "text..."]];
player createDiaryRecord ["Diary", ["III. EXECUTION", "text..."]];
player createDiaryRecord ["Diary", ["II. MISSION", "text..."]];
player createDiaryRecord ["Diary", ["I. SITUATION", "text..."]];

// Formatting:
// <br/> - line break
// <font color='#FF0000'>red text</font>
// <marker name='marker_name'>link to marker</marker>
// <img image='path.jpg' width='200' height='200'/>
```

## Event Scripts
- onPlayerRespawn.sqf - params ["_newUnit", "_oldUnit", "_respawn", "_respawnDelay"]
- onPlayerKilled.sqf - params ["_oldUnit", "_killer", "_respawn", "_respawnDelay"]
- initServer.sqf - server only, runs once
- initPlayerLocal.sqf - params ["_player", "_didJIP"]
- init.sqf - runs on all machines

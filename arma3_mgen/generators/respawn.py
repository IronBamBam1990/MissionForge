"""Generates respawn-related scripts."""

from ..config_schema import MissionConfig


def generate_on_player_killed(config: MissionConfig) -> str:
    lines = []
    lines.append("// onPlayerKilled.sqf")
    lines.append('params ["_oldUnit", "_killer", "_respawn", "_respawnDelay"];')
    lines.append("")
    if config.respawn.observer_mode:
        lines.append("// Switch to spectator while waiting for respawn")
        lines.append('["Initialize", [player, [], false]] call BIS_fnc_EGSpectator;')
    lines.append("")
    return "\n".join(lines) + "\n"


def generate_on_player_respawn(config: MissionConfig) -> str:
    lines = []
    lines.append("// onPlayerRespawn.sqf")
    lines.append('params ["_newUnit", "_oldUnit", "_respawn", "_respawnDelay"];')
    lines.append("")
    if config.respawn.observer_mode:
        lines.append("// Exit spectator on respawn")
        lines.append('["Terminate"] call BIS_fnc_EGSpectator;')
    lines.append("")
    lines.append("// Water safety + terrain snap on respawn")
    lines.append("// Uses BIS_fnc_findSafePos (client-safe, waterMode=0 = land only)")
    lines.append("private _p = getPosATL _newUnit;")
    lines.append("if (surfaceIsWater _p || {getTerrainHeightASL [_p select 0, _p select 1] < 0}) then {")
    lines.append("\tprivate _safe = [_p, 0, 500, 3, 0, 0.7, 0, [], [_p, _p]] call BIS_fnc_findSafePos;")
    lines.append("\tif (surfaceIsWater _safe || {getTerrainHeightASL [_safe select 0, _safe select 1] < 0}) then {")
    lines.append("\t\t_safe = [_p, 50, 1500, 3, 0, 0.8, 0, [], [_p, _p]] call BIS_fnc_findSafePos;")
    lines.append("\t};")
    lines.append("\t_newUnit setPosATL [_safe select 0, _safe select 1, 0];")
    lines.append('\tdiag_log format ["IBC: Respawn - player moved from water to %1", _safe];')
    lines.append("} else {")
    lines.append("\t_newUnit setPosATL [_p select 0, _p select 1, 0];")
    lines.append("};")
    lines.append("")
    lines.append("// Backup check after delay (catches late position update from server)")
    lines.append("_newUnit spawn {")
    lines.append("\tsleep 2;")
    lines.append("\tprivate _p2 = getPosATL _this;")
    lines.append("\tif (surfaceIsWater _p2 || {getTerrainHeightASL [_p2 select 0, _p2 select 1] < 0}) then {")
    lines.append("\t\tprivate _safe2 = [_p2, 0, 500, 3, 0, 0.7, 0, [], [_p2, _p2]] call BIS_fnc_findSafePos;")
    lines.append("\t\tif (surfaceIsWater _safe2 || {getTerrainHeightASL [_safe2 select 0, _safe2 select 1] < 0}) then {")
    lines.append("\t\t\t_safe2 = [_p2, 50, 1500, 3, 0, 0.8, 0] call BIS_fnc_findSafePos;")
    lines.append("\t\t};")
    lines.append("\t\t_this setPosATL [_safe2 select 0, _safe2 select 1, 0];")
    lines.append('\t\tdiag_log format ["IBC: Respawn delayed fix - moved from water to %1", _safe2];')
    lines.append("\t};")
    lines.append("};")
    lines.append("")
    return "\n".join(lines) + "\n"

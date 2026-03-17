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
    lines.append("// Snap to terrain surface to prevent underground respawn")
    lines.append("_newUnit setPosATL [getPosATL _newUnit select 0, getPosATL _newUnit select 1, 0.1];")
    lines.append("")
    return "\n".join(lines) + "\n"

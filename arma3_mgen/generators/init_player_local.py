"""Generates initPlayerLocal.sqf - client-side initialization."""

from ..config_schema import MissionConfig
from .briefing import generate_briefing_body


def generate_init_player_local(config: MissionConfig) -> str:
    lines = []
    lines.append("// Player local initialization")
    lines.append('params ["_player", "_didJIP"];')
    lines.append("")
    lines.append("// IMMEDIATE terrain snap - player spawns at 500m ASL in SQM, snap to ground")
    lines.append("private _p = getPosATL _player;")
    lines.append("_player setPosATL [_p select 0, _p select 1, 0];")
    lines.append("")
    lines.append("// Backup: repeat snap after short delay (in case first one failed)")
    lines.append("[] spawn {")
    lines.append("\tsleep 0.5;")
    lines.append("\tprivate _p2 = getPosATL player;")
    lines.append("\tplayer setPosATL [_p2 select 0, _p2 select 1, 0];")
    lines.append("};")
    lines.append("")
    lines.append("// Briefing - inline (no execVM needed)")
    lines.append("waitUntil {!isNull player};")
    lines.append(generate_briefing_body(config))
    lines.append("")
    return "\n".join(lines) + "\n"

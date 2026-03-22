"""Generates description.ext - complete mission configuration."""

from ..config_schema import MissionConfig


def generate_description_ext(config: MissionConfig) -> str:
    display = config.meta.display_name or config.meta.mission_name
    lines = []

    # Presentation
    lines.append(f'author = "{config.meta.author}";')
    lines.append(f'onLoadName = "{display}";')
    lines.append(f'onLoadMission = "{display}";')
    lines.append(f'overviewText = "{display}";')
    lines.append("")

    # Respawn
    lines.append("// Respawn")
    lines.append("respawn = 3;  // BASE")
    lines.append(f"respawnDelay = {config.respawn.wave_interval};")
    lines.append('respawnTemplates[] = {"Wave", "MenuPosition", "Spectator"};')
    lines.append("respawnOnStart = -1;")
    lines.append("")

    # Respawn dialog
    if config.respawn.observer_mode:
        lines.append("// Spectator in respawn screen")
        lines.append("respawnDialog = 1;")
        lines.append("")

    # Tickets
    if config.respawn.tickets_per_player > 0:
        lines.append(f"// Tickets - {config.respawn.tickets_per_player} per player")
        lines.append("class CfgRespawnTemplates")
        lines.append("{")
        lines.append('\tclass Tickets')
        lines.append("\t{")
        lines.append('\t\tonPlayerKilled = "onPlayerKilled.sqf";')
        lines.append("\t};")
        lines.append("};")
        lines.append("")

    # Misc settings
    lines.append("// Settings")
    lines.append("enableDebugConsole = 1;")
    lines.append("disabledAI = 0;  // 0 = AI fills empty player slots (bots replace absent players)")
    lines.append("aiKills = 0;")
    lines.append("")

    # Corpse/wreck management
    lines.append("// Corpse and wreck management")
    lines.append("corpseManagerMode = 1;")
    lines.append("corpseLimit = 20;")
    lines.append("corpseRemovalMinTime = 120;")
    lines.append("corpseRemovalMaxTime = 600;")
    lines.append("wreckManagerMode = 1;")
    lines.append("wreckLimit = 10;")
    lines.append("wreckRemovalMinTime = 120;")
    lines.append("wreckRemovalMaxTime = 600;")
    lines.append("")

    lines.append("")

    # Debriefing
    lines.append("// Debriefing")
    lines.append("class CfgDebriefing")
    lines.append("{")
    lines.append('\tclass End1')
    lines.append("\t{")
    lines.append('\t\ttitle = "Mission Complete";')
    lines.append('\t\tdescription = "All objectives completed.";')
    lines.append("\t\tpictureBackground = \"\";")
    lines.append("\t};")
    lines.append('\tclass Lose')
    lines.append("\t{")
    lines.append('\t\ttitle = "Mission Failed";')
    lines.append('\t\tdescription = "Objectives not completed.";')
    lines.append("\t\tpictureBackground = \"\";")
    lines.append("\t};")
    lines.append("};")

    return "\n".join(lines) + "\n"

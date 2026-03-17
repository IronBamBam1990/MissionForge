"""Generates scripts/briefing.sqf - in-game OPORD briefing."""

from ..config_schema import MissionConfig


def generate_briefing_body(config: MissionConfig) -> str:
    """Generate just the createDiaryRecord calls (no params/waitUntil wrapper).

    Used by initPlayerLocal.sqf to inline the briefing.
    """
    b = config.briefing
    lines = []

    # Add sections in reverse order so they display correctly
    sections = []
    if b.command_signal:
        sections.append(("V. DOWODZENIE I LACZNOSC", b.command_signal))
    if b.logistics:
        sections.append(("IV. ZABEZPIECZENIE LOGISTYCZNE", b.logistics))
    if b.execution:
        sections.append(("III. REALIZACJA", b.execution))
    if b.mission:
        sections.append(("II. ZADANIE", b.mission))
    if b.situation:
        sections.append(("I. SYTUACJA", b.situation))

    # Auto-generate radio info if not in command_signal
    if config.radio.system and config.radio.system != "none":
        radio_info = f"System lacznosci: {config.radio.system.upper()}<br/>"
        radio_info += "Przydzial radii:<br/>"
        radio_info += "- PRC-343: kazdy zolnierz (zasieg 500m)<br/>"
        radio_info += "- PRC-152: dowodcy druzyn, SL, TL (zasieg 5km)<br/>"
        radio_info += "- PRC-117F: PL, RATELO, FAC (zasieg 20km)<br/>"
        if config.radio.channels:
            radio_info += "<br/>Kanaly:<br/>"
            for ch in config.radio.channels:
                name = ch.get("name", "?")
                freq = ch.get("frequency", "?")
                radio_info += f"- {name}: {freq}<br/>"
        if not b.command_signal:
            sections.append(("V. DOWODZENIE I LACZNOSC", radio_info))
        else:
            # Append radio info to existing command_signal
            idx = next((i for i, s in enumerate(sections) if "DOWODZENIE" in s[0]), None)
            if idx is not None:
                sections[idx] = (sections[idx][0], sections[idx][1] + "<br/><br/>" + radio_info)

    for title, content in sections:
        escaped = _escape_sqf(content)
        lines.append(f'player createDiaryRecord ["Diary", ["{title}",')
        lines.append(f'\t"{escaped}"')
        lines.append("]];")
        lines.append("")

    return "\n".join(lines)


def generate_briefing(config: MissionConfig) -> str:
    """Generate briefing.sqf file (kept for backwards compatibility)."""
    lines = []
    lines.append("// Briefing - OPORD")
    lines.append("// Sections appear in reverse order of creation")
    lines.append('params ["_player"];')
    lines.append("")
    lines.append("waitUntil {!isNull player};")
    lines.append("")
    lines.append(generate_briefing_body(config))
    return "\n".join(lines) + "\n"


def _escape_sqf(text: str) -> str:
    """Escape text for SQF string - double quotes and newlines to <br/>."""
    text = text.replace('"', '""')
    text = text.replace("\n", "<br/>")
    text = text.replace("\r", "")
    return text

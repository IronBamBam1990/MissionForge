"""Generates init.sqf - GPS, optional ACE3 items."""

from ..config_schema import MissionConfig


def generate_init_sqf(config: MissionConfig) -> str:
    lines = []
    display = config.meta.display_name or config.meta.mission_name
    lines.append(f"// {display}")
    lines.append("// IBC ARMA 3 Mission Generator")
    lines.append("")
    lines.append("waitUntil {!isNull player};")
    lines.append("waitUntil {time > 0};")
    lines.append("")

    # GPS always
    lines.append("// GPS + minimap")
    lines.append("player linkItem 'ItemGPS';")
    lines.append("showGPS true;")
    lines.append("")

    # Standard items always
    lines.append("// Standard items")
    lines.append("player linkItem 'ItemMap';")
    lines.append("player linkItem 'ItemCompass';")
    lines.append("player linkItem 'ItemWatch';")
    lines.append("player linkItem 'ItemRadio';")
    lines.append("")

    # ACE3 items only when enabled
    if config.ace3_enabled:
        lines.append("// ACE3 items")
        lines.append('if (isClass (configFile >> "CfgPatches" >> "ace_microdagr")) then {')
        lines.append('\tplayer addItem "ACE_microDAGR";')
        lines.append("};")
        lines.append('if (isClass (configFile >> "CfgPatches" >> "ace_interaction")) then {')
        lines.append('\tplayer addItem "ACE_Cellphone";')
        lines.append("};")
        lines.append("")

    # Route markers
    if config.markers.routes:
        lines.append("// Route markers")
        for route in config.markers.routes:
            if len(route.points) >= 2:
                flat = []
                for pt in route.points:
                    flat.extend([round(pt[0], 1), round(pt[2], 1)])
                coords = ",".join(str(c) for c in flat)
                lines.append(f'_m = createMarkerLocal ["{route.name}", [{round(route.points[0][0],1)},{round(route.points[0][2],1)}]];')
                lines.append(f'_m setMarkerShapeLocal "POLYLINE";')
                lines.append(f'_m setMarkerPolylineLocal [{coords}];')
                lines.append(f'_m setMarkerColorLocal "{route.color}";')
                if route.text:
                    lines.append(f'_m setMarkerTextLocal "{route.text}";')
                lines.append("")

    return "\n".join(lines) + "\n"

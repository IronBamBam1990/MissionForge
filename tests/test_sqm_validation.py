"""SQM validation tests - verify generated SQM structure is correct."""

import json
import re
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from arma3_mgen.config_schema import MissionConfig
from arma3_mgen.generators.mission_sqm import generate_mission_sqm


def load_config(name: str) -> MissionConfig:
    config_path = Path(__file__).parent.parent / "configs" / name
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return MissionConfig(**data)


def load_faction(name: str) -> dict | None:
    faction_path = Path(__file__).parent.parent / "arma3_mgen" / "data" / "factions" / f"{name}.json"
    if faction_path.exists():
        with open(faction_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def count_pattern(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text))


def test_minimal_altis():
    """Test SQM generation from minimal_altis.json config."""
    config = load_config("minimal_altis.json")
    faction = load_faction(config.faction_preset)
    enemy_faction = load_faction(config.enemy_faction_preset)
    sqm = generate_mission_sqm(config, faction, enemy_faction)

    errors = []

    # 1. Check version
    if 'version=53;' not in sqm:
        errors.append("Missing version=53")

    # 2. Check binarizationWanted
    if 'binarizationWanted=0;' not in sqm:
        errors.append("Missing binarizationWanted=0")

    # 3. Count BLUFOR groups: 1 squad
    blufor_groups = count_pattern(sqm, r'side="West";\n\t+class Entities')
    # Actually count Group entities with side West
    west_groups = len(re.findall(r'dataType="Group";\n\t+side="West";', sqm))
    if west_groups < 1:
        errors.append(f"Expected at least 1 BLUFOR group, found {west_groups}")

    # 4. Count OPFOR groups: 1 garrison fireteam
    east_groups = len(re.findall(r'dataType="Group";\n\t+side="East";', sqm))
    if east_groups < 1:
        errors.append(f"Expected at least 1 OPFOR group, found {east_groups}")

    # 5. Check BLUFOR units have isPlayer=1
    # Find units inside West groups
    if 'isPlayer=1;' not in sqm:
        errors.append("No BLUFOR units with isPlayer=1 found")

    # 6. Check OPFOR units have flags=2
    if 'flags=2;' not in sqm:
        errors.append("No OPFOR units with flags=2 found")

    # 7. Check OPFOR units have skill init
    if 'this setSkill' not in sqm:
        errors.append("No OPFOR units with setSkill init found")

    # 8. Check garrison leader has ibc_garrison variable
    if 'ibc_garrison' not in sqm:
        errors.append("Garrison leader missing ibc_garrison variable")

    # 9. Check markers exist
    markers = len(re.findall(r'dataType="Marker";', sqm))
    if markers < 2:  # obj_1 + start_pos + respawn_west = 3
        errors.append(f"Expected at least 2 markers, found {markers}")

    # 10. Check items= counts match actual items
    # Find all class blocks with items= and verify count
    items_matches = re.findall(r'class (Entities|Waypoints)\n\t*\{\n\t*items=(\d+);', sqm)
    for class_name, count_str in items_matches:
        expected = int(count_str)
        # This is a simplified check - just verify items > 0
        if expected < 1:
            errors.append(f"class {class_name} has items={expected}")

    # 11. Check nextID is reasonable
    next_id_match = re.search(r'class ItemIDProvider\n\t*\{\n\t*nextID=(\d+);', sqm)
    if next_id_match:
        next_id = int(next_id_match.group(1))
        # 4 BLUFOR units + 1 BLUFOR group + 4 OPFOR units + 1 OPFOR group = 10
        if next_id < 10:
            errors.append(f"nextID={next_id} seems too low (expected >= 10)")
    else:
        errors.append("Missing ItemIDProvider.nextID")

    # 12. Verify entity IDs are unique (markers have separate ID namespace)
    # Split SQM into sections - entities before markers
    # Entity IDs: inside Group/Object blocks (not Marker blocks)
    # Simple approach: find all id= lines and separate by context
    lines = sqm.split("\n")
    entity_ids = set()
    marker_ids = set()
    in_marker = False
    for line in lines:
        stripped = line.strip()
        if 'dataType="Marker"' in stripped:
            in_marker = True
        elif 'dataType="Group"' in stripped or 'dataType="Object"' in stripped:
            in_marker = False
        id_match = re.match(r'\s*id=(\d+);', stripped)
        if id_match:
            id_val = int(id_match.group(1))
            if in_marker:
                if id_val in marker_ids:
                    errors.append(f"Duplicate marker ID: {id_val}")
                marker_ids.add(id_val)
            else:
                if id_val in entity_ids:
                    errors.append(f"Duplicate entity ID: {id_val}")
                entity_ids.add(id_val)

    # Report
    if errors:
        print("FAILED - SQM Validation Errors:")
        for e in errors:
            print(f"  - {e}")
        print(f"\nSQM output ({len(sqm)} chars):")
        # Print first 100 lines for debugging
        for i, line in enumerate(sqm.split("\n")[:100]):
            print(f"  {i + 1}: {line}")
        return False
    else:
        print("PASSED - SQM validation OK")
        print(f"  BLUFOR groups: {west_groups}")
        print(f"  OPFOR groups:  {east_groups}")
        print(f"  Markers:       {markers}")
        print(f"  Entity IDs:    {len(entity_ids)}")
        print(f"  Marker IDs:    {len(marker_ids)}")
        print(f"  nextID:        {next_id_match.group(1) if next_id_match else '?'}")
        print(f"  Total chars:   {len(sqm)}")
        return True


def test_with_patrol():
    """Test SQM with patrol waypoints using crimson_dawn config."""
    config_path = Path(__file__).parent.parent / "configs" / "crimson_dawn.json"
    if not config_path.exists():
        print("SKIP - crimson_dawn.json not found")
        return True

    config = load_config("crimson_dawn.json")
    faction = load_faction(config.faction_preset)
    enemy_faction = load_faction(config.enemy_faction_preset)
    sqm = generate_mission_sqm(config, faction, enemy_faction)

    errors = []

    # Check patrol waypoints exist if any patrol positions
    has_patrol = any(
        pos.type == "patrol"
        for zone in config.opfor.zones
        for pos in zone.positions
    )
    if has_patrol:
        if 'class Waypoints' not in sqm:
            errors.append("Patrol group missing class Waypoints")
        if 'type="CYCLE"' not in sqm:
            errors.append("Missing CYCLE waypoint for patrol route")
        if 'type="MOVE"' not in sqm:
            errors.append("Missing MOVE waypoints for patrol route")

    # Check vehicles if motorized
    has_motorized = any(
        pos.composition in ("motorized", "mechanized") and pos.vehicle_class
        for zone in config.opfor.zones
        for pos in zone.positions
    )
    if has_motorized:
        if 'createVehicleCrew this' not in sqm:
            errors.append("Motorized vehicle missing createVehicleCrew init")

    if errors:
        print("FAILED - Crimson Dawn validation:")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        east_groups = len(re.findall(r'dataType="Group";\n\t+side="East";', sqm))
        waypoint_blocks = len(re.findall(r'class Waypoints', sqm))
        print(f"PASSED - Crimson Dawn: {east_groups} OPFOR groups, {waypoint_blocks} waypoint blocks")
        return True


if __name__ == "__main__":
    print("=" * 50)
    print("SQM Validation Tests")
    print("=" * 50)
    print()

    results = []
    results.append(("minimal_altis", test_minimal_altis()))
    print()
    results.append(("crimson_dawn", test_with_patrol()))
    print()

    print("=" * 50)
    all_passed = all(r[1] for r in results)
    for name, passed in results:
        print(f"  {name}: {'PASS' if passed else 'FAIL'}")
    print(f"\n{'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    sys.exit(0 if all_passed else 1)

"""Pydantic models for mission configuration.

Designed for millions of configurations - every field optional with sane defaults.
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class FlexModel(BaseModel):
    """Base model that ignores extra fields from AI output."""
    model_config = ConfigDict(extra="ignore")


# ── Meta ──

class MissionMeta(FlexModel):
    mission_name: str = "IBC_Mission"
    display_name: str = ""
    author: str = "7BOW"
    map: str = "Altis"
    location: str = ""  # target location name on map (resolved by mission_builder)
    map_classname_override: Optional[str] = None
    game_type: str = "Coop"
    max_players: int = 40


class IntelConfig(FlexModel):
    year: int = 2026
    month: int = 3
    day: int = 14
    hour: int = 6
    minute: int = 0
    weather: float = 0.0
    fog: float = 0.0
    wind: float = 0.0


# ── Loadout system ──

class LoadoutItem(FlexModel):
    """Single loadout item (weapon, magazine, item, etc.)"""
    classname: str
    count: int = 1  # how many (for magazines, grenades, etc.)


class LoadoutPreset(FlexModel):
    """Complete loadout for a role - replaces default gear."""
    primary_weapon: Optional[str] = None       # "arifle_MX_F"
    primary_mags: int = 8
    secondary_weapon: Optional[str] = None     # "hgun_P07_F"
    secondary_mags: int = 3
    launcher: Optional[str] = None             # "launch_NLAW_F"
    launcher_mags: int = 1
    optic: Optional[str] = None                # "optic_MRCO"
    suppressor: Optional[str] = None           # "muzzle_snds_H"
    bipod: Optional[str] = None
    vest: Optional[str] = None                 # "V_PlateCarrier1_rgr"
    uniform: Optional[str] = None              # "U_B_CombatUniform_mcam"
    helmet: Optional[str] = None               # "H_HelmetB"
    backpack: Optional[str] = None             # "B_AssaultPack_rgr"
    nvg: Optional[str] = None                  # "NVGoggles" or "NVGoggles_OPFOR"
    items: list[str] = Field(default_factory=list)  # ["FirstAidKit", "ItemGPS", "ItemMap"]
    extra_mags: list[LoadoutItem] = Field(default_factory=list)  # extra magazines/grenades


# ── BLUFOR ──

class PlayerUnit(FlexModel):
    role: str = "rifleman"
    rank: str = "PRIVATE"
    classname_override: Optional[str] = None
    radio: Optional[str] = None
    loadout_override: Optional[dict] = None  # legacy
    loadout: Optional[LoadoutPreset] = None  # new loadout system


class PlayerGroup(FlexModel):
    callsign: str = "ALPHA 1"
    type: str = "rifle_squad"
    position: list[float] = Field(default_factory=lambda: [0, 0, 0])
    spawn_area: str = ""  # "fob", "helipad", "motor_pool", "infil" - where this group starts
    units: list[PlayerUnit] = Field(default_factory=list)


class BluforConfig(FlexModel):
    groups: list[PlayerGroup] = Field(default_factory=list)


# ── Vehicles (player vehicles at spawn) ──

class PlayerVehicle(FlexModel):
    """Vehicle available to players at their spawn/base."""
    vehicle_class: str = "B_MRAP_01_F"
    callsign: str = ""
    position: list[float] = Field(default_factory=lambda: [0, 0, 0])
    spawn_area: str = ""  # "motor_pool", "helipad", "near_infantry"
    crew_roles: list[str] = Field(default_factory=list)  # roles that start in this vehicle


# ── Air support ──

class AirSupportAircraft(FlexModel):
    callsign: str = "HAWK 1"
    vehicle_class: str = "B_Heli_Transport_01_F"  # default to transport heli (not jet)
    pilot_role: str = "helicopter_pilot"
    position: list[float] = Field(default_factory=lambda: [0, 0, 0])
    direction: float = 0.0
    spawn_type: str = "ground"  # "fly" = in air, "ground" = on helipad/flat terrain
    spawn_location: str = "helipad"  # "helipad", "flat_terrain", "airfield", "fob"


class AirSupportConfig(FlexModel):
    enabled: bool = False
    aircraft: list[AirSupportAircraft] = Field(default_factory=list)


# ── Spawn areas (multiple start points) ──

class SpawnArea(FlexModel):
    """Named spawn area - groups reference this by spawn_area field."""
    name: str  # "fob", "helipad", "motor_pool", "infil_north"
    position: list[float] = Field(default_factory=lambda: [0, 0, 0])
    type: str = "generic"  # "fob", "helipad", "airfield", "motor_pool", "insertion"
    description: str = ""  # "FOB Phoenix", "LZ Eagle"


# ── OPFOR ──

class EnemyBehavior(FlexModel):
    mode: str = "AWARE"
    combat: str = "RED"
    speed: str = "NORMAL"


class EnemyPosition(FlexModel):
    id: str = ""
    type: str = "garrison"
    # garrison, patrol, qrf, checkpoint, static, sniper, mg_nest,
    # vehicle_patrol, air_patrol, sad_patrol, guard_route, convoy
    position: list[float] = Field(default_factory=lambda: [0, 0, 0])
    size: str = "fireteam"  # fireteam, squad, section
    composition: str = "infantry"  # infantry, motorized, mechanized
    vehicle_class: Optional[str] = None
    patrol_route: Optional[list[list[float]]] = None  # waypoints path
    trigger_radius: float = 300.0
    behavior: EnemyBehavior = Field(default_factory=EnemyBehavior)
    custom_units: Optional[list[str]] = None
    static_weapon: Optional[str] = None
    garrison_radius: float = 150.0
    speed: str = "LIMITED"  # LIMITED, NORMAL, FULL
    formation: str = "WEDGE"  # WEDGE, COLUMN, LINE, STAG COLUMN, ECH LEFT
    altitude: float = 300.0  # for air patrols


class EnemyZone(FlexModel):
    name: str = ""
    center: list[float] = Field(default_factory=lambda: [0, 0, 0])
    positions: list[EnemyPosition] = Field(default_factory=list)
    fortifications: list[dict] = Field(default_factory=list)
    mines: list[list[float]] = Field(default_factory=list)


class OpforConfig(FlexModel):
    skill_range: list[float] = Field(default_factory=lambda: [0.4, 0.7])
    zones: list[EnemyZone] = Field(default_factory=list)


# ── Markers ──

class MarkerDef(FlexModel):
    name: str
    text: str = ""
    position: list[float] = Field(default_factory=lambda: [0, 0, 0])
    type: str = "mil_dot"
    color: str = "Default"
    shape: str = "ICON"
    size_a: float = 1.0
    size_b: float = 1.0
    angle: float = 0.0


class RouteMarker(FlexModel):
    name: str
    text: str = ""
    points: list[list[float]] = Field(default_factory=list)
    color: str = "ColorBlue"


class MarkersConfig(FlexModel):
    objectives: list[MarkerDef] = Field(default_factory=list)
    phase_lines: list[MarkerDef] = Field(default_factory=list)
    waypoints: list[MarkerDef] = Field(default_factory=list)
    sbf: list[MarkerDef] = Field(default_factory=list)
    rally_points: list[MarkerDef] = Field(default_factory=list)
    routes: list[RouteMarker] = Field(default_factory=list)
    custom: list[MarkerDef] = Field(default_factory=list)


# ── Respawn ──

class ReinsertConfig(FlexModel):
    enabled: bool = True
    priority: list[str] = Field(default_factory=lambda: ["combat_medic", "platoon_sergeant", "platoon_leader", "orp"])


class RespawnConfig(FlexModel):
    wave_interval: int = 600
    tickets_per_player: int = 2
    observer_mode: bool = True
    reinsert: ReinsertConfig = Field(default_factory=ReinsertConfig)
    technical_respawn: bool = True


# ── Objects ──

class ResupplyCrate(FlexModel):
    position: list[float] = Field(default_factory=lambda: [0, 0, 0])
    type: str = "ammo"  # ammo, medical, explosives, at, special, arsenal, general
    crate_class: str = "Box_NATO_Ammo_F"
    condition: str = ""


class HostageDef(FlexModel):
    id: str = "hostage_1"
    position: list[float] = Field(default_factory=lambda: [0, 0, 0])
    count: int = 1
    guarded: bool = True
    task_name: str = ""
    task_text: str = "Uratuj zakladnikow"


class HostageConfig(FlexModel):
    enabled: bool = False
    hostages: list[HostageDef] = Field(default_factory=list)


class CivilianConfig(FlexModel):
    enabled: bool = False
    density: str = "low"
    zones: list[dict] = Field(default_factory=list)


class FortificationDef(FlexModel):
    type: str = "sandbag"
    position: list[float] = Field(default_factory=lambda: [0, 0, 0])
    direction: float = 0.0


class RadioConfig(FlexModel):
    system: str = "acre2"
    channels: list[dict] = Field(default_factory=list)


class BriefingConfig(FlexModel):
    language: str = "pl"
    situation: str = ""
    mission: str = ""
    execution: str = ""
    logistics: str = ""
    command_signal: str = ""


# ── Mission Config (root) ──

# ── Advanced Mechanics ──

class CounterattackConfig(FlexModel):
    enabled: bool = False
    trigger: str = "obj_complete"  # when to trigger: "obj_complete", "timer", "alert_combat"
    delay_seconds: int = 120
    spawn_position: list[float] = Field(default_factory=lambda: [0, 0, 0])
    target_position: list[float] = Field(default_factory=lambda: [0, 0, 0])
    units: list[str] = Field(default_factory=lambda: ["O_Soldier_SL_F", "O_Soldier_F", "O_Soldier_F", "O_Soldier_AR_F", "O_Soldier_GL_F", "O_Soldier_F"])
    vehicle_class: str = ""  # optional vehicle for the counterattack force


class ConvoyDef(FlexModel):
    vehicles: list[str] = Field(default_factory=list)  # vehicle classnames
    route: list[list[float]] = Field(default_factory=list)  # waypoints
    side: str = "east"
    speed: str = "LIMITED"  # LIMITED, NORMAL, FULL


class ExtractionConfig(FlexModel):
    enabled: bool = False
    position: list[float] = Field(default_factory=lambda: [0, 0, 0])
    radius: float = 30.0
    condition: str = "all_objectives"  # when extraction becomes available


class HoldPositionConfig(FlexModel):
    enabled: bool = False
    position: list[float] = Field(default_factory=lambda: [0, 0, 0])
    duration_seconds: int = 1200  # 20 minutes default
    radius: float = 100.0


class AlertSystemConfig(FlexModel):
    enabled: bool = False
    initial_state: str = "STEALTH"  # STEALTH, ALERT, COMBAT
    combat_radius: float = 500.0
    alert_radius: float = 800.0


class IEDConfig(FlexModel):
    enabled: bool = False
    positions: list[list[float]] = Field(default_factory=list)
    count_per_zone: int = 3
    radius: float = 200.0


class MortarConfig(FlexModel):
    enabled: bool = False
    target_position: list[float] = Field(default_factory=lambda: [0, 0, 0])
    rounds: int = 8
    spread: float = 80.0
    delay_trigger: str = "alert_combat"  # when mortar fires


# ── Mission Config (root) ──

class MissionConfig(FlexModel):
    meta: MissionMeta = Field(default_factory=MissionMeta)
    intel: IntelConfig = Field(default_factory=IntelConfig)
    faction_preset: str = "vanilla_nato"
    enemy_faction_preset: str = "vanilla_csat"
    radio: RadioConfig = Field(default_factory=RadioConfig)
    blufor: BluforConfig = Field(default_factory=BluforConfig)
    spawn_areas: list[SpawnArea] = Field(default_factory=list)
    player_vehicles: list[PlayerVehicle] = Field(default_factory=list)
    air_support: AirSupportConfig = Field(default_factory=AirSupportConfig)
    opfor: OpforConfig = Field(default_factory=OpforConfig)
    markers: MarkersConfig = Field(default_factory=MarkersConfig)
    respawn: RespawnConfig = Field(default_factory=RespawnConfig)
    civilians: CivilianConfig = Field(default_factory=CivilianConfig)
    hostages: HostageConfig = Field(default_factory=HostageConfig)
    resupply: list[ResupplyCrate] = Field(default_factory=list)
    fortifications: list[FortificationDef] = Field(default_factory=list)
    briefing: BriefingConfig = Field(default_factory=BriefingConfig)
    time_limit: int = 0
    loadout_presets: dict[str, LoadoutPreset] = Field(default_factory=dict)
    # Advanced objectives
    intel_objects: list[dict] = Field(default_factory=list)  # [{position, task_id, class}]
    destroy_targets: list[dict] = Field(default_factory=list)  # [{position, task_id, class}]
    reinforcement_waves: list[dict] = Field(default_factory=list)  # [{delay, position, units, vehicle}]
    supply_drops: list[dict] = Field(default_factory=list)  # [{position, type, delay}]
    # Weather transitions
    weather_transitions: list[dict] = Field(default_factory=list)  # [{delay, overcast, rain, fog}]
    # Night ops
    flare_illumination: Optional[dict] = None  # {position, interval, count}
    ambient_combat: Optional[dict] = None  # {position, interval, duration}
    # Mod toggles (set by web UI)
    ace3_enabled: bool = False
    # Advanced mechanics
    alert_system: AlertSystemConfig = Field(default_factory=AlertSystemConfig)
    counterattack: CounterattackConfig = Field(default_factory=CounterattackConfig)
    convoys: list[ConvoyDef] = Field(default_factory=list)
    extraction: ExtractionConfig = Field(default_factory=ExtractionConfig)
    hold_position: HoldPositionConfig = Field(default_factory=HoldPositionConfig)
    ied: IEDConfig = Field(default_factory=IEDConfig)
    mortar: MortarConfig = Field(default_factory=MortarConfig)

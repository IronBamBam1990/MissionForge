"""FastAPI web application for ARMA 3 Mission Generator.

Prompt-centric: user describes mission in natural language,
Claude CLI parses it into config, engine generates files.
"""

import asyncio
import json
import sys
import tempfile
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

sys.path.insert(0, str(Path(__file__).parent.parent))

from arma3_mgen.config_loader import load_config_from_dict, MAPS_DB
from arma3_mgen.config_schema import MissionConfig
from arma3_mgen.generators.mission_folder import generate_mission
from arma3_mgen.mission_builder import compute_mission_layout

app = FastAPI(title="IBC ARMA 3 Mission Generator")

static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))

data_dir = Path(__file__).parent.parent / "arma3_mgen" / "data"
DEFAULT_OUTPUT = Path.home() / "Documents" / "Arma 3" / "missions"

# Load schema example for Claude prompt
SCHEMA_EXAMPLE = json.dumps(MissionConfig().model_dump(), indent=2)

# Load available factions
def _load_factions_summary():
    factions_dir = data_dir / "factions"
    result = {}
    if factions_dir.exists():
        for f in factions_dir.glob("*.json"):
            with open(f, "r", encoding="utf-8") as fp:
                d = json.load(fp)
                result[f.stem] = d.get("faction_name", f.stem)
    return result

FACTIONS_SUMMARY = _load_factions_summary()

# Load locations database
def _load_locations():
    loc_file = data_dir / "locations.json"
    if loc_file.exists():
        with open(loc_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

LOCATIONS_DB = _load_locations()

def _build_locations_prompt():
    """Build locations reference for the system prompt."""
    lines = []
    for map_name, map_data in LOCATIONS_DB.items():
        size = map_data.get("_size", "?")
        lines.append(f"\n{map_name} (rozmiar {size}x{size}):")
        for category, locations in map_data.items():
            if category.startswith("_"):
                continue
            for name, coords in locations.items():
                lines.append(f"  {name}: [{coords[0]}, 0, {coords[1]}]")
    return "\n".join(lines)


def _build_system_prompt():
    """Build the system prompt for Claude CLI - detailed, framework handles coordinates."""
    factions_list = "\n".join(f"  - {k}: {v}" for k, v in FACTIONS_SUMMARY.items())
    maps_list = "\n".join(f"  - {name}" for name in sorted(MAPS_DB.keys()))

    return f"""Jestes generatorem konfiguracji misji ARMA 3 dla klanu milsim 7BOW (7 Brygada Obrony Wybrzeza). Odpowiedz WYLACZNIE czystym JSON-em.
Framework sam oblicza koordynaty na podstawie meta.location - NIE podawaj position.

MAPY: {maps_list}
FRAKCJE: {factions_list}

ROLE BLUFOR: platoon_leader, platoon_sergeant, squad_leader, team_leader, autorifleman,
grenadier, rifleman, combat_medic, medic, ratelo, mg_gunner, mg_assistant, mg_ammo_bearer,
at_gunner, at_assistant, at_ammo_bearer, marksman, sniper, engineer, cas_pilot, helicopter_pilot
RANGI: PRIVATE, CORPORAL, SERGEANT, LIEUTENANT, CAPTAIN

===== WSZYSTKIE TYPY POZYCJI OPFOR =====
Uzywaj wielu roznych typow aby misja byla zroznicowana i dynamiczna!

PIECHOTA STATYCZNA:
- garrison: jednostki w budynkach (garrison_radius okresla promien szukania budynkow)
- static: nieruchoma pozycja w terenie
- sniper: para sniper+spotter, wysoki skill
- mg_nest: gniazdo karabinu maszynowego (statyczny HMG, mozesz podac static_weapon)
- checkpoint: punkt kontrolny z barykada

PATROLE (ruch!):
- patrol: piechota patrolujaca losowo w promieniu
- vehicle_patrol: zmotoryzowany patrol (wymaga vehicle_class)
- air_patrol: helikopter patrolowy (altitude domyslnie 300m, wymaga vehicle_class np. "O_Heli_Light_02_F")
- sad_patrol: Search And Destroy - agresywny patrol szukajacy BLUFOR
- guard_route: patrol z wyznaczona trasa (uzyj patrol_route z waypointami)
- convoy: konwoj pojazdow jadacy trasa (vehicle_class - oddziel przecinkami np. "O_MRAP_02_F,O_Truck_02_transport_F,O_MRAP_02_F")

REAKTYWNE:
- qrf: Quick Reaction Force - aktywuje sie gdy BLUFOR w trigger_radius (domyslnie 300m)

OPCJE DLA POZYCJI:
- patrol_route: lista waypointow [[x,y,z],[x,y,z],...] - dla guard_route, convoy (framework oblicza jesli brak)
- vehicle_class: classname pojazdu - WYMAGANE dla vehicle_patrol, air_patrol, convoy; opcjonalne dla qrf
  Dla convoy: oddziel pojazdy przecinkami: "O_MRAP_02_F,O_Truck_02_transport_F"
- speed: "LIMITED" (domyslny), "NORMAL", "FULL" - predkosc ruchu patroli
- formation: "WEDGE" (domyslny), "COLUMN", "LINE", "STAG COLUMN", "ECH LEFT"
- altitude: wysokosc lotu dla air_patrol (domyslnie 300)
- trigger_radius: promien aktywacji QRF (domyslnie 300)
- garrison_radius: promien szukania budynkow dla garrison (domyslnie 150)
- static_weapon: classname statycznego uzbrojenia dla mg_nest (np. "O_HMG_01_high_F")

ROZMIARY: fireteam (4), squad (8), section (12)
KOMPOZYCJA: infantry, motorized (z pojazdem), mechanized (z APC/IFV)

POJAZDY OPFOR (dla motorized/mechanized/vehicle_patrol):
- "O_MRAP_02_F" - MRAP CSAT
- "O_Truck_02_transport_F" - ciezarowka transportowa
- "O_APC_Wheeled_02_rcws_F" - APC kolowy
- "O_APC_Tracked_02_cannon_F" - IFV gasienicowy
- "O_MBT_02_cannon_F" - czolg T-100
- "O_Heli_Light_02_F" - helikopter lekki (air_patrol)
- "O_Heli_Attack_02_F" - helikopter szturmowy (air_patrol)

===== SYSTEM ALERTU =====
Kontroluje swiadomosc OPFOR - od skradania do walki otwartej.
"alert_system": {{"enabled": true, "initial_state": "STEALTH", "combat_radius": 500.0, "alert_radius": 800.0}}
- initial_state: "STEALTH" (wrogowie nie wiedza o BLUFOR), "ALERT" (czujni), "COMBAT" (walcza)
- combat_radius: dystans na ktorym rozpoczyna sie walka
- alert_radius: dystans na ktorym OPFOR staje sie czujny
Uzyj STEALTH dla misji infiltracyjnych, ALERT dla standardowych, COMBAT dla goracej strefy.

===== KONTRATAK =====
Zorganizowany kontratak OPFOR po spelnieniu warunku.
"counterattack": {{
  "enabled": true,
  "trigger": "obj_complete",
  "delay_seconds": 120,
  "units": ["O_Soldier_SL_F","O_Soldier_F","O_Soldier_F","O_Soldier_AR_F","O_Soldier_GL_F","O_Soldier_F"],
  "vehicle_class": "O_MRAP_02_F"
}}
- trigger: "obj_complete" (po zakonczeniu obiektywu), "timer" (po czasie), "alert_combat" (po wykryciu)
- delay_seconds: opoznienie od triggera
- units: lista classnames jednostek kontrataku
- vehicle_class: opcjonalny pojazd dla sil kontrataku

===== IED (Improvizowane urzadzenia wybuchowe) =====
"ied": {{"enabled": true, "count_per_zone": 3, "radius": 200.0}}
- count_per_zone: ile IED na strefe OPFOR
- radius: promien rozmieszczenia wokol drog
Idealne dla misji w terenie zabudowanym i wzdluz drog. Framework rozmieszcza automatycznie.

===== UTRZYMANIE POZYCJI (Hold Position) =====
BLUFOR musi utrzymac punkt przez okreslony czas.
"hold_position": {{"enabled": true, "duration_seconds": 1200, "radius": 100.0}}
- duration_seconds: jak dlugo trzeba utrzymac (domyslnie 1200 = 20 min)
- radius: promien strefy do utrzymania

===== EKSTRAKCJA =====
Punkt ekstrakcji - misja konczy sie gdy BLUFOR dotrze po wykonaniu zadan.
"extraction": {{"enabled": true, "condition": "all_objectives", "radius": 30.0}}
- condition: "all_objectives" (po wszystkich celach), mozna tez uzyc nazwy konkretnego celu

===== MOŹDZIERZ =====
Ostrzal mozdzierzowy na pozycje BLUFOR.
"mortar": {{"enabled": true, "rounds": 8, "spread": 80.0, "delay_trigger": "alert_combat"}}
- rounds: liczba pociskow
- spread: rozrzut w metrach
- delay_trigger: "alert_combat" (po wykryciu), "timer", "obj_complete"

===== ZAKLADNICY =====
Cywile przetrzymywani przez OPFOR.
"hostages": {{"enabled": true, "hostages": [{{"id":"VIP_1","count":2,"task_text":"Uratuj zakladnikow"}}]}}
- Framework umieszcza ich w strefie OPFOR i tworzy task ratunkowy

===== OBIEKTY WYWIADOWCZE (Intel) =====
Dokumenty/laptopy do zebrania - tworza taski.
"intel_objects": [{{"task_id":"intel_1","class":"Land_Laptop_unfolded_F"}}]
- task_id: unikalny identyfikator taska
- class: classname obiektu (np. "Land_Laptop_unfolded_F", "Land_File1_F", "Land_File2_F")
Framework umieszcza obiekty w strefach OPFOR.

===== CELE DO ZNISZCZENIA =====
Obiekty ktore BLUFOR musi zniszczyc (pojazdy, sprzet, radiostacje).
"destroy_targets": [{{"task_id":"destroy_radio","class":"Land_TripodScreen_01_large_F"}}]
- task_id: unikalny identyfikator taska
- class: classname obiektu do zniszczenia

===== FALE POSILKOW =====
Dodatkowe oddzialy OPFOR pojawiajace sie w trakcie misji.
"reinforcement_waves": [{{"delay": 600, "units": ["O_Soldier_SL_F","O_Soldier_F","O_Soldier_F","O_Soldier_AR_F"], "vehicle": "O_Truck_02_transport_F"}}]
- delay: sekundy od poczatku misji
- units: lista classnames jednostek
- vehicle: opcjonalny pojazd transportowy

===== ZRZUTY ZAOPATRZENIA =====
Spadochronowe zrzuty zaopatrzenia dla BLUFOR.
"supply_drops": [{{"type": "ammo", "delay": 900}}]
- type: "ammo", "medical", "at", "special"
- delay: sekundy od poczatku misji (lub od spelnienia warunku)

===== PRZEJSCIA POGODOWE =====
Dynamiczna zmiana pogody w trakcie misji.
"weather_transitions": [{{"delay": 1800, "overcast": 0.8, "rain": 0.5, "fog": 0.1}}]
- delay: sekundy od poczatku misji
- overcast: zachmurzenie 0.0-1.0
- rain: deszcz 0.0-1.0
- fog: mgla 0.0-1.0
Swietne do tworzenia klimatu - np. misja zaczyna sie pogodnie, potem nadchodzi burza.

===== OSWIETLENIE FLARAMI =====
Cykliczne flarki nad polem walki (misje nocne).
"flare_illumination": {{"interval": 120, "count": 10}}
- interval: co ile sekund nowa flara
- count: ile flar lacznie

===== AMBIENT COMBAT =====
Odglosy walki w tle tworzace atmosfere.
"ambient_combat": {{"interval": 60, "duration": 300}}
- interval: co ile sekund odpalenie
- duration: jak dlugo trwa ambient

===== POJAZDY GRACZA =====
Pojazdy dostepne dla BLUFOR na spawnie.
"player_vehicles": [
  {{"vehicle_class": "B_MRAP_01_F", "callsign": "VIC 1", "spawn_area": "garage"}},
  {{"vehicle_class": "B_Heli_Transport_01_F", "callsign": "BIRD 1", "spawn_area": "helipad"}}
]
- spawn_area: "helipad" (lądowisko), "garage" (garaz/motor_pool), "road" (droga)
- crew_roles: opcjonalna lista rol ktore zaczynaja w pojezdzie

===== WSPARCIE POWIETRZNE =====
Helikoptery/samoloty BLUFOR.
"air_support": {{
  "enabled": true,
  "aircraft": [
    {{"callsign": "HAWK 1", "vehicle_class": "B_Heli_Transport_01_F", "pilot_role": "helicopter_pilot", "spawn_type": "ground", "spawn_location": "helipad"}},
    {{"callsign": "EAGLE 1", "vehicle_class": "B_Plane_CAS_01_F", "pilot_role": "cas_pilot", "spawn_type": "fly", "spawn_location": "airfield"}}
  ]
}}
- spawn_type: "ground" (na ziemi, np. helipad) lub "fly" (w powietrzu, juz leci)
- spawn_location: "helipad", "flat_terrain", "airfield", "fob"

===== SKRZYNIE ZAOPATRZENIA =====
Skrzynie z zaopatrzeniem na spawnie BLUFOR.
"resupply": [
  {{"type": "ammo", "crate_class": "Box_NATO_Ammo_F"}},
  {{"type": "medical", "crate_class": "ACE_medicalSupplyCrate"}},
  {{"type": "explosives", "crate_class": "Box_NATO_AmmoOrd_F"}},
  {{"type": "at", "crate_class": "Box_NATO_WpsLaworkers_F"}},
  {{"type": "special", "crate_class": "Box_NATO_Support_F"}},
  {{"type": "arsenal", "crate_class": "B_supplyCrate_F"}}
]
- type: "ammo", "medical", "explosives", "at" (AT/AA), "special", "arsenal" (pelny arsenal), "general"
- crate_class: classname skrzynki w ARMA 3

===== LOADOUT PRESETS =====
Niestandardowe wyposazenie dla konkretnych rol.
"loadout_presets": {{
  "sniper": {{
    "primary_weapon": "srifle_EBR_F",
    "primary_mags": 10,
    "optic": "optic_SOS",
    "suppressor": "muzzle_snds_B",
    "vest": "V_PlateCarrier1_rgr",
    "uniform": "U_B_CombatUniform_mcam",
    "helmet": "H_Booniehat_mcamo",
    "nvg": "NVGoggles",
    "items": ["FirstAidKit", "ItemGPS", "ItemMap", "ItemCompass", "ItemWatch"]
  }}
}}
Kazdy preset nadpisuje domyslne wyposazenie dla danej roli.

===== TYPOWA STRUKTURA PLUTONU IBC (20 graczy) =====
- HQ: platoon_leader, platoon_sergeant, ratelo, combat_medic
- ALPHA 1 (rifle): squad_leader, team_leader, 2x rifleman, autorifleman, grenadier, combat_medic, rifleman
- BRAVO 1 (rifle): jak ALPHA
- CHARLIE 1 (wsparcie): squad_leader, mg_gunner, mg_assistant, mg_ammo_bearer, at_gunner, at_assistant, marksman, combat_medic

===== WAZNE ZASADY =====
- Kazda strefa OPFOR powinna miec MINIMUM 3 pozycje (garrison + patrol + cos jeszcze)
- Duza misja = wiecej stref, kazda z 3-6 pozycjami wroga
- Patrol MUSI istniec w kazdej strefie (inaczej wrogowie stoja nieruchomo)
- QRF motorized daje dynamike - uzywaj czesto
- vehicle_patrol i air_patrol dodaja mobilnosc - uzywaj w wiekszych misjach
- sad_patrol jest agresywny - swietny dla misji obronnych
- Dla 20 graczy: 3-5 stref, 30-60 OPFOR (lacznie)
- Briefing: pisz jak prawdziwy OPORD wojskowy, szczegolowo, po polsku BEZ polskich znakow
- Marka obiektywow MUSI odpowiadac nazwom stref OPFOR (aby triggery dzialaly)
  np. strefa "OBJ_ALPHA" -> obiektyw "obj_alpha" z text "OBJ ALPHA"
- Uzywaj zaawansowanych mechanik gdy pasuja do opisu misji:
  * Misja nocna -> flare_illumination, alert_system STEALTH
  * Misja w miescie -> ied, checkpoint, garrison, mg_nest
  * Misja obronna -> hold_position, counterattack, reinforcement_waves
  * Misja infiltracyjna -> alert_system STEALTH, sniper, intel_objects
  * Misja ratunkowa -> hostages, extraction
  * Konwoj -> convoy, ied, checkpoint
  * Dluga misja -> weather_transitions, supply_drops, resupply

===== PRZYKLAD KOMPLETNEGO JSON =====
{{
  "meta": {{
    "mission_name": "7BOW_NAZWA_OPERACJI",
    "display_name": "Nazwa operacji",
    "author": "7BOW",
    "map": "Altis",
    "location": "nazwa lokalizacji na mapie",
    "game_type": "Coop",
    "max_players": 20
  }},
  "intel": {{"year":2026,"month":3,"day":17,"hour":6,"minute":0,"weather":0.1,"fog":0.0,"wind":0.0}},
  "faction_preset": "vanilla_nato",
  "enemy_faction_preset": "vanilla_csat",
  "radio": {{"system":"acre2"}},
  "blufor": {{
    "groups": [
      {{
        "callsign": "HQ",
        "type": "platoon_hq",
        "units": [
          {{"role":"platoon_leader","rank":"LIEUTENANT"}},
          {{"role":"platoon_sergeant","rank":"SERGEANT"}},
          {{"role":"ratelo"}},
          {{"role":"combat_medic","rank":"CORPORAL"}}
        ]
      }},
      {{
        "callsign": "ALPHA 1",
        "type": "rifle_squad",
        "units": [
          {{"role":"squad_leader","rank":"SERGEANT"}},
          {{"role":"team_leader","rank":"CORPORAL"}},
          {{"role":"rifleman"}},
          {{"role":"rifleman"}},
          {{"role":"autorifleman"}},
          {{"role":"grenadier"}},
          {{"role":"combat_medic","rank":"CORPORAL"}},
          {{"role":"rifleman"}}
        ]
      }}
    ]
  }},
  "player_vehicles": [
    {{"vehicle_class": "B_MRAP_01_F", "callsign": "VIC 1", "spawn_area": "garage"}}
  ],
  "air_support": {{
    "enabled": true,
    "aircraft": [
      {{"callsign": "HAWK 1", "vehicle_class": "B_Heli_Transport_01_F", "pilot_role": "helicopter_pilot", "spawn_type": "ground", "spawn_location": "helipad"}}
    ]
  }},
  "opfor": {{
    "skill_range": [0.4, 0.7],
    "zones": [
      {{
        "name": "OBJ_ALPHA",
        "positions": [
          {{"id":"A1","type":"garrison","size":"squad","garrison_radius":150}},
          {{"id":"A2","type":"patrol","size":"fireteam","speed":"LIMITED","formation":"WEDGE"}},
          {{"id":"A3","type":"sniper"}},
          {{"id":"A4","type":"mg_nest","static_weapon":"O_HMG_01_high_F"}},
          {{"id":"A5","type":"qrf","size":"fireteam","composition":"motorized","vehicle_class":"O_MRAP_02_F","trigger_radius":300}},
          {{"id":"A6","type":"vehicle_patrol","size":"fireteam","vehicle_class":"O_MRAP_02_F","speed":"NORMAL"}}
        ]
      }},
      {{
        "name": "OBJ_BRAVO",
        "positions": [
          {{"id":"B1","type":"garrison","size":"fireteam"}},
          {{"id":"B2","type":"patrol","size":"fireteam"}},
          {{"id":"B3","type":"checkpoint","size":"fireteam"}},
          {{"id":"B4","type":"sad_patrol","size":"fireteam","speed":"NORMAL"}}
        ]
      }},
      {{
        "name": "OBJ_CHARLIE",
        "positions": [
          {{"id":"C1","type":"garrison","size":"squad"}},
          {{"id":"C2","type":"guard_route","size":"fireteam","speed":"LIMITED"}},
          {{"id":"C3","type":"static","size":"fireteam"}},
          {{"id":"C4","type":"air_patrol","vehicle_class":"O_Heli_Light_02_F","altitude":300}}
        ]
      }}
    ]
  }},
  "alert_system": {{"enabled": true, "initial_state": "STEALTH", "combat_radius": 500.0, "alert_radius": 800.0}},
  "counterattack": {{
    "enabled": true,
    "trigger": "obj_complete",
    "delay_seconds": 120,
    "units": ["O_Soldier_SL_F","O_Soldier_F","O_Soldier_F","O_Soldier_AR_F","O_Soldier_GL_F","O_Soldier_F"],
    "vehicle_class": "O_MRAP_02_F"
  }},
  "ied": {{"enabled": false}},
  "hold_position": {{"enabled": false}},
  "extraction": {{"enabled": true, "condition": "all_objectives", "radius": 30.0}},
  "mortar": {{"enabled": false}},
  "hostages": {{"enabled": false}},
  "intel_objects": [],
  "destroy_targets": [],
  "reinforcement_waves": [{{"delay": 900, "units": ["O_Soldier_SL_F","O_Soldier_F","O_Soldier_F","O_Soldier_AR_F"], "vehicle": "O_Truck_02_transport_F"}}],
  "supply_drops": [],
  "weather_transitions": [{{"delay": 2400, "overcast": 0.7, "rain": 0.3, "fog": 0.0}}],
  "flare_illumination": null,
  "ambient_combat": null,
  "resupply": [
    {{"type": "ammo", "crate_class": "Box_NATO_Ammo_F"}},
    {{"type": "medical", "crate_class": "ACE_medicalSupplyCrate"}}
  ],
  "markers": {{
    "objectives": [
      {{"name":"obj_alpha","text":"OBJ ALPHA","type":"hd_objective","color":"ColorRed"}},
      {{"name":"obj_bravo","text":"OBJ BRAVO","type":"hd_objective","color":"ColorRed"}},
      {{"name":"obj_charlie","text":"OBJ CHARLIE","type":"hd_objective","color":"ColorRed"}}
    ]
  }},
  "respawn": {{"wave_interval":600,"tickets_per_player":2,"observer_mode":true}},
  "civilians": {{"enabled":false}},
  "briefing": {{
    "language":"pl",
    "situation":"Szczegolowy opis sytuacji taktycznej...",
    "mission":"Opis zadania bojowego...",
    "execution":"Szczegolowy plan realizacji z fazami...",
    "logistics":"Zaopatrzenie, ewakuacja medyczna, amunicja...",
    "command_signal":"Lancuch dowodzenia, czestotliwosci radiowe..."
  }},
  "time_limit": 120
}}

===== KRYTYCZNE =====
- NIE podawaj koordynatow (position) - framework OBLICZA JE SAM na podstawie meta.location
- Briefing po polsku BEZ polskich znakow (a zamiast a, c zamiast c, o zamiast o, z zamiast z itd.)
- Nazwy markerow: male litery, podkreslnik (obj_alpha, wp_1)
- Nazwy stref OPFOR musza PASOWAC do nazw obiektywow (OBJ_ALPHA <-> obj_alpha)
- Odpowiedz WYLACZNIE czystym JSON-em, absolutnie zero markdown, zero komentarzy
- Jesli uzytkownik prosi o zakladnikow/hostages - DODAJ sekcje hostages z enabled:true
- Jesli uzytkownik prosi o pojazdy - DODAJ composition:"motorized" i vehicle_class
- ZAWSZE tworz realistyczny, zroznicowany OPFOR - nie sam garrison!
- UZYWAJ zaawansowanych mechanik (alert, counterattack, extraction, mortar, ied, itp.) gdy pasuja do scenariusza
- Dla misji nocnych ZAWSZE dodaj flare_illumination lub alert_system STEALTH
- player_vehicles dodaj gdy misja wymaga mobilnosci lub dystanse sa duze
- air_support dodaj gdy prompt wspomina helikoptery lub lotnictwo
- resupply dodaj gdy misja jest dluga lub wymaga specjalistycznego sprzetu
"""


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/prompt")
async def handle_prompt(request: Request):
    """Main endpoint: takes natural language prompt, calls Claude CLI, generates mission."""
    body = await request.json()
    user_prompt = body.get("prompt", "").strip()
    mods = body.get("mods", {})

    if not user_prompt:
        return JSONResponse(status_code=400, content={"error": "Pusty prompt"})

    # Append mod info to prompt so AI knows what's available
    mod_info = []
    if mods.get("ace3"): mod_info.append("ACE3 WLACZONY (microDAGR, cellphone, medical)")
    if mods.get("acre2"): mod_info.append("ACRE2 WLACZONY (radio: acre2)")
    if mods.get("tfar"): mod_info.append("TFAR WLACZONY (radio: tfar)")
    if mod_info:
        user_prompt += "\n\nAKTYWNE MODY: " + ", ".join(mod_info)
    if not mods.get("ace3"):
        user_prompt += "\n\nACE3 WYLACZONY - NIE uzywaj ACE3 classnames."
    user_prompt += "\n\nWAZNE: Uzywaj TYLKO vanilla ARMA 3 classnames (B_Soldier_F, B_officer_F, O_Soldier_F, itp). NIE uzywaj classnames z modow (rhsusf_, rhs_, CUP_)."

    # Step 1: Call Claude CLI to parse prompt into config JSON
    system_prompt = _build_system_prompt()

    try:
        config_json = await _call_claude_cli(system_prompt, user_prompt)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"[ERROR] Claude CLI failed: {e}\n{tb}")
        return JSONResponse(status_code=200, content={
            "success": False,
            "error": f"Claude CLI error: {str(e)}",
            "step": "parsing"
        })

    # Step 2: Parse the JSON config
    try:
        config_data = json.loads(config_json)
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parse failed: {e}")
        print(f"[ERROR] Raw output: {config_json[:500]}")
        return {"success": False, "error": f"AI zwrocil niepoprawny JSON: {str(e)}", "raw_output": config_json[:2000]}

    # Step 3: Compute layout (fix coordinates, add missing elements)
    try:
        config_data = compute_mission_layout(config_data)
    except Exception as e:
        print(f"[WARN] Layout computation: {e}")

    # Step 3b: Apply mod settings from UI
    config_data["ace3_enabled"] = mods.get("ace3", False)
    # Radio system — UI toggle ALWAYS overrides AI output
    if mods.get("acre2"):
        config_data.setdefault("radio", {})["system"] = "acre2"
    elif mods.get("tfar"):
        config_data.setdefault("radio", {})["system"] = "tfar"

    # Step 4: Validate and generate
    try:
        config = load_config_from_dict(config_data)
        mission_path = generate_mission(config, str(DEFAULT_OUTPUT))

        return {
            "success": True,
            "mission_name": mission_path.name,
            "path": str(mission_path),
            "config": config_data,
        }
    except Exception as e:
        import traceback
        print(f"[ERROR] Generation failed: {e}\n{traceback.format_exc()}")
        return {"success": False, "error": f"Blad generowania: {str(e)}", "config": config_data}


async def _call_claude_cli(system_prompt: str, user_prompt: str) -> str:
    """Call Claude CLI as subprocess and return its output.

    Uses pipe for user prompt and --append-system-prompt for system prompt.
    System prompt is kept short; full schema is included in user prompt.
    """
    # Combine system instructions with user prompt into one piped message
    full_prompt = system_prompt + "\n\n---\n\nOPIS MISJI OD UZYTKOWNIKA:\n\n" + user_prompt

    proc = await asyncio.create_subprocess_exec(
        "claude",
        "-p",
        "--output-format", "text",
        "--model", "opus",
        "--effort", "max",
        "--max-turns", "10",
        "--no-session-persistence",
        "--tools", "",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(input=full_prompt.encode('utf-8')),
            timeout=300
        )
    except asyncio.TimeoutError:
        proc.kill()
        raise RuntimeError("Timeout - AI nie odpowiedzial w 300 sekund")

    output = stdout.decode("utf-8", errors="replace").strip()
    err_output = stderr.decode("utf-8", errors="replace").strip()

    print(f"[CLAUDE] returncode={proc.returncode} stdout_len={len(output)} stderr_len={len(err_output)}")
    if err_output:
        print(f"[CLAUDE STDERR] {err_output[:300]}")

    if proc.returncode != 0:
        raise RuntimeError(f"exit code {proc.returncode}: {err_output[:500]}")

    if not output:
        raise RuntimeError(f"AI zwrocil pusty output. Stderr: {err_output[:300]}")

    output = _extract_json(output)
    return output


def _extract_json(text: str) -> str:
    """Extract JSON from Claude output, stripping markdown fences if present."""
    text = text.strip()

    # Remove markdown code fences
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    # Try to find JSON object boundaries
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end + 1]

    return text


@app.get("/api/maps")
async def get_maps():
    return {"maps": MAPS_DB}


@app.get("/api/factions")
async def get_factions():
    return {"factions": FACTIONS_SUMMARY}


@app.get("/api/missions")
async def list_missions():
    missions = []
    if DEFAULT_OUTPUT.exists():
        for d in sorted(DEFAULT_OUTPUT.iterdir()):
            if d.is_dir() and (d / "mission.sqm").exists():
                missions.append({"name": d.name, "path": str(d)})
    return {"missions": missions}


# Keep direct JSON generation endpoint as fallback
@app.post("/api/generate")
async def generate_direct(request: Request):
    try:
        data = await request.json()
        config = load_config_from_dict(data)
        mission_path = generate_mission(config, str(DEFAULT_OUTPUT))
        return {
            "success": True,
            "message": f"Mission generated: {mission_path.name}",
            "path": str(mission_path),
        }
    except Exception as e:
        return JSONResponse(status_code=400, content={"success": False, "message": str(e)})


def main():
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()

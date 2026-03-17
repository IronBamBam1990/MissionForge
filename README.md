# 7BOW ARMA 3 MISSION GENERATOR — INSTRUKCJA

**Wersja:** 0.1.0
**Autor:** Kamil Padula
**Ostatnia aktualizacja:** 2026-03-17


<img width="1979" height="1134" alt="image" src="https://github.com/user-attachments/assets/936c68ce-84ec-4a50-a77e-701bedc18a89" />



---

## 1. WPROWADZENIE

### 1.1 Co to jest

7BOW ARMA 3 Mission Generator to framework do automatycznego generowania misji kooperacyjnych (PvE) dla ARMA 3. Stworzony z mysla o klanie 7BOW (7 Brygada Obrony Wybrzeza) i operacjach milsim, pozwala w kilka minut wygenerowac kompletna misje z pelnym ORBAT-em, OPFOR-em, taskami, markerami, respawnem i zaawansowanymi mechanikami.

### 1.2 Jak dziala

Pipeline generowania misji:

```
Prompt (tekst naturalny)
    -> AI Model (parsuje na JSON)
    -> Python (walidacja + generacja)
    -> SQF/SQM (pliki misji ARMA 3)
    -> Eden Editor / Server
```

1. **Prompt** — Opisujesz misje w jezyku naturalnym (po polsku lub angielsku)
2. **AI Model** — Sztuczna inteligencja parsuje opis i generuje strukturalny JSON (MissionConfig)
3. **Python** — Framework waliduje JSON przez Pydantic, generuje pliki misji:
   - `mission.sqm` — BLUFOR (gracze), markery, ustawienia mapy
   - `initServer.sqf` — OPFOR, pojazdy, mechaniki, taski
   - `init.sqf` — inicjalizacja klienta
   - `initPlayerLocal.sqf` — terrain snap, loadouty, radio
   - `description.ext` — konfiguracja respawnu, parametry misji
   - `briefing.sqf` — briefing OPORD
4. **Wynik** — Gotowy folder misji w `Documents/Arma 3/missions/`

### 1.3 Wymagania

**Wymagane:**

- Python 3.11+
- ARMA 3
- Klucz API do modelu AI

**Opcjonalne mody:**

- **ACE3** — zaawansowany system medyczny, balistyka
- **ACRE2** — realistyczna komunikacja radiowa (zalecane)
- **TFAR** — alternatywny system radia

---

## 2. URUCHOMIENIE

### 2.1 Jak uruchomic serwer web

```bash
cd "C:\Users\kamil\Documents\Arma 3\mission-generator"
python run_server.py
```

Serwer startuje na `http://127.0.0.1:8000` (domyslnie).

### 2.2 Jak otworzyc interface

Otworz przegladarke i wejdz na `http://127.0.0.1:8000`. Zobaczysz terminal-style interface z:

- **Sidebar** — szablony misji, ustawienia modow, lista wygenerowanych misji
- **Pole tekstowe** — tutaj wpisujesz opis misji lub wklejasz briefing OPORD
- **Przycisk EXECUTE** — generuje misje (skrot: `Ctrl+Enter`)

### 2.3 Jak wygenerowac misje

1. Wybierz szablon z paska bocznego (np. RAID, PATROL) lub napisz wlasny opis
2. Zaznacz mody w sekcji "Mods" (ACE3, ACRE2, TFAR)
3. Kliknij **EXECUTE** lub nacisnij `Ctrl+Enter`
4. Poczekaj 30-60 sekund na przetworzenie przez AI
5. Zobaczysz status: `MISSION GENERATED: nazwa_misji`
6. Kliknij `> show_config.json` zeby zobaczyc wygenerowana konfiguracje

### 2.4 Jak otworzyc w Eden Editor

1. Uruchom ARMA 3
2. Eden Editor -> Open Scenario
3. Przejdz do: `Documents/Arma 3/missions/`
4. Znajdz folder misji (np. `7BOW_Iron_Dawn.Altis`)
5. Otworz misje
6. BLUFOR (gracze) sa juz umieszczeni — mozesz je przesunac w edytorze
7. OPFOR spawnuje sie dynamicznie przez initServer.sqf

---

## 3. SZABLONY MISJI

### 3.1 Lista szablonow

Kazdy szablon jest **w pelni zrandomizowany** — kazde klikniecie generuje inna misje:

| Szablon                | Opis                                  | Typowy sklad                |
| ---------------------- | ------------------------------------- | --------------------------- |
| **RAID**         | Atak na 2 cele, zniszcz i wycofaj sie | Pluton + wsparcie + pojazdy |
| **PATROL**       | Patrol bojowy po rejonie, 4-6 punktow | 2-3 druzyny                 |
| **DEFENSE**      | Obrona pozycji przed falami wroga     | Pluton + pojazdy            |
| **AMBUSH**       | Zasadzka na konwoj wroga              | 1-2 druzyny + sniper        |
| **ESCORT**       | Eskortuj sojuszniczy konwoj           | Pluton + pojazdy            |
| **CONVOY**       | Zniszcz konwoj wroga na trasie        | 2-3 druzyny + pojazdy       |
| **SAR**          | Search & Rescue — uratuj zakladnikow | Druzyna ratunkowa           |
| **RECON**        | Rozpoznanie, misja cicha              | Zespol 4-6 osob             |
| **HOSTAGE**      | Odbij zakladnikow z budynkow          | 2-3 druzyny + sniper        |
| **CRIMSON DAWN** | Predefiniowana misja (Altis, Kavala)  | Pelny pluton + CAS          |

### 3.2 Jak dziala randomizacja

Kazdy szablon losuje:

- **Mape** — Altis, Stratis, Tanoa, Malden, Livonia
- **Lokalizacje** — realne miasta z wybranej mapy (np. Kavala, Pyrgos na Altis)
- **Nazwe operacji** — np. "IRON DAWN", "STEEL FURY", "SHADOW BLADE"
- **Callsign** — TITAN, VIKING, SPARTAN, GUARDIAN...
- **Czas** — od nocy (04:00) po polnoc (23:00)
- **Pogode** — slonecznie, mgla, deszcz, burza
- **Rok** — 1985 do 2026
- **Frakcje BLUFOR** — NATO (vanilla_nato)
- **OPFOR** — CSAT (vanilla_csat)
- **Skill wroga** — od 0.3 (rekruci) do 0.9 (specnaz)
- **Mechaniki** — alert system, IED, kontratak, mortar, fale wzmocnien...
- **Pojazdy** — MRAP, APC, ciezarowki, pickup techniczny...

### 3.3 Jak pisac wlasne prompty

Mozesz napisac dowolny opis misji. AI rozumie:

- Jezyk naturalny (polski lub angielski)
- Briefing OPORD format
- Skroty wojskowe (SL, TL, AR, AT, MG, QRF, IRP, ORP, SBF)

**Przyklad prostego promptu:**

```
Misja na Altis, okolice Kavala. 2 druzyny piechoty NATO.
Cel: oczyscic wioski z CSAT. 3 grupy wroga w garrisonie.
Respawn 10 min, 2 tickety. Godzina 06:00.
```

**Przyklad zaawansowanego promptu:**

```
OPERACJA SHADOW FURY

Mapa: Altis, lokalizacja Kavala, rok 2026.
Start 05:30, mgla poranna, przejscie w deszcz po 30 minutach.

ORBAT BLUFOR (NATO):
- HQ: PL (LIEUTENANT), PS, RATELO, Medyk
- 1-1: SL, 2xTL, 2xAR, Grenadier, Rifleman, Medyk
- 1-2: identyczny sklad
- Wsparcie: 2xMG, AT, amunicyjny
- CAS: helikopter transportowy

OPFOR (CSAT):
Cel ALPHA - Kavala polnoc:
- 4x fireteam garrison w budynkach
- 2x fireteam patrol
- 1x sniper team na wzgorzu
- QRF squad zmotoryzowany (MRAP), trigger 300m
- IED na podejsciu

System alertow: STEALTH -> ALERT -> COMBAT
Kontratak po zdobyciu celu (squad + APC)
Ostrzal mozdzierzowy po kontakcie

Skill wroga: 0.5-0.7 (weterani)
Respawn wave 10min, 2 tickety, ACRE2.
```

---

## 4. KONFIGURACJA MISJI (JSON)

Kazda misja jest opisana przez `MissionConfig` — glowny obiekt JSON. Wszystkie pola sa **opcjonalne** z rozsadnymi wartosciami domyslnymi.

### 4.1 meta — Metadane misji

```json
{
  "meta": {
    "mission_name": "7BOW_Iron_Dawn",
    "display_name": "Iron Dawn",
    "author": "7BOW",
    "map": "Altis",
    "map_classname_override": null,
    "game_type": "Coop",
    "max_players": 40
  }
}
```

| Pole             | Typ    | Domyslnie      | Opis                                          |
| ---------------- | ------ | -------------- | --------------------------------------------- |
| `mission_name` | string | "7BOW_Mission" | Nazwa folderu misji                           |
| `display_name` | string | ""             | Nazwa wyswietlana w lobby                     |
| `author`       | string | "7BOW"         | Autor misji                                   |
| `map`          | string | "Altis"        | Mapa (Altis, Stratis, Tanoa, Malden, Livonia) |
| `game_type`    | string | "Coop"         | Typ gry                                       |
| `max_players`  | int    | 40             | Maksymalna liczba graczy                      |

### 4.2 intel — Czas i pogoda

```json
{
  "intel": {
    "year": 2026,
    "month": 3,
    "day": 14,
    "hour": 6,
    "minute": 0,
    "weather": 0.0,
    "fog": 0.0,
    "wind": 0.0
  }
}
```

| Pole        | Typ   | Zakres  | Opis                             |
| ----------- | ----- | ------- | -------------------------------- |
| `hour`    | int   | 0-23    | Godzina startu                   |
| `weather` | float | 0.0-1.0 | Zachmurzenie (0=czysto, 1=pelne) |
| `fog`     | float | 0.0-1.0 | Mgla (0=brak, 1=gesta)           |
| `wind`    | float | 0.0-1.0 | Wiatr                            |

### 4.3 blufor — Sily wlasne (gracze)

```json
{
  "blufor": {
    "groups": [
      {
        "callsign": "CASTLE 1-1",
        "type": "rifle_squad",
        "position": [14500, 0, 16200],
        "spawn_area": "fob",
        "units": [
          {"role": "squad_leader", "rank": "SERGEANT"},
          {"role": "team_leader", "rank": "CORPORAL"},
          {"role": "autorifleman", "rank": "PRIVATE"},
          {"role": "grenadier", "rank": "PRIVATE"},
          {"role": "rifleman", "rank": "PRIVATE"},
          {"role": "rifleman", "rank": "PRIVATE"},
          {"role": "rifleman", "rank": "PRIVATE"},
          {"role": "combat_medic", "rank": "CORPORAL"}
        ]
      }
    ]
  }
}
```

**Dostepne role:**

- `platoon_leader` — B_officer_F (LIEUTENANT)
- `platoon_sergeant` — B_Soldier_SL_F (SERGEANT)
- `squad_leader` — B_Soldier_SL_F (SERGEANT)
- `team_leader` — B_Soldier_TL_F (CORPORAL)
- `autorifleman` — B_Soldier_AR_F
- `grenadier` — B_Soldier_GL_F
- `rifleman` — B_Soldier_F
- `combat_medic` / `medic` — B_medic_F (CORPORAL)
- `ratelo` — B_Soldier_F
- `mg_gunner` — B_soldier_M_F
- `mg_assistant` — B_Soldier_A_F
- `at_gunner` — B_soldier_LAT_F
- `at_assistant` — B_Soldier_A_F
- `marksman` — B_soldier_M_F
- `sniper` — B_sniper_F
- `engineer` — B_engineer_F
- `explosive_specialist` — B_soldier_exp_F
- `cas_pilot` — B_Pilot_F
- `helicopter_pilot` — B_Helipilot_F

**Rangi:** PRIVATE, CORPORAL, SERGEANT, LIEUTENANT, CAPTAIN, MAJOR, COLONEL

### 4.4 opfor — Sily przeciwnika

```json
{
  "opfor": {
    "skill_range": [0.4, 0.7],
    "zones": [
      {
        "name": "obj_alpha",
        "center": [14200, 0, 16500],
        "positions": [
          // ... pozycje wroga (patrz ponizej)
        ],
        "fortifications": [
          {"type": "sandbag", "position": [14200, 0, 16510], "direction": 90}
        ],
        "mines": [
          [14180, 0, 16480]
        ]
      }
    ]
  }
}
```

**skill_range** — `[min, max]` — zakres umiejetnosci AI. Kazdy zolnierz dostaje losowa wartosc z zakresu.

- `[0.3, 0.5]` — rekruci (niedokladni, wolni)
- `[0.4, 0.6]` — regularne sily
- `[0.5, 0.7]` — weterani
- `[0.6, 0.8]` — elita
- `[0.7, 0.9]` — specnaz (zabojczo celni)

### 4.5 Typy pozycji OPFOR

Kazda pozycja w strefie (zone) to obiekt `EnemyPosition`:

#### garrison — Garnizon w budynkach

Jednostki sa rozmieszczane w pozycjach budynkow (okna, drzwi, dachy). Losowe rozmieszczenie.

```json
{
  "id": "A-1",
  "type": "garrison",
  "position": [14200, 0, 16500],
  "size": "fireteam",
  "garrison_radius": 150
}
```

#### patrol — Patrol pieszy

Patrol piechoty po waypointach (manualny) lub automatyczny (po drogach).

```json
{
  "id": "A-2",
  "type": "patrol",
  "position": [14300, 0, 16400],
  "size": "fireteam",
  "speed": "LIMITED",
  "formation": "WEDGE",
  "patrol_route": [
    [14300, 0, 16400],
    [14400, 0, 16500],
    [14350, 0, 16600],
    [14250, 0, 16450]
  ]
}
```

Jesli `patrol_route` jest puste/null, system automatycznie generuje trase po drogach (`7BOW_fnc_smartInfantryPatrol`).

#### vehicle_patrol — Patrol pojazdowy

```json
{
  "id": "A-3",
  "type": "vehicle_patrol",
  "position": [14500, 0, 16300],
  "vehicle_class": "O_MRAP_02_F",
  "speed": "LIMITED",
  "patrol_route": [
    [14500, 0, 16300],
    [14700, 0, 16500],
    [14600, 0, 16700]
  ]
}
```

Jesli `patrol_route` jest puste, uzywa `7BOW_fnc_smartVehiclePatrol` — automatyczny patrol po sieci drogowej.

#### air_patrol — Patrol powietrzny

```json
{
  "id": "A-4",
  "type": "air_patrol",
  "vehicle_class": "O_Heli_Light_02_F",
  "altitude": 200,
  "patrol_route": [
    [14000, 0, 16000],
    [15000, 0, 16000],
    [15000, 0, 17000],
    [14000, 0, 17000]
  ]
}
```

#### sad_patrol — Search and Destroy

Agresywny patrol — jednostki aktywnie szukaja i atakuja. Tryb COMBAT, combat mode RED.

```json
{
  "id": "A-5",
  "type": "sad_patrol",
  "size": "squad",
  "patrol_route": [
    [14200, 0, 16500],
    [14400, 0, 16700],
    [14100, 0, 16800]
  ]
}
```

#### guard_route — Trasa wartownicza

Grupa przechodzi miedzy punktami i czeka w kazdym przez okreslony czas.

```json
{
  "id": "A-6",
  "type": "guard_route",
  "size": "fireteam",
  "patrol_route": [
    [14200, 0, 16500],
    [14300, 0, 16600],
    [14250, 0, 16550]
  ]
}
```

#### convoy — Konwoj

```json
{
  "id": "C-1",
  "type": "convoy",
  "vehicle_class": "O_Truck_02_covered_F,O_MRAP_02_F,O_Truck_02_covered_F",
  "speed": "LIMITED",
  "patrol_route": [
    [14000, 0, 16000],
    [15000, 0, 17000]
  ]
}
```

Jesli trasa jest podana (>=2 punkty), uzywa `7BOW_fnc_convoy`. Jesli nie, uzywa `7BOW_fnc_smartConvoy` z automatycznym GPS po drogach.

#### sniper — Zespol snajperski

```json
{
  "id": "A-SNP",
  "type": "sniper",
  "position": [14100, 0, 16800]
}
```

Automatycznie generuje O_sniper_F + O_spotter_F. Tryb STEALTH, combat mode RED, wysoki skill celowania (0.9).

#### mg_nest — Gniazdo karabinu maszynowego

```json
{
  "id": "A-MG",
  "type": "mg_nest",
  "position": [14250, 0, 16550],
  "static_weapon": "O_HMG_01_high_F"
}
```

Tworzy bron statyczna, pierwsza jednostka wsiadla jako strzelec. Domyslnie O_HMG_01_high_F.

#### checkpoint — Punkt kontrolny

```json
{
  "id": "A-CP",
  "type": "checkpoint",
  "position": [14300, 0, 16200],
  "size": "fireteam"
}
```

Automatycznie znajduje najblizsza droge i stawia bariere (Land_RoadBarrier_F).

#### qrf — Quick Reaction Force

```json
{
  "id": "A-QRF",
  "type": "qrf",
  "position": [14500, 0, 16800],
  "size": "squad",
  "composition": "motorized",
  "vehicle_class": "O_MRAP_02_F",
  "trigger_radius": 300
}
```

QRF aktywuje sie gdy BLUFOR wejdzie w `trigger_radius` od centrum strefy. Przechodzi w tryb COMBAT i atakuje SAD.

#### static — Pozycja statyczna

Domyslny typ — jednostki pojawiaja sie w pozycji, tryb AWARE, combat RED.

```json
{
  "id": "A-S1",
  "type": "static",
  "position": [14300, 0, 16500],
  "size": "fireteam"
}
```

### 4.6 Rozmiary grup (size)

| Size         | Sklad domyslny                                                            |
| ------------ | ------------------------------------------------------------------------- |
| `fireteam` | TL, Rifleman, AR, Grenadier (4 osoby)                                     |
| `squad`    | SL, TL, Rifleman, AR, GL, TL, Rifleman, Medic (8 osob)                    |
| `section`  | SL, TL, 2xRifleman, AR, GL, TL, 2xRifleman, AR, Marksman, Medic (12 osob) |

### 4.7 Kompozycja (composition)

| Composition    | Opis                                    |
| -------------- | --------------------------------------- |
| `infantry`   | Tylko piechota                          |
| `motorized`  | Piechota + pojazd kolowy (np. MRAP)     |
| `mechanized` | Piechota + pojazd opancerzony (np. APC) |

Dla `motorized`/`mechanized` z `vehicle_class`, pojazd jest spawnowany 10m obok pozycji.

### 4.8 markers — Markery na mapie

```json
{
  "markers": {
    "objectives": [
      {"name": "obj_alpha", "text": "Cel ALPHA", "position": [14200, 0, 16500], "type": "mil_objective", "color": "ColorRed"}
    ],
    "waypoints": [
      {"name": "wp1", "text": "WP1", "position": [14300, 0, 16300], "type": "mil_dot", "color": "ColorBlue"}
    ],
    "sbf": [
      {"name": "sbf1", "text": "SBF 1", "position": [14100, 0, 16400], "type": "mil_triangle", "color": "ColorBlue"}
    ],
    "rally_points": [
      {"name": "orp1", "text": "ORP", "position": [14400, 0, 16100], "type": "mil_dot", "color": "ColorGreen"}
    ],
    "phase_lines": [
      {"name": "pl_red", "text": "PL RED", "position": [14200, 0, 16300], "type": "mil_dot", "color": "ColorRed"}
    ],
    "routes": [
      {
        "name": "route_alpha",
        "text": "Trasa ALPHA",
        "points": [[14400, 0, 16100], [14300, 0, 16300], [14200, 0, 16500]],
        "color": "ColorBlue"
      }
    ],
    "custom": []
  }
}
```

**Typy markerow:**

- `mil_dot` — kropka
- `mil_objective` — cel
- `mil_triangle` — trojkat (SBF)
- `mil_flag` — flaga
- `b_inf` — piechota BLUFOR
- `b_armor` — pojazd BLUFOR
- `b_air` — lotnictwo BLUFOR
- `hd_end` — punkt ewakuacji
- `hd_pickup` — punkt odbioru

**Kolory:** `ColorRed`, `ColorBlue`, `ColorGreen`, `ColorBlack`, `ColorWhite`, `Default`

### 4.9 respawn — System respawnu

```json
{
  "respawn": {
    "wave_interval": 600,
    "tickets_per_player": 2,
    "observer_mode": true,
    "reinsert": {
      "enabled": true,
      "priority": ["combat_medic", "platoon_sergeant", "platoon_leader", "orp"]
    },
    "technical_respawn": true
  }
}
```

| Pole                   | Opis                                  |
| ---------------------- | ------------------------------------- |
| `wave_interval`      | Czas miedzy falami respawnu (sekundy) |
| `tickets_per_player` | Ile razy gracz moze sie odrodzic      |
| `observer_mode`      | Tryb obserwatora po smierci           |
| `reinsert.priority`  | Kolejnosc punktow reinsercji          |
| `technical_respawn`  | Awaryjny respawn (jesli bug)          |

### 4.10 hostages — Zakladnicy

```json
{
  "hostages": {
    "enabled": true,
    "hostages": [
      {
        "id": "hostage_1",
        "position": [14200, 0, 16500],
        "count": 2,
        "guarded": true,
        "task_name": "rescue_alpha",
        "task_text": "Uratuj zakladnikow w budynku ALPHA"
      }
    ]
  }
}
```

Zakladnicy sa spawnowani wewnatrz budynkow (7BOW_fnc_indoorPos), sa captive, nie moga sie ruszac. Monitor co 5 sekund sprawdza czy BLUFOR jest blisko i czy nie ma wroga — jesli tak, zakladnik jest uratowany.

### 4.11 civilians — Cywile

```json
{
  "civilians": {
    "enabled": true,
    "density": "medium",
    "zones": [
      {"center": [14200, 0, 16500], "radius": 200}
    ]
  }
}
```

Gestosc: `low` (3 cywili), `medium` (6), `high` (10) na stefe.

---

## 5. ZAAWANSOWANE MECHANIKI

### 5.1 Alert System (STEALTH -> ALERT -> COMBAT)

System stanow alertu wroga. Wszystkie grupy OPFOR reaguja na zmiane stanu.

```json
{
  "alert_system": {
    "enabled": true,
    "initial_state": "STEALTH",
    "combat_radius": 500,
    "alert_radius": 800
  }
}
```

**Stany:**

| Stan              | Zachowanie AI     | Wyzwalacz                             |
| ----------------- | ----------------- | ------------------------------------- |
| **STEALTH** | SAFE, GREEN       | Start misji                           |
| **ALERT**   | AWARE, YELLOW     | BLUFOR blisko (<150m) lub zabity wrog |
| **COMBAT**  | COMBAT, RED, FULL | 2+ zabitych wrogow lub strzaly        |

**Jak dziala w grze:**

- Na poczatku wszyscy wrogowie sa spokojni (SAFE)
- Gdy gracz podejdzie za blisko — ALERT (wrogowie zaczynaja patrolowac)
- Gdy zaczyna sie walka — COMBAT (wszystkie grupy atakuja agresywnie)
- Hint na ekranie informuje o zmianie stanu

### 5.2 Counterattack (Kontratak)

Wrogi kontratak po spenieniu warunku.

```json
{
  "counterattack": {
    "enabled": true,
    "trigger": "obj_complete",
    "delay_seconds": 120,
    "spawn_position": [15000, 0, 17000],
    "target_position": [14200, 0, 16500],
    "units": ["O_Soldier_SL_F", "O_Soldier_F", "O_Soldier_F", "O_Soldier_AR_F", "O_Soldier_GL_F", "O_Soldier_F"],
    "vehicle_class": "O_APC_Wheeled_02_rcws_v2_F"
  }
}
```

**Wyzwalacze (trigger):**

- `obj_complete` — po wykonaniu pierwszego celu (zadania)
- `timer` — po okreslonym czasie (delay_seconds)
- `alert_combat` — gdy alert przejdzie w stan COMBAT

**Jak dziala:** Grupa wroga spawnuje sie na `spawn_position` z opcjonalnym pojazdem, przechodzi w tryb COMBAT i rusza SAD w kierunku `target_position`. Hint: "Kontratak wroga! Wzmocnienia w drodze!"

### 5.3 IED (Improvised Explosive Device)

Miny na drogach ukryte pod smieciami.

```json
{
  "ied": {
    "enabled": true,
    "positions": [[14300, 0, 16400], [14400, 0, 16500]],
    "count_per_zone": 3,
    "radius": 200
  }
}
```

**Jak dziala:** System szuka drog w promieniu `radius` od pozycji, umieszcza miny (APERSBoundingMine) zamaskowane obiektami Land_GarbagePallet_F. Jesli `positions` jest puste, IED sa rozmieszczane wokol stref OPFOR.

### 5.4 Hold Position (Utrzymaj pozycje)

Utrzymaj zone przez okreslony czas.

```json
{
  "hold_position": {
    "enabled": true,
    "position": [14200, 0, 16500],
    "duration_seconds": 1200,
    "radius": 100
  }
}
```

**Jak dziala:**

- Tworzy marker ELLIPSE na mapie (stefa do utrzymania)
- Timer zaczyna odliczac gdy BLUFOR wejdzie w zone
- Jesli BLUFOR opusci zone — timer resetuje sie!
- HUD pokazuje: "HOLD: 15:30" (czas pozostaly)
- Ostatnia minuta — ostrzezenie
- Po uplywie czasu — task SUCCEEDED

### 5.5 Extraction (Ewakuacja)

Punkt ewakuacji — konczy misje.

```json
{
  "extraction": {
    "enabled": true,
    "position": [14800, 0, 15800],
    "radius": 30,
    "condition": "all_objectives"
  }
}
```

**Warunki (condition):**

- `all_objectives` — punkt aktywny dopiero po wykonaniu wszystkich celow
- Inne — punkt aktywny od razu

**Jak dziala:** Tworzy marker EXFIL, task "Dotrzec do punktu ewakuacji". Gdy BLUFOR wejdzie w promien — misja zakonczona sukcesem.

### 5.6 Mortar (Ostrzal mozdzierzowy)

```json
{
  "mortar": {
    "enabled": true,
    "target_position": [14200, 0, 16500],
    "rounds": 8,
    "spread": 80,
    "delay_trigger": "alert_combat"
  }
}
```

**Wyzwalacze:**

- `alert_combat` — gdy stan alertu przejdzie w COMBAT + 30 sekund opoznienia
- Inne — po 120 sekundach od startu misji

**Jak dziala:** Hint "UWAGA! Ostrzal mozdzierzowy!", potem 8 pociskow 82mm z losowym rozrzutem (80m) wokol `target_position`. Odstepu miedzy pociskami: 3-5 sekund.

### 5.7 Reinforcement Waves (Fale wzmocnien)

```json
{
  "reinforcement_waves": [
    {
      "delay": 300,
      "position": [15000, 0, 17000],
      "units": ["O_Soldier_SL_F", "O_Soldier_F", "O_Soldier_F", "O_Soldier_AR_F"],
      "vehicle": "O_MRAP_02_F"
    },
    {
      "delay": 600,
      "position": [14800, 0, 17200],
      "units": ["O_Soldier_SL_F", "O_Soldier_F", "O_Soldier_F", "O_Soldier_F", "O_Soldier_GL_F", "O_medic_F"],
      "vehicle": ""
    }
  ]
}
```

**Jak dziala:** Kazda fala spawnuje po `delay` sekundach. Jednostki pojawiaja sie na `position`, wsiadaja do pojazdu (jesli jest), i ruszaja SAD w kierunku najblizszego gracza. Hint informuje o kierunku: "Wrogowie wzmocnienia z kierunku wschod!"

### 5.8 Supply Drops (Zrzuty zaopatrzenia)

```json
{
  "supply_drops": [
    {"position": [14300, 0, 16200], "type": "ammo", "delay": 900}
  ]
}
```

**Jak dziala:** Po `delay` sekundach helikopter (B_Heli_Transport_03_F) przyleci z 2km i zrzuci skrzynie z zaopatrzeniem. Hint: "Zaopatrzenie w drodze! ETA 30 sekund." -> "Zaopatrzenie zrzucone!"

### 5.9 Weather Transitions (Zmiany pogody)

```json
{
  "weather_transitions": [
    {"delay": 1800, "overcast": 0.8, "rain": 0.5, "fog": 0.1}
  ]
}
```

**Jak dziala:** Po `delay` sekundach pogoda plynnie przechodzi do nowych wartosci. Pozwala na dynamiczne scenariusze — np. start w sloncu, potem burza.

### 5.10 Flare Illumination (Oswietlenie flarami)

```json
{
  "flare_illumination": {
    "position": [14200, 0, 16500],
    "interval": 60,
    "count": 10
  }
}
```

**Jak dziala:** Co `interval` sekund odpala flare (F_40mm_White) na wysokosci 200m nad `position`. Idealne do misji nocnych.

### 5.11 Ambient Combat (Odlegle walki)

```json
{
  "ambient_combat": {
    "position": [12000, 0, 15000],
    "interval": 30,
    "duration": 1800
  }
}
```

**Jak dziala:** Przez `duration` sekund, co `interval` generuje odlegle odglosy eksplozji w promieniu 2km od `position`. Swiat zyje — gdzies w tle toczy sie walka.

### 5.12 Intel Objects (Obiekty inteligencji)

```json
{
  "intel_objects": [
    {
      "position": [14200, 0, 16500],
      "task_id": "intel_laptop",
      "class": "Land_Laptop_unfolded_F"
    }
  ]
}
```

**Jak dziala:** Spawnuje obiekt (domyslnie laptop) z akcja "Zbierz intel". Gracz podchodzi, wciska akcje, odgrywa animacje (8 sekund), task SUCCEEDED. Obiekt znika.

### 5.13 Destroy Targets (Cele do zniszczenia)

```json
{
  "destroy_targets": [
    {
      "position": [14400, 0, 16600],
      "task_id": "destroy_fuel",
      "class": "Land_CanisterFuel_F"
    }
  ]
}
```

**Jak dziala:** Spawnuje obiekt (np. beczki z paliwem). Monitor sprawdza co 3 sekundy czy obiekt zostal zniszczony. Jesli tak — task SUCCEEDED, hint "Cel zniszczony!"

---

## 6. PATHING I NAWIGACJA

### 6.1 Inteligentny pathfinding po drogach (findRoadPath)

Framework posiada wbudowany system GPS — BFS (Breadth-First Search) po sieci drogowej ARMA 3.

**7BOW_fnc_findRoadPath** — znajduje trase miedzy dwoma punktami po drogach:

1. Szuka najblizszych drog do punktu startowego i koncowego
2. Uruchamia priorytetowy BFS (rozszerza wezel najblizszy do celu)
3. Konwertuje sciezke drog na waypoints
4. Inteligentne samplowanie — wiecej waypointow na zakretach, mniej na prostych
5. Fallback na prosta linie jesli brak drog

**Parametry:** max 300 krokow BFS, tolerance 50m, waypoint co zmiane kierunku >15 stopni lub 200m.

### 6.2 Smart Vehicle Patrol (generateRoadPatrol + smartVehiclePatrol)

Wymaga TYLKO pozycji i promienia — sam generuje trase po drogach.

```
[pojazd, pozycja, promien, predkosc] -> automatyczny patrol po drogach w promieniu
```

**7BOW_fnc_generateRoadPatrol** — generuje kolista trase po drogach:

1. Szuka drog w promieniu
2. Sortuje po kacie od centrum
3. Wybiera rownomiernie rozlozone punkty
4. Zamyka petle (CYCLE waypoint)

**7BOW_fnc_smartVehiclePatrol** — pelny smart patrol:

1. Generuje trase z generateRoadPatrol
2. Spawnuje pojazd na pierwszej drodze
3. Dodaje waypoints z MOVE + CYCLE
4. Ustawia predkosc, behaviour, combat mode

### 6.3 Smart Infantry Patrol

**7BOW_fnc_smartInfantryPatrol** — jak vehicle patrol ale dla piechoty:

- Jesli sa drogi — patrol po drogach
- Jesli nie ma drog — fallback na 4 punkty wokol centrum (co 90 stopni)
- Formacja, predkosc, behaviour konfigurowalne

### 6.4 Smart Convoy (GPS pathfinding miedzy miastami)

**7BOW_fnc_smartConvoy** — konwoj z pelnym GPS:

1. **Kalkulacja trasy** — uzywa findRoadPath do obliczenia pelnej trasy PRZED spawnem
2. **Spawn z odstepu** — kazdy pojazd offsetowany o `spacing` metrow wzdluz kierunku trasy
3. **Ta sama trasa** — wszystkie pojazdy dostaja IDENTYCZNE waypoints
4. **Limiter predkosci** — zapobiega wyprzedzaniu (limitSpeed)
5. **Combat reaction** — monitor walki

### 6.5 Convoy Combat Reaction System

Wbudowany w 7BOW_fnc_smartConvoy:

1. **Monitor** — co 3 sekundy sprawdza czy konwoj jest atakowany
2. **Detekcja** — damage pojazdu > 0.1 LUB wrog w promieniu 300m
3. **Reakcja walki:**
   - Wszystkie grupy przechodzac w COMBAT/RED/FULL
   - Piechota wysiada z ciezarowek (kierowcy/strzelcy zostaja)
   - Wylogowanie do RPT: "Convoy under attack!"
4. **Wznowienie ruchu** — po 30s bez kontaktu, powrot do SAFE/YELLOW/LIMITED

### 6.6 Manual vs Automatic Routes

**Manualny:** Podajesz `patrol_route` w konfiguracji — AI uzywa dokladnie tych waypointow.

**Automatyczny:** Nie podajesz `patrol_route` (null/puste) — system automatycznie generuje trase:

- Patrol piechoty -> `7BOW_fnc_smartInfantryPatrol`
- Patrol pojazdu -> `7BOW_fnc_smartVehiclePatrol`
- Konwoj -> `7BOW_fnc_smartConvoy`

---

## 7. POJAZDY

### 7.1 Player Vehicles (Pojazdy graczy)

```json
{
  "player_vehicles": [
    {
      "vehicle_class": "B_MRAP_01_F",
      "callsign": "VIC 1",
      "position": [14500, 0, 16100],
      "spawn_area": "road",
      "crew_roles": []
    }
  ]
}
```

**spawn_area:**

- `"helipad"` — pojazdy lotnicze sa spawnowane na najblizszym helipadzie (7BOW_fnc_findHelipad)
- `"garage"` — pojazdy ladowe szukaja garazu/hangaru (7BOW_fnc_findGarage)
- `"road"` — spawn na najblizszej drodze (7BOW_fnc_spawnVehicleOnRoad)
- Inne / puste — spawn na plaskim terenie

System automatycznie rozpoznaje typ pojazdu (heli/plane/jet/vtol -> helipad, reszta -> teren).

### 7.2 Air Support (Wsparcie powietrzne)

```json
{
  "air_support": {
    "enabled": true,
    "aircraft": [
      {
        "callsign": "HAWK 1",
        "vehicle_class": "B_Heli_Transport_01_F",
        "pilot_role": "helicopter_pilot",
        "position": [14600, 0, 16000],
        "direction": 90,
        "spawn_type": "ground",
        "spawn_location": "helipad"
      }
    ]
  }
}
```

**spawn_type:**

- `"fly"` — spawn w powietrzu z predkoscia (7BOW_fnc_spawnAircraft), nie stall-uje
- `"ground"` — na helipadzie/terenie

### 7.3 OPFOR Vehicles

Pojazdy wroga sa spawnowane automatycznie dla pozycji z `composition: "motorized"` lub `"mechanized"` i `vehicle_class`.

### 7.4 Domyslny pojazd

Jesli nie zdefiniujesz zadnych player_vehicles, system automatycznie spawnuje B_MRAP_01_F obok pozycji gracza.

---

## 8. GEAR I LOADOUTY

### 8.1 Virtual Arsenal

```json
{
  "resupply": [
    {"position": [14500, 0, 16100], "type": "arsenal"}
  ]
}
```

Tworzy skrzynie B_supplyCrate_F z pelnym Virtual Arsenal (BIS_fnc_arsenal). Gracze moga wybrac dowolny sprzet.

### 8.2 Gear Crates (Skrzynie z zaopatrzeniem)

```json
{
  "resupply": [
    {"position": [14500, 0, 16120], "type": "ammo"},
    {"position": [14500, 0, 16140], "type": "medical"},
    {"position": [14500, 0, 16160], "type": "explosives"},
    {"position": [14500, 0, 16180], "type": "at"},
    {"position": [14500, 0, 16200], "type": "special"}
  ]
}
```

**Typy skrzyn:**

| Typ            | Zawartosc                                                                           |
| -------------- | ----------------------------------------------------------------------------------- |
| `ammo`       | 50x 6.5mm mag, 10x belt AR, 20x 9mm, 15x granaty, 15x smoke, 10x 40mm HE, 4x NLAW   |
| `medical`    | 30x apteczka, 3x medikit, 10x smoke, 10x smoke green                                |
| `explosives` | 8x demo charge, 4x satchel, 6x claymore, 4x APERS mine, 2x minedetector             |
| `at`         | 4x NLAW launcher, 8x NLAW ammo, 2x Titan launcher, 4x Titan AT                      |
| `special`    | 2x DMR, 2x EBR, celowniki, tlumiki, 10x NVG, lornetki, rangefinder, laserdesignator |
| `general`    | 30x mag, 15x apteczka, 10x granat, 10x smoke                                        |

### 8.3 Loadout Presets

```json
{
  "loadout_presets": {
    "squad_leader": {
      "primary_weapon": "arifle_MX_F",
      "primary_mags": 8,
      "secondary_weapon": "hgun_P07_F",
      "secondary_mags": 3,
      "optic": "optic_MRCO",
      "suppressor": "muzzle_snds_H",
      "vest": "V_PlateCarrier1_rgr",
      "uniform": "U_B_CombatUniform_mcam",
      "helmet": "H_HelmetB",
      "backpack": "B_AssaultPack_rgr",
      "nvg": "NVGoggles",
      "items": ["FirstAidKit", "ItemGPS"],
      "extra_mags": [
        {"classname": "HandGrenade", "count": 2},
        {"classname": "SmokeShell", "count": 2}
      ]
    }
  }
}
```

### 8.4 Jak dziala 7BOW_fnc_applyLoadout

1. Usuwa CALY sprzet z jednostki (bron, ubrania, plecak, helm, gogle)
2. Zaklada ubranie, kamizelke, helm, plecak, gogle
3. Dodaje magazynki broni glownej, potem bron (wazna kolejnosc!)
4. Dodaje dodatki: celownik, tlumik, dwojnog, latarka
5. Dodaje bron boczna (pistolet) + magazynki
6. Dodaje launcher + amunicje
7. Dodaje NVG
8. Dodaje przedmioty (apteczki, granaty, etc.)
9. Zawsze daje: ItemMap, ItemCompass, ItemWatch, ItemRadio

---

## 9. KOMUNIKACJA

### 9.1 ACRE2 Setup

```json
{
  "radio": {
    "system": "acre2",
    "channels": [
      {"name": "ALPHA", "frequency": 1},
      {"name": "BRAVO", "frequency": 2},
      {"name": "CMD", "frequency": 5}
    ]
  }
}
```

**7BOW_fnc_setupACRE2** automatycznie przydziela radia na podstawie roli:

| Rola                        | Radio                                        |
| --------------------------- | -------------------------------------------- |
| Wszyscy                     | AN/PRC-343 (krotki zasieg, wewnatrz druzyny) |
| SL, TL, Sergeant            | AN/PRC-152 (sredni zasieg, miedzy druzynami) |
| PL, RATELO, FAC, Lieutenant | AN/PRC-117F (daleki zasieg, platoon/CAS)     |
| Piloci                      | AN/PRC-152                                   |

**Kanaly:**

- PRC-343: kanal = druzyna wewnetrzna
- PRC-152: kanal 1 = siec druzyny, kanal 2 = siec plutonu
- PRC-117F: kanal 1 = siec plutonu, kanal 2 = batalion/CAS

### 9.2 TFAR Setup

```json
{
  "radio": {
    "system": "tfar"
  }
}
```

**7BOW_fnc_setupTFAR** — prostsza konfiguracja:

- Liderzy, sierzanci, RATELO, oficerowie dostaja tf_anprc152

### 9.3 Informacja w briefingu

System radia jest automatycznie wlaczony w briefingu misji. Gracze widza przydzielone kanaly i czestotliwosci.

---

## 10. SQF FUNCTIONS REFERENCE

Lista wszystkich 45 7BOW_fnc_* z krotkim opisem.

### SPAWN (7 funkcji)

#### 7BOW_fnc_spawnGroup

Spawnuje grupe piechoty z terrain snap.

```sqf
// Parametry: pozycja, strona, tablica klas
_grp = [[14200, 16500, 0], east, ["O_Soldier_SL_F", "O_Soldier_F", "O_Soldier_AR_F"]] call 7BOW_fnc_spawnGroup;
```

#### 7BOW_fnc_spawnGroupInBuilding

Spawnuje grupe WEWNATRZ budynkow (losowe pozycje budynkowe).

```sqf
// Parametry: pozycja, strona, klasy, [promien]
_grp = [[14200, 16500, 0], east, ["O_Soldier_F", "O_Soldier_F"], 100] call 7BOW_fnc_spawnGroupInBuilding;
```

#### 7BOW_fnc_spawnVehicle

Spawnuje pojazd z terrain snap. Opcjonalnie z zaloga.

```sqf
// Parametry: klasa, pozycja, [kierunek], [z_zaloga]
_veh = ["O_MRAP_02_F", [14200, 16500, 0], 90, true] call 7BOW_fnc_spawnVehicle;
```

#### 7BOW_fnc_spawnVehicleOnRoad

Spawnuje pojazd na najblizszej drodze w promieniu.

```sqf
// Parametry: klasa, pozycja, [promien], [z_zaloga]
_veh = ["O_MRAP_02_F", [14200, 16500, 0], 200, true] call 7BOW_fnc_spawnVehicleOnRoad;
```

#### 7BOW_fnc_spawnAircraft

Spawnuje statek powietrzny w locie (z predkoscia, nie stall-uje).

```sqf
// Parametry: klasa, pozycja, [kierunek], [wysokosc], [predkosc]
_ac = ["O_Heli_Light_02_F", [14200, 16500, 0], 90, 200, 60] call 7BOW_fnc_spawnAircraft;
```

#### 7BOW_fnc_spawnObject

Spawnuje statyczny obiekt z terrain snap (fortyfikacje, barykady, skrzynie).

```sqf
// Parametry: klasa, pozycja, [kierunek]
_obj = ["Land_BagFence_Long_F", [14200, 16500, 0], 45] call 7BOW_fnc_spawnObject;
```

#### 7BOW_fnc_spawnConvoy

Spawnuje konwoj pojazdow z waypointami.

```sqf
// Parametry: tablica klas, trasa, strona, [predkosc]
_convoy = [["O_Truck_02_F", "O_MRAP_02_F"], _route, east, "LIMITED"] call 7BOW_fnc_spawnConvoy;
```

### POSITION (5 funkcji)

#### 7BOW_fnc_findHelipad

Szuka helipadu lub plaskiego terenu do ladowania.

```sqf
_padPos = [[14200, 16500, 0], 500] call 7BOW_fnc_findHelipad;
```

#### 7BOW_fnc_indoorPos

Znajduje pozycje wewnatrz budynku (okna, pokoje).

```sqf
_roomPos = [[14200, 16500, 0], 100] call 7BOW_fnc_indoorPos;
```

#### 7BOW_fnc_findGarage

Szuka garazu, szopy lub hangaru dla pojazdu.

```sqf
_garagePos = [[14200, 16500, 0], 300] call 7BOW_fnc_findGarage;
```

#### 7BOW_fnc_findRoadPos

Znajduje pozycje na najblizszej drodze.

```sqf
_roadPos = [[14200, 16500, 0], 200] call 7BOW_fnc_findRoadPos;
```

#### 7BOW_fnc_findFlatPos

Szuka bezpiecznej, plaskiej pozycji.

```sqf
_flatPos = [[14200, 16500, 0], 0, 200, 5] call 7BOW_fnc_findFlatPos;
```

### GEAR (3 funkcje)

#### 7BOW_fnc_applyLoadout

Aplikuje pelny loadout na jednostke (strip + equip).

```sqf
[_unit, _loadoutHashMap] call 7BOW_fnc_applyLoadout;
```

#### 7BOW_fnc_spawnArsenal

Tworzy Virtual Arsenal crate.

```sqf
_box = [[14200, 16500, 0]] call 7BOW_fnc_spawnArsenal;
```

#### 7BOW_fnc_spawnGearCrate

Tworzy pre-loaded skrzynie z zaopatrzeniem.

```sqf
// Parametry: pozycja, typ ("ammo"/"medical"/"explosives"/"at"/"special"), [klasa]
_box = [[14200, 16500, 0], "ammo"] call 7BOW_fnc_spawnGearCrate;
```

### AI (2 funkcje)

#### 7BOW_fnc_setSkills

Ustawia skill AI — wszystkie podumiejetnosci (celnosc, refleks, odwaga, etc.).

```sqf
// Parametry: grupa, baza, zakres
[_grp, 0.4, 0.3] call 7BOW_fnc_setSkills;
// Kazda jednostka dostaje: baza + random(zakres), wiec 0.4-0.7
```

#### 7BOW_fnc_garrison

Rozmieszcza grupe w budynkach (pozycje budynkowe, losowe).

```sqf
// Parametry: grupa, pozycja, [promien]
[_grp, [14200, 16500, 0], 150] call 7BOW_fnc_garrison;
```

### ENVIRONMENT (3 funkcje)

#### 7BOW_fnc_weatherTransition

Dynamiczna zmiana pogody w trakcie misji.

```sqf
// Parametry: opoznienie, zachmurzenie, deszcz, mgla, [czas_przejscia]
[1800, 0.8, 0.5, 0.1, 300] call 7BOW_fnc_weatherTransition;
```

#### 7BOW_fnc_flareIllum

Periodyczne flary nad obszarem (misje nocne).

```sqf
// Parametry: pozycja, [interwal], [ilosc], [wysokosc]
[[14200, 16500, 0], 60, 10, 200] call 7BOW_fnc_flareIllum;
```

#### 7BOW_fnc_ambientCombat

Odlegle odglosy walki (atmosfera).

```sqf
// Parametry: pozycja, [interwal], [czas_trwania]
[[12000, 15000, 0], 30, 1800] call 7BOW_fnc_ambientCombat;
```

### OBJECTIVES (4 funkcje)

#### 7BOW_fnc_spawnIntel

Intel do zebrania (laptop, dokumenty) z interakcja.

```sqf
// Parametry: pozycja, task_id, [klasa], [czas_interakcji]
_obj = [[14200, 16500, 0], "intel_1", "Land_Laptop_unfolded_F", 8] call 7BOW_fnc_spawnIntel;
```

#### 7BOW_fnc_spawnDestroyTarget

Cel do zniszczenia z monitorem.

```sqf
// Parametry: pozycja, task_id, [klasa]
_obj = [[14200, 16500, 0], "destroy_fuel", "Land_CanisterFuel_F"] call 7BOW_fnc_spawnDestroyTarget;
```

#### 7BOW_fnc_reinforcementWaves

Fale wzmocnien wroga z opoznieniem.

```sqf
// Parametry: tablica fal [[delay, pos, units, vehicle], ...]
[[[300, _pos, _units, "O_MRAP_02_F"], [600, _pos2, _units2, ""]]] call 7BOW_fnc_reinforcementWaves;
```

#### 7BOW_fnc_supplyDrop

Zrzut zaopatrzenia helikopterem.

```sqf
// Parametry: pozycja_zrzutu, [typ_skrzyni], [opoznienie]
[[14200, 16500, 0], "ammo", 900] call 7BOW_fnc_supplyDrop;
```

### PATHING (10 funkcji)

#### 7BOW_fnc_findRoadPath

GPS-style pathfinder — BFS po sieci drogowej.

```sqf
// Parametry: start, koniec, [max_krokow]
_route = [[14000, 16000, 0], [15000, 17000, 0], 300] call 7BOW_fnc_findRoadPath;
// Zwraca: [[x,y,0], [x,y,0], ...] — waypoints po drogach
```

#### 7BOW_fnc_generateRoadPatrol

Generuje kolista trase po drogach wokol punktu.

```sqf
// Parametry: centrum, [promien], [ilosc_waypointow]
_route = [[14200, 16500, 0], 400, 6] call 7BOW_fnc_generateRoadPatrol;
```

#### 7BOW_fnc_smartVehiclePatrol

Smart patrol pojazdu — auto-trasa po drogach.

```sqf
// Parametry: klasa, centrum, [promien], [predkosc], [behaviour]
_veh = ["O_MRAP_02_F", [14200, 16500, 0], 400, "LIMITED", "SAFE"] call 7BOW_fnc_smartVehiclePatrol;
```

#### 7BOW_fnc_smartInfantryPatrol

Smart patrol piechoty — auto-trasa po drogach.

```sqf
// Parametry: klasy, centrum, strona, [promien], [predkosc], [formacja]
_grp = [["O_Soldier_TL_F","O_Soldier_F","O_Soldier_AR_F","O_Soldier_GL_F"], [14200, 16500, 0], east, 300, "LIMITED", "WEDGE"] call 7BOW_fnc_smartInfantryPatrol;
```

#### 7BOW_fnc_smartConvoy

Smart convoy z GPS pathfindingiem, spacing, combat reaction.

```sqf
// Parametry: klasy pojazdow, start, koniec, [predkosc], [odstep], [combat_reaction]
_convoy = [["O_Truck_02_F","O_MRAP_02_F","O_Truck_02_F"], _start, _end, "LIMITED", 40, true] call 7BOW_fnc_smartConvoy;
```

#### 7BOW_fnc_vehiclePatrol

Patrol pojazdu po manualnych waypointach (cykliczny).

```sqf
// Parametry: klasa, waypoints, strona, [predkosc], [behaviour], [combat]
_veh = ["O_MRAP_02_F", _waypoints, east, "LIMITED", "SAFE", "YELLOW"] call 7BOW_fnc_vehiclePatrol;
```

#### 7BOW_fnc_infantryPatrol

Patrol piechoty po manualnych waypointach (cykliczny).

```sqf
// Parametry: klasy, waypoints, strona, [predkosc], [behaviour], [formacja]
_grp = [_classes, _waypoints, east, "LIMITED", "SAFE", "WEDGE"] call 7BOW_fnc_infantryPatrol;
```

#### 7BOW_fnc_aircraftPatrol

Patrol powietrzny (krazenie po waypointach).

```sqf
// Parametry: klasa, waypoints, strona, [wysokosc], [predkosc]
_ac = ["O_Heli_Light_02_F", _waypoints, east, 200, 50] call 7BOW_fnc_aircraftPatrol;
```

#### 7BOW_fnc_sadPatrol

Search and Destroy patrol — agresywny.

```sqf
// Parametry: klasy, waypoints, strona
_grp = [_classes, _waypoints, east] call 7BOW_fnc_sadPatrol;
```

#### 7BOW_fnc_guardRoute

Trasa wartownicza — patrol z przystankami.

```sqf
// Parametry: klasy, waypoints, strona, [czas_strazowania]
_grp = [_classes, _waypoints, east, 120] call 7BOW_fnc_guardRoute;
```

### MECHANICS (6 funkcji)

#### 7BOW_fnc_setAlertState

Zmienia stan alertu wroga.

```sqf
["COMBAT"] call 7BOW_fnc_setAlertState;
```

#### 7BOW_fnc_startAlertMonitor

Uruchamia monitor alertu (shots, casualties, proximity).

```sqf
[500, 800] call 7BOW_fnc_startAlertMonitor;
```

#### 7BOW_fnc_counterattack

Spawnuje kontratak wroga.

```sqf
// Parametry: cel, spawn, jednostki, opoznienie, [pojazd]
[_targetPos, _spawnPos, _units, 0, "O_APC_Wheeled_02_rcws_v2_F"] call 7BOW_fnc_counterattack;
```

#### 7BOW_fnc_spawnIED

Rozmieszcza IED na drogach.

```sqf
// Parametry: pozycja, [promien], [ilosc]
[[14200, 16500, 0], 200, 3] call 7BOW_fnc_spawnIED;
```

#### 7BOW_fnc_createExtraction

Tworzy punkt ewakuacji.

```sqf
// Parametry: pozycja, [promien], [task_id]
[[14800, 15800, 0], 30, "obj_extract"] call 7BOW_fnc_createExtraction;
```

#### 7BOW_fnc_holdPosition

Obrona pozycji z timerem.

```sqf
// Parametry: pozycja, czas, [promien], [task_id]
[[14200, 16500, 0], 1200, 100, "obj_hold"] call 7BOW_fnc_holdPosition;
```

#### 7BOW_fnc_mortarBarrage

Ostrzal mozdzierzowy.

```sqf
// Parametry: cel, [pociski], [rozrzut], [opoznienie]
[[14200, 16500, 0], 8, 80, 3] call 7BOW_fnc_mortarBarrage;
```

### RADIO (3 funkcje)

#### 7BOW_fnc_setupACRE2

Automatyczny setup radii ACRE2 na podstawie rol.

```sqf
[] call 7BOW_fnc_setupACRE2;
```

#### 7BOW_fnc_setACRE2Channels

Konfiguracja kanalow ACRE2.

```sqf
[[["ALPHA", 1], ["BRAVO", 2], ["CMD", 5]]] call 7BOW_fnc_setACRE2Channels;
```

#### 7BOW_fnc_setupTFAR

Automatyczny setup radii TFAR.

```sqf
[] call 7BOW_fnc_setupTFAR;
```

---

## 11. ARCHITEKTURA TECHNICZNA

### 11.1 Struktura plikow

```
mission-generator/
├── run_server.py              # Start serwera web
├── arma3_mgen/
│   ├── config_schema.py       # Pydantic modele (MissionConfig)
│   ├── config_loader.py       # Wczytywanie JSON/YAML
│   ├── mission_builder.py     # Glowny builder (koordynuje generatory)
│   ├── generators/
│   │   ├── mission_sqm.py     # BLUFOR -> mission.sqm
│   │   ├── init_server.py     # OPFOR/mechaniki -> initServer.sqf
│   │   ├── init_sqf.py        # init.sqf
│   │   ├── init_player_local.py  # initPlayerLocal.sqf
│   │   ├── description_ext.py # description.ext
│   │   ├── briefing.py        # briefing.sqf
│   │   ├── respawn.py         # Respawn config
│   │   ├── sqf_modules.py     # Wszystkie 7BOW_fnc_* (45 funkcji)
│   │   └── mission_folder.py  # Zapis do folderu
│   ├── sqm/
│   │   ├── writer.py          # SQM format writer
│   │   └── id_manager.py      # Unikalne ID dla obiektow SQM
│   └── utils/
│       └── ...
├── web/
│   ├── app.py                 # Flask serwer
│   ├── api/
│   │   └── __init__.py        # REST API endpoints
│   └── templates/
│       └── index.html         # Web UI (terminal-style)
└── tests/
    └── test_sqm_validation.py
```

### 11.2 Jak dziala mission_sqm.py (BLUFOR w SQM)

SQM to format binarny/tekstowy ARMA 3 dla mission.sqm. Generator:

1. Iteruje po `config.blufor.groups`
2. Dla kazdej jednostki resolve-uje klase na podstawie roli (`ROLE_CLASSNAMES`)
3. Pozycja SQM: `[east, altitude_ASL, north]` — ustawia altitude na 2000m ASL
4. `initPlayerLocal.sqf` natychmiast snapuje gracza na teren (setPosATL z Z=0)
5. Tylko BLUFOR idzie do SQM — OPFOR spawnuje przez SQF (initServer)

**Dlaczego OPFOR nie jest w SQM?**
SQM ustawia Y=0 (altitude) co powoduje ze AI spawnuje pod ziemia i umiera zanim jakikolwiek skrypt moze to naprawic. Dlatego OPFOR jest spawnowany dynamicznie przez initServer.sqf z terrain snap.

### 11.3 Jak dziala init_server.py (OPFOR w SQF)

Pipeline generacji initServer.sqf:

1. **Terrain snap** — snapuje wszystkie jednostki z SQM na teren
2. **Helper functions** — wstrzykuje 45 7BOW_fnc_* z sqf_modules.py
3. **Radio setup** — ACRE2 lub TFAR
4. **Player vehicles** — helipad/garage/road detection
5. **Air support** — samoloty/helikoptery
6. **OPFOR** — iteruje po zonach i pozycjach, generuje SQF per typ
7. **Hostages** — cywile w budynkach
8. **Civilians** — losowi cywile
9. **Resupply** — Arsenal + skrzynie
10. **Fortifications** — barykady, hesco
11. **Tasks** — BIS_fnc_taskCreate na podstawie markerow objectives
12. **Hostage monitor** — sprawdzanie uratowania
13. **Mission monitor** — zone clear, QRF activation, win/lose
14. **Mechaniki** — alert, counterattack, convoy, IED, hold, extraction, mortar, intel, destroy, reinforcements, supply drops, weather, flares, ambient combat
15. **Time limit** — opcjonalny limit czasu
16. **Summary hint** — "7BOW MISSION READY" z podsumowaniem

### 11.4 Konwersja pozycji

**WAZNE:** Format pozycji rozni sie miedzy konfiguracja a SQF!

- **Config JSON:** `[east, altitude, north]` — trzyelementowa tablica
- **SQF:** `[east, north, 0]` — east i north zamienione miejscami, altitude = 0 (terrain snap)
- **SQM:** `[east, altitude_ASL, north]` — jak config ale z prawdziwa wysokoscia

Funkcja `_sqf()` w init_server.py konwertuje:

```python
def _sqf(pos):
    """Config [east, alt, north] -> SQF [east, north, 0]"""
    return f"[{round(pos[0], 1)}, {round(pos[2], 1)}, 0]"
```

**Uwaga:** pos[0] = east, pos[1] = altitude (ignorowane), pos[2] = north

### 11.5 Terrain Snap System

Problem: ARMA 3 nie snapuje automatycznie spawnowanych jednostek na teren. Jednostki moga byc pod ziemia lub w powietrzu.

Rozwiazanie: Kazda 7BOW_fnc_spawn* funkcja ustawia:

```sqf
_unit setPosATL [getPosATL _unit select 0, getPosATL _unit select 1, 0];
```

Dodatkowo initServer.sqf na poczatku snapuje WSZYSTKIE jednostki z SQM:

```sqf
{ _x setPosATL [getPosATL _x select 0, getPosATL _x select 1, 0] } forEach allUnits;
```

### 11.6 MCP Server

Framework udostepnia MCP (Model Context Protocol) server z narzediami:

- **read_rpt** — czyta logi RPT ARMA 3
- **read_rpt_errors** — filtruje tylko bledy z RPT
- **screenshot** — robi screenshot z gry
- **write_mission_file** — zapisuje pliki do folderu misji
- **read_mission_file** — czyta pliki misji
- **list_missions** — lista wygenerowanych misji

---

## 12. ROZWIAZYWANIE PROBLEMOW

### 12.1 Jednostki pod ziemia

**Objaw:** OPFOR nie widoczny, ale na mapie sa markery.
**Przyczyna:** Brak terrain snap.
**Rozwiazanie:** initServer.sqf automatycznie snapuje. Jesli problem sie powtarza, sprawdz czy initServer.sqf laduje sie poprawnie (RPT logi).

### 12.2 OPFOR nie spawnuje

**Objaw:** Brak wroga na mapie.
**Kroki diagnostyczne:**

1. Otworz logi RPT: `C:\Users\[user]\AppData\Local\Arma 3\[profil]\*.rpt`
2. Szukaj: `7BOW:` — wszystkie logi frameworka zaczynaja sie od tego prefixu
3. Szukaj bledow: `Error`, `undefined variable`, `Type Array, expected Object`
4. Sprawdz czy initServer.sqf jest w folderze misji

### 12.3 Pozycje SQF vs SQM format

**Czesty blad:** Zamienianie east/north w pozycjach.

- **SQM:** `[east, alt, north]`
- **SQF (setPosATL):** `[east, north, alt]`
- **Config:** `[east, alt, north]` (jak SQM)

### 12.4 Jak czytac logi RPT

Plik RPT: `C:\Users\[user]\AppData\Local\Arma 3\[profil]\arma3_[data].rpt`

Wazne linie:

```
7BOW: 15 units snapped          // terrain snap
7BOW: ACRE2 radios assigned     // radio setup
7BOW: 8 OPFOR groups spawned    // spawn wroga
7BOW: READY - 8 OPFOR, 3 tasks  // misja gotowa
7BOW ALERT: STEALTH -> ALERT    // zmiana alertu
7BOW: Counterattack from...     // kontratak
7BOW GPS: Route found!          // pathfinding
7BOW: Convoy under attack!      // convoy system
```

### 12.5 Jak debugowac w ARMA 3

1. **Eden Editor** — otwierz misje, sprawdz pozycje BLUFOR
2. **Debug Console** — w grze nacisnij ESC -> Debug Console:
   ```sqf
   // Policz wrogow
   hint str ({side _x == east && alive _x} count allUnits);

   // Pokaz stan alertu
   hint 7BOW_alertState;

   // Teleportuj do pozycji
   player setPosATL [14200, 16500, 0];

   // Sprawdz taski
   hint str (player call BIS_fnc_tasksUnit);
   ```
3. **RPT logi** — najwazniejsze zrodlo informacji o bledach

---

## 13. PRZYKLADY KOMPLETNYCH KONFIGURACJI

### 13.1 Prosta misja (1 cel, 1 druzyna)

```json
{
  "meta": {
    "mission_name": "7BOW_Simple_Raid",
    "map": "Altis",
    "max_players": 10
  },
  "intel": {
    "hour": 8,
    "weather": 0.0,
    "fog": 0.0
  },
  "blufor": {
    "groups": [
      {
        "callsign": "ALPHA 1",
        "position": [14500, 0, 16200],
        "units": [
          {"role": "squad_leader"},
          {"role": "team_leader"},
          {"role": "autorifleman"},
          {"role": "grenadier"},
          {"role": "rifleman"},
          {"role": "rifleman"},
          {"role": "at_gunner"},
          {"role": "combat_medic"}
        ]
      }
    ]
  },
  "opfor": {
    "skill_range": [0.4, 0.6],
    "zones": [
      {
        "name": "obj_alpha",
        "center": [14200, 0, 16500],
        "positions": [
          {"id": "A-1", "type": "garrison", "position": [14200, 0, 16500], "size": "fireteam"},
          {"id": "A-2", "type": "garrison", "position": [14220, 0, 16520], "size": "fireteam"},
          {"id": "A-3", "type": "patrol", "position": [14250, 0, 16450], "size": "fireteam"}
        ]
      }
    ]
  },
  "markers": {
    "objectives": [
      {"name": "obj_alpha", "text": "Cel ALPHA - Oczyscic wioski", "position": [14200, 0, 16500], "type": "mil_objective", "color": "ColorRed"}
    ],
    "waypoints": [
      {"name": "wp1", "text": "WP1", "position": [14400, 0, 16300]}
    ]
  },
  "respawn": {
    "wave_interval": 600,
    "tickets_per_player": 2
  },
  "resupply": [
    {"position": [14500, 0, 16200], "type": "ammo"}
  ]
}
```

### 13.2 Srednia misja (2 cele, pluton, pojazdy)

```json
{
  "meta": {
    "mission_name": "7BOW_Iron_Fist",
    "map": "Altis",
    "max_players": 30
  },
  "intel": {
    "hour": 6,
    "weather": 0.1,
    "fog": 0.3
  },
  "radio": {
    "system": "acre2",
    "channels": [
      {"name": "ALPHA", "frequency": 1},
      {"name": "BRAVO", "frequency": 2},
      {"name": "CMD", "frequency": 5}
    ]
  },
  "blufor": {
    "groups": [
      {
        "callsign": "CASTLE 1-0",
        "type": "hq",
        "position": [14500, 0, 16100],
        "units": [
          {"role": "platoon_leader", "rank": "LIEUTENANT"},
          {"role": "platoon_sergeant", "rank": "SERGEANT"},
          {"role": "ratelo"},
          {"role": "combat_medic"}
        ]
      },
      {
        "callsign": "CASTLE 1-1",
        "type": "rifle_squad",
        "position": [14510, 0, 16100],
        "units": [
          {"role": "squad_leader"},
          {"role": "team_leader"},
          {"role": "autorifleman"},
          {"role": "grenadier"},
          {"role": "team_leader"},
          {"role": "autorifleman"},
          {"role": "rifleman"},
          {"role": "combat_medic"}
        ]
      },
      {
        "callsign": "CASTLE 1-2",
        "type": "rifle_squad",
        "position": [14520, 0, 16100],
        "units": [
          {"role": "squad_leader"},
          {"role": "team_leader"},
          {"role": "autorifleman"},
          {"role": "grenadier"},
          {"role": "team_leader"},
          {"role": "autorifleman"},
          {"role": "rifleman"},
          {"role": "combat_medic"}
        ]
      },
      {
        "callsign": "CASTLE 1-3",
        "type": "weapons_squad",
        "position": [14530, 0, 16100],
        "units": [
          {"role": "squad_leader"},
          {"role": "mg_gunner"},
          {"role": "mg_assistant"},
          {"role": "at_gunner"},
          {"role": "at_assistant"}
        ]
      }
    ]
  },
  "player_vehicles": [
    {"vehicle_class": "B_MRAP_01_F", "callsign": "VIC 1", "position": [14500, 0, 16080], "spawn_area": "road"},
    {"vehicle_class": "B_MRAP_01_F", "callsign": "VIC 2", "position": [14520, 0, 16080], "spawn_area": "road"}
  ],
  "opfor": {
    "skill_range": [0.5, 0.7],
    "zones": [
      {
        "name": "obj_alpha",
        "center": [14200, 0, 16500],
        "positions": [
          {"id": "A-1", "type": "garrison", "position": [14190, 0, 16490], "size": "fireteam"},
          {"id": "A-2", "type": "garrison", "position": [14210, 0, 16510], "size": "fireteam"},
          {"id": "A-3", "type": "garrison", "position": [14200, 0, 16530], "size": "fireteam"},
          {"id": "A-4", "type": "patrol", "position": [14250, 0, 16450], "size": "fireteam", "speed": "LIMITED"},
          {"id": "A-SNP", "type": "sniper", "position": [14100, 0, 16600]},
          {"id": "A-QRF", "type": "qrf", "position": [14300, 0, 16700], "size": "squad", "composition": "motorized", "vehicle_class": "O_MRAP_02_F", "trigger_radius": 300}
        ]
      },
      {
        "name": "obj_bravo",
        "center": [13800, 0, 16800],
        "positions": [
          {"id": "B-1", "type": "garrison", "position": [13790, 0, 16790], "size": "fireteam"},
          {"id": "B-2", "type": "garrison", "position": [13810, 0, 16810], "size": "squad"},
          {"id": "B-3", "type": "patrol", "position": [13850, 0, 16750], "size": "fireteam"},
          {"id": "B-MG", "type": "mg_nest", "position": [13780, 0, 16830], "static_weapon": "O_HMG_01_high_F"},
          {"id": "B-QRF", "type": "qrf", "position": [13900, 0, 16900], "size": "fireteam", "trigger_radius": 250}
        ]
      }
    ]
  },
  "markers": {
    "objectives": [
      {"name": "obj_alpha", "text": "Cel ALPHA - Wioska polnocna", "position": [14200, 0, 16500], "type": "mil_objective", "color": "ColorRed"},
      {"name": "obj_bravo", "text": "Cel BRAVO - Wioska poludniowa", "position": [13800, 0, 16800], "type": "mil_objective", "color": "ColorRed"}
    ],
    "waypoints": [
      {"name": "wp1", "text": "WP1", "position": [14400, 0, 16300]},
      {"name": "wp2", "text": "WP2", "position": [14200, 0, 16400]},
      {"name": "wp3", "text": "WP3", "position": [14000, 0, 16600]},
      {"name": "wp4", "text": "WP4", "position": [13850, 0, 16750]}
    ],
    "sbf": [
      {"name": "sbf1", "text": "SBF 1", "position": [14100, 0, 16400], "type": "mil_triangle", "color": "ColorBlue"}
    ],
    "rally_points": [
      {"name": "orp", "text": "ORP", "position": [14450, 0, 16200], "type": "mil_dot", "color": "ColorGreen"}
    ]
  },
  "respawn": {
    "wave_interval": 600,
    "tickets_per_player": 2,
    "observer_mode": true
  },
  "resupply": [
    {"position": [14500, 0, 16100], "type": "arsenal"},
    {"position": [14500, 0, 16120], "type": "ammo"},
    {"position": [14500, 0, 16140], "type": "medical"}
  ],
  "extraction": {
    "enabled": true,
    "position": [14600, 0, 15900],
    "radius": 30,
    "condition": "all_objectives"
  }
}
```

### 13.3 Zaawansowana misja (wszystkie mechaniki)

```json
{
  "meta": {
    "mission_name": "7BOW_Shadow_Storm",
    "map": "Altis",
    "max_players": 40
  },
  "intel": {
    "year": 2026,
    "month": 3,
    "day": 15,
    "hour": 5,
    "minute": 30,
    "weather": 0.2,
    "fog": 0.4
  },
  "radio": {
    "system": "acre2",
    "channels": [
      {"name": "ALPHA", "frequency": 1},
      {"name": "BRAVO", "frequency": 2},
      {"name": "CHARLIE", "frequency": 3},
      {"name": "CMD", "frequency": 5}
    ]
  },
  "blufor": {
    "groups": [
      {
        "callsign": "VIKING 1-0",
        "type": "hq",
        "position": [14500, 0, 16100],
        "units": [
          {"role": "platoon_leader", "rank": "LIEUTENANT"},
          {"role": "platoon_sergeant", "rank": "SERGEANT"},
          {"role": "ratelo"},
          {"role": "combat_medic"}
        ]
      },
      {
        "callsign": "VIKING 1-1",
        "type": "rifle_squad",
        "position": [14510, 0, 16100],
        "units": [
          {"role": "squad_leader"},
          {"role": "team_leader"},
          {"role": "autorifleman"},
          {"role": "grenadier"},
          {"role": "team_leader"},
          {"role": "autorifleman"},
          {"role": "rifleman"},
          {"role": "combat_medic"}
        ]
      },
      {
        "callsign": "VIKING 1-2",
        "type": "rifle_squad",
        "position": [14520, 0, 16100],
        "units": [
          {"role": "squad_leader"},
          {"role": "team_leader"},
          {"role": "autorifleman"},
          {"role": "grenadier"},
          {"role": "team_leader"},
          {"role": "autorifleman"},
          {"role": "rifleman"},
          {"role": "combat_medic"}
        ]
      },
      {
        "callsign": "VIKING 1-3",
        "type": "rifle_squad",
        "position": [14530, 0, 16100],
        "units": [
          {"role": "squad_leader"},
          {"role": "team_leader"},
          {"role": "autorifleman"},
          {"role": "grenadier"},
          {"role": "team_leader"},
          {"role": "autorifleman"},
          {"role": "rifleman"},
          {"role": "combat_medic"}
        ]
      },
      {
        "callsign": "VIKING 1-4",
        "type": "weapons_squad",
        "position": [14540, 0, 16100],
        "units": [
          {"role": "squad_leader"},
          {"role": "mg_gunner"},
          {"role": "mg_assistant"},
          {"role": "mg_gunner"},
          {"role": "at_gunner"},
          {"role": "at_assistant"}
        ]
      }
    ]
  },
  "player_vehicles": [
    {"vehicle_class": "B_MRAP_01_F", "callsign": "VIC 1", "position": [14500, 0, 16060], "spawn_area": "road"},
    {"vehicle_class": "B_MRAP_01_F", "callsign": "VIC 2", "position": [14520, 0, 16060], "spawn_area": "road"},
    {"vehicle_class": "B_Truck_01_transport_F", "callsign": "LOGI 1", "position": [14540, 0, 16060], "spawn_area": "road"}
  ],
  "air_support": {
    "enabled": true,
    "aircraft": [
      {
        "callsign": "HAWK 1",
        "vehicle_class": "B_Heli_Transport_01_F",
        "pilot_role": "helicopter_pilot",
        "position": [14600, 0, 16000],
        "spawn_type": "ground",
        "spawn_location": "helipad"
      }
    ]
  },
  "opfor": {
    "skill_range": [0.5, 0.7],
    "zones": [
      {
        "name": "obj_alpha",
        "center": [14200, 0, 16500],
        "positions": [
          {"id": "A-1", "type": "garrison", "position": [14180, 0, 16480], "size": "fireteam"},
          {"id": "A-2", "type": "garrison", "position": [14200, 0, 16500], "size": "fireteam"},
          {"id": "A-3", "type": "garrison", "position": [14220, 0, 16520], "size": "fireteam"},
          {"id": "A-4", "type": "garrison", "position": [14210, 0, 16540], "size": "fireteam"},
          {"id": "A-5", "type": "patrol", "position": [14250, 0, 16450], "size": "fireteam"},
          {"id": "A-6", "type": "patrol", "position": [14150, 0, 16550], "size": "fireteam"},
          {"id": "A-SNP", "type": "sniper", "position": [14100, 0, 16600]},
          {"id": "A-MG", "type": "mg_nest", "position": [14230, 0, 16470]},
          {"id": "A-QRF", "type": "qrf", "position": [14350, 0, 16700], "size": "squad", "composition": "motorized", "vehicle_class": "O_MRAP_02_F", "trigger_radius": 300}
        ],
        "fortifications": [
          {"type": "sandbag", "position": [14200, 0, 16490], "direction": 180},
          {"type": "sandbag", "position": [14210, 0, 16490], "direction": 180}
        ]
      },
      {
        "name": "obj_bravo",
        "center": [13800, 0, 16800],
        "positions": [
          {"id": "B-1", "type": "garrison", "position": [13790, 0, 16790], "size": "fireteam"},
          {"id": "B-2", "type": "garrison", "position": [13810, 0, 16810], "size": "squad"},
          {"id": "B-3", "type": "patrol", "position": [13850, 0, 16750], "size": "fireteam"},
          {"id": "B-CP", "type": "checkpoint", "position": [13900, 0, 16700], "size": "fireteam"},
          {"id": "B-VP", "type": "vehicle_patrol", "position": [13800, 0, 16800], "vehicle_class": "O_MRAP_02_F", "speed": "LIMITED"},
          {"id": "B-QRF", "type": "qrf", "position": [13700, 0, 16900], "size": "squad", "composition": "motorized", "vehicle_class": "O_MRAP_02_F", "trigger_radius": 300}
        ]
      }
    ]
  },
  "markers": {
    "objectives": [
      {"name": "obj_alpha", "text": "Cel ALPHA - Centrum dowodzenia", "position": [14200, 0, 16500], "type": "mil_objective", "color": "ColorRed"},
      {"name": "obj_bravo", "text": "Cel BRAVO - Magazyn broni", "position": [13800, 0, 16800], "type": "mil_objective", "color": "ColorRed"}
    ],
    "waypoints": [
      {"name": "wp1", "text": "WP1", "position": [14400, 0, 16300]},
      {"name": "wp2", "text": "WP2", "position": [14300, 0, 16400]},
      {"name": "wp3", "text": "WP3", "position": [14100, 0, 16500]},
      {"name": "wp4", "text": "WP4", "position": [13950, 0, 16650]},
      {"name": "wp5", "text": "WP5", "position": [13850, 0, 16750]}
    ],
    "sbf": [
      {"name": "sbf1", "text": "SBF 1", "position": [14050, 0, 16380], "type": "mil_triangle", "color": "ColorBlue"},
      {"name": "sbf2", "text": "SBF 2", "position": [13700, 0, 16700], "type": "mil_triangle", "color": "ColorBlue"}
    ],
    "rally_points": [
      {"name": "irp", "text": "IRP", "position": [14500, 0, 16100], "type": "mil_dot", "color": "ColorGreen"},
      {"name": "orp_a", "text": "ORP ALPHA", "position": [14350, 0, 16350], "type": "mil_dot", "color": "ColorGreen"},
      {"name": "orp_b", "text": "ORP BRAVO", "position": [13950, 0, 16650], "type": "mil_dot", "color": "ColorGreen"}
    ],
    "routes": [
      {
        "name": "route_main",
        "text": "MSR",
        "points": [[14500, 0, 16100], [14400, 0, 16300], [14200, 0, 16500], [13950, 0, 16650], [13800, 0, 16800]],
        "color": "ColorBlue"
      }
    ]
  },
  "alert_system": {
    "enabled": true,
    "initial_state": "STEALTH",
    "combat_radius": 500,
    "alert_radius": 800
  },
  "counterattack": {
    "enabled": true,
    "trigger": "obj_complete",
    "delay_seconds": 120,
    "spawn_position": [14500, 0, 17000],
    "target_position": [14200, 0, 16500],
    "units": ["O_Soldier_SL_F", "O_Soldier_F", "O_Soldier_F", "O_Soldier_AR_F", "O_Soldier_GL_F", "O_Soldier_F", "O_Soldier_F", "O_medic_F"],
    "vehicle_class": "O_APC_Wheeled_02_rcws_v2_F"
  },
  "ied": {
    "enabled": true,
    "positions": [[14300, 0, 16350]],
    "count_per_zone": 2,
    "radius": 150
  },
  "mortar": {
    "enabled": true,
    "target_position": [14200, 0, 16500],
    "rounds": 6,
    "spread": 60,
    "delay_trigger": "alert_combat"
  },
  "hold_position": {
    "enabled": true,
    "position": [13800, 0, 16800],
    "duration_seconds": 900,
    "radius": 100
  },
  "extraction": {
    "enabled": true,
    "position": [14600, 0, 15900],
    "radius": 30,
    "condition": "all_objectives"
  },
  "reinforcement_waves": [
    {
      "delay": 600,
      "position": [14600, 0, 17100],
      "units": ["O_Soldier_SL_F", "O_Soldier_F", "O_Soldier_F", "O_Soldier_AR_F"],
      "vehicle": "O_MRAP_02_F"
    },
    {
      "delay": 1200,
      "position": [13500, 0, 17000],
      "units": ["O_Soldier_SL_F", "O_Soldier_F", "O_Soldier_F", "O_Soldier_F", "O_Soldier_GL_F", "O_medic_F"],
      "vehicle": ""
    }
  ],
  "supply_drops": [
    {"position": [14350, 0, 16350], "type": "ammo", "delay": 1800}
  ],
  "weather_transitions": [
    {"delay": 1800, "overcast": 0.8, "rain": 0.5, "fog": 0.0}
  ],
  "flare_illumination": {
    "position": [14200, 0, 16500],
    "interval": 90,
    "count": 8
  },
  "ambient_combat": {
    "position": [12000, 0, 15000],
    "interval": 45,
    "duration": 2400
  },
  "intel_objects": [
    {"position": [14200, 0, 16510], "task_id": "intel_laptop", "class": "Land_Laptop_unfolded_F"}
  ],
  "destroy_targets": [
    {"position": [13810, 0, 16820], "task_id": "destroy_cache", "class": "Box_East_AmmoOrd_F"}
  ],
  "hostages": {
    "enabled": true,
    "hostages": [
      {"id": "hostage_1", "position": [14200, 0, 16500], "count": 1, "task_name": "rescue_agent", "task_text": "Uratuj agenta wywiadu"}
    ]
  },
  "respawn": {
    "wave_interval": 600,
    "tickets_per_player": 2,
    "observer_mode": true
  },
  "resupply": [
    {"position": [14500, 0, 16100], "type": "arsenal"},
    {"position": [14500, 0, 16120], "type": "ammo"},
    {"position": [14500, 0, 16140], "type": "medical"}
  ],
  "time_limit": 120
}
```

Ta misja zawiera: system alertow, kontratak, IED, mortar, hold position, ekstrakcje, 2 fale wzmocnien, zrzut zaopatrzenia, zmiane pogody, flary, ambient combat, intel do zebrania, cel do zniszczenia, zakladnika, i limit czasu 120 minut.

---

## DODATEK A: PRESETY FRAKCJI

| Preset           | Opis            |
| ---------------- | --------------- |
| `vanilla_nato` | NATO (domyslny) |
| `vanilla_csat` | CSAT            |

## DODATEK B: MAPY

| Mapa    | Classname | Mod         |
| ------- | --------- | ----------- |
| Altis   | Altis     | Vanilla     |
| Stratis | Stratis   | Vanilla     |
| Tanoa   | Tanoa     | Apex DLC    |
| Malden  | Malden    | Vanilla     |
| Livonia | Enoch     | Contact DLC |

## DODATEK C: SKROTY

| Skrot | Znaczenie                            |
| ----- | ------------------------------------ |
| ORBAT | Order of Battle (organizacja sil)    |
| OPORD | Operations Order (rozkaz operacyjny) |
| SL    | Squad Leader                         |
| TL    | Team Leader                          |
| AR    | Automatic Rifleman                   |
| AT    | Anti-Tank                            |
| MG    | Machine Gunner                       |
| QRF   | Quick Reaction Force                 |
| IRP   | Initial Rally Point                  |
| ORP   | Objective Rally Point                |
| SBF   | Support by Fire                      |
| PL    | Phase Line                           |
| MSR   | Main Supply Route                    |
| CAS   | Close Air Support                    |
| EXFIL | Exfiltration (ewakuacja)             |
| SAD   | Search and Destroy                   |
| IED   | Improvised Explosive Device          |

---

*7BOW ARMA 3 Mission Generator v0.1.0 — Kamil Padula, 2026*

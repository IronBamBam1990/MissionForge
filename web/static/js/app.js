// IBC ARMA 3 Mission Generator - Frontend Logic

// ============================================
// State
// ============================================
const state = {
    groups: [],
    zones: [],
    markers: [],
    maps: {},
    factions: {},
    groupCounter: 0,
    zoneCounter: 0,
    markerCounter: 0,
};

// ============================================
// Role templates
// ============================================
const ROLES = [
    'platoon_leader', 'platoon_sergeant', 'squad_leader', 'team_leader',
    'autorifleman', 'grenadier', 'rifleman', 'combat_medic', 'medic',
    'ratelo', 'mg_gunner', 'mg_assistant', 'mg_ammo_bearer',
    'at_gunner', 'at_assistant', 'at_ammo_bearer',
    'marksman', 'sniper', 'engineer', 'explosive_specialist',
    'cas_pilot', 'helicopter_pilot'
];

const RANKS = ['PRIVATE', 'CORPORAL', 'SERGEANT', 'LIEUTENANT', 'CAPTAIN', 'MAJOR'];

const GROUP_TEMPLATES = {
    platoon_hq: {
        callsign: 'CASTLE 1-6', type: 'platoon_hq',
        units: [
            { role: 'platoon_leader', rank: 'LIEUTENANT' },
            { role: 'platoon_sergeant', rank: 'SERGEANT' },
            { role: 'ratelo', rank: 'PRIVATE' },
            { role: 'combat_medic', rank: 'CORPORAL' },
        ]
    },
    rifle_squad: {
        callsign: 'CASTLE 1-1', type: 'rifle_squad',
        units: [
            { role: 'squad_leader', rank: 'SERGEANT' },
            { role: 'team_leader', rank: 'CORPORAL' },
            { role: 'autorifleman', rank: 'PRIVATE' },
            { role: 'grenadier', rank: 'PRIVATE' },
            { role: 'rifleman', rank: 'PRIVATE' },
            { role: 'team_leader', rank: 'CORPORAL' },
            { role: 'autorifleman', rank: 'PRIVATE' },
            { role: 'grenadier', rank: 'PRIVATE' },
        ]
    },
    mg_squad: {
        callsign: 'CASTLE 1-4', type: 'mg_squad',
        units: [
            { role: 'squad_leader', rank: 'SERGEANT' },
            { role: 'mg_gunner', rank: 'PRIVATE' },
            { role: 'mg_assistant', rank: 'PRIVATE' },
            { role: 'mg_ammo_bearer', rank: 'PRIVATE' },
        ]
    },
    at_squad: {
        callsign: 'CASTLE 1-5', type: 'at_squad',
        units: [
            { role: 'squad_leader', rank: 'SERGEANT' },
            { role: 'at_gunner', rank: 'PRIVATE' },
            { role: 'at_assistant', rank: 'PRIVATE' },
            { role: 'at_ammo_bearer', rank: 'PRIVATE' },
        ]
    },
    cas: {
        callsign: 'HAWK 1-1', type: 'cas',
        units: [
            { role: 'cas_pilot', rank: 'LIEUTENANT' },
        ]
    },
    custom: {
        callsign: 'CUSTOM', type: 'custom',
        units: [
            { role: 'squad_leader', rank: 'SERGEANT' },
        ]
    }
};

// ============================================
// Initialization
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initRangeInputs();
    initButtons();
    loadMaps();
    loadFactions();
});

function initTabs() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(`tab-${tab.dataset.tab}`).classList.add('active');

            if (tab.dataset.tab === 'preview') updatePreview();
        });
    });
}

function initRangeInputs() {
    ['intel_weather', 'intel_fog', 'opfor_skill_min', 'opfor_skill_max'].forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        const valId = id.replace('intel_', '').replace('opfor_', '') + '_val';
        const valEl = document.getElementById(valId) ||
                      document.getElementById(id.split('_').pop() + '_val');
        if (valEl) {
            el.addEventListener('input', () => { valEl.textContent = el.value; });
        }
    });
    // Fix specific IDs
    const weatherEl = document.getElementById('intel_weather');
    if (weatherEl) weatherEl.addEventListener('input', () => {
        document.getElementById('weather_val').textContent = weatherEl.value;
    });
    const fogEl = document.getElementById('intel_fog');
    if (fogEl) fogEl.addEventListener('input', () => {
        document.getElementById('fog_val').textContent = fogEl.value;
    });
    const skillMinEl = document.getElementById('opfor_skill_min');
    if (skillMinEl) skillMinEl.addEventListener('input', () => {
        document.getElementById('skill_min_val').textContent = skillMinEl.value;
    });
    const skillMaxEl = document.getElementById('opfor_skill_max');
    if (skillMaxEl) skillMaxEl.addEventListener('input', () => {
        document.getElementById('skill_max_val').textContent = skillMaxEl.value;
    });
}

function initButtons() {
    document.getElementById('btn-add-group').addEventListener('click', addGroup);
    document.getElementById('btn-add-zone').addEventListener('click', addZone);
    document.getElementById('btn-add-marker').addEventListener('click', addMarker);
    document.getElementById('btn-generate').addEventListener('click', generateMission);
    document.getElementById('btn-export').addEventListener('click', exportConfig);
    document.getElementById('btn-import').addEventListener('click', () => {
        document.getElementById('file-import').click();
    });
    document.getElementById('file-import').addEventListener('change', importConfig);
}

// ============================================
// Data loading
// ============================================
async function loadMaps() {
    try {
        const res = await fetch('/api/maps');
        const data = await res.json();
        state.maps = data.maps;
        const select = document.getElementById('map_select');
        select.innerHTML = '';
        Object.keys(data.maps).sort().forEach(name => {
            const opt = document.createElement('option');
            opt.value = name;
            opt.textContent = `${name} (${data.maps[name]})`;
            select.appendChild(opt);
        });
        // Default to Altis
        select.value = 'Altis';
    } catch (e) {
        console.error('Failed to load maps:', e);
    }
}

async function loadFactions() {
    try {
        const res = await fetch('/api/factions');
        const data = await res.json();
        state.factions = data.factions;
        ['faction_preset', 'enemy_faction_preset'].forEach(id => {
            const select = document.getElementById(id);
            select.innerHTML = '';
            Object.entries(data.factions).forEach(([key, info]) => {
                const opt = document.createElement('option');
                opt.value = key;
                opt.textContent = `${info.name} (${info.side})`;
                select.appendChild(opt);
            });
        });
        // Set defaults
        const fp = document.getElementById('faction_preset');
        if (fp.querySelector('[value="vanilla_nato"]')) fp.value = 'vanilla_nato';
        const ep = document.getElementById('enemy_faction_preset');
        if (ep.querySelector('[value="vanilla_csat"]')) ep.value = 'vanilla_csat';
    } catch (e) {
        console.error('Failed to load factions:', e);
    }
}

// ============================================
// ORBAT management
// ============================================
function addGroup() {
    const templateKey = document.getElementById('group-template').value;
    const template = JSON.parse(JSON.stringify(GROUP_TEMPLATES[templateKey]));
    const idx = state.groupCounter++;
    template._id = idx;
    template.position = [0, 0, 0];
    state.groups.push(template);
    renderGroups();
}

function removeGroup(id) {
    state.groups = state.groups.filter(g => g._id !== id);
    renderGroups();
}

function addUnitToGroup(groupId) {
    const group = state.groups.find(g => g._id === groupId);
    if (group) {
        group.units.push({ role: 'rifleman', rank: 'PRIVATE' });
        renderGroups();
    }
}

function removeUnitFromGroup(groupId, unitIdx) {
    const group = state.groups.find(g => g._id === groupId);
    if (group && group.units.length > 1) {
        group.units.splice(unitIdx, 1);
        renderGroups();
    }
}

function renderGroups() {
    const container = document.getElementById('orbat-groups');
    container.innerHTML = '';

    state.groups.forEach(group => {
        const card = document.createElement('div');
        card.className = 'group-card';
        card.innerHTML = `
            <div class="card-header">
                <div style="display:flex;gap:8px;align-items:center">
                    <input type="text" value="${group.callsign}" style="width:150px;font-weight:bold"
                        onchange="updateGroupField(${group._id}, 'callsign', this.value)">
                    <span style="color:var(--text-muted);font-size:12px">${group.type}</span>
                </div>
                <div class="card-actions">
                    <div class="position-input" style="display:flex;gap:4px">
                        <input type="number" value="${group.position[0]}" style="width:80px" placeholder="X"
                            onchange="updateGroupPos(${group._id}, 0, this.value)">
                        <input type="number" value="${group.position[2]}" style="width:80px" placeholder="Y"
                            onchange="updateGroupPos(${group._id}, 2, this.value)">
                    </div>
                    <button class="btn btn-sm" onclick="addUnitToGroup(${group._id})">+ Unit</button>
                    <button class="btn btn-sm btn-danger" onclick="removeGroup(${group._id})">X</button>
                </div>
            </div>
            <div class="unit-list">
                ${group.units.map((u, i) => `
                    <div class="unit-row">
                        <select onchange="updateUnit(${group._id}, ${i}, 'role', this.value)">
                            ${ROLES.map(r => `<option value="${r}" ${r === u.role ? 'selected' : ''}>${r.replace(/_/g, ' ')}</option>`).join('')}
                        </select>
                        <select onchange="updateUnit(${group._id}, ${i}, 'rank', this.value)">
                            ${RANKS.map(r => `<option value="${r}" ${r === u.rank ? 'selected' : ''}>${r}</option>`).join('')}
                        </select>
                        <span style="color:var(--text-muted);font-size:12px">#${i + 1}</span>
                        <button class="btn btn-sm btn-danger" onclick="removeUnitFromGroup(${group._id}, ${i})">-</button>
                    </div>
                `).join('')}
            </div>
        `;
        container.appendChild(card);
    });
}

function updateGroupField(id, field, value) {
    const group = state.groups.find(g => g._id === id);
    if (group) group[field] = value;
}

function updateGroupPos(id, idx, value) {
    const group = state.groups.find(g => g._id === id);
    if (group) group.position[idx] = parseFloat(value) || 0;
}

function updateUnit(groupId, unitIdx, field, value) {
    const group = state.groups.find(g => g._id === groupId);
    if (group && group.units[unitIdx]) {
        group.units[unitIdx][field] = value;
    }
}

// ============================================
// OPFOR zones
// ============================================
function addZone() {
    const idx = state.zoneCounter++;
    state.zones.push({
        _id: idx,
        name: `ZONE_${idx + 1}`,
        center: [0, 0, 0],
        positions: []
    });
    renderZones();
}

function removeZone(id) {
    state.zones = state.zones.filter(z => z._id !== id);
    renderZones();
}

function addPosition(zoneId) {
    const zone = state.zones.find(z => z._id === zoneId);
    if (zone) {
        const posIdx = zone.positions.length + 1;
        zone.positions.push({
            id: `${zone.name[0]}-${posIdx}`,
            type: 'garrison',
            position: [...zone.center],
            size: 'fireteam',
            composition: 'infantry',
        });
        renderZones();
    }
}

function removePosition(zoneId, posIdx) {
    const zone = state.zones.find(z => z._id === zoneId);
    if (zone) {
        zone.positions.splice(posIdx, 1);
        renderZones();
    }
}

function renderZones() {
    const container = document.getElementById('opfor-zones');
    container.innerHTML = '';

    state.zones.forEach(zone => {
        const card = document.createElement('div');
        card.className = 'zone-card';
        card.innerHTML = `
            <div class="card-header">
                <div style="display:flex;gap:8px;align-items:center">
                    <input type="text" value="${zone.name}" style="width:150px;font-weight:bold;color:var(--accent-red)"
                        onchange="updateZoneField(${zone._id}, 'name', this.value)">
                    <span style="color:var(--text-muted);font-size:12px">Centrum:</span>
                    <input type="number" value="${zone.center[0]}" style="width:80px" placeholder="X"
                        onchange="updateZoneCenter(${zone._id}, 0, this.value)">
                    <input type="number" value="${zone.center[2]}" style="width:80px" placeholder="Y"
                        onchange="updateZoneCenter(${zone._id}, 2, this.value)">
                </div>
                <div class="card-actions">
                    <button class="btn btn-sm" onclick="addPosition(${zone._id})">+ Pozycja</button>
                    <button class="btn btn-sm btn-danger" onclick="removeZone(${zone._id})">X</button>
                </div>
            </div>
            <div class="unit-list">
                ${zone.positions.map((p, i) => `
                    <div class="position-row">
                        <input type="text" value="${p.id}" style="width:60px"
                            onchange="updatePosField(${zone._id}, ${i}, 'id', this.value)">
                        <select onchange="updatePosField(${zone._id}, ${i}, 'type', this.value)">
                            ${['garrison','patrol','qrf','checkpoint','static'].map(t =>
                                `<option value="${t}" ${t === p.type ? 'selected' : ''}>${t}</option>`
                            ).join('')}
                        </select>
                        <select onchange="updatePosField(${zone._id}, ${i}, 'size', this.value)">
                            ${['fireteam','squad','section'].map(s =>
                                `<option value="${s}" ${s === p.size ? 'selected' : ''}>${s}</option>`
                            ).join('')}
                        </select>
                        <div style="display:flex;gap:4px">
                            <input type="number" value="${p.position[0]}" style="width:70px" placeholder="X"
                                onchange="updatePosCoord(${zone._id}, ${i}, 0, this.value)">
                            <input type="number" value="${p.position[2]}" style="width:70px" placeholder="Y"
                                onchange="updatePosCoord(${zone._id}, ${i}, 2, this.value)">
                        </div>
                        <button class="btn btn-sm btn-danger" onclick="removePosition(${zone._id}, ${i})">-</button>
                    </div>
                `).join('')}
            </div>
        `;
        container.appendChild(card);
    });
}

function updateZoneField(id, field, value) {
    const zone = state.zones.find(z => z._id === id);
    if (zone) zone[field] = value;
}

function updateZoneCenter(id, idx, value) {
    const zone = state.zones.find(z => z._id === id);
    if (zone) zone.center[idx] = parseFloat(value) || 0;
}

function updatePosField(zoneId, posIdx, field, value) {
    const zone = state.zones.find(z => z._id === zoneId);
    if (zone && zone.positions[posIdx]) {
        zone.positions[posIdx][field] = value;
    }
}

function updatePosCoord(zoneId, posIdx, coordIdx, value) {
    const zone = state.zones.find(z => z._id === zoneId);
    if (zone && zone.positions[posIdx]) {
        zone.positions[posIdx].position[coordIdx] = parseFloat(value) || 0;
    }
}

// ============================================
// Markers
// ============================================
function addMarker() {
    const category = document.getElementById('marker-category').value;
    const idx = state.markerCounter++;

    const defaults = {
        objectives: { type: 'hd_objective', color: 'ColorRed', text: `Cel ${idx + 1}` },
        waypoints: { type: 'mil_dot', color: 'ColorBlue', text: `WP ${idx + 1}` },
        phase_lines: { type: 'mil_dot', color: 'ColorYellow', text: `PL ${idx + 1}`, shape: 'RECTANGLE', size_a: 400, size_b: 5 },
        sbf: { type: 'mil_triangle', color: 'ColorBlue', text: `SBF ${idx + 1}` },
        rally_points: { type: 'mil_flag', color: 'ColorGreen', text: `ORP ${idx + 1}` },
        custom: { type: 'mil_dot', color: 'Default', text: `Marker ${idx + 1}` },
    };

    const def = defaults[category] || defaults.custom;
    state.markers.push({
        _id: idx,
        category: category,
        name: `marker_${idx}`,
        text: def.text,
        position: [0, 0, 0],
        type: def.type,
        color: def.color,
        shape: def.shape || 'ICON',
        size_a: def.size_a || 1,
        size_b: def.size_b || 1,
    });
    renderMarkers();
}

function removeMarker(id) {
    state.markers = state.markers.filter(m => m._id !== id);
    renderMarkers();
}

function renderMarkers() {
    const container = document.getElementById('markers-list');
    container.innerHTML = '';

    state.markers.forEach(m => {
        const card = document.createElement('div');
        card.className = 'marker-card';
        card.innerHTML = `
            <div class="card-header">
                <div style="display:flex;gap:8px;align-items:center">
                    <span style="color:var(--text-muted);font-size:11px;text-transform:uppercase">${m.category}</span>
                    <input type="text" value="${m.text}" style="width:150px"
                        onchange="updateMarkerField(${m._id}, 'text', this.value)">
                    <input type="text" value="${m.name}" style="width:120px;color:var(--text-muted)"
                        onchange="updateMarkerField(${m._id}, 'name', this.value)">
                </div>
                <div class="card-actions" style="display:flex;gap:4px;align-items:center">
                    <input type="number" value="${m.position[0]}" style="width:80px" placeholder="X"
                        onchange="updateMarkerPos(${m._id}, 0, this.value)">
                    <input type="number" value="${m.position[2]}" style="width:80px" placeholder="Y"
                        onchange="updateMarkerPos(${m._id}, 2, this.value)">
                    <select onchange="updateMarkerField(${m._id}, 'color', this.value)" style="width:120px">
                        ${['Default','ColorRed','ColorBlue','ColorGreen','ColorYellow','ColorOrange','ColorBlack','ColorWhite','ColorPink','ColorBrown'].map(c =>
                            `<option value="${c}" ${c === m.color ? 'selected' : ''}>${c.replace('Color','')}</option>`
                        ).join('')}
                    </select>
                    <button class="btn btn-sm btn-danger" onclick="removeMarker(${m._id})">X</button>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

function updateMarkerField(id, field, value) {
    const m = state.markers.find(m => m._id === id);
    if (m) m[field] = value;
}

function updateMarkerPos(id, idx, value) {
    const m = state.markers.find(m => m._id === id);
    if (m) m.position[idx] = parseFloat(value) || 0;
}

// ============================================
// Build config
// ============================================
function buildConfig() {
    const val = id => document.getElementById(id)?.value || '';
    const num = id => parseFloat(document.getElementById(id)?.value) || 0;
    const chk = id => document.getElementById(id)?.checked || false;

    // Organize markers by category
    const markersByCategory = {
        objectives: [], phase_lines: [], waypoints: [],
        sbf: [], rally_points: [], custom: []
    };
    state.markers.forEach(m => {
        const cat = markersByCategory[m.category] || markersByCategory.custom;
        cat.push({
            name: m.name,
            text: m.text,
            position: m.position,
            type: m.type,
            color: m.color,
            shape: m.shape,
            size_a: m.size_a,
            size_b: m.size_b,
        });
    });

    // Build groups (separate CAS from regular)
    const regularGroups = [];
    const casAircraft = [];

    state.groups.forEach(g => {
        if (g.type === 'cas') {
            casAircraft.push({
                callsign: g.callsign,
                vehicle_class: 'B_Plane_CAS_01_dynamicLoadout_F',
                pilot_role: 'cas_pilot',
                position: g.position,
                direction: 0,
            });
        } else {
            regularGroups.push({
                callsign: g.callsign,
                type: g.type,
                position: g.position,
                units: g.units.map(u => ({
                    role: u.role,
                    rank: u.rank,
                })),
            });
        }
    });

    // Build zones
    const zones = state.zones.map(z => ({
        name: z.name,
        center: z.center,
        positions: z.positions.map(p => ({
            id: p.id,
            type: p.type,
            position: p.position,
            size: p.size,
            composition: p.composition || 'infantry',
        })),
    }));

    return {
        meta: {
            mission_name: val('mission_name'),
            display_name: val('display_name'),
            author: val('author'),
            map: val('map_select'),
            map_classname_override: val('map_override') || null,
            game_type: val('game_type'),
            max_players: num('max_players') || 40,
        },
        intel: {
            year: num('intel_year') || 2026,
            month: num('intel_month') || 3,
            day: num('intel_day') || 17,
            hour: num('intel_hour') || 6,
            minute: num('intel_minute') || 0,
            weather: parseFloat(val('intel_weather')) || 0,
            fog: parseFloat(val('intel_fog')) || 0,
        },
        faction_preset: val('faction_preset'),
        enemy_faction_preset: val('enemy_faction_preset'),
        radio_system: val('radio_system'),
        blufor: { groups: regularGroups },
        air_support: {
            enabled: casAircraft.length > 0,
            aircraft: casAircraft,
        },
        opfor: {
            skill_range: [
                parseFloat(val('opfor_skill_min')) || 0.4,
                parseFloat(val('opfor_skill_max')) || 0.7,
            ],
            zones: zones,
        },
        markers: markersByCategory,
        respawn: {
            wave_interval: num('wave_interval') || 600,
            tickets_per_player: num('tickets_per_player') || 2,
            observer_mode: chk('observer_mode'),
            reinsert_teleport: chk('reinsert_teleport'),
            technical_respawn: chk('technical_respawn'),
        },
        briefing: {
            language: 'pl',
            situation: val('brief_situation'),
            mission: val('brief_mission'),
            execution: val('brief_execution'),
            logistics: val('brief_logistics'),
            command_signal: val('brief_command'),
        },
    };
}

// ============================================
// Generate
// ============================================
async function generateMission() {
    const statusEl = document.getElementById('status-text');
    statusEl.textContent = 'Generowanie...';
    statusEl.className = '';

    try {
        const config = buildConfig();
        const res = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config),
        });
        const data = await res.json();

        if (data.success) {
            statusEl.textContent = `Wygenerowano: ${data.path}`;
            statusEl.className = 'success';
        } else {
            statusEl.textContent = `Blad: ${data.message}`;
            statusEl.className = 'error';
        }
    } catch (e) {
        statusEl.textContent = `Blad: ${e.message}`;
        statusEl.className = 'error';
    }
}

// ============================================
// Import / Export
// ============================================
function exportConfig() {
    const config = buildConfig();
    const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${config.meta.mission_name || 'mission'}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

function importConfig(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (ev) => {
        try {
            const config = JSON.parse(ev.target.result);
            loadConfigToUI(config);
            document.getElementById('status-text').textContent = 'Zaimportowano konfiguracje';
            document.getElementById('status-text').className = 'success';
        } catch (err) {
            document.getElementById('status-text').textContent = `Blad importu: ${err.message}`;
            document.getElementById('status-text').className = 'error';
        }
    };
    reader.readAsText(file);
    e.target.value = ''; // Reset
}

function loadConfigToUI(config) {
    const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };
    const setChk = (id, val) => { const el = document.getElementById(id); if (el) el.checked = val; };

    // Meta
    if (config.meta) {
        setVal('mission_name', config.meta.mission_name || '');
        setVal('display_name', config.meta.display_name || '');
        setVal('author', config.meta.author || 'IBC');
        setVal('map_select', config.meta.map || 'Altis');
        setVal('map_override', config.meta.map_classname_override || '');
        setVal('max_players', config.meta.max_players || 40);
        setVal('game_type', config.meta.game_type || 'Coop');
    }

    // Intel
    if (config.intel) {
        setVal('intel_year', config.intel.year || 2026);
        setVal('intel_month', config.intel.month || 3);
        setVal('intel_day', config.intel.day || 17);
        setVal('intel_hour', config.intel.hour || 6);
        setVal('intel_minute', config.intel.minute || 0);
        setVal('intel_weather', config.intel.weather || 0);
        setVal('intel_fog', config.intel.fog || 0);
    }

    // Factions
    setVal('faction_preset', config.faction_preset || 'vanilla_nato');
    setVal('enemy_faction_preset', config.enemy_faction_preset || 'vanilla_csat');
    setVal('radio_system', config.radio_system || 'acre2');

    // Groups
    state.groups = [];
    state.groupCounter = 0;
    if (config.blufor?.groups) {
        config.blufor.groups.forEach(g => {
            const idx = state.groupCounter++;
            state.groups.push({
                _id: idx,
                callsign: g.callsign,
                type: g.type,
                position: g.position || [0, 0, 0],
                units: g.units || [],
            });
        });
    }
    // CAS as groups
    if (config.air_support?.aircraft) {
        config.air_support.aircraft.forEach(a => {
            const idx = state.groupCounter++;
            state.groups.push({
                _id: idx,
                callsign: a.callsign,
                type: 'cas',
                position: a.position || [0, 0, 0],
                units: [{ role: 'cas_pilot', rank: 'LIEUTENANT' }],
            });
        });
    }
    renderGroups();

    // OPFOR zones
    state.zones = [];
    state.zoneCounter = 0;
    if (config.opfor?.zones) {
        config.opfor.zones.forEach(z => {
            const idx = state.zoneCounter++;
            state.zones.push({
                _id: idx,
                name: z.name,
                center: z.center || [0, 0, 0],
                positions: z.positions || [],
            });
        });
    }
    setVal('opfor_skill_min', config.opfor?.skill_range?.[0] || 0.4);
    setVal('opfor_skill_max', config.opfor?.skill_range?.[1] || 0.7);
    renderZones();

    // Markers
    state.markers = [];
    state.markerCounter = 0;
    if (config.markers) {
        Object.entries(config.markers).forEach(([cat, list]) => {
            if (Array.isArray(list)) {
                list.forEach(m => {
                    const idx = state.markerCounter++;
                    state.markers.push({
                        _id: idx,
                        category: cat,
                        name: m.name,
                        text: m.text || '',
                        position: m.position || [0, 0, 0],
                        type: m.type || 'mil_dot',
                        color: m.color || 'Default',
                        shape: m.shape || 'ICON',
                        size_a: m.size_a || 1,
                        size_b: m.size_b || 1,
                    });
                });
            }
        });
    }
    renderMarkers();

    // Respawn
    if (config.respawn) {
        setVal('wave_interval', config.respawn.wave_interval || 600);
        setVal('tickets_per_player', config.respawn.tickets_per_player || 2);
        setChk('observer_mode', config.respawn.observer_mode !== false);
        setChk('reinsert_teleport', config.respawn.reinsert_teleport !== false);
        setChk('technical_respawn', config.respawn.technical_respawn !== false);
    }

    // Briefing
    if (config.briefing) {
        setVal('brief_situation', config.briefing.situation || '');
        setVal('brief_mission', config.briefing.mission || '');
        setVal('brief_execution', config.briefing.execution || '');
        setVal('brief_logistics', config.briefing.logistics || '');
        setVal('brief_command', config.briefing.command_signal || '');
    }
}

// ============================================
// Preview
// ============================================
function updatePreview() {
    const config = buildConfig();
    document.getElementById('json-preview').textContent = JSON.stringify(config, null, 2);
}

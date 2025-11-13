// Warhammer 40k Mathhammer Application

// State management
const state = {
    attacker: null,
    defender: null,
    compareAttacker: null,
    compareDefender: null,
    simAttacker: null,
    simDefender: null,
    units: []
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeSearchHandlers();
    initializeButtons();
    loadDatasetInfo();
});

// Tab management
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;

            // Update active states
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            button.classList.add('active');
            document.getElementById(`${tabName}-tab`).classList.add('active');
        });
    });
}

// Search handlers
function initializeSearchHandlers() {
    setupSearch('attackerSearch', 'attackerResults', selectAttacker);
    setupSearch('defenderSearch', 'defenderResults', selectDefender);
    setupSearch('compareAttackerSearch', 'compareAttackerResults', selectCompareAttacker);
    setupSearch('compareDefenderSearch', 'compareDefenderResults', selectCompareDefender);
    setupSearch('simAttackerSearch', 'simAttackerResults', selectSimAttacker);
    setupSearch('simDefenderSearch', 'simDefenderResults', selectSimDefender);
}

function setupSearch(inputId, resultsId, selectCallback) {
    const input = document.getElementById(inputId);
    const results = document.getElementById(resultsId);

    let debounceTimer;
    input.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        const query = e.target.value.trim();

        if (query.length < 2) {
            results.classList.remove('show');
            return;
        }

        debounceTimer = setTimeout(() => searchUnits(query, results, selectCallback), 300);
    });

    // Close results when clicking outside
    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !results.contains(e.target)) {
            results.classList.remove('show');
        }
    });
}

async function searchUnits(query, resultsElement, selectCallback) {
    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const units = await response.json();

        if (units.length === 0) {
            resultsElement.innerHTML = '<div class="search-result-item">No units found</div>';
            resultsElement.classList.add('show');
            return;
        }

        resultsElement.innerHTML = units.map(unit => `
            <div class="search-result-item" data-unit-id="${unit.id}">
                <div class="result-name">${unit.name}</div>
                <div class="result-faction">${unit.faction}</div>
            </div>
        `).join('');

        // Add click handlers
        resultsElement.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', () => {
                const unitId = item.dataset.unitId;
                selectCallback(unitId);
                resultsElement.classList.remove('show');
            });
        });

        resultsElement.classList.add('show');
    } catch (error) {
        console.error('Search error:', error);
        resultsElement.innerHTML = '<div class="search-result-item error-text">Search failed</div>';
        resultsElement.classList.add('show');
    }
}

// Unit selection functions
async function selectAttacker(unitId) {
    const unit = await loadUnit(unitId);
    state.attacker = unit;
    displayUnitInfo(unit, 'attackerInfo');
    populateWeaponSelect(unit, 'weaponSelect');
}

async function selectDefender(unitId) {
    const unit = await loadUnit(unitId);
    state.defender = unit;
    displayUnitInfo(unit, 'defenderInfo');
}

async function selectCompareAttacker(unitId) {
    const unit = await loadUnit(unitId);
    state.compareAttacker = unit;
    displayUnitInfo(unit, 'compareAttackerInfo');
}

async function selectCompareDefender(unitId) {
    const unit = await loadUnit(unitId);
    state.compareDefender = unit;
    displayUnitInfo(unit, 'compareDefenderInfo');
}

async function selectSimAttacker(unitId) {
    const unit = await loadUnit(unitId);
    state.simAttacker = unit;
    displayUnitInfo(unit, 'simAttackerInfo');
    populateWeaponSelect(unit, 'simWeaponSelect');
}

async function selectSimDefender(unitId) {
    const unit = await loadUnit(unitId);
    state.simDefender = unit;
    displayUnitInfo(unit, 'simDefenderInfo');
}

async function loadUnit(unitId) {
    const response = await fetch(`/api/units/${unitId}`);
    return await response.json();
}

function displayUnitInfo(unit, elementId) {
    const element = document.getElementById(elementId);

    let html = `<h4>${unit.name}</h4>`;
    html += `<div style="color: var(--text-secondary); margin-bottom: 10px;">${unit.faction} • ${unit.points} pts</div>`;

    if (unit.profile) {
        html += '<div class="stat-grid">';
        if (unit.profile.movement) html += `<div class="stat-item"><span class="stat-label">M</span><span class="stat-value">${unit.profile.movement}"</span></div>`;
        if (unit.profile.toughness) html += `<div class="stat-item"><span class="stat-label">T</span><span class="stat-value">${unit.profile.toughness}</span></div>`;
        if (unit.profile.save) html += `<div class="stat-item"><span class="stat-label">Sv</span><span class="stat-value">${unit.profile.save}</span></div>`;
        if (unit.profile.wounds) html += `<div class="stat-item"><span class="stat-label">W</span><span class="stat-value">${unit.profile.wounds}</span></div>`;
        if (unit.profile.leadership) html += `<div class="stat-item"><span class="stat-label">Ld</span><span class="stat-value">${unit.profile.leadership}</span></div>`;
        if (unit.profile.oc) html += `<div class="stat-item"><span class="stat-label">OC</span><span class="stat-value">${unit.profile.oc}</span></div>`;
        html += '</div>';
    }

    if (unit.weapons && unit.weapons.length > 0) {
        html += `<div style="margin-top: 10px; color: var(--text-secondary);">${unit.weapons.length} weapon(s) available</div>`;
    }

    element.innerHTML = html;
}

function populateWeaponSelect(unit, selectId) {
    const select = document.getElementById(selectId);
    select.innerHTML = '<option value="">Select a weapon</option>';

    if (unit.weapons) {
        unit.weapons.forEach(weapon => {
            const option = document.createElement('option');
            option.value = weapon.name;
            option.textContent = `${weapon.name} (${weapon.type})`;
            select.appendChild(option);
        });
    }
}

// Button handlers
function initializeButtons() {
    document.getElementById('loadDatasetBtn').addEventListener('click', loadDataset);
    document.getElementById('calculateBtn').addEventListener('click', calculateAttack);
    document.getElementById('compareBtn').addEventListener('click', compareWeapons);
    document.getElementById('simulateBtn').addEventListener('click', simulateCombat);
}

async function loadDataset() {
    const statusElement = document.getElementById('datasetStatus');
    statusElement.innerHTML = '<span class="loading">Loading dataset...</span>';

    try {
        const response = await fetch('/api/load-dataset', { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            statusElement.innerHTML = `<span class="success-text">✓ Loaded ${result.units_loaded} units from ${result.factions} factions</span>`;
        } else {
            statusElement.innerHTML = `<span class="error-text">Failed to load dataset: ${result.error}</span>`;
        }
    } catch (error) {
        statusElement.innerHTML = `<span class="error-text">Error loading dataset</span>`;
        console.error('Dataset load error:', error);
    }
}

async function loadDatasetInfo() {
    try {
        const response = await fetch('/api/dataset/info');
        const info = await response.json();

        const statusElement = document.getElementById('datasetStatus');
        if (info.units_count > 0) {
            statusElement.innerHTML = `<span class="success-text">✓ ${info.units_count} units loaded from ${info.factions_count} factions</span>`;
        } else {
            statusElement.innerHTML = '<span class="warning">No dataset loaded. Add .cat files to datasets/ folder and reload.</span>';
        }
    } catch (error) {
        console.error('Failed to load dataset info:', error);
    }
}

async function calculateAttack() {
    const weaponName = document.getElementById('weaponSelect').value;
    const numModels = parseInt(document.getElementById('numModels').value);

    if (!state.attacker || !state.defender || !weaponName) {
        alert('Please select attacker, defender, and weapon');
        return;
    }

    try {
        const response = await fetch('/api/calculate/attack', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                attacker_id: state.attacker.id,
                weapon_name: weaponName,
                defender_id: state.defender.id,
                num_models: numModels
            })
        });

        const result = await response.json();
        displayAttackResults(result);
    } catch (error) {
        console.error('Calculation error:', error);
        alert('Calculation failed');
    }
}

function displayAttackResults(result) {
    const resultsElement = document.getElementById('attackResults');

    const html = `
        <h3>Attack Results</h3>
        <div style="text-align: center; margin-bottom: 20px; color: var(--text-secondary);">
            ${result.num_models} ${result.attacker} attacking ${result.defender} with ${result.weapon}
        </div>
        <div class="result-grid">
            <div class="result-card">
                <div class="result-label">Expected Hits</div>
                <div class="result-value">${result.expected_hits}</div>
                <div class="result-subtitle">${result.hit_probability}% hit chance</div>
            </div>
            <div class="result-card">
                <div class="result-label">Expected Wounds</div>
                <div class="result-value">${result.expected_wounds}</div>
                <div class="result-subtitle">${result.wound_probability}% wound chance</div>
            </div>
            <div class="result-card">
                <div class="result-label">Unsaved Wounds</div>
                <div class="result-value">${result.expected_unsaved_wounds}</div>
                <div class="result-subtitle">${result.save_failure_probability}% save failure</div>
            </div>
            <div class="result-card">
                <div class="result-label">Expected Damage</div>
                <div class="result-value">${result.expected_damage}</div>
                <div class="result-subtitle">Total damage dealt</div>
            </div>
        </div>
    `;

    resultsElement.innerHTML = html;
}

async function compareWeapons() {
    const numModels = parseInt(document.getElementById('compareNumModels').value);

    if (!state.compareAttacker || !state.compareDefender) {
        alert('Please select both units');
        return;
    }

    try {
        const response = await fetch('/api/compare/weapons', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                unit_id: state.compareAttacker.id,
                defender_id: state.compareDefender.id,
                num_models: numModels
            })
        });

        const result = await response.json();
        displayComparisonResults(result);
    } catch (error) {
        console.error('Comparison error:', error);
        alert('Comparison failed');
    }
}

function displayComparisonResults(result) {
    const resultsElement = document.getElementById('compareResults');

    // Find best weapon
    const best = result.comparison.reduce((max, w) => w.expected_damage > max.expected_damage ? w : max, result.comparison[0]);

    let html = `
        <h3>Weapon Comparison</h3>
        <div style="text-align: center; margin-bottom: 20px; color: var(--text-secondary);">
            ${result.attacker} vs ${result.defender}
        </div>
        <table class="comparison-table">
            <thead>
                <tr>
                    <th>Weapon</th>
                    <th>Expected Hits</th>
                    <th>Expected Wounds</th>
                    <th>Unsaved Wounds</th>
                    <th>Expected Damage</th>
                </tr>
            </thead>
            <tbody>
    `;

    result.comparison.forEach(weapon => {
        const isBest = weapon.weapon === best.weapon;
        const rowClass = isBest ? 'best' : '';
        html += `
            <tr>
                <td class="${rowClass}">${weapon.weapon}${isBest ? ' ⭐' : ''}</td>
                <td>${weapon.expected_hits}</td>
                <td>${weapon.expected_wounds}</td>
                <td>${weapon.expected_unsaved}</td>
                <td class="${rowClass}">${weapon.expected_damage}</td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    resultsElement.innerHTML = html;
}

async function simulateCombat() {
    const attackerCount = parseInt(document.getElementById('simAttackerCount').value);
    const defenderCount = parseInt(document.getElementById('simDefenderCount').value);
    const weaponName = document.getElementById('simWeaponSelect').value || null;

    if (!state.simAttacker || !state.simDefender) {
        alert('Please select both units');
        return;
    }

    try {
        const response = await fetch('/api/simulate/combat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                attacker_id: state.simAttacker.id,
                defender_id: state.simDefender.id,
                attacker_count: attackerCount,
                defender_count: defenderCount,
                weapon_name: weaponName
            })
        });

        const result = await response.json();
        displaySimulationResults(result);
    } catch (error) {
        console.error('Simulation error:', error);
        alert('Simulation failed');
    }
}

function displaySimulationResults(result) {
    const resultsElement = document.getElementById('simulateResults');

    const html = `
        <h3>Combat Simulation Results</h3>
        <div class="combat-summary">
            <h4>${result.attacker} vs ${result.defender}</h4>
            <div class="combat-detail">
                <span>Weapon Used:</span>
                <span style="color: var(--accent-color);">${result.weapon}</span>
            </div>
            <div class="combat-detail">
                <span>Total Attacks:</span>
                <span style="color: var(--accent-color);">${result.num_attacks}</span>
            </div>
            <div class="combat-detail">
                <span>Expected Hits:</span>
                <span>${result.expected_hits}</span>
            </div>
            <div class="combat-detail">
                <span>Expected Wounds:</span>
                <span>${result.expected_wounds}</span>
            </div>
            <div class="combat-detail">
                <span>Total Damage:</span>
                <span>${result.expected_damage}</span>
            </div>
        </div>
        <div class="result-grid" style="margin-top: 20px;">
            <div class="result-card">
                <div class="result-label">Models Killed</div>
                <div class="result-value">${result.models_killed}</div>
            </div>
            <div class="result-card">
                <div class="result-label">Defenders Remaining</div>
                <div class="result-value">${result.defender_remaining}</div>
            </div>
        </div>
    `;

    resultsElement.innerHTML = html;
}

/**
 * Battle Mode - Army vs Army Combat
 * Handles loading two armies and calculating unit-vs-unit combat
 */

// Global state
let army1 = null;
let army2 = null;
let selectedCombatType = 'ranged';
let selectedAttackerUnit = null;
let selectedDefenderUnit = null;
let selectedWeapon = null;
let loadingFor = null; // 'army1' or 'army2'

// Comparison mode
let comparisonMode = false;
let selectedWeapons = []; // For comparison mode

// CP Tracking
let cpTotal = 10;
let cpRemaining = 10;
let spentStratagems = {}; // { stratagemId: { name, cost } }

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    updateCPDisplay();
});

function setupEventListeners() {
    // Dataset autoload
    document.getElementById('autoload-datasets-btn').addEventListener('click', autoloadDatasets);

    // Army loading
    document.getElementById('load-army-1-btn').addEventListener('click', () => {
        loadingFor = 'army1';
        showLoadArmyModal();
    });

    document.getElementById('load-army-2-btn').addEventListener('click', () => {
        loadingFor = 'army2';
        showLoadArmyModal();
    });

    // Modal
    document.getElementById('cancel-load-modal-btn').addEventListener('click', () => {
        hideModal('load-army-modal');
    });

    // Combat type buttons
    document.querySelectorAll('.combat-type-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.combat-type-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedCombatType = btn.dataset.type;

            // Load stratagems for this phase
            loadStratagemsForPhase();

            // Reset weapon selection when combat type changes
            selectedWeapon = null;
            if (selectedAttackerUnit) {
                loadWeaponsForUnit();
            }
        });
    });

    // Unit selection
    document.getElementById('attacker-unit-select').addEventListener('change', (e) => {
        const unitIndex = parseInt(e.target.value);
        if (!isNaN(unitIndex) && army1) {
            selectedAttackerUnit = army1.units[unitIndex];
            displayUnitDetails('attacker', selectedAttackerUnit);
            loadWeaponsForUnit();
        }
    });

    document.getElementById('defender-unit-select').addEventListener('change', (e) => {
        const unitIndex = parseInt(e.target.value);
        if (!isNaN(unitIndex) && army2) {
            selectedDefenderUnit = army2.units[unitIndex];
            displayUnitDetails('defender', selectedDefenderUnit);
            checkReadyForCalculation();
        }
    });

    // Calculate button
    document.getElementById('calculate-btn').addEventListener('click', () => {
        calculateCombat();
    });

    // CP reset button
    document.getElementById('cp-reset-btn').addEventListener('click', () => {
        resetCP();
    });
}

async function showLoadArmyModal() {
    showModal('load-army-modal');

    const listDiv = document.getElementById('army-list-modal');
    listDiv.innerHTML = '<p>Loading...</p>';

    try {
        const response = await fetch('/api/army/list');
        const data = await response.json();

        if (data.success) {
            if (data.armies.length === 0) {
                listDiv.innerHTML = '<p class="placeholder">No saved armies found. Create one in Army Builder first.</p>';
                return;
            }

            listDiv.innerHTML = '';

            data.armies.forEach(armyInfo => {
                const card = createArmySelectionCard(armyInfo);
                listDiv.appendChild(card);
            });
        } else {
            listDiv.innerHTML = '<p class="placeholder">Error loading armies</p>';
        }
    } catch (error) {
        console.error('Error loading army list:', error);
        listDiv.innerHTML = '<p class="placeholder">Failed to load armies</p>';
    }
}

function createArmySelectionCard(armyInfo) {
    const card = document.createElement('div');
    card.className = 'saved-army-card';

    const name = document.createElement('div');
    name.className = 'saved-army-name';
    name.textContent = armyInfo.name;

    const meta = document.createElement('div');
    meta.className = 'saved-army-meta';
    meta.innerHTML = `
        ${armyInfo.faction}<br>
        ${armyInfo.points}/${armyInfo.points_limit} pts<br>
        <small>${new Date(armyInfo.modified_at).toLocaleString()}</small>
    `;

    card.appendChild(name);
    card.appendChild(meta);

    card.addEventListener('click', () => loadArmyForBattle(armyInfo.filename));

    return card;
}

async function loadArmyForBattle(filename) {
    try {
        const response = await fetch(`/api/battle/load-army-for-battle/${filename}`);
        const data = await response.json();

        if (data.success) {
            const army = data.army;

            if (loadingFor === 'army1') {
                army1 = army;
                displayArmyInfo(1, army);
                populateUnitSelect('attacker', army);
            } else {
                army2 = army;
                displayArmyInfo(2, army);
                populateUnitSelect('defender', army);
            }

            hideModal('load-army-modal');
            showToast(`Loaded ${army.name}`, 'success');

            // Show battle config if both armies loaded
            if (army1 && army2) {
                document.getElementById('battle-config').style.display = 'block';
            }
        } else {
            showToast('Error loading army: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error loading army:', error);
        showToast('Failed to load army', 'error');
    }
}

function displayArmyInfo(armyNumber, army) {
    const infoDiv = document.getElementById(`army-${armyNumber}-info`);
    infoDiv.classList.add('loaded');

    infoDiv.innerHTML = `
        <div class="army-name">${army.name}</div>
        <div class="army-details">
            <strong>Faction:</strong> ${army.faction}<br>
            <strong>Detachment:</strong> ${army.detachment}<br>
            <strong>Points:</strong> ${army.units.reduce((sum, u) => sum + (u.points_cost || 0), 0)}/${army.points_limit}
        </div>
        <div class="army-units-count">
            ${army.units.length} units
        </div>
    `;
}

function populateUnitSelect(role, army) {
    const selectId = role === 'attacker' ? 'attacker-unit-select' : 'defender-unit-select';
    const select = document.getElementById(selectId);

    select.innerHTML = `<option value="">Select ${role} unit...</option>`;

    army.units.forEach((unit, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = `${unit.unit_name} (${unit.points_cost} pts)`;
        select.appendChild(option);
    });
}

async function displayUnitDetails(role, unit) {
    const detailsDiv = document.getElementById(`${role}-unit-details`);
    detailsDiv.classList.add('loaded');

    // Fetch full unit data from catalog
    try {
        const response = await fetch(`/api/unit/${unit.unit_id}`);
        const data = await response.json();

        if (data.success) {
            const fullUnit = data.unit;

            // Build abilities HTML
            let abilitiesHTML = '';
            if (fullUnit.profile && fullUnit.profile.abilities && fullUnit.profile.abilities.length > 0) {
                abilitiesHTML = `
                    <div class="unit-abilities">
                        <div class="unit-abilities-title">Unit Abilities</div>
                        ${fullUnit.profile.abilities.map(ability => `
                            <div class="ability-item">
                                <div class="ability-item-name">${ability.name}</div>
                                ${ability.description ? `<div class="ability-item-description">${ability.description}</div>` : ''}
                            </div>
                        `).join('')}
                    </div>
                `;
            }

            detailsDiv.innerHTML = `
                <div class="unit-detail-name">${unit.unit_name}</div>
                <div class="unit-stat-grid">
                    <div class="unit-stat">
                        <span class="unit-stat-label">M</span>
                        <span class="unit-stat-value">${fullUnit.movement || '-'}</span>
                    </div>
                    <div class="unit-stat">
                        <span class="unit-stat-label">T</span>
                        <span class="unit-stat-value">${fullUnit.toughness || '-'}</span>
                    </div>
                    <div class="unit-stat">
                        <span class="unit-stat-label">Sv</span>
                        <span class="unit-stat-value">${fullUnit.save || '-'}</span>
                    </div>
                    <div class="unit-stat">
                        <span class="unit-stat-label">W</span>
                        <span class="unit-stat-value">${fullUnit.wounds || '-'}</span>
                    </div>
                    <div class="unit-stat">
                        <span class="unit-stat-label">Ld</span>
                        <span class="unit-stat-value">${fullUnit.leadership || '-'}</span>
                    </div>
                    <div class="unit-stat">
                        <span class="unit-stat-label">OC</span>
                        <span class="unit-stat-value">${fullUnit.oc || '-'}</span>
                    </div>
                </div>
                ${abilitiesHTML}
            `;

            // Store full unit data
            if (role === 'attacker') {
                selectedAttackerUnit.fullData = fullUnit;
            } else {
                selectedDefenderUnit.fullData = fullUnit;
            }
        }
    } catch (error) {
        console.error('Error loading unit details:', error);
    }
}

async function loadWeaponsForUnit() {
    if (!selectedAttackerUnit || !selectedAttackerUnit.fullData) {
        return;
    }

    const weaponSection = document.getElementById('weapon-selection');
    weaponSection.style.display = 'block';

    const weaponList = document.getElementById('weapon-list');
    weaponList.innerHTML = '<p>Loading weapons...</p>';

    try {
        const fullUnit = selectedAttackerUnit.fullData;

        // Prepare weapons data
        const weapons = fullUnit.weapons.map(w => ({
            name: w.name,
            type: w.type,
            attacks: w.attacks,
            skill: w.skill,
            strength: w.strength,
            ap: w.ap,
            damage: w.damage,
            keywords: w.keywords || ''
        }));

        // Filter weapons based on combat type
        const response = await fetch('/api/battle/get-available-weapons', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                weapons: weapons,
                combat_type: selectedCombatType,
                categories: fullUnit.categories || []
            })
        });

        const data = await response.json();

        if (data.success) {
            const availableWeapons = data.weapons;

            if (availableWeapons.length === 0) {
                weaponList.innerHTML = '<p class="placeholder">No weapons available for this combat type</p>';
                return;
            }

            // Show note if Monster/Vehicle
            if (data.note) {
                const note = document.createElement('div');
                note.className = 'alert alert-info';
                note.textContent = data.note;
                weaponList.innerHTML = '';
                weaponList.appendChild(note);
            } else {
                weaponList.innerHTML = '';
            }

            availableWeapons.forEach(weapon => {
                const card = createWeaponCard(weapon);
                weaponList.appendChild(card);
            });
        }
    } catch (error) {
        console.error('Error loading weapons:', error);
        showToast('Failed to load weapons', 'error');
    }
}

function createWeaponCard(weapon) {
    const card = document.createElement('div');
    card.className = 'weapon-battle-card';

    const keywords = weapon.keywords ? weapon.keywords.split(',').map(k => k.trim()).filter(k => k) : [];

    card.innerHTML = `
        <div class="weapon-battle-name">${weapon.name}</div>
        <div class="weapon-battle-type">${weapon.type}</div>
        <div class="weapon-stats-row">
            <div class="weapon-stat-item">
                <strong>${weapon.attacks || '-'}</strong>
                <small>A</small>
            </div>
            <div class="weapon-stat-item">
                <strong>${weapon.skill || '-'}</strong>
                <small>BS/WS</small>
            </div>
            <div class="weapon-stat-item">
                <strong>${weapon.strength || '-'}</strong>
                <small>S</small>
            </div>
            <div class="weapon-stat-item">
                <strong>${weapon.ap || '-'}</strong>
                <small>AP</small>
            </div>
            <div class="weapon-stat-item">
                <strong>${weapon.damage || '-'}</strong>
                <small>D</small>
            </div>
        </div>
        ${keywords.length > 0 ? `
            <div class="weapon-keywords">
                ${keywords.map(k => `<span class="keyword-badge">${k}</span>`).join('')}
            </div>
        ` : ''}
    `;

    card.addEventListener('click', () => {
        if (comparisonMode) {
            // Multi-select mode
            const index = selectedWeapons.findIndex(w => w.name === weapon.name);
            if (index > -1) {
                selectedWeapons.splice(index, 1);
                card.classList.remove('selected');
            } else {
                if (selectedWeapons.length < 5) { // Limit to 5 weapons
                    selectedWeapons.push(weapon);
                    card.classList.add('selected');
                } else {
                    showToast('Maximum 5 weapons for comparison', 'warning');
                }
            }
            checkReadyForCalculation();
        } else {
            // Single select mode
            document.querySelectorAll('.weapon-battle-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            selectedWeapon = weapon;
            selectedWeapons = [weapon]; // Keep selectedWeapons in sync
            checkReadyForCalculation();
        }
    });

    return card;
}

function checkReadyForCalculation() {
    const calculateSection = document.getElementById('calculate-section');
    const calculateBtn = document.getElementById('calculate-btn');

    const ready = selectedAttackerUnit && selectedDefenderUnit &&
                  (comparisonMode ? selectedWeapons.length > 0 : selectedWeapon);

    if (ready) {
        calculateSection.style.display = 'block';
        if (comparisonMode && selectedWeapons.length > 1) {
            calculateBtn.innerHTML = `<i class="fas fa-balance-scale"></i> Compare ${selectedWeapons.length} Weapons`;
        } else {
            calculateBtn.innerHTML = `⚔️ Calculate Combat`;
        }
    } else {
        calculateSection.style.display = 'none';
    }
}

async function calculateCombat() {
    if (!selectedAttackerUnit || !selectedDefenderUnit || selectedWeapons.length === 0) {
        showToast('Please select attacker, defender, and weapon(s)', 'warning');
        return;
    }

    // If in comparison mode with multiple weapons, run comparison
    if (comparisonMode && selectedWeapons.length > 1) {
        await runWeaponComparison();
        return;
    }

    try {
        showToast('Calculating combat...', 'info');

        // Get simulation parameters
        const numSimulations = parseInt(document.getElementById('num-simulations').value) || 1;
        const defenderUnitSize = parseInt(document.getElementById('defender-unit-size').value) || 10;

        const response = await fetch('/api/battle/calculate-combat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                attacker_unit: {
                    name: selectedAttackerUnit.unit_name,
                    id: selectedAttackerUnit.unit_id
                },
                attacker_weapon: selectedWeapon,
                defender_unit: {
                    name: selectedDefenderUnit.unit_name,
                    id: selectedDefenderUnit.unit_id,
                    toughness: parseInt(selectedDefenderUnit.fullData.toughness),
                    save: parseInt(selectedDefenderUnit.fullData.save.replace('+', '')),
                    invuln: selectedDefenderUnit.fullData.invuln ? parseInt(selectedDefenderUnit.fullData.invuln.replace('+', '')) : null,
                    wounds: parseInt(selectedDefenderUnit.fullData.wounds),
                    unit_size: defenderUnitSize,
                    keywords: selectedDefenderUnit.fullData.categories || []
                },
                combat_type: selectedCombatType,
                active_stratagems: activeStratagems,  // Include active stratagems
                num_simulations: numSimulations  // Include simulation iterations
            })
        });

        const data = await response.json();

        if (data.success) {
            displayResults(data);
            showToast('Combat calculated!', 'success');
        } else {
            showToast('Error: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error calculating combat:', error);
        showToast('Failed to calculate combat', 'error');
    }
}

function displayResults(data) {
    const resultsSection = document.getElementById('battle-results');
    const resultsContent = document.getElementById('results-content');

    const result = data.result;
    const summary = data.summary;
    const stats = data.stats;
    const numSims = data.num_simulations || 1;

    // Format numbers (round if averages)
    const fmt = (val) => numSims > 1 ? val.toFixed(1) : Math.round(val);

    resultsContent.innerHTML = `
        <div class="results-summary">
            <div class="results-title">Combat Results${numSims > 1 ? ` (${numSims} iterations)` : ''}</div>
            <div class="results-matchup">
                ${summary.attacker} vs ${summary.defender}
            </div>
            <div class="results-grid">
                <div class="result-stat">
                    <span class="result-stat-value">${result.num_attacks}</span>
                    <span class="result-stat-label">Attacks</span>
                </div>
                <div class="result-stat">
                    <span class="result-stat-value">${fmt(result.num_hits)}</span>
                    <span class="result-stat-label">Hits</span>
                </div>
                <div class="result-stat">
                    <span class="result-stat-value">${fmt(result.num_wounds)}</span>
                    <span class="result-stat-label">Wounds</span>
                </div>
                <div class="result-stat">
                    <span class="result-stat-value">${fmt(result.num_saves_failed)}</span>
                    <span class="result-stat-label">Failed Saves</span>
                </div>
                <div class="result-stat">
                    <span class="result-stat-value">${fmt(result.total_damage)}</span>
                    <span class="result-stat-label">Total Damage</span>
                </div>
                <div class="result-stat">
                    <span class="result-stat-value">${fmt(summary.models_killed)}</span>
                    <span class="result-stat-label">Models Killed</span>
                </div>
            </div>
        </div>

        <div class="results-detailed">
            <div class="result-breakdown">
                <h4>Attack Sequence</h4>
                <div class="result-item">
                    <span>Total Attacks:</span>
                    <span>${result.num_attacks}</span>
                </div>
                <div class="result-item">
                    <span>Successful Hits:</span>
                    <span>${fmt(result.num_hits)} (${fmt(result.num_critical_hits)} critical)</span>
                </div>
                <div class="result-item">
                    <span>Successful Wounds:</span>
                    <span>${fmt(result.num_wounds)} (${fmt(result.num_critical_wounds)} critical)</span>
                </div>
                <div class="result-item">
                    <span>Saves Made:</span>
                    <span>${fmt(result.num_saves_made)}</span>
                </div>
                <div class="result-item">
                    <span>Saves Failed:</span>
                    <span>${fmt(result.num_saves_failed)}</span>
                </div>
                <div class="result-item">
                    <span>Damage Dealt:</span>
                    <span>${fmt(result.total_damage)}</span>
                </div>
                ${result.damage_after_fnp !== result.total_damage ? `
                <div class="result-item">
                    <span>After Feel No Pain:</span>
                    <span>${fmt(result.damage_after_fnp)}</span>
                </div>
                ` : ''}
                ${result.mortal_wounds && result.mortal_wounds > 0 ? `
                <div class="result-item" style="border-left: 3px solid #e94560;">
                    <span>💀 Mortal Wounds:</span>
                    <span style="color: #e94560; font-weight: bold;">${result.mortal_wounds}</span>
                </div>
                ` : ''}
            </div>

            <div class="result-breakdown">
                <h4>Final Impact</h4>
                <div class="result-item">
                    <span>Models Destroyed:</span>
                    <span><strong>${fmt(summary.models_killed)}</strong></span>
                </div>
                <div class="result-item">
                    <span>Wounds Inflicted:</span>
                    <span><strong>${fmt(summary.wounds_dealt)}</strong></span>
                </div>
                ${summary.mortal_wounds && summary.mortal_wounds > 0 ? `
                <div class="result-item">
                    <span>From Mortal Wounds:</span>
                    <span style="color: #e94560;"><strong>${summary.mortal_wounds}</strong></span>
                </div>
                ` : ''}
            </div>

            <div class="result-breakdown">
                <h4 style="color: #4CAF50;">⚡ Efficiency Metrics</h4>
                <div class="efficiency-metrics">
                    <div class="efficiency-metric">
                        <span class="efficiency-metric-value">${((result.num_hits / result.num_attacks) * 100).toFixed(1)}%</span>
                        <span class="efficiency-metric-label">Hit Rate</span>
                    </div>
                    <div class="efficiency-metric">
                        <span class="efficiency-metric-value">${result.num_hits > 0 ? ((result.num_wounds / result.num_hits) * 100).toFixed(1) : 0}%</span>
                        <span class="efficiency-metric-label">Wound Rate</span>
                    </div>
                    <div class="efficiency-metric">
                        <span class="efficiency-metric-value">${result.num_wounds > 0 ? ((result.num_saves_failed / result.num_wounds) * 100).toFixed(1) : 0}%</span>
                        <span class="efficiency-metric-label">Save Failure Rate</span>
                    </div>
                    <div class="efficiency-metric">
                        <span class="efficiency-metric-value">${(summary.wounds_dealt / result.num_attacks).toFixed(2)}</span>
                        <span class="efficiency-metric-label">Damage Per Attack</span>
                    </div>
                </div>
            </div>

            ${stats ? `
            <div class="result-breakdown">
                <h4 style="color: #d4af37;">📊 Statistics (${numSims} rolls)</h4>
                <div class="result-item">
                    <span>Damage Range:</span>
                    <span>${stats.min_damage} - ${stats.max_damage} (avg: ${stats.avg_damage.toFixed(1)})</span>
                </div>
                <div class="result-item">
                    <span>Models Killed Range:</span>
                    <span>${stats.min_models_killed} - ${stats.max_models_killed} (avg: ${stats.avg_models_killed.toFixed(1)})</span>
                </div>
            </div>

            ${stats.damage_distribution && stats.damage_distribution.length > 0 && numSims >= 100 ? `
            <div class="result-breakdown">
                <h4 style="color: #d4af37;">📈 Damage Probability Distribution</h4>
                <div class="distribution-chart">
                    ${stats.damage_distribution.map(([damage, percent]) => `
                        <div class="distribution-row">
                            <span class="distribution-label">${damage} dmg</span>
                            <div class="distribution-bar-container">
                                <div class="distribution-bar" style="width: ${percent}%"></div>
                                <span class="distribution-percent">${percent.toFixed(1)}%</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>

            <div class="result-breakdown">
                <h4 style="color: #d4af37;">🎯 Models Killed Probability</h4>
                <div class="distribution-chart">
                    ${stats.models_distribution.map(([models, percent]) => `
                        <div class="distribution-row">
                            <span class="distribution-label">${models} models</span>
                            <div class="distribution-bar-container">
                                <div class="distribution-bar models-bar" style="width: ${percent}%"></div>
                                <span class="distribution-percent">${percent.toFixed(1)}%</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            ` : ''}
            ` : ''}

            ${data.stratagems_applied && data.stratagems_applied.length > 0 ? `
            <div class="result-breakdown">
                <h4 style="color: #e94560;">⚡ Active Stratagems</h4>
                ${data.stratagems_applied.map(strat => `
                    <div class="result-item">
                        <span>✓ ${strat}</span>
                        <span style="color: #e94560;">Applied</span>
                    </div>
                `).join('')}
            </div>
            ` : ''}
        </div>
    `;

    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

async function runWeaponComparison() {
    showToast(`Comparing ${selectedWeapons.length} weapons...`, 'info');

    const numSimulations = parseInt(document.getElementById('num-simulations').value) || 1;
    const defenderUnitSize = parseInt(document.getElementById('defender-unit-size').value) || 10;

    try {
        // Run combat for each weapon
        const results = await Promise.all(selectedWeapons.map(async (weapon) => {
            const response = await fetch('/api/battle/calculate-combat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    attacker_unit: {
                        name: selectedAttackerUnit.unit_name,
                        id: selectedAttackerUnit.unit_id
                    },
                    attacker_weapon: weapon,
                    defender_unit: {
                        name: selectedDefenderUnit.unit_name,
                        id: selectedDefenderUnit.unit_id,
                        toughness: parseInt(selectedDefenderUnit.fullData.toughness),
                        save: parseInt(selectedDefenderUnit.fullData.save.replace('+', '')),
                        invuln: selectedDefenderUnit.fullData.invuln ? parseInt(selectedDefenderUnit.fullData.invuln.replace('+', '')) : null,
                        wounds: parseInt(selectedDefenderUnit.fullData.wounds),
                        unit_size: defenderUnitSize,
                        keywords: selectedDefenderUnit.fullData.categories || []
                    },
                    combat_type: selectedCombatType,
                    active_stratagems: activeStratagems,
                    num_simulations: numSimulations
                })
            });

            const data = await response.json();
            return {
                weapon: weapon,
                data: data
            };
        }));

        displayComparisonResults(results, numSimulations);
        showToast('Comparison complete!', 'success');
    } catch (error) {
        console.error('Error running comparison:', error);
        showToast('Failed to compare weapons', 'error');
    }
}

function displayComparisonResults(results, numSims) {
    const resultsSection = document.getElementById('battle-results');
    const resultsContent = document.getElementById('results-content');

    const fmt = (val) => numSims > 1 ? val.toFixed(1) : Math.round(val);

    // Sort by models killed (descending)
    const sortedResults = [...results].sort((a, b) =>
        b.data.summary.models_killed - a.data.summary.models_killed
    );

    resultsContent.innerHTML = `
        <div class="results-summary">
            <div class="results-title">
                <i class="fas fa-balance-scale"></i> Weapon Comparison${numSims > 1 ? ` (${numSims} iterations)` : ''}
            </div>
            <div class="results-matchup">
                ${results[0].data.summary.attacker.split(' with ')[0]} vs ${results[0].data.summary.defender}
            </div>
        </div>

        <div class="comparison-table">
            <table class="results-table">
                <thead>
                    <tr>
                        <th>Weapon</th>
                        <th>Attacks</th>
                        <th>Hits</th>
                        <th>Wounds</th>
                        <th>Damage</th>
                        <th class="highlight">Models Killed</th>
                        <th>Efficiency</th>
                    </tr>
                </thead>
                <tbody>
                    ${sortedResults.map((r, idx) => {
                        const efficiency = r.data.summary.wounds_dealt / r.data.result.num_attacks;
                        return `
                        <tr class="${idx === 0 ? 'best-result' : ''}">
                            <td class="weapon-name">
                                ${idx === 0 ? '<i class="fas fa-trophy" style="color: #d4af37; margin-right: 5px;"></i>' : ''}
                                ${r.weapon.name}
                            </td>
                            <td>${r.data.result.num_attacks}</td>
                            <td>${fmt(r.data.result.num_hits)}</td>
                            <td>${fmt(r.data.result.num_wounds)}</td>
                            <td>${fmt(r.data.summary.wounds_dealt)}</td>
                            <td class="highlight"><strong>${fmt(r.data.summary.models_killed)}</strong></td>
                            <td><strong>${efficiency.toFixed(2)}</strong> dmg/atk</td>
                        </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        </div>

        ${numSims > 1 && sortedResults[0].data.stats ? `
        <div class="comparison-stats">
            <h4 style="color: #d4af37;">📊 Best Weapon Statistics</h4>
            <div class="result-breakdown">
                <div class="result-item">
                    <span>Best: ${sortedResults[0].weapon.name}</span>
                    <span>${fmt(sortedResults[0].data.summary.models_killed)} models killed avg</span>
                </div>
                <div class="result-item">
                    <span>Damage Range:</span>
                    <span>${sortedResults[0].data.stats.min_damage} - ${sortedResults[0].data.stats.max_damage}</span>
                </div>
            </div>
        </div>
        ` : ''}
    `;

    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Utility functions
function showModal(modalId) {
    document.getElementById(modalId).classList.add('show');
}

function hideModal(modalId) {
    document.getElementById(modalId).classList.remove('show');
}

// Stratagem Management
let activeStratagems = [];

async function loadStratagemsForPhase() {
    const stratagemsList = document.getElementById('stratagems-list');

    // Map combat types to phases
    const phaseMap = {
        'ranged': 'shooting',
        'melee': 'fight',
        'ranged_engaged': 'opponent_shooting'
    };

    const phase = phaseMap[selectedCombatType];
    if (!phase) return;

    try {
        const response = await fetch(`/api/stratagems/phase/${phase}`);
        const data = await response.json();

        if (data.stratagems && data.stratagems.length > 0) {
            stratagemsList.innerHTML = data.stratagems.map(strat => `
                <div class="stratagem-item" data-id="${strat.id}" onclick="toggleStratagem('${strat.id}')">
                    <div class="stratagem-header">
                        <span class="stratagem-name">${strat.name}</span>
                        <span class="stratagem-cp">${strat.cp_cost} CP</span>
                    </div>
                    <div class="stratagem-description">${strat.description.substring(0, 100)}...</div>
                </div>
            `).join('');
        } else {
            stratagemsList.innerHTML = '<p style="color: #888;">No stratagems available for this phase</p>';
        }
    } catch (error) {
        console.error('Error loading stratagems:', error);
        stratagemsList.innerHTML = '<p style="color: #e94560;">Error loading stratagems</p>';
    }
}

async function toggleStratagem(stratagemId) {
    const index = activeStratagems.indexOf(stratagemId);
    const element = document.querySelector(`[data-id="${stratagemId}"]`);

    if (index > -1) {
        // Deactivate stratagem - refund CP
        const stratData = spentStratagems[stratagemId];
        if (stratData) {
            cpRemaining += stratData.cost;
            delete spentStratagems[stratagemId];
        }
        activeStratagems.splice(index, 1);
        element.classList.remove('active');
        showToast(`Deactivated: ${stratData ? stratData.name : stratagemId}`, 'info');
    } else {
        // Activate stratagem - spend CP
        // Fetch stratagem details to get cost
        try {
            const response = await fetch(`/api/stratagems/${stratagemId}`);
            const stratData = await response.json();

            if (cpRemaining >= stratData.cp_cost) {
                cpRemaining -= stratData.cp_cost;
                spentStratagems[stratagemId] = {
                    name: stratData.name,
                    cost: stratData.cp_cost
                };
                activeStratagems.push(stratagemId);
                element.classList.add('active');
                showToast(`Activated: ${stratData.name} (-${stratData.cp_cost} CP)`, 'success');
            } else {
                showToast(`Not enough CP! Need ${stratData.cp_cost} CP, have ${cpRemaining} CP`, 'error');
                return;
            }
        } catch (error) {
            console.error('Error fetching stratagem:', error);
            showToast('Error activating stratagem', 'error');
            return;
        }
    }

    updateCPDisplay();
    console.log('Active stratagems:', activeStratagems);
    console.log('CP remaining:', cpRemaining);
}

// CP Management Functions
function updateCPDisplay() {
    const cpRemainingEl = document.getElementById('cp-remaining');
    const cpTotalEl = document.getElementById('cp-total');
    const cpSpentInfo = document.getElementById('cp-spent-info');

    // Update counter
    cpRemainingEl.textContent = cpRemaining;
    cpTotalEl.textContent = cpTotal;

    // Update color based on remaining CP
    cpRemainingEl.classList.remove('low', 'critical');
    if (cpRemaining <= 2) {
        cpRemainingEl.classList.add('critical');
    } else if (cpRemaining <= 5) {
        cpRemainingEl.classList.add('low');
    }

    // Update spent stratagems list
    const spentStratagemIds = Object.keys(spentStratagems);
    if (spentStratagemIds.length > 0) {
        cpSpentInfo.classList.add('has-spent');
        cpSpentInfo.innerHTML = spentStratagemIds.map(id => {
            const strat = spentStratagems[id];
            return `
                <div class="cp-spent-item">
                    <span class="cp-spent-name">${strat.name}</span>
                    <span class="cp-spent-cost">-${strat.cost} CP</span>
                </div>
            `;
        }).join('');
    } else {
        cpSpentInfo.classList.remove('has-spent');
        cpSpentInfo.innerHTML = '';
    }
}

function resetCP() {
    // Refund all CP
    cpRemaining = cpTotal;
    spentStratagems = {};

    // Clear active stratagems
    activeStratagems.forEach(id => {
        const element = document.querySelector(`[data-id="${id}"]`);
        if (element) {
            element.classList.remove('active');
        }
    });
    activeStratagems = [];

    updateCPDisplay();
    showToast('Command Points reset to ' + cpTotal, 'success');
}

function toggleComparisonMode() {
    comparisonMode = !comparisonMode;
    const btn = document.getElementById('comparison-mode-btn');

    if (comparisonMode) {
        btn.innerHTML = '<i class="fas fa-check-square"></i> Disable Comparison Mode';
        btn.classList.remove('btn-secondary');
        btn.classList.add('btn-primary');
        selectedWeapons = selectedWeapon ? [selectedWeapon] : [];
        showToast('Comparison mode enabled - select multiple weapons', 'info');
    } else {
        btn.innerHTML = '<i class="fas fa-balance-scale"></i> Enable Comparison Mode';
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-secondary');
        // Keep only the first weapon selected
        selectedWeapon = selectedWeapons.length > 0 ? selectedWeapons[0] : null;
        selectedWeapons = selectedWeapon ? [selectedWeapon] : [];
        // Update visual selection
        document.querySelectorAll('.weapon-battle-card').forEach(c => c.classList.remove('selected'));
        if (selectedWeapon) {
            const cards = Array.from(document.querySelectorAll('.weapon-battle-card'));
            const selectedCard = cards.find(card => card.textContent.includes(selectedWeapon.name));
            if (selectedCard) selectedCard.classList.add('selected');
        }
        showToast('Comparison mode disabled', 'info');
    }

    checkReadyForCalculation();
}

async function autoloadDatasets() {
    const btn = document.getElementById('autoload-datasets-btn');
    const status = document.getElementById('dataset-status');

    try {
        // Disable button and show loading
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading Datasets...';
        status.textContent = 'Loading datasets from GitHub...';
        status.style.color = 'var(--primary-color)';

        // Call the API endpoint
        const response = await fetch('/api/load-dataset', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            status.textContent = `✓ Datasets loaded successfully! Units: ${data.unit_count}, Weapons: ${data.weapon_count}`;
            status.style.color = 'var(--success-color)';
            showToast('Datasets loaded successfully!', 'success');
        } else {
            status.textContent = `✗ Error: ${data.error || 'Failed to load datasets'}`;
            status.style.color = 'var(--danger-color)';
            showToast('Failed to load datasets', 'error');
        }
    } catch (error) {
        console.error('Error autoloading datasets:', error);
        status.textContent = `✗ Error: ${error.message}`;
        status.style.color = 'var(--danger-color)';
        showToast('Error loading datasets', 'error');
    } finally {
        // Re-enable button
        btn.disabled = false;
        btn.innerHTML = '<i class="fab fa-github"></i> Autoload All Datasets';
    }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

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
        document.querySelectorAll('.weapon-battle-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        selectedWeapon = weapon;
        checkReadyForCalculation();
    });

    return card;
}

function checkReadyForCalculation() {
    const calculateSection = document.getElementById('calculate-section');

    if (selectedAttackerUnit && selectedDefenderUnit && selectedWeapon) {
        calculateSection.style.display = 'block';
    } else {
        calculateSection.style.display = 'none';
    }
}

async function calculateCombat() {
    if (!selectedAttackerUnit || !selectedDefenderUnit || !selectedWeapon) {
        showToast('Please select attacker, defender, and weapon', 'warning');
        return;
    }

    try {
        showToast('Calculating combat...', 'info');

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
                    unit_size: 10, // TODO: Get from unit composition
                    keywords: selectedDefenderUnit.fullData.categories || []
                },
                combat_type: selectedCombatType,
                active_stratagems: activeStratagems  // Include active stratagems
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

    resultsContent.innerHTML = `
        <div class="results-summary">
            <div class="results-title">Combat Results</div>
            <div class="results-matchup">
                ${summary.attacker} vs ${summary.defender}
            </div>
            <div class="results-grid">
                <div class="result-stat">
                    <span class="result-stat-value">${result.num_attacks}</span>
                    <span class="result-stat-label">Attacks</span>
                </div>
                <div class="result-stat">
                    <span class="result-stat-value">${result.num_hits}</span>
                    <span class="result-stat-label">Hits</span>
                </div>
                <div class="result-stat">
                    <span class="result-stat-value">${result.num_wounds}</span>
                    <span class="result-stat-label">Wounds</span>
                </div>
                <div class="result-stat">
                    <span class="result-stat-value">${result.num_saves_failed}</span>
                    <span class="result-stat-label">Failed Saves</span>
                </div>
                <div class="result-stat">
                    <span class="result-stat-value">${result.total_damage}</span>
                    <span class="result-stat-label">Total Damage</span>
                </div>
                <div class="result-stat">
                    <span class="result-stat-value">${result.models_destroyed}</span>
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
                    <span>${result.num_hits} (${result.num_critical_hits} critical)</span>
                </div>
                <div class="result-item">
                    <span>Successful Wounds:</span>
                    <span>${result.num_wounds} (${result.num_critical_wounds} critical)</span>
                </div>
                <div class="result-item">
                    <span>Saves Made:</span>
                    <span>${result.num_saves_made}</span>
                </div>
                <div class="result-item">
                    <span>Saves Failed:</span>
                    <span>${result.num_saves_failed}</span>
                </div>
                <div class="result-item">
                    <span>Damage Dealt:</span>
                    <span>${result.total_damage}</span>
                </div>
                ${result.damage_after_fnp !== result.total_damage ? `
                <div class="result-item">
                    <span>After Feel No Pain:</span>
                    <span>${result.damage_after_fnp}</span>
                </div>
                ` : ''}
            </div>

            <div class="result-breakdown">
                <h4>Final Impact</h4>
                <div class="result-item">
                    <span>Models Destroyed:</span>
                    <span><strong>${result.models_destroyed}</strong></span>
                </div>
                <div class="result-item">
                    <span>Wounds Inflicted:</span>
                    <span><strong>${result.damage_after_fnp}</strong></span>
                </div>
            </div>

            ${data.stratagems_applied && data.stratagems_applied.length > 0 ? `
            <div class="result-breakdown">
                <h4 style="color: #e94560;">Active Stratagems</h4>
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

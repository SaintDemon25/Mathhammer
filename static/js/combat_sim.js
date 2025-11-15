// Warhammer 40k Combat Simulator - Interactive JavaScript

let currentStep = 1;
const totalSteps = 4;

// ===== TOAST NOTIFICATION SYSTEM =====

function showToast(message, type = 'info', title = null, duration = 4000) {
    const container = document.getElementById('toast-container');
    if (!container) {
        // Create container if it doesn't exist
        const newContainer = document.createElement('div');
        newContainer.id = 'toast-container';
        newContainer.className = 'toast-container';
        document.body.appendChild(newContainer);
        return showToast(message, type, title, duration);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };

    const titles = {
        success: title || 'Success',
        error: title || 'Error',
        warning: title || 'Warning',
        info: title || 'Info'
    };

    toast.innerHTML = `
        <div class="toast-icon">
            <i class="fas ${icons[type]}"></i>
        </div>
        <div class="toast-content">
            <div class="toast-title">${titles[type]}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" onclick="closeToast(this)">
            <i class="fas fa-times"></i>
        </button>
    `;

    container.appendChild(toast);

    // Auto remove after duration
    if (duration > 0) {
        setTimeout(() => {
            closeToast(toast.querySelector('.toast-close'));
        }, duration);
    }

    return toast;
}

function closeToast(button) {
    const toast = button.closest('.toast');
    toast.classList.add('removing');
    setTimeout(() => {
        toast.remove();
    }, 300);
}

function showLoading(message = 'Loading...') {
    return showToast(message, 'info', 'Loading', 0);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    updateAttackTypeLabel();
    loadFactions(); // Load available factions
});

function initializeEventListeners() {
    // Attack type change
    document.getElementById('attack_type').addEventListener('change', updateAttackTypeLabel);

    // Step navigation via clicking step indicators
    document.querySelectorAll('.step').forEach(step => {
        step.addEventListener('click', () => {
            const stepNum = parseInt(step.dataset.step);
            if (stepNum <= currentStep || step.classList.contains('completed')) {
                goToStep(stepNum);
            }
        });
    });

    // Input validation
    addInputValidation();
}

function updateAttackTypeLabel() {
    const attackType = document.getElementById('attack_type').value;
    const label = document.getElementById('skill-label');
    label.textContent = attackType === 'ranged' ? 'Ballistic Skill (BS)' : 'Weapon Skill (WS)';
}

function addInputValidation() {
    // Add real-time validation feedback
    const inputs = document.querySelectorAll('input[type="number"]');
    inputs.forEach(input => {
        input.addEventListener('input', () => {
            validateInput(input);
        });
    });
}

// ===== UNIT LOADING FUNCTIONS =====

async function loadFactions() {
    try {
        // First, try to load units from dataset
        const loadResponse = await fetch('/api/load-units', {
            method: 'POST'
        });
        const loadResult = await loadResponse.json();

        if (!loadResult.success) {
            console.log('No units loaded yet:', loadResult.error);
            return;
        }

        // Get list of selectable units
        const response = await fetch('/api/units/selectable');
        const data = await response.json();

        if (data.units && data.units.length > 0) {
            // Extract unique factions
            const factions = [...new Set(data.units.map(u => u.faction))].sort();

            // Populate attacker faction dropdown
            const attackerFactionSelect = document.getElementById('attacker_faction');
            if (attackerFactionSelect) {
                factions.forEach(faction => {
                    const option = document.createElement('option');
                    option.value = faction;
                    option.textContent = faction;
                    attackerFactionSelect.appendChild(option);
                });

                // Add change listener
                attackerFactionSelect.addEventListener('change', () => {
                    populateUnitsForFaction('attacker', attackerFactionSelect.value);
                });
            }

            // Populate defender faction dropdown
            const defenderFactionSelect = document.getElementById('defender_faction');
            if (defenderFactionSelect) {
                factions.forEach(faction => {
                    const option = document.createElement('option');
                    option.value = faction;
                    option.textContent = faction;
                    defenderFactionSelect.appendChild(option);
                });

                // Add change listener
                defenderFactionSelect.addEventListener('change', () => {
                    populateUnitsForFaction('defender', defenderFactionSelect.value);
                });
            }

            console.log(`Loaded ${data.count} units from ${factions.length} factions`);
        }
    } catch (error) {
        console.error('Error loading factions:', error);
    }
}

async function populateUnitsForFaction(role, faction) {
    try {
        // Show the unit card section
        const unitCard = document.getElementById(`${role}-unit-card`);
        const unitsGrid = document.getElementById(`${role}-units-grid`);

        unitCard.style.display = 'block';
        unitsGrid.innerHTML = '<div class="section-loading"><div class="spinner large"></div><p>Loading units...</p></div>';

        const response = await fetch(`/api/units/selectable?faction=${encodeURIComponent(faction)}`);
        const data = await response.json();

        // Clear and populate with unit cards
        unitsGrid.innerHTML = '';

        if (data.units.length === 0) {
            unitsGrid.innerHTML = '<div class="no-weapons-message"><i class="fas fa-exclamation-circle"></i><p>No units found for this faction</p></div>';
            return;
        }

        data.units.forEach(unit => {
            const card = document.createElement('div');
            card.className = 'unit-card';
            card.dataset.unitId = unit.id;

            card.innerHTML = `
                <div class="unit-card-name">${unit.name}</div>
            `;

            card.onclick = () => selectUnit(role, unit.id, card);
            unitsGrid.appendChild(card);
        });

        // Scroll to units section
        unitCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    } catch (error) {
        console.error('Error loading units:', error);
        showToast('Failed to load units: ' + error.message, 'error');
    }
}

async function selectUnit(role, unitId, cardElement) {
    // Remove selected class from all unit cards
    document.querySelectorAll(`#${role}-units-grid .unit-card`).forEach(c => c.classList.remove('selected'));
    cardElement.classList.add('selected');

    if (role === 'attacker') {
        // Load weapons for this unit
        await populateWeaponsForUnit(unitId);
    } else if (role === 'defender') {
        // Auto-load defender stats
        await loadDefenderFromUnitId(unitId);
    }
}

async function populateWeaponsForUnit(unitId) {
    try {
        // Show the weapon card section
        const weaponCard = document.getElementById('attacker-weapon-card');
        const weaponsGrid = document.getElementById('attacker-weapons-grid');

        weaponCard.style.display = 'block';
        weaponsGrid.innerHTML = '<div class="section-loading"><div class="spinner large"></div><p>Loading weapons...</p></div>';

        const response = await fetch(`/api/unit/${unitId}`);
        const data = await response.json();

        // Clear and populate with weapon cards
        weaponsGrid.innerHTML = '';

        if (!data.weapons || data.weapons.length === 0) {
            weaponsGrid.innerHTML = '<div class="no-weapons-message"><i class="fas fa-crosshairs"></i><p>No weapons available for this unit</p></div>';
            return;
        }

        // Create a card for EACH weapon
        data.weapons.forEach((weapon, index) => {
            const card = document.createElement('div');
            card.className = 'weapon-card';
            card.dataset.weaponIndex = index;
            card.dataset.weaponData = JSON.stringify(weapon);

            // Build abilities HTML
            let abilitiesHTML = '';
            if (weapon.abilities && weapon.abilities.length > 0) {
                abilitiesHTML = '<div class="weapon-card-abilities">';
                weapon.abilities.forEach(ability => {
                    abilitiesHTML += `<span class="weapon-ability-badge">${ability}</span>`;
                });
                abilitiesHTML += '</div>';
            }

            card.innerHTML = `
                <div class="weapon-card-header">
                    <div class="weapon-card-name">${weapon.name}</div>
                    <div class="weapon-card-type">${weapon.type || 'Weapon'}</div>
                </div>
                <div class="weapon-card-stats">
                    <div class="weapon-stat">
                        <span class="weapon-stat-label">A</span>
                        <span class="weapon-stat-value">${weapon.attacks || '-'}</span>
                    </div>
                    <div class="weapon-stat">
                        <span class="weapon-stat-label">SK</span>
                        <span class="weapon-stat-value">${weapon.skill || '-'}</span>
                    </div>
                    <div class="weapon-stat">
                        <span class="weapon-stat-label">S</span>
                        <span class="weapon-stat-value">${weapon.strength || '-'}</span>
                    </div>
                    <div class="weapon-stat">
                        <span class="weapon-stat-label">AP</span>
                        <span class="weapon-stat-value">${weapon.ap || '0'}</span>
                    </div>
                    <div class="weapon-stat">
                        <span class="weapon-stat-label">D</span>
                        <span class="weapon-stat-value">${weapon.damage || '-'}</span>
                    </div>
                </div>
                ${abilitiesHTML}
            `;

            card.onclick = () => selectWeapon(card, weapon);
            weaponsGrid.appendChild(card);
        });

        // Auto-select first weapon
        if (data.weapons.length > 0) {
            const firstCard = weaponsGrid.querySelector('.weapon-card');
            selectWeapon(firstCard, data.weapons[0]);
        }

        // Scroll to weapons section
        weaponCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    } catch (error) {
        console.error('Error loading weapons:', error);
        showToast('Failed to load weapons: ' + error.message, 'error');
    }
}

function selectWeapon(cardElement, weaponData) {
    // Remove selected class from all weapon cards
    document.querySelectorAll('#attacker-weapons-grid .weapon-card').forEach(c => c.classList.remove('selected'));
    cardElement.classList.add('selected');

    // Auto-fill stats from weapon
    loadWeaponStats(weaponData);
}

function loadWeaponStats(weaponData) {
    try {
        // Auto-fill attacker fields
        document.getElementById('num_attacks').value = parseAttacks(weaponData.attacks) || 1;
        document.getElementById('skill').value = parseSkill(weaponData.skill) || 4;
        document.getElementById('strength').value = weaponData.strength || 4;
        document.getElementById('ap').value = Math.abs(weaponData.ap || 0);
        document.getElementById('damage').value = weaponData.damage || '1';

        // Set attack type based on weapon type
        const attackType = document.getElementById('attack_type');
        if (weaponData.type && weaponData.type.toLowerCase().includes('melee')) {
            attackType.value = 'melee';
        } else {
            attackType.value = 'ranged';
        }
        updateAttackTypeLabel();

        // Auto-fill weapon abilities if available
        if (weaponData.abilities && weaponData.abilities.length > 0) {
            applyWeaponAbilities(weaponData.abilities);
        }
    } catch (error) {
        console.error('Error loading weapon stats:', error);
        showToast('Error loading weapon stats: ' + error.message, 'error');
    }
}

async function loadDefenderFromUnitId(unitId) {
    try {
        // Get unit data
        const response = await fetch(`/api/unit/${unitId}`);
        const data = await response.json();

        if (data.profile) {
            // Auto-fill defender fields
            if (data.profile.toughness) {
                document.getElementById('toughness').value = data.profile.toughness;
            }
            if (data.profile.save) {
                document.getElementById('save').value = parseSkill(data.profile.save) || 3;
            }
            if (data.profile.wounds) {
                document.getElementById('wounds_per_model').value = data.profile.wounds;
            }
            if (data.profile.invuln) {
                document.getElementById('invuln').value = parseSkill(data.profile.invuln) || '';
            }

            // Apply defender abilities if available
            if (data.profile.abilities && data.profile.abilities.length > 0) {
                applyDefenderAbilities(data.profile.abilities);
            }
        }

    } catch (error) {
        console.error('Error loading defender from unit:', error);
        showToast('Error loading unit data: ' + error.message, 'error');
    }
}

// OLD FUNCTION - KEPT FOR BACKWARD COMPAT (not used anymore)
async function loadDefenderFromUnit() {
    const unitId = document.getElementById('defender_unit')?.value;
    if (unitId) {
        await loadDefenderFromUnitId(unitId);
    }
}

function parseAttacks(attacksStr) {
    // Parse attacks value (could be "2", "D6", "2D6", etc.)
    if (!attacksStr) return 1;

    // If it's a number, return it
    const num = parseInt(attacksStr);
    if (!isNaN(num)) return num;

    // If it's dice notation, return average value
    if (attacksStr.includes('D6')) {
        const multiplier = attacksStr.replace('D6', '') || '1';
        return Math.round(parseInt(multiplier) * 3.5); // Average of D6
    }
    if (attacksStr.includes('D3')) {
        const multiplier = attacksStr.replace('D3', '') || '1';
        return Math.round(parseInt(multiplier) * 2); // Average of D3
    }

    return 1; // Default
}

function parseSkill(skillStr) {
    // Parse skill value (e.g., "3+", "4+", "N/A")
    if (!skillStr || skillStr === 'N/A' || skillStr === '-') return null;

    // Extract number from "3+" format
    const match = skillStr.match(/(\d+)/);
    if (match) {
        return parseInt(match[1]);
    }

    return null;
}

function applyWeaponAbilities(abilities) {
    // Auto-check weapon ability checkboxes based on loaded abilities
    const abilityMap = {
        'Lethal Hits': 'lethal_hits',
        'Devastating Wounds': 'devastating_wounds',
        'Twin-linked': 'twin_linked',
        'Torrent': 'torrent',
        'Blast': 'blast',
        'Ignores Cover': 'ignores_cover',
        'Hazardous': 'hazardous',
        'Precision': 'precision',
        'Heavy': 'heavy',
        'Assault': 'assault'
    };

    // Reset all weapon abilities first
    Object.values(abilityMap).forEach(id => {
        const elem = document.getElementById(id);
        if (elem) elem.checked = false;
    });

    // Apply loaded abilities
    abilities.forEach(ability => {
        // Handle both string and object formats
        const abilityName = (typeof ability === 'string' ? ability : ability.name || '').trim();

        // Check for exact matches
        if (abilityMap[abilityName]) {
            const elem = document.getElementById(abilityMap[abilityName]);
            if (elem) elem.checked = true;
        }

        // Check for parameterized abilities (Anti-X, Melta X, etc.)
        if (abilityName.startsWith('Anti-')) {
            const elem = document.getElementById('anti');
            if (elem) elem.value = abilityName.replace('Anti-', '');
        } else if (abilityName.startsWith('Melta')) {
            const elem = document.getElementById('melta');
            if (elem) {
                const match = abilityName.match(/Melta\s+(\d+)/);
                if (match) elem.value = match[1];
            }
        } else if (abilityName.startsWith('Sustained Hits')) {
            const elem = document.getElementById('sustained_hits');
            if (elem) {
                const match = abilityName.match(/Sustained Hits\s+(\d+)/);
                if (match) elem.value = match[1];
                else elem.value = '1'; // Default to 1 if no number specified
            }
        } else if (abilityName.startsWith('Rapid Fire')) {
            const elem = document.getElementById('rapid_fire');
            if (elem) {
                const match = abilityName.match(/Rapid Fire\s+(\d+)/);
                if (match) elem.value = match[1];
            }
        }
    });

    // Abilities applied - visual feedback from checked boxes is enough
}

function applyDefenderAbilities(abilities) {
    // Auto-check defender ability checkboxes based on loaded abilities
    abilities.forEach(ability => {
        // Handle both string and object formats
        const abilityName = (typeof ability === 'string' ? ability : ability.name || '').trim();

        // Check for defender abilities
        if (abilityName === 'Stealth') {
            const elem = document.getElementById('stealth');
            if (elem) elem.checked = true;
        } else if (abilityName === 'Lone Operative') {
            const elem = document.getElementById('lone_operative');
            if (elem) elem.checked = true;
        } else if (abilityName.startsWith('Feel No Pain')) {
            const elem = document.getElementById('feel_no_pain');
            if (elem) {
                const match = abilityName.match(/Feel No Pain\s+(\d+)\+/);
                if (match) elem.value = match[1];
            }
        }
    });

    // Abilities applied - visual feedback from checked boxes is enough
}

function validateInput(input) {
    const value = parseInt(input.value);
    const min = parseInt(input.min);
    const max = parseInt(input.max);

    if (value < min || value > max || isNaN(value)) {
        input.style.borderColor = 'var(--danger-color)';
    } else {
        input.style.borderColor = 'var(--border-color)';
    }
}

function nextStep() {
    if (currentStep < totalSteps) {
        // Validate current step before proceeding
        if (validateCurrentStep()) {
            // Mark current step as completed
            document.querySelector(`.step[data-step="${currentStep}"]`).classList.add('completed');

            currentStep++;
            updateStepDisplay();
        }
    }
}

function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        updateStepDisplay();
    }
}

function goToStep(stepNum) {
    if (stepNum >= 1 && stepNum <= totalSteps) {
        currentStep = stepNum;
        updateStepDisplay();
    }
}

function updateStepDisplay() {
    // Update step indicators
    document.querySelectorAll('.step').forEach(step => {
        const stepNum = parseInt(step.dataset.step);
        step.classList.toggle('active', stepNum === currentStep);
    });

    // Update content panels
    document.querySelectorAll('.step-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`step-${currentStep}`).classList.add('active');

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function validateCurrentStep() {
    // Basic validation for each step
    switch (currentStep) {
        case 1:
            return validateAttackerConfig();
        case 2:
            return validateDefenderConfig();
        case 3:
            return true; // Abilities are optional
        case 4:
            return true;
        default:
            return true;
    }
}

function validateAttackerConfig() {
    const attacks = parseInt(document.getElementById('num_attacks').value);
    const skill = parseInt(document.getElementById('skill').value);
    const strength = parseInt(document.getElementById('strength').value);

    if (attacks < 1 || attacks > 100) {
        showError('Number of attacks must be between 1 and 100');
        return false;
    }
    if (skill < 2 || skill > 6) {
        showError('Skill value must be between 2+ and 6+');
        return false;
    }
    if (strength < 1 || strength > 20) {
        showError('Strength must be between 1 and 20');
        return false;
    }

    return true;
}

function validateDefenderConfig() {
    const toughness = parseInt(document.getElementById('toughness').value);
    const save = parseInt(document.getElementById('save').value);
    const wounds = parseInt(document.getElementById('wounds_per_model').value);
    const size = parseInt(document.getElementById('unit_size').value);

    if (toughness < 1 || toughness > 20) {
        showError('Toughness must be between 1 and 20');
        return false;
    }
    if (save < 2 || save > 7) {
        showError('Save value must be between 2+ and 7+ (no save)');
        return false;
    }
    if (wounds < 1 || wounds > 30) {
        showError('Wounds per model must be between 1 and 30');
        return false;
    }
    if (size < 1 || size > 30) {
        showError('Unit size must be between 1 and 30');
        return false;
    }

    return true;
}

function showError(message) {
    showToast(message, 'error');
}

function resetSimulator() {
    if (confirm('Are you sure you want to reset all values?')) {
        currentStep = 1;
        updateStepDisplay();

        // Clear completed status
        document.querySelectorAll('.step').forEach(step => {
            step.classList.remove('completed');
        });

        // Reset form values
        document.getElementById('num_attacks').value = '10';
        document.getElementById('skill').value = '3';
        document.getElementById('strength').value = '4';
        document.getElementById('ap').value = '0';
        document.getElementById('damage').value = '1';
        document.getElementById('toughness').value = '4';
        document.getElementById('save').value = '3';
        document.getElementById('invuln').value = '';
        document.getElementById('wounds_per_model').value = '2';
        document.getElementById('unit_size').value = '5';

        // Clear checkboxes
        document.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            cb.checked = false;
        });

        // Clear optional fields
        document.querySelectorAll('input[placeholder*="None"]').forEach(input => {
            input.value = '';
        });

        // Hide results
        document.getElementById('results-container').style.display = 'none';
    }
}

async function runSimulation() {
    const btn = event.target;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> SIMULATING...';

    try {
        // Gather all data
        const data = {
            // Attacker
            num_attacks: parseInt(document.getElementById('num_attacks').value),
            attack_type: document.getElementById('attack_type').value,
            skill: parseInt(document.getElementById('skill').value),
            strength: parseInt(document.getElementById('strength').value),
            ap: parseInt(document.getElementById('ap').value),
            damage: document.getElementById('damage').value,

            // Defender
            toughness: parseInt(document.getElementById('toughness').value),
            save: parseInt(document.getElementById('save').value),
            invuln: document.getElementById('invuln').value || null,
            wounds_per_model: parseInt(document.getElementById('wounds_per_model').value),
            unit_size: parseInt(document.getElementById('unit_size').value),

            // Weapon abilities
            lethal_hits: document.getElementById('lethal_hits').checked,
            devastating_wounds: document.getElementById('devastating_wounds').checked,
            twin_linked: document.getElementById('twin_linked').checked,
            torrent: document.getElementById('torrent').checked,
            blast: document.getElementById('blast').checked,
            ignores_cover: document.getElementById('ignores_cover').checked,
            hazardous: document.getElementById('hazardous').checked,
            precision: document.getElementById('precision').checked,
            heavy: document.getElementById('heavy').checked,
            assault: document.getElementById('assault').checked,
            sustained_hits: document.getElementById('sustained_hits').value || null,
            melta: document.getElementById('melta').value || null,
            rapid_fire: document.getElementById('rapid_fire').value || null,
            anti: document.getElementById('anti').value || null,

            // Defender abilities
            feel_no_pain: document.getElementById('feel_no_pain').value || null,
            stealth: document.getElementById('stealth').checked,
            lone_operative: document.getElementById('lone_operative').checked,
            cover: document.getElementById('cover').checked,
            cover_bonus: parseInt(document.getElementById('cover_bonus').value) || 1,
            target_keywords: parseKeywords(document.getElementById('target_keywords').value),

            // Re-rolls
            reroll_all_hits: document.getElementById('reroll_all_hits').checked,
            reroll_hit_1s: document.getElementById('reroll_hit_1s').checked,
            reroll_all_wounds: document.getElementById('reroll_all_wounds').checked,
            reroll_wound_1s: document.getElementById('reroll_wound_1s').checked,

            // Context
            range_to_target: parseInt(document.getElementById('range_to_target').value),
            attacker_moved: document.getElementById('attacker_moved').checked,

            // Simulation options
            num_simulations: parseInt(document.getElementById('num_simulations').value)
        };

        // Call API
        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            displayResults(result);
        } else {
            showError('Simulation failed: ' + result.error);
        }

    } catch (error) {
        console.error('Simulation error:', error);
        showError('An error occurred during simulation: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-play"></i> RUN SIMULATION';
    }
}

function parseKeywords(keywordsStr) {
    if (!keywordsStr || keywordsStr.trim() === '') {
        return [];
    }
    return keywordsStr.split(',').map(kw => kw.trim().toUpperCase()).filter(kw => kw !== '');
}

function displayResults(result) {
    const resultsContainer = document.getElementById('results-container');
    const resultsContent = document.getElementById('results-content');
    const statsContent = document.getElementById('stats-content');

    // Show results container
    resultsContainer.style.display = 'block';

    // Display sample result (from first simulation)
    const sample = result.sample_result;
    resultsContent.innerHTML = `
        <div class="result-grid">
            <div class="stat-box">
                <div class="stat-box-label">Total Attacks</div>
                <div class="stat-box-value">${sample.num_attacks}</div>
            </div>
            <div class="stat-box">
                <div class="stat-box-label">Hits</div>
                <div class="stat-box-value">${sample.num_hits}</div>
                <small style="color: var(--text-secondary);">${sample.num_critical_hits} critical</small>
            </div>
            <div class="stat-box">
                <div class="stat-box-label">Wounds</div>
                <div class="stat-box-value">${sample.num_wounds}</div>
                <small style="color: var(--text-secondary);">${sample.num_critical_wounds} critical</small>
            </div>
            <div class="stat-box">
                <div class="stat-box-label">Failed Saves</div>
                <div class="stat-box-value danger">${sample.num_saves_failed}</div>
            </div>
            <div class="stat-box">
                <div class="stat-box-label">Damage Dealt</div>
                <div class="stat-box-value danger">${sample.total_damage}</div>
            </div>
            <div class="stat-box">
                <div class="stat-box-label">After FNP</div>
                <div class="stat-box-value danger">${sample.damage_after_fnp}</div>
            </div>
            <div class="stat-box glow">
                <div class="stat-box-label">Models Destroyed</div>
                <div class="stat-box-value success">${sample.models_destroyed}</div>
            </div>
        </div>

        ${sample.sustained_hits_generated > 0 ? `
            <div class="result-stat">
                <span class="result-label"><i class="fas fa-plus-circle"></i> Sustained Hits Generated</span>
                <span class="result-value">${sample.sustained_hits_generated}</span>
            </div>
        ` : ''}

        ${sample.lethal_hits_auto_wounds > 0 ? `
            <div class="result-stat">
                <span class="result-label"><i class="fas fa-crosshairs"></i> Lethal Hits Auto-wounds</span>
                <span class="result-value">${sample.lethal_hits_auto_wounds}</span>
            </div>
        ` : ''}

        ${sample.hazardous_damage > 0 ? `
            <div class="result-stat">
                <span class="result-label"><i class="fas fa-radiation"></i> Hazardous Self-Damage</span>
                <span class="result-value danger">${sample.hazardous_damage}</span>
            </div>
        ` : ''}
    `;

    // Display statistics (from multiple simulations)
    const stats = result.stats;
    const numSims = result.num_simulations;

    statsContent.innerHTML = `
        <p style="color: var(--text-secondary); margin-bottom: 20px;">
            <i class="fas fa-info-circle"></i> Based on ${numSims.toLocaleString()} simulation${numSims > 1 ? 's' : ''}
        </p>

        <div class="result-grid">
            <div class="stat-box">
                <div class="stat-box-label">Avg Hits</div>
                <div class="stat-box-value">${stats.avg_hits.toFixed(2)}</div>
                <small style="color: var(--text-secondary);">${stats.avg_critical_hits.toFixed(2)} crit</small>
            </div>
            <div class="stat-box">
                <div class="stat-box-label">Avg Wounds</div>
                <div class="stat-box-value">${stats.avg_wounds.toFixed(2)}</div>
                <small style="color: var(--text-secondary);">${stats.avg_critical_wounds.toFixed(2)} crit</small>
            </div>
            <div class="stat-box">
                <div class="stat-box-label">Avg Failed Saves</div>
                <div class="stat-box-value">${stats.avg_saves_failed.toFixed(2)}</div>
            </div>
            <div class="stat-box">
                <div class="stat-box-label">Avg Damage</div>
                <div class="stat-box-value danger">${stats.avg_damage_after_fnp.toFixed(2)}</div>
            </div>
            <div class="stat-box glow">
                <div class="stat-box-label">Avg Models Killed</div>
                <div class="stat-box-value success">${stats.avg_models_destroyed.toFixed(2)}</div>
            </div>
        </div>

        <h4 style="color: var(--accent-color); margin: 25px 0 15px;">Damage Range</h4>
        <div class="result-stat">
            <span class="result-label">Minimum Damage</span>
            <span class="result-value">${stats.min_damage}</span>
        </div>
        <div class="result-stat">
            <span class="result-label">Maximum Damage</span>
            <span class="result-value">${stats.max_damage}</span>
        </div>
        <div class="result-stat">
            <span class="result-label">Minimum Models Destroyed</span>
            <span class="result-value">${stats.min_models_destroyed}</span>
        </div>
        <div class="result-stat">
            <span class="result-label">Maximum Models Destroyed</span>
            <span class="result-value highlight">${stats.max_models_destroyed}</span>
        </div>
    `;

    // Scroll to results
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ===== GITHUB DATASET LOADER =====

const GITHUB_API = 'https://api.github.com/repos/BSData/wh40k-10e/contents';
const GITHUB_RAW = 'https://raw.githubusercontent.com/BSData/wh40k-10e/main';

async function openGitHubLoader() {
    const modal = document.getElementById('github-modal');
    modal.style.display = 'block';

    try {
        // Fetch available .cat files from GitHub
        const response = await fetch(GITHUB_API);
        const files = await response.json();

        // Filter for .cat files (faction catalogs)
        const catalogs = files.filter(file => file.name.endsWith('.cat') && !file.name.includes('Library'));

        // Display faction cards
        const factionsContainer = document.getElementById('github-factions');
        factionsContainer.innerHTML = '';

        catalogs.forEach(catalog => {
            const factionName = catalog.name.replace('.cat', '');
            const card = document.createElement('div');
            card.className = 'faction-card';
            card.innerHTML = `
                <div class="faction-card-name">
                    <i class="fas fa-download"></i> ${factionName}
                </div>
                <div class="faction-card-info">
                    Size: ${(catalog.size / 1024).toFixed(0)} KB
                </div>
            `;
            card.onclick = () => downloadFromGitHub(catalog.name, catalog.download_url);
            factionsContainer.appendChild(card);
        });

    } catch (error) {
        console.error('Error loading GitHub datasets:', error);
        showToast('Failed to load datasets from GitHub: ' + error.message, 'error');
        const factionsContainer = document.getElementById('github-factions');
        factionsContainer.innerHTML = '<p style="color: var(--danger-color);">Failed to load datasets. Please try again.</p>';
    }
}

function closeGitHubLoader() {
    document.getElementById('github-modal').style.display = 'none';
}

async function downloadFromGitHub(filename, downloadUrl) {
    const loadingToast = showLoading(`Downloading ${filename}...`);

    try {
        // Download the file
        const response = await fetch(downloadUrl);
        const content = await response.text();

        closeToast(loadingToast.querySelector('.toast-close'));
        const processingToast = showLoading('Processing dataset...');

        // Send to backend to process
        const uploadResponse = await fetch('/api/upload-dataset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename: filename,
                content: content
            })
        });

        const result = await uploadResponse.json();

        closeToast(processingToast.querySelector('.toast-close'));

        if (result.success) {
            showToast(`Successfully loaded ${result.units_loaded} units from ${filename}`, 'success', 'Dataset Loaded', 6000);
            closeGitHubLoader();

            // Reload factions in the UI
            setTimeout(() => {
                loadFactions();
            }, 500);
        } else {
            showToast('Failed to process dataset: ' + result.error, 'error');
        }

    } catch (error) {
        console.error('Error downloading from GitHub:', error);
        showToast('Failed to download dataset: ' + error.message, 'error');
    }
}

async function loadLocalDataset() {
    const loadingToast = showLoading('Loading local dataset...');

    try {
        const response = await fetch('/api/load-units', {
            method: 'POST'
        });
        const result = await response.json();

        closeToast(loadingToast.querySelector('.toast-close'));

        if (result.success) {
            showToast(`Loaded ${result.selectable_units} units from local datasets`, 'success', 'Dataset Loaded', 5000);
            // Reload factions in the UI
            setTimeout(() => {
                loadFactions();
            }, 500);
        } else {
            showToast('No local datasets found. Please download from GitHub or add .cat files to the datasets folder.', 'warning', 'No Datasets', 6000);
        }
    } catch (error) {
        console.error('Error loading local dataset:', error);
        showToast('Failed to load local dataset: ' + error.message, 'error');
    }
}

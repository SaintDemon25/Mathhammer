// Warhammer 40k Combat Simulator - Interactive JavaScript

let currentStep = 1;
const totalSteps = 4;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    updateAttackTypeLabel();
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
    alert(message); // Simple alert for now, could be improved with modal
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

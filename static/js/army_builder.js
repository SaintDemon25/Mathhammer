/**
 * Warhammer 40k Army Builder
 * Frontend logic for army list building and management
 */

// Global state
let currentArmy = {
    name: 'New Army',
    faction: '',
    detachment: 'Gladius Strike Force',
    points_limit: 2000,
    units: [],
    created_at: new Date().toISOString(),
    modified_at: new Date().toISOString()
};

let allUnits = [];
let factions = [];
let currentCategory = 'all';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
    loadUnitsData();
});

function initializeApp() {
    console.log('Initializing Army Builder...');
}

function setupEventListeners() {
    // Buttons
    document.getElementById('new-army-btn').addEventListener('click', () => showNewArmyModal());
    document.getElementById('load-army-btn').addEventListener('click', () => showLoadArmyModal());
    document.getElementById('save-army-btn').addEventListener('click', () => saveArmy());
    document.getElementById('edit-army-btn').addEventListener('click', () => showEditArmyModal());

    // Modals
    document.getElementById('cancel-army-btn').addEventListener('click', () => hideModal('army-details-modal'));
    document.getElementById('cancel-load-btn').addEventListener('click', () => hideModal('load-army-modal'));
    document.getElementById('army-details-form').addEventListener('submit', (e) => {
        e.preventDefault();
        createOrUpdateArmy();
    });

    // Faction select
    document.getElementById('faction-select').addEventListener('change', (e) => {
        filterUnitsByFaction(e.target.value);
    });

    // Category tabs
    document.querySelectorAll('.category-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            setActiveCategory(e.target.dataset.category);
        });
    });
}

async function loadUnitsData() {
    try {
        showToast('Loading units...', 'info');

        // Load units
        const response = await fetch('/api/load-units', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            // Get selectable units
            const unitsResponse = await fetch('/api/units/selectable');
            const unitsData = await unitsResponse.json();

            factions = unitsData.factions || [];
            allUnits = [];

            // Flatten units by faction
            for (const faction of factions) {
                const units = unitsData.units[faction] || [];
                allUnits.push(...units);
            }

            console.log(`Loaded ${allUnits.length} units from ${factions.length} factions`);

            populateFactionSelects();
            showToast(`Loaded ${allUnits.length} units`, 'success');
        } else {
            showToast('Error loading units: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error loading units:', error);
        showToast('Failed to load units', 'error');
    }
}

function populateFactionSelects() {
    const selects = [
        document.getElementById('faction-select'),
        document.getElementById('input-faction')
    ];

    selects.forEach(select => {
        select.innerHTML = '<option value="">Select Faction</option>';
        factions.forEach(faction => {
            const option = document.createElement('option');
            option.value = faction;
            option.textContent = faction;
            select.appendChild(option);
        });
    });
}

function filterUnitsByFaction(faction) {
    const unitList = document.getElementById('unit-list');

    if (!faction) {
        unitList.innerHTML = '<p class="placeholder">Select a faction to browse units</p>';
        return;
    }

    const factionUnits = allUnits.filter(u => u.faction === faction);

    // Filter by category
    let filtered = factionUnits;
    if (currentCategory !== 'all') {
        filtered = factionUnits.filter(u => {
            const categories = u.categories || u.keywords || [];
            return categories.some(cat => cat.toLowerCase().includes(currentCategory.toLowerCase()));
        });
    }

    renderUnitList(filtered);
}

function renderUnitList(units) {
    const unitList = document.getElementById('unit-list');

    if (units.length === 0) {
        unitList.innerHTML = '<p class="placeholder">No units found</p>';
        return;
    }

    unitList.innerHTML = '';

    units.forEach(unit => {
        const card = createUnitCard(unit);
        unitList.appendChild(card);
    });
}

function createUnitCard(unit) {
    const card = document.createElement('div');
    card.className = 'unit-card';

    const header = document.createElement('div');
    header.className = 'unit-card-header';

    const name = document.createElement('span');
    name.className = 'unit-card-name';
    name.textContent = unit.name;

    const points = document.createElement('span');
    points.className = 'unit-card-points';
    points.textContent = `${unit.points_cost || 0} pts`;

    header.appendChild(name);
    header.appendChild(points);

    // Categories
    const categoriesDiv = document.createElement('div');
    categoriesDiv.className = 'unit-card-categories';

    const categories = unit.categories || unit.keywords || [];
    categories.slice(0, 3).forEach(cat => {
        const badge = document.createElement('span');
        badge.className = 'category-badge';
        badge.textContent = cat;
        categoriesDiv.appendChild(badge);
    });

    card.appendChild(header);
    card.appendChild(categoriesDiv);

    // Click to add to army
    card.addEventListener('click', () => addUnitToArmy(unit));

    return card;
}

function setActiveCategory(category) {
    currentCategory = category;

    // Update UI
    document.querySelectorAll('.category-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.category === category);
    });

    // Re-filter units
    const faction = document.getElementById('faction-select').value;
    if (faction) {
        filterUnitsByFaction(faction);
    }
}

function addUnitToArmy(unit) {
    // Create army unit
    const armyUnit = {
        unit_id: unit.id,
        unit_name: unit.name,
        faction: unit.faction,
        points_cost: unit.points_cost || 0,
        selected_models: [],
        enhancements: []
    };

    currentArmy.units.push(armyUnit);
    currentArmy.modified_at = new Date().toISOString();

    updateArmyDisplay();
    showToast(`Added ${unit.name} to army`, 'success');
}

function removeUnitFromArmy(index) {
    const unit = currentArmy.units[index];
    currentArmy.units.splice(index, 1);
    currentArmy.modified_at = new Date().toISOString();

    updateArmyDisplay();
    showToast(`Removed ${unit.unit_name} from army`, 'info');
}

function updateArmyDisplay() {
    // Update header
    document.getElementById('army-name-display').textContent = currentArmy.name;
    document.getElementById('army-faction').textContent = currentArmy.faction || '-';
    document.getElementById('army-detachment').textContent = currentArmy.detachment;

    // Calculate total points
    const totalPoints = currentArmy.units.reduce((sum, u) => sum + (u.points_cost || 0), 0);
    document.getElementById('army-points').textContent = totalPoints;
    document.getElementById('army-points-limit').textContent = currentArmy.points_limit;

    // Color code points
    const pointsDisplay = document.querySelector('.points-display');
    if (totalPoints > currentArmy.points_limit) {
        pointsDisplay.style.color = '#e74c3c';
    } else if (totalPoints >= currentArmy.points_limit * 0.9) {
        pointsDisplay.style.color = '#f39c12';
    } else {
        pointsDisplay.style.color = 'var(--accent-color)';
    }

    // Update roster
    renderRoster();
}

function renderRoster() {
    const rosterList = document.getElementById('roster-list');

    if (currentArmy.units.length === 0) {
        rosterList.innerHTML = '<p class="placeholder">Add units to your army</p>';
        return;
    }

    rosterList.innerHTML = '';

    currentArmy.units.forEach((unit, index) => {
        const card = createRosterUnitCard(unit, index);
        rosterList.appendChild(card);
    });
}

function createRosterUnitCard(unit, index) {
    const card = document.createElement('div');
    card.className = 'roster-unit-card';

    const header = document.createElement('div');
    header.className = 'roster-unit-header';

    const info = document.createElement('div');
    const name = document.createElement('div');
    name.className = 'unit-card-name';
    name.textContent = unit.unit_name;

    const points = document.createElement('div');
    points.className = 'unit-card-points';
    points.textContent = `${unit.points_cost} pts`;

    info.appendChild(name);
    info.appendChild(points);

    const actions = document.createElement('div');
    actions.className = 'roster-unit-actions';

    const removeBtn = document.createElement('button');
    removeBtn.className = 'btn-icon';
    removeBtn.innerHTML = '🗑️';
    removeBtn.title = 'Remove unit';
    removeBtn.addEventListener('click', () => removeUnitFromArmy(index));

    actions.appendChild(removeBtn);

    header.appendChild(info);
    header.appendChild(actions);

    card.appendChild(header);

    return card;
}

// Modal Management
function showNewArmyModal() {
    document.getElementById('modal-title').textContent = 'New Army';
    document.getElementById('input-army-name').value = '';
    document.getElementById('input-faction').value = '';
    document.getElementById('input-detachment').value = 'Gladius Strike Force';
    document.getElementById('input-points-limit').value = '2000';

    showModal('army-details-modal');
}

function showEditArmyModal() {
    document.getElementById('modal-title').textContent = 'Edit Army';
    document.getElementById('input-army-name').value = currentArmy.name;
    document.getElementById('input-faction').value = currentArmy.faction;
    document.getElementById('input-detachment').value = currentArmy.detachment;
    document.getElementById('input-points-limit').value = currentArmy.points_limit;

    showModal('army-details-modal');
}

function createOrUpdateArmy() {
    const name = document.getElementById('input-army-name').value;
    const faction = document.getElementById('input-faction').value;
    const detachment = document.getElementById('input-detachment').value;
    const pointsLimit = parseInt(document.getElementById('input-points-limit').value);

    currentArmy.name = name;
    currentArmy.faction = faction;
    currentArmy.detachment = detachment;
    currentArmy.points_limit = pointsLimit;
    currentArmy.modified_at = new Date().toISOString();

    // If faction changed, clear units
    const factionChanged = document.getElementById('faction-select').value !== faction;
    if (factionChanged && currentArmy.units.length > 0) {
        if (!confirm('Changing faction will clear your current army. Continue?')) {
            return;
        }
        currentArmy.units = [];
    }

    // Set faction filter
    document.getElementById('faction-select').value = faction;
    filterUnitsByFaction(faction);

    updateArmyDisplay();
    hideModal('army-details-modal');
    showToast('Army updated', 'success');
}

async function saveArmy() {
    if (currentArmy.units.length === 0) {
        showToast('Cannot save empty army', 'warning');
        return;
    }

    if (!currentArmy.name || !currentArmy.faction) {
        showToast('Please set army name and faction first', 'warning');
        showEditArmyModal();
        return;
    }

    try {
        const response = await fetch('/api/army/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                army: currentArmy
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`Army saved: ${data.filename}`, 'success');
        } else {
            showToast('Error saving army: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error saving army:', error);
        showToast('Failed to save army', 'error');
    }
}

async function showLoadArmyModal() {
    showModal('load-army-modal');

    const listDiv = document.getElementById('saved-armies-list');
    listDiv.innerHTML = '<p>Loading...</p>';

    try {
        const response = await fetch('/api/army/list');
        const data = await response.json();

        if (data.success) {
            if (data.armies.length === 0) {
                listDiv.innerHTML = '<p class="placeholder">No saved armies</p>';
                return;
            }

            listDiv.innerHTML = '';

            data.armies.forEach(army => {
                const card = createSavedArmyCard(army);
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

function createSavedArmyCard(armyInfo) {
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

    card.addEventListener('click', () => loadArmy(armyInfo.filename));

    return card;
}

async function loadArmy(filename) {
    try {
        const response = await fetch(`/api/army/load/${filename}`);
        const data = await response.json();

        if (data.success) {
            currentArmy = data.army;
            document.getElementById('faction-select').value = currentArmy.faction;
            filterUnitsByFaction(currentArmy.faction);
            updateArmyDisplay();
            hideModal('load-army-modal');
            showToast(`Loaded: ${currentArmy.name}`, 'success');
        } else {
            showToast('Error loading army: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error loading army:', error);
        showToast('Failed to load army', 'error');
    }
}

// Utility Functions
function showModal(modalId) {
    document.getElementById(modalId).classList.add('show');
}

function hideModal(modalId) {
    document.getElementById(modalId).classList.remove('show');
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

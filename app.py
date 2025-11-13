"""
Flask web application for Warhammer 40k Mathhammer
"""

import os
import json
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

from mathhammer.parser import BSDataParser
from mathhammer.calculator import MathHammer
from mathhammer.models import DataCatalog, UnitProfile, WeaponProfile, Characteristic

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'datasets'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global data catalog
catalog = DataCatalog()
parser = BSDataParser()

# Ensure datasets directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/units', methods=['GET'])
def get_units():
    """Get all units"""
    units_data = []
    for unit in catalog.units.values():
        units_data.append({
            'id': unit.id,
            'name': unit.name,
            'faction': unit.faction,
            'points': unit.points_cost,
            'has_profile': unit.unit_profile is not None,
            'weapon_count': len(unit.weapons)
        })
    return jsonify(units_data)


@app.route('/api/units/<unit_id>', methods=['GET'])
def get_unit(unit_id):
    """Get detailed unit information"""
    unit = catalog.get_unit(unit_id)
    if not unit:
        return jsonify({'error': 'Unit not found'}), 404

    unit_data = {
        'id': unit.id,
        'name': unit.name,
        'faction': unit.faction,
        'points': unit.points_cost,
        'keywords': unit.keywords
    }

    # Add unit profile
    if unit.unit_profile:
        unit_data['profile'] = {
            'movement': unit.unit_profile.movement,
            'toughness': unit.unit_profile.toughness,
            'save': unit.unit_profile.save,
            'wounds': unit.unit_profile.wounds,
            'leadership': unit.unit_profile.leadership,
            'oc': unit.unit_profile.objective_control,
            'invuln': unit.unit_profile.invulnerable_save
        }

    # Add weapons
    unit_data['weapons'] = []
    for weapon in unit.weapons:
        unit_data['weapons'].append({
            'name': weapon.name,
            'type': weapon.type_name,
            'range': weapon.range_value,
            'attacks': weapon.attacks,
            'skill': weapon.skill,
            'strength': weapon.strength,
            'ap': weapon.armor_penetration,
            'damage': weapon.damage
        })

    # Add abilities
    unit_data['abilities'] = []
    for ability in unit.abilities:
        unit_data['abilities'].append({
            'name': ability.name,
            'description': ability.description
        })

    return jsonify(unit_data)


@app.route('/api/factions', methods=['GET'])
def get_factions():
    """Get all factions"""
    return jsonify(catalog.factions)


@app.route('/api/search', methods=['GET'])
def search_units():
    """Search units by name"""
    query = request.args.get('q', '')
    units = catalog.search_units(query)

    results = []
    for unit in units[:50]:  # Limit to 50 results
        results.append({
            'id': unit.id,
            'name': unit.name,
            'faction': unit.faction
        })

    return jsonify(results)


@app.route('/api/calculate/attack', methods=['POST'])
def calculate_attack():
    """Calculate attack outcomes"""
    data = request.json

    attacker_id = data.get('attacker_id')
    weapon_name = data.get('weapon_name')
    defender_id = data.get('defender_id')
    num_models = data.get('num_models', 1)

    # Get units
    attacker = catalog.get_unit(attacker_id)
    defender = catalog.get_unit(defender_id)

    if not attacker or not defender:
        return jsonify({'error': 'Unit not found'}), 404

    if not attacker.unit_profile or not defender.unit_profile:
        return jsonify({'error': 'Unit missing profile data'}), 400

    # Get weapon
    weapon = attacker.get_weapon_by_name(weapon_name)
    if not weapon:
        return jsonify({'error': 'Weapon not found'}), 404

    # Calculate
    result = MathHammer.calculate_attack_sequence(
        weapon=weapon,
        attacker=attacker.unit_profile,
        defender=defender.unit_profile,
        num_models_attacking=num_models
    )

    return jsonify({
        'attacker': attacker.name,
        'weapon': weapon_name,
        'defender': defender.name,
        'num_models': num_models,
        'expected_hits': round(result.expected_hits, 2),
        'expected_wounds': round(result.expected_wounds, 2),
        'expected_unsaved_wounds': round(result.expected_unsaved_wounds, 2),
        'expected_damage': round(result.expected_damage, 2),
        'hit_probability': round(result.hit_probability * 100, 1),
        'wound_probability': round(result.wound_probability * 100, 1),
        'save_failure_probability': round(result.save_failure_probability * 100, 1)
    })


@app.route('/api/compare/weapons', methods=['POST'])
def compare_weapons():
    """Compare weapon effectiveness"""
    data = request.json

    unit_id = data.get('unit_id')
    defender_id = data.get('defender_id')
    num_models = data.get('num_models', 1)

    unit = catalog.get_unit(unit_id)
    defender = catalog.get_unit(defender_id)

    if not unit or not defender:
        return jsonify({'error': 'Unit not found'}), 404

    if not defender.unit_profile:
        return jsonify({'error': 'Defender missing profile'}), 400

    if not unit.weapons:
        return jsonify({'error': 'Unit has no weapons'}), 400

    # Compare all weapons
    results = MathHammer.compare_weapons(
        weapons=unit.weapons,
        defender=defender.unit_profile,
        num_models_attacking=num_models
    )

    comparison = []
    for weapon_name, result in results:
        comparison.append({
            'weapon': weapon_name,
            'expected_damage': round(result.expected_damage, 2),
            'expected_hits': round(result.expected_hits, 2),
            'expected_wounds': round(result.expected_wounds, 2),
            'expected_unsaved': round(result.expected_unsaved_wounds, 2)
        })

    return jsonify({
        'attacker': unit.name,
        'defender': defender.name,
        'comparison': comparison
    })


@app.route('/api/simulate/combat', methods=['POST'])
def simulate_combat():
    """Simulate unit vs unit combat"""
    data = request.json

    attacker_id = data.get('attacker_id')
    defender_id = data.get('defender_id')
    attacker_count = data.get('attacker_count', 1)
    defender_count = data.get('defender_count', 1)
    weapon_name = data.get('weapon_name')

    attacker = catalog.get_unit(attacker_id)
    defender = catalog.get_unit(defender_id)

    if not attacker or not defender:
        return jsonify({'error': 'Unit not found'}), 404

    try:
        simulation = MathHammer.simulate_combat(
            attacker=attacker,
            defender=defender,
            attacker_model_count=attacker_count,
            defender_model_count=defender_count,
            weapon_name=weapon_name
        )

        return jsonify({
            'attacker': simulation.attacker_name,
            'defender': simulation.defender_name,
            'weapon': simulation.weapon_name,
            'num_attacks': simulation.num_attacks,
            'expected_hits': round(simulation.attack_result.expected_hits, 2),
            'expected_wounds': round(simulation.attack_result.expected_wounds, 2),
            'expected_damage': round(simulation.attack_result.expected_damage, 2),
            'models_killed': round(simulation.expected_models_killed, 2),
            'defender_remaining': round(simulation.defender_models_remaining, 2)
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/load-dataset', methods=['POST'])
def load_dataset():
    """Load dataset from datasets directory"""
    try:
        dataset_path = Path(app.config['UPLOAD_FOLDER'])

        # Clear existing catalog
        global catalog, parser
        parser = BSDataParser()

        # Load all data files
        catalog = parser.load_dataset(str(dataset_path))

        return jsonify({
            'success': True,
            'units_loaded': len(catalog.units),
            'factions': len(catalog.factions),
            'faction_list': catalog.factions
        })
    except Exception as e:
        logger.error(f"Error loading dataset: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/dataset/info', methods=['GET'])
def dataset_info():
    """Get information about loaded dataset"""
    return jsonify({
        'units_count': len(catalog.units),
        'factions_count': len(catalog.factions),
        'factions': catalog.factions
    })


if __name__ == '__main__':
    # Try to load default dataset on startup
    try:
        dataset_path = Path(app.config['UPLOAD_FOLDER'])
        if any(dataset_path.glob('*.cat')) or any(dataset_path.glob('*.gst')):
            logger.info("Loading default dataset...")
            catalog = parser.load_dataset(str(dataset_path))
            logger.info(f"Loaded {len(catalog.units)} units from {len(catalog.factions)} factions")
    except Exception as e:
        logger.warning(f"Could not load default dataset: {e}")

    app.run(debug=True, host='0.0.0.0', port=5000)

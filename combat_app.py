"""
Flask web application for Warhammer 40k Combat Simulator
User-friendly GUI with full 10th edition rules support
"""

import os
import json
from flask import Flask, render_template, request, jsonify
from pathlib import Path

from combat_engine import (
    CombatSimulator, WeaponAbilities, UnitAbilities, AttackType,
    AttackSequenceResult, DiceRoll
)
from enhanced_parser import EnhancedBSDataParser
from mathhammer.models import DataCatalog

app = Flask(__name__)
app.config['SECRET_KEY'] = 'combat-sim-secret-key'

# Global data
catalog = DataCatalog()
parser = EnhancedBSDataParser()


@app.route('/')
def index():
    """Main combat simulator page"""
    return render_template('combat_simulator.html')


@app.route('/api/simulate', methods=['POST'])
def simulate_combat():
    """
    Simulate combat with given parameters
    Returns detailed results including all rolls
    """
    try:
        data = request.json

        # Parse weapon stats
        num_attacks = int(data.get('num_attacks', 1))
        skill = int(data.get('skill', 4))
        strength = int(data.get('strength', 4))
        ap = int(data.get('ap', 0))
        damage = data.get('damage', '1')
        attack_type = AttackType.RANGED if data.get('attack_type') == 'ranged' else AttackType.MELEE

        # Parse target stats
        toughness = int(data.get('toughness', 4))
        save = int(data.get('save', 3))
        invuln = data.get('invuln')
        if invuln:
            invuln = int(invuln)
        wounds_per_model = int(data.get('wounds_per_model', 1))
        unit_size = int(data.get('unit_size', 5))

        # Parse weapon abilities
        weapon_abilities = WeaponAbilities(
            anti=parse_anti(data.get('anti')),
            blast=data.get('blast', False),
            devastating_wounds=data.get('devastating_wounds', False),
            hazardous=data.get('hazardous', False),
            heavy=data.get('heavy', False),
            ignores_cover=data.get('ignores_cover', False),
            indirect_fire=data.get('indirect_fire', False),
            lethal_hits=data.get('lethal_hits', False),
            melta=parse_optional_int(data.get('melta')),
            precision=data.get('precision', False),
            rapid_fire=parse_optional_int(data.get('rapid_fire')),
            sustained_hits=parse_optional_int(data.get('sustained_hits')),
            torrent=data.get('torrent', False),
            twin_linked=data.get('twin_linked', False),
            assault=data.get('assault', False)
        )

        # Parse target abilities
        target_keywords = set(data.get('target_keywords', []))
        target_abilities = UnitAbilities(
            feel_no_pain=parse_optional_int(data.get('feel_no_pain')),
            stealth=data.get('stealth', False),
            lone_operative=data.get('lone_operative', False),
            cover=data.get('cover', False),
            cover_bonus=int(data.get('cover_bonus', 1)),
            keywords=target_keywords
        )

        # Parse attacker abilities
        attacker_abilities = UnitAbilities(
            reroll_hit_rolls_of_1=data.get('reroll_hit_1s', False),
            reroll_all_hit_rolls=data.get('reroll_all_hits', False),
            reroll_wound_rolls_of_1=data.get('reroll_wound_1s', False),
            reroll_all_wound_rolls=data.get('reroll_all_wounds', False)
        )

        # Context
        range_to_target = int(data.get('range_to_target', 24))
        attacker_moved = data.get('attacker_moved', False)

        # Run simulation multiple times for statistics
        num_simulations = int(data.get('num_simulations', 1))
        results = []

        for _ in range(num_simulations):
            result = CombatSimulator.simulate_attack_sequence(
                num_attacks=num_attacks,
                skill=skill,
                strength=strength,
                ap=ap,
                damage=damage,
                attack_type=attack_type,
                toughness=toughness,
                save=save,
                invuln=invuln,
                wounds_per_model=wounds_per_model,
                unit_size=unit_size,
                weapon_abilities=weapon_abilities,
                target_abilities=target_abilities,
                attacker_abilities=attacker_abilities,
                range_to_target=range_to_target,
                attacker_moved=attacker_moved
            )
            results.append(result)

        # Calculate statistics
        stats = calculate_statistics(results)

        # Return detailed results
        return jsonify({
            'success': True,
            'num_simulations': num_simulations,
            'stats': stats,
            'sample_result': {
                'num_attacks': results[0].num_attacks,
                'num_hits': results[0].num_hits,
                'num_critical_hits': results[0].num_critical_hits,
                'num_wounds': results[0].num_wounds,
                'num_critical_wounds': results[0].num_critical_wounds,
                'num_saves_failed': results[0].num_saves_failed,
                'total_damage': results[0].total_damage,
                'damage_after_fnp': results[0].damage_after_fnp,
                'models_destroyed': results[0].models_destroyed,
                'sustained_hits_generated': results[0].sustained_hits_generated,
                'lethal_hits_auto_wounds': results[0].lethal_hits_auto_wounds,
                'hazardous_damage': results[0].hazardous_damage
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/load-units', methods=['POST'])
def load_units():
    """Load units from BSData with enhanced parsing"""
    global catalog, parser

    try:
        dataset_path = Path('datasets')
        parser = EnhancedBSDataParser()
        catalog = parser.load_dataset_enhanced(str(dataset_path))

        return jsonify({
            'success': True,
            'units_loaded': len(catalog.units),
            'selectable_units': len(parser.selectable_units),
            'factions': catalog.factions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/units/selectable', methods=['GET'])
def get_selectable_units():
    """Get list of selectable units organized by faction"""
    faction = request.args.get('faction', None)

    if faction:
        units = [u for u in parser.selectable_units if u['faction'] == faction]
    else:
        units = parser.selectable_units

    return jsonify({
        'units': units,
        'count': len(units)
    })


@app.route('/api/units/by-category', methods=['GET'])
def get_units_by_category():
    """Get units organized by battlefield role"""
    faction = request.args.get('faction', None)
    categorized = parser.get_units_by_category()

    # Filter by faction if specified
    if faction:
        for category in categorized:
            categorized[category] = [
                {'id': u.id, 'name': u.name, 'faction': u.faction}
                for u in categorized[category]
                if u.faction == faction
            ]
    else:
        for category in categorized:
            categorized[category] = [
                {'id': u.id, 'name': u.name, 'faction': u.faction}
                for u in categorized[category]
            ]

    return jsonify(categorized)


@app.route('/api/units', methods=['GET'])
def get_units():
    """Get all loaded units"""
    units_data = []
    for unit in catalog.units.values():
        units_data.append({
            'id': unit.id,
            'name': unit.name,
            'faction': unit.faction,
            'has_profile': unit.unit_profile is not None,
            'weapons': [{
                'name': w.name,
                'type': w.type_name,
                'range': w.range_value,
                'attacks': w.attacks,
                'skill': w.skill,
                'strength': w.strength,
                'ap': w.armor_penetration,
                'damage': w.damage
            } for w in unit.weapons] if unit.weapons else []
        })
    return jsonify(units_data)


@app.route('/api/unit/<unit_id>', methods=['GET'])
def get_unit(unit_id):
    """Get specific unit details"""
    unit = catalog.get_unit(unit_id)
    if not unit:
        return jsonify({'error': 'Unit not found'}), 404

    # Extract unit abilities from keywords
    unit_abilities = []
    if unit.unit_profile and hasattr(unit.unit_profile, 'characteristics'):
        try:
            for char in unit.unit_profile.characteristics:
                # Handle Characteristic objects
                if hasattr(char, 'name') and hasattr(char, 'value'):
                    char_name = char.name
                    char_value = char.value
                elif isinstance(char, dict):
                    char_name = char.get('name', '')
                    char_value = char.get('value', '')
                else:
                    continue

                if char_name and char_name.lower() in ['keywords', 'abilities']:
                    # Parse comma-separated abilities
                    if char_value:
                        unit_abilities.extend([a.strip() for a in char_value.split(',')])
        except Exception as e:
            logger.warning(f"Error extracting unit abilities: {e}")

    return jsonify({
        'id': unit.id,
        'name': unit.name,
        'faction': unit.faction,
        'profile': {
            'toughness': unit.unit_profile.toughness if unit.unit_profile else None,
            'save': unit.unit_profile.save if unit.unit_profile else None,
            'wounds': unit.unit_profile.wounds if unit.unit_profile else None,
            'invuln': unit.unit_profile.invulnerable_save if unit.unit_profile else None,
            'abilities': unit_abilities
        } if unit.unit_profile else None,
        'weapons': [{
            'name': w.name,
            'type': w.type_name,
            'attacks': w.attacks,
            'skill': w.skill,
            'strength': w.strength,
            'ap': w.armor_penetration,
            'damage': w.damage,
            'abilities': extract_weapon_abilities(w)
        } for w in unit.weapons]
    })


def extract_weapon_abilities(weapon):
    """Extract abilities from weapon characteristics"""
    abilities = []
    if not hasattr(weapon, 'characteristics'):
        return abilities

    try:
        for char in weapon.characteristics:
            # Handle Characteristic objects
            if hasattr(char, 'name') and hasattr(char, 'value'):
                char_name = char.name
                char_value = char.value
            elif isinstance(char, dict):
                char_name = char.get('name', '')
                char_value = char.get('value', '')
            else:
                continue

            if char_name and char_name.lower() in ['keywords', 'abilities']:
                # Parse comma-separated abilities
                if char_value:
                    abilities.extend([a.strip() for a in char_value.split(',')])
    except Exception as e:
        logger.warning(f"Error extracting weapon abilities: {e}")

    return abilities


def parse_anti(anti_str):
    """Parse anti ability from string like 'INFANTRY 4+'"""
    if not anti_str or anti_str == '':
        return None
    parts = anti_str.split()
    if len(parts) >= 2:
        keyword = parts[0].upper()
        value = int(parts[1].replace('+', ''))
        return (keyword, value)
    return None


def parse_optional_int(value):
    """Parse optional integer value"""
    if value is None or value == '' or value == 'null':
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def calculate_statistics(results: list) -> dict:
    """Calculate statistics from multiple simulation runs"""
    if not results:
        return {}

    total = len(results)

    return {
        'avg_attacks': sum(r.num_attacks for r in results) / total,
        'avg_hits': sum(r.num_hits for r in results) / total,
        'avg_critical_hits': sum(r.num_critical_hits for r in results) / total,
        'avg_wounds': sum(r.num_wounds for r in results) / total,
        'avg_critical_wounds': sum(r.num_critical_wounds for r in results) / total,
        'avg_saves_failed': sum(r.num_saves_failed for r in results) / total,
        'avg_damage': sum(r.total_damage for r in results) / total,
        'avg_damage_after_fnp': sum(r.damage_after_fnp for r in results) / total,
        'avg_models_destroyed': sum(r.models_destroyed for r in results) / total,
        'min_damage': min(r.damage_after_fnp for r in results),
        'max_damage': max(r.damage_after_fnp for r in results),
        'min_models_destroyed': min(r.models_destroyed for r in results),
        'max_models_destroyed': max(r.models_destroyed for r in results)
    }


@app.route('/api/upload-dataset', methods=['POST'])
def upload_dataset():
    """Upload and process a dataset from GitHub"""
    global catalog, parser

    try:
        data = request.json
        filename = data.get('filename')
        content = data.get('content')

        if not filename or not content:
            return jsonify({
                'success': False,
                'error': 'Missing filename or content'
            }), 400

        # Save to datasets directory
        dataset_path = Path('datasets')
        dataset_path.mkdir(exist_ok=True)

        file_path = dataset_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Reload all datasets with enhanced parser
        parser = EnhancedBSDataParser()
        catalog = parser.load_dataset_enhanced(str(dataset_path))

        return jsonify({
            'success': True,
            'units_loaded': len(catalog.units),
            'selectable_units': len(parser.selectable_units),
            'factions': catalog.factions
        })

    except Exception as e:
        logger.error(f"Error uploading dataset: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Try to load dataset on startup
    try:
        dataset_path = Path('datasets')
        if dataset_path.exists() and any(dataset_path.glob('*.cat')):
            catalog = parser.load_dataset_enhanced(str(dataset_path))
            print(f"✓ Loaded {len(catalog.units)} units from {len(catalog.factions)} factions")
            print(f"✓ {len(parser.selectable_units)} selectable units")
    except Exception as e:
        print(f"⚠ Could not load dataset on startup: {e}")
        print("  You can load it later using the 'Load Dataset' button")

    app.run(debug=True, host='0.0.0.0', port=5000)

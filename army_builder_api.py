"""
Army Builder API
Backend endpoints for army list building, saving, and loading
"""

from flask import Blueprint, request, jsonify
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from mathhammer.models import Army, ArmyUnit, SelectedModel, SelectedWeapon

logger = logging.getLogger(__name__)

# Create blueprint
army_builder_bp = Blueprint('army_builder', __name__, url_prefix='/api/army')

# Directory for saving army lists
ARMY_LISTS_DIR = Path('army_lists')
ARMY_LISTS_DIR.mkdir(exist_ok=True)


@army_builder_bp.route('/create', methods=['POST'])
def create_army():
    """Create a new army roster"""
    try:
        data = request.json
        name = data.get('name', 'New Army')
        faction = data.get('faction', '')
        detachment = data.get('detachment', 'Gladius Strike Force')
        points_limit = data.get('points_limit', 2000)

        army = Army(
            name=name,
            faction=faction,
            detachment=detachment,
            points_limit=points_limit,
            created_at=datetime.now().isoformat(),
            modified_at=datetime.now().isoformat()
        )

        return jsonify({
            'success': True,
            'army': army_to_dict(army)
        })

    except Exception as e:
        logger.error(f"Error creating army: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@army_builder_bp.route('/save', methods=['POST'])
def save_army():
    """Save army roster to file"""
    try:
        data = request.json
        army_data = data.get('army')

        if not army_data:
            return jsonify({'success': False, 'error': 'No army data provided'}), 400

        army_name = army_data.get('name', 'Unnamed Army')
        # Create safe filename
        filename = f"{army_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = ARMY_LISTS_DIR / filename

        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(army_data, f, indent=2)

        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': str(filepath)
        })

    except Exception as e:
        logger.error(f"Error saving army: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@army_builder_bp.route('/load/<filename>', methods=['GET'])
def load_army(filename):
    """Load army roster from file"""
    try:
        filepath = ARMY_LISTS_DIR / filename

        if not filepath.exists():
            return jsonify({'success': False, 'error': 'Army list not found'}), 404

        with open(filepath, 'r', encoding='utf-8') as f:
            army_data = json.load(f)

        return jsonify({
            'success': True,
            'army': army_data
        })

    except Exception as e:
        logger.error(f"Error loading army: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@army_builder_bp.route('/list', methods=['GET'])
def list_armies():
    """List all saved army rosters"""
    try:
        armies = []

        for filepath in ARMY_LISTS_DIR.glob('*.json'):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    army_data = json.load(f)

                armies.append({
                    'filename': filepath.name,
                    'name': army_data.get('name', 'Unknown'),
                    'faction': army_data.get('faction', ''),
                    'points': sum(u.get('points_cost', 0) for u in army_data.get('units', [])),
                    'points_limit': army_data.get('points_limit', 2000),
                    'modified_at': army_data.get('modified_at', '')
                })
            except Exception as e:
                logger.warning(f"Could not load {filepath.name}: {e}")
                continue

        # Sort by modified date (newest first)
        armies.sort(key=lambda x: x.get('modified_at', ''), reverse=True)

        return jsonify({
            'success': True,
            'armies': armies
        })

    except Exception as e:
        logger.error(f"Error listing armies: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@army_builder_bp.route('/delete/<filename>', methods=['DELETE'])
def delete_army(filename):
    """Delete an army roster"""
    try:
        filepath = ARMY_LISTS_DIR / filename

        if not filepath.exists():
            return jsonify({'success': False, 'error': 'Army list not found'}), 404

        filepath.unlink()

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"Error deleting army: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@army_builder_bp.route('/validate', methods=['POST'])
def validate_army():
    """Validate an army roster"""
    try:
        data = request.json
        army_data = data.get('army')

        if not army_data:
            return jsonify({'success': False, 'error': 'No army data provided'}), 400

        errors = []
        warnings = []

        # Check points limit
        total_points = sum(u.get('points_cost', 0) for u in army_data.get('units', []))
        points_limit = army_data.get('points_limit', 2000)

        if total_points > points_limit:
            errors.append(f"Army exceeds points limit: {total_points}/{points_limit}")

        # Check unit limits (max 3 of each datasheet, 6 for Battleline)
        unit_counts = {}
        for unit in army_data.get('units', []):
            unit_id = unit.get('unit_id')
            unit_counts[unit_id] = unit_counts.get(unit_id, 0) + 1

        # TODO: Check against actual unit data to determine max counts

        # Check if army has at least one unit
        if len(army_data.get('units', [])) == 0:
            warnings.append("Army has no units")

        return jsonify({
            'success': True,
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'total_points': total_points,
            'points_limit': points_limit
        })

    except Exception as e:
        logger.error(f"Error validating army: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


def army_to_dict(army: Army) -> Dict:
    """Convert Army object to dictionary"""
    return {
        'name': army.name,
        'faction': army.faction,
        'detachment': army.detachment,
        'points_limit': army.points_limit,
        'units': [
            {
                'unit_id': u.unit_id,
                'unit_name': u.unit_name,
                'faction': u.faction,
                'points_cost': u.points_cost,
                'selected_models': [
                    {
                        'model_id': m.model_id,
                        'model_name': m.model_name,
                        'count': m.count,
                        'selected_weapons': {
                            group: {
                                'name': weapon.weapon_profile.name,
                                'option_id': weapon.option_id
                            }
                            for group, weapon in m.selected_weapons.items()
                        }
                    }
                    for m in u.selected_models
                ],
                'enhancements': u.enhancements
            }
            for u in army.units
        ],
        'created_at': army.created_at,
        'modified_at': army.modified_at
    }

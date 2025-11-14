"""
Battle Mode API
Backend for army-vs-army combat calculations
"""

from flask import Blueprint, request, jsonify
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from combat_engine import CombatSimulator, WeaponAbilities, UnitAbilities, AttackType
from mathhammer.models import Army

logger = logging.getLogger(__name__)

# Create blueprint
battle_mode_bp = Blueprint('battle_mode', __name__, url_prefix='/api/battle')


def filter_weapons_for_combat(weapons: List[Dict], combat_type: str, is_monster_vehicle: bool = False) -> List[Dict]:
    """
    Filter weapons based on combat type and unit type

    Combat types:
    - 'ranged': Shooting phase, not in engagement range
    - 'melee': Fight phase, in engagement range
    - 'ranged_engaged': Shooting phase while in engagement (Monsters/Vehicles only)

    Rules:
    - Ranged combat: All ranged weapons
    - Melee combat: All melee weapons + pistols
    - Ranged while engaged: Only pistols (or all weapons for Monsters/Vehicles with -1 hit)
    """
    filtered = []

    for weapon in weapons:
        weapon_type = weapon.get('type', '').lower()
        keywords = weapon.get('keywords', '').lower()

        if combat_type == 'ranged':
            # Normal ranged combat - all ranged weapons
            if 'ranged' in weapon_type:
                filtered.append(weapon)

        elif combat_type == 'melee':
            # Melee combat - melee weapons and pistols
            if 'melee' in weapon_type:
                filtered.append(weapon)
            elif 'pistol' in keywords:
                # Pistols can be used in melee
                filtered.append(weapon)

        elif combat_type == 'ranged_engaged':
            # Shooting while in engagement range
            if is_monster_vehicle:
                # Monsters/Vehicles can shoot all weapons at -1 hit
                if 'ranged' in weapon_type:
                    weapon_copy = weapon.copy()
                    weapon_copy['hit_modifier'] = -1  # Add -1 to hit
                    filtered.append(weapon_copy)
            else:
                # Normal units can only use pistols
                if 'pistol' in keywords:
                    filtered.append(weapon)

    return filtered


@battle_mode_bp.route('/get-available-weapons', methods=['POST'])
def get_available_weapons():
    """Get weapons available for a unit based on combat type"""
    try:
        data = request.json
        weapons = data.get('weapons', [])
        combat_type = data.get('combat_type', 'ranged')
        categories = data.get('categories', [])

        # Check if unit is Monster or Vehicle
        is_monster_vehicle = any(cat.lower() in ['monster', 'vehicle'] for cat in categories)

        # Filter weapons
        available = filter_weapons_for_combat(weapons, combat_type, is_monster_vehicle)

        return jsonify({
            'success': True,
            'weapons': available,
            'is_monster_vehicle': is_monster_vehicle,
            'note': 'Monsters/Vehicles shoot at -1 hit when engaged' if combat_type == 'ranged_engaged' and is_monster_vehicle else None
        })

    except Exception as e:
        logger.error(f"Error filtering weapons: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@battle_mode_bp.route('/calculate-combat', methods=['POST'])
def calculate_combat():
    """Calculate combat between two units"""
    try:
        data = request.json

        # Attacker data
        attacker_weapon = data.get('attacker_weapon')
        attacker_unit = data.get('attacker_unit')
        combat_type = data.get('combat_type', 'ranged')

        # Defender data
        defender_unit = data.get('defender_unit')

        # Extract weapon stats
        attacks_str = attacker_weapon.get('attacks', '1')
        skill_str = attacker_weapon.get('skill', '3+')
        strength_str = attacker_weapon.get('strength', '4')
        ap_str = attacker_weapon.get('ap', '0')
        damage_str = attacker_weapon.get('damage', '1')
        keywords = attacker_weapon.get('keywords', '').lower()

        # Parse numeric values
        try:
            # Parse attacks (can be dice notation)
            if 'd' in attacks_str.lower():
                num_attacks = 3  # Average for D6
            else:
                num_attacks = int(attacks_str)

            # Parse skill (3+ -> 3)
            skill = int(skill_str.replace('+', ''))

            # Parse strength
            strength = int(strength_str)

            # Parse AP
            ap = int(ap_str) if ap_str else 0

        except ValueError as e:
            return jsonify({'success': False, 'error': f'Invalid weapon stats: {e}'}), 400

        # Extract defender stats
        toughness = defender_unit.get('toughness', 4)
        save = defender_unit.get('save', 3)
        invuln = defender_unit.get('invuln')
        wounds = defender_unit.get('wounds', 2)
        unit_size = defender_unit.get('unit_size', 10)

        # Determine attack type
        attack_type = AttackType.MELEE if combat_type == 'melee' else AttackType.RANGED

        # Parse weapon abilities
        weapon_abilities = WeaponAbilities()

        if 'lethal hits' in keywords:
            weapon_abilities.lethal_hits = True
        if 'devastating wounds' in keywords:
            weapon_abilities.devastating_wounds = True
        if 'twin-linked' in keywords or 'twin' in keywords:
            weapon_abilities.twin_linked = True
        if 'sustained hits' in keywords:
            weapon_abilities.sustained_hits = 1
        if 'torrent' in keywords:
            weapon_abilities.torrent = True
        if 'melta' in keywords:
            weapon_abilities.melta = 2

        # Check for hit modifier (Monster/Vehicle shooting while engaged)
        hit_modifier = attacker_weapon.get('hit_modifier', 0)
        if hit_modifier != 0:
            weapon_abilities.bs_ws_modifier = hit_modifier

        # Parse target abilities
        target_abilities = UnitAbilities()

        defender_keywords = defender_unit.get('keywords', [])
        # TODO: Parse FNP and other defensive abilities from unit data

        # Run simulation
        sim = CombatSimulator()
        result = sim.simulate_attack_sequence(
            num_attacks=num_attacks,
            skill=skill,
            strength=strength,
            ap=ap,
            damage=damage_str,
            toughness=toughness,
            save=save,
            invuln=invuln,
            wounds_per_model=wounds,
            unit_size=unit_size,
            attack_type=attack_type,
            weapon_abilities=weapon_abilities,
            target_abilities=target_abilities,
            attacker_abilities=UnitAbilities()
        )

        # Format result
        return jsonify({
            'success': True,
            'result': {
                'num_attacks': num_attacks,
                'num_hits': result.num_hits,
                'num_critical_hits': result.num_critical_hits,
                'num_wounds': result.num_wounds,
                'num_critical_wounds': result.num_critical_wounds,
                'num_saves_made': result.num_saves_made,
                'num_saves_failed': result.num_saves_failed,
                'total_damage': result.total_damage,
                'damage_after_fnp': result.damage_after_fnp,
                'models_destroyed': result.models_destroyed
            },
            'summary': {
                'attacker': f"{attacker_unit.get('name')} with {attacker_weapon.get('name')}",
                'defender': defender_unit.get('name'),
                'combat_type': combat_type,
                'models_killed': result.models_destroyed,
                'wounds_dealt': result.damage_after_fnp
            }
        })

    except Exception as e:
        logger.error(f"Error calculating combat: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@battle_mode_bp.route('/load-army-for-battle/<filename>', methods=['GET'])
def load_army_for_battle(filename):
    """Load an army roster for battle mode"""
    try:
        from pathlib import Path

        army_lists_dir = Path('army_lists')
        filepath = army_lists_dir / filename

        if not filepath.exists():
            return jsonify({'success': False, 'error': 'Army not found'}), 404

        with open(filepath, 'r', encoding='utf-8') as f:
            army_data = json.load(f)

        return jsonify({
            'success': True,
            'army': army_data
        })

    except Exception as e:
        logger.error(f"Error loading army: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

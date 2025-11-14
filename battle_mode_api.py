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
from stratagems import apply_stratagem_to_combat, get_stratagem_by_id

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
    """Calculate combat between two units with stratagem effects"""
    try:
        data = request.json

        # Attacker data
        attacker_weapon = data.get('attacker_weapon')
        attacker_unit = data.get('attacker_unit')
        combat_type = data.get('combat_type', 'ranged')

        # Defender data
        defender_unit = data.get('defender_unit')

        # Active stratagems
        active_stratagems = data.get('active_stratagems', [])

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

        # Apply stratagem effects
        combat_params = {
            'skill': skill,
            'hit_modifier': hit_modifier,
            'invuln': invuln,
            'has_cover': False,
            'has_precision': False,
            'overwatch_mode': False,
            'command_reroll_available': False,
            'mortal_wounds_bonus': 0
        }

        applied_stratagems = []
        for stratagem_id in active_stratagems:
            stratagem = get_stratagem_by_id(stratagem_id)
            if stratagem:
                combat_params = apply_stratagem_to_combat(stratagem_id, combat_params)
                applied_stratagems.append(stratagem.name)
                logger.info(f"Applied stratagem: {stratagem.name}")

        # Update values from stratagem effects
        skill = combat_params.get('skill', skill)
        hit_modifier = combat_params.get('hit_modifier', hit_modifier)
        invuln = combat_params.get('invuln', invuln)
        mortal_wounds_bonus = combat_params.get('mortal_wounds_bonus', 0)

        # Apply cover bonus if Go to Ground was used
        if combat_params.get('has_cover'):
            target_abilities.cover = True
            target_abilities.cover_bonus = 1

        # Apply Smokescreen hit modifier
        if combat_params.get('hit_modifier', 0) != 0:
            weapon_abilities.bs_ws_modifier = combat_params['hit_modifier']

        # Apply Precision if Epic Challenge was used
        if combat_params.get('has_precision'):
            weapon_abilities.precision = True

        # Run simulation (run multiple times for statistics)
        num_simulations = data.get('num_simulations', 1)
        results = []

        for _ in range(num_simulations):
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
            results.append(result)

        # Calculate average result if multiple simulations
        if num_simulations > 1:
            avg_result = {
                'num_attacks': num_attacks,
                'num_hits': sum(r.num_hits for r in results) / num_simulations,
                'num_critical_hits': sum(r.num_critical_hits for r in results) / num_simulations,
                'num_wounds': sum(r.num_wounds for r in results) / num_simulations,
                'num_critical_wounds': sum(r.num_critical_wounds for r in results) / num_simulations,
                'num_saves_made': sum(r.num_saves_made for r in results) / num_simulations,
                'num_saves_failed': sum(r.num_saves_failed for r in results) / num_simulations,
                'total_damage': sum(r.total_damage for r in results) / num_simulations,
                'damage_after_fnp': sum(r.damage_after_fnp for r in results) / num_simulations,
                'models_destroyed': sum(r.models_destroyed for r in results) / num_simulations,
                'mortal_wounds': mortal_wounds_bonus
            }

            # Calculate statistics
            total_damages = [r.total_damage + mortal_wounds_bonus for r in results]
            models_killed = [r.models_destroyed for r in results]

            stats = {
                'min_damage': min(total_damages),
                'max_damage': max(total_damages),
                'avg_damage': sum(total_damages) / len(total_damages),
                'min_models_killed': min(models_killed),
                'max_models_killed': max(models_killed),
                'avg_models_killed': sum(models_killed) / len(models_killed)
            }
        else:
            # Single simulation
            result = results[0]
            avg_result = {
                'num_attacks': num_attacks,
                'num_hits': result.num_hits,
                'num_critical_hits': result.num_critical_hits,
                'num_wounds': result.num_wounds,
                'num_critical_wounds': result.num_critical_wounds,
                'num_saves_made': result.num_saves_made,
                'num_saves_failed': result.num_saves_failed,
                'total_damage': result.total_damage,
                'damage_after_fnp': result.damage_after_fnp,
                'models_destroyed': result.models_destroyed,
                'mortal_wounds': mortal_wounds_bonus
            }
            stats = None

        # Add mortal wounds to final damage
        final_damage = avg_result['damage_after_fnp'] + mortal_wounds_bonus
        final_models = int(final_damage / wounds) if wounds > 0 else 0

        # Format result
        return jsonify({
            'success': True,
            'result': avg_result,
            'stats': stats,
            'num_simulations': num_simulations,
            'summary': {
                'attacker': f"{attacker_unit.get('name')} with {attacker_weapon.get('name')}",
                'defender': defender_unit.get('name'),
                'combat_type': combat_type,
                'models_killed': final_models,
                'wounds_dealt': final_damage,
                'mortal_wounds': mortal_wounds_bonus
            },
            'stratagems_applied': applied_stratagems
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

"""
Mathhammer calculation engine for Warhammer 40k combat outcomes
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

from .models import Unit, WeaponProfile, UnitProfile

logger = logging.getLogger(__name__)


@dataclass
class AttackResult:
    """Result of an attack calculation"""
    expected_hits: float
    expected_wounds: float
    expected_unsaved_wounds: float
    expected_damage: float
    hit_probability: float
    wound_probability: float
    save_failure_probability: float


@dataclass
class CombatSimulation:
    """Result of a full combat simulation"""
    attacker_name: str
    defender_name: str
    weapon_name: str
    num_attacks: int
    attack_result: AttackResult
    expected_models_killed: float
    defender_models_remaining: float


class MathHammer:
    """Core mathhammer calculation engine"""

    @staticmethod
    def parse_dice_value(value: str) -> float:
        """Parse dice notation (e.g., 'D6', '2D6', 'D3', etc.) into expected value"""
        if not value:
            return 0.0

        value = value.strip().upper()

        # Handle static numbers
        try:
            return float(value)
        except ValueError:
            pass

        # Handle dice notation
        dice_pattern = r'(\d*)D(\d+)'
        match = re.match(dice_pattern, value)

        if match:
            num_dice = int(match.group(1)) if match.group(1) else 1
            dice_sides = int(match.group(2))
            # Expected value of a die is (sides + 1) / 2
            return num_dice * (dice_sides + 1) / 2.0

        # If we can't parse it, return 0
        logger.warning(f"Could not parse dice value: {value}")
        return 0.0

    @staticmethod
    def parse_target_number(value: str) -> int:
        """Parse target number (e.g., '3+' returns 3)"""
        if not value:
            return 7  # Impossible

        value = value.strip().replace('+', '').replace('-', '')

        try:
            return int(value)
        except ValueError:
            logger.warning(f"Could not parse target number: {value}")
            return 7

    @staticmethod
    def calculate_hit_probability(skill: str) -> float:
        """Calculate probability of hitting with given BS/WS"""
        target = MathHammer.parse_target_number(skill)

        if target > 6:
            return 0.0
        if target < 2:
            return 1.0

        # Probability is (7 - target) / 6
        return (7 - target) / 6.0

    @staticmethod
    def calculate_wound_probability(strength: int, toughness: int) -> float:
        """Calculate probability of wounding based on S vs T"""
        if strength == 0 or toughness == 0:
            return 0.0

        if strength >= 2 * toughness:
            target = 2
        elif strength > toughness:
            target = 3
        elif strength == toughness:
            target = 4
        elif strength < toughness and strength * 2 > toughness:
            target = 5
        else:  # strength * 2 <= toughness
            target = 6

        return (7 - target) / 6.0

    @staticmethod
    def calculate_save_probability(save: int, ap: int, invuln: Optional[int] = None) -> float:
        """Calculate probability of making a save"""
        # Apply AP to normal save
        modified_save = save - ap

        # Use invuln if it's better
        if invuln is not None:
            effective_save = min(modified_save, invuln)
        else:
            effective_save = modified_save

        if effective_save > 6:
            return 0.0
        if effective_save < 2:
            return 1.0

        return (7 - effective_save) / 6.0

    @staticmethod
    def calculate_attack_sequence(
        weapon: WeaponProfile,
        attacker: Optional[UnitProfile],
        defender: UnitProfile,
        num_models_attacking: int = 1
    ) -> AttackResult:
        """
        Calculate expected outcomes for a full attack sequence

        Args:
            weapon: The weapon being used
            attacker: The attacking unit profile (optional, needed for context)
            defender: The defending unit profile
            num_models_attacking: Number of models making attacks

        Returns:
            AttackResult with all calculated probabilities and expected values
        """
        # Parse weapon characteristics
        num_attacks = MathHammer.parse_dice_value(weapon.attacks or "1") * num_models_attacking
        skill = weapon.skill or "4+"
        strength = int(MathHammer.parse_dice_value(weapon.strength or "4"))
        ap = abs(int(MathHammer.parse_dice_value(weapon.armor_penetration or "0")))
        damage = MathHammer.parse_dice_value(weapon.damage or "1")

        # Parse defender characteristics
        toughness = int(MathHammer.parse_dice_value(defender.toughness or "4"))
        save = MathHammer.parse_target_number(defender.save or "3+")
        invuln_str = defender.invulnerable_save
        invuln = MathHammer.parse_target_number(invuln_str) if invuln_str else None

        # Calculate probabilities
        hit_prob = MathHammer.calculate_hit_probability(skill)
        wound_prob = MathHammer.calculate_wound_probability(strength, toughness)
        save_prob = MathHammer.calculate_save_probability(save, ap, invuln)
        save_fail_prob = 1.0 - save_prob

        # Calculate expected values through the sequence
        expected_hits = num_attacks * hit_prob
        expected_wounds = expected_hits * wound_prob
        expected_unsaved = expected_wounds * save_fail_prob
        expected_damage = expected_unsaved * damage

        return AttackResult(
            expected_hits=expected_hits,
            expected_wounds=expected_wounds,
            expected_unsaved_wounds=expected_unsaved,
            expected_damage=expected_damage,
            hit_probability=hit_prob,
            wound_probability=wound_prob,
            save_failure_probability=save_fail_prob
        )

    @staticmethod
    def compare_weapons(
        weapons: List[WeaponProfile],
        defender: UnitProfile,
        num_models_attacking: int = 1
    ) -> List[Tuple[str, AttackResult]]:
        """
        Compare effectiveness of multiple weapons against a target

        Returns:
            List of (weapon_name, AttackResult) tuples sorted by expected damage
        """
        results = []

        for weapon in weapons:
            result = MathHammer.calculate_attack_sequence(
                weapon=weapon,
                attacker=None,
                defender=defender,
                num_models_attacking=num_models_attacking
            )
            results.append((weapon.name, result))

        # Sort by expected damage (descending)
        results.sort(key=lambda x: x[1].expected_damage, reverse=True)

        return results

    @staticmethod
    def simulate_combat(
        attacker: Unit,
        defender: Unit,
        attacker_model_count: int = 1,
        defender_model_count: int = 1,
        weapon_name: Optional[str] = None
    ) -> CombatSimulation:
        """
        Simulate a full combat between two units

        Args:
            attacker: Attacking unit
            defender: Defending unit
            attacker_model_count: Number of attacking models
            defender_model_count: Number of defending models
            weapon_name: Specific weapon to use (if None, uses first weapon)

        Returns:
            CombatSimulation with results
        """
        if not attacker.unit_profile or not defender.unit_profile:
            raise ValueError("Both units must have unit profiles")

        # Select weapon
        if weapon_name:
            weapon = attacker.get_weapon_by_name(weapon_name)
            if not weapon:
                raise ValueError(f"Weapon '{weapon_name}' not found on attacker")
        elif attacker.weapons:
            weapon = attacker.weapons[0]
        else:
            raise ValueError("Attacker has no weapons")

        # Calculate attack result
        result = MathHammer.calculate_attack_sequence(
            weapon=weapon,
            attacker=attacker.unit_profile,
            defender=defender.unit_profile,
            num_models_attacking=attacker_model_count
        )

        # Calculate models killed
        defender_wounds = MathHammer.parse_dice_value(defender.unit_profile.wounds or "1")
        expected_models_killed = result.expected_damage / defender_wounds if defender_wounds > 0 else 0
        models_remaining = max(0, defender_model_count - expected_models_killed)

        return CombatSimulation(
            attacker_name=attacker.name,
            defender_name=defender.name,
            weapon_name=weapon.name,
            num_attacks=int(MathHammer.parse_dice_value(weapon.attacks or "1") * attacker_model_count),
            attack_result=result,
            expected_models_killed=expected_models_killed,
            defender_models_remaining=models_remaining
        )

    @staticmethod
    def calculate_points_efficiency(
        attacker: Unit,
        defender: Unit,
        attacker_model_count: int = 1
    ) -> Dict[str, float]:
        """
        Calculate points efficiency of attacks

        Returns:
            Dictionary with efficiency metrics
        """
        if not attacker.weapons:
            return {}

        weapon = attacker.weapons[0]
        result = MathHammer.calculate_attack_sequence(
            weapon=weapon,
            attacker=attacker.unit_profile,
            defender=defender.unit_profile,
            num_models_attacking=attacker_model_count
        )

        defender_wounds = MathHammer.parse_dice_value(defender.unit_profile.wounds or "1")
        models_killed = result.expected_damage / defender_wounds if defender_wounds > 0 else 0

        # Calculate points destroyed
        points_destroyed = models_killed * (defender.points_cost / max(1, attacker_model_count))

        # Calculate efficiency (points destroyed per point spent)
        efficiency = points_destroyed / attacker.points_cost if attacker.points_cost > 0 else 0

        return {
            'expected_damage': result.expected_damage,
            'models_killed': models_killed,
            'points_destroyed': points_destroyed,
            'efficiency': efficiency,
            'damage_per_point': result.expected_damage / attacker.points_cost if attacker.points_cost > 0 else 0
        }

"""
Unit-Specific Ability Parser and Handler
Parses ability descriptions from BSData and applies effects in combat
"""

import re
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class AbilityEffect(Enum):
    """Types of ability effects"""
    REROLL_HITS = "reroll_hits"
    REROLL_WOUNDS = "reroll_wounds"
    ADD_ATTACKS = "add_attacks"
    IMPROVE_STRENGTH = "improve_strength"
    IMPROVE_AP = "improve_ap"
    IMPROVE_DAMAGE = "improve_damage"
    MORTAL_WOUNDS = "mortal_wounds"
    IGNORE_WOUNDS = "ignore_wounds"
    IMPROVE_SAVE = "improve_save"
    IGNORE_AP = "ignore_ap"
    CRITICAL_HITS = "critical_hits"
    CRITICAL_WOUNDS = "critical_wounds"


@dataclass
class AbilityModifier:
    """Represents a parsed ability effect"""
    effect_type: AbilityEffect
    value: any  # Could be int, str, or callable
    condition: Optional[str] = None  # e.g., "when charging", "vs INFANTRY"
    weapon_restriction: Optional[str] = None  # e.g., "bolt rifles"


class UnitAbilityParser:
    """Parses unit ability descriptions into combat modifiers"""

    def __init__(self):
        # Patterns for recognizing ability effects
        self.patterns = [
            # Re-roll patterns
            (r're-roll.*(?:hit|attack|to hit).*roll.*of.*1', AbilityEffect.REROLL_HITS, '1s'),
            (r're-roll.*(?:hit|attack|to hit)', AbilityEffect.REROLL_HITS, 'all'),
            (r're-roll.*wound.*roll.*of.*1', AbilityEffect.REROLL_WOUNDS, '1s'),
            (r're-roll.*wound', AbilityEffect.REROLL_WOUNDS, 'all'),

            # Add to characteristic
            (r'add (\d+) to (?:the )?attacks characteristic', AbilityEffect.ADD_ATTACKS, None),
            (r'add (\d+) to (?:the )?strength characteristic', AbilityEffect.IMPROVE_STRENGTH, None),
            (r'\+(\d+) to (?:the )?ap characteristic', AbilityEffect.IMPROVE_AP, None),
            (r'\+(\d+) to (?:the )?damage characteristic', AbilityEffect.IMPROVE_DAMAGE, None),

            # Mortal wounds
            (r'inflict.*(\d+).*mortal wound', AbilityEffect.MORTAL_WOUNDS, None),
            (r'(\d+).*mortal wound.*on.*(?:unmodified|critical).*(?:hit|wound).*(?:roll|of).*(\d+)',
             AbilityEffect.MORTAL_WOUNDS, None),

            # Save/damage reduction
            (r'halve (?:the )?damage characteristic', AbilityEffect.IGNORE_WOUNDS, '0.5'),
            (r'reduce.*damage.*by (\d+)', AbilityEffect.IGNORE_WOUNDS, None),
            (r'invulnerable save.*(\d+)\+', AbilityEffect.IMPROVE_SAVE, None),

            # Critical effects
            (r'critical.*hit.*on.*(?:unmodified|roll).*(?:of )?(\d+)\+', AbilityEffect.CRITICAL_HITS, None),
            (r'critical.*wound.*on.*(?:unmodified|roll).*(?:of )?(\d+)\+', AbilityEffect.CRITICAL_WOUNDS, None),
        ]

    def parse_ability(self, name: str, description: str) -> List[AbilityModifier]:
        """Parse an ability description into modifiers"""
        modifiers = []

        if not description:
            return modifiers

        desc_lower = description.lower()

        for pattern, effect_type, default_value in self.patterns:
            match = re.search(pattern, desc_lower)
            if match:
                # Extract value from pattern if it has a capture group
                if match.groups():
                    value = match.group(1)
                    try:
                        value = int(value)
                    except ValueError:
                        pass
                else:
                    value = default_value

                # Check for conditions
                condition = None
                if 'when charging' in desc_lower or 'charge' in desc_lower:
                    condition = 'charging'
                elif 'melee' in desc_lower:
                    condition = 'melee'
                elif 'ranged' in desc_lower or 'shooting' in desc_lower:
                    condition = 'ranged'

                # Check for weapon restrictions
                weapon_restriction = None
                weapon_match = re.search(r'(?:of |equipped by |with )([\w\s]+)(?:\s+equipped|$)', desc_lower)
                if weapon_match:
                    weapon_restriction = weapon_match.group(1).strip()

                modifier = AbilityModifier(
                    effect_type=effect_type,
                    value=value,
                    condition=condition,
                    weapon_restriction=weapon_restriction
                )

                modifiers.append(modifier)

        return modifiers

    def get_known_abilities(self) -> Dict[str, List[AbilityModifier]]:
        """Returns hardcoded definitions for common known abilities"""
        return {
            # Space Marine abilities
            'Shock Assault': [
                AbilityModifier(AbilityEffect.REROLL_WOUNDS, '1s', condition='melee')
            ],

            'Target Elimination': [
                AbilityModifier(AbilityEffect.ADD_ATTACKS, 2, weapon_restriction='bolt rifle')
            ],

            'Refuse to Yield': [
                AbilityModifier(AbilityEffect.IGNORE_WOUNDS, 0.5)
            ],

            'Objective Secured': [],  # No combat effect

            'Oath of Moment': [
                AbilityModifier(AbilityEffect.REROLL_HITS, 'all')
            ],

            # Generic pattern-based abilities
            'Devastating Wounds': [
                AbilityModifier(AbilityEffect.CRITICAL_WOUNDS, 6)
            ],

            'Lethal Hits': [
                AbilityModifier(AbilityEffect.CRITICAL_HITS, 6)
            ],

            'Sustained Hits': [
                AbilityModifier(AbilityEffect.CRITICAL_HITS, 6)
            ],

            'Twin-linked': [
                AbilityModifier(AbilityEffect.REROLL_WOUNDS, 'all')
            ],
        }


class AbilityApplicator:
    """Applies ability modifiers to combat calculations"""

    @staticmethod
    def apply_to_attacks(modifiers: List[AbilityModifier], base_attacks: int, **context) -> int:
        """Apply modifiers that affect attack count"""
        attacks = base_attacks

        for mod in modifiers:
            if mod.effect_type == AbilityEffect.ADD_ATTACKS:
                # Check weapon restriction
                if mod.weapon_restriction:
                    weapon_name = context.get('weapon_name', '').lower()
                    if mod.weapon_restriction not in weapon_name:
                        continue

                attacks += mod.value

        return attacks

    @staticmethod
    def apply_to_strength(modifiers: List[AbilityModifier], base_strength: int, **context) -> int:
        """Apply modifiers that affect strength"""
        strength = base_strength

        for mod in modifiers:
            if mod.effect_type == AbilityEffect.IMPROVE_STRENGTH:
                strength += mod.value

        return strength

    @staticmethod
    def apply_to_ap(modifiers: List[AbilityModifier], base_ap: int, **context) -> int:
        """Apply modifiers that affect AP"""
        ap = base_ap

        for mod in modifiers:
            if mod.effect_type == AbilityEffect.IMPROVE_AP:
                ap += mod.value  # Note: AP is negative, so this makes it worse

        return ap

    @staticmethod
    def apply_to_damage(modifiers: List[AbilityModifier], base_damage: int, **context) -> float:
        """Apply modifiers that affect damage"""
        damage = float(base_damage)

        for mod in modifiers:
            if mod.effect_type == AbilityEffect.IMPROVE_DAMAGE:
                damage += mod.value
            elif mod.effect_type == AbilityEffect.IGNORE_WOUNDS:
                # Defender ability - reduces damage
                if isinstance(mod.value, float):
                    damage *= mod.value
                else:
                    damage -= mod.value
                damage = max(0, damage)

        return damage

    @staticmethod
    def get_reroll_type(modifiers: List[AbilityModifier], roll_type: str, **context) -> Optional[str]:
        """Determine if hits/wounds should be rerolled"""
        attack_type = context.get('attack_type', 'ranged')

        for mod in modifiers:
            # Check hit rerolls
            if roll_type == 'hit' and mod.effect_type == AbilityEffect.REROLL_HITS:
                # Check conditions
                if mod.condition and mod.condition != attack_type:
                    continue

                return mod.value  # 'all', '1s', or specific value

            # Check wound rerolls
            elif roll_type == 'wound' and mod.effect_type == AbilityEffect.REROLL_WOUNDS:
                if mod.condition and mod.condition != attack_type:
                    continue

                return mod.value

        return None

    @staticmethod
    def get_critical_threshold(modifiers: List[AbilityModifier], roll_type: str) -> int:
        """Get the critical roll threshold (default 6)"""
        threshold = 6

        for mod in modifiers:
            if roll_type == 'hit' and mod.effect_type == AbilityEffect.CRITICAL_HITS:
                if isinstance(mod.value, int):
                    threshold = min(threshold, mod.value)

            elif roll_type == 'wound' and mod.effect_type == AbilityEffect.CRITICAL_WOUNDS:
                if isinstance(mod.value, int):
                    threshold = min(threshold, mod.value)

        return threshold


# Global parser instance
ability_parser = UnitAbilityParser()
ability_applicator = AbilityApplicator()

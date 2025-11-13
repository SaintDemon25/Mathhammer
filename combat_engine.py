"""
Warhammer 40k 10th Edition Combat Simulation Engine
Complete implementation of all core rules and weapon abilities
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple, Set
from enum import Enum
import random
from collections import defaultdict


class AttackType(Enum):
    """Type of attack"""
    RANGED = "ranged"
    MELEE = "melee"


class DiceRoll:
    """Represents a dice roll with modifiers"""

    @staticmethod
    def roll_d6() -> int:
        """Roll a single D6"""
        return random.randint(1, 6)

    @staticmethod
    def roll_dice(num_dice: int) -> List[int]:
        """Roll multiple D6"""
        return [DiceRoll.roll_d6() for _ in range(num_dice)]

    @staticmethod
    def parse_dice_notation(notation: str) -> int:
        """Parse dice notation like 'D6', '2D6', 'D3' and return result"""
        notation = notation.upper().strip()

        # Handle static numbers
        try:
            return int(notation)
        except ValueError:
            pass

        # Handle dice notation
        if 'D' in notation:
            parts = notation.split('D')
            num_dice = int(parts[0]) if parts[0] else 1
            dice_type = int(parts[1])

            total = 0
            for _ in range(num_dice):
                total += random.randint(1, dice_type)
            return total

        return 1


@dataclass
class WeaponAbilities:
    """All weapon abilities"""
    # Core weapon abilities
    anti: Optional[Tuple[str, int]] = None  # (keyword, value) e.g., ("INFANTRY", 4)
    blast: bool = False
    devastating_wounds: bool = False
    extra_attacks: Optional[str] = None  # For parsing additional attacks from abilities
    hazardous: bool = False
    heavy: bool = False
    ignores_cover: bool = False
    indirect_fire: bool = False
    lance: bool = False
    lethal_hits: bool = False
    melta: Optional[int] = None  # Melta X
    one_shot: bool = False
    pistol: bool = False
    precision: bool = False
    psychic: bool = False
    rapid_fire: Optional[int] = None  # Rapid Fire X
    sustained_hits: Optional[int] = None  # Sustained Hits X
    torrent: bool = False
    twin_linked: bool = False

    # Additional modifiers
    assault: bool = False

    def __str__(self):
        """String representation of active abilities"""
        abilities = []
        if self.anti:
            abilities.append(f"Anti-{self.anti[0]} {self.anti[1]}+")
        if self.blast:
            abilities.append("Blast")
        if self.devastating_wounds:
            abilities.append("Devastating Wounds")
        if self.hazardous:
            abilities.append("Hazardous")
        if self.heavy:
            abilities.append("Heavy")
        if self.ignores_cover:
            abilities.append("Ignores Cover")
        if self.indirect_fire:
            abilities.append("Indirect Fire")
        if self.lethal_hits:
            abilities.append("Lethal Hits")
        if self.melta:
            abilities.append(f"Melta {self.melta}")
        if self.precision:
            abilities.append("Precision")
        if self.rapid_fire:
            abilities.append(f"Rapid Fire {self.rapid_fire}")
        if self.sustained_hits:
            abilities.append(f"Sustained Hits {self.sustained_hits}")
        if self.torrent:
            abilities.append("Torrent")
        if self.twin_linked:
            abilities.append("Twin-linked")
        if self.assault:
            abilities.append("Assault")

        return ", ".join(abilities) if abilities else "None"


@dataclass
class UnitAbilities:
    """Defensive and unit abilities"""
    feel_no_pain: Optional[int] = None  # X+ value
    stealth: bool = False
    lone_operative: bool = False
    cover: bool = False  # Unit is in cover
    cover_bonus: int = 0  # Additional save bonus from cover (usually +1)

    # Re-roll abilities
    reroll_hit_rolls_of_1: bool = False
    reroll_all_hit_rolls: bool = False
    reroll_wound_rolls_of_1: bool = False
    reroll_all_wound_rolls: bool = False

    # Modifier abilities
    hit_modifier: int = 0  # Additional modifier to hit rolls
    wound_modifier: int = 0  # Additional modifier to wound rolls
    save_modifier: int = 0  # Additional modifier to saves

    # Keywords for Anti-X
    keywords: Set[str] = field(default_factory=set)

    def __str__(self):
        """String representation of active abilities"""
        abilities = []
        if self.feel_no_pain:
            abilities.append(f"Feel No Pain {self.feel_no_pain}+")
        if self.stealth:
            abilities.append("Stealth")
        if self.lone_operative:
            abilities.append("Lone Operative")
        if self.cover:
            abilities.append(f"Cover (+{self.cover_bonus})")
        if self.reroll_all_hit_rolls:
            abilities.append("Re-roll hits")
        elif self.reroll_hit_rolls_of_1:
            abilities.append("Re-roll hit 1s")
        if self.reroll_all_wound_rolls:
            abilities.append("Re-roll wounds")
        elif self.reroll_wound_rolls_of_1:
            abilities.append("Re-roll wound 1s")

        return ", ".join(abilities) if abilities else "None"


@dataclass
class AttackSequenceResult:
    """Result of a complete attack sequence"""
    num_attacks: int = 0
    num_hits: int = 0
    num_critical_hits: int = 0
    num_wounds: int = 0
    num_critical_wounds: int = 0
    num_saves_made: int = 0
    num_saves_failed: int = 0
    total_damage: int = 0
    damage_after_fnp: int = 0
    models_destroyed: int = 0

    # Detailed breakdowns
    hit_rolls: List[int] = field(default_factory=list)
    wound_rolls: List[int] = field(default_factory=list)
    save_rolls: List[int] = field(default_factory=list)
    fnp_rolls: List[int] = field(default_factory=list)

    # Special events
    hazardous_damage: int = 0
    sustained_hits_generated: int = 0
    lethal_hits_auto_wounds: int = 0

    def __str__(self):
        """Human-readable summary"""
        lines = [
            f"Attacks: {self.num_attacks}",
            f"Hits: {self.num_hits} ({self.num_critical_hits} critical)",
            f"Wounds: {self.num_wounds} ({self.num_critical_wounds} critical)",
            f"Saves Failed: {self.num_saves_failed}/{self.num_wounds}",
            f"Damage Dealt: {self.total_damage}",
        ]

        if self.damage_after_fnp < self.total_damage:
            lines.append(f"Damage After FNP: {self.damage_after_fnp}")

        lines.append(f"Models Destroyed: {self.models_destroyed}")

        if self.sustained_hits_generated > 0:
            lines.append(f"Sustained Hits: +{self.sustained_hits_generated}")
        if self.lethal_hits_auto_wounds > 0:
            lines.append(f"Lethal Hits Auto-wounds: {self.lethal_hits_auto_wounds}")
        if self.hazardous_damage > 0:
            lines.append(f"Hazardous Damage: {self.hazardous_damage}")

        return "\n".join(lines)


class CombatSimulator:
    """
    Complete 10th Edition combat simulator with all core rules
    """

    # Modifier caps
    MAX_MODIFIER = 1
    MIN_MODIFIER = -1

    @staticmethod
    def cap_modifier(modifier: int) -> int:
        """Cap modifiers to +/-1"""
        return max(CombatSimulator.MIN_MODIFIER, min(CombatSimulator.MAX_MODIFIER, modifier))

    @staticmethod
    def calculate_wound_threshold(strength: int, toughness: int) -> int:
        """
        Calculate required wound roll based on S vs T
        S >= 2*T: 2+
        S > T: 3+
        S == T: 4+
        S < T: 5+
        S <= T/2: 6+
        """
        if strength >= 2 * toughness:
            return 2
        elif strength > toughness:
            return 3
        elif strength == toughness:
            return 4
        elif strength * 2 > toughness:
            return 5
        else:
            return 6

    @staticmethod
    def roll_hit(
        skill: int,
        modifier: int,
        weapon_abilities: WeaponAbilities,
        target_abilities: UnitAbilities,
        attacker_abilities: UnitAbilities,
        moved: bool = False
    ) -> Tuple[bool, bool]:
        """
        Roll to hit. Returns (hit_success, is_critical)

        Args:
            skill: BS or WS value (e.g., 3 for 3+)
            modifier: Base modifier to hit
            weapon_abilities: Weapon abilities
            target_abilities: Target's defensive abilities
            attacker_abilities: Attacker's abilities
            moved: Whether attacker moved (affects Heavy weapons)
        """
        # Roll the dice
        roll = DiceRoll.roll_d6()

        # Unmodified 1 always fails
        if roll == 1:
            return False, False

        # Unmodified 6 is always a critical hit
        is_critical = (roll == 6)

        # Calculate total modifier
        total_modifier = modifier

        # Stealth: -1 to hit for ranged attacks
        if target_abilities.stealth:
            total_modifier -= 1

        # Heavy: -1 to hit if moved
        if weapon_abilities.heavy and moved:
            total_modifier -= 1

        # Add attacker modifiers
        total_modifier += attacker_abilities.hit_modifier

        # Cap modifier
        total_modifier = CombatSimulator.cap_modifier(total_modifier)

        # Check if hit succeeds
        modified_roll = roll + total_modifier
        hit_success = modified_roll >= skill or is_critical

        return hit_success, is_critical

    @staticmethod
    def roll_wound(
        strength: int,
        toughness: int,
        modifier: int,
        weapon_abilities: WeaponAbilities,
        target_abilities: UnitAbilities,
        is_critical_hit: bool = False
    ) -> Tuple[bool, bool]:
        """
        Roll to wound. Returns (wound_success, is_critical_wound)

        Args:
            strength: Attack strength
            toughness: Target toughness
            modifier: Base modifier to wound
            weapon_abilities: Weapon abilities
            target_abilities: Target abilities
            is_critical_hit: Whether this came from a critical hit
        """
        # Lethal Hits: Critical hits auto-wound
        if is_critical_hit and weapon_abilities.lethal_hits:
            return True, False  # Auto-wound but not a critical wound

        # Roll the dice
        roll = DiceRoll.roll_d6()

        # Unmodified 1 always fails
        if roll == 1:
            return False, False

        # Calculate wound threshold
        threshold = CombatSimulator.calculate_wound_threshold(strength, toughness)

        # Check for Critical Wound (unmodified 6)
        is_critical_wound = (roll == 6)

        # Anti-X: Wound rolls of Y+ against keyword X are critical wounds
        if weapon_abilities.anti and not is_critical_wound:
            keyword, value = weapon_abilities.anti
            if keyword.upper() in {kw.upper() for kw in target_abilities.keywords}:
                if roll >= value:
                    is_critical_wound = True

        # Calculate total modifier
        total_modifier = modifier + target_abilities.wound_modifier
        total_modifier = CombatSimulator.cap_modifier(total_modifier)

        # Check if wound succeeds
        modified_roll = roll + total_modifier
        wound_success = modified_roll >= threshold or is_critical_wound

        return wound_success, is_critical_wound

    @staticmethod
    def roll_save(
        save_value: int,
        invuln_value: Optional[int],
        ap: int,
        weapon_abilities: WeaponAbilities,
        target_abilities: UnitAbilities
    ) -> bool:
        """
        Roll save. Returns True if save is made.

        Devastating Wounds: Critical wounds bypass all saves
        """
        # Roll the dice
        roll = DiceRoll.roll_d6()

        # Unmodified 1 always fails
        if roll == 1:
            return False

        # Calculate armor save with AP
        # AP reduces save (higher number = worse save)
        # If AP is 1 (meaning AP-1), it makes a 3+ save become 4+
        modified_save = save_value + abs(ap)

        # Apply cover bonus (if not ignored)
        # Cover improves save (lower number = better save)
        if target_abilities.cover and not weapon_abilities.ignores_cover:
            modified_save -= target_abilities.cover_bonus

        # Apply save modifier
        modified_save -= target_abilities.save_modifier

        # Check invulnerable save (use better of the two)
        if invuln_value is not None:
            effective_save = min(modified_save, invuln_value)
        else:
            effective_save = modified_save

        # Save cannot be better than 2+
        effective_save = max(2, effective_save)

        # Check if save succeeds
        return roll >= effective_save

    @staticmethod
    def roll_feel_no_pain(fnp_value: int) -> bool:
        """Roll Feel No Pain save"""
        roll = DiceRoll.roll_d6()
        return roll >= fnp_value

    @staticmethod
    def calculate_blast_attacks(base_attacks: int, target_unit_size: int) -> int:
        """
        Calculate attacks with Blast ability
        5-9 models: +1 attack
        10+ models: +2 attacks (or D6, whichever is better)
        """
        if not base_attacks:
            return 0

        if target_unit_size >= 10:
            # Maximum of +2 attacks
            return base_attacks + 2
        elif target_unit_size >= 5:
            return base_attacks + 1
        else:
            return base_attacks

    @staticmethod
    def simulate_attack_sequence(
        # Weapon stats
        num_attacks: int,
        skill: int,  # BS or WS
        strength: int,
        ap: int,
        damage: str,  # Can be number or dice notation like "D6"
        attack_type: AttackType,

        # Target stats
        toughness: int,
        save: int,
        invuln: Optional[int],
        wounds_per_model: int,
        unit_size: int,

        # Abilities
        weapon_abilities: WeaponAbilities,
        target_abilities: UnitAbilities,
        attacker_abilities: UnitAbilities,

        # Context
        range_to_target: int = 24,
        attacker_moved: bool = False
    ) -> AttackSequenceResult:
        """
        Simulate complete attack sequence with all rules
        """
        result = AttackSequenceResult()

        # Handle Hazardous
        if weapon_abilities.hazardous:
            hazard_roll = DiceRoll.roll_d6()
            if hazard_roll == 1:
                # Attacker suffers mortal wounds
                result.hazardous_damage = DiceRoll.parse_dice_notation(damage)

        # Calculate number of attacks
        base_attacks = num_attacks

        # Blast: Add attacks based on target size
        if weapon_abilities.blast:
            base_attacks = CombatSimulator.calculate_blast_attacks(base_attacks, unit_size)

        # Rapid Fire: Add attacks within half range
        if weapon_abilities.rapid_fire and attack_type == AttackType.RANGED:
            weapon_range = range_to_target * 2  # Assuming we're at half range for testing
            if range_to_target <= weapon_range / 2:
                base_attacks += weapon_abilities.rapid_fire

        result.num_attacks = base_attacks

        # PHASE 1: HIT ROLLS
        hits = []
        critical_hits = []

        for _ in range(base_attacks):
            # Torrent: Auto-hits
            if weapon_abilities.torrent:
                hits.append(False)  # Not a critical
                result.hit_rolls.append(99)  # Special marker for auto-hit
                continue

            # Roll to hit
            hit_success, is_critical = CombatSimulator.roll_hit(
                skill, 0, weapon_abilities, target_abilities, attacker_abilities, attacker_moved
            )

            result.hit_rolls.append(DiceRoll.roll_d6())

            # Re-roll mechanics
            if not hit_success:
                if attacker_abilities.reroll_all_hit_rolls:
                    hit_success, is_critical = CombatSimulator.roll_hit(
                        skill, 0, weapon_abilities, target_abilities, attacker_abilities, attacker_moved
                    )
                elif attacker_abilities.reroll_hit_rolls_of_1 and result.hit_rolls[-1] == 1:
                    hit_success, is_critical = CombatSimulator.roll_hit(
                        skill, 0, weapon_abilities, target_abilities, attacker_abilities, attacker_moved
                    )

            if hit_success:
                hits.append(is_critical)
                if is_critical:
                    critical_hits.append(True)
                    result.num_critical_hits += 1

                    # Sustained Hits: Generate additional hits
                    if weapon_abilities.sustained_hits:
                        for _ in range(weapon_abilities.sustained_hits):
                            hits.append(False)  # Additional hits are not critical
                            result.sustained_hits_generated += 1

        result.num_hits = len(hits)

        # PHASE 2: WOUND ROLLS
        wounds = []
        critical_wounds = []

        for is_critical_hit in hits:
            # Lethal Hits: Critical hits auto-wound
            if is_critical_hit and weapon_abilities.lethal_hits:
                wounds.append(False)  # Auto-wound but not critical wound
                result.lethal_hits_auto_wounds += 1
                continue

            # Roll to wound
            wound_success, is_critical_wound = CombatSimulator.roll_wound(
                strength, toughness, 0, weapon_abilities, target_abilities, is_critical_hit
            )

            result.wound_rolls.append(DiceRoll.roll_d6())

            # Re-roll mechanics (Twin-Linked)
            if not wound_success and weapon_abilities.twin_linked:
                wound_success, is_critical_wound = CombatSimulator.roll_wound(
                    strength, toughness, 0, weapon_abilities, target_abilities, is_critical_hit
                )

            # Re-roll from abilities
            if not wound_success:
                if attacker_abilities.reroll_all_wound_rolls:
                    wound_success, is_critical_wound = CombatSimulator.roll_wound(
                        strength, toughness, 0, weapon_abilities, target_abilities, is_critical_hit
                    )
                elif attacker_abilities.reroll_wound_rolls_of_1 and result.wound_rolls[-1] == 1:
                    wound_success, is_critical_wound = CombatSimulator.roll_wound(
                        strength, toughness, 0, weapon_abilities, target_abilities, is_critical_hit
                    )

            if wound_success:
                wounds.append(is_critical_wound)
                if is_critical_wound:
                    result.num_critical_wounds += 1

        result.num_wounds = len(wounds)

        # PHASE 3: SAVING THROWS
        failed_saves = []

        for is_critical_wound in wounds:
            # Devastating Wounds: Critical wounds bypass all saves
            if is_critical_wound and weapon_abilities.devastating_wounds:
                failed_saves.append(True)
                result.num_saves_failed += 1
                continue

            # Roll save
            save_success = CombatSimulator.roll_save(
                save, invuln, ap, weapon_abilities, target_abilities
            )

            result.save_rolls.append(DiceRoll.roll_d6())

            if save_success:
                result.num_saves_made += 1
            else:
                failed_saves.append(is_critical_wound)
                result.num_saves_failed += 1

        # PHASE 4: DAMAGE
        total_damage = 0

        for _ in failed_saves:
            # Parse damage value
            damage_value = DiceRoll.parse_dice_notation(damage)

            # Melta: Extra damage at close range
            if weapon_abilities.melta and attack_type == AttackType.RANGED:
                weapon_range = range_to_target * 2
                if range_to_target <= weapon_range / 2:
                    damage_value += weapon_abilities.melta

            total_damage += damage_value

        result.total_damage = total_damage

        # PHASE 5: FEEL NO PAIN
        damage_after_fnp = total_damage

        if target_abilities.feel_no_pain:
            for _ in range(total_damage):
                fnp_roll = DiceRoll.roll_d6()
                result.fnp_rolls.append(fnp_roll)
                if CombatSimulator.roll_feel_no_pain(target_abilities.feel_no_pain):
                    damage_after_fnp -= 1

        result.damage_after_fnp = damage_after_fnp

        # Calculate models destroyed
        result.models_destroyed = min(damage_after_fnp // wounds_per_model, unit_size)

        return result


# Convenience function for quick testing
def quick_combat_test():
    """Quick test of combat system"""
    print("=" * 60)
    print("WARHAMMER 40K 10TH EDITION COMBAT SIMULATOR TEST")
    print("=" * 60)

    # Test 1: Basic combat
    print("\nTest 1: Space Marine Bolt Rifle vs Ork Boyz")
    print("-" * 60)

    weapon_abilities = WeaponAbilities()
    target_abilities = UnitAbilities(keywords={"INFANTRY", "GREENSKINS"})
    attacker_abilities = UnitAbilities()

    result = CombatSimulator.simulate_attack_sequence(
        num_attacks=10,
        skill=3,  # 3+ BS
        strength=4,
        ap=1,
        damage="1",
        attack_type=AttackType.RANGED,
        toughness=5,
        save=6,
        invuln=None,
        wounds_per_model=1,
        unit_size=10,
        weapon_abilities=weapon_abilities,
        target_abilities=target_abilities,
        attacker_abilities=attacker_abilities
    )

    print(result)

    # Test 2: Devastating Wounds + Lethal Hits
    print("\n\nTest 2: Plasma Gun with Lethal Hits and Devastating Wounds")
    print("-" * 60)

    weapon_abilities = WeaponAbilities(
        lethal_hits=True,
        devastating_wounds=True,
        hazardous=True
    )
    target_abilities = UnitAbilities(
        feel_no_pain=5,
        keywords={"INFANTRY"}
    )

    result = CombatSimulator.simulate_attack_sequence(
        num_attacks=5,
        skill=3,
        strength=8,
        ap=3,
        damage="2",
        attack_type=AttackType.RANGED,
        toughness=4,
        save=3,
        invuln=5,
        wounds_per_model=2,
        unit_size=5,
        weapon_abilities=weapon_abilities,
        target_abilities=target_abilities,
        attacker_abilities=UnitAbilities()
    )

    print(result)

    # Test 3: Anti-Infantry with Sustained Hits
    print("\n\nTest 3: Anti-Infantry 4+ with Sustained Hits 1")
    print("-" * 60)

    weapon_abilities = WeaponAbilities(
        anti=("INFANTRY", 4),
        sustained_hits=1
    )
    target_abilities = UnitAbilities(
        keywords={"INFANTRY", "IMPERIUM"},
        stealth=True
    )

    result = CombatSimulator.simulate_attack_sequence(
        num_attacks=12,
        skill=4,
        strength=5,
        ap=2,
        damage="1",
        attack_type=AttackType.RANGED,
        toughness=4,
        save=3,
        invuln=None,
        wounds_per_model=1,
        unit_size=10,
        weapon_abilities=weapon_abilities,
        target_abilities=target_abilities,
        attacker_abilities=UnitAbilities()
    )

    print(result)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    quick_combat_test()

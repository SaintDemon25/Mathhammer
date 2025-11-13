#!/usr/bin/env python3
"""
Test script for unit ability parser
Verifies that ability descriptions are correctly parsed into modifiers
"""

from unit_abilities import UnitAbilityParser, AbilityEffect, AbilityApplicator


def test_ability_parsing():
    """Test parsing of various ability descriptions"""
    parser = UnitAbilityParser()

    print("="*80)
    print("UNIT ABILITY PARSER TEST")
    print("="*80)

    test_cases = [
        ("Shock Assault", "Each time a model in this unit targets an enemy unit with a melee attack, re-roll a Wound roll of 1."),
        ("Target Elimination", "Add 2 to the Attacks characteristic of bolt rifles equipped by models in this unit"),
        ("Oath of Moment", "Each time a model in this unit makes an attack, re-roll a Hit roll of 1"),
        ("Devastating Ability", "Critical Wound rolls inflict 3 mortal wounds"),
        ("Refuse to Yield", "Each time an attack is allocated to this model, halve the Damage characteristic of that attack"),
    ]

    for name, description in test_cases:
        print(f"\n{'-'*80}")
        print(f"Ability: {name}")
        print(f"Description: {description[:100]}...")

        modifiers = parser.parse_ability(name, description)

        if modifiers:
            print(f"✓ Parsed {len(modifiers)} modifier(s):")
            for mod in modifiers:
                print(f"  • {mod.effect_type.value}: {mod.value}")
                if mod.condition:
                    print(f"    Condition: {mod.condition}")
                if mod.weapon_restriction:
                    print(f"    Weapon: {mod.weapon_restriction}")
        else:
            print("  No modifiers parsed")


def test_known_abilities():
    """Test known ability definitions"""
    parser = UnitAbilityParser()
    known = parser.get_known_abilities()

    print(f"\n{'='*80}")
    print(f"KNOWN ABILITIES ({len(known)})")
    print(f"{'='*80}")

    for name, modifiers in known.items():
        if modifiers:
            print(f"\n{name}:")
            for mod in modifiers:
                print(f"  • {mod.effect_type.value}: {mod.value}")
        else:
            print(f"\n{name}: (no combat effect)")


def test_ability_application():
    """Test applying ability modifiers"""
    print(f"\n{'='*80}")
    print("ABILITY APPLICATION TEST")
    print(f"{'='*80}")

    parser = UnitAbilityParser()
    applicator = AbilityApplicator()
    known = parser.get_known_abilities()

    # Test Target Elimination
    print("\nTest: Target Elimination (should add 2 attacks to bolt rifles)")
    mods = known['Target Elimination']
    base_attacks = 2

    attacks_bolt_rifle = applicator.apply_to_attacks(mods, base_attacks, weapon_name="Bolt Rifle")
    attacks_other = applicator.apply_to_attacks(mods, base_attacks, weapon_name="Plasma Gun")

    print(f"  Base attacks: {base_attacks}")
    print(f"  With Bolt Rifle: {attacks_bolt_rifle} {'✓' if attacks_bolt_rifle == 4 else '✗'}")
    print(f"  With Plasma Gun: {attacks_other} {'✓' if attacks_other == 2 else '✗'}")

    # Test Refuse to Yield
    print("\nTest: Refuse to Yield (should halve damage)")
    mods = known['Refuse to Yield']
    base_damage = 3

    reduced_damage = applicator.apply_to_damage(mods, base_damage)

    print(f"  Base damage: {base_damage}")
    print(f"  After Refuse to Yield: {reduced_damage} {'✓' if reduced_damage == 1.5 else '✗'}")

    # Test Shock Assault
    print("\nTest: Shock Assault (should re-roll wound 1s in melee)")
    mods = known['Shock Assault']

    reroll = applicator.get_reroll_type(mods, 'wound', attack_type='melee')

    print(f"  Re-roll type: {reroll} {'✓' if reroll == '1s' else '✗'}")


def main():
    test_ability_parsing()
    test_known_abilities()
    test_ability_application()

    print(f"\n{'='*80}")
    print("✅ ALL TESTS COMPLETED")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()

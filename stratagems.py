"""
Warhammer 40k 10th Edition Stratagems System
Includes core stratagems and their effects
"""
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class StratagemPhase(Enum):
    """When a stratagem can be used"""
    COMMAND = "Command Phase"
    MOVEMENT = "Movement Phase"
    SHOOTING = "Shooting Phase"
    CHARGE = "Charge Phase"
    FIGHT = "Fight Phase"
    ANY = "Any Phase"
    OPPONENT_MOVEMENT = "Opponent's Movement Phase"
    OPPONENT_CHARGE = "Opponent's Charge Phase"
    OPPONENT_SHOOTING = "Opponent's Shooting Phase"


@dataclass
class Stratagem:
    """Represents a stratagem with its rules and effects"""
    id: str
    name: str
    cp_cost: int
    phase: StratagemPhase
    description: str
    effect: str
    restrictions: str = ""
    is_core: bool = True  # Core vs Detachment stratagem
    faction: str = ""  # Empty for core stratagems


# Core Stratagems (Available to all armies)
CORE_STRATAGEMS = [
    Stratagem(
        id="command_reroll",
        name="Command Re-roll",
        cp_cost=1,
        phase=StratagemPhase.ANY,
        description="Re-roll one Hit roll, Wound roll, Damage roll, saving throw, Advance roll, Charge roll, Desperate Escape test, Hazardous test, or the number of attacks made by a weapon.",
        effect="reroll_one_die",
        restrictions="Can be used once per Command Phase"
    ),
    Stratagem(
        id="fire_overwatch",
        name="Fire Overwatch",
        cp_cost=1,
        phase=StratagemPhase.OPPONENT_MOVEMENT,
        description="When an enemy unit moves or charges, one of your units within 24\" can shoot at that enemy unit (hits on 6s only).",
        effect="overwatch_shooting",
        restrictions="Can only use this Stratagem once per turn. Unit must be eligible to shoot."
    ),
    Stratagem(
        id="go_to_ground",
        name="Go to Ground",
        cp_cost=1,
        phase=StratagemPhase.OPPONENT_SHOOTING,
        description="One Infantry unit gains the Benefit of Cover and a 6+ Invulnerable save against shooting attacks this phase.",
        effect="cover_and_invuln",
        restrictions="Infantry unit only. Use when targeted by shooting."
    ),
    Stratagem(
        id="tank_shock",
        name="Tank Shock",
        cp_cost=1,
        phase=StratagemPhase.CHARGE,
        description="After a Vehicle charges, pick one melee weapon and one enemy unit engaged. Roll D6 equal to weapon's Strength (add 2D6 if S > T). Each 5+ inflicts one mortal wound (max 6).",
        effect="charge_mortal_wounds",
        restrictions="Vehicle unit only. Use after charging."
    ),
    Stratagem(
        id="grenades",
        name="Grenades",
        cp_cost=1,
        phase=StratagemPhase.SHOOTING,
        description="Pick an enemy unit within 8\" of one of your units with Grenades keyword. Roll 6D6; inflict one mortal wound for each 6.",
        effect="grenade_mortal_wounds",
        restrictions="Unit must have Grenades keyword. Target must be within 8\" and visible."
    ),
    Stratagem(
        id="heroic_intervention",
        name="Heroic Intervention",
        cp_cost=2,
        phase=StratagemPhase.OPPONENT_CHARGE,
        description="Move one of your Character units up to 6\" to get into base contact with an enemy unit.",
        effect="heroic_move",
        restrictions="Character unit only. Use after opponent charges."
    ),
    Stratagem(
        id="counter_offensive",
        name="Counter-Offensive",
        cp_cost=2,
        phase=StratagemPhase.FIGHT,
        description="Allows one of your units to fight after your opponent has picked one of their units to fight (if they haven't already fought).",
        effect="interrupt_fight",
        restrictions="Use when opponent picks a unit to fight."
    ),
    Stratagem(
        id="epic_challenge",
        name="Epic Challenge",
        cp_cost=1,
        phase=StratagemPhase.FIGHT,
        description="Give one of your Character models the Precision rule for this phase.",
        effect="grant_precision",
        restrictions="Character model only. Use in Fight phase."
    ),
    Stratagem(
        id="insane_bravery",
        name="Insane Bravery",
        cp_cost=1,
        phase=StratagemPhase.COMMAND,
        description="Use after one of your units fails a Battleshock test. That unit automatically passes the test.",
        effect="auto_pass_battleshock",
        restrictions="Use after failing Battleshock test."
    ),
    Stratagem(
        id="smokescreen",
        name="Smokescreen",
        cp_cost=1,
        phase=StratagemPhase.OPPONENT_SHOOTING,
        description="Give a unit with the Smoke keyword -1 to be hit when targeted by shooting attacks.",
        effect="minus_one_to_hit",
        restrictions="Unit must have Smoke keyword. Use when targeted."
    ),
    Stratagem(
        id="rapid_ingress",
        name="Rapid Ingress",
        cp_cost=1,
        phase=StratagemPhase.OPPONENT_MOVEMENT,
        description="Bring one Strategic Reserves unit onto the battlefield during your opponent's Movement phase.",
        effect="early_reserves",
        restrictions="Unit must be in Strategic Reserves. Can only arrive on eligible turns."
    ),
]


def get_core_stratagems() -> List[Stratagem]:
    """Get all core stratagems"""
    return CORE_STRATAGEMS


def get_stratagem_by_id(stratagem_id: str) -> Optional[Stratagem]:
    """Get a specific stratagem by ID"""
    for strat in CORE_STRATAGEMS:
        if strat.id == stratagem_id:
            return strat
    return None


def get_stratagems_by_phase(phase: StratagemPhase) -> List[Stratagem]:
    """Get all stratagems usable in a specific phase"""
    return [s for s in CORE_STRATAGEMS if s.phase == phase or s.phase == StratagemPhase.ANY]


def apply_stratagem_to_combat(stratagem_id: str, combat_params: dict) -> dict:
    """
    Apply stratagem effects to combat parameters
    Returns modified combat parameters
    """
    strat = get_stratagem_by_id(stratagem_id)
    if not strat:
        return combat_params

    modified_params = combat_params.copy()

    # Apply effects based on stratagem
    if strat.id == "command_reroll":
        # Handled in UI - allows reroll of one die
        modified_params['command_reroll_available'] = True

    elif strat.id == "fire_overwatch":
        # Overwatch: hits on 6s only
        modified_params['overwatch_mode'] = True
        modified_params['hit_modifier'] = 0  # Will only hit on unmodified 6s

    elif strat.id == "go_to_ground":
        # Benefit of Cover + 6++ save
        modified_params['has_cover'] = True
        if not modified_params.get('invuln') or int(modified_params.get('invuln', 7)) > 6:
            modified_params['invuln'] = 6

    elif strat.id == "smokescreen":
        # -1 to hit
        current_hit_mod = modified_params.get('hit_modifier', 0)
        modified_params['hit_modifier'] = current_hit_mod - 1

    elif strat.id == "epic_challenge":
        # Grant Precision
        modified_params['has_precision'] = True

    return modified_params

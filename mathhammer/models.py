"""
Data models for Warhammer 40k units, weapons, and profiles
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class Characteristic:
    """Represents a single characteristic value (e.g., Movement, Toughness, etc.)"""
    name: str
    value: str  # String because can be "6+", "D6", etc.

    def as_number(self) -> Optional[float]:
        """Convert to number if possible"""
        try:
            # Handle dice notation (just extract the number for now)
            if 'D' in self.value.upper():
                parts = self.value.upper().split('D')
                if len(parts) == 2:
                    return float(parts[1]) if parts[0] == '' else float(parts[0]) * float(parts[1])
            # Handle save values like "3+"
            if '+' in self.value or '-' in self.value:
                return float(self.value.replace('+', '').replace('-', ''))
            return float(self.value)
        except (ValueError, AttributeError):
            return None


@dataclass
class Profile:
    """Generic profile with characteristics"""
    name: str
    type_name: str  # "Unit", "Ranged Weapons", "Melee Weapons", "Abilities"
    characteristics: Dict[str, Characteristic] = field(default_factory=dict)

    def get_characteristic(self, name: str) -> Optional[Characteristic]:
        """Get a characteristic by name"""
        return self.characteristics.get(name)

    def get_value(self, name: str) -> Optional[str]:
        """Get characteristic value as string"""
        char = self.get_characteristic(name)
        return char.value if char else None


@dataclass
class WeaponProfile(Profile):
    """Weapon-specific profile"""

    @property
    def range_value(self) -> Optional[str]:
        return self.get_value("Range")

    @property
    def attacks(self) -> Optional[str]:
        return self.get_value("A")

    @property
    def ballistic_skill(self) -> Optional[str]:
        """For ranged weapons"""
        return self.get_value("BS")

    @property
    def weapon_skill(self) -> Optional[str]:
        """For melee weapons"""
        return self.get_value("WS")

    @property
    def strength(self) -> Optional[str]:
        return self.get_value("S")

    @property
    def armor_penetration(self) -> Optional[str]:
        return self.get_value("AP")

    @property
    def damage(self) -> Optional[str]:
        return self.get_value("D")

    @property
    def skill(self) -> Optional[str]:
        """Returns either BS or WS depending on weapon type"""
        return self.ballistic_skill or self.weapon_skill


@dataclass
class UnitProfile(Profile):
    """Unit-specific profile"""

    @property
    def movement(self) -> Optional[str]:
        return self.get_value("M")

    @property
    def toughness(self) -> Optional[str]:
        return self.get_value("T")

    @property
    def save(self) -> Optional[str]:
        return self.get_value("Sv")

    @property
    def wounds(self) -> Optional[str]:
        return self.get_value("W")

    @property
    def leadership(self) -> Optional[str]:
        return self.get_value("Ld")

    @property
    def objective_control(self) -> Optional[str]:
        return self.get_value("OC")

    @property
    def invulnerable_save(self) -> Optional[str]:
        """Check for invulnerable save"""
        return self.get_value("Invulnerable Save") or self.get_value("InvSv")


@dataclass
class Ability:
    """Represents a special ability or rule"""
    name: str
    description: str
    keywords: List[str] = field(default_factory=list)


@dataclass
class Constraint:
    """Represents a BSData constraint (min/max selections)"""
    type: str  # "min" or "max"
    value: int
    field: str = "selections"
    scope: str = "parent"


@dataclass
class WeaponOption:
    """Represents a weapon selection option with constraints"""
    id: str
    name: str
    weapon_profile: Optional[WeaponProfile] = None
    is_default: bool = False
    constraints: List[Constraint] = field(default_factory=list)


@dataclass
class WeaponOptionGroup:
    """Represents a group of mutually exclusive weapon options"""
    name: str  # e.g., "Weapon 1", "Weapon 2"
    options: List[WeaponOption] = field(default_factory=list)
    min_selections: int = 0
    max_selections: int = 1
    default_option_id: Optional[str] = None


@dataclass
class ModelComposition:
    """Represents a model within a unit (e.g., Intercessor Sergeant)"""
    id: str
    name: str
    min_count: int = 1
    max_count: int = 1
    unit_profile: Optional[UnitProfile] = None
    weapon_groups: List[WeaponOptionGroup] = field(default_factory=list)
    fixed_weapons: List[WeaponProfile] = field(default_factory=list)  # Weapons that are always included


@dataclass
class Unit:
    """Represents a complete unit with all its profiles and options"""
    id: str
    name: str
    faction: str = ""
    unit_profile: Optional[UnitProfile] = None
    weapons: List[WeaponProfile] = field(default_factory=list)
    abilities: List[Ability] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    points_cost: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Army builder fields
    model_composition: List[ModelComposition] = field(default_factory=list)
    max_in_roster: int = 3  # Default: 3 of each datasheet (10th ed rule)
    categories: List[str] = field(default_factory=list)  # e.g., ["Battleline", "Infantry", "Character"]

    def get_weapon_by_name(self, name: str) -> Optional[WeaponProfile]:
        """Find a weapon by name"""
        for weapon in self.weapons:
            if weapon.name.lower() == name.lower():
                return weapon
        return None


@dataclass
class DataCatalog:
    """Container for all loaded game data"""
    units: Dict[str, Unit] = field(default_factory=dict)
    weapons: Dict[str, WeaponProfile] = field(default_factory=dict)
    abilities: Dict[str, Ability] = field(default_factory=dict)
    factions: List[str] = field(default_factory=list)

    def add_unit(self, unit: Unit):
        """Add a unit to the catalog"""
        self.units[unit.id] = unit
        if unit.faction and unit.faction not in self.factions:
            self.factions.append(unit.faction)

    def get_unit(self, unit_id: str) -> Optional[Unit]:
        """Get a unit by ID"""
        return self.units.get(unit_id)

    def get_units_by_faction(self, faction: str) -> List[Unit]:
        """Get all units for a faction"""
        return [u for u in self.units.values() if u.faction == faction]

    def search_units(self, query: str) -> List[Unit]:
        """Search units by name"""
        query = query.lower()
        return [u for u in self.units.values() if query in u.name.lower()]


@dataclass
class SelectedWeapon:
    """Represents a selected weapon in an army list"""
    weapon_profile: WeaponProfile
    option_id: str  # Links back to WeaponOption


@dataclass
class SelectedModel:
    """Represents selected models within a unit"""
    model_id: str
    model_name: str
    count: int
    selected_weapons: Dict[str, SelectedWeapon] = field(default_factory=dict)  # group_name -> weapon


@dataclass
class ArmyUnit:
    """Represents a unit in an army list with selected options"""
    unit_id: str
    unit_name: str
    faction: str
    selected_models: List[SelectedModel] = field(default_factory=list)
    points_cost: int = 0
    enhancements: List[str] = field(default_factory=list)  # For characters


@dataclass
class Army:
    """Represents a complete army roster"""
    name: str
    faction: str
    detachment: str = "Gladius Strike Force"  # Default detachment
    points_limit: int = 2000  # Default: Strike Force
    units: List[ArmyUnit] = field(default_factory=list)
    created_at: str = ""
    modified_at: str = ""

    def total_points(self) -> int:
        """Calculate total points of army"""
        return sum(u.points_cost for u in self.units)

    def unit_count(self, unit_id: str) -> int:
        """Count how many times a unit datasheet appears"""
        return sum(1 for u in self.units if u.unit_id == unit_id)

    def is_valid(self) -> bool:
        """Check if army is valid (within points, at least 1 character, etc.)"""
        # Check points limit
        if self.total_points() > self.points_limit:
            return False

        # TODO: Add more validation rules
        return True

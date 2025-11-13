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

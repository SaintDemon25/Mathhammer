"""
BSData XML Parser for Warhammer 40k 10th Edition
Parses .gst (game system) and .cat (catalog) files
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

from .models import (
    Unit, UnitProfile, WeaponProfile, Ability, Characteristic,
    Profile, DataCatalog
)

logger = logging.getLogger(__name__)


class BSDataParser:
    """Parser for BattleScribe data files"""

    # BattleScribe XML namespace
    NAMESPACE = {'bs': 'http://www.battlescribe.net/schema/catalogueSchema'}

    def __init__(self):
        self.catalog = DataCatalog()
        self.game_system_data = {}
        self.shared_profiles = {}
        self.shared_rules = {}
        self.use_namespace = True  # Flag to track if we need namespace handling

    def _find(self, element: ET.Element, path: str) -> List[ET.Element]:
        """Find elements with namespace handling"""
        try:
            # Convert XPath to use namespace prefix
            # Replace element names with prefixed versions
            # e.g., ".//selectionEntry" -> ".//bs:selectionEntry"
            ns_path = path
            for tag in ['selectionEntry', 'sharedSelectionEntry', 'profile', 'profileType',
                       'characteristicType', 'characteristic', 'rule', 'description', 'cost',
                       'categoryLink', 'entryLink']:
                ns_path = ns_path.replace(f'//{tag}', f'//bs:{tag}')
                ns_path = ns_path.replace(f'/{tag}', f'/bs:{tag}')

            result = element.findall(ns_path, self.NAMESPACE)
            if result:
                return result
        except Exception as e:
            logger.debug(f"Namespace find failed for {path}: {e}")

        # Fallback to without namespace
        return element.findall(path)

    def _find_one(self, element: ET.Element, path: str) -> Optional[ET.Element]:
        """Find single element with namespace handling"""
        try:
            # Convert XPath to use namespace prefix
            ns_path = path
            for tag in ['selectionEntry', 'sharedSelectionEntry', 'profile', 'profileType',
                       'characteristicType', 'characteristic', 'rule', 'description', 'cost',
                       'categoryLink', 'entryLink']:
                ns_path = ns_path.replace(f'//{tag}', f'//bs:{tag}')
                ns_path = ns_path.replace(f'/{tag}', f'/bs:{tag}')

            result = element.find(ns_path, self.NAMESPACE)
            if result is not None:
                return result
        except Exception as e:
            logger.debug(f"Namespace find_one failed for {path}: {e}")

        # Fallback to without namespace
        return element.find(path)

    def parse_game_system(self, file_path: str) -> Dict:
        """Parse the game system file (.gst)"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            logger.info(f"Parsing game system: {root.get('name', 'Unknown')}")

            # Store profile types for reference
            profile_types = {}
            for profile_type in self._find(root, './/profileType'):
                type_id = profile_type.get('id')
                type_name = profile_type.get('name')
                characteristics = []

                for char_type in self._find(profile_type, './/characteristicType'):
                    characteristics.append({
                        'id': char_type.get('id'),
                        'name': char_type.get('name')
                    })

                profile_types[type_id] = {
                    'name': type_name,
                    'characteristics': characteristics
                }

            self.game_system_data['profile_types'] = profile_types

            # Parse shared profiles
            for profile in self._find(root, './/profile'):
                self._parse_profile_element(profile)

            # Parse shared rules/abilities
            for rule in self._find(root, './/rule'):
                ability = self._parse_rule_element(rule)
                if ability:
                    rule_id = rule.get('id')
                    self.shared_rules[rule_id] = ability

            return self.game_system_data

        except Exception as e:
            logger.error(f"Error parsing game system file: {e}")
            raise

    def parse_catalog(self, file_path: str, faction_name: Optional[str] = None) -> DataCatalog:
        """Parse a catalog file (.cat)"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            catalog_name = root.get('name', Path(file_path).stem)
            if not faction_name:
                faction_name = catalog_name

            logger.info(f"Parsing catalog: {catalog_name}")

            # Parse all selection entries (units, weapons, etc.)
            all_entries = self._find(root, './/selectionEntry')
            logger.info(f"Found {len(all_entries)} selectionEntry elements")

            for entry in all_entries:
                unit = self._parse_selection_entry(entry, faction_name)
                if unit:
                    self.catalog.add_unit(unit)

            # Parse shared selection entries (these are rare, usually selectionEntry inside sharedSelectionEntries)
            shared_entries = self._find(root, './/sharedSelectionEntry')
            logger.info(f"Found {len(shared_entries)} sharedSelectionEntry elements")

            for entry in shared_entries:
                unit = self._parse_selection_entry(entry, faction_name)
                if unit:
                    self.catalog.add_unit(unit)

            return self.catalog

        except Exception as e:
            logger.error(f"Error parsing catalog file: {e}")
            raise

    def _parse_selection_entry(self, entry: ET.Element, faction: str) -> Optional[Unit]:
        """Parse a selection entry (unit or equipment)"""
        entry_type = entry.get('type', '')
        entry_id = entry.get('id', '')
        entry_name = entry.get('name', '')

        if not entry_name:
            return None

        # Only process entries that look like units (have type='model' or 'unit' or have a Unit profile)
        # We'll check for Unit profiles later, so be more permissive here
        if entry_type in ['upgrade']:  # Skip pure upgrades
            # But check if it has profiles that might indicate it's actually a unit
            has_unit_profile = False
            for profile in self._find(entry, './/profile'):
                if profile.get('typeName') == 'Unit':
                    has_unit_profile = True
                    break
            if not has_unit_profile:
                return None

        # Create unit
        unit = Unit(
            id=entry_id,
            name=entry_name,
            faction=faction
        )

        # Parse profiles (unit stats, weapons, abilities)
        for profile in self._find(entry, './/profile'):
            parsed_profile = self._parse_profile_element(profile)
            if parsed_profile:
                if parsed_profile.type_name == 'Unit':
                    unit.unit_profile = UnitProfile(
                        name=parsed_profile.name,
                        type_name=parsed_profile.type_name,
                        characteristics=parsed_profile.characteristics
                    )
                elif parsed_profile.type_name in ['Ranged Weapons', 'Melee Weapons']:
                    weapon = WeaponProfile(
                        name=parsed_profile.name,
                        type_name=parsed_profile.type_name,
                        characteristics=parsed_profile.characteristics
                    )
                    unit.weapons.append(weapon)
                elif parsed_profile.type_name == 'Abilities':
                    # Convert ability profile to Ability object
                    desc = parsed_profile.get_value('Description') or ''
                    ability = Ability(name=parsed_profile.name, description=desc)
                    unit.abilities.append(ability)

        # Parse nested selection entries (weapons, equipment)
        for nested_entry in self._find(entry, './/selectionEntry'):
            self._parse_nested_equipment(nested_entry, unit)

        # Parse rules/abilities
        for rule in self._find(entry, './/rule'):
            ability = self._parse_rule_element(rule)
            if ability:
                unit.abilities.append(ability)

        # Parse costs
        for cost in self._find(entry, './/cost'):
            cost_type = cost.get('name', '')
            if cost_type == 'pts':
                try:
                    unit.points_cost = int(float(cost.get('value', 0)))
                except ValueError:
                    pass

        # Parse categories/keywords
        for category_link in self._find(entry, './/categoryLink'):
            category_name = category_link.get('name', '')
            if category_name:
                unit.keywords.append(category_name)

        # Only return units that have a unit profile or weapons
        if unit.unit_profile or unit.weapons:
            logger.debug(f"Loaded unit: {unit.name} (profile={unit.unit_profile is not None}, weapons={len(unit.weapons)})")
            return unit
        else:
            logger.debug(f"Skipping {entry_name}: no profile or weapons")
            return None

    def _parse_nested_equipment(self, entry: ET.Element, unit: Unit):
        """Parse nested equipment/weapons"""
        entry_type = entry.get('type', '')

        # Parse profiles from nested entries
        for profile in self._find(entry, './/profile'):
            parsed_profile = self._parse_profile_element(profile)
            if parsed_profile:
                if parsed_profile.type_name in ['Ranged Weapons', 'Melee Weapons']:
                    weapon = WeaponProfile(
                        name=parsed_profile.name,
                        type_name=parsed_profile.type_name,
                        characteristics=parsed_profile.characteristics
                    )
                    # Check if weapon already exists
                    if not any(w.name == weapon.name for w in unit.weapons):
                        unit.weapons.append(weapon)

    def _parse_profile_element(self, profile: ET.Element) -> Optional[Profile]:
        """Parse a profile element into a Profile object"""
        profile_name = profile.get('name', '')
        profile_type = profile.get('typeName', '')

        if not profile_name:
            return None

        characteristics = {}

        for characteristic in self._find(profile, './/characteristic'):
            char_name = characteristic.get('name', '')
            char_value = characteristic.text or ''

            if char_name:
                characteristics[char_name] = Characteristic(
                    name=char_name,
                    value=char_value.strip()
                )

        return Profile(
            name=profile_name,
            type_name=profile_type,
            characteristics=characteristics
        )

    def _parse_rule_element(self, rule: ET.Element) -> Optional[Ability]:
        """Parse a rule element into an Ability object"""
        rule_name = rule.get('name', '')
        description = ''

        desc_element = self._find_one(rule, './/description')
        if desc_element is not None and desc_element.text:
            description = desc_element.text.strip()

        if rule_name:
            return Ability(name=rule_name, description=description)

        return None

    def load_dataset(self, dataset_dir: str) -> DataCatalog:
        """Load a complete dataset from a directory"""
        dataset_path = Path(dataset_dir)

        # First, parse game system file if it exists
        gst_files = list(dataset_path.glob('*.gst'))
        if gst_files:
            logger.info(f"Loading game system: {gst_files[0]}")
            self.parse_game_system(str(gst_files[0]))

        # Then parse all catalog files
        cat_files = list(dataset_path.glob('*.cat'))
        logger.info(f"Found {len(cat_files)} catalog files")

        for cat_file in cat_files:
            try:
                logger.info(f"Loading catalog: {cat_file.name}")
                self.parse_catalog(str(cat_file))
            except Exception as e:
                logger.error(f"Failed to parse {cat_file.name}: {e}")
                continue

        logger.info(f"Loaded {len(self.catalog.units)} units from {len(self.catalog.factions)} factions")

        return self.catalog

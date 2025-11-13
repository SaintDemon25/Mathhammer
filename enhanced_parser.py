"""
Enhanced BSData parser with proper unit listing
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
from pathlib import Path
import logging

from mathhammer.models import Unit, UnitProfile, WeaponProfile, Characteristic, DataCatalog
from mathhammer.parser import BSDataParser

logger = logging.getLogger(__name__)


class EnhancedBSDataParser(BSDataParser):
    """Enhanced parser that properly handles entryLinks and unit organization"""

    def __init__(self):
        super().__init__()
        self.entry_link_map = {}  # Maps entry link IDs to unit names
        self.selectable_units = []  # List of units that can be selected
        self.shared_definitions = {}  # Maps targetId to actual weapon/equipment definitions

    def parse_catalog_with_entry_links(self, file_path: str, faction_name: Optional[str] = None) -> DataCatalog:
        """Parse catalog and build proper unit list from entryLinks"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            catalog_name = root.get('name', Path(file_path).stem)
            if not faction_name:
                faction_name = catalog_name

            logger.info(f"Parsing catalog: {catalog_name}")

            # FIRST: Build a map of ALL shared definitions by targetId
            logger.info("Building shared definitions map...")
            self._build_shared_definitions_map(root)

            # Second, parse all shared selection entries (actual unit definitions)
            unit_definitions = {}
            shared_entries = self._find(root, './/selectionEntry')
            logger.info(f"Found {len(shared_entries)} unit definitions")

            for entry in shared_entries:
                entry_id = entry.get('id')
                unit = self._parse_selection_entry_enhanced(entry, faction_name)
                if unit:
                    unit_definitions[entry_id] = unit

            # Now parse entryLinks (these are the selectable units)
            entry_links = []

            # Get entryLinks from root level
            for link in self._find(root, './/entryLink'):
                link_type = link.get('type', '')
                if link_type == 'selectionEntry':
                    entry_links.append(link)

            logger.info(f"Found {len(entry_links)} selectable units (entryLinks)")

            # Process entryLinks to create selectable unit list
            for link in entry_links:
                name = link.get('name', '')
                target_id = link.get('targetId', '')
                hidden = link.get('hidden', 'false').lower() == 'true'

                # Skip hidden units and non-unit entries
                if hidden or not name or name in ['Detachment', 'Warlord']:
                    continue

                # Get the actual unit definition
                if target_id in unit_definitions:
                    unit = unit_definitions[target_id]
                    # Update name from entryLink (more user-friendly)
                    unit.name = name

                    # Only add if it has a unit profile (actual unit, not just equipment)
                    if unit.unit_profile:
                        self.catalog.add_unit(unit)
                        self.selectable_units.append({
                            'id': unit.id,
                            'name': name,
                            'faction': faction_name,
                            'target_id': target_id
                        })

            logger.info(f"Loaded {len(self.catalog.units)} selectable units")
            return self.catalog

        except Exception as e:
            logger.error(f"Error parsing catalog: {e}", exc_info=True)
            raise

    def _build_shared_definitions_map(self, root: ET.Element):
        """Build a map of all shared selection entries for weapon/equipment lookups"""
        # Find all sharedSelectionEntries
        for entry in self._find(root, './/selectionEntry'):
            entry_id = entry.get('id')
            if entry_id:
                self.shared_definitions[entry_id] = entry

        logger.info(f"Built shared definitions map with {len(self.shared_definitions)} entries")

    def _parse_selection_entry_enhanced(self, entry: ET.Element, faction: str) -> Optional[Unit]:
        """Enhanced parsing that follows entryLinks and resolves weapons recursively"""
        entry_type = entry.get('type', '')
        entry_id = entry.get('id', '')
        entry_name = entry.get('name', '')

        if not entry_name:
            return None

        # Create unit
        unit = Unit(
            id=entry_id,
            name=entry_name,
            faction=faction
        )

        # Parse profiles (unit stats, abilities)
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
                    desc = parsed_profile.get_value('Description') or ''
                    from mathhammer.models import Ability
                    ability = Ability(name=parsed_profile.name, description=desc)
                    unit.abilities.append(ability)

        # ENHANCED: Parse selectionEntryGroups recursively and follow entryLinks
        self._parse_weapons_from_entry_groups(entry, unit)

        # Parse nested selection entries (weapons, equipment)
        for nested_entry in self._find(entry, './/selectionEntry'):
            self._parse_nested_equipment_enhanced(nested_entry, unit)

        # Parse categories/keywords
        for category_link in self._find(entry, './/categoryLink'):
            category_name = category_link.get('name', '')
            if category_name:
                unit.keywords.append(category_name)

        # Return unit even without weapons (we'll get them from nested structures)
        if unit.unit_profile or unit.weapons:
            logger.debug(f"Loaded unit: {unit.name} (profile={unit.unit_profile is not None}, weapons={len(unit.weapons)})")
            return unit
        else:
            logger.debug(f"Skipping {entry_name}: no profile or weapons")
            return None

    def _parse_weapons_from_entry_groups(self, entry: ET.Element, unit: Unit):
        """Recursively parse selectionEntryGroups and follow entryLinks to find weapons"""
        # Find all selectionEntryGroups
        for group in self._find(entry, './/selectionEntryGroup'):
            # Look for entryLinks within this group (use .// to find all descendants)
            for entry_link in self._find(group, './/entryLink'):
                target_id = entry_link.get('targetId', '')
                link_type = entry_link.get('type', '')

                # Resolve the entryLink to actual definition
                if target_id in self.shared_definitions:
                    linked_entry = self.shared_definitions[target_id]

                    # Parse weapons from the linked entry (use .// to find all nested profiles)
                    for profile in self._find(linked_entry, './/profile'):
                        parsed_profile = self._parse_profile_element(profile)
                        if parsed_profile and parsed_profile.type_name in ['Ranged Weapons', 'Melee Weapons']:
                            weapon = WeaponProfile(
                                name=parsed_profile.name,
                                type_name=parsed_profile.type_name,
                                characteristics=parsed_profile.characteristics
                            )
                            # Check if weapon already exists
                            if not any(w.name == weapon.name for w in unit.weapons):
                                unit.weapons.append(weapon)

    def _parse_nested_equipment_enhanced(self, entry: ET.Element, unit: Unit):
        """Enhanced nested equipment parsing"""
        # Parse profiles from nested entries
        for profile in self._find(entry, 'profile'):
            parsed_profile = self._parse_profile_element(profile)
            if parsed_profile and parsed_profile.type_name in ['Ranged Weapons', 'Melee Weapons']:
                weapon = WeaponProfile(
                    name=parsed_profile.name,
                    type_name=parsed_profile.type_name,
                    characteristics=parsed_profile.characteristics
                )
                # Check if weapon already exists
                if not any(w.name == weapon.name for w in unit.weapons):
                    unit.weapons.append(weapon)

    def get_selectable_units_list(self) -> List[Dict]:
        """Get list of units that can be selected (from entryLinks)"""
        return self.selectable_units

    def get_units_by_category(self) -> Dict[str, List]:
        """Organize units by category (HQ, Troops, Elites, etc.)"""
        categorized = {
            'HQ': [],
            'Troops': [],
            'Elites': [],
            'Fast Attack': [],
            'Heavy Support': [],
            'Dedicated Transport': [],
            'Fortification': [],
            'Other': []
        }

        for unit in self.catalog.units.values():
            # Check keywords to determine category
            keywords = [kw.lower() for kw in unit.keywords]

            if 'character' in keywords or 'hq' in keywords:
                categorized['HQ'].append(unit)
            elif 'battleline' in keywords or 'troops' in keywords:
                categorized['Troops'].append(unit)
            elif 'elites' in keywords:
                categorized['Elites'].append(unit)
            elif 'fast attack' in keywords:
                categorized['Fast Attack'].append(unit)
            elif 'heavy support' in keywords:
                categorized['Heavy Support'].append(unit)
            elif 'dedicated transport' in keywords or 'transport' in keywords:
                categorized['Dedicated Transport'].append(unit)
            elif 'fortification' in keywords:
                categorized['Fortification'].append(unit)
            else:
                categorized['Other'].append(unit)

        return categorized

    def load_dataset_enhanced(self, dataset_dir: str) -> DataCatalog:
        """Load complete dataset with enhanced parsing"""
        dataset_path = Path(dataset_dir)

        # Parse game system file
        gst_files = list(dataset_path.glob('*.gst'))
        if gst_files:
            logger.info(f"Loading game system: {gst_files[0]}")
            self.parse_game_system(str(gst_files[0]))

        # Parse all catalog files with entryLink support
        cat_files = list(dataset_path.glob('*.cat'))
        logger.info(f"Found {len(cat_files)} catalog files")

        for cat_file in cat_files:
            try:
                logger.info(f"Loading catalog: {cat_file.name}")
                self.parse_catalog_with_entry_links(str(cat_file))
            except Exception as e:
                logger.error(f"Failed to parse {cat_file.name}: {e}")
                continue

        logger.info(f"Total selectable units: {len(self.selectable_units)}")
        logger.info(f"Total factions: {len(self.catalog.factions)}")

        return self.catalog

    def _parse_abilities_from_keywords(self, keywords_str: str) -> List[str]:
        """Parse ability keywords from comma-separated string"""
        if not keywords_str:
            return []

        # Split by comma and clean up
        abilities = [kw.strip() for kw in keywords_str.split(',')]
        return [ab for ab in abilities if ab]

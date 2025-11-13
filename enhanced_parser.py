"""
Enhanced BSData parser with proper unit listing
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
from pathlib import Path
import logging

from mathhammer.models import (
    Unit, UnitProfile, WeaponProfile, Characteristic, DataCatalog,
    Ability, Constraint, WeaponOption, WeaponOptionGroup, ModelComposition
)
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
                unit.categories.append(category_name)

        # Parse constraints (max in roster, etc.)
        unit.max_in_roster = self._parse_max_in_roster(entry)

        # Parse points cost
        unit.points_cost = self._parse_points_cost(entry)

        # Parse model composition (for units with multiple model types)
        unit.model_composition = self._parse_model_composition(entry, faction)

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

    def _parse_constraint(self, constraint_elem: ET.Element) -> Optional[Constraint]:
        """Parse a single constraint element"""
        try:
            constraint_type = constraint_elem.get('type', '')
            value_str = constraint_elem.get('value', '0')
            field = constraint_elem.get('field', 'selections')
            scope = constraint_elem.get('scope', 'parent')

            # Only parse min/max constraints
            if constraint_type not in ['min', 'max']:
                return None

            return Constraint(
                type=constraint_type,
                value=int(value_str),
                field=field,
                scope=scope
            )
        except (ValueError, AttributeError) as e:
            logger.debug(f"Could not parse constraint: {e}")
            return None

    def _parse_max_in_roster(self, entry: ET.Element) -> int:
        """Parse maximum number of this unit allowed in roster"""
        # Look for constraint with scope="roster" or "force" and field="selections"
        for constraint in self._find(entry, './/constraint'):
            constraint_type = constraint.get('type', '')
            scope = constraint.get('scope', '')
            field = constraint.get('field', '')

            if constraint_type == 'max' and scope in ['roster', 'force'] and field == 'selections':
                value_str = constraint.get('value', '3')
                try:
                    return int(value_str)
                except ValueError:
                    pass

        # Check if it's a Battleline or Dedicated Transport (max 6 in 10th ed)
        for category_link in self._find(entry, './/categoryLink'):
            category = category_link.get('name', '').lower()
            if 'battleline' in category or 'dedicated transport' in category:
                return 6

        # Default is 3 in 10th edition
        return 3

    def _parse_points_cost(self, entry: ET.Element) -> int:
        """Parse points cost from cost elements"""
        for cost in self._find(entry, './/cost'):
            cost_name = cost.get('name', '').lower()
            if cost_name in ['pts', 'points']:
                value_str = cost.get('value', '0')
                try:
                    return int(float(value_str))
                except ValueError:
                    pass
        return 0

    def _parse_model_composition(self, entry: ET.Element, faction: str) -> List[ModelComposition]:
        """Parse model composition from selectionEntryGroups"""
        models = []

        # Look for selectionEntryGroups that contain model selectionEntries
        # Get direct child groups only (to avoid nested weapon groups)
        seen_models = set()  # Track models to avoid duplicates
        for group in self._find(entry, './/selectionEntryGroup'):
            group_name = group.get('name', '')

            # Look for DIRECT model children within this group (not nested)
            for model_entry in self._find(group, './/selectionEntry'):
                model_type = model_entry.get('type', '')
                if model_type != 'model':
                    continue

                model_id = model_entry.get('id', '')
                model_name = model_entry.get('name', '')

                # Skip if we already saw this model (can happen with nested groups)
                if model_id in seen_models:
                    continue
                seen_models.add(model_id)

                # Parse model constraints (min/max count)
                min_count = 1
                max_count = 1

                for constraint in self._find(model_entry, 'constraints/constraint'):
                    c = self._parse_constraint(constraint)
                    if c and c.scope == 'parent' and c.field == 'selections':
                        if c.type == 'min':
                            min_count = c.value
                        elif c.type == 'max':
                            max_count = c.value

                # Parse model's unit profile
                model_profile = None
                for profile in self._find(model_entry, 'profiles/profile'):
                    parsed = self._parse_profile_element(profile)
                    if parsed and parsed.type_name == 'Unit':
                        model_profile = UnitProfile(
                            name=parsed.name,
                            type_name=parsed.type_name,
                            characteristics=parsed.characteristics
                        )
                        break

                # Parse weapon option groups for this model
                weapon_groups = self._parse_weapon_option_groups(model_entry)

                # Parse fixed weapons (from entryLinks with min=max=1)
                fixed_weapons = self._parse_fixed_weapons(model_entry)

                model = ModelComposition(
                    id=model_id,
                    name=model_name,
                    min_count=min_count,
                    max_count=max_count,
                    unit_profile=model_profile,
                    weapon_groups=weapon_groups,
                    fixed_weapons=fixed_weapons
                )

                models.append(model)

        return models

    def _parse_weapon_option_groups(self, model_entry: ET.Element) -> List[WeaponOptionGroup]:
        """Parse weapon selection groups for a model"""
        groups = []

        for group_elem in self._find(model_entry, 'selectionEntryGroups/selectionEntryGroup'):
            group_name = group_elem.get('name', '')
            default_id = group_elem.get('defaultSelectionEntryId', '')

            # Parse group constraints
            min_sel = 0
            max_sel = 1

            for constraint in self._find(group_elem, 'constraints/constraint'):
                c = self._parse_constraint(constraint)
                if c and c.scope == 'parent' and c.field == 'selections':
                    if c.type == 'min':
                        min_sel = c.value
                    elif c.type == 'max':
                        max_sel = c.value

            # Parse weapon options within this group
            options = []

            # From direct selectionEntry elements
            for entry in self._find(group_elem, 'selectionEntries/selectionEntry'):
                option = self._parse_weapon_option(entry, default_id)
                if option:
                    options.append(option)

            # From entryLinks
            for link in self._find(group_elem, 'entryLinks/entryLink'):
                option = self._parse_weapon_option_from_link(link, default_id)
                if option:
                    options.append(option)

            if options:
                group = WeaponOptionGroup(
                    name=group_name,
                    options=options,
                    min_selections=min_sel,
                    max_selections=max_sel,
                    default_option_id=default_id if default_id else None
                )
                groups.append(group)

        return groups

    def _parse_weapon_option(self, entry: ET.Element, default_id: str) -> Optional[WeaponOption]:
        """Parse a single weapon option from selectionEntry"""
        option_id = entry.get('id', '')
        option_name = entry.get('name', '')
        is_default = (option_id == default_id)

        # Parse weapon profile
        weapon_prof = None
        for profile in self._find(entry, './/profile'):
            parsed = self._parse_profile_element(profile)
            if parsed and parsed.type_name in ['Ranged Weapons', 'Melee Weapons']:
                weapon_prof = WeaponProfile(
                    name=parsed.name,
                    type_name=parsed.type_name,
                    characteristics=parsed.characteristics
                )
                break

        # Parse constraints
        constraints = []
        for constraint in self._find(entry, 'constraints/constraint'):
            c = self._parse_constraint(constraint)
            if c:
                constraints.append(c)

        return WeaponOption(
            id=option_id,
            name=option_name,
            weapon_profile=weapon_prof,
            is_default=is_default,
            constraints=constraints
        )

    def _parse_weapon_option_from_link(self, link: ET.Element, default_id: str) -> Optional[WeaponOption]:
        """Parse weapon option from entryLink"""
        link_id = link.get('id', '')
        target_id = link.get('targetId', '')
        option_name = link.get('name', '')
        is_default = (link_id == default_id or target_id == default_id)

        # Resolve the target
        weapon_prof = None
        if target_id in self.shared_definitions:
            target_entry = self.shared_definitions[target_id]

            # Parse weapon profile from target
            for profile in self._find(target_entry, './/profile'):
                parsed = self._parse_profile_element(profile)
                if parsed and parsed.type_name in ['Ranged Weapons', 'Melee Weapons']:
                    weapon_prof = WeaponProfile(
                        name=parsed.name,
                        type_name=parsed.type_name,
                        characteristics=parsed.characteristics
                    )
                    break

        # Parse constraints
        constraints = []
        for constraint in self._find(link, 'constraints/constraint'):
            c = self._parse_constraint(constraint)
            if c:
                constraints.append(c)

        return WeaponOption(
            id=link_id or target_id,
            name=option_name,
            weapon_profile=weapon_prof,
            is_default=is_default,
            constraints=constraints
        )

    def _parse_fixed_weapons(self, model_entry: ET.Element) -> List[WeaponProfile]:
        """Parse weapons that are always equipped (min=max=1 with no choices)"""
        fixed = []

        for link in self._find(model_entry, 'entryLinks/entryLink'):
            target_id = link.get('targetId', '')
            link_name = link.get('name', '')

            # Check if this is a fixed weapon (has min=max=1 constraints)
            min_val = None
            max_val = None

            for constraint in self._find(link, 'constraints/constraint'):
                c = self._parse_constraint(constraint)
                if c and c.scope == 'parent' and c.field == 'selections':
                    if c.type == 'min':
                        min_val = c.value
                    elif c.type == 'max':
                        max_val = c.value

            # Fixed weapon: min=1, max=1
            if min_val == 1 and max_val == 1:
                # Resolve weapon
                if target_id in self.shared_definitions:
                    target_entry = self.shared_definitions[target_id]

                    for profile in self._find(target_entry, './/profile'):
                        parsed = self._parse_profile_element(profile)
                        if parsed and parsed.type_name in ['Ranged Weapons', 'Melee Weapons']:
                            weapon = WeaponProfile(
                                name=parsed.name,
                                type_name=parsed.type_name,
                                characteristics=parsed.characteristics
                            )
                            fixed.append(weapon)
                            break

        return fixed

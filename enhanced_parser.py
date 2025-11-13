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

    def parse_catalog_with_entry_links(self, file_path: str, faction_name: Optional[str] = None) -> DataCatalog:
        """Parse catalog and build proper unit list from entryLinks"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            catalog_name = root.get('name', Path(file_path).stem)
            if not faction_name:
                faction_name = catalog_name

            logger.info(f"Parsing catalog: {catalog_name}")

            # First, parse all shared selection entries (actual unit definitions)
            unit_definitions = {}
            shared_entries = self._find(root, './/selectionEntry')
            logger.info(f"Found {len(shared_entries)} unit definitions")

            for entry in shared_entries:
                entry_id = entry.get('id')
                unit = self._parse_selection_entry(entry, faction_name)
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

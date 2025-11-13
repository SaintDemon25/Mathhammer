#!/usr/bin/env python3
"""Test XML namespace parsing"""

import xml.etree.ElementTree as ET

tree = ET.parse('datasets/Imperium - Space Marines.cat')
root = tree.getroot()

print("Root tag:", root.tag)
print("Root attribs:", list(root.attrib.keys())[:5])

# Try different ways to find selectionEntry
NAMESPACE = {'bs': 'http://www.battlescribe.net/schema/catalogueSchema'}

# Method 1: with namespace
entries1 = root.findall('.//bs:selectionEntry', NAMESPACE)
print(f"\nMethod 1 (with namespace): Found {len(entries1)} entries")

# Method 2: without namespace
entries2 = root.findall('.//selectionEntry')
print(f"Method 2 (without namespace): Found {len(entries2)} entries")

# Method 3: direct children
shared_section = root.find('.//bs:sharedSelectionEntries', NAMESPACE)
if shared_section is not None:
    print(f"\nFound sharedSelectionEntries section")
    direct_entries = list(shared_section)
    print(f"Direct children: {len(direct_entries)}")
    if direct_entries:
        print(f"First child tag: {direct_entries[0].tag}")
        print(f"First child name: {direct_entries[0].get('name', 'N/A')}")
        print(f"First child type: {direct_entries[0].get('type', 'N/A')}")
else:
    print("\nsharedSelectionEntries section not found")

# Method 4: all selectionEntry under sharedSelectionEntries
if shared_section is not None:
    sel_entries = shared_section.findall('.//bs:selectionEntry', NAMESPACE)
    print(f"\nselectionEntry elements under sharedSelectionEntries: {len(sel_entries)}")

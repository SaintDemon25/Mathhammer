# Datasets Directory

This directory is for storing BSData format files (`.cat` and `.gst` files) for Warhammer 40k 10th Edition.

## How to Import Datasets

### Option 1: Clone the BSData Repository (Recommended)

```bash
# Clone the BSData Warhammer 40k 10th Edition repository
cd datasets/
git clone https://github.com/BSData/wh40k-10e.git
mv wh40k-10e/* .
rm -rf wh40k-10e/
```

### Option 2: Download Individual Files

1. Visit https://github.com/BSData/wh40k-10e
2. Download the `.gst` file (game system): `Warhammer 40,000.gst`
3. Download the `.cat` files (faction catalogs) you want to use
4. Place them in this directory

### Option 3: Copy from BattleScribe

If you have BattleScribe installed, you can copy the data files from:

- **Windows**: `%APPDATA%/BattleScribe/data/`
- **Mac**: `~/Library/Application Support/BattleScribe/data/`
- **Linux**: `~/.local/share/BattleScribe/data/`

## File Types

- **`.gst`**: Game System Template - defines the core rules and profile types
- **`.cat`**: Catalog - contains faction-specific units, weapons, and abilities

## Example Files

Essential files to get started:
- `Warhammer 40,000.gst` - Core game system (required)
- `Imperium - Space Marines.cat` - Space Marines faction
- `Chaos - Chaos Space Marines.cat` - Chaos Space Marines faction
- Any other faction catalogs you want to use

## After Adding Files

1. Restart the application or click "Reload Dataset" in the web interface
2. The parser will automatically load all `.cat` and `.gst` files from this directory
3. Units and weapons will be available in the mathhammer calculator

## Notes

- Files are gitignored by default (see `.gitignore`)
- Keep your data files updated for the latest balance changes
- The BSData repository is regularly updated by the community

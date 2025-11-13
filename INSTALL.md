# Installation Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download Dataset (Optional but Recommended)

```bash
cd datasets/
git clone https://github.com/BSData/wh40k-10e.git temp
mv temp/*.cat temp/*.gst . 2>/dev/null || true
rm -rf temp/
cd ..
```

Alternatively, download specific files from https://github.com/BSData/wh40k-10e

### 3. Run the Application

```bash
python app.py
```

### 4. Open in Browser

Navigate to: `http://localhost:5000`

## Detailed Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for cloning datasets)

### Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Dataset Setup

The application supports importing BSData format files:

1. **Automatic Download**:
   ```bash
   cd datasets/
   git clone https://github.com/BSData/wh40k-10e.git
   mv wh40k-10e/* .
   rm -rf wh40k-10e/
   cd ..
   ```

2. **Manual Download**:
   - Visit https://github.com/BSData/wh40k-10e
   - Download `.gst` and `.cat` files
   - Place them in the `datasets/` directory

3. **From BattleScribe**:
   - Copy files from your BattleScribe data directory
   - See `datasets/README.md` for locations

### Running the Application

```bash
python app.py
```

The application will:
1. Start a Flask web server on port 5000
2. Automatically load any datasets found in `datasets/`
3. Open to http://0.0.0.0:5000

### Accessing the Web Interface

Open your web browser and go to:
- Local: `http://localhost:5000`
- Network: `http://<your-ip>:5000`

## Usage

### Attack Calculator
1. Search and select an attacking unit
2. Choose a weapon from the dropdown
3. Search and select a defending unit
4. Set number of attacking models
5. Click "Calculate" to see expected outcomes

### Weapon Comparison
1. Select a unit with multiple weapons
2. Select a target unit
3. Click "Compare Weapons" to see which is most effective

### Combat Simulation
1. Select attacking and defending units
2. Set model counts for both sides
3. Optionally choose a specific weapon
4. Click "Simulate Combat" to see full results

## Troubleshooting

### No Units Showing
- Ensure you have `.cat` and `.gst` files in `datasets/`
- Click "Reload Dataset" in the web interface
- Check the console for parsing errors

### Parser Errors
- Verify files are valid BSData XML format
- Ensure you have both `.gst` (game system) and `.cat` (catalog) files
- Try downloading fresh files from the BSData repository

### Port Already in Use
Edit `app.py` and change the port:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Changed from 5000
```

## Development

### Running in Debug Mode
The application runs in debug mode by default, which:
- Auto-reloads when code changes
- Shows detailed error messages
- Enables Flask debug toolbar

### Running in Production
For production deployment:
```bash
# Disable debug mode in app.py
app.run(debug=False, host='0.0.0.0', port=5000)

# Or use a production server like gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Endpoints

The application provides REST API endpoints:

- `GET /api/units` - List all units
- `GET /api/units/<id>` - Get unit details
- `GET /api/factions` - List factions
- `GET /api/search?q=<query>` - Search units
- `POST /api/calculate/attack` - Calculate attack outcomes
- `POST /api/compare/weapons` - Compare weapons
- `POST /api/simulate/combat` - Simulate combat
- `POST /api/load-dataset` - Reload dataset

## Support

For issues or questions:
- Check the README.md for general information
- Review datasets/README.md for dataset-related issues
- Open an issue on the repository

## Credits

- BSData community for the data format and repositories
- BattleScribe for the original application and format
- Games Workshop for Warhammer 40,000

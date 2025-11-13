# Warhammer 40k Mathhammer Tool

A web-based mathhammer calculator for Warhammer 40,000 10th Edition that supports importing BSData format datasets.

## Features

- **Attack Outcome Calculator**: Calculate expected hits, wounds, and damage
- **Weapon Effectiveness Comparison**: Compare different weapons against various targets
- **Unit vs Unit Combat Simulation**: Simulate full combat scenarios between units
- **BSData Import**: Import unit and weapon data from BSData repositories

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Mathhammer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser to `http://localhost:5000`

## Dataset Import

The tool supports importing datasets in BSData format (BattleScribe XML files):

- Place `.cat` (catalog) and `.gst` (game system) files in the `datasets/` directory
- Use the web interface to import and parse the datasets
- The default dataset is from [BSData/wh40k-10e](https://github.com/BSData/wh40k-10e)

## Project Structure

```
Mathhammer/
├── app.py                  # Flask web application
├── mathhammer/
│   ├── calculator.py       # Core calculation engine
│   ├── parser.py          # BSData XML parser
│   └── models.py          # Data models for units/weapons
├── static/
│   ├── css/               # Stylesheets
│   └── js/                # Frontend JavaScript
├── templates/
│   └── index.html         # Web interface
├── datasets/              # BSData files
└── requirements.txt       # Python dependencies
```

## Usage

### Attack Calculator
1. Select an attacking unit and weapon
2. Select a target unit
3. View calculated probabilities for hits, wounds, saves, and total damage

### Weapon Comparison
1. Select multiple weapons to compare
2. Choose a target profile
3. View side-by-side effectiveness metrics

### Combat Simulation
1. Select two units to fight
2. Configure unit sizes and special rules
3. Run simulation to see expected outcomes

## License

MIT License

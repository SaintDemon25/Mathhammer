# 🎮 Quick Start Guide - Warhammer 40k Combat Simulator

## Start in 3 Steps

### 1. Install Flask
```bash
pip install Flask
```

### 2. Run the App
```bash
python combat_app.py
```

### 3. Open Browser
Navigate to: **http://localhost:5000**

---

## First Simulation

### Example: Space Marine vs Ork

**Step 1 - Attacker (Space Marine with Bolt Rifle):**
- Attacks: 2
- BS: 3+
- Strength: 4
- AP: -1 (enter as 1)
- Damage: 1

**Step 2 - Defender (Ork Boy):**
- Toughness: 5
- Save: 6+
- Wounds per Model: 1
- Unit Size: 10

**Step 3 - Abilities:**
- No special abilities needed for basic test

**Step 4 - Simulate:**
- Simulations: 100
- Click "RUN SIMULATION"

You should see:
- Average hits: ~1.3
- Average wounds: ~0.6
- Average models killed: ~0.4

---

## Example With Abilities

### Plasma Gun with Lethal Hits & Devastating Wounds

**Attacker:**
- Attacks: 2
- BS: 3+
- Strength: 8
- AP: -3 (enter as 3)
- Damage: 2

**Defender (Terminator):**
- Toughness: 5
- Save: 2+
- Invuln: 4++
- Wounds: 3
- Unit Size: 5

**Abilities:**
- ✅ Lethal Hits
- ✅ Devastating Wounds
- ✅ Hazardous

**Results:** Watch critical hits auto-wound and critical wounds bypass the invuln save!

---

## Interface Navigation

### Progress Steps
1. **Attacker** - Configure weapon profile
2. **Defender** - Configure target profile
3. **Abilities** - Select special rules
4. **Simulate** - Run and view results

### Tips
- Hover over (ⓘ) for help on any field
- All ability toggles include descriptions
- Invalid inputs highlighted in red
- Can click step numbers to go back

---

## Common Scenarios to Test

### 1. Lethal Hits
```
Weapon: Any weapon
Abilities: ✅ Lethal Hits
Target: High toughness (T8+)
Result: See critical hits auto-wound!
```

### 2. Devastating Wounds
```
Weapon: High AP weapon
Abilities: ✅ Devastating Wounds
Target: Good save (2+ with invuln)
Result: Critical wounds bypass ALL saves!
```

### 3. Anti-Infantry
```
Weapon: Any anti-infantry weapon
Abilities: Anti-INFANTRY 4+, Sustained Hits 1
Target Keywords: INFANTRY
Result: More critical wounds + extra hits!
```

### 4. Cover vs Ignores Cover
```
Test A:
  Defender: ✅ Cover
  Weapon: No ignores cover

Test B:
  Defender: ✅ Cover
  Weapon: ✅ Ignores Cover

Compare: See the difference!
```

---

## Troubleshooting

### App won't start
```bash
# Make sure Flask is installed
pip install Flask

# Check for errors
python combat_app.py
```

### Port already in use
Edit `combat_app.py` line at bottom:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change port
```

### No results showing
- Make sure all required fields are filled
- Check browser console for errors (F12)
- Try with fewer simulations first (1 or 10)

---

## Testing the Engine

### Run Comprehensive Tests
```bash
python test_comprehensive.py
```

Should show:
```
✓ ALL TESTS PASSED!
SUMMARY: 13 passed, 0 failed
```

### Quick Combat Test
```bash
python combat_engine.py
```

Shows 3 example combats with different ability combinations.

---

## API Testing

### Test with curl
```bash
curl -X POST http://localhost:5000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "num_attacks": 10,
    "skill": 3,
    "strength": 4,
    "ap": 1,
    "damage": "1",
    "attack_type": "ranged",
    "toughness": 4,
    "save": 3,
    "wounds_per_model": 2,
    "unit_size": 5,
    "num_simulations": 100
  }'
```

---

## What's Included

### Core Files
- `combat_app.py` - Web application
- `combat_engine.py` - Combat rules engine
- `templates/combat_simulator.html` - Web interface
- `static/css/combat_sim.css` - Styling
- `static/js/combat_sim.js` - Interactivity

### Documentation
- `COMBAT_SIMULATOR_README.md` - Full documentation
- `QUICK_START.md` - This file
- `test_comprehensive.py` - Test suite

### Original Mathhammer
- Still intact in `app.py` and `mathhammer/`
- Can run original version: `python app.py`
- BSData parser fully functional

---

## Features Checklist

### ✅ Implemented
- [x] All core combat rules
- [x] All weapon abilities
- [x] All defensive abilities
- [x] Re-roll mechanics
- [x] Critical hit/wound mechanics
- [x] Modifier caps
- [x] Invulnerable saves
- [x] Feel No Pain
- [x] Cover mechanics
- [x] Statistical simulations
- [x] User-friendly GUI
- [x] Step-by-step wizard
- [x] Tooltips and help
- [x] REST API
- [x] Comprehensive tests

### 📝 Not Implemented (Future)
- [ ] Stratagems
- [ ] Psychic phase
- [ ] Multi-round combat
- [ ] Damage overflow
- [ ] Vehicle damage tables
- [ ] Visual charts/graphs
- [ ] Save/load configurations
- [ ] Points efficiency analysis

---

## Next Steps

1. ✅ Run the app
2. ✅ Try the examples above
3. ✅ Test your own unit matchups
4. ✅ Experiment with ability combinations
5. ✅ Run the test suite
6. ✅ Read full documentation
7. ✅ Have fun with mathhammer!

---

**Made with ⚔️ for the Warhammer community**

*For the Emperor! (or Chaos, Xenos, whatever you're into)*

# Pro Wrestling Sim - Developer Guide

## Project Overview
Python pro wrestling booking simulator with Flask web UI, Tkinter desktop UI, and CLI.

**Stack:** Python 3.10+, Flask + Bootstrap 5, JSON persistence, no database.
**Version:** v0.6+ (Post-MVP, Active Development)
**Repository:** https://github.com/yourusername/pro-wrestling (replace with actual URL)

---

## Architecture

### Directory Structure
```
src/core/       - Pure game logic (no I/O). Dataclasses, simulation, calculations.
src/services/   - Orchestration layer. GameService is the single API for all UIs.
src/ui/web/     - Flask app (app.py) + Jinja2 templates (21+ templates).
src/ui/desktop/ - Tkinter GUI (tkinter_app.py).
src/ui/cli/     - Text-based menu interface.
data/databases/ - Moddable JSON template databases.
saves/          - Per-save JSON files (wrestlers, titles, feuds, company, etc).
docs/           - System overhaul documents and roadmaps.
```

### Design Principles
**Key pattern:** `GameService` (services/game_service.py) is the sole entry point for all game operations. All three UIs call the same service methods. Core modules never do I/O.

**Architecture rules:**
1. **Core layer** (`core/`) - Pure game logic, no I/O, no print/input
2. **Services layer** (`services/`) - Orchestration, all UI calls go through `GameService`
3. **UI layer** (`ui/`) - All user interaction isolated here

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `src/core/wrestler.py` | Wrestler model (27 attributes, fighting styles, finishers, fatigue, injury) |
| `src/core/match.py` | Match simulation engine (10 match types, rating formulas) |
| `src/core/show.py` | Show runner, revenue engine, TV ratings |
| `src/core/game_state.py` | GameState dataclass, all result dataclasses, advance_week() |
| `src/core/economy.py` | Company (bank, prestige, viewers) and Contract |
| `src/core/auto_booker.py` | AI booking with 6-priority match card generation |
| `src/core/feud.py` | Feuds with auto-escalation (heated/intense/blood) |
| `src/core/stable.py` | Factions with interference mechanics |
| `src/core/calendar.py` | Weekly shows, PPV calendar, scheduling |
| `src/core/records.py` | Match history, streaks, H2H, title reigns |
| `src/core/news_feed.py` | News feed manager for backstage news items |
| `src/services/game_service.py` | Orchestration: show running, save/load, all game ops |
| `src/services/file_service.py` | JSON file I/O for all save data |
| `src/ui/web/app.py` | Flask routes (dashboard, booking, results, roster, etc) |

---

## Current Feature Set

### Core Game Features
- **10 Match Types:** Singles, Tag Team, Triple Threat, Fatal 4-Way, Ladder, Iron Man, Elimination Chamber, Money in the Bank, Royal Rumble, Steel Cage
- **27 Wrestler Attributes:** Physical (6), Offense (8), Defense (4), Entertainment (5), Intangibles (4)
- **Fighting Styles:** 10 styles (powerhouse, technician, high_flyer, brawler, etc.)
- **Finisher/Signature System:** Each wrestler has named finishers with damage ratings
- **Fatigue & Injury:** Condition/stamina drain, injury risk, recovery mechanics
- **TV Ratings & Attendance:** Viewership tracking, ratings calculation, revenue engine
- **Feuds:** Auto-escalating feuds with rating bonuses (heated/intense/blood)
- **Stables:** Factions with interference mechanics and shared heat
- **Tag Teams:** Chemistry system affecting match ratings
- **AI Auto-Booking:** Priority-based card generation (feuds > titles > rankings)
- **Records System:** Match history, streaks, H2H records, title reign history
- **News Feed:** Backstage news for major events (title changes, injuries, 5-star matches)
- **Economy:** Bank account, ticket revenue, PPV buys, prestige system
- **Calendar:** 52-week year, 12 PPVs, weekly shows, brand assignments

### UI Features
- **Three Interfaces:** Web UI (Flask), Desktop UI (Tkinter), CLI
- **Dashboard:** Rankings, titles, feuds, stables, company stats, news feed
- **Booking System:** Manual booking + AI suggestions with accept/reject
- **Results Display:** Match ratings, commentary, financial reports, broadcast stats
- **Roster Management:** Create/edit wrestlers, assign to brands
- **Title Management:** Create titles, book defenses, view reign history

---

## Completed Roadmap Items (v0.6)

| Feature | Status | Details |
|---------|--------|---------|
| **Fatigue/Injury System** | ✅ DONE | Condition drain, injury risk, recovery, booking enforcement |
| **TV Ratings & Attendance** | ✅ DONE | Viewership, ratings scale, attendance, revenue engine, prestige |
| **Backstage News Feed** | ✅ DONE | NewsFeedManager, dashboard card, persists to news.json |
| **Wrestler Rating Overhaul** | ✅ DONE | 27 attributes, fighting styles, finisher system, tier system |
| **Web UI** | ✅ DONE | Full Flask UI with Bootstrap 5, 21+ templates |

---

## Upcoming Work

### Priority 1: Match Commentary Overhaul
**Status:** NOT STARTED
**Difficulty:** High
**Impact:** High

Replace static commentary templates with procedural narrative generation driven by wrestler fighting styles, finishers, and match stats. See `docs/COMMENTARY_SYSTEM_OVERHAUL.md` for details.

### Priority 2: Calendar & Brand System Enhancements
**Status:** PARTIAL (basic calendar exists, needs visual UI + multi-show weeks)
**Difficulty:** High
**Impact:** High

Add visual calendar UI, support multiple shows per week, custom PPV calendar management. See `docs/CALENDAR_SYSTEM_OVERHAUL.md` and `docs/MULTI_SHOW_AND_PPV_CHANGES.md`.

### Priority 3: UI Polish
**Status:** IN PROGRESS
**Difficulty:** Medium
**Impact:** Medium

Web UI functional but needs visual polish. Better color usage, card designs, typography. See `WEB_UI_TODO.md` for specific issues.

---

## Development Workflow

### Before Starting Work
1. **Pull latest changes** from GitHub
2. **Create a feature branch** for your work: `git checkout -b feature/your-feature-name`
3. **Read relevant docs** in `docs/` folder if working on a major system
4. **Test with a fresh save** to verify existing functionality works

### While Working
1. **Make incremental commits** with clear messages
2. **Test frequently** via the web UI (run `Play Web.bat`)
3. **Follow architecture rules** (keep core layer I/O-free)
4. **Update CLAUDE.md** if adding new major features or files

### After Completing Work
1. **Test with both new and existing saves** (migration testing)
2. **Commit all changes** with descriptive message
3. **Push to GitHub** (see Git Workflow below)
4. **Update roadmap docs** if feature is complete

---

## Git Workflow

### IMPORTANT: Always Push Changes to GitHub

After completing work, ALWAYS push your changes to the remote repository:

```bash
# 1. Check status
git status

# 2. Stage all changes
git add .

# 3. Commit with descriptive message
git commit -m "Descriptive message about what was done"

# 4. Push to GitHub (main branch or feature branch)
git push origin main

# OR if on a feature branch:
git push origin feature/your-feature-name
```

### Commit Message Guidelines
- **Use present tense:** "Add feature" not "Added feature"
- **Be specific:** "Fix Royal Rumble star_power attribute error" not "Fix bug"
- **Reference systems:** "Update wrestler.py: Add finisher system with 27 attributes"
- **Group related changes:** One commit per logical unit of work

### When to Push
- **After completing a feature** (even if small)
- **After fixing a bug**
- **After updating documentation**
- **At the end of each session**
- **Before switching tasks**

### Branching Strategy (Optional)
For major features, consider using feature branches:
```bash
# Create feature branch
git checkout -b feature/commentary-overhaul

# Work on feature, commit frequently
git add .
git commit -m "Add phased commentary generation"

# When feature complete, merge to main
git checkout main
git merge feature/commentary-overhaul
git push origin main
```

---

## Testing & Verification

### No Automated Tests
No test suite exists. All verification is manual via UI.

### Manual Testing Checklist
- [ ] Create new game - verify roster loads
- [ ] Book all match types - verify each simulates correctly
- [ ] Run show - verify results display properly
- [ ] Save/Load game - verify state persists
- [ ] Test with existing save - verify backward compatibility
- [ ] Check news feed - verify events generate news
- [ ] Test AI booking - verify card suggestions work
- [ ] Check records - verify stats track correctly

### Common Test Scenarios
1. **New save with default database**
2. **Existing v0.5 save** (migration test)
3. **Edge cases:** Injured wrestlers, empty roster, no titles
4. **Multi-match shows:** Mix of all match types
5. **Feud completion:** Blowoff matches and auto-resolution

---

## Data Format & Save Files

### Save Game Structure
All JSON. Each save folder contains:
- `wrestlers.json` - Wrestler roster with all attributes
- `tag_teams.json` - Tag teams with chemistry
- `titles.json` - Championship titles
- `feuds.json` - Active feuds
- `stables.json` - Factions
- `records.json` - Match history and stats
- `company.json` - Bank, prestige, viewers
- `game_state.json` - Current week, year, metadata
- `calendar.json` - Schedule, weekly shows
- `brands.json` - Brand split data
- `weekly_shows.json` - Recurring show definitions
- `news.json` - News feed items

### Backward Compatibility
When modifying data structures:
1. Add new fields with default values in `__init__`
2. Keep old field names as aliases when possible
3. Write migration logic in `from_dict()` methods
4. Test loading old saves before committing

---

## Running the Game

### Web UI (Recommended)
```bash
# Double-click:
Play Web.bat

# OR from terminal:
cd src\ui\web
python app.py
```
Then open http://127.0.0.1:5000

### Desktop UI
```bash
# Double-click:
Play Wrestling.bat

# OR from terminal:
cd src\ui\desktop
python tkinter_app.py
```

### CLI
```bash
cd src
python main.py
```

---

## Reference Documentation

### System Overhaul Documents
Detailed technical specs for major system overhauls located in `docs/`:

- **[Wrestler Rating Overhaul](docs/WRESTLER_RATING_OVERHAUL.md)** - 27 attributes, fighting styles ✅ COMPLETE
- **[Calendar System Overhaul](docs/CALENDAR_SYSTEM_OVERHAUL.md)** - Visual calendar, brands, weekly shows
- **[Commentary System Overhaul](docs/COMMENTARY_SYSTEM_OVERHAUL.md)** - Phased commentary, talking segments
- **[Multi-Show & PPV Changes](docs/MULTI_SHOW_AND_PPV_CHANGES.md)** - Multiple shows per week, custom PPVs
- **[Development Roadmap](docs/README.md)** - Master index and implementation order

### Additional Resources
- **wrestlers.md** - Reference data for top 20 wrestlers (peak ratings)
- **WEB_UI_TODO.md** - Web UI improvement tasks and issues

---

## Quick Reference

### Wrestler Stats (27 total)
- **Physical (6):** strength, speed, agility, durability, stamina, recovery
- **Offense (8):** striking, grappling, submission, high_flying, hardcore, power_moves, technical, dirty_tactics
- **Defense (4):** strike_defense, grapple_defense, aerial_defense, ring_awareness
- **Entertainment (5):** mic_skills, charisma, look, star_power, entrance
- **Intangibles (4):** psychology, consistency, big_match, clutch

### Legacy Attribute Aliases (for old code)
- `brawl` → `striking`
- `tech` → `technical`
- `air` → `high_flying`
- `psych` → `psychology`
- `mic` → `mic_skills`

### Match Rating Factors
- Base: Average of wrestler stats (overall, specific skills)
- Style match: Fighting style compatibility
- Chemistry: Tag team chemistry (for tag matches)
- Feud bonus: +3 (heated), +6 (intense), +10 (blood)
- Condition penalty: Up to -15 if avg condition < 50
- Match type bonus: Chamber +12, MITB +15, etc.

---

## Notes for AI Assistants

- **Always check CLAUDE.md** before starting work for current context
- **Read relevant docs/** files for major system changes
- **Follow architecture rules** strictly (no I/O in core/)
- **Test via web UI** for verification
- **Update this file** when adding major features
- **Push to GitHub** after completing work (critical!)

---

**Last Updated:** 2026-02-01
**Current Version:** v0.6+
**Status:** Active Development

# Pro Wrestling Sim - MVP Completion Roadmap

**Created:** January 17, 2026
**Status:** POST-MVP - Phase F Complete + Web UI (ALL PHASES COMPLETE)
**Last Session:** Added Flask Web UI

---

## Current State Summary

### MVP Features - ALL COMPLETE
- Match simulation engine (singles, tag team, Royal Rumble)
- Wrestler stats system (9 stats across ring work and entertainment)
- Tag team system with chemistry mechanics
- Win/loss tracking and rankings (Top 5 singles, Top 5 tag)
- 12-PPV calendar system
- Save/load with auto-save after shows
- Steel cage match variant
- Match commentary generation
- Title system with title match booking and title changes
- Create wrestlers and titles in-game
- Royal Rumble (10-man elimination)
- CLI fully functional
- Tkinter Desktop UI fully functional

### Post-MVP Progress - ALL COMPLETE
- [x] Phase A: Feuds & Storylines - COMPLETE
- [x] Phase B: Stables - COMPLETE
- [x] Phase C: AI Auto-Booking - COMPLETE
  - [x] Card suggestion generation
  - [x] Priority-based booking (feuds > titles > rankings)
  - [x] TV vs PPV card sizing
  - [x] Feud suggestions
  - [x] User override (accept/reject matches)
- [x] Phase D: Additional Match Types - COMPLETE
  - [x] Triple Threat
  - [x] Fatal 4-Way
  - [x] Ladder Match
  - [x] Iron Man Match
- [x] Phase E: Records & Standings System - COMPLETE
  - [x] Match History Log
  - [x] Win/Loss Streaks
  - [x] Head-to-Head Records
  - [x] Title Reign History
  - [x] PPV vs TV Stats
- [x] Phase F: Gimmick Match Types - COMPLETE
  - [x] Elimination Chamber (6-man pod-based elimination)
  - [x] Money in the Bank (6-8 man ladder match with briefcase contract)

### Future Backlog (Optional)
- [ ] No DQ/Hardcore Match
- [ ] Tables Match
- [ ] Battle Royal
- [ ] Hell in a Cell

---

## Phase 1: Quick Wins - COMPLETE

### Task 1.1: Title Match Booking (CLI) - COMPLETE
### Task 1.2: View Titles Screen (CLI) - COMPLETE
### Task 1.3: Add Wrestler (CLI) - COMPLETE
### Task 1.4: Add Title (CLI) - COMPLETE
### Task 1.5: Royal Rumble Match Type - COMPLETE

---

## Phase 2: Desktop UI - COMPLETE (Tkinter)

All features from CLI implemented in Tkinter GUI.

---

## Phase A: Feuds & Storylines - COMPLETE

**Completed:** January 18, 2026

### Features Implemented

| Feature | Description |
|---------|-------------|
| Feud Data Model | `src/core/feud.py` with full persistence |
| One-Feud Limit | Each wrestler can only be in one active feud |
| Rating Bonuses | Heated (+3), Intense (+6), Blood (+10) |
| Auto-Resolution | Feud ends after set number of matches |
| Intensity Escalation | heated → intense (2 matches) → blood (4 matches) |
| Blowoff Match | Schedule next match to end feud |
| Feud Commentary | 20+ feud-specific commentary lines |
| CLI Management | Full feud CRUD in Head Office menu |
| Tkinter Management | Full feud CRUD with dialogs |
| Booking Indicators | Shows feud status when booking matches |
| Results Display | Feud info and resolution in show results |

### Files Created
- `src/core/feud.py` - Feud dataclass and persistence

### Files Modified
- `src/core/game_state.py` - Added feuds list, lookup methods, MatchResult fields
- `src/services/file_service.py` - Added `get_feuds_path()`
- `src/services/game_service.py` - Added 7 feud API methods
- `src/core/match.py` - Added feud field and rating bonus
- `src/core/show.py` - Auto-detect feuds, record results, track ending
- `src/core/commentary.py` - Added feud commentary by intensity
- `src/ui/cli/cli_app.py` - Feud management menu and screens
- `src/ui/desktop/tkinter_app.py` - Feud management button and dialogs

### Data Persistence
Feuds saved to `saves/[FedName]/feuds.json`

---

## Phase B: Stables - COMPLETE

**Completed:** January 18, 2026

### Features Implemented

| Feature | Description |
|---------|-------------|
| Stable Data Model | `src/core/stable.py` with full persistence |
| Minimum 3 Members | Enforced on create and when removing |
| One Leader | Each stable has designated leader |
| One Stable Limit | Wrestlers can only be in one active stable |
| Power Rating | Average of member overall ratings |
| Shared Heat | Winner's stablemates +2 heat, loser's stablemates -1 |
| Match Interference | 20% base chance (40% if losing), 70% helps / 30% DQ backfire |
| Interference Rating | Clean interference +3, DQ -5 to match rating |
| Interference Commentary | 14 new commentary lines for interference |
| CLI Management | Full stable CRUD in Head Office menu |
| Tkinter Management | Full stable CRUD with dialogs |
| Results Display | Interference shown in match results |

### Files Created
- `src/core/stable.py` - Stable dataclass and persistence

### Files Modified
- `src/core/game_state.py` - Added stables list, lookup methods, interference fields
- `src/services/file_service.py` - Added `get_stables_path()`
- `src/services/game_service.py` - Added 8 stable API methods
- `src/core/match.py` - Added interference logic with stable detection
- `src/core/show.py` - Added shared heat, interference commentary
- `src/core/commentary.py` - Added interference commentary lines
- `src/ui/cli/cli_app.py` - Stable management menu and screens
- `src/ui/desktop/tkinter_app.py` - Stable management button and dialogs

### Data Persistence
Stables saved to `saves/[FedName]/stables.json`

---

## Completed Post-MVP Phases

### Phase C: AI Auto-Booking - COMPLETE

**Completed:** January 21, 2026

### Features Implemented

| Feature | Description |
|---------|-------------|
| Card Suggestions | AI generates complete match cards based on game state |
| Priority-Based Booking | Blowoff > Titles > Tags > Feuds > Rankings > Variety |
| Title Matches PPV Only | Title defenses only occur on PPV events |
| Tag Title Detection | Titles with "Tag" in name defended as tag matches |
| TV vs PPV Sizing | TV shows get 4-5 matches, PPVs get 6-8 matches |
| Contender Selection | Feud opponent > #1 ranked > Win streak > Top tier random |
| Feud Suggestions | AI suggests new feuds based on heat and rankings |
| User Override | Accept/reject individual matches via checkboxes |
| CLI Integration | AI Suggest Card option with toggle and regenerate |
| Tkinter Integration | AI Book Show button with visual checkbox interface |

### Files Created
- `src/core/auto_booker.py` - AutoBooker class, MatchSuggestion, FeudSuggestion, CardSuggestion dataclasses

### Files Modified
- `src/services/game_service.py` - Added get_card_suggestions(), apply_card_suggestions(), start_suggested_feud()
- `src/ui/cli/cli_app.py` - Added AI booking flow with choice screen, suggestion display, toggle matches
- `src/ui/desktop/tkinter_app.py` - Added AI Book Show button and suggestion dialog with checkboxes

### Booking Algorithm
1. **Blowoff Matches** (MANDATORY) - Feuds with blowoff scheduled
2. **Title Defenses** (PPV ONLY) - All held titles; tag titles as tag matches
3. **Tag Team Matches** - 1-2 on PPV, 1 on TV (booked early to guarantee slots)
4. **Active Feuds** - Book feud participants against each other
5. **Rankings-Based** - Top-ranked wrestlers in meaningful matches (limited to leave room)
6. **Variety Fill** - Multi-man matches for card diversity

---

### Phase D: Additional Match Types - COMPLETE

**Completed:** January 19, 2026

### Features Implemented

| Feature | Description |
|---------|-------------|
| Triple Threat | 3-man match, first pinfall wins, MultiManMatch class |
| Fatal 4-Way | 4-man match, first pinfall wins, MultiManMatch class |
| Ladder Match | Climb to retrieve prize, favors Air stat |
| Iron Man Match | Timed match (30/60 min), most falls wins, can draw |

### Files Created
- `src/core/match.py` - Added MultiManMatch, LadderMatch, IronManMatch classes

### Files Modified
- `src/core/game_state.py` - Added MultiManResult, LadderMatchResult, IronManResult
- `src/core/show.py` - Added match lists, booking methods, processing
- `src/services/game_service.py` - Added add_multi_man_match_to_show, add_ladder_match_to_show, add_iron_man_match_to_show
- `src/ui/cli/cli_app.py` - Added booking flows and result displays for all new types
- `src/ui/desktop/tkinter_app.py` - Added dialogs and result displays for all new types

---

### Phase E: Records & Standings System - COMPLETE

**Completed:** January 20, 2026

### Features Implemented

| Feature | Description |
|---------|-------------|
| Match History Log | Full record of every match with date, participants, winner, rating |
| Win/Loss Streaks | Current and longest streaks tracked per wrestler |
| Head-to-Head Records | Lookup win/loss record between any two wrestlers |
| Title Reign History | Track all reigns with won/lost dates and successful defenses |
| PPV vs TV Stats | Separate win/loss records for PPV and TV shows |
| PPV Auto-Detection | Shows on PPV weeks automatically flagged as PPV |

### Files Created
- `src/core/records.py` - MatchHistoryEntry, WrestlerRecords, TitleReign, RecordsManager

### Files Modified
- `src/core/game_state.py` - Added records field to GameState
- `src/core/show.py` - Added is_ppv parameter, match recording after each match type
- `src/core/calendar.py` - Added is_ppv_week() and get_ppv_for_week() helpers
- `src/services/file_service.py` - Added get_records_path(), load_records_data(), save_records_data()
- `src/services/game_service.py` - Added 5 records API methods, PPV auto-detection
- `src/ui/cli/cli_app.py` - Added Records & History menu with 4 screens
- `src/ui/desktop/tkinter_app.py` - Added Records & History button with 4 dialogs

### Data Persistence
Records saved to `saves/[FedName]/records.json`

### Backward Compatibility
- Existing saves load with empty history (no data loss)
- History starts recording from when feature is added

---

### Phase F: Gimmick Match Types - COMPLETE

**Completed:** January 22, 2026

### Features Implemented

| Feature | Description |
|---------|-------------|
| Elimination Chamber | 6-man elimination match, 2 start + 4 pods, last survivor wins |
| Chamber Pod System | Wrestlers released at intervals, early entrants take more damage |
| Chamber Title Matches | Can be booked as championship matches |
| Money in the Bank | 6-8 wrestler ladder match for a briefcase contract |
| MITB Briefcase | Winner gets `has_mitb_briefcase` flag for future title shot |
| MITB Cash-In | API method to cash in briefcase (removes flag) |
| AI Booking Support | Auto-booker can suggest chamber and mitb match types |

### Files Modified
- `src/core/match.py` - Added EliminationChamberMatch and MoneyInTheBankMatch classes
- `src/core/wrestler.py` - Added `has_mitb_briefcase` attribute with persistence
- `src/core/game_state.py` - Added EliminationChamberResult and MoneyInTheBankResult dataclasses
- `src/core/show.py` - Added chamber_matches and mitb_matches lists, booking methods, run processing
- `src/core/auto_booker.py` - Added chamber and mitb match type support
- `src/services/game_service.py` - Added add_chamber_match_to_show(), add_mitb_match_to_show(), get_mitb_holder(), cash_in_mitb()
- `src/ui/cli/cli_app.py` - Added Chamber and MITB booking flows and result display
- `src/ui/desktop/tkinter_app.py` - Added Chamber and MITB dialogs and result display

### Match Mechanics

**Elimination Chamber:**
- 6 wrestlers required
- First 2 start in ring, wrestlers 3-6 in pods
- Pods release at timed intervals
- Elimination by pinfall/submission
- Damage accumulates - early entrants are disadvantaged
- Favors stamina and brawl stats
- +12 rating bonus for spectacle

**Money in the Bank:**
- 6-8 wrestlers required
- Ladder match variant
- Winner retrieves briefcase
- Grants `has_mitb_briefcase = True` on wrestler
- Briefcase allows future title shot cash-in
- Favors Air stat (climbing)
- +15 rating bonus for spectacle

---

## Technical Reference

### Key File Locations

| Component | Path |
|-----------|------|
| Entry point | `src/main.py` |
| Game API | `src/services/game_service.py` |
| File I/O | `src/services/file_service.py` |
| CLI | `src/ui/cli/cli_app.py` |
| Desktop UI | `src/ui/desktop/tkinter_app.py` |
| **Web UI** | `src/ui/web/app.py` |
| **Web Templates** | `src/ui/web/templates/*.html` |
| Match engine | `src/core/match.py` |
| Show runner | `src/core/show.py` |
| Wrestler model | `src/core/wrestler.py` |
| Tag team model | `src/core/tag_team.py` |
| Title model | `src/core/title.py` |
| **Feud model** | `src/core/feud.py` |
| **Stable model** | `src/core/stable.py` |
| **Records model** | `src/core/records.py` |
| **Auto-Booker** | `src/core/auto_booker.py` |
| Economy | `src/core/economy.py` |
| Calendar | `src/core/calendar.py` |
| Commentary | `src/core/commentary.py` |
| Rankings | `src/core/ranking.py` |
| Data classes | `src/core/game_state.py` |

### Architecture Rules
1. **Core layer** (`core/`): Pure game logic, no I/O, no print/input
2. **Services layer** (`services/`): Orchestration, all UI calls go through `GameService`
3. **UI layer** (`ui/`): All user interaction isolated here

### Running the Game
```bash
cd D:\simple_sim_sports\pro-wrestling\src
python main.py
```

### Running Desktop UI
**Double-click (no terminal):**
- `Play Wrestling.bat`
- `play.pyw`

**From terminal:**
```bash
cd D:\simple_sim_sports\pro-wrestling\src\ui\desktop
python tkinter_app.py
```

### Running Web UI (NEW!)
**Double-click:**
- `Play Web.bat`

**From terminal:**
```bash
cd D:\simple_sim_sports\pro-wrestling\src\ui\web
python app.py
```
Then open http://127.0.0.1:5000 in your browser.

**Requirements:** `pip install flask`

---

## Session Handoff Notes

**Web UI Added - January 22, 2026**

### What was done this session:

**Flask Web UI - COMPLETE**
- Created complete Flask web application at `src/ui/web/app.py`
- Built 21 HTML templates with Bootstrap 5 dark theme
- Wrestling-themed styling (gold/red/black color scheme)
- All features from CLI/Tkinter now available in web browser:
  - Dashboard with federation overview
  - Roster management with wrestler profiles
  - Show booking (manual and AI-assisted)
  - All match types supported
  - Title management with history
  - Feud management
  - Stable management
  - Tag team management
  - Records & history
  - Head-to-head lookups
- Created `Play Web.bat` for easy launch
- Updated requirements.txt with Flask dependency

### Files Created:
- `src/ui/web/app.py` - Flask application (720+ lines)
- `src/ui/web/templates/base.html` - Base template with Bootstrap dark theme
- `src/ui/web/templates/index.html` - Start menu (new/load game)
- `src/ui/web/templates/dashboard.html` - Main dashboard
- `src/ui/web/templates/roster.html` - Roster view
- `src/ui/web/templates/wrestler.html` - Wrestler profile
- `src/ui/web/templates/booking.html` - Show booking
- `src/ui/web/templates/ai_booking.html` - AI booking interface
- `src/ui/web/templates/results.html` - Show results
- `src/ui/web/templates/titles.html` - Titles view
- `src/ui/web/templates/title_history.html` - Title reign history
- `src/ui/web/templates/rankings.html` - Rankings
- `src/ui/web/templates/feuds.html` - Feud management
- `src/ui/web/templates/stables.html` - Stable management
- `src/ui/web/templates/tag_teams.html` - Tag team management
- `src/ui/web/templates/records.html` - Match history
- `src/ui/web/templates/head_to_head.html` - H2H lookup
- `src/ui/web/templates/create_wrestler.html` - Create wrestler form
- `src/ui/web/templates/create_title.html` - Create title form
- `src/ui/web/templates/create_feud.html` - Start feud form
- `src/ui/web/templates/create_stable.html` - Create stable form
- `src/ui/web/templates/create_tag_team.html` - Create tag team form
- `Play Web.bat` - Launch script

---

**Phase F Complete - January 22, 2026**

### What was done this session:

**Phase F: Gimmick Match Types - COMPLETE**
- Created EliminationChamberMatch class with 6-man pod-based elimination system
- Created MoneyInTheBankMatch class with 6-8 wrestler ladder match and briefcase
- Added `has_mitb_briefcase` attribute to Wrestler class with persistence
- Added EliminationChamberResult and MoneyInTheBankResult dataclasses
- Integrated new match types into show.py with full processing
- Added GameService API methods: add_chamber_match_to_show(), add_mitb_match_to_show(), get_mitb_holder(), cash_in_mitb()
- Added CLI booking flows for both match types with result display
- Added Tkinter dialogs for both match types with result display
- Updated auto_booker.py to support chamber and mitb match suggestions
- Updated _apply_match_suggestion to handle new match types

### Key Features:
- **Elimination Chamber**: 6 wrestlers, 2 start + 4 pods, survival-based elimination, favors stamina/brawl
- **Money in the Bank**: 6-8 wrestlers, ladder match, winner gets briefcase for future title shot
- **MITB Briefcase System**: Tracked on wrestler, can be cashed in via API

---

**Phase C Complete - January 21, 2026**

### What was done that session:

**Phase C: AI Auto-Booking - COMPLETE**
- Created `src/core/auto_booker.py` with AutoBooker class and dataclasses
- Added GameService API methods for card suggestions
- Added CLI "AI Suggest Card" flow with toggle, regenerate, manual fallback
- Added Tkinter "AI Book Show" button with checkbox-based suggestion dialog

### Key Features Implemented:
- **AutoBooker Class**: Generates complete match cards based on game state
- **Priority-Based Algorithm**: Blowoff > Titles > Feuds > Rankings > Tag Teams > Variety
- **Card Sizing**: TV shows get 4-5 matches, PPVs get 6-8 matches
- **Contender Selection**: Smart title challenger selection (feud > ranked > hot > random)
- **Feud Suggestions**: AI recommends new feuds based on heat and rankings
- **User Override**: Accept/reject individual matches before running show

### Files Created This Session:
- `src/core/auto_booker.py` - MatchSuggestion, FeudSuggestion, CardSuggestion, AutoBooker

### Files Modified This Session:
- `src/services/game_service.py` - Added get_card_suggestions(), apply_card_suggestions(), start_suggested_feud(), _apply_match_suggestion()
- `src/ui/cli/cli_app.py` - Added _book_show_screen() choice, _ai_booking_flow(), _display_match_suggestion(), _toggle_match_flow(), _start_feud_from_suggestion(), _manual_booking_flow()
- `src/ui/desktop/tkinter_app.py` - Added show_ai_booking(), _display_ai_booking_screen(), _toggle_match_var(), _format_match_description(), _apply_ai_suggestion(), _regenerate_suggestions(), _start_suggested_feud()

---

## NEXT SESSION: What To Do

### ALL PHASES COMPLETE!
Phases A through F are all complete. The game is fully functional with all planned features.

### Optional Future Enhancements
If additional match types are desired:
- No DQ/Hardcore Match
- Tables Match
- Battle Royal
- Hell in a Cell

### Other Potential Features
- Brand/roster split system
- Custom wrestler movesets in commentary
- Enhanced AI booking (auto-book entire seasons)
- Tournament bracket system
- Career mode

---

## Previous Session Notes

**Phase E Complete - January 20, 2026**

### What was done that session:

**Phase E: Records & Standings System - COMPLETE**
- Created `src/core/records.py` with MatchHistoryEntry, WrestlerRecords, TitleReign, RecordsManager dataclasses
- Added persistence functions to file_service.py for records.json
- Integrated records into GameState and game_service load/save
- Modified show.py to record all match types after simulation
- Added PPV auto-detection using calendar system
- Added CLI "View Records & History" menu with 4 screens
- Added Tkinter "Records & History" button with 4 dialogs


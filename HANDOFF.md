# Pro Wrestling Sim - Technical Handoff Document

**Date:** February 1, 2026
**Version:** v0.6.1
**Status:** Production-Ready, Active Development
**Last Updated By:** Development Team (AI-Assisted)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Core Systems](#core-systems)
6. [UI Implementation](#ui-implementation)
7. [Data Persistence](#data-persistence)
8. [Development Workflow](#development-workflow)
9. [Recent Changes](#recent-changes)
10. [Known Issues](#known-issues)
11. [Next Steps](#next-steps)
12. [Code Patterns & Examples](#code-patterns--examples)
13. [Testing & Deployment](#testing--deployment)

---

## Executive Summary

**What is this?**
A Python-based pro wrestling booking simulator with three UI modes (Web, Desktop, CLI). Users manage a wrestling federation, book shows, create storylines, and simulate matches.

**Current State:**
- ✅ Fully functional with 10 match types
- ✅ Modern dark-themed web UI with glassmorphism
- ✅ AI auto-booking system
- ✅ Comprehensive records and statistics
- ✅ Feuds, stables, tag teams
- ✅ Fatigue/injury system
- ✅ TV ratings and financial simulation

**Production Ready:** Yes, all core features work
**Test Coverage:** Manual testing only (no automated tests)
**Documentation:** CLAUDE.md (dev guide), docs/ (technical specs)

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER INTERFACES                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ Flask UI │  │ Tkinter  │  │   CLI    │             │
│  │  (Web)   │  │ (Desktop)│  │  (Text)  │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
│       │             │              │                    │
│       └─────────────┴──────────────┘                    │
│                     │                                    │
│              ┌──────▼──────┐                            │
│              │ GameService │  (Single API Layer)        │
│              └──────┬──────┘                            │
│                     │                                    │
│       ┌─────────────┼─────────────┐                    │
│       │             │              │                    │
│  ┌────▼────┐  ┌────▼────┐  ┌─────▼─────┐             │
│  │  Core   │  │ Services │  │   Data    │             │
│  │ Logic   │  │  Layer   │  │   (JSON)  │             │
│  └─────────┘  └──────────┘  └───────────┘             │
└─────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Separation of Concerns**
   - `core/` = Pure game logic (NO I/O, NO print/input)
   - `services/` = Orchestration layer (file I/O, API methods)
   - `ui/` = User interfaces (all three modes)

2. **Single API Pattern**
   - ALL UIs call the SAME GameService methods
   - No code duplication between interfaces
   - Easy to add new UIs

3. **Data-Driven**
   - All game data in JSON files
   - Fully moddable databases
   - Human-readable save files

---

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Language** | Python | 3.10+ | Core logic |
| **Web Framework** | Flask | 3.0+ | Web UI |
| **Desktop UI** | Tkinter | Built-in | Desktop GUI |
| **Data Format** | JSON | Native | Persistence |
| **CSS Framework** | Bootstrap 5 | 5.3.2 | Web styling |
| **Icons** | Bootstrap Icons | 1.11.1 | UI icons |

### Dependencies

```txt
Flask>=3.0.0
```

**That's it!** Tkinter is built-in to Python, everything else is standard library.

### Browser Compatibility

- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari
- ⚠️ IE11 not supported (modern CSS features)

---

## Project Structure

```
pro-wrestling/
├── src/
│   ├── main.py                    # CLI entry point
│   ├── core/                      # Game logic (NO I/O)
│   │   ├── wrestler.py            # Wrestler model (27 attrs)
│   │   ├── match.py               # Match simulation (10 types)
│   │   ├── show.py                # Show runner, revenue
│   │   ├── game_state.py          # GameState, result classes
│   │   ├── economy.py             # Company, Contract
│   │   ├── auto_booker.py         # AI booking logic
│   │   ├── feud.py                # Feuds with escalation
│   │   ├── stable.py              # Factions/stables
│   │   ├── tag_team.py            # Tag teams
│   │   ├── title.py               # Championships
│   │   ├── calendar.py            # Calendar, PPVs
│   │   ├── records.py             # Match history, stats
│   │   ├── news_feed.py           # News generation
│   │   ├── commentary.py          # Match commentary
│   │   ├── ranking.py             # Rankings calculation
│   │   └── brand.py               # Brand split
│   │
│   ├── services/                  # Orchestration
│   │   ├── game_service.py        # MAIN API (600+ lines)
│   │   └── file_service.py        # JSON I/O
│   │
│   └── ui/                        # User Interfaces
│       ├── web/                   # Flask Web UI
│       │   ├── app.py             # Flask routes (720+ lines)
│       │   ├── templates/         # 21 Jinja2 templates
│       │   │   ├── base.html      # Base template
│       │   │   ├── dashboard.html # Main dashboard
│       │   │   ├── booking.html   # Show booking
│       │   │   └── ...
│       │   └── static/
│       │       └── css/
│       │           └── style.css  # Dark theme (900+ lines)
│       │
│       ├── desktop/               # Tkinter GUI
│       │   └── tkinter_app.py     # Desktop UI (1200+ lines)
│       │
│       └── cli/                   # Text-based
│           └── cli_app.py         # CLI (1500+ lines)
│
├── data/
│   └── databases/
│       └── default/
│           ├── wrestlers.json     # Template roster
│           ├── tag_teams.json     # Template teams
│           └── titles.json        # Template championships
│
├── saves/                         # User save games
│   └── [SaveName]/
│       ├── wrestlers.json
│       ├── tag_teams.json
│       ├── titles.json
│       ├── feuds.json
│       ├── stables.json
│       ├── records.json
│       ├── company.json
│       ├── game_state.json
│       ├── calendar.json
│       ├── brands.json
│       ├── weekly_shows.json
│       └── news.json
│
├── docs/                          # Technical specs
│   ├── README.md                  # Overhaul index
│   ├── WRESTLER_RATING_OVERHAUL.md
│   ├── CALENDAR_SYSTEM_OVERHAUL.md
│   ├── COMMENTARY_SYSTEM_OVERHAUL.md
│   └── MULTI_SHOW_AND_PPV_CHANGES.md
│
├── CLAUDE.md                      # Developer guide
├── HANDOFF.md                     # This document
├── wrestlers.md                   # Reference data
├── WEB_UI_TODO.md                 # UI improvement tasks
├── Play Web.bat                   # Launch web UI
├── Play Wrestling.bat             # Launch desktop UI
├── play.pyw                       # Launch desktop (no console)
└── requirements.txt               # Python dependencies
```

---

## Core Systems

### 1. Wrestler System

**File:** `src/core/wrestler.py` (590 lines)

**27 Attributes Organized in 5 Categories:**

```python
# Physical (6)
strength, speed, agility, durability, stamina, recovery

# Offense (8)
striking, grappling, submission, high_flying, hardcore,
power_moves, technical, dirty_tactics

# Defense (4)
strike_defense, grapple_defense, aerial_defense, ring_awareness

# Entertainment (5)
mic_skills, charisma, look, star_power, entrance

# Intangibles (4)
psychology, consistency, big_match, clutch
```

**Key Features:**
- `FightingStyle` enum (10 styles: powerhouse, technician, high_flyer, etc.)
- Finisher/signature move system
- Fatigue/injury tracking
- Dynamic overall rating calculation
- Legacy attribute aliases for backward compatibility

**Code Example:**
```python
from core.wrestler import Wrestler, FightingStyle

# Create wrestler
wrestler = Wrestler(
    id=1,
    name="Stone Cold Steve Austin",
    age=32,
    alignment="Face",
    primary_style=FightingStyle.BRAWLER,

    # Physical
    strength=85,
    speed=75,
    agility=70,
    durability=90,
    stamina=85,
    recovery=80,

    # ... (27 total attributes)

    finisher_name="Stone Cold Stunner",
    finisher_type="Striking",
    finisher_damage=95
)

# Get overall rating (calculated)
rating = wrestler.get_overall_rating()  # 0-100

# Update after match (fatigue/injury)
wrestler.update_after_match(match_length=15)
wrestler.check_injury_risk()  # Returns True if injured

# Legacy aliases (backward compatibility)
brawl_stat = wrestler.brawl  # -> wrestler.striking
tech_stat = wrestler.tech    # -> wrestler.technical
```

**Migration:** Old 9-attribute wrestlers auto-convert to 27 attributes on load.

---

### 2. Match Simulation System

**File:** `src/core/match.py` (800+ lines)

**10 Match Types:**

1. **Singles Match** - 1v1
2. **Tag Team Match** - 2v2 with chemistry
3. **Triple Threat** - 3-way, first fall
4. **Fatal 4-Way** - 4-way, first fall
5. **Ladder Match** - Climb to retrieve prize
6. **Iron Man Match** - Timed, most falls wins
7. **Elimination Chamber** - 6-man pod elimination
8. **Money in the Bank** - 6-8 man ladder, briefcase
9. **Royal Rumble** - 10-man timed elimination
10. **Steel Cage** - Modifier on singles/tag

**Rating Formula (Simplified):**
```python
def calculate_rating(wrestler_a, wrestler_b):
    # Base rating from stats
    base = (wrestler_a.overall + wrestler_b.overall) / 2

    # Style compatibility
    style_mod = get_style_compatibility(wrestler_a.style, wrestler_b.style)

    # Psychology bonus
    psych_bonus = (wrestler_a.psychology + wrestler_b.psychology) / 200 * 10

    # Feud bonus (if in feud)
    feud_bonus = 0
    if in_feud:
        if intensity == "heated": feud_bonus = 3
        elif intensity == "intense": feud_bonus = 6
        elif intensity == "blood": feud_bonus = 10

    # Condition penalty
    condition_penalty = 0
    avg_condition = (wrestler_a.condition + wrestler_b.condition) / 2
    if avg_condition < 50:
        condition_penalty = (50 - avg_condition) / 3.33  # Up to -15

    # Final rating
    rating = base + style_mod + psych_bonus + feud_bonus - condition_penalty
    rating = max(0, min(100, rating))  # Clamp 0-100

    return rating
```

**Code Example:**
```python
from core.match import Match

# Create singles match
match = Match(
    wrestler_a=austin,
    wrestler_b=rock,
    is_title_match=True,
    title_id=1,
    is_steel_cage=False
)

# Simulate
result = match.simulate()

# Result contains:
# - winner (Wrestler)
# - loser (Wrestler)
# - rating (0-100)
# - commentary (list of strings)
# - is_title_change (bool)
# - interference_occurred (bool)
# - stable_helped (Stable or None)
```

---

### 3. Game Service (THE API)

**File:** `src/services/game_service.py` (600+ lines)

**This is the SINGLE ENTRY POINT for all game operations.**

**Key Methods:**

```python
class GameService:
    """Single API for all game operations."""

    # === Game Management ===
    def create_new_game(db_name: str, save_name: str) -> tuple[bool, str]
    def load_game(save_name: str) -> tuple[bool, str]
    def save_game() -> tuple[bool, str]
    def list_saves() -> list[str]
    def list_databases() -> list[str]

    # === Show Management ===
    def create_show(show_name: str) -> Show
    def add_singles_match_to_show(w_a_id, w_b_id, title_id=None, cage=False)
    def add_tag_match_to_show(team_a_id, team_b_id, title_id=None)
    def add_multi_man_match_to_show(wrestler_ids: list, title_id=None)
    # ... (methods for all 10 match types)
    def play_show() -> ShowResult
    def cancel_show()

    # === Wrestler Management ===
    def get_roster() -> list[Wrestler]
    def get_wrestler_by_id(wrestler_id: int) -> Wrestler
    def create_wrestler(**kwargs) -> tuple[bool, str, Wrestler]
    def get_available_wrestlers(brand_id=None) -> list[Wrestler]

    # === Title Management ===
    def get_titles() -> list[Title]
    def create_title(**kwargs) -> tuple[bool, str, Title]
    def get_title_by_id(title_id: int) -> Title

    # === Feud Management ===
    def start_feud(w_a_id, w_b_id, matches=3) -> tuple[bool, str, Feud]
    def get_active_feuds() -> list[Feud]
    def get_feud_by_wrestlers(w_a_id, w_b_id) -> Feud

    # === Stable Management ===
    def create_stable(name, leader_id, member_ids) -> tuple[bool, str, Stable]
    def get_active_stables() -> list[Stable]

    # === AI Booking ===
    def get_card_suggestions(show_name=None, brand_id=None) -> CardSuggestion
    def apply_card_suggestions(suggestions: CardSuggestion) -> tuple[bool, str]

    # === Records & Stats ===
    def get_wrestler_rankings() -> list[Wrestler]
    def get_tag_team_rankings() -> list[TagTeam]
    def get_match_history(limit=50) -> list[MatchHistoryEntry]

    # === Calendar ===
    def advance_week()
    def get_current_date_string() -> str
    def get_next_ppv_string() -> str
    def get_remaining_shows_this_week() -> list[ScheduledShow]

    # === News Feed ===
    def get_news(limit=10) -> list[NewsItem]

    # === Brands ===
    def get_active_brands() -> list[Brand]
    def create_brand(**kwargs) -> tuple[bool, str, Brand]
```

**Usage Pattern:**
```python
from services.game_service import GameService

game = GameService()

# Create new game
success, msg = game.create_new_game("default", "My Federation")

# Get roster
roster = game.get_roster()

# Create show
show = game.create_show("Monday Night Raw")

# Add match
success, msg = game.add_singles_match_to_show(
    wrestler_a_id=1,
    wrestler_b_id=2,
    title_id=1,
    is_steel_cage=False
)

# Run show
result = game.play_show()

# Result contains:
# - show_name
# - match_results (list)
# - tv_rating
# - attendance
# - revenue
# - etc.
```

---

### 4. AI Auto-Booking System

**File:** `src/core/auto_booker.py` (400+ lines)

**Priority-Based Booking Algorithm:**

```
1. Blowoff Matches (MANDATORY)
   - Feuds scheduled to end

2. Title Defenses (PPV ONLY)
   - All held titles
   - Tag titles = tag matches

3. Active Feuds
   - Book feud participants vs each other
   - Advance storylines

4. Tag Team Matches
   - 1-2 on PPV, 1 on TV
   - Booked early to guarantee slots

5. Rankings-Based Matches
   - Top-ranked in meaningful matches
   - Limited to leave room

6. Variety Fill
   - Multi-man matches for diversity
```

**Code Example:**
```python
from services.game_service import GameService

game = GameService()

# Get AI suggestions
suggestions = game.get_card_suggestions(
    show_name="Raw",
    brand_id=1  # Optional: filter by brand
)

# Suggestions contains:
# - matches: list[MatchSuggestion]
# - feud_suggestions: list[FeudSuggestion]
# - show_name: str

# Toggle individual matches
for i, match in enumerate(suggestions.matches):
    match.is_accepted = True  # or False
    print(f"{i}. {match.description}")

# Apply accepted matches
success, msg = game.apply_card_suggestions(suggestions)
```

---

### 5. Save/Load System

**File:** `src/services/file_service.py` (300+ lines)

**Save Game Structure:**

```
saves/MyFederation/
├── wrestlers.json         # All wrestlers
├── tag_teams.json         # Tag teams
├── titles.json            # Championships
├── feuds.json             # Active feuds
├── stables.json           # Factions
├── records.json           # Match history
├── company.json           # Bank, prestige, viewers
├── game_state.json        # Year, month, week
├── calendar.json          # Schedule, PPVs
├── brands.json            # Brand split
├── weekly_shows.json      # Recurring shows
└── news.json              # News feed
```

**All files are JSON** - human-readable and fully moddable!

**Example - wrestlers.json:**
```json
[
  {
    "id": 1,
    "name": "Stone Cold Steve Austin",
    "nickname": "The Texas Rattlesnake",
    "age": 32,
    "height": 74,
    "weight": 252,
    "nationality": "USA",
    "alignment": "Face",
    "primary_style": "brawler",

    "strength": 85,
    "speed": 75,
    "agility": 70,
    "durability": 90,
    "stamina": 85,
    "recovery": 80,

    "striking": 95,
    "grappling": 80,
    "submission": 70,
    "high_flying": 50,
    "hardcore": 90,
    "power_moves": 85,
    "technical": 75,
    "dirty_tactics": 80,

    "strike_defense": 85,
    "grapple_defense": 80,
    "aerial_defense": 70,
    "ring_awareness": 90,

    "mic_skills": 98,
    "charisma": 100,
    "look": 85,
    "star_power": 100,
    "entrance": 95,

    "psychology": 90,
    "consistency": 85,
    "big_match": 95,
    "clutch": 98,

    "finisher_name": "Stone Cold Stunner",
    "finisher_type": "Striking",
    "finisher_damage": 95,
    "signature_name": "Lou Thesz Press",
    "signature_type": "Brawling",
    "signature_damage": 75,

    "wins": 0,
    "losses": 0,
    "heat": 50,
    "morale": 100,
    "condition": 100,
    "is_injured": false,
    "injury_weeks_remaining": 0,
    "has_mitb_briefcase": false
  }
]
```

**Backward Compatibility:**

Old saves with 9 attributes auto-convert:
```python
# Old format (9 attributes)
{
  "brawl": 95,
  "tech": 75,
  "air": 50,
  "psych": 90,
  "stamina": 85,
  "mic": 98,
  "charisma": 100,
  "look": 85,
  "star_quality": 100
}

# Auto-converts to 27 attributes on load
# Aliases maintained: brawl->striking, tech->technical, etc.
```

---

## UI Implementation

### Web UI Architecture

**Framework:** Flask 3.0 + Bootstrap 5.3.2
**Templates:** Jinja2 (21 templates)
**Styling:** Custom dark theme with glassmorphism

**Key Routes:**

```python
# app.py structure

# === Start Menu ===
@app.route('/')                          # index.html
@app.route('/new-game', methods=['POST'])
@app.route('/load-game', methods=['POST'])

# === Main Game ===
@app.route('/dashboard')                 # dashboard.html
@app.route('/save-game', methods=['POST'])
@app.route('/exit-game')

# === Roster ===
@app.route('/roster')                    # roster.html
@app.route('/wrestler/<int:wrestler_id>') # wrestler.html
@app.route('/create-wrestler')           # create_wrestler.html

# === Booking ===
@app.route('/booking')                   # booking.html
@app.route('/booking/select-show', methods=['POST'])
@app.route('/booking/create-show', methods=['POST'])
@app.route('/booking/add-singles', methods=['POST'])
@app.route('/booking/add-tag', methods=['POST'])
# ... (routes for all 10 match types)
@app.route('/booking/run-show', methods=['POST'])
@app.route('/booking/ai-book')          # ai_booking.html
@app.route('/results')                   # results.html

# === Titles ===
@app.route('/titles')                    # titles.html
@app.route('/create-title')              # create_title.html
@app.route('/title/<int:title_id>/history') # title_history.html

# === Feuds ===
@app.route('/feuds')                     # feuds.html
@app.route('/create-feud')               # create_feud.html

# === Stables ===
@app.route('/stables')                   # stables.html
@app.route('/create-stable')             # create_stable.html

# === Brands ===
@app.route('/brands')                    # brands.html
@app.route('/create-brand')              # create_brand.html
@app.route('/brand/<int:brand_id>/roster') # brand_roster.html

# === Stats ===
@app.route('/rankings')                  # rankings.html
@app.route('/records')                   # records.html

# === Schedule ===
@app.route('/calendar')                  # calendar.html
@app.route('/weekly-shows')              # weekly_shows.html
@app.route('/ppv-settings')              # ppv_settings.html
```

**Template Inheritance:**

```
base.html (master template)
├── Navigation
├── Flash messages
└── Content block

All templates extend base.html:
{% extends "base.html" %}
{% block title %}Page Title{% endblock %}
{% block content %}
  <!-- Page content -->
{% endblock %}
```

---

### Dark Theme Design System

**File:** `src/ui/web/static/css/style.css` (900+ lines)

**CSS Variables:**

```css
:root {
  /* Backgrounds */
  --bg-primary: #0d1117;      /* Nearly black */
  --bg-secondary: #161b22;    /* Card backgrounds */
  --bg-tertiary: #1c2128;     /* Elevated surfaces */
  --bg-hover: #21262d;        /* Hover states */
  --bg-glass: rgba(22, 27, 34, 0.8);  /* Glassmorphism */

  /* Text (WCAG AA compliant) */
  --text-primary: #e6edf3;    /* 12.63:1 contrast */
  --text-secondary: #8b949e;  /* 5.39:1 contrast */
  --text-muted: #6e7681;      /* 4.54:1 contrast */

  /* Accent Colors */
  --gold-primary: #ffd700;    /* Championship gold */
  --gold-secondary: #d4af37;
  --gold-dark: #b8960f;

  --red-primary: #ff6b6b;     /* Ring red */
  --green-primary: #51cf66;   /* Success */
  --blue-primary: #4dabf7;    /* Info */
  --purple-primary: #9775fa;  /* Brands */

  /* Spacing (8px base) */
  --space-xs: 0.25rem;   /* 4px */
  --space-sm: 0.5rem;    /* 8px */
  --space-md: 1rem;      /* 16px */
  --space-lg: 1.5rem;    /* 24px */
  --space-xl: 2rem;      /* 32px */
  --space-2xl: 3rem;     /* 48px */
  --space-3xl: 4rem;     /* 64px */

  /* Border Radius */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --radius-xl: 18px;
  --radius-full: 9999px;

  /* Shadows (5-tier) */
  --shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
  --shadow-sm: 0 2px 4px 0 rgba(0, 0, 0, 0.4);
  --shadow-md: 0 4px 8px 0 rgba(0, 0, 0, 0.5);
  --shadow-lg: 0 8px 16px 0 rgba(0, 0, 0, 0.6);
  --shadow-xl: 0 16px 32px 0 rgba(0, 0, 0, 0.7);

  /* Transitions */
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 350ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

**Key UI Components:**

**1. Glassmorphism Navbar:**
```css
.navbar {
  background: rgba(22, 27, 34, 0.85);
  backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid rgba(48, 54, 61, 0.5);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}
```

**2. Modern Cards:**
```css
.card {
  background: linear-gradient(135deg,
    rgba(22, 27, 34, 0.9) 0%,
    rgba(28, 33, 40, 0.85) 100%);
  border: 1px solid rgba(48, 54, 61, 0.6);
  border-radius: var(--radius-xl);
  backdrop-filter: blur(10px);
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}
```

**3. Championship Gold Buttons:**
```css
.btn-primary {
  background: linear-gradient(135deg,
    #ffd700 0%,
    #f4c430 50%,
    #d4af37 100%);
  color: #0d1117;
  box-shadow: 0 4px 14px 0 rgba(255, 215, 0, 0.35);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px 0 rgba(255, 215, 0, 0.5);
}
```

**4. Modern Form Inputs:**
```css
.form-control {
  background: linear-gradient(135deg,
    rgba(28, 33, 40, 0.8) 0%,
    rgba(22, 27, 34, 0.9) 100%);
  border: 1.5px solid rgba(48, 54, 61, 0.5);
  border-radius: var(--radius-lg);
}

.form-control:focus {
  border-color: var(--gold-primary);
  box-shadow: 0 0 0 3px rgba(255, 215, 0, 0.15);
}
```

**5. Utility Classes:**
```css
.glass-panel       /* Glassmorphism effect */
.hover-lift        /* Lift on hover */
.glow-gold         /* Gold shadow glow */
.text-gradient-gold /* Gold gradient text */
.stat-card         /* Modern stat display */
.page-header       /* Page headers */
.status-dot        /* Status indicators */
```

---

## Data Persistence

### Save Format Details

**All data stored as JSON arrays/objects**

**1. GameState (`game_state.json`):**
```json
{
  "save_name": "My Federation",
  "year": 1,
  "month": 3,
  "week": 2
}
```

**2. Company (`company.json`):**
```json
{
  "bank_account": 500000,
  "prestige": 65,
  "viewers": 1250000
}
```

**3. Feuds (`feuds.json`):**
```json
[
  {
    "id": 1,
    "wrestler_a_id": 1,
    "wrestler_b_id": 2,
    "intensity": "intense",
    "total_matches_planned": 5,
    "matches_so_far": 2,
    "is_active": true,
    "blowoff_scheduled": false
  }
]
```

**4. Records (`records.json`):**
```json
{
  "match_history": [
    {
      "match_id": 1,
      "date": "Y1 M1 W1",
      "show_name": "Raw",
      "match_type": "Singles",
      "participants": [1, 2],
      "winner_id": 1,
      "rating": 85,
      "is_title_match": true,
      "title_id": 1,
      "is_ppv": false
    }
  ],
  "wrestler_records": {
    "1": {
      "wrestler_id": 1,
      "total_wins": 15,
      "total_losses": 3,
      "current_win_streak": 5,
      "longest_win_streak": 8,
      "ppv_wins": 3,
      "ppv_losses": 1,
      "tv_wins": 12,
      "tv_losses": 2
    }
  },
  "title_reigns": [
    {
      "reign_id": 1,
      "title_id": 1,
      "wrestler_id": 1,
      "won_date": "Y1 M1 W1",
      "lost_date": null,
      "successful_defenses": 5,
      "is_active": true
    }
  ]
}
```

---

## Development Workflow

### Setup

```bash
# 1. Clone repository
git clone https://github.com/droman2684/pro-wrestling-sim.git
cd pro-wrestling-sim

# 2. Install Python 3.10+ (if not installed)
# Download from python.org

# 3. Install dependencies
pip install -r requirements.txt

# 4. Test it works
cd src/ui/web
python app.py
# Open http://127.0.0.1:5000
```

### Running the App

**Web UI (Recommended):**
```bash
# Option 1: Double-click
Play Web.bat

# Option 2: Command line
cd src/ui/web
python app.py
```

**Desktop UI:**
```bash
# Option 1: Double-click
Play Wrestling.bat

# Option 2: Command line
cd src/ui/desktop
python tkinter_app.py
```

**CLI:**
```bash
cd src
python main.py
```

### Git Workflow

**IMPORTANT:** Always push changes to GitHub after completing work!

```bash
# 1. Check status
git status

# 2. Stage changes
git add .

# 3. Commit with descriptive message
git commit -m "Feature: Add new match type"

# 4. Push to GitHub
git push origin main
```

**Commit Message Guidelines:**
- Use present tense: "Add feature" not "Added feature"
- Be specific: "Fix Royal Rumble injury bug" not "Fix bug"
- Reference systems: "Update match.py: Add Iron Man match type"

**Branching (Optional):**
```bash
# For large features
git checkout -b feature/new-feature
# ... work ...
git add .
git commit -m "Add new feature"
git checkout main
git merge feature/new-feature
git push origin main
```

### Making Changes

**1. Adding a New Attribute to Wrestler:**

```python
# Step 1: Update wrestler.py
@dataclass
class Wrestler:
    # ... existing attributes ...
    new_attribute: int = 50  # Add with default

# Step 2: Update to_dict() method
def to_dict(self) -> dict:
    return {
        # ... existing fields ...
        "new_attribute": self.new_attribute
    }

# Step 3: Update from_dict() method (with migration)
@staticmethod
def from_dict(data: dict) -> 'Wrestler':
    return Wrestler(
        # ... existing fields ...
        new_attribute=data.get('new_attribute', 50)  # Default for old saves
    )

# Step 4: Update create_wrestler in game_service.py
def create_wrestler(self, **kwargs):
    wrestler = Wrestler(
        # ... existing params ...
        new_attribute=kwargs.get('new_attribute', 50)
    )

# Step 5: Update web UI template (create_wrestler.html)
<div class="mb-3">
  <label class="form-label">New Attribute</label>
  <input type="number" name="new_attribute"
         class="form-control" value="50" min="0" max="100">
</div>

# Step 6: Update web route (app.py)
@app.route('/create-wrestler', methods=['POST'])
def create_wrestler():
    new_attribute = int(request.form.get('new_attribute', 50))
    # ... pass to game.create_wrestler()
```

**2. Adding a New Match Type:**

```python
# Step 1: Create match class in match.py
class NewMatchType:
    def __init__(self, wrestler_a, wrestler_b, **kwargs):
        self.wrestler_a = wrestler_a
        self.wrestler_b = wrestler_b
        # ... init

    def simulate(self) -> NewMatchResult:
        # Simulation logic
        rating = self._calculate_rating()
        winner = self._determine_winner()

        return NewMatchResult(
            winner=winner,
            loser=loser,
            rating=rating,
            # ... other fields
        )

# Step 2: Create result dataclass in game_state.py
@dataclass
class NewMatchResult:
    winner: Wrestler
    loser: Wrestler
    rating: int
    # ... other fields

# Step 3: Add to Show (show.py)
class Show:
    def __init__(self, name):
        # ... existing lists ...
        self.new_matches: List[NewMatchType] = []

    def run_show(self):
        # ... process other matches ...

        for match in self.new_matches:
            result = match.simulate()
            self.results.append(result)
            # ... handle aftermath

# Step 4: Add GameService method
def add_new_match_to_show(self, wrestler_a_id, wrestler_b_id):
    if not self.current_show:
        return False, "No show in progress"

    wrestler_a = self.get_wrestler_by_id(wrestler_a_id)
    wrestler_b = self.get_wrestler_by_id(wrestler_b_id)

    match = NewMatchType(wrestler_a, wrestler_b)
    self.current_show.new_matches.append(match)

    return True, "Match added"

# Step 5: Add web route
@app.route('/booking/add-new-match', methods=['POST'])
def add_new_match():
    wrestler_a_id = int(request.form.get('wrestler_a'))
    wrestler_b_id = int(request.form.get('wrestler_b'))

    success, msg = game.add_new_match_to_show(wrestler_a_id, wrestler_b_id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('booking'))

# Step 6: Add UI in booking.html
<div class="accordion-item">
  <h2 class="accordion-header">
    <button class="accordion-button collapsed"
            data-bs-toggle="collapse"
            data-bs-target="#newMatchCollapse">
      New Match Type
    </button>
  </h2>
  <div id="newMatchCollapse" class="accordion-collapse collapse">
    <div class="accordion-body">
      <form action="{{ url_for('add_new_match') }}" method="post">
        <!-- Wrestler selects -->
        <button type="submit">Add to Card</button>
      </form>
    </div>
  </div>
</div>
```

---

## Recent Changes

### February 1, 2026 - UI/UX Modernization

**Changes:**
1. ✅ Restructured navigation (Brands to top-level)
2. ✅ Added Getting Started onboarding guide
3. ✅ Improved booking workflow (3-step process)
4. ✅ Implemented dark theme with glassmorphism
5. ✅ Fixed text contrast on white backgrounds
6. ✅ Applied modern UI/UX best practices
7. ✅ Updated documentation (CLAUDE.md, this handoff)

**Commits:**
- `8f8ca48` - Update documentation: Consolidate developer guide
- `1af9916` - Major UX/UI improvements: Navigation, onboarding, booking
- `c4742b6` - Fix: Use correct method to check if shows run
- `2700e1e` - Implement dark theme with WCAG AA contrast
- `92b7860` - Fix text contrast on white/light backgrounds
- `3ea8c82` - Apply modern UI/UX best practices

**Files Modified:**
- `src/ui/web/templates/base.html` - Navigation + dark mode
- `src/ui/web/templates/dashboard.html` - Getting started guide
- `src/ui/web/templates/booking.html` - 3-step workflow
- `src/ui/web/templates/brands.html` - Better empty state
- `src/ui/web/static/css/style.css` - Complete rewrite (900+ lines)
- `CLAUDE.md` - Comprehensive developer guide

---

## Known Issues

### None Critical

**Minor Issues:**
- No automated test suite (all testing is manual)
- Some UI templates could be further optimized
- Multi-show per week not fully implemented (calendar exists, UI needs work)

**Future Improvements:**
- Add unit tests for core logic
- Add integration tests for GameService
- Implement custom PPV calendar management UI
- Add tournament bracket system

---

## Next Steps

### Immediate Priorities (v0.7)

**1. Commentary System Overhaul** (High Priority)
- File: `src/core/commentary.py`
- Current: Static templates
- Goal: Procedural generation based on fighting styles
- Difficulty: High
- Impact: High
- See: `docs/COMMENTARY_SYSTEM_OVERHAUL.md`

**2. Calendar UI Enhancements** (Medium Priority)
- Current: Basic calendar view exists
- Goal: Visual month grid, multi-show per week
- Difficulty: Medium
- Impact: High
- See: `docs/CALENDAR_SYSTEM_OVERHAUL.md`

**3. Web UI Polish** (Low Priority)
- Current: Functional, modern dark theme
- Goal: Additional refinements, animations
- Difficulty: Low
- Impact: Medium
- See: `WEB_UI_TODO.md`

### Long-Term Vision

**Advanced Features:**
- **Tournament System** - Brackets, auto-advancement
- **Wrestler Career Mode** - Play as a wrestler, not booker
- **Online Multiplayer** - Compete with other federations
- **Mod Support** - Community-created content
- **Mobile App** - iOS/Android version

---

## Code Patterns & Examples

### Pattern 1: Adding Data to GameState

```python
# 1. Create model class (e.g., src/core/new_feature.py)
@dataclass
class NewFeature:
    id: int
    name: str
    value: int

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "value": self.value
        }

    @staticmethod
    def from_dict(data: dict) -> 'NewFeature':
        return NewFeature(
            id=data["id"],
            name=data["name"],
            value=data["value"]
        )

# 2. Add to GameState (src/core/game_state.py)
@dataclass
class GameState:
    # ... existing fields ...
    new_features: List[NewFeature] = field(default_factory=list)

# 3. Add file service methods (src/services/file_service.py)
def get_new_features_path(self, save_name: str) -> str:
    return os.path.join(self.get_save_dir(save_name), "new_features.json")

def load_new_features(self, save_name: str) -> List[NewFeature]:
    path = self.get_new_features_path(save_name)
    if not os.path.exists(path):
        return []

    with open(path, 'r') as f:
        data = json.load(f)

    return [NewFeature.from_dict(item) for item in data]

def save_new_features(self, save_name: str, features: List[NewFeature]):
    path = self.get_new_features_path(save_name)
    data = [f.to_dict() for f in features]

    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

# 4. Add GameService methods (src/services/game_service.py)
def get_new_features(self) -> List[NewFeature]:
    if not self.is_game_loaded:
        return []
    return self._state.new_features

def create_new_feature(self, name: str, value: int) -> tuple[bool, str, NewFeature]:
    if not self.is_game_loaded:
        return False, "No game loaded", None

    # Generate ID
    next_id = max([f.id for f in self._state.new_features], default=0) + 1

    # Create
    feature = NewFeature(id=next_id, name=name, value=value)
    self._state.new_features.append(feature)

    # Save
    self._save_new_features()

    return True, "Feature created", feature

def _save_new_features(self):
    self._file_service.save_new_features(
        self._state.save_name,
        self._state.new_features
    )

def _load_new_features(self):
    features = self._file_service.load_new_features(self._state.save_name)
    self._state.new_features = features

# 5. Update load_game() to load new data
def load_game(self, save_name: str) -> tuple[bool, str]:
    # ... existing loads ...
    self._load_new_features()  # Add this
```

### Pattern 2: Creating a Web UI Page

```python
# 1. Create route in app.py
@app.route('/new-page')
@require_game_loaded
def new_page():
    """Display new page."""
    # Get data from game service
    features = game.get_new_features()

    return render_template('new_page.html',
        features=features,
        game=game
    )

@app.route('/create-feature', methods=['GET', 'POST'])
@require_game_loaded
def create_feature():
    """Create new feature."""
    if request.method == 'GET':
        return render_template('create_feature.html')

    # POST - process form
    name = request.form.get('name')
    value = int(request.form.get('value', 0))

    success, msg, feature = game.create_new_feature(name, value)
    flash(msg, 'success' if success else 'error')

    if success:
        return redirect(url_for('new_page'))
    return redirect(url_for('create_feature'))

# 2. Create template (templates/new_page.html)
{% extends "base.html" %}

{% block title %}New Page{% endblock %}

{% block content %}
<div class="page-header">
  <h2>
    <i class="bi bi-star me-2"></i>New Features
  </h2>
  <p>Manage your new features here</p>
</div>

<div class="row">
  <div class="col-lg-8">
    <div class="card">
      <div class="card-header">
        <i class="bi bi-list-ul me-2"></i>All Features
      </div>
      <div class="card-body">
        {% if features %}
          {% for feature in features %}
            <div class="mb-2">
              <strong>{{ feature.name }}</strong>: {{ feature.value }}
            </div>
          {% endfor %}
        {% else %}
          <p class="text-muted">No features yet.</p>
        {% endif %}
      </div>
      <div class="card-footer">
        <a href="{{ url_for('create_feature') }}"
           class="btn btn-primary">
          <i class="bi bi-plus-circle me-1"></i>Create Feature
        </a>
      </div>
    </div>
  </div>
</div>
{% endblock %}

# 3. Create form template (templates/create_feature.html)
{% extends "base.html" %}

{% block title %}Create Feature{% endblock %}

{% block content %}
<h2>Create New Feature</h2>

<div class="row">
  <div class="col-lg-6">
    <div class="card">
      <div class="card-body">
        <form action="{{ url_for('create_feature') }}" method="post">
          <div class="mb-3">
            <label class="form-label">Name</label>
            <input type="text" name="name"
                   class="form-control" required>
          </div>

          <div class="mb-3">
            <label class="form-label">Value</label>
            <input type="number" name="value"
                   class="form-control" value="0" min="0" max="100">
          </div>

          <button type="submit" class="btn btn-primary">
            Create
          </button>
          <a href="{{ url_for('new_page') }}"
             class="btn btn-secondary">
            Cancel
          </a>
        </form>
      </div>
    </div>
  </div>
</div>
{% endblock %}

# 4. Add navigation link (templates/base.html)
<li class="nav-item dropdown">
  <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
    Features
  </a>
  <ul class="dropdown-menu">
    <li>
      <a class="dropdown-item" href="{{ url_for('new_page') }}">
        <i class="bi bi-star me-2"></i>View Features
      </a>
    </li>
    <li>
      <a class="dropdown-item" href="{{ url_for('create_feature') }}">
        <i class="bi bi-plus-circle me-2"></i>Create Feature
      </a>
    </li>
  </ul>
</li>
```

---

## Testing & Deployment

### Manual Testing Checklist

**Before each commit:**
- [ ] Create new game - verify roster loads
- [ ] Book singles match - verify simulation works
- [ ] Run show - verify results display
- [ ] Save game - verify files written
- [ ] Load game - verify state restored
- [ ] Test with existing save - verify backward compatibility

**Full regression test:**
- [ ] All 10 match types simulate correctly
- [ ] AI booking generates valid cards
- [ ] Feuds track correctly
- [ ] Stables interfere properly
- [ ] Records accumulate correctly
- [ ] News feed generates events
- [ ] Calendar advances properly
- [ ] All UI pages load without errors

### Running the Web UI

**Development:**
```bash
cd src/ui/web
python app.py

# Flask runs on http://127.0.0.1:5000
# Debug mode enabled (auto-reload on code changes)
```

**Production (Example with Waitress):**
```bash
pip install waitress

# Create production.py:
from waitress import serve
from app import app

serve(app, host='0.0.0.0', port=5000)

# Run:
python production.py
```

### Deployment Options

**1. Local Desktop App:**
- Users run `Play Web.bat` or `Play Wrestling.bat`
- No server needed
- All data stored locally

**2. Self-Hosted Server:**
- Deploy Flask app to Linux server
- Use Gunicorn or Waitress
- Nginx reverse proxy
- Multiple users with separate save folders

**3. Cloud Hosting:**
- Heroku, Railway, Render, etc.
- Include `Procfile`:
  ```
  web: cd src/ui/web && python app.py
  ```
- Set Python version in `runtime.txt`:
  ```
  python-3.10.0
  ```

---

## Appendix: File Reference

### Critical Files (Don't Delete!)

**Core Logic:**
- `src/core/wrestler.py` - Wrestler model (590 lines)
- `src/core/match.py` - Match simulation (800+ lines)
- `src/core/show.py` - Show runner (500+ lines)
- `src/core/game_state.py` - State management (400+ lines)
- `src/services/game_service.py` - **THE API** (600+ lines)

**Web UI:**
- `src/ui/web/app.py` - Flask routes (720+ lines)
- `src/ui/web/templates/base.html` - Master template
- `src/ui/web/static/css/style.css` - Dark theme (900+ lines)

**Data:**
- `data/databases/default/wrestlers.json` - Template roster
- All files in `saves/*/` - User save data

**Documentation:**
- `CLAUDE.md` - Developer guide (MUST READ)
- `HANDOFF.md` - This document
- `docs/` - Technical specifications

### Configuration Files

**requirements.txt:**
```txt
Flask>=3.0.0
```

**Play Web.bat:**
```batch
@echo off
cd /d "%~dp0src\ui\web"
python app.py
pause
```

**Play Wrestling.bat:**
```batch
@echo off
cd /d "%~dp0src\ui\desktop"
python tkinter_app.py
pause
```

---

## Contact & Support

**Repository:** https://github.com/droman2684/pro-wrestling-sim
**Issues:** https://github.com/droman2684/pro-wrestling-sim/issues
**Developer Guide:** `CLAUDE.md`
**Technical Specs:** `docs/README.md`

---

## Quick Start for New Developers

```bash
# 1. Clone and setup
git clone https://github.com/droman2684/pro-wrestling-sim.git
cd pro-wrestling-sim
pip install -r requirements.txt

# 2. Read documentation
# - CLAUDE.md (developer guide)
# - This file (HANDOFF.md)
# - docs/README.md (technical specs)

# 3. Run the app
cd src/ui/web
python app.py
# Open http://127.0.0.1:5000

# 4. Explore the code
# - Start with src/services/game_service.py (THE API)
# - Read src/core/wrestler.py (data model)
# - Read src/core/match.py (simulation)
# - Check src/ui/web/app.py (web routes)

# 5. Make changes
# - Edit files
# - Test manually
# - Commit and push

git add .
git commit -m "Your changes"
git push origin main
```

---

## Final Notes

**This is a complete, working application.** All core features are implemented and tested. The codebase is clean, well-organized, and follows consistent patterns.

**Key Strengths:**
- ✅ Clean architecture (core/services/ui separation)
- ✅ Single API pattern (GameService)
- ✅ Modular match types (easy to extend)
- ✅ JSON persistence (human-readable)
- ✅ Modern UI with dark theme
- ✅ Comprehensive feature set

**Key Weaknesses:**
- ⚠️ No automated tests
- ⚠️ Manual testing only
- ⚠️ Some advanced features not implemented (tournaments, career mode)

**For Success:**
1. **Read CLAUDE.md first** - comprehensive dev guide
2. **Follow the patterns** - they're consistent throughout
3. **Test manually** - create game, book show, verify results
4. **Commit often** - push to GitHub after each feature
5. **Ask questions** - check docs/ folder for technical specs

**This handoff provides everything needed to understand, maintain, and extend the pro wrestling simulator. Good luck!** 🏆

---

**Document Version:** 1.0
**Date:** February 1, 2026
**Next Review:** As needed for major changes

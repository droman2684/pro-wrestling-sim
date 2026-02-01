# Simple Sim Sports: Pro Wrestling - Build v0.5 (Alpha)

**Project Status:** FUNCTIONAL PROTOTYPE
**Engine:** Python 3.10+
**Data Storage:** JSON (Moddable + Persistence)
**Date:** January 17, 2026

---

## 1. Directory Structure
*Ensure your local environment matches this tree exactly.*

```text
SimpleSimWrestling/
├── data/
│   └── databases/
│       └── default/
│           ├── wrestlers.json  <-- Master Template (Read-Only)
│           └── tag_teams.json  <-- Tag Team Template (Read-Only)
├── saves/                      <-- User Save Files (Read/Write)
├── src/
│   ├── main.py                 <-- Entry Point (thin launcher)
│   ├── core/                   <-- Pure Game Logic (NO I/O)
│   │   ├── wrestler.py         <-- Wrestler class + load/save
│   │   ├── match.py            <-- Match simulation engine (singles + tag)
│   │   ├── show.py             <-- Show runner (returns data)
│   │   ├── game_state.py       <-- GameState, MatchResult, TagMatchResult, ShowResult
│   │   └── tag_team.py         <-- TagTeam class + load/save
│   ├── services/               <-- API Layer
│   │   ├── game_service.py     <-- Main orchestration service
│   │   └── file_service.py     <-- File system operations
│   └── ui/                     <-- User Interfaces
│       └── cli/
│           └── cli_app.py      <-- Terminal interface
```

## 2. Architecture Overview

| Layer | Purpose | Key Components |
| :--- | :--- | :--- |
| **`core/`** | Pure game logic. No print/input. Returns data objects. | `Wrestler`, `Match`, `Show`, `GameState`, `ShowResult`, `TagTeam`, `TagMatchResult` |
| **`services/`** | API layer. Orchestrates game operations. Both CLI and future GUI call this. | `GameService.load_game()`, `GameService.play_show()`, `GameService.create_tag_team()` |
| **`ui/cli/`** | Terminal interface. All print/input isolated here. | `CLIApp` |

**Key Abstraction:** `GameService` is the single API for all game operations. Any UI (CLI, Desktop, Web) calls the same service methods.

## 3. Current Feature Set (v0.5)

* [x] **Multiverse System:** Can create unlimited independent save games (`/saves/SaveName`).
* [x] **Moddable Roster:** Game reads from `wrestlers.json`.
* [x] **Match Engine:** Calculates winner based on stats + variance. Calculates Star Rating based on Workrate/Psychology.
* [x] **Persistence:** Stamina drains and Morale/Heat updates after every show.
* [x] **Auto-Save:** Roster state is automatically saved to disk when a show ends.
* [x] **Layered Architecture:** Game logic separated from UI via `GameService` API (supports multiple frontends).
* [x] **Tag Team System:** Create/manage tag teams with chemistry mechanics, book tag matches, view rankings.

---

## 4. MVP Roadmap (v1.0 Target)

### Epic 2: Architecture Refactor ✅ COMPLETE
Separate game logic from UI to enable multiple frontends (CLI, Desktop, Web).

| Task | Description | Status |
|:-----|:------------|:-------|
| **Task 2.1** | Create `core/` module with pure game logic (no I/O) | Complete |
| **Task 2.2** | Create `services/` layer with `GameService` API | Complete |
| **Task 2.3** | Extract CLI to `ui/cli/` module | Complete |
| **Task 2.4** | Create `GameState`, `MatchResult`, `ShowResult` data classes | Complete |
| **Task 2.5** | Remove all print/input from core game logic | Complete |

**Result:** Any UI can now call `GameService` methods. Zero game logic duplication between interfaces.

---

### Epic 3: Match Types
Expand beyond singles matches to provide variety and marquee events.

| Match Type | Participants | Details | Status |
|:-----------|:-------------|:--------|:-------|
| **Singles** | 1v1 | Baseline match type | Complete |
| **Tag Team** | 2v2 | Chemistry affects rating, tracks pinned wrestler | Complete |
| **Steel Cage** | 1v1 or 2v2 | Modifier on singles/tag, flavor text + rating bump | Planned |
| **Royal Rumble (10-Man)** | 10 | 2 start, 8 timed entries, stamina-based elimination, fatigue accumulation, winner flagged | Planned |

**Royal Rumble Mechanics:**
- 2 wrestlers start, 8 enter at timed intervals
- Elimination probability = current stamina + base stats + RNG
- Early entrants accumulate fatigue (disadvantage)
- Winner flagged for future title shot integration

---

### Epic 4: Tag Team System ✅ COMPLETE
Enable tag team wrestling with persistent team data.

| Task | Description | Status |
|:-----|:------------|:-------|
| **Task 4.1** | Create `TagTeam` class (Team Name, Member IDs, Chemistry Score) | Complete |
| **Task 4.2** | Store tag teams in `tag_teams.json` | Complete |
| **Task 4.3** | Add tag team match logic to `match.py` | Complete |
| **Task 4.4** | Integrate tag team rankings | Complete |
| **Task 4.5** | CLI: Tag Team Management screens (create/disband) | Complete |
| **Task 4.6** | CLI: Tag match booking flow | Complete |
| **Task 4.7** | Prevent wrestler double-booking (singles + tag on same card) | Complete |

**Implemented Features:**
- **TagTeam class:** id, name, member_ids, chemistry (0-100), wins, losses, is_active
- **Team Rating:** Average of member overalls × chemistry modifier (0.8 to 1.2)
- **Chemistry Mechanics:** +1-3 on wins, -1 on losses, capped at 0-100
- **Match Rating Bonus:** +5 at chemistry 80+, -5 at chemistry 20-
- **Wrestler Exclusivity:** One active team per wrestler
- **Narrative:** Tracks pinned wrestler for results display
- **Availability:** Team unavailable if member condition < 20

**Result:** Tag team wrestling fully integrated with chemistry mechanics and rankings.

---

### Epic 5: Match Commentary (Highlight Moments)
Add texture to match results with generated key spots.

* **Task 5.1:** Create highlight moment pool (generic moves/spots)
* **Task 5.2:** Generate 6-8 key spots per match based on match type and rating
* **Task 5.3:** Higher-rated matches pull from "dramatic" pool; lower-rated from "sloppy" pool

**Future Enhancement:** Wrestler-specific movesets feed into commentary (finishers, signatures)

---

### Epic 6: Calendar & PPV System
Full season simulation with weekly shows and named pay-per-views.

* **Task 6.1:** Implement 52-week calendar structure
* **Task 6.2:** Create weekly show runner (one flagship per week)
* **Task 6.3:** Define 12 named PPVs with tier system
* **Task 6.4:** Add "sim to next PPV" option
* **Task 6.5:** PPV matches carry higher stakes (rankings, prestige)

**PPV Calendar:**

| Month | Event | Tier |
|:------|:------|:-----|
| January | New Year's Fury | Standard |
| February | Breaking Point | Standard |
| March | **Championship Chaos** | Big Four |
| April | Battlegrounds | Standard |
| May | Collision Course | Standard |
| June | **Summer Scorcher** | Big Four |
| July | Uprising | Standard |
| August | Fallout | Standard |
| September | **Supremacy** | Big Four |
| October | No Escape | Standard |
| November | Final Stand | Standard |
| December | **Grand Slam** | Flagship (WrestleMania-tier) |

**Show Mechanics:**
- Week-to-week play with option to sim to next PPV
- Sandbox booking - user has full agency
- PPVs have elevated prestige and ranking impact

---

### Epic 7: Rankings System
Transparent contender rankings driven by performance.

* **Task 7.1:** Implement win/loss record tracking per wrestler
* **Task 7.2:** Create Top 5 rankings for Singles division
* **Task 7.3:** Create Top 5 rankings for Tag Team division
* **Task 7.4:** Ranking update logic: wins/losses weighted by opponent quality

**Ranking Logic:**
- Beat a #1 contender = big jump
- Beat an unranked wrestler = marginal gain
- Losses weighted inversely
- PPV results carry extra weight

---

### Epic 10: Desktop UI (Flet)
Replace terminal interface with a modern desktop application.

* **Task 10.1:** Install Flet framework, create `ui/desktop/` module structure
* **Task 10.2:** Build main window with navigation (Start Menu, Head Office, Booking)
* **Task 10.3:** Create Roster View screen (sortable table, wrestler cards)
* **Task 10.4:** Create Show Booking screen (drag-drop or click-to-add matches)
* **Task 10.5:** Create Show Results screen (match-by-match display with animations)
* **Task 10.6:** Add Calendar View (when Epic 6 is complete)
* **Task 10.7:** Add Rankings View (when Epic 7 is complete)
* **Task 10.8:** Package as standalone executable (PyInstaller or Flet's built-in)

**Design Principles:**
- All screens call `GameService` methods (no direct data access)
- Desktop app is a peer to CLI, not a replacement
- Start simple: functional first, polish later
- Mobile-friendly layouts (Flet supports mobile export later)

**Framework Choice: Flet**
- Python-native (no JavaScript/HTML required)
- Modern Material Design look out of the box
- Cross-platform (Windows, Mac, Linux, Web, Mobile)
- Gentler learning curve than PyQt

**Dependency:** Epic 2 (Architecture Refactor) ✅

---

### Epic 8: Championships (Post-MVP Priority)
* **Task 8.1:** Create `Title` class (Name, Prestige, Current Holder)
* **Task 8.2:** Add Title Defense logic to `Match` class
* **Task 8.3:** Tie rankings to title opportunities

---

### Epic 9: Economy (Post-MVP Priority)
* **Task 9.1:** Create `Company` class (Bank Account, Prestige)
* **Task 9.2:** Add `Contract` data to wrestlers (Per Appearance Fee)
* **Task 9.3:** Update `Show.run_show()` to calculate Profit/Loss (Ticket Sales - Wrestler Pay)

---

## 5. Deferred Features (Post-MVP)

| Feature | Description | Dependency |
|:--------|:------------|:-----------|
| **Stables** | Wrestler groupings (3-6 members) | Interference system |
| **Interference** | Run-ins, distractions affecting matches | Stables |
| **Brands** | Roster splits, separate shows | Calendar system |
| **Feuds** | Storyline system, up to 5 active per brand | Brands, pre-booking |
| **Auto Pre-Booking** | AI suggests cards based on feuds/rankings | Feuds, rankings |
| **Wrestler Movesets** | Personalized finishers/signatures in commentary | Commentary system |
| **Mobile App** | iOS/Android via Flet export | Desktop UI (Epic 10) |
| **Web Version** | Browser-based via Flet web target | Desktop UI (Epic 10) |

---

## 6. Technical Extensibility Notes

Build current systems with future features in mind:

- **Wrestler data model:** Leave room for brand assignment field
- **Match data model:** Include optional feud_id field (nullable for now)
- **Show data model:** Support "suggested card" injection hook for future auto-booking
- **Tag Team structure:** Design so Stables can layer on top without rework ✅ (TagTeam.is_active allows soft delete for future stable membership)
- **Commentary system:** Abstract move pools so wrestler-specific moves can swap in later

---

## 7. What's Next

With Epic 4 (Tag Team System) complete, recommended next priorities:

### Immediate Options

| Epic | Description | Dependencies | Complexity |
|:-----|:------------|:-------------|:-----------|
| **Epic 3: Steel Cage** | Add match type modifier with rating bump | None | Low |
| **Epic 5: Commentary** | Highlight moments for match texture | None | Medium |
| **Epic 7: Rankings** | Win/loss tracking, Top 5 rankings | None | Medium |
| **Epic 6: Calendar** | 52-week structure, PPV system | None | High |

### Suggested Path

1. **Epic 7 (Rankings)** - Natural extension since we now track wins/losses on tag teams. Add singles win/loss tracking and implement ranking logic.

2. **Epic 3 (Steel Cage)** - Quick win to add variety. Simple modifier on existing match types.

3. **Epic 5 (Commentary)** - Adds texture without new game mechanics. Can work alongside other features.

4. **Epic 6 (Calendar)** - Major feature that unlocks PPV prestige system. Save for dedicated sprint.

### Technical Debt
- None identified. Codebase is clean and follows established patterns.

# Pro Wrestling Sim - Development Context

## Project Overview
Python pro wrestling booking simulator with Flask web UI, Tkinter desktop UI, and CLI.
**Stack:** Python 3.10+, Flask + Bootstrap 5, JSON persistence, no database.

## Architecture
```
src/core/       - Pure game logic (no I/O). Dataclasses, simulation, calculations.
src/services/   - Orchestration layer. GameService is the single API for all UIs.
src/ui/web/     - Flask app (app.py) + Jinja2 templates (21+ templates).
src/ui/desktop/ - Tkinter GUI (tkinter_app.py).
src/ui/cli/     - Text-based menu interface.
data/databases/ - Moddable JSON template databases.
saves/          - Per-save JSON files (wrestlers, titles, feuds, company, etc).
```

**Key pattern:** `GameService` (services/game_service.py) is the sole entry point for all game operations. All three UIs call the same service methods. Core modules never do I/O.

## Key Files
| File | Purpose |
|------|---------|
| `src/core/match.py` | Match simulation engine (10 match types, rating formulas) |
| `src/core/wrestler.py` | Wrestler model (27 attributes, fatigue, injury) |
| `src/core/show.py` | Show runner, revenue engine, TV ratings |
| `src/core/game_state.py` | GameState dataclass, all result dataclasses, advance_week() |
| `src/core/economy.py` | Company (bank, prestige, viewers) and Contract |
| `src/core/auto_booker.py` | AI booking with 6-priority match card generation |
| `src/core/feud.py` | Feuds with auto-escalation (heated/intense/blood) |
| `src/core/stable.py` | Factions with interference mechanics |
| `src/core/calendar.py` | Weekly shows, PPV calendar, scheduling |
| `src/core/records.py` | Match history, streaks, H2H, title reigns |
| `src/services/game_service.py` | Orchestration: show running, save/load, all game ops |
| `src/services/file_service.py` | JSON file I/O for all save data |
| `src/ui/web/app.py` | Flask routes (dashboard, booking, results, roster, etc) |

## What's Been Implemented (as of v0.6 work)

### Roadmap Features - Status
| # | Feature | Status |
|---|---------|--------|
| 1 | **Fatigue/Injury System** | **DONE** - condition drain, injury risk, recovery, booking enforcement |
| 2 | **TV Ratings & Attendance** | **DONE** - TV rating scale, viewership tracking, attendance, revenue engine, prestige |
| 3 | **Match Logs (Observer-style)** | NOT STARTED - commentary.py has static templates, needs procedural style-based generation |
| 4 | **Backstage News Feed** | **DONE** - integrated NewsFeedManager, UI card on dashboard, persists to news.json |
| 5 | **Visual Card Canvas** | NOT STARTED |

### Backstage News Feed Details (completed)
- `NewsFeedManager` integrated into `GameState` and `GameService`
- News items generated for: Title Changes, Injuries, 5-Star Matches, Feud Escalations, Welcome Message
- Persists to `news.json` in save folder
- Dashboard UI displays recent news with category-specific badges (Gold/Red/Primary)
- Auto-generates "Welcome" news item for migrated saves

### Fatigue/Injury Details (completed)
- `wrestler.update_after_match()` drains condition (scaled by durability) alongside stamina
- `wrestler.check_injury_risk()` triggers when condition < 25, rolls against durability
- `_condition_penalty()` in match.py reduces ratings when avg condition < 50 (up to -15)
- `game_state.advance_week()` recovers stamina (20/week + recovery bonus), condition (3-8/week), heals injuries
- Auto-booker and tag team availability filter out injured wrestlers
- Injury badge on wrestler profile page

### TV Ratings & Attendance Details (completed)
- `Company.viewers` added (starts 1M, persisted in company.json)
- `show.py` has 5 pure calculation functions: `calculate_tv_rating()`, `calculate_attendance()`, `calculate_viewer_change()`, `calculate_prestige_change()`, `calculate_revenue()`
- `ShowResult` extended with: tv_rating, attendance, ticket_revenue, ppv_revenue, viewer_change, prestige_change
- Results page shows Broadcast Report + Financial Report cards
- Dashboard sidebar shows Company Stats (viewers, prestige bar, bank)
- Revenue model: tickets scale with prestige, PPV buys = 5-15% of viewers at $44.99

### Bug Fix Applied
- `match.py` Royal Rumble: `w.star_quality` -> `w.star_power` (attribute didn't exist)

## Match Types (10)
Singles, Tag Team, Triple Threat, Fatal 4-Way, Ladder, Iron Man, Elimination Chamber, Money in the Bank, Royal Rumble, Steel Cage (modifier).

## Wrestler Stats (27 attributes)
- **Physical (6):** strength, speed, agility, durability, stamina, recovery
- **Offense (8):** striking, grappling, submission, high_flying, hardcore, power_moves, technical, dirty_tactics
- **Defense (4):** strike_defense, grapple_defense, aerial_defense, ring_awareness
- **Entertainment (5):** mic_skills, charisma, look, star_power, entrance
- **Intangibles (4):** psychology, consistency, big_match, clutch
- **Legacy aliases:** brawl->striking, tech->technical, air->high_flying, psych->psychology

## Save Game Format
All JSON. Files per save: wrestlers.json, tag_teams.json, titles.json, feuds.json, stables.json, records.json, company.json, game_state.json, calendar.json, brands.json, weekly_shows.json.

## No Test Suite
No automated tests exist. Verification is manual via the web UI.

## Next Up (Roadmap Priority)
**3. "Wrestling Observer" Match Logs** - Replace static commentary templates with procedural narrative generation driven by wrestler fighting styles and stats. High difficulty, high impact.

# Pro Wrestling Sim - Development Roadmap

## Overview

This document serves as the master index for all planned system overhauls and provides a recommended implementation order based on dependencies and impact.

---

## Overhaul Documents

| Document | Description | Complexity | Priority | Status |
|----------|-------------|------------|----------|--------|
| [Wrestler Rating Overhaul](./WRESTLER_RATING_OVERHAUL.md) | WWE 2K-style attribute system with 27 stats, fighting styles, and special moves | High | 1 | COMPLETE |
| [Calendar System Overhaul](./CALENDAR_SYSTEM_OVERHAUL.md) | Visual calendar, recurring weekly shows, brand split with title assignments | High | 2 | Pending |
| [Commentary System Overhaul](./COMMENTARY_SYSTEM_OVERHAUL.md) | Phased match commentary, talking segments for TV shows | Medium | 3 | Pending |

---

## Recommended Implementation Order

### Phase 1: Wrestler Rating System - COMPLETE
**Document:** [WRESTLER_RATING_OVERHAUL.md](./WRESTLER_RATING_OVERHAUL.md)

**Status:** IMPLEMENTED

**What Was Implemented:**
1. Updated `Wrestler` class with 27 new attributes across 5 categories:
   - Physical (6): strength, speed, agility, durability, stamina, recovery
   - Offense (8): striking, grappling, submission, high_flying, hardcore, power_moves, technical, dirty_tactics
   - Defense (4): strike_defense, grapple_defense, aerial_defense, ring_awareness
   - Entertainment (5): mic_skills, charisma, look, star_power, entrance
   - Intangibles (4): psychology, consistency, big_match, clutch
2. Added `FightingStyle` enum with 10 styles (powerhouse, technician, high_flyer, etc.)
3. Added finisher/signature move system with name, type, and damage
4. Legacy format auto-migration (old 9-attribute wrestlers convert automatically)
5. Updated wrestler profile UI with all new stats displayed
6. Updated create wrestler form with all 27 attributes
7. Made nickname optional (was required as "gimmick_name")
8. Added height/weight to wrestler bio
9. Added tier system based on overall rating
10. Added backward compatibility aliases (brawl, tech, air, psych, mic) for existing match code

**Files Modified:**
- `src/core/wrestler.py` (major rewrite - 590 lines)
- `src/services/game_service.py` (updated create_wrestler with new params)
- `src/ui/web/app.py` (updated create_wrestler route)
- `src/ui/web/templates/wrestler.html` (complete rewrite)
- `src/ui/web/templates/create_wrestler.html` (complete rewrite)
- `src/ui/web/templates/roster.html` (updated for nickname)
- `data/databases/default/wrestlers.json` (migrated to new format)

---

### Phase 2: Calendar & Brand System
**Document:** [CALENDAR_SYSTEM_OVERHAUL.md](./CALENDAR_SYSTEM_OVERHAUL.md)

**Why Second:**
- Provides the scheduling framework for shows
- Brand split determines which wrestlers/titles appear on which shows
- Must exist before commentary segments (segments are per-show)
- Weekly show structure needed for talking segments
- Creates the visual calendar UI users will interact with

**Key Deliverables:**
1. Create `Brand` class and management
2. Create `WeeklyShow` class for recurring shows
3. Create `CalendarManager` for scheduling
4. Build calendar view UI (month grid)
5. Add brand creation and management pages
6. Implement wrestler/title assignment to brands
7. Add draft/trade functionality
8. Update navigation with calendar dropdown

**Files to Create:**
- `src/core/brand.py`
- `src/core/weekly_show.py`
- `src/ui/web/templates/calendar.html`
- `src/ui/web/templates/brands.html`
- `src/ui/web/templates/create_weekly_show.html`
- `src/ui/web/templates/create_brand.html`
- `data/databases/default/brands.json`
- `data/databases/default/weekly_shows.json`

**Files to Modify:**
- `src/core/calendar.py` (major rewrite)
- `src/core/game_state.py`
- `src/services/game_service.py`
- `src/ui/web/app.py`
- `src/ui/web/templates/base.html`
- `src/ui/web/templates/dashboard.html`

**Estimated Scope:** ~20-25 files affected

---

### Phase 3: Commentary & Segments System
**Document:** [COMMENTARY_SYSTEM_OVERHAUL.md](./COMMENTARY_SYSTEM_OVERHAUL.md)

**Why Third:**
- Depends on wrestler attributes (fighting styles, finishers) from Phase 1
- Depends on show structure (major/minor, segments) from Phase 2
- Talking segments only make sense with weekly TV shows
- Can reference brand rivalries and storylines
- Enhances existing functionality rather than restructuring data

**Key Deliverables:**
1. Rewrite commentary generation with match phases
2. Add wrestler-specific move callouts (uses Phase 1 finishers)
3. Create segment types (promo, interview, confrontation, etc.)
4. Add segment booking to weekly shows (uses Phase 2 show structure)
5. Calculate segment ratings based on mic skills
6. Update results page to show segments between matches
7. Add segment booking UI to booking page

**Files to Create:**
- `src/core/segment.py`

**Files to Modify:**
- `src/core/commentary.py` (major rewrite)
- `src/core/show.py`
- `src/core/game_state.py`
- `src/services/game_service.py`
- `src/ui/web/app.py`
- `src/ui/web/templates/booking.html`
- `src/ui/web/templates/results.html`

**Estimated Scope:** ~10-15 files affected

---

## Dependency Graph

```
┌─────────────────────────────────────────────────────────────────┐
│                     PHASE 1: WRESTLER RATINGS                    │
│                                                                  │
│  - 27 attributes (physical, offense, defense, entertainment)    │
│  - Fighting styles                                               │
│  - Finisher/signature moves                                      │
│  - Optional nickname                                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PHASE 2: CALENDAR & BRANDS                     │
│                                                                  │
│  - Visual calendar view                                          │
│  - Recurring weekly shows (major/minor)                          │
│  - Brand split system                                            │
│  - Title/wrestler assignments                                    │
│                                                                  │
│  Depends on: Wrestler data structure (Phase 1)                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PHASE 3: COMMENTARY & SEGMENTS                  │
│                                                                  │
│  - Phased match commentary                                       │
│  - Wrestler-specific move callouts                               │
│  - Talking segments (promos, interviews, etc.)                   │
│  - Segment rating system                                         │
│                                                                  │
│  Depends on: Wrestler moves (Phase 1), Show structure (Phase 2)  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Tips

### Before Starting Each Phase

1. **Create a feature branch** for the phase
2. **Read the full document** before writing any code
3. **Start with data structures** (classes, dataclasses)
4. **Write migration scripts** before changing schemas
5. **Update tests** as you go (if tests exist)

### Migration Strategy

Each phase involves data structure changes. Follow this pattern:

```python
# 1. Add backward compatibility to class __init__
def __init__(self, data: dict):
    # New fields with defaults for old data
    self.new_field = data.get('new_field', default_value)

# 2. Create migration function
def migrate_old_data(old_data: dict) -> dict:
    """Convert old format to new format."""
    new_data = old_data.copy()
    new_data['new_field'] = calculate_default(old_data)
    return new_data

# 3. Run migration on existing save files
def migrate_save_file(filepath: str):
    with open(filepath) as f:
        old_data = json.load(f)
    new_data = [migrate_old_data(item) for item in old_data]
    with open(filepath, 'w') as f:
        json.dump(new_data, f, indent=4)
```

### Testing Approach

For each phase:
1. Test with a fresh new game
2. Test with an existing save file (migration)
3. Test UI forms and validation
4. Test edge cases (empty data, missing fields)

---

## Summary Table

| Phase | System | Key Changes | Dependencies | Files | Status |
|-------|--------|-------------|--------------|-------|--------|
| 1 | Wrestler Ratings | 27 attrs, styles, moves | None | ~15-20 | COMPLETE |
| 2 | Calendar/Brands | Calendar UI, brands, weekly shows | Phase 1 | ~20-25 | Pending |
| 3 | Commentary/Segments | Phased commentary, talking segments | Phase 1 & 2 | ~10-15 | Pending |

**Total Estimated Files:** 45-60 files across all phases

---

## Quick Links

- [Wrestler Rating Overhaul](./WRESTLER_RATING_OVERHAUL.md) - Phase 1
- [Calendar System Overhaul](./CALENDAR_SYSTEM_OVERHAUL.md) - Phase 2
- [Commentary System Overhaul](./COMMENTARY_SYSTEM_OVERHAUL.md) - Phase 3

---

## Notes

- Each phase can be released independently as a working update
- Phase 1 is the foundation - don't skip or rush it
- Phase 2 adds major new features users will interact with daily
- Phase 3 is the "polish" phase that enhances immersion
- Consider user feedback between phases before proceeding

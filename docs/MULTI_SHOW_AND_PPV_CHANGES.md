# Multi-Show Week & PPV Calendar Enhancements

## Overview

Currently the simulation limits users to running one show per week. This document outlines changes to support:
1. **Multiple shows per week** - If multiple brands/weekly shows exist, simulate all of them each week
2. **Custom PPV calendar** - Allow users to add/edit/remove PPVs from the calendar

---

## Current State

### Weekly Show Simulation
- `game_service.play_show()` advances the week after running a single show
- `game_service.simulate_week()` only books and plays one show
- Calendar generates `ScheduledShow` entries for ALL weekly shows, but the game flow only processes one

### PPV Calendar
- Hardcoded 12 PPVs in `calendar.py` (`PPV_CALENDAR` constant)
- One PPV per month at week 4
- No UI to add/edit/remove PPVs
- PPV tiers: Standard, Big Four, Flagship

---

## Proposed Changes

### 1. Multi-Show Week Support

#### A. New Week Flow
Instead of advancing week after each show, introduce a new flow:

```
Week N:
  1. Get all scheduled shows for week N
  2. User books/plays shows in order (by day_of_week)
  3. Only advance week when ALL shows for week N are completed
```

#### B. Changes to `game_service.py`

**New method: `get_remaining_shows_this_week()`**
- Returns list of uncompleted `ScheduledShow` objects for current week
- Ordered by `day_of_week` (Monday first, Sunday last)

**Modify: `play_show()`**
- Remove automatic `advance_week()` call
- Check if all shows for week are completed
- Only advance week if no remaining shows

**New method: `advance_week_if_complete()`**
- Called after each show
- Checks `get_remaining_shows_this_week()`
- If empty, calls `advance_week()`

**Modify: `simulate_week()`**
- Loop through ALL scheduled shows for the week
- Auto-book and play each one
- Advance week only after all are done

#### C. Changes to `calendar.py`

**New method in `CalendarManager`: `get_incomplete_shows_for_week(year, month, week)`**
- Returns `ScheduledShow` objects where `is_completed=False`
- Sorted by `day_of_week`

**New method: `all_shows_completed_for_week(year, month, week)`**
- Returns `True` if no incomplete shows remain

#### D. UI/CLI Changes
- Show list of remaining shows for the week
- Indicate which show is "next" (by day)
- Display completion status per show

---

### 2. Custom PPV Calendar

#### A. Data Structure Changes

**Modify `CalendarManager`**
- Change `ppv_calendar` from constant to instance variable
- Load/save with calendar data
- Support dynamic add/edit/delete

**New class: `PPVDefinition`**
```python
@dataclass
class PPVDefinition:
    id: int
    name: str
    month: int           # 1-12
    week: int            # 1-4 (or 5 for some months)
    tier: str            # "Standard", "Big Four", "Flagship"
    brand_id: Optional[int]  # None = dual-brand
    is_active: bool      # Can disable without deleting
```

#### B. CalendarManager Methods

**`add_ppv(name, month, week, tier, brand_id=None)`**
- Create new PPV definition
- Regenerate affected month's schedule

**`edit_ppv(ppv_id, **kwargs)`**
- Update PPV properties
- Handle month/week changes (reschedule)

**`remove_ppv(ppv_id)`**
- Delete PPV from calendar
- Remove any associated scheduled shows

**`get_ppv_calendar()`**
- Return list of all PPV definitions
- Ordered by month, then week

**`get_ppvs_for_month(month)`**
- Filter PPVs for specific month

#### C. Schedule Generation Updates

**Modify `generate_month_schedule()`**
- Use instance `ppv_calendar` instead of constant
- Support multiple PPVs in same month
- Support PPVs on any week (not just week 4)

#### D. Persistence

**Update `to_dict()` / `from_dict()`**
- Serialize `ppv_calendar` list
- Include all PPV definitions with IDs

---

## Implementation Order

### Phase 1: Multi-Show Week (Priority)
1. Add `get_incomplete_shows_for_week()` to CalendarManager
2. Add `all_shows_completed_for_week()` to CalendarManager
3. Modify `play_show()` to not auto-advance
4. Add `advance_week_if_complete()` logic
5. Update `simulate_week()` to handle all shows
6. Test with 2-brand setup

### Phase 2: PPV Calendar
1. Create `PPVDefinition` dataclass
2. Convert `PPV_CALENDAR` constant to instance variable
3. Add CRUD methods for PPVs
4. Update schedule generation
5. Update serialization
6. Add CLI/UI commands

---

## Testing Scenarios

### Multi-Show
- Single brand (1 show/week) - should work as before
- Two brands (2 shows/week) - must play both before week advances
- Three+ shows - all must complete
- Mix of major/minor shows in same week

### PPV Calendar
- Add PPV to empty month
- Add second PPV to same month
- Move PPV to different month
- Change PPV from dual-brand to single-brand
- Delete PPV mid-year

---

## Notes

- Week advancement is the critical change - must not break existing saves
- PPV calendar changes should migrate existing hardcoded PPVs to new format
- Consider: What happens if user skips a show? Force completion or allow skip?

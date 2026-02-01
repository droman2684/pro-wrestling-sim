# Calendar & Schedule System Overhaul

## Overview

This document outlines the plan to overhaul the calendar system to include a visual calendar view, recurring weekly shows, major/minor show designations, and a brand split system with title assignments.

---

## Current System (To Be Replaced)

### Current Calendar Implementation

**Location:** `src/core/calendar.py`

**Current Features:**
- Static `PPV_CALENDAR` list with 12 PPVs (one per month, always week 4)
- Simple Year/Month/Week tracking in `GameState`
- `is_ppv_week()` and `get_next_ppv()` helper functions
- No weekly show scheduling
- No recurring shows
- No brand split

**Current Problems:**
1. No visual calendar view
2. Cannot create custom weekly shows
3. No recurring show support (like "every Monday")
4. No major/minor show distinction
5. No brand split or title assignments to shows
6. PPVs are hardcoded, not customizable
7. No way to see upcoming schedule

---

## New Calendar System

### Core Concepts

#### Days of the Week
```python
class DayOfWeek(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
```

#### Show Tiers
```python
class ShowTier(Enum):
    MAJOR = "major"          # Flagship weekly show (Raw, Nitro)
    MINOR = "minor"          # Secondary weekly show (Velocity, Heat)
    PPV = "ppv"              # Pay-per-view event
    SPECIAL = "special"      # Special one-off events
```

#### Brand System
```python
@dataclass
class Brand:
    """A brand/roster split (like Raw vs SmackDown)."""
    id: int
    name: str                           # "Monday Night Raw", "Thursday Nitro"
    short_name: str                     # "Raw", "Nitro"
    color: str                          # Hex color for UI (#FF0000)
    assigned_titles: List[int]          # Title IDs exclusive to this brand
    assigned_wrestlers: List[int]       # Wrestler IDs on this brand
    weekly_show: Optional['WeeklyShow'] # The recurring show for this brand
    is_active: bool = True

    def get_roster(self, all_wrestlers: List) -> List:
        """Get wrestlers assigned to this brand."""
        return [w for w in all_wrestlers if w.id in self.assigned_wrestlers]

    def get_titles(self, all_titles: List) -> List:
        """Get titles assigned to this brand."""
        return [t for t in all_titles if t.id in self.assigned_titles]
```

---

### Weekly Show System

#### Weekly Show Definition
```python
@dataclass
class WeeklyShow:
    """A recurring weekly television show."""
    id: int
    name: str                           # "Monday Night Raw"
    short_name: str                     # "Raw"
    day_of_week: DayOfWeek              # When it airs
    tier: ShowTier                      # MAJOR or MINOR
    brand_id: Optional[int]             # Associated brand (for brand split)
    arena: str                          # Default arena name
    is_active: bool = True

    # Show configuration
    match_slots: int = 5                # Number of matches per show
    segment_slots: int = 3              # Number of talking segments
    runtime_minutes: int = 120          # 2 hours default

    # Stats tracking
    total_episodes: int = 0
    average_rating: float = 0.0

    def get_next_occurrence(self, current_week: int, current_year: int) -> dict:
        """Calculate the next date this show will air."""
        pass
```

#### Show Scheduling
```python
@dataclass
class ScheduledShow:
    """A specific instance of a show on the calendar."""
    id: int
    show_type: str                      # "weekly", "ppv", "special"
    name: str                           # Show name
    brand_id: Optional[int]             # Brand association

    # Date
    year: int
    month: int
    week: int
    day_of_week: DayOfWeek

    # Show details
    tier: ShowTier
    arena: str = ""
    is_booked: bool = False             # Has the card been set?
    is_completed: bool = False          # Has it been run?
    card: Optional['Show'] = None       # The actual Show object when booked
    result: Optional['ShowResult'] = None  # Result after running

    # For PPVs
    ppv_tier: str = ""                  # "Standard", "Big Four", "Flagship"

    @property
    def display_date(self) -> str:
        """Human readable date string."""
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        return f"{day_names[self.day_of_week.value]}, Week {self.week}, Month {self.month}, Year {self.year}"
```

---

### Brand Split System

#### Title-to-Brand Assignment
```python
@dataclass
class TitleAssignment:
    """Links a title to a brand."""
    title_id: int
    brand_id: int
    assigned_date: dict                 # {year, month, week}
    is_exclusive: bool = True           # Can only be defended on this brand's shows

    # Floating titles (can appear on any brand)
    # Set is_exclusive = False for titles like WWE Championship
    # that can be defended across brands
```

#### Wrestler-to-Brand Assignment
```python
@dataclass
class WrestlerAssignment:
    """Links a wrestler to a brand."""
    wrestler_id: int
    brand_id: int
    assigned_date: dict                 # {year, month, week}
    is_free_agent: bool = False         # Can appear on any show

    # Draft/Trade history
    previous_brands: List[dict] = field(default_factory=list)
    # [{brand_id, start_date, end_date}, ...]
```

---

### Calendar Manager

```python
class CalendarManager:
    """Manages the schedule and calendar for the game."""

    def __init__(self, game_state: 'GameState'):
        self.game_state = game_state
        self.brands: List[Brand] = []
        self.weekly_shows: List[WeeklyShow] = []
        self.scheduled_shows: List[ScheduledShow] = []
        self.ppv_calendar: List[dict] = []

    # Brand Management
    def create_brand(self, name: str, short_name: str, color: str) -> Brand:
        """Create a new brand."""
        pass

    def assign_wrestler_to_brand(self, wrestler_id: int, brand_id: int) -> None:
        """Assign a wrestler to a brand."""
        pass

    def assign_title_to_brand(self, title_id: int, brand_id: int, exclusive: bool = True) -> None:
        """Assign a title to a brand."""
        pass

    def draft_wrestler(self, wrestler_id: int, from_brand_id: int, to_brand_id: int) -> None:
        """Move a wrestler from one brand to another."""
        pass

    # Weekly Show Management
    def create_weekly_show(
        self,
        name: str,
        day_of_week: DayOfWeek,
        tier: ShowTier,
        brand_id: Optional[int] = None
    ) -> WeeklyShow:
        """Create a new recurring weekly show."""
        pass

    def update_weekly_show(self, show_id: int, **kwargs) -> None:
        """Update weekly show settings."""
        pass

    def deactivate_weekly_show(self, show_id: int) -> None:
        """Stop a weekly show from recurring."""
        pass

    # Schedule Management
    def generate_month_schedule(self, year: int, month: int) -> List[ScheduledShow]:
        """Generate all scheduled shows for a given month."""
        scheduled = []

        # Add weekly shows for each week
        for week in range(1, 5):
            for weekly_show in self.weekly_shows:
                if weekly_show.is_active:
                    scheduled.append(ScheduledShow(
                        id=self._get_next_id(),
                        show_type="weekly",
                        name=weekly_show.name,
                        brand_id=weekly_show.brand_id,
                        year=year,
                        month=month,
                        week=week,
                        day_of_week=weekly_show.day_of_week,
                        tier=weekly_show.tier,
                    ))

        # Add PPVs
        for ppv in self.ppv_calendar:
            if ppv['month'] == month:
                scheduled.append(ScheduledShow(
                    id=self._get_next_id(),
                    show_type="ppv",
                    name=ppv['name'],
                    brand_id=ppv.get('brand_id'),
                    year=year,
                    month=month,
                    week=ppv['week'],
                    day_of_week=DayOfWeek.SUNDAY,  # PPVs on Sunday
                    tier=ShowTier.PPV,
                    ppv_tier=ppv['tier'],
                ))

        return sorted(scheduled, key=lambda x: (x.week, x.day_of_week.value))

    def get_week_schedule(self, year: int, month: int, week: int) -> List[ScheduledShow]:
        """Get all shows for a specific week."""
        return [s for s in self.scheduled_shows
                if s.year == year and s.month == month and s.week == week]

    def get_upcoming_shows(self, count: int = 10) -> List[ScheduledShow]:
        """Get the next N upcoming shows."""
        current = (self.game_state.year, self.game_state.month, self.game_state.week)
        future = [s for s in self.scheduled_shows
                  if (s.year, s.month, s.week) >= current and not s.is_completed]
        return sorted(future, key=lambda x: (x.year, x.month, x.week, x.day_of_week.value))[:count]
```

---

### Calendar View Data Structure

```python
@dataclass
class CalendarMonth:
    """Data structure for rendering a month calendar view."""
    year: int
    month: int
    month_name: str                     # "January", "February", etc.
    weeks: List['CalendarWeek']

@dataclass
class CalendarWeek:
    """A single week in the calendar."""
    week_number: int                    # 1-4
    days: List['CalendarDay']
    is_current_week: bool = False

@dataclass
class CalendarDay:
    """A single day in the calendar."""
    day_of_week: DayOfWeek
    day_name: str                       # "Monday", etc.
    shows: List[ScheduledShow]          # Shows on this day
    is_today: bool = False

def generate_calendar_view(
    calendar_manager: CalendarManager,
    year: int,
    month: int
) -> CalendarMonth:
    """Generate calendar view data for a specific month."""
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    weeks = []
    for week_num in range(1, 5):
        days = []
        for day in DayOfWeek:
            shows = calendar_manager.get_shows_for_day(year, month, week_num, day)
            days.append(CalendarDay(
                day_of_week=day,
                day_name=day.name.capitalize(),
                shows=shows,
                is_today=(
                    calendar_manager.game_state.year == year and
                    calendar_manager.game_state.month == month and
                    calendar_manager.game_state.week == week_num
                    # Note: We don't track current day, only week
                )
            ))

        weeks.append(CalendarWeek(
            week_number=week_num,
            days=days,
            is_current_week=(
                calendar_manager.game_state.year == year and
                calendar_manager.game_state.month == month and
                calendar_manager.game_state.week == week_num
            )
        ))

    return CalendarMonth(
        year=year,
        month=month,
        month_name=month_names[month - 1],
        weeks=weeks
    )
```

---

### PPV Calendar Updates

```python
# Updated PPV structure with brand support
PPV_CALENDAR = [
    {
        'month': 1, 'week': 4,
        'name': "New Year's Fury",
        'tier': 'Standard',
        'brand_id': None,               # None = all brands (joint PPV)
        'is_dual_brand': True,          # Both brands participate
    },
    {
        'month': 2, 'week': 4,
        'name': 'No Way Out',
        'tier': 'Standard',
        'brand_id': 1,                  # Brand-exclusive PPV
        'is_dual_brand': False,
    },
    {
        'month': 3, 'week': 4,
        'name': 'Championship Chaos',
        'tier': 'Big Four',
        'brand_id': None,
        'is_dual_brand': True,
    },
    # ... etc
]

# Allow custom PPV creation
@dataclass
class CustomPPV:
    """A user-created PPV event."""
    id: int
    name: str
    month: int
    week: int
    tier: str                           # Standard, Big Four, Flagship
    brand_id: Optional[int]             # None for dual-brand
    is_dual_brand: bool = True
    arena: str = ""
    match_slots: int = 7                # PPVs have more matches
```

---

### JSON Data Structure

#### brands.json
```json
[
    {
        "id": 1,
        "name": "Monday Night Raw",
        "short_name": "Raw",
        "color": "#FF0000",
        "assigned_titles": [1, 3, 5],
        "assigned_wrestlers": [1, 2, 3, 4, 5, 6, 7, 8],
        "is_active": true
    },
    {
        "id": 2,
        "name": "Thursday Nitro",
        "short_name": "Nitro",
        "color": "#FFD700",
        "assigned_titles": [2, 4, 6],
        "assigned_wrestlers": [9, 10, 11, 12, 13, 14, 15],
        "is_active": true
    }
]
```

#### weekly_shows.json
```json
[
    {
        "id": 1,
        "name": "Monday Night Raw",
        "short_name": "Raw",
        "day_of_week": 0,
        "tier": "major",
        "brand_id": 1,
        "arena": "Various Arenas",
        "is_active": true,
        "match_slots": 5,
        "segment_slots": 3,
        "runtime_minutes": 120,
        "total_episodes": 0,
        "average_rating": 0.0
    },
    {
        "id": 2,
        "name": "Thursday Nitro",
        "short_name": "Nitro",
        "day_of_week": 3,
        "tier": "major",
        "brand_id": 2,
        "arena": "Various Arenas",
        "is_active": true,
        "match_slots": 5,
        "segment_slots": 3,
        "runtime_minutes": 120,
        "total_episodes": 0,
        "average_rating": 0.0
    },
    {
        "id": 3,
        "name": "Sunday Heat",
        "short_name": "Heat",
        "day_of_week": 6,
        "tier": "minor",
        "brand_id": null,
        "arena": "TV Studio",
        "is_active": true,
        "match_slots": 4,
        "segment_slots": 1,
        "runtime_minutes": 60,
        "total_episodes": 0,
        "average_rating": 0.0
    }
]
```

#### schedule.json (generated per month)
```json
{
    "year": 1,
    "month": 3,
    "scheduled_shows": [
        {
            "id": 1,
            "show_type": "weekly",
            "name": "Monday Night Raw",
            "brand_id": 1,
            "year": 1,
            "month": 3,
            "week": 1,
            "day_of_week": 0,
            "tier": "major",
            "is_booked": false,
            "is_completed": false
        },
        {
            "id": 2,
            "show_type": "weekly",
            "name": "Thursday Nitro",
            "brand_id": 2,
            "year": 1,
            "month": 3,
            "week": 1,
            "day_of_week": 3,
            "tier": "major",
            "is_booked": false,
            "is_completed": false
        },
        {
            "id": 3,
            "show_type": "ppv",
            "name": "Championship Chaos",
            "brand_id": null,
            "year": 1,
            "month": 3,
            "week": 4,
            "day_of_week": 6,
            "tier": "ppv",
            "ppv_tier": "Big Four",
            "is_booked": false,
            "is_completed": false
        }
    ]
}
```

---

### UI Components

#### Calendar View Template (`calendar.html`)
```html
{% extends "base.html" %}

{% block title %}Calendar - {{ calendar.month_name }} Year {{ calendar.year }}{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <div class="d-flex align-items-center gap-3">
        <a href="{{ url_for('calendar_view', year=prev_year, month=prev_month) }}"
           class="btn btn-outline-light">
            <i class="bi bi-chevron-left"></i>
        </a>
        <h2 class="mb-0">
            <i class="bi bi-calendar3 me-2 text-gold"></i>
            {{ calendar.month_name }} - Year {{ calendar.year }}
        </h2>
        <a href="{{ url_for('calendar_view', year=next_year, month=next_month) }}"
           class="btn btn-outline-light">
            <i class="bi bi-chevron-right"></i>
        </a>
    </div>
    <a href="{{ url_for('create_weekly_show') }}" class="btn btn-gold">
        <i class="bi bi-plus-circle me-1"></i>Create Weekly Show
    </a>
</div>

<!-- Calendar Legend -->
<div class="d-flex gap-3 mb-4">
    <span class="badge bg-danger">Major Show</span>
    <span class="badge bg-secondary">Minor Show</span>
    <span class="badge bg-warning text-dark">PPV</span>
    {% for brand in brands %}
    <span class="badge" style="background-color: {{ brand.color }};">{{ brand.short_name }}</span>
    {% endfor %}
</div>

<!-- Calendar Grid -->
<div class="card border-0 shadow-sm">
    <div class="card-body p-0">
        <table class="table table-bordered mb-0 calendar-table">
            <thead class="bg-dark text-white">
                <tr>
                    <th class="text-center" style="width: 5%;">Week</th>
                    <th style="width: 13.5%;">Monday</th>
                    <th style="width: 13.5%;">Tuesday</th>
                    <th style="width: 13.5%;">Wednesday</th>
                    <th style="width: 13.5%;">Thursday</th>
                    <th style="width: 13.5%;">Friday</th>
                    <th style="width: 13.5%;">Saturday</th>
                    <th style="width: 13.5%;">Sunday</th>
                </tr>
            </thead>
            <tbody>
                {% for week in calendar.weeks %}
                <tr class="{% if week.is_current_week %}table-active current-week{% endif %}">
                    <td class="text-center align-middle bg-light">
                        <strong>{{ week.week_number }}</strong>
                        {% if week.is_current_week %}
                        <br><small class="text-success">NOW</small>
                        {% endif %}
                    </td>
                    {% for day in week.days %}
                    <td class="calendar-day p-2">
                        {% for show in day.shows %}
                        <div class="calendar-show mb-1 p-2 rounded
                            {% if show.tier.value == 'ppv' %}bg-warning bg-opacity-25 border-warning
                            {% elif show.tier.value == 'major' %}bg-danger bg-opacity-10 border-danger
                            {% else %}bg-secondary bg-opacity-10 border-secondary{% endif %}
                            border-start border-3"
                            {% if show.brand_id %}
                            style="border-left-color: {{ get_brand_color(show.brand_id) }} !important;"
                            {% endif %}>

                            <div class="d-flex justify-content-between align-items-start">
                                <strong class="small">{{ show.name }}</strong>
                                {% if show.is_completed %}
                                <i class="bi bi-check-circle-fill text-success"></i>
                                {% elif show.is_booked %}
                                <i class="bi bi-calendar-check text-info"></i>
                                {% endif %}
                            </div>

                            {% if show.show_type == 'ppv' %}
                            <span class="badge bg-warning text-dark mt-1" style="font-size: 0.65rem;">
                                {{ show.ppv_tier }}
                            </span>
                            {% endif %}

                            {% if not show.is_completed and not show.is_booked %}
                            <a href="{{ url_for('book_show', show_id=show.id) }}"
                               class="btn btn-sm btn-outline-primary mt-2 w-100">
                                Book
                            </a>
                            {% elif show.is_booked and not show.is_completed %}
                            <a href="{{ url_for('run_scheduled_show', show_id=show.id) }}"
                               class="btn btn-sm btn-success mt-2 w-100">
                                Run Show
                            </a>
                            {% elif show.is_completed %}
                            <a href="{{ url_for('show_results', show_id=show.id) }}"
                               class="btn btn-sm btn-outline-light mt-2 w-100">
                                Results
                            </a>
                            {% endif %}
                        </div>
                        {% else %}
                        <div class="text-muted small text-center py-3">
                            No shows
                        </div>
                        {% endfor %}
                    </td>
                    {% endfor %}
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>

<!-- Upcoming Shows List (Alternative View) -->
<div class="card border-0 shadow-sm mt-4">
    <div class="card-header bg-white">
        <h5 class="mb-0"><i class="bi bi-list-ul me-2"></i>Upcoming Shows</h5>
    </div>
    <div class="card-body p-0">
        <table class="table table-hover mb-0">
            <thead class="bg-light">
                <tr>
                    <th>Show</th>
                    <th>Day</th>
                    <th>Date</th>
                    <th>Brand</th>
                    <th>Status</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                {% for show in upcoming_shows %}
                <tr>
                    <td>
                        <strong>{{ show.name }}</strong>
                        {% if show.show_type == 'ppv' %}
                        <span class="badge bg-warning text-dark ms-2">PPV</span>
                        {% endif %}
                    </td>
                    <td>{{ show.day_of_week.name|capitalize }}</td>
                    <td>Week {{ show.week }}, Month {{ show.month }}</td>
                    <td>
                        {% if show.brand_id %}
                        {% set brand = get_brand(show.brand_id) %}
                        <span class="badge" style="background-color: {{ brand.color }};">
                            {{ brand.short_name }}
                        </span>
                        {% else %}
                        <span class="text-muted">All Brands</span>
                        {% endif %}
                    </td>
                    <td>
                        {% if show.is_completed %}
                        <span class="badge bg-success">Completed</span>
                        {% elif show.is_booked %}
                        <span class="badge bg-info">Booked</span>
                        {% else %}
                        <span class="badge bg-secondary">Pending</span>
                        {% endif %}
                    </td>
                    <td>
                        {% if not show.is_completed and not show.is_booked %}
                        <a href="{{ url_for('book_show', show_id=show.id) }}"
                           class="btn btn-sm btn-outline-primary">Book</a>
                        {% elif show.is_booked and not show.is_completed %}
                        <a href="{{ url_for('run_scheduled_show', show_id=show.id) }}"
                           class="btn btn-sm btn-success">Run</a>
                        {% else %}
                        <a href="{{ url_for('show_results', show_id=show.id) }}"
                           class="btn btn-sm btn-outline-light">View</a>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
```

#### Create Weekly Show Form (`create_weekly_show.html`)
```html
{% extends "base.html" %}

{% block title %}Create Weekly Show{% endblock %}

{% block content %}
<h2 class="mb-4">
    <i class="bi bi-calendar-plus me-2 text-gold"></i>Create Weekly Show
</h2>

<div class="card border-0 shadow-sm">
    <div class="card-body">
        <form method="post" action="{{ url_for('create_weekly_show') }}">
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label class="form-label">Show Name</label>
                    <input type="text" name="name" class="form-control"
                           placeholder="e.g., Monday Night Raw" required>
                </div>
                <div class="col-md-6 mb-3">
                    <label class="form-label">Short Name</label>
                    <input type="text" name="short_name" class="form-control"
                           placeholder="e.g., Raw" required>
                </div>
            </div>

            <div class="row">
                <div class="col-md-6 mb-3">
                    <label class="form-label">Day of Week</label>
                    <select name="day_of_week" class="form-select" required>
                        <option value="0">Monday</option>
                        <option value="1">Tuesday</option>
                        <option value="2">Wednesday</option>
                        <option value="3">Thursday</option>
                        <option value="4">Friday</option>
                        <option value="5">Saturday</option>
                        <option value="6">Sunday</option>
                    </select>
                </div>
                <div class="col-md-6 mb-3">
                    <label class="form-label">Show Tier</label>
                    <select name="tier" class="form-select" required>
                        <option value="major">Major (Flagship Show)</option>
                        <option value="minor">Minor (Secondary Show)</option>
                    </select>
                    <div class="form-text">
                        Major shows are flagship programs like Raw or Nitro.
                        Minor shows are secondary programs like Heat or Velocity.
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-6 mb-3">
                    <label class="form-label">Brand (Optional)</label>
                    <select name="brand_id" class="form-select">
                        <option value="">No Brand (All Rosters)</option>
                        {% for brand in brands %}
                        <option value="{{ brand.id }}">{{ brand.name }}</option>
                        {% endfor %}
                    </select>
                    <div class="form-text">
                        Assign this show to a specific brand for roster/title exclusivity.
                    </div>
                </div>
                <div class="col-md-6 mb-3">
                    <label class="form-label">Runtime (Minutes)</label>
                    <select name="runtime" class="form-select">
                        <option value="60">1 Hour</option>
                        <option value="120" selected>2 Hours</option>
                        <option value="180">3 Hours</option>
                    </select>
                </div>
            </div>

            <div class="row">
                <div class="col-md-6 mb-3">
                    <label class="form-label">Match Slots</label>
                    <input type="number" name="match_slots" class="form-control"
                           value="5" min="2" max="10">
                </div>
                <div class="col-md-6 mb-3">
                    <label class="form-label">Segment Slots</label>
                    <input type="number" name="segment_slots" class="form-control"
                           value="3" min="0" max="6">
                </div>
            </div>

            <div class="d-flex gap-2">
                <button type="submit" class="btn btn-gold">
                    <i class="bi bi-check-circle me-1"></i>Create Show
                </button>
                <a href="{{ url_for('calendar_view') }}" class="btn btn-outline-light">Cancel</a>
            </div>
        </form>
    </div>
</div>
{% endblock %}
```

#### Brand Management Page (`brands.html`)
```html
{% extends "base.html" %}

{% block title %}Brand Management{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h2 class="mb-0">
        <i class="bi bi-diagram-3 me-2 text-gold"></i>Brand Split
    </h2>
    <a href="{{ url_for('create_brand') }}" class="btn btn-gold">
        <i class="bi bi-plus-circle me-1"></i>Create Brand
    </a>
</div>

{% if not brands %}
<div class="info-box">
    <h5>No Brand Split Active</h5>
    <p class="mb-0">
        Create brands to split your roster into separate shows with exclusive titles.
        This is similar to WWE's Raw vs SmackDown split.
    </p>
</div>
{% else %}

<div class="row">
    {% for brand in brands %}
    <div class="col-lg-6 mb-4">
        <div class="card border-0 shadow-sm h-100"
             style="border-top: 4px solid {{ brand.color }} !important;">
            <div class="card-header bg-white d-flex justify-content-between align-items-center">
                <h4 class="mb-0" style="color: {{ brand.color }};">
                    {{ brand.name }}
                </h4>
                <span class="badge" style="background-color: {{ brand.color }};">
                    {{ brand.short_name }}
                </span>
            </div>
            <div class="card-body">
                <!-- Weekly Show -->
                <div class="mb-4">
                    <h6 class="text-muted small text-uppercase">Weekly Show</h6>
                    {% if brand.weekly_show %}
                    <p class="mb-0">
                        <strong>{{ brand.weekly_show.name }}</strong>
                        ({{ brand.weekly_show.day_of_week.name|capitalize }}s)
                    </p>
                    {% else %}
                    <p class="text-muted mb-0">No weekly show assigned</p>
                    {% endif %}
                </div>

                <!-- Assigned Titles -->
                <div class="mb-4">
                    <h6 class="text-muted small text-uppercase">Exclusive Titles</h6>
                    {% set brand_titles = brand.get_titles(titles) %}
                    {% if brand_titles %}
                    <div class="d-flex flex-wrap gap-2">
                        {% for title in brand_titles %}
                        <span class="badge badge-champion">
                            <i class="bi bi-trophy-fill me-1"></i>{{ title.name }}
                        </span>
                        {% endfor %}
                    </div>
                    {% else %}
                    <p class="text-muted mb-0">No titles assigned</p>
                    {% endif %}
                </div>

                <!-- Roster Count -->
                <div class="mb-4">
                    <h6 class="text-muted small text-uppercase">Roster</h6>
                    {% set brand_roster = brand.get_roster(roster) %}
                    <p class="mb-0">
                        <strong>{{ brand_roster|length }}</strong> wrestlers assigned
                        <a href="{{ url_for('brand_roster', brand_id=brand.id) }}"
                           class="ms-2 small">View Roster</a>
                    </p>
                </div>
            </div>
            <div class="card-footer bg-white">
                <div class="d-flex gap-2">
                    <a href="{{ url_for('edit_brand', brand_id=brand.id) }}"
                       class="btn btn-sm btn-outline-primary">
                        <i class="bi bi-pencil me-1"></i>Edit
                    </a>
                    <a href="{{ url_for('assign_titles', brand_id=brand.id) }}"
                       class="btn btn-sm btn-outline-primary">
                        <i class="bi bi-trophy me-1"></i>Manage Titles
                    </a>
                    <a href="{{ url_for('assign_wrestlers', brand_id=brand.id) }}"
                       class="btn btn-sm btn-outline-primary">
                        <i class="bi bi-people me-1"></i>Manage Roster
                    </a>
                </div>
            </div>
        </div>
    </div>
    {% endfor %}
</div>

<!-- Draft Feature -->
<div class="card border-0 shadow-sm mt-4">
    <div class="card-header bg-white">
        <h5 class="mb-0"><i class="bi bi-arrow-left-right me-2"></i>Draft / Trade</h5>
    </div>
    <div class="card-body">
        <p class="text-muted">Move wrestlers between brands through drafts or trades.</p>
        <a href="{{ url_for('draft') }}" class="btn btn-outline-primary">
            <i class="bi bi-shuffle me-1"></i>Start Draft
        </a>
    </div>
</div>

{% endif %}
{% endblock %}
```

---

### New Flask Routes

```python
# Calendar routes
@app.route('/calendar')
@app.route('/calendar/<int:year>/<int:month>')
@require_game_loaded
def calendar_view(year=None, month=None):
    """Display calendar view for a month."""
    if year is None:
        year = game_service.game_state.year
    if month is None:
        month = game_service.game_state.month

    calendar_data = game_service.get_calendar_month(year, month)
    upcoming = game_service.get_upcoming_shows(10)
    brands = game_service.get_brands()

    return render_template('calendar.html',
        calendar=calendar_data,
        upcoming_shows=upcoming,
        brands=brands,
        prev_year=year if month > 1 else year - 1,
        prev_month=month - 1 if month > 1 else 12,
        next_year=year if month < 12 else year + 1,
        next_month=month + 1 if month < 12 else 1,
    )

# Weekly show management
@app.route('/create-weekly-show', methods=['GET', 'POST'])
@require_game_loaded
def create_weekly_show():
    """Create a new recurring weekly show."""
    if request.method == 'POST':
        # Handle creation
        pass
    brands = game_service.get_brands()
    return render_template('create_weekly_show.html', brands=brands)

@app.route('/weekly-shows')
@require_game_loaded
def weekly_shows():
    """List all weekly shows."""
    shows = game_service.get_weekly_shows()
    return render_template('weekly_shows.html', shows=shows)

# Brand management
@app.route('/brands')
@require_game_loaded
def brands():
    """Brand management page."""
    brands = game_service.get_brands()
    titles = game_service.game_state.titles
    roster = game_service.game_state.roster
    return render_template('brands.html', brands=brands, titles=titles, roster=roster)

@app.route('/create-brand', methods=['GET', 'POST'])
@require_game_loaded
def create_brand():
    """Create a new brand."""
    pass

@app.route('/brand/<int:brand_id>/roster')
@require_game_loaded
def brand_roster(brand_id):
    """View wrestlers assigned to a brand."""
    pass

@app.route('/brand/<int:brand_id>/assign-wrestlers', methods=['GET', 'POST'])
@require_game_loaded
def assign_wrestlers(brand_id):
    """Assign wrestlers to a brand."""
    pass

@app.route('/brand/<int:brand_id>/assign-titles', methods=['GET', 'POST'])
@require_game_loaded
def assign_titles(brand_id):
    """Assign titles to a brand."""
    pass

@app.route('/draft', methods=['GET', 'POST'])
@require_game_loaded
def draft():
    """Draft wrestlers between brands."""
    pass

# Scheduled show management
@app.route('/book-show/<int:show_id>', methods=['GET', 'POST'])
@require_game_loaded
def book_show(show_id):
    """Book matches for a scheduled show."""
    pass

@app.route('/run-show/<int:show_id>', methods=['POST'])
@require_game_loaded
def run_scheduled_show(show_id):
    """Run a scheduled show."""
    pass
```

---

### Navigation Updates

Add to `base.html` navbar:
```html
<!-- Calendar dropdown -->
<li class="nav-item dropdown">
    <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
        <i class="bi bi-calendar3 me-1"></i>Schedule
    </a>
    <ul class="dropdown-menu">
        <li><a class="dropdown-item" href="{{ url_for('calendar_view') }}">
            <i class="bi bi-calendar-month me-2"></i>Calendar View
        </a></li>
        <li><a class="dropdown-item" href="{{ url_for('weekly_shows') }}">
            <i class="bi bi-tv me-2"></i>Weekly Shows
        </a></li>
        <li><hr class="dropdown-divider"></li>
        <li><a class="dropdown-item" href="{{ url_for('brands') }}">
            <i class="bi bi-diagram-3 me-2"></i>Brand Split
        </a></li>
    </ul>
</li>
```

---

### Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/core/calendar.py` | Rewrite | Complete overhaul with new classes |
| `src/core/brand.py` | Create | Brand class and management |
| `src/core/weekly_show.py` | Create | Weekly show classes |
| `src/core/game_state.py` | Modify | Add calendar manager, brands |
| `src/services/game_service.py` | Modify | Add calendar/brand methods |
| `src/ui/web/app.py` | Modify | Add new routes |
| `templates/calendar.html` | Create | Calendar view page |
| `templates/create_weekly_show.html` | Create | Create show form |
| `templates/weekly_shows.html` | Create | List weekly shows |
| `templates/brands.html` | Create | Brand management page |
| `templates/create_brand.html` | Create | Create brand form |
| `templates/brand_roster.html` | Create | Brand roster view |
| `templates/assign_wrestlers.html` | Create | Assign wrestlers to brand |
| `templates/assign_titles.html` | Create | Assign titles to brand |
| `templates/base.html` | Modify | Add calendar nav dropdown |
| `templates/dashboard.html` | Modify | Add upcoming shows widget |
| `data/databases/default/brands.json` | Create | Default brand data |
| `data/databases/default/weekly_shows.json` | Create | Default show data |

---

### Summary of Features

| Feature | Current | New |
|---------|---------|-----|
| Calendar View | None | Full month grid view |
| Weekly Shows | None | Recurring shows on specific days |
| Show Tiers | PPV only | Major, Minor, PPV, Special |
| Brands | None | Full brand split system |
| Title Assignment | Global | Per-brand exclusive |
| Wrestler Assignment | Global | Per-brand roster |
| PPV Customization | Hardcoded | Fully customizable |
| Show Scheduling | Manual one-off | Auto-generated recurring |
| Draft System | None | Move wrestlers between brands |
| Navigation | None | Calendar dropdown menu |

### Example Setup

**Two-Brand Split (WWE-style):**
- **Monday Night Raw** (Major, Monday)
  - WWE Championship
  - US Championship
  - Raw Tag Team Championship
  - 8 wrestlers assigned

- **Friday Night SmackDown** (Major, Friday)
  - Universal Championship
  - Intercontinental Championship
  - SmackDown Tag Team Championship
  - 7 wrestlers assigned

**Three-Brand Split (with developmental):**
- **Raw** (Major, Monday) - Main roster
- **SmackDown** (Major, Friday) - Main roster
- **NXT** (Minor, Wednesday) - Developmental

This overhaul transforms the simple time tracker into a full scheduling system with visual calendar, recurring shows, and brand management.

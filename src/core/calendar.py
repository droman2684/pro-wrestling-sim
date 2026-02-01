"""
Calendar & Schedule System
Handles weekly shows, PPVs, brands, and the game calendar.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.game_state import GameState
    from core.show import Show


class DayOfWeek(Enum):
    """Days of the week."""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class ShowTier(Enum):
    """Classification of show importance."""
    MAJOR = "major"      # Flagship weekly show (Raw, Nitro)
    MINOR = "minor"      # Secondary weekly show (Velocity, Heat)
    PPV = "ppv"          # Pay-per-view event
    SPECIAL = "special"  # Special one-off events


@dataclass
class PPVDefinition:
    """Definition of a recurring PPV event."""
    id: int
    name: str
    month: int           # 1-12
    week: int            # 1-4 (or 5)
    tier: str            # "Standard", "Big Four", "Flagship"
    brand_id: Optional[int] = None  # None = dual-brand
    is_active: bool = True

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'month': self.month,
            'week': self.week,
            'tier': self.tier,
            'brand_id': self.brand_id,
            'is_active': self.is_active
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PPVDefinition':
        return cls(
            id=data.get('id', 0),
            name=data['name'],
            month=data['month'],
            week=data['week'],
            tier=data.get('tier', 'Standard'),
            brand_id=data.get('brand_id'),
            is_active=data.get('is_active', True)
        )


# Default PPV Calendar - used if no custom PPVs defined
PPV_CALENDAR = [
    {'month': 1, 'week': 4, 'name': "New Year's Fury", 'tier': 'Standard', 'brand_id': None, 'is_dual_brand': True},
    {'month': 2, 'week': 4, 'name': 'Breaking Point', 'tier': 'Standard', 'brand_id': None, 'is_dual_brand': True},
    {'month': 3, 'week': 4, 'name': 'Championship Chaos', 'tier': 'Big Four', 'brand_id': None, 'is_dual_brand': True},
    {'month': 4, 'week': 4, 'name': 'Battlegrounds', 'tier': 'Standard', 'brand_id': None, 'is_dual_brand': True},
    {'month': 5, 'week': 4, 'name': 'Collision Course', 'tier': 'Standard', 'brand_id': None, 'is_dual_brand': True},
    {'month': 6, 'week': 4, 'name': 'Summer Scorcher', 'tier': 'Big Four', 'brand_id': None, 'is_dual_brand': True},
    {'month': 7, 'week': 4, 'name': 'Uprising', 'tier': 'Standard', 'brand_id': None, 'is_dual_brand': True},
    {'month': 8, 'week': 4, 'name': 'Fallout', 'tier': 'Standard', 'brand_id': None, 'is_dual_brand': True},
    {'month': 9, 'week': 4, 'name': 'Supremacy', 'tier': 'Big Four', 'brand_id': None, 'is_dual_brand': True},
    {'month': 10, 'week': 4, 'name': 'No Escape', 'tier': 'Standard', 'brand_id': None, 'is_dual_brand': True},
    {'month': 11, 'week': 4, 'name': 'Final Stand', 'tier': 'Standard', 'brand_id': None, 'is_dual_brand': True},
    {'month': 12, 'week': 4, 'name': 'Grand Slam', 'tier': 'Flagship', 'brand_id': None, 'is_dual_brand': True},
]


@dataclass
class ScheduledShow:
    """A specific instance of a show on the calendar."""
    id: int
    show_type: str              # "weekly", "ppv", "special"
    name: str                   # Show name
    brand_id: Optional[int]     # Brand association (None for all brands)

    # Date
    year: int
    month: int
    week: int
    day_of_week: DayOfWeek

    # Show details
    tier: ShowTier
    arena: str = ""
    is_booked: bool = False     # Has the card been set?
    is_completed: bool = False  # Has it been run?

    # For PPVs
    ppv_tier: str = ""          # "Standard", "Big Four", "Flagship"

    # Results (populated after running)
    final_rating: int = 0

    @property
    def display_date(self) -> str:
        """Human readable date string."""
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        return f"{day_names[self.day_of_week.value]}, Week {self.week}, Month {self.month}, Year {self.year}"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'show_type': self.show_type,
            'name': self.name,
            'brand_id': self.brand_id,
            'year': self.year,
            'month': self.month,
            'week': self.week,
            'day_of_week': self.day_of_week.value,
            'tier': self.tier.value,
            'arena': self.arena,
            'is_booked': self.is_booked,
            'is_completed': self.is_completed,
            'ppv_tier': self.ppv_tier,
            'final_rating': self.final_rating,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ScheduledShow':
        """Create from dictionary."""
        return cls(
            id=data['id'],
            show_type=data['show_type'],
            name=data['name'],
            brand_id=data.get('brand_id'),
            year=data['year'],
            month=data['month'],
            week=data['week'],
            day_of_week=DayOfWeek(data['day_of_week']),
            tier=ShowTier(data['tier']),
            arena=data.get('arena', ''),
            is_booked=data.get('is_booked', False),
            is_completed=data.get('is_completed', False),
            ppv_tier=data.get('ppv_tier', ''),
            final_rating=data.get('final_rating', 0),
        )


@dataclass
class CalendarDay:
    """A single day in the calendar."""
    day_of_week: DayOfWeek
    day_name: str               # "Monday", etc.
    shows: List[ScheduledShow] = field(default_factory=list)
    is_today: bool = False


@dataclass
class CalendarWeek:
    """A single week in the calendar."""
    week_number: int            # 1-4
    days: List[CalendarDay] = field(default_factory=list)
    is_current_week: bool = False


@dataclass
class CalendarMonth:
    """Data structure for rendering a month calendar view."""
    year: int
    month: int
    month_name: str             # "January", "February", etc.
    weeks: List[CalendarWeek] = field(default_factory=list)


MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


class CalendarManager:
    """Manages the schedule and calendar for the game."""

    def __init__(self):
        from core.brand import Brand
        from core.weekly_show import WeeklyShow

        self.brands: List[Brand] = []
        self.weekly_shows: List[WeeklyShow] = []
        self.scheduled_shows: List[ScheduledShow] = []
        
        # Initialize PPVs from default constant
        self.ppv_calendar: List[PPVDefinition] = []
        for idx, ppv in enumerate(PPV_CALENDAR):
            self.ppv_calendar.append(PPVDefinition(
                id=idx + 1,
                name=ppv['name'],
                month=ppv['month'],
                week=ppv['week'],
                tier=ppv['tier'],
                brand_id=ppv.get('brand_id'),
                is_active=True
            ))
            
        self._next_show_id: int = 1

    def _get_next_id(self) -> int:
        """Get next unique show ID."""
        result = self._next_show_id
        self._next_show_id += 1
        return result

    # --- PPV Management ---

    def add_ppv(self, name: str, month: int, week: int, tier: str, brand_id: Optional[int] = None) -> PPVDefinition:
        """Add a new PPV to the calendar."""
        new_id = max([p.id for p in self.ppv_calendar], default=0) + 1
        ppv = PPVDefinition(
            id=new_id,
            name=name,
            month=month,
            week=week,
            tier=tier,
            brand_id=brand_id,
            is_active=True
        )
        self.ppv_calendar.append(ppv)
        return ppv

    def edit_ppv(self, ppv_id: int, **kwargs) -> bool:
        """Edit an existing PPV."""
        ppv = next((p for p in self.ppv_calendar if p.id == ppv_id), None)
        if not ppv:
            return False
            
        for key, value in kwargs.items():
            if hasattr(ppv, key):
                setattr(ppv, key, value)
        return True

    def remove_ppv(self, ppv_id: int) -> bool:
        """Remove a PPV from the calendar."""
        ppv = next((p for p in self.ppv_calendar if p.id == ppv_id), None)
        if not ppv:
            return False
        self.ppv_calendar.remove(ppv)
        return True

    def get_ppv_calendar(self) -> List[PPVDefinition]:
        """Get all PPVs ordered by date."""
        return sorted(self.ppv_calendar, key=lambda x: (x.month, x.week))

    def get_ppvs_for_month(self, month: int) -> List[PPVDefinition]:
        """Get all PPVs for a specific month."""
        return sorted(
            [p for p in self.ppv_calendar if p.month == month and p.is_active],
            key=lambda x: x.week
        )

    def is_ppv_week(self, month: int, week: int) -> bool:
        """Check if the given month/week is a PPV event."""
        for ppv in self.ppv_calendar:
            if ppv.is_active and ppv.month == month and ppv.week == week:
                return True
        return False

    def get_ppv_for_week(self, month: int, week: int) -> Optional[PPVDefinition]:
        """Get the PPV info for a given month/week, or None if not a PPV."""
        for ppv in self.ppv_calendar:
            if ppv.is_active and ppv.month == month and ppv.week == week:
                return ppv
        return None

    def get_next_ppv(self, current_month: int, current_week: int) -> Optional[PPVDefinition]:
        """Finds the next upcoming PPV based on the current date."""
        # Check for a PPV in the current month, but later in the month
        sorted_ppvs = self.get_ppv_calendar()
        
        for ppv in sorted_ppvs:
            if not ppv.is_active:
                continue
            if ppv.month == current_month and ppv.week >= current_week:
                return ppv
            if ppv.month > current_month:
                return ppv
        
        # If no more PPVs this year, wrap around to first of next year
        for ppv in sorted_ppvs:
             if ppv.is_active:
                 return ppv
                 
        return None

    # --- Brand Management ---

    def create_brand(self, name: str, short_name: str, color: str) -> 'Brand':
        """Create a new brand."""
        from core.brand import Brand

        new_id = max([b.id for b in self.brands], default=0) + 1
        brand = Brand(
            id=new_id,
            name=name,
            short_name=short_name,
            color=color,
            assigned_titles=[],
            assigned_wrestlers=[],
            is_active=True
        )
        self.brands.append(brand)
        return brand

    def get_brand_by_id(self, brand_id: int) -> Optional['Brand']:
        """Find a brand by ID."""
        for brand in self.brands:
            if brand.id == brand_id:
                return brand
        return None

    def assign_wrestler_to_brand(self, wrestler_id: int, brand_id: int) -> bool:
        """Assign a wrestler to a brand."""
        brand = self.get_brand_by_id(brand_id)
        if not brand:
            return False

        # Remove from any other brand first
        for b in self.brands:
            if wrestler_id in b.assigned_wrestlers:
                b.assigned_wrestlers.remove(wrestler_id)

        if wrestler_id not in brand.assigned_wrestlers:
            brand.assigned_wrestlers.append(wrestler_id)
        return True

    def assign_title_to_brand(self, title_id: int, brand_id: int, exclusive: bool = True) -> bool:
        """Assign a title to a brand."""
        brand = self.get_brand_by_id(brand_id)
        if not brand:
            return False

        # Remove from any other brand first
        for b in self.brands:
            if title_id in b.assigned_titles:
                b.assigned_titles.remove(title_id)

        if title_id not in brand.assigned_titles:
            brand.assigned_titles.append(title_id)
        return True

    def unassign_wrestler_from_brand(self, wrestler_id: int) -> None:
        """Remove a wrestler from their current brand (make free agent)."""
        for brand in self.brands:
            if wrestler_id in brand.assigned_wrestlers:
                brand.assigned_wrestlers.remove(wrestler_id)

    def unassign_title_from_brand(self, title_id: int) -> None:
        """Remove a title from its current brand (make floating)."""
        for brand in self.brands:
            if title_id in brand.assigned_titles:
                brand.assigned_titles.remove(title_id)

    def get_wrestler_brand(self, wrestler_id: int) -> Optional['Brand']:
        """Get the brand a wrestler is assigned to."""
        for brand in self.brands:
            if brand.is_active and wrestler_id in brand.assigned_wrestlers:
                return brand
        return None

    def get_title_brand(self, title_id: int) -> Optional['Brand']:
        """Get the brand a title is assigned to."""
        for brand in self.brands:
            if brand.is_active and title_id in brand.assigned_titles:
                return brand
        return None

    def draft_wrestler(self, wrestler_id: int, from_brand_id: int, to_brand_id: int) -> bool:
        """Move a wrestler from one brand to another."""
        return self.assign_wrestler_to_brand(wrestler_id, to_brand_id)

    # --- Weekly Show Management ---

    def create_weekly_show(
        self,
        name: str,
        short_name: str,
        day_of_week: DayOfWeek,
        tier: ShowTier,
        brand_id: Optional[int] = None,
        match_slots: int = 5,
        segment_slots: int = 3,
        runtime_minutes: int = 120
    ) -> 'WeeklyShow':
        """Create a new recurring weekly show."""
        from core.weekly_show import WeeklyShow

        new_id = max([s.id for s in self.weekly_shows], default=0) + 1
        show = WeeklyShow(
            id=new_id,
            name=name,
            short_name=short_name,
            day_of_week=day_of_week,
            tier=tier,
            brand_id=brand_id,
            arena="Various Arenas",
            is_active=True,
            match_slots=match_slots,
            segment_slots=segment_slots,
            runtime_minutes=runtime_minutes,
            total_episodes=0,
            average_rating=0.0
        )
        self.weekly_shows.append(show)

        # Inject into existing schedule for current and future months
        # Determine current year/month from existing scheduled shows or default
        if self.scheduled_shows:
            # Find the max year currently scheduled
            max_year = max(s.year for s in self.scheduled_shows)
            # Find the min month currently scheduled for that year (to avoid back-filling too far if we want, but filling whole year is safer)
            # Actually, better to just fill for any month that already has a schedule generated.
            
            # Get set of (year, month) pairs that exist in schedule
            scheduled_months = set((s.year, s.month) for s in self.scheduled_shows)
            
            for (year, month) in scheduled_months:
                for week in range(1, 5):
                    # Check if we should add it (avoid duplicates if re-running logic, though new ID implies new show)
                    # Just add it.
                    self.scheduled_shows.append(ScheduledShow(
                        id=self._get_next_id(),
                        show_type="weekly",
                        name=show.name,
                        brand_id=show.brand_id,
                        year=year,
                        month=month,
                        week=week,
                        day_of_week=show.day_of_week,
                        tier=show.tier,
                    ))
            
            # Re-sort schedule
            self.scheduled_shows.sort(key=lambda x: (x.year, x.month, x.week, x.day_of_week.value))

        return show

    def get_weekly_show_by_id(self, show_id: int) -> Optional['WeeklyShow']:
        """Find a weekly show by ID."""
        for show in self.weekly_shows:
            if show.id == show_id:
                return show
        return None

    def update_weekly_show(self, show_id: int, **kwargs) -> bool:
        """Update weekly show settings."""
        show = self.get_weekly_show_by_id(show_id)
        if not show:
            return False

        for key, value in kwargs.items():
            if hasattr(show, key):
                setattr(show, key, value)
        return True

    def deactivate_weekly_show(self, show_id: int) -> bool:
        """Stop a weekly show from recurring."""
        show = self.get_weekly_show_by_id(show_id)
        if not show:
            return False
        show.is_active = False
        return True

    # --- Schedule Management ---

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
        ppvs = self.get_ppvs_for_month(month)
        for ppv in ppvs:
            scheduled.append(ScheduledShow(
                id=self._get_next_id(),
                show_type="ppv",
                name=ppv.name,
                brand_id=ppv.brand_id,
                year=year,
                month=month,
                week=ppv.week,
                day_of_week=DayOfWeek.SUNDAY,  # PPVs on Sunday
                tier=ShowTier.PPV,
                ppv_tier=ppv.tier,
            ))

        # Store in scheduled_shows
        self.scheduled_shows.extend(scheduled)

        return sorted(scheduled, key=lambda x: (x.week, x.day_of_week.value))

    def ensure_month_schedule(self, year: int, month: int) -> None:
        """Ensure a month's schedule exists."""
        existing = [s for s in self.scheduled_shows
                    if s.year == year and s.month == month]
        if not existing:
            self.generate_month_schedule(year, month)

    def get_week_schedule(self, year: int, month: int, week: int) -> List[ScheduledShow]:
        """Get all shows for a specific week."""
        self.ensure_month_schedule(year, month)
        return sorted(
            [s for s in self.scheduled_shows
             if s.year == year and s.month == month and s.week == week],
            key=lambda x: x.day_of_week.value
        )
        
    def get_incomplete_shows_for_week(self, year: int, month: int, week: int) -> List[ScheduledShow]:
        """Get incomplete shows for a specific week, sorted by day."""
        shows = self.get_week_schedule(year, month, week)
        return [s for s in shows if not s.is_completed]

    def all_shows_completed_for_week(self, year: int, month: int, week: int) -> bool:
        """Check if all shows for the week have been completed."""
        return len(self.get_incomplete_shows_for_week(year, month, week)) == 0

    def get_upcoming_shows(self, current_year: int, current_month: int, current_week: int, count: int = 10) -> List[ScheduledShow]:
        """Get the next N upcoming shows."""
        # Ensure current and next month schedules exist
        self.ensure_month_schedule(current_year, current_month)
        next_month = current_month + 1 if current_month < 12 else 1
        next_year = current_year if current_month < 12 else current_year + 1
        self.ensure_month_schedule(next_year, next_month)

        current = (current_year, current_month, current_week)
        future = [s for s in self.scheduled_shows
                  if (s.year, s.month, s.week) >= current and not s.is_completed]
        return sorted(future, key=lambda x: (x.year, x.month, x.week, x.day_of_week.value))[:count]

    def get_scheduled_show_by_id(self, show_id: int) -> Optional[ScheduledShow]:
        """Find a scheduled show by ID."""
        for show in self.scheduled_shows:
            if show.id == show_id:
                return show
        return None

    def mark_show_booked(self, show_id: int) -> bool:
        """Mark a scheduled show as booked."""
        show = self.get_scheduled_show_by_id(show_id)
        if show:
            show.is_booked = True
            return True
        return False

    def mark_show_completed(self, show_id: int, rating: int = 0) -> bool:
        """Mark a scheduled show as completed."""
        show = self.get_scheduled_show_by_id(show_id)
        if show:
            show.is_completed = True
            show.final_rating = rating
            return True
        return False

    # --- Calendar View Generation ---

    def generate_calendar_view(self, year: int, month: int, current_year: int, current_month: int, current_week: int) -> CalendarMonth:
        """Generate calendar view data for a specific month."""
        self.ensure_month_schedule(year, month)

        weeks = []
        for week_num in range(1, 5):
            days = []
            for day in DayOfWeek:
                shows = [s for s in self.scheduled_shows
                         if s.year == year and s.month == month
                         and s.week == week_num and s.day_of_week == day]
                days.append(CalendarDay(
                    day_of_week=day,
                    day_name=day.name.capitalize(),
                    shows=shows,
                    is_today=(
                        current_year == year and
                        current_month == month and
                        current_week == week_num
                    )
                ))

            weeks.append(CalendarWeek(
                week_number=week_num,
                days=days,
                is_current_week=(
                    current_year == year and
                    current_month == month and
                    current_week == week_num
                )
            ))

        return CalendarMonth(
            year=year,
            month=month,
            month_name=MONTH_NAMES[month - 1],
            weeks=weeks
        )

    # --- Serialization ---

    def to_dict(self) -> dict:
        """Convert to dictionary for saving."""
        return {
            'brands': [b.to_dict() for b in self.brands],
            'weekly_shows': [s.to_dict() for s in self.weekly_shows],
            'scheduled_shows': [s.to_dict() for s in self.scheduled_shows],
            'ppv_calendar': [p.to_dict() for p in self.ppv_calendar],
            '_next_show_id': self._next_show_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CalendarManager':
        """Create from dictionary."""
        from core.brand import Brand
        from core.weekly_show import WeeklyShow

        manager = cls()
        manager.brands = [Brand.from_dict(b) for b in data.get('brands', [])]
        manager.weekly_shows = [WeeklyShow.from_dict(s) for s in data.get('weekly_shows', [])]
        manager.scheduled_shows = [ScheduledShow.from_dict(s) for s in data.get('scheduled_shows', [])]
        
        # Load PPV calendar
        ppv_data = data.get('ppv_calendar', [])
        if ppv_data and isinstance(ppv_data[0], dict) and 'tier' in ppv_data[0]:
            # New format
            manager.ppv_calendar = [PPVDefinition.from_dict(p) for p in ppv_data]
        else:
            # Legacy format (or default fallback)
            # If empty or old format, re-initialize default
            manager.ppv_calendar = []
            legacy_data = ppv_data if ppv_data else PPV_CALENDAR
            for idx, ppv in enumerate(legacy_data):
                manager.ppv_calendar.append(PPVDefinition(
                    id=idx + 1,
                    name=ppv.get('name', 'Unknown PPV'),
                    month=ppv.get('month', 1),
                    week=ppv.get('week', 4),
                    tier=ppv.get('tier', 'Standard'),
                    brand_id=ppv.get('brand_id'),
                    is_active=True
                ))

        manager._next_show_id = data.get('_next_show_id', 1)
        return manager

# --- Legacy compatibility functions ---

def get_next_ppv(current_month: int, current_week: int) -> Optional[Dict]:
    """
    Finds the next upcoming PPV based on the current date.
    Legacy function for compatibility.
    """
    # Check for a PPV in the current month, but later in the month
    for ppv in PPV_CALENDAR:
        if ppv['month'] == current_month and ppv['week'] >= current_week:
            return ppv

    # Check for PPVs in the following months
    for month in range(current_month + 1, 13):
        for ppv in PPV_CALENDAR:
            if ppv['month'] == month:
                return ppv

    # If in December and no more PPVs, wrap around to next year
    if current_month == 12:
        return PPV_CALENDAR[0]

    return None


def is_ppv_week(month: int, week: int) -> bool:
    """Check if the given month/week is a PPV event."""
    for ppv in PPV_CALENDAR:
        if ppv['month'] == month and ppv['week'] == week:
            return True
    return False


def get_ppv_for_week(month: int, week: int) -> Optional[Dict]:
    """Get the PPV info for a given month/week, or None if not a PPV."""
    for ppv in PPV_CALENDAR:
        if ppv['month'] == month and ppv['week'] == week:
            return ppv
    return None

from typing import List, Optional, Tuple
import random
from core.game_state import GameState, ShowResult
from core.wrestler import Wrestler, load_roster, save_roster
from core.tag_team import TagTeam, load_tag_teams, save_tag_teams
from core.title import Title, load_titles, save_titles
from core.feud import Feud, load_feuds, save_feuds
from core.stable import Stable, load_stables, save_stables
from core.economy import Company
from core.records import RecordsManager, WrestlerRecords, TitleReign
from core.show import Show
from core import calculate_wrestler_rankings, calculate_tag_team_rankings # Import ranking functions
from core.calendar import (
    CalendarManager, DayOfWeek, ShowTier, ScheduledShow, CalendarMonth
)
from core.brand import Brand
from core.weekly_show import WeeklyShow
from core.auto_booker import AutoBooker, CardSuggestion, MatchSuggestion, FeudSuggestion
from core.news_feed import NewsFeedManager, generate_show_news, generate_weekly_news
from services import file_service


class GameService:
    """
    Main service layer for all game operations.
    This is the API that both CLI and future GUI will use.
    """

    def __init__(self):
        self._state: Optional[GameState] = None
        self._current_show: Optional[Show] = None
        self._current_scheduled_show_id: Optional[int] = None

    @property
    def state(self) -> Optional[GameState]:
        return self._state

    @property
    def is_game_loaded(self) -> bool:
        return self._state is not None and self._state.is_loaded

    # --- Database & Save Management ---

    def list_databases(self) -> List[str]:
        """Get list of available database templates."""
        return file_service.list_databases()

    def list_saves(self) -> List[str]:
        """Get list of existing save games."""
        return file_service.list_saves()

    def create_new_game(self, db_name: str, save_name: str) -> Tuple[bool, str]:
        """
        Create a new game from a database template.
        Returns (success, message).
        """
        success, message = file_service.create_new_save(db_name, save_name)
        if success:
            # Automatically load the new game
            return self.load_game(save_name)
        return success, message

    def load_game(self, save_name: str) -> Tuple[bool, str]:
        """
        Load an existing save game.
        Returns (success, message).
        """
        if not file_service.save_exists(save_name):
            return False, f"Save '{save_name}' not found."

        roster_path = file_service.get_roster_path(save_name)
        roster = load_roster(str(roster_path))

        if not roster:
            return False, f"Could not load roster from '{save_name}'."

        # Load tag teams (optional)
        tag_teams_path = file_service.get_tag_teams_path(save_name)
        tag_teams = load_tag_teams(str(tag_teams_path))
        
        # Load titles (optional)
        titles_path = file_service.get_titles_path(save_name)
        titles = load_titles(str(titles_path))

        # Load feuds (optional)
        feuds_path = file_service.get_feuds_path(save_name)
        feuds = load_feuds(str(feuds_path))

        # Load stables (optional)
        stables_path = file_service.get_stables_path(save_name)
        stables = load_stables(str(stables_path))

        # Load game state data (calendar)
        game_state_data = file_service.load_game_state_data(save_name)
        
        # Load company data
        company_data = file_service.load_company_data(save_name)

        # Load records data
        records_data = file_service.load_records_data(save_name)
        records = RecordsManager.from_dict(records_data)

        # Load calendar data
        calendar_data = file_service.load_calendar_data(save_name)
        calendar_manager = CalendarManager.from_dict(calendar_data)

        # Load news data
        news_data = file_service.load_news_data(save_name)
        news_feed = NewsFeedManager.from_dict(news_data)
        
        # Initialize if empty (migration for existing saves)
        if not news_feed.feed_entries:
            current_date = f"Year {game_state_data.get('year', 1)}, Month {game_state_data.get('month', 1)}, Week {game_state_data.get('week', 1)}"
            news_feed.create_entry(
                date=current_date,
                category="system_update",
                headline="New Feature: Breaking News Feed",
                body="Welcome to the new dashboard! The PWInsider Elite news wire is now live. Expect updates on title changes, injuries, backstage morale, and match results as you play.",
                importance="major"
            )
            # Save immediately so it persists
            file_service.save_news_data(save_name, news_feed.to_dict())

        self._state = GameState(
            save_name=save_name,
            save_path=str(file_service.get_save_path(save_name)),
            roster=roster,
            tag_teams=tag_teams,
            titles=titles,
            feuds=feuds,
            stables=stables,
            company=Company(**company_data),
            records=records,
            calendar_manager=calendar_manager,
            news_feed=news_feed,
            year=game_state_data.get('year', 1),
            month=game_state_data.get('month', 1),
            week=game_state_data.get('week', 1)
        )

        return True, f"Loaded '{save_name}' with {len(roster)} wrestlers and {len(tag_teams)} tag teams."

    def save_game(self) -> Tuple[bool, str]:
        """Save current game state to disk."""
        if not self.is_game_loaded:
            return False, "No game loaded."

        # Save roster
        roster_path = file_service.get_roster_path(self._state.save_name)
        save_roster(self._state.roster, str(roster_path))

        # Save tag teams
        tag_teams_path = file_service.get_tag_teams_path(self._state.save_name)
        save_tag_teams(self._state.tag_teams, str(tag_teams_path))
        
        # Save titles
        titles_path = file_service.get_titles_path(self._state.save_name)
        save_titles(self._state.titles, str(titles_path))

        # Save feuds
        feuds_path = file_service.get_feuds_path(self._state.save_name)
        save_feuds(self._state.feuds, str(feuds_path))

        # Save stables
        stables_path = file_service.get_stables_path(self._state.save_name)
        save_stables(self._state.stables, str(stables_path))

        # Save game state data (calendar)
        game_state_data = {
            'year': self._state.year,
            'month': self._state.month,
            'week': self._state.week
        }
        file_service.save_game_state_data(self._state.save_name, game_state_data)
        
        # Save company data
        company_data = self._state.company.to_dict()
        file_service.save_company_data(self._state.save_name, company_data)

        # Save records data
        records_data = self._state.records.to_dict()
        file_service.save_records_data(self._state.save_name, records_data)

        # Save calendar data
        calendar_data = self._state.calendar_manager.to_dict()
        file_service.save_calendar_data(self._state.save_name, calendar_data)

        # Save news data
        news_data = self._state.news_feed.to_dict()
        file_service.save_news_data(self._state.save_name, news_data)

        return True, f"Saved to '{self._state.save_name}'."

    # --- Roster Operations ---

    def get_roster(self) -> List[Wrestler]:
        """Get the current roster, sorted by overall rating."""
        if not self.is_game_loaded:
            return []
        return sorted(self._state.roster, key=lambda w: w.get_overall_rating(), reverse=True)

    def get_wrestler_by_id(self, wrestler_id: int) -> Optional[Wrestler]:
        """Find a wrestler by ID."""
        if not self.is_game_loaded:
            return None
        return self._state.get_wrestler_by_id(wrestler_id)

    def get_wrestler_by_index(self, index: int) -> Optional[Wrestler]:
        """Get wrestler by roster index (0-based)."""
        if not self.is_game_loaded:
            return None
        roster = self._state.roster
        if 0 <= index < len(roster):
            return roster[index]
        return None

    def get_wrestler_rankings(self) -> List[Wrestler]:
        """Get the ranked list of wrestlers."""
        if not self.is_game_loaded:
            return []
        return calculate_wrestler_rankings(self._state.roster)

    def get_title_rankings(self) -> List[Tuple[Title, List[Wrestler]]]:
        """
        Get rankings for each title.
        Returns a list of tuples: [(Title, [Wrestlers])]
        """
        if not self.is_game_loaded:
            return []
        
        rankings = []
        all_wrestlers = self._state.roster
        
        for title in self._state.titles:
            # Determine eligible wrestlers for this title
            eligible_wrestlers = []
            
            # Check brand exclusivity
            title_brand = self.get_title_brand(title.id)
            
            for w in all_wrestlers:
                # Skip current holder
                if w.id == title.current_holder_id:
                    continue
                    
                # Skip if injured (optional, but realistic)
                if w.is_injured:
                    continue
                
                # Check brand alignment
                if title_brand:
                    wrestler_brand = self.get_wrestler_brand(w.id)
                    if wrestler_brand != title_brand:
                        continue
                
                eligible_wrestlers.append(w)
            
            # Calculate rankings for eligible pool
            # Using standard criteria: Win % -> Wins -> Overall Rating
            ranked_list = calculate_wrestler_rankings(eligible_wrestlers)
            
            # Store top 10
            rankings.append((title, ranked_list[:10]))
            
        return rankings

    # --- Show & Simulation Operations ---

    def create_show(self, show_name: str, is_ppv: bool = None, scheduled_show_id: int = None) -> bool:
        """Start booking a new show. Auto-detects PPV if not specified.

        Args:
            show_name: Name of the show
            is_ppv: Whether this is a PPV (auto-detected if not specified)
            scheduled_show_id: Optional ID of the scheduled show from the calendar
        """
        if not self.is_game_loaded:
            return False

        # If linked to a scheduled show, use its properties
        if scheduled_show_id is not None:
            scheduled = self.get_scheduled_show_by_id(scheduled_show_id)
            if scheduled:
                show_name = show_name or scheduled.name
                is_ppv = scheduled.show_type == "ppv"
                self._state.calendar_manager.mark_show_booked(scheduled_show_id)
                self._current_scheduled_show_id = scheduled_show_id

        # Auto-detect PPV if not specified
        if is_ppv is None:
            is_ppv = self._state.calendar_manager.is_ppv_week(self._state.month, self._state.week)

        self._current_show = Show(show_name, is_ppv=is_ppv)
        return True

    def get_current_show(self) -> Optional[Show]:
        """Get the show currently being booked."""
        return self._current_show

    def add_match_to_show(self, wrestler_a: Wrestler, wrestler_b: Wrestler, is_steel_cage: bool = False, is_title_match: bool = False, title_id: Optional[int] = None) -> bool:
        """Add a match to the current show being booked."""
        if self._current_show is None:
            return False
        if wrestler_a == wrestler_b:
            return False
        self._current_show.add_match(wrestler_a, wrestler_b, is_steel_cage=is_steel_cage, is_title_match=is_title_match, title_id=title_id, game_state=self._state)
        return True

    def get_remaining_shows_this_week(self) -> List[ScheduledShow]:
        """Get list of uncompleted scheduled shows for the current week."""
        if not self.is_game_loaded:
            return []
        return self._state.calendar_manager.get_incomplete_shows_for_week(
            self._state.year, self._state.month, self._state.week
        )

    def advance_week_if_complete(self) -> bool:
        """
        Check if all shows for the week are done, and if so, advance the week.
        Returns True if week was advanced.
        """
        if not self.is_game_loaded:
            return False
            
        if self._state.calendar_manager.all_shows_completed_for_week(
            self._state.year, self._state.month, self._state.week
        ):
            # Capture pre-advance state for news generation
            pre_advance_injured = {w.id for w in self._state.roster if w.is_injured}

            self._state.advance_week()

            # Generate weekly news (e.g. injury returns)
            generate_weekly_news(self._state, self._state.news_feed, pre_advance_injured)
            return True
        return False

    def play_show(self) -> Optional[ShowResult]:
        """
        Run the current show simulation.
        Returns ShowResult with all match data.
        Automatically saves game state and conditionally advances the week.
        """
        if self._current_show is None or not self.is_game_loaded:
            return None

        if self._current_show.match_count == 0:
            return None

        # Capture pre-show state for news generation
        pre_show_snapshot = {
            "feud_intensities": {f.id: f.intensity for f in self._state.feuds},
            "injured_ids": {w.id for w in self._state.roster if w.is_injured},
            "viewers": self._state.company.viewers
        }

        # Run the show (updates wrestler stats and titles internally)
        result = self._current_show.run(self._state)

        # Generate news for the show
        generate_show_news(result, self._state, self._state.news_feed, pre_show_snapshot)

        # Mark scheduled show as completed if linked
        if self._current_scheduled_show_id is not None:
            self._state.calendar_manager.mark_show_completed(
                self._current_scheduled_show_id,
                rating=result.final_rating
            )
            self._current_scheduled_show_id = None

        # Conditionally advance the week
        self.advance_week_if_complete()

        # Auto-save
        self.save_game()

        # Clear current show
        self._current_show = None

        return result

    def cancel_show(self) -> None:
        """Cancel the current show being booked."""
        # Unmark scheduled show if linked
        if self._current_scheduled_show_id is not None:
            scheduled = self.get_scheduled_show_by_id(self._current_scheduled_show_id)
            if scheduled:
                scheduled.is_booked = False
            self._current_scheduled_show_id = None

        self._current_show = None
    
    def _auto_book_show(self, show_name: str, num_matches: int = 5):
        """Creates and auto-books a show with random matches."""
        self.create_show(show_name)
        available_wrestlers = list(self._state.roster)
        
        for _ in range(num_matches):
            if len(available_wrestlers) < 2:
                break
            w1 = random.choice(available_wrestlers)
            available_wrestlers.remove(w1)
            w2 = random.choice(available_wrestlers)
            available_wrestlers.remove(w2)
            self.add_match_to_show(w1, w2)
            
    def simulate_week(self) -> Optional[ShowResult]:
        """Simulates a single week, auto-booking and playing all scheduled shows."""
        if not self.is_game_loaded:
            return None
        
        # Get all shows for this week
        scheduled_shows = self.get_week_schedule()
        
        # If no shows scheduled, force one generic show (legacy behavior/fallback)
        if not scheduled_shows:
            show_name = f"Weekly Show - {self.get_current_date_string()}"
            self._auto_book_show(show_name)
            return self.play_show()

        last_result = None
        
        # Process each scheduled show that isn't completed
        for scheduled in scheduled_shows:
            if scheduled.is_completed:
                continue
                
            # Create show linked to schedule
            self.create_show(scheduled.name, scheduled_show_id=scheduled.id)
            
            # Auto-book matches
            # TODO: Improve auto-booking to use brand roster if applicable
            self._auto_book_show(scheduled.name) # This currently resets create_show context, need to fix
            
            # Since _auto_book_show calls create_show internally which overwrites our linked show,
            # we need to be careful. _auto_book_show implementation above calls create_show(show_name).
            # Let's refactor the loop to be safer.
            pass

        # Correct implementation of the loop:
        results = []
        
        # We need to re-fetch incomplete shows because play_show() might advance week if we are at the end,
        # but here we want to run them all. Wait, play_show advances week only if all complete.
        # So we can just iterate.
        
        incomplete_shows = self.get_remaining_shows_this_week()
        
        if not incomplete_shows:
            # If all done (or none exist), maybe just advance? 
            # Or if strictly no shows scheduled, run a generic one.
            if not scheduled_shows:
                 show_name = f"Weekly Show - {self.get_current_date_string()}"
                 self._auto_book_show(show_name)
                 return self.play_show()
            
            # If shows existed but all done, ensure we advanced
            self.advance_week_if_complete()
            return None

        for scheduled in incomplete_shows:
            # Setup the show
            self.create_show(scheduled.name, scheduled_show_id=scheduled.id)
            
            # Auto-book matches
            # We can't use _auto_book_show as-is because it calls create_show again.
            # Let's inline the booking logic or modify _auto_book_show. 
            # For now, inline simple booking.
            
            available_wrestlers = list(self._state.roster)
            # Filter by brand if show is branded
            if scheduled.brand_id:
                brand = self.get_brand_by_id(scheduled.brand_id)
                if brand:
                    brand_roster_ids = brand.assigned_wrestlers
                    available_wrestlers = [w for w in available_wrestlers if w.id in brand_roster_ids]

            num_matches = 5
            for _ in range(num_matches):
                if len(available_wrestlers) < 2:
                    break
                w1 = random.choice(available_wrestlers)
                available_wrestlers.remove(w1)
                w2 = random.choice(available_wrestlers)
                available_wrestlers.remove(w2)
                self.add_match_to_show(w1, w2)
            
            # Play the show
            last_result = self.play_show()
            if last_result:
                results.append(last_result)
                
        return last_result # Return the last result as representative, or change return type

    def sim_to_next_ppv(self) -> List[ShowResult]:
        """Simulates all weeks until the next PPV."""
        if not self.is_game_loaded:
            return []
        
        next_ppv = self._state.calendar_manager.get_next_ppv(self._state.month, self._state.week)
        if not next_ppv:
            return []

        results = []
        while not (self._state.month == next_ppv.month and self._state.week == next_ppv.week):
            result = self.simulate_week()
            if result:
                results.append(result)
        
        return results

    # --- Game Info ---

    def get_save_name(self) -> str:
        """Get the current save name."""
        if not self.is_game_loaded:
            return ""
        return self._state.save_name

    def get_current_date_string(self) -> str:
        """Get the current game date as a formatted string."""
        if not self.is_game_loaded:
            return ""
        return self._state.date_string
        
    def get_next_ppv_string(self) -> str:
        """Get the next upcoming PPV as a formatted string."""
        if not self.is_game_loaded:
            return ""
        ppv = self._state.calendar_manager.get_next_ppv(self._state.month, self._state.week)
        if ppv:
            return f"Next PPV: {ppv.name} (Month {ppv.month}, Week {ppv.week})"
        return "No upcoming PPVs."

    def get_ppv_schedule(self) -> List[dict]:
        """Get the full PPV schedule."""
        return self.get_ppv_calendar()

    def get_news(self, limit: int = 20) -> List[dict]:
        """Get recent news entries."""
        if not self.is_game_loaded:
            return []
        entries = self._state.news_feed.get_recent(limit)
        return [e.to_dict() for e in entries]

    # --- Company Info ---
    
    def get_company(self) -> Optional[Company]:
        """Get the company object."""
        if not self.is_game_loaded:
            return None
        return self._state.company

    # --- Roster Management ---

    def create_wrestler(
        self,
        name: str,
        nickname: str = None,
        age: int = 25,
        height: int = 72,
        weight: int = 220,
        region: str = "Unknown",
        # Physical stats
        strength: int = 50,
        speed: int = 50,
        agility: int = 50,
        durability: int = 50,
        recovery: int = 50,
        # Offense stats
        striking: int = 50,
        grappling: int = 50,
        submission: int = 50,
        high_flying: int = 50,
        hardcore: int = 50,
        power_moves: int = 50,
        technical: int = 50,
        dirty_tactics: int = 50,
        # Defense stats
        strike_defense: int = 50,
        grapple_defense: int = 50,
        aerial_defense: int = 50,
        ring_awareness: int = 50,
        # Entertainment stats
        mic_skills: int = 50,
        charisma: int = 50,
        look: int = 50,
        star_power: int = 50,
        entrance: int = 50,
        # Intangibles
        psychology: int = 50,
        consistency: int = 75,
        big_match: int = 50,
        clutch: int = 50,
        # Style and moves
        primary_style: str = "all_rounder",
        secondary_style: str = None,
        finisher_name: str = "",
        finisher_type: str = "power",
        alignment: str = "Face"
    ) -> Tuple[bool, str]:
        """
        Create a new wrestler with the new 27-attribute system.
        Returns (success, message).
        """
        if not self.is_game_loaded:
            return False, "No game loaded."

        if not name or not name.strip():
            return False, "Wrestler name is required."

        # Helper to clamp values
        def clamp(val: int) -> int:
            return max(1, min(100, val))

        # Generate new ID
        new_id = max([w.id for w in self._state.roster], default=0) + 1

        # Build finisher if provided
        finishers = []
        if finisher_name and finisher_name.strip():
            finishers.append({
                "name": finisher_name.strip(),
                "type": finisher_type,
                "damage": 85
            })

        # Build wrestler data dict with new format
        wrestler_data = {
            "id": new_id,
            "name": name.strip(),
            "nickname": nickname.strip() if nickname else None,
            "billing_name": None,

            "bio": {
                "age": age,
                "height": height,
                "weight": weight,
                "home_region": region,
                "years_active": 1
            },

            "physical": {
                "strength": clamp(strength),
                "speed": clamp(speed),
                "agility": clamp(agility),
                "durability": clamp(durability),
                "stamina": 100,  # Start fresh
                "recovery": clamp(recovery)
            },

            "offense": {
                "striking": clamp(striking),
                "grappling": clamp(grappling),
                "submission": clamp(submission),
                "high_flying": clamp(high_flying),
                "hardcore": clamp(hardcore),
                "power_moves": clamp(power_moves),
                "technical": clamp(technical),
                "dirty_tactics": clamp(dirty_tactics)
            },

            "defense": {
                "strike_defense": clamp(strike_defense),
                "grapple_defense": clamp(grapple_defense),
                "aerial_defense": clamp(aerial_defense),
                "ring_awareness": clamp(ring_awareness)
            },

            "entertainment": {
                "mic_skills": clamp(mic_skills),
                "charisma": clamp(charisma),
                "look": clamp(look),
                "star_power": clamp(star_power),
                "entrance": clamp(entrance)
            },

            "intangibles": {
                "psychology": clamp(psychology),
                "consistency": clamp(consistency),
                "big_match": clamp(big_match),
                "clutch": clamp(clutch)
            },

            "styles": {
                "primary": primary_style,
                "secondary": secondary_style
            },

            "moves": {
                "finishers": finishers,
                "signatures": []
            },

            "status": {
                "morale": 75,
                "condition": 100,
                "alignment": alignment,
                "heat": 50,
                "wins": 0,
                "losses": 0,
                "has_mitb_briefcase": False,
                "is_injured": False,
                "injury_weeks_remaining": 0
            },

            "contract": {
                "per_appearance_fee": 1000
            }
        }

        # Create wrestler and add to roster
        from core.wrestler import Wrestler
        new_wrestler = Wrestler(wrestler_data)
        self._state.roster.append(new_wrestler)
        self.save_game()

        return True, f"Created wrestler: {new_wrestler.display_name} [{new_wrestler.get_overall_rating()}]"

    # --- Title Operations ---

    def get_titles(self) -> List[Title]:
        """Get all titles."""
        if not self.is_game_loaded:
            return []
        return self._state.titles

    def create_title(self, name: str, prestige: int = 50) -> Tuple[bool, str]:
        """
        Create a new championship title.
        Returns (success, message).
        """
        if not self.is_game_loaded:
            return False, "No game loaded."

        if not name or not name.strip():
            return False, "Title name is required."

        # Check for duplicate names
        existing_names = [t.name.lower() for t in self._state.titles]
        if name.strip().lower() in existing_names:
            return False, f"A title named '{name}' already exists."

        # Generate new ID
        new_id = max([t.id for t in self._state.titles], default=0) + 1

        # Create new title (starts vacant)
        new_title = Title(
            id=new_id,
            name=name.strip(),
            prestige=max(1, min(100, prestige)),
            current_holder_id=None
        )

        self._state.titles.append(new_title)
        self.save_game()

        return True, f"Created championship: {new_title.name} [Prestige: {new_title.prestige}]"

    def get_title_by_id(self, title_id: int) -> Optional[Title]:
        """Find a title by ID."""
        if not self.is_game_loaded:
            return None
        return next((t for t in self._state.titles if t.id == title_id), None)

    # --- Tag Team Operations ---

    def get_tag_teams(self) -> List[TagTeam]:
        """Get all tag teams."""
        if not self.is_game_loaded:
            return []
        return self._state.tag_teams

    def get_available_tag_teams(self, brand_id: Optional[int] = None) -> List[TagTeam]:
        """Get tag teams that are available (active and members in condition).

        If brand_id is provided, only returns teams where both members are on that brand.
        """
        if not self.is_game_loaded:
            return []

        teams = [team for team in self._state.tag_teams
                 if team.is_available(self._state.roster)]

        if brand_id is not None:
            teams = self.get_brand_tag_teams(brand_id, teams)

        return teams

    def get_brand_tag_teams(self, brand_id: int, teams: List[TagTeam] = None) -> List[TagTeam]:
        """Get tag teams where both members are assigned to the brand."""
        if not self.is_game_loaded:
            return []

        brand = self.get_brand_by_id(brand_id)
        if not brand:
            return []

        brand_wrestler_ids = set(brand.assigned_wrestlers)

        if teams is None:
            teams = self._state.tag_teams

        return [
            team for team in teams
            if team.is_active
            and all(mid in brand_wrestler_ids for mid in team.member_ids)
        ]

    def get_tag_team_by_id(self, team_id: int) -> Optional[TagTeam]:
        """Find a tag team by ID."""
        if not self.is_game_loaded:
            return None
        return self._state.get_tag_team_by_id(team_id)

    def create_tag_team(self, name: str, member_a_id: int, member_b_id: int) -> Tuple[bool, str]:
        """
        Create a new tag team with two wrestlers.
        Returns (success, message).
        """
        if not self.is_game_loaded:
            return False, "No game loaded."

        # Validate wrestlers exist
        member_a = self._state.get_wrestler_by_id(member_a_id)
        member_b = self._state.get_wrestler_by_id(member_b_id)

        if not member_a:
            return False, f"Wrestler with ID {member_a_id} not found."
        if not member_b:
            return False, f"Wrestler with ID {member_b_id} not found."

        if member_a_id == member_b_id:
            return False, "A wrestler cannot team with themselves."

        # Check if either wrestler is already on a team
        if self._state.is_wrestler_on_team(member_a_id):
            return False, f"{member_a.name} is already on a tag team."
        if self._state.is_wrestler_on_team(member_b_id):
            return False, f"{member_b.name} is already on a tag team."

        # Generate new ID
        new_id = max([t.id for t in self._state.tag_teams], default=0) + 1

        # Create the team
        new_team = TagTeam(
            id=new_id,
            name=name,
            member_ids=[member_a_id, member_b_id],
            chemistry=50,
            wins=0,
            losses=0,
            is_active=True
        )

        self._state.tag_teams.append(new_team)
        self.save_game()

        return True, f"Created tag team '{name}' with {member_a.name} and {member_b.name}."

    def disband_tag_team(self, team_id: int) -> Tuple[bool, str]:
        """
        Disband a tag team by marking it inactive.
        Returns (success, message).
        """
        if not self.is_game_loaded:
            return False, "No game loaded."

        team = self._state.get_tag_team_by_id(team_id)
        if not team:
            return False, f"Tag team with ID {team_id} not found."

        if not team.is_active:
            return False, f"'{team.name}' is already disbanded."

        team.is_active = False
        self.save_game()

        return True, f"'{team.name}' has been disbanded."

    def get_tag_team_rankings(self) -> List[TagTeam]:
        """Get the ranked list of tag teams."""
        if not self.is_game_loaded:
            return []
        return calculate_tag_team_rankings(self._state.tag_teams, self._state.roster)

    def add_tag_match_to_show(self, team_a: TagTeam, team_b: TagTeam, is_steel_cage: bool = False, is_title_match: bool = False, title_id: Optional[int] = None) -> bool:
        """Add a tag team match to the current show being booked."""
        if self._current_show is None:
            return False
        if team_a == team_b:
            return False
        self._current_show.add_tag_match(team_a, team_b, self._state.roster, is_steel_cage=is_steel_cage, is_title_match=is_title_match, title_id=title_id, game_state=self._state)
        return True

    def is_wrestler_booked_on_show(self, wrestler_id: int) -> bool:
        """Check if a wrestler is already booked on the current show."""
        if self._current_show is None:
            return False
        return self._current_show.is_wrestler_booked(wrestler_id)

    def add_rumble_to_show(self, wrestlers: List[Wrestler]) -> Tuple[bool, str]:
        """
        Add a Royal Rumble match to the current show.
        Requires exactly 10 wrestlers.
        Returns (success, message).
        """
        if self._current_show is None:
            return False, "No show is currently being booked."

        if len(wrestlers) != 10:
            return False, "Royal Rumble requires exactly 10 wrestlers."

        # Check for duplicates
        wrestler_ids = [w.id for w in wrestlers]
        if len(wrestler_ids) != len(set(wrestler_ids)):
            return False, "Duplicate wrestlers in Royal Rumble."

        # Check if any wrestler is already booked
        for w in wrestlers:
            if self._current_show.is_wrestler_booked(w.id):
                return False, f"{w.name} is already booked on this show."

        self._current_show.add_rumble_match(wrestlers, self._state)
        return True, "Royal Rumble match added to the card!"

    def add_multi_man_match_to_show(self, wrestlers: List[Wrestler], is_title_match: bool = False, title_id: Optional[int] = None) -> Tuple[bool, str]:
        """
        Add a Triple Threat (3) or Fatal 4-Way (4) match to the current show.
        Returns (success, message).
        """
        if self._current_show is None:
            return False, "No show is currently being booked."

        if len(wrestlers) < 3 or len(wrestlers) > 4:
            return False, "Multi-man match requires 3-4 wrestlers."

        # Check for duplicates
        wrestler_ids = [w.id for w in wrestlers]
        if len(wrestler_ids) != len(set(wrestler_ids)):
            return False, "Duplicate wrestlers in match."

        # Check if any wrestler is already booked
        for w in wrestlers:
            if self._current_show.is_wrestler_booked(w.id):
                return False, f"{w.name} is already booked on this show."

        self._current_show.add_multi_man_match(wrestlers, self._state, is_title_match=is_title_match, title_id=title_id)
        match_type = "Triple Threat" if len(wrestlers) == 3 else "Fatal 4-Way"
        return True, f"{match_type} match added to the card!"

    def add_ladder_match_to_show(self, wrestlers: List[Wrestler], is_title_match: bool = False, title_id: Optional[int] = None) -> Tuple[bool, str]:
        """
        Add a Ladder match to the current show.
        Returns (success, message).
        """
        if self._current_show is None:
            return False, "No show is currently being booked."

        if len(wrestlers) < 2:
            return False, "Ladder match requires at least 2 wrestlers."

        # Check for duplicates
        wrestler_ids = [w.id for w in wrestlers]
        if len(wrestler_ids) != len(set(wrestler_ids)):
            return False, "Duplicate wrestlers in match."

        # Check if any wrestler is already booked
        for w in wrestlers:
            if self._current_show.is_wrestler_booked(w.id):
                return False, f"{w.name} is already booked on this show."

        self._current_show.add_ladder_match(wrestlers, self._state, is_title_match=is_title_match, title_id=title_id)

        if len(wrestlers) == 2:
            match_type = "Ladder Match"
        elif len(wrestlers) <= 4:
            match_type = f"{len(wrestlers)}-Way Ladder Match"
        else:
            match_type = "Money in the Bank Ladder Match"

        return True, f"{match_type} added to the card!"

    def add_iron_man_match_to_show(self, wrestler_a: Wrestler, wrestler_b: Wrestler,
                                    time_limit: int = 30, is_title_match: bool = False,
                                    title_id: Optional[int] = None) -> Tuple[bool, str]:
        """
        Add an Iron Man match to the current show.
        Returns (success, message).
        """
        if self._current_show is None:
            return False, "No show is currently being booked."

        if wrestler_a == wrestler_b:
            return False, "Cannot book a wrestler against themselves."

        # Check if wrestlers are already booked
        if self._current_show.is_wrestler_booked(wrestler_a.id):
            return False, f"{wrestler_a.name} is already booked on this show."
        if self._current_show.is_wrestler_booked(wrestler_b.id):
            return False, f"{wrestler_b.name} is already booked on this show."

        self._current_show.add_iron_man_match(wrestler_a, wrestler_b, time_limit, self._state,
                                               is_title_match=is_title_match, title_id=title_id)
        return True, f"{time_limit}-Minute Iron Man Match added to the card!"

    def add_chamber_match_to_show(self, wrestlers: List[Wrestler],
                                   is_title_match: bool = False,
                                   title_id: Optional[int] = None) -> Tuple[bool, str]:
        """
        Add an Elimination Chamber match to the current show.
        Requires exactly 6 wrestlers.
        Returns (success, message).
        """
        if self._current_show is None:
            return False, "No show is currently being booked."

        if len(wrestlers) != 6:
            return False, "Elimination Chamber requires exactly 6 wrestlers."

        # Check for duplicates
        if len(set(w.id for w in wrestlers)) != 6:
            return False, "Cannot have duplicate wrestlers in the match."

        # Check if any wrestler is already booked
        for w in wrestlers:
            if self._current_show.is_wrestler_booked(w.id):
                return False, f"{w.name} is already booked on this show."

        self._current_show.add_chamber_match(wrestlers, self._state,
                                              is_title_match=is_title_match, title_id=title_id)
        return True, "Elimination Chamber match added to the card!"

    def add_mitb_match_to_show(self, wrestlers: List[Wrestler]) -> Tuple[bool, str]:
        """
        Add a Money in the Bank ladder match to the current show.
        Requires 6-8 wrestlers.
        Returns (success, message).
        """
        if self._current_show is None:
            return False, "No show is currently being booked."

        if len(wrestlers) < 6 or len(wrestlers) > 8:
            return False, "Money in the Bank requires 6-8 wrestlers."

        # Check for duplicates
        if len(set(w.id for w in wrestlers)) != len(wrestlers):
            return False, "Cannot have duplicate wrestlers in the match."

        # Check if any wrestler is already booked
        for w in wrestlers:
            if self._current_show.is_wrestler_booked(w.id):
                return False, f"{w.name} is already booked on this show."

        self._current_show.add_mitb_match(wrestlers, self._state)
        return True, "Money in the Bank ladder match added to the card!"

    def get_mitb_holder(self) -> Optional[Wrestler]:
        """Get the wrestler currently holding the Money in the Bank briefcase, if any."""
        if not self.is_game_loaded:
            return None
        for wrestler in self._state.roster:
            if wrestler.has_mitb_briefcase:
                return wrestler
        return None

    def cash_in_mitb(self, holder: Wrestler, title_id: int) -> Tuple[bool, str]:
        """
        Cash in the Money in the Bank briefcase for a title shot.
        This just removes the briefcase - the actual match must be booked separately.
        Returns (success, message).
        """
        if not self.is_game_loaded:
            return False, "No game loaded."

        if not holder.has_mitb_briefcase:
            return False, f"{holder.name} does not have the Money in the Bank briefcase."

        title = self.get_title_by_id(title_id)
        if not title:
            return False, "Title not found."

        holder.has_mitb_briefcase = False
        self.save_game()
        return True, f"{holder.name} has cashed in Money in the Bank for a {title.name} shot!"

    # --- Feud Operations ---

    def get_feuds(self) -> List[Feud]:
        """Get all feuds."""
        if not self.is_game_loaded:
            return []
        return self._state.feuds

    def get_active_feuds(self) -> List[Feud]:
        """Get only active feuds."""
        if not self.is_game_loaded:
            return []
        return [feud for feud in self._state.feuds if feud.is_active]

    def get_feud_by_id(self, feud_id: int) -> Optional[Feud]:
        """Find a feud by ID."""
        if not self.is_game_loaded:
            return None
        return self._state.get_feud_by_id(feud_id)

    def get_wrestler_feud(self, wrestler_id: int) -> Optional[Feud]:
        """Get the active feud for a wrestler."""
        if not self.is_game_loaded:
            return None
        return self._state.get_wrestler_feud(wrestler_id)

    def create_feud(self, wrestler_a_id: int, wrestler_b_id: int,
                    intensity: str = "heated", matches: int = 3) -> Tuple[bool, str]:
        """
        Create a new feud between two wrestlers.
        Validates one-feud-per-wrestler rule.
        Returns (success, message).
        """
        if not self.is_game_loaded:
            return False, "No game loaded."

        # Validate wrestlers exist
        wrestler_a = self._state.get_wrestler_by_id(wrestler_a_id)
        wrestler_b = self._state.get_wrestler_by_id(wrestler_b_id)

        if not wrestler_a:
            return False, f"Wrestler with ID {wrestler_a_id} not found."
        if not wrestler_b:
            return False, f"Wrestler with ID {wrestler_b_id} not found."

        if wrestler_a_id == wrestler_b_id:
            return False, "A wrestler cannot feud with themselves."

        # Check one-feud-per-wrestler rule
        if self._state.is_wrestler_in_feud(wrestler_a_id):
            return False, f"{wrestler_a.name} is already in an active feud."
        if self._state.is_wrestler_in_feud(wrestler_b_id):
            return False, f"{wrestler_b.name} is already in an active feud."

        # Validate intensity
        valid_intensities = ["heated", "intense", "blood"]
        if intensity not in valid_intensities:
            intensity = "heated"

        # Validate matches count
        matches = max(1, min(10, matches))

        # Generate new ID
        new_id = max([f.id for f in self._state.feuds], default=0) + 1

        # Create the feud
        new_feud = Feud(
            id=new_id,
            wrestler_a_id=wrestler_a_id,
            wrestler_b_id=wrestler_b_id,
            intensity=intensity,
            matches_remaining=matches,
            total_matches=0,
            wins_a=0,
            wins_b=0,
            is_active=True,
            blowoff_match_scheduled=False
        )

        self._state.feuds.append(new_feud)
        self.save_game()

        return True, f"Started feud between {wrestler_a.name} and {wrestler_b.name} ({intensity.upper()}, {matches} matches)."

    def end_feud(self, feud_id: int) -> Tuple[bool, str]:
        """
        Manually end a feud.
        Returns (success, message).
        """
        if not self.is_game_loaded:
            return False, "No game loaded."

        feud = self._state.get_feud_by_id(feud_id)
        if not feud:
            return False, f"Feud with ID {feud_id} not found."

        if not feud.is_active:
            return False, "This feud has already ended."

        feud.is_active = False
        self.save_game()

        wrestler_a = self._state.get_wrestler_by_id(feud.wrestler_a_id)
        wrestler_b = self._state.get_wrestler_by_id(feud.wrestler_b_id)
        a_name = wrestler_a.name if wrestler_a else "Unknown"
        b_name = wrestler_b.name if wrestler_b else "Unknown"

        return True, f"Feud between {a_name} and {b_name} has been ended."

    def schedule_blowoff_match(self, feud_id: int) -> Tuple[bool, str]:
        """
        Schedule a blowoff match for a feud (next match ends feud).
        Returns (success, message).
        """
        if not self.is_game_loaded:
            return False, "No game loaded."

        feud = self._state.get_feud_by_id(feud_id)
        if not feud:
            return False, f"Feud with ID {feud_id} not found."

        if not feud.is_active:
            return False, "This feud has already ended."

        if feud.blowoff_match_scheduled:
            return False, "Blowoff match is already scheduled."

        feud.blowoff_match_scheduled = True
        self.save_game()

        wrestler_a = self._state.get_wrestler_by_id(feud.wrestler_a_id)
        wrestler_b = self._state.get_wrestler_by_id(feud.wrestler_b_id)
        a_name = wrestler_a.name if wrestler_a else "Unknown"
        b_name = wrestler_b.name if wrestler_b else "Unknown"

        return True, f"Blowoff match scheduled for {a_name} vs {b_name}. Next match will end the feud!"

    # --- Stable Operations ---

    def get_stables(self) -> List[Stable]:
        """Get all stables."""
        if not self.is_game_loaded:
            return []
        return self._state.stables

    def get_active_stables(self) -> List[Stable]:
        """Get only active stables."""
        if not self.is_game_loaded:
            return []
        return [stable for stable in self._state.stables if stable.is_active]

    def get_stable_by_id(self, stable_id: int) -> Optional[Stable]:
        """Find a stable by ID."""
        if not self.is_game_loaded:
            return None
        return self._state.get_stable_by_id(stable_id)

    def get_wrestler_stable(self, wrestler_id: int) -> Optional[Stable]:
        """Get the active stable a wrestler is in."""
        if not self.is_game_loaded:
            return None
        return self._state.get_wrestler_stable(wrestler_id)

    def create_stable(self, name: str, leader_id: int, member_ids: List[int]) -> Tuple[bool, str]:
        """
        Create a new stable with a leader and at least 3 members.
        The leader must be included in member_ids.
        Returns (success, message).
        """
        if not self.is_game_loaded:
            return False, "No game loaded."

        if not name or not name.strip():
            return False, "Stable name is required."

        # Validate minimum 3 members
        if len(member_ids) < 3:
            return False, "A stable requires at least 3 members."

        # Validate leader is in members
        if leader_id not in member_ids:
            return False, "Leader must be a member of the stable."

        # Validate all wrestlers exist
        for wrestler_id in member_ids:
            wrestler = self._state.get_wrestler_by_id(wrestler_id)
            if not wrestler:
                return False, f"Wrestler with ID {wrestler_id} not found."

        # Check one-stable-per-wrestler rule
        for wrestler_id in member_ids:
            if self._state.is_wrestler_in_stable(wrestler_id):
                wrestler = self._state.get_wrestler_by_id(wrestler_id)
                return False, f"{wrestler.name} is already in a stable."

        # Check for duplicate names
        existing_names = [s.name.lower() for s in self._state.stables if s.is_active]
        if name.strip().lower() in existing_names:
            return False, f"A stable named '{name}' already exists."

        # Generate new ID
        new_id = max([s.id for s in self._state.stables], default=0) + 1

        # Create the stable
        new_stable = Stable(
            id=new_id,
            name=name.strip(),
            leader_id=leader_id,
            member_ids=list(member_ids),  # Copy to avoid reference issues
            is_active=True
        )

        self._state.stables.append(new_stable)
        self.save_game()

        leader = self._state.get_wrestler_by_id(leader_id)
        leader_name = leader.name if leader else "Unknown"
        return True, f"Created stable '{name}' with {len(member_ids)} members. Leader: {leader_name}"

    def disband_stable(self, stable_id: int) -> Tuple[bool, str]:
        """
        Disband a stable by marking it inactive.
        Returns (success, message).
        """
        if not self.is_game_loaded:
            return False, "No game loaded."

        stable = self._state.get_stable_by_id(stable_id)
        if not stable:
            return False, f"Stable with ID {stable_id} not found."

        if not stable.is_active:
            return False, f"'{stable.name}' is already disbanded."

        stable.is_active = False
        self.save_game()

        return True, f"'{stable.name}' has been disbanded."

    def add_member_to_stable(self, stable_id: int, wrestler_id: int) -> Tuple[bool, str]:
        """
        Add a wrestler to an existing stable.
        Returns (success, message).
        """
        if not self.is_game_loaded:
            return False, "No game loaded."

        stable = self._state.get_stable_by_id(stable_id)
        if not stable:
            return False, f"Stable with ID {stable_id} not found."

        if not stable.is_active:
            return False, f"'{stable.name}' is disbanded."

        wrestler = self._state.get_wrestler_by_id(wrestler_id)
        if not wrestler:
            return False, f"Wrestler with ID {wrestler_id} not found."

        # Check if wrestler is already in a stable
        if self._state.is_wrestler_in_stable(wrestler_id):
            existing_stable = self._state.get_wrestler_stable(wrestler_id)
            return False, f"{wrestler.name} is already in '{existing_stable.name}'."

        if not stable.add_member(wrestler_id):
            return False, f"{wrestler.name} is already a member of '{stable.name}'."

        self.save_game()
        return True, f"{wrestler.name} has joined '{stable.name}'."

    def remove_member_from_stable(self, stable_id: int, wrestler_id: int) -> Tuple[bool, str]:
        """
        Remove a wrestler from a stable.
        Cannot remove if it would leave fewer than 3 members.
        Returns (success, message).
        """
        if not self.is_game_loaded:
            return False, "No game loaded."

        stable = self._state.get_stable_by_id(stable_id)
        if not stable:
            return False, f"Stable with ID {stable_id} not found."

        if not stable.is_active:
            return False, f"'{stable.name}' is disbanded."

        wrestler = self._state.get_wrestler_by_id(wrestler_id)
        if not wrestler:
            return False, f"Wrestler with ID {wrestler_id} not found."

        if wrestler_id not in stable.member_ids:
            return False, f"{wrestler.name} is not a member of '{stable.name}'."

        if len(stable.member_ids) <= 3:
            return False, f"Cannot remove {wrestler.name}. A stable must have at least 3 members."

        # Remove the member (this also handles leader reassignment if needed)
        was_leader = wrestler_id == stable.leader_id
        stable.remove_member(wrestler_id)

        self.save_game()

        if was_leader:
            new_leader = self._state.get_wrestler_by_id(stable.leader_id)
            new_leader_name = new_leader.name if new_leader else "Unknown"
            return True, f"{wrestler.name} has left '{stable.name}'. New leader: {new_leader_name}"
        return True, f"{wrestler.name} has left '{stable.name}'."

    def set_stable_leader(self, stable_id: int, wrestler_id: int) -> Tuple[bool, str]:
        """
        Change the leader of a stable.
        Returns (success, message).
        """
        if not self.is_game_loaded:
            return False, "No game loaded."

        stable = self._state.get_stable_by_id(stable_id)
        if not stable:
            return False, f"Stable with ID {stable_id} not found."

        if not stable.is_active:
            return False, f"'{stable.name}' is disbanded."

        wrestler = self._state.get_wrestler_by_id(wrestler_id)
        if not wrestler:
            return False, f"Wrestler with ID {wrestler_id} not found."

        if wrestler_id not in stable.member_ids:
            return False, f"{wrestler.name} is not a member of '{stable.name}'."

        if wrestler_id == stable.leader_id:
            return False, f"{wrestler.name} is already the leader of '{stable.name}'."

        stable.set_leader(wrestler_id)
        self.save_game()

        return True, f"{wrestler.name} is now the leader of '{stable.name}'."

    # --- Records Operations ---

    def get_match_history(self, limit: int = 50) -> List:
        """Get recent match history."""
        if not self.is_game_loaded:
            return []
        return self._state.records.get_recent_matches(limit)

    def get_wrestler_match_history(self, wrestler_id: int, limit: int = 50) -> List:
        """Get match history for a specific wrestler."""
        if not self.is_game_loaded:
            return []
        return self._state.records.get_wrestler_match_history(wrestler_id, limit)

    def get_head_to_head(self, wrestler_a_id: int, wrestler_b_id: int) -> dict:
        """Get head-to-head record between two wrestlers."""
        if not self.is_game_loaded:
            return {"wrestler_a_id": wrestler_a_id, "wrestler_b_id": wrestler_b_id,
                    "wins_a": 0, "wins_b": 0, "total_matches": 0, "matches": []}
        return self._state.records.get_head_to_head(wrestler_a_id, wrestler_b_id)

    def get_wrestler_records(self, wrestler_id: int) -> Optional[WrestlerRecords]:
        """Get extended records for a wrestler (streaks, PPV/TV stats)."""
        if not self.is_game_loaded:
            return None
        return self._state.records.get_wrestler_records(wrestler_id)

    def get_title_history(self, title_id: int) -> List[TitleReign]:
        """Get reign history for a specific title."""
        if not self.is_game_loaded:
            return []
        return self._state.records.get_title_history(title_id)

    # --- AI Auto-Booking Operations ---

    def get_card_suggestions(self, show_name: str = None, brand_id: int = None) -> Optional[CardSuggestion]:
        """
        Generate AI suggestions for the next show's card.
        Auto-detects if PPV based on current date.

        Args:
            show_name: Optional show name. If not provided, auto-generates based on date.
            brand_id: Optional brand ID to filter roster, titles, and teams.

        Returns:
            CardSuggestion with matches, feud suggestions, and warnings.
        """
        if not self.is_game_loaded:
            return None

        is_ppv = self._state.calendar_manager.is_ppv_week(self._state.month, self._state.week)

        if show_name is None:
            if is_ppv:
                ppv = self._state.calendar_manager.get_ppv_for_week(self._state.month, self._state.week)
                show_name = ppv.name if ppv else "PPV"
            else:
                show_name = f"Weekly Show - {self.get_current_date_string()}"

        booker = AutoBooker()
        return booker.generate_card(self._state, is_ppv, show_name, brand_id=brand_id)

    def apply_card_suggestions(self, card: CardSuggestion) -> Tuple[bool, str]:
        """
        Apply a card suggestion (or modified version) to create a show.
        Only applies matches marked as is_accepted=True.

        Args:
            card: CardSuggestion with matches to apply

        Returns:
            (success, message) tuple
        """
        if not self.is_game_loaded:
            return False, "No game loaded."

        # If no show is currently active, create one.
        # If one IS active (e.g. user created it then clicked AI Book), reuse it.
        if self._current_show is None:
            if not self.create_show(card.show_name, card.is_ppv):
                return False, "Could not create show."

        accepted_matches = [m for m in card.matches if m.is_accepted]

        if not accepted_matches:
            # If we created the show just for this and it failed, maybe cancel?
            # But if we reused it, we should probably keep it.
            # Let's just return error but keep the show state safe.
            return False, "No matches accepted."

        applied_count = 0
        for match in accepted_matches:
            success = self._apply_match_suggestion(match)
            if success:
                applied_count += 1

        if applied_count == 0:
            return False, "Could not apply any matches."

        return True, f"Applied {applied_count} matches to card."

    def _apply_match_suggestion(self, match: MatchSuggestion) -> bool:
        """Apply a single match suggestion to the current show."""
        try:
            if match.match_type == "singles":
                w1 = self.get_wrestler_by_id(match.participant_ids[0])
                w2 = self.get_wrestler_by_id(match.participant_ids[1])
                if not w1 or not w2:
                    return False
                return self.add_match_to_show(
                    w1, w2,
                    is_steel_cage=match.is_steel_cage,
                    is_title_match=match.is_title_match,
                    title_id=match.title_id
                )

            elif match.match_type == "tag":
                t1 = self.get_tag_team_by_id(match.participant_ids[0])
                t2 = self.get_tag_team_by_id(match.participant_ids[1])
                if not t1 or not t2:
                    return False
                return self.add_tag_match_to_show(
                    t1, t2,
                    is_title_match=match.is_title_match,
                    title_id=match.title_id
                )

            elif match.match_type in ("triple_threat", "fatal_four_way"):
                wrestlers = [self.get_wrestler_by_id(pid) for pid in match.participant_ids]
                if None in wrestlers:
                    return False
                success, _ = self.add_multi_man_match_to_show(
                    wrestlers,
                    is_title_match=match.is_title_match,
                    title_id=match.title_id
                )
                return success

            elif match.match_type == "ladder":
                wrestlers = [self.get_wrestler_by_id(pid) for pid in match.participant_ids]
                if None in wrestlers:
                    return False
                success, _ = self.add_ladder_match_to_show(
                    wrestlers,
                    is_title_match=match.is_title_match,
                    title_id=match.title_id
                )
                return success

            elif match.match_type == "iron_man":
                w1 = self.get_wrestler_by_id(match.participant_ids[0])
                w2 = self.get_wrestler_by_id(match.participant_ids[1])
                if not w1 or not w2:
                    return False
                success, _ = self.add_iron_man_match_to_show(
                    w1, w2,
                    time_limit=match.time_limit,
                    is_title_match=match.is_title_match,
                    title_id=match.title_id
                )
                return success

            elif match.match_type == "chamber":
                wrestlers = [self.get_wrestler_by_id(pid) for pid in match.participant_ids]
                if None in wrestlers or len(wrestlers) != 6:
                    return False
                success, _ = self.add_chamber_match_to_show(
                    wrestlers,
                    is_title_match=match.is_title_match,
                    title_id=match.title_id
                )
                return success

            elif match.match_type == "mitb":
                wrestlers = [self.get_wrestler_by_id(pid) for pid in match.participant_ids]
                if None in wrestlers or len(wrestlers) < 6:
                    return False
                success, _ = self.add_mitb_match_to_show(wrestlers)
                return success

            return False
        except Exception:
            return False

    def start_suggested_feud(self, suggestion: FeudSuggestion) -> Tuple[bool, str]:
        """
        Create a feud from an AI suggestion.

        Args:
            suggestion: FeudSuggestion with wrestler IDs

        Returns:
            (success, message) tuple
        """
        return self.create_feud(
            suggestion.wrestler_a_id,
            suggestion.wrestler_b_id,
            intensity="heated",
            matches=3
        )

    # --- Calendar Operations ---

    def get_calendar_manager(self) -> Optional[CalendarManager]:
        """Get the calendar manager."""
        if not self.is_game_loaded:
            return None
        return self._state.calendar_manager

    def get_calendar_month(self, year: int, month: int) -> Optional[CalendarMonth]:
        """Get calendar view data for a specific month."""
        if not self.is_game_loaded:
            return None
        return self._state.calendar_manager.generate_calendar_view(
            year, month,
            self._state.year, self._state.month, self._state.week
        )

    def get_upcoming_shows(self, count: int = 10) -> List[ScheduledShow]:
        """Get upcoming scheduled shows."""
        if not self.is_game_loaded:
            return []
        return self._state.calendar_manager.get_upcoming_shows(
            self._state.year, self._state.month, self._state.week, count
        )

    def get_week_schedule(self, year: int = None, month: int = None, week: int = None) -> List[ScheduledShow]:
        """Get all shows for a specific week (defaults to current week)."""
        if not self.is_game_loaded:
            return []
        if year is None:
            year = self._state.year
        if month is None:
            month = self._state.month
        if week is None:
            week = self._state.week
        return self._state.calendar_manager.get_week_schedule(year, month, week)

    def get_scheduled_show_by_id(self, show_id: int) -> Optional[ScheduledShow]:
        """Get a scheduled show by ID."""
        if not self.is_game_loaded:
            return None
        return self._state.calendar_manager.get_scheduled_show_by_id(show_id)

    # --- Brand Operations ---

    def get_brands(self) -> List[Brand]:
        """Get all brands."""
        if not self.is_game_loaded:
            return []
        return self._state.calendar_manager.brands

    def get_active_brands(self) -> List[Brand]:
        """Get only active brands."""
        if not self.is_game_loaded:
            return []
        return [b for b in self._state.calendar_manager.brands if b.is_active]

    def get_brand_by_id(self, brand_id: int) -> Optional[Brand]:
        """Get a brand by ID."""
        if not self.is_game_loaded:
            return None
        return self._state.calendar_manager.get_brand_by_id(brand_id)

    def create_brand(self, name: str, short_name: str, color: str) -> Tuple[bool, str]:
        """Create a new brand."""
        if not self.is_game_loaded:
            return False, "No game loaded."

        if not name or not name.strip():
            return False, "Brand name is required."

        # Check for duplicate names
        existing = [b.name.lower() for b in self._state.calendar_manager.brands]
        if name.lower() in existing:
            return False, f"A brand named '{name}' already exists."

        brand = self._state.calendar_manager.create_brand(name, short_name, color)
        self.save_game()
        return True, f"Created brand: {brand.name}"

    def assign_wrestler_to_brand(self, wrestler_id: int, brand_id: int) -> Tuple[bool, str]:
        """Assign a wrestler to a brand."""
        if not self.is_game_loaded:
            return False, "No game loaded."

        wrestler = self.get_wrestler_by_id(wrestler_id)
        if not wrestler:
            return False, "Wrestler not found."

        brand = self.get_brand_by_id(brand_id)
        if not brand:
            return False, "Brand not found."

        self._state.calendar_manager.assign_wrestler_to_brand(wrestler_id, brand_id)
        self.save_game()
        return True, f"{wrestler.name} assigned to {brand.name}."

    def assign_title_to_brand(self, title_id: int, brand_id: int) -> Tuple[bool, str]:
        """Assign a title to a brand."""
        if not self.is_game_loaded:
            return False, "No game loaded."

        title = self.get_title_by_id(title_id)
        if not title:
            return False, "Title not found."

        brand = self.get_brand_by_id(brand_id)
        if not brand:
            return False, "Brand not found."

        self._state.calendar_manager.assign_title_to_brand(title_id, brand_id)
        self.save_game()
        return True, f"{title.name} assigned to {brand.name}."

    def unassign_wrestler_from_brand(self, wrestler_id: int) -> Tuple[bool, str]:
        """Make a wrestler a free agent (no brand)."""
        if not self.is_game_loaded:
            return False, "No game loaded."

        wrestler = self.get_wrestler_by_id(wrestler_id)
        if not wrestler:
            return False, "Wrestler not found."

        self._state.calendar_manager.unassign_wrestler_from_brand(wrestler_id)
        self.save_game()
        return True, f"{wrestler.name} is now a free agent."

    def unassign_title_from_brand(self, title_id: int) -> Tuple[bool, str]:
        """Make a title a floating title (no brand)."""
        if not self.is_game_loaded:
            return False, "No game loaded."

        title = self.get_title_by_id(title_id)
        if not title:
            return False, "Title not found."

        self._state.calendar_manager.unassign_title_from_brand(title_id)
        self.save_game()
        return True, f"{title.name} is now a floating title."

    def get_wrestler_brand(self, wrestler_id: int) -> Optional[Brand]:
        """Get the brand a wrestler is assigned to."""
        if not self.is_game_loaded:
            return None
        return self._state.calendar_manager.get_wrestler_brand(wrestler_id)

    def get_title_brand(self, title_id: int) -> Optional[Brand]:
        """Get the brand a title is assigned to."""
        if not self.is_game_loaded:
            return None
        return self._state.calendar_manager.get_title_brand(title_id)

    def get_brand_roster(self, brand_id: int) -> List[Wrestler]:
        """Get wrestlers assigned to a brand."""
        if not self.is_game_loaded:
            return []
        brand = self.get_brand_by_id(brand_id)
        if not brand:
            return []
        return brand.get_roster(self._state.roster)

    def get_unassigned_wrestlers(self) -> List[Wrestler]:
        """Get wrestlers not assigned to any brand (free agents)."""
        if not self.is_game_loaded:
            return []
        assigned = set()
        for brand in self._state.calendar_manager.brands:
            assigned.update(brand.assigned_wrestlers)
        return [w for w in self._state.roster if w.id not in assigned]

    def get_brand_titles(self, brand_id: int) -> List[Title]:
        """Get titles assigned to a brand."""
        if not self.is_game_loaded:
            return []
        brand = self.get_brand_by_id(brand_id)
        if not brand:
            return []
        return brand.get_titles(self._state.titles)

    def get_unassigned_titles(self) -> List[Title]:
        """Get titles not assigned to any brand (floating)."""
        if not self.is_game_loaded:
            return []
        assigned = set()
        for brand in self._state.calendar_manager.brands:
            assigned.update(brand.assigned_titles)
        return [t for t in self._state.titles if t.id not in assigned]

    # --- PPV Operations ---

    def get_ppv_calendar(self) -> List[dict]:
        """Get the PPV calendar list as dictionaries."""
        if not self.is_game_loaded:
            return []
        return [ppv.to_dict() for ppv in self._state.calendar_manager.get_ppv_calendar()]

    def update_ppv_name(self, month: int, new_name: str) -> Tuple[bool, str]:
        """Update the name of a PPV for a specific month (legacy wrapper)."""
        if not self.is_game_loaded:
            return False, "No game loaded."

        if not new_name or not new_name.strip():
            return False, "PPV name is required."

        ppvs = self._state.calendar_manager.get_ppvs_for_month(month)
        if not ppvs:
             return False, f"No PPV found for month {month}"
        
        # Update the first active PPV found for the month (legacy behavior assumption)
        ppv = ppvs[0]
        old_name = ppv.name
        self._state.calendar_manager.edit_ppv(ppv.id, name=new_name.strip())
        self.save_game()
        return True, f"Updated PPV from '{old_name}' to '{new_name}'"

    def add_ppv(self, name: str, month: int, week: int, tier: str, brand_id: Optional[int] = None) -> Tuple[bool, str]:
        """Add a new PPV to the calendar."""
        if not self.is_game_loaded:
            return False, "No game loaded."
            
        self._state.calendar_manager.add_ppv(name, month, week, tier, brand_id)
        self.save_game()
        return True, f"Added PPV '{name}' to Month {month}, Week {week}."

    def remove_ppv(self, ppv_id: int) -> Tuple[bool, str]:
        """Remove a PPV from the calendar."""
        if not self.is_game_loaded:
            return False, "No game loaded."
            
        if self._state.calendar_manager.remove_ppv(ppv_id):
            self.save_game()
            return True, "PPV removed."
        return False, "PPV not found."

    def get_current_scheduled_show_id(self) -> Optional[int]:
        """Get the ID of the currently selected scheduled show."""
        return self._current_scheduled_show_id

    # --- Weekly Show Operations ---

    def get_weekly_shows(self) -> List[WeeklyShow]:
        """Get all weekly shows."""
        if not self.is_game_loaded:
            return []
        return self._state.calendar_manager.weekly_shows

    def get_active_weekly_shows(self) -> List[WeeklyShow]:
        """Get only active weekly shows."""
        if not self.is_game_loaded:
            return []
        return [s for s in self._state.calendar_manager.weekly_shows if s.is_active]

    def get_weekly_show_by_id(self, show_id: int) -> Optional[WeeklyShow]:
        """Get a weekly show by ID."""
        if not self.is_game_loaded:
            return None
        return self._state.calendar_manager.get_weekly_show_by_id(show_id)

    def create_weekly_show(
        self,
        name: str,
        short_name: str,
        day_of_week: int,
        tier: str,
        brand_id: Optional[int] = None,
        match_slots: int = 5,
        segment_slots: int = 3,
        runtime_minutes: int = 120
    ) -> Tuple[bool, str]:
        """Create a new weekly show."""
        if not self.is_game_loaded:
            return False, "No game loaded."

        if not name or not name.strip():
            return False, "Show name is required."

        # Convert day_of_week int to enum
        try:
            day = DayOfWeek(day_of_week)
        except ValueError:
            return False, "Invalid day of week."

        # Convert tier string to enum
        try:
            show_tier = ShowTier(tier)
        except ValueError:
            return False, "Invalid show tier."

        show = self._state.calendar_manager.create_weekly_show(
            name=name,
            short_name=short_name,
            day_of_week=day,
            tier=show_tier,
            brand_id=brand_id,
            match_slots=match_slots,
            segment_slots=segment_slots,
            runtime_minutes=runtime_minutes
        )
        self.save_game()
        return True, f"Created weekly show: {show.name}"

    def deactivate_weekly_show(self, show_id: int) -> Tuple[bool, str]:
        """Deactivate a weekly show."""
        if not self.is_game_loaded:
            return False, "No game loaded."

        show = self.get_weekly_show_by_id(show_id)
        if not show:
            return False, "Show not found."

        self._state.calendar_manager.deactivate_weekly_show(show_id)
        self.save_game()
        return True, f"{show.name} has been cancelled."
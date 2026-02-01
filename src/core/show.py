from typing import List, Union, TYPE_CHECKING, Optional
from core.match import Match, RoyalRumbleMatch, MultiManMatch, LadderMatch, IronManMatch, EliminationChamberMatch, MoneyInTheBankMatch
from core.game_state import GameState, MatchResult, TagMatchResult, RumbleResult, MultiManResult, LadderMatchResult, IronManResult, EliminationChamberResult, MoneyInTheBankResult, ShowResult
from core.commentary import generate_interference_commentary
from core.records import MatchHistoryEntry

if TYPE_CHECKING:
    from core.wrestler import Wrestler
    from core.tag_team import TagTeam


def calculate_tv_rating(final_rating: int) -> float:
    """Convert show's 0-100 rating to a TV rating on a 1.0-5.0 scale."""
    tv = 1.0 + (final_rating / 100.0) * 4.0
    return round(max(1.0, min(5.0, tv)), 1)


def calculate_attendance(prestige: int, avg_heat: float, is_ppv: bool, viewers: int) -> int:
    """Calculate event attendance based on prestige, heat, show type, and viewership."""
    if is_ppv:
        base = 10000 + int(prestige * 400)       # 10k to 50k
        viewer_floor = viewers // 50               # 20k at 1M viewers
    else:
        base = 5000 + int(prestige * 100)         # 5k to 15k
        viewer_floor = viewers // 200              # 5k at 1M viewers

    # Heat modifier: avg_heat 50 = 1.0x, heat 100 = 1.3x, heat 0 = 0.7x
    heat_modifier = 0.7 + (avg_heat / 100.0) * 0.6
    attendance = int(base * heat_modifier)
    attendance = max(attendance, viewer_floor)
    return attendance


def calculate_viewer_change(final_rating: int, prestige: int, current_viewers: int) -> int:
    """
    Calculate viewer growth/shrinkage after a show.
    Shows above the quality threshold grow viewers, below shrink them.
    """
    threshold = (prestige / 2) + 25  # Higher prestige = higher expectations
    diff = final_rating - threshold
    pct_change = diff * 0.0015
    pct_change = max(-0.05, min(0.05, pct_change))
    return int(current_viewers * pct_change)


def calculate_prestige_change(final_rating: int, current_prestige: int) -> int:
    """Calculate prestige change after a show based on quality."""
    if final_rating >= 80:
        change = 2 if final_rating >= 90 else 1
        if current_prestige >= 80:
            change = max(0, change - 1)
    elif final_rating >= 60:
        change = 1 if final_rating >= 70 else 0
        if current_prestige >= 90:
            change = 0
    elif final_rating >= 40:
        change = 0
    elif final_rating >= 20:
        change = -1
        if current_prestige <= 20:
            change = 0
    else:
        change = -2
        if current_prestige <= 10:
            change = -1
    return change


def calculate_revenue(attendance: int, is_ppv: bool, viewers: int, prestige: int) -> tuple:
    """
    Calculate ticket_revenue and ppv_revenue.
    Returns (ticket_revenue, ppv_revenue).
    """
    if is_ppv:
        ticket_price = 30 + int(prestige * 0.7)  # $30 to $100
        ppv_price = 44.99
        ppv_buy_rate = 0.05 + (prestige / 100.0) * 0.10  # 5% to 15%
        ppv_buys = int(viewers * ppv_buy_rate)
        ppv_revenue = int(ppv_buys * ppv_price)
    else:
        ticket_price = 15 + int(prestige * 0.35)  # $15 to $50
        ppv_revenue = 0

    ticket_revenue = attendance * ticket_price
    return ticket_revenue, ppv_revenue


class Show:
    """
    Represents a wrestling event/show.
    Pure logic - no I/O operations.
    """
    def __init__(self, name: str, is_ppv: bool = False):
        self.name = name
        self.is_ppv = is_ppv
        self.matches: List[Match] = []
        self.rumble_matches: List[RoyalRumbleMatch] = []
        self.multi_man_matches: List[MultiManMatch] = []
        self.ladder_matches: List[LadderMatch] = []
        self.iron_man_matches: List[IronManMatch] = []
        self.chamber_matches: List[EliminationChamberMatch] = []
        self.mitb_matches: List[MoneyInTheBankMatch] = []
        self.is_finished = False

    def add_match(self, wrestler_a: 'Wrestler', wrestler_b: 'Wrestler', is_steel_cage: bool = False, is_title_match: bool = False, title_id: Optional[int] = None, game_state: 'GameState' = None) -> None:
        """Creates a singles match and adds it to the card."""
        new_match = Match(wrestler_a, wrestler_b, is_steel_cage=is_steel_cage, is_title_match=is_title_match, title_id=title_id, game_state=game_state)
        self.matches.append(new_match)

    def add_tag_match(self, team_a: 'TagTeam', team_b: 'TagTeam', roster: List['Wrestler'], is_steel_cage: bool = False, is_title_match: bool = False, title_id: Optional[int] = None, game_state: 'GameState' = None) -> None:
        """Creates a tag team match and adds it to the card."""
        new_match = Match(
            match_type="Tag Team",
            team_a=team_a,
            team_b=team_b,
            roster=roster,
            is_steel_cage=is_steel_cage,
            is_title_match=is_title_match,
            title_id=title_id,
            game_state=game_state
        )
        self.matches.append(new_match)

    def add_rumble_match(self, wrestlers: List['Wrestler'], game_state: 'GameState' = None) -> None:
        """Creates a Royal Rumble match and adds it to the card."""
        rumble = RoyalRumbleMatch(wrestlers, game_state)
        self.rumble_matches.append(rumble)

    def add_multi_man_match(self, wrestlers: List['Wrestler'], game_state: 'GameState' = None,
                            is_title_match: bool = False, title_id: Optional[int] = None) -> None:
        """Creates a Triple Threat (3) or Fatal 4-Way (4) match and adds it to the card."""
        multi_man = MultiManMatch(wrestlers, game_state, is_title_match=is_title_match, title_id=title_id)
        self.multi_man_matches.append(multi_man)

    def add_ladder_match(self, wrestlers: List['Wrestler'], game_state: 'GameState' = None,
                         is_title_match: bool = False, title_id: Optional[int] = None) -> None:
        """Creates a Ladder match and adds it to the card."""
        ladder = LadderMatch(wrestlers, game_state, is_title_match=is_title_match, title_id=title_id)
        self.ladder_matches.append(ladder)

    def add_iron_man_match(self, wrestler_a: 'Wrestler', wrestler_b: 'Wrestler',
                           time_limit: int = 30, game_state: 'GameState' = None,
                           is_title_match: bool = False, title_id: Optional[int] = None) -> None:
        """Creates an Iron Man match and adds it to the card."""
        iron_man = IronManMatch(wrestler_a, wrestler_b, time_limit, game_state,
                                is_title_match=is_title_match, title_id=title_id)
        self.iron_man_matches.append(iron_man)

    def add_chamber_match(self, wrestlers: List['Wrestler'], game_state: 'GameState' = None,
                          is_title_match: bool = False, title_id: Optional[int] = None) -> None:
        """Creates an Elimination Chamber match and adds it to the card."""
        chamber = EliminationChamberMatch(wrestlers, game_state, is_title_match=is_title_match, title_id=title_id)
        self.chamber_matches.append(chamber)

    def add_mitb_match(self, wrestlers: List['Wrestler'], game_state: 'GameState' = None) -> None:
        """Creates a Money in the Bank ladder match and adds it to the card."""
        mitb = MoneyInTheBankMatch(wrestlers, game_state)
        self.mitb_matches.append(mitb)

    def is_wrestler_booked(self, wrestler_id: int) -> bool:
        """Check if a wrestler is already booked on this show."""
        for match in self.matches:
            if match.match_type == "Tag Team":
                # Check tag team members
                if match.team_a and wrestler_id in match.team_a.member_ids:
                    return True
                if match.team_b and wrestler_id in match.team_b.member_ids:
                    return True
            else:
                # Check singles match wrestlers
                if match.p1 and match.p1.id == wrestler_id:
                    return True
                if match.p2 and match.p2.id == wrestler_id:
                    return True
        # Check Royal Rumble participants
        for rumble in self.rumble_matches:
            if any(w.id == wrestler_id for w in rumble.wrestlers):
                return True
        # Check multi-man match participants
        for multi_man in self.multi_man_matches:
            if any(w.id == wrestler_id for w in multi_man.wrestlers):
                return True
        # Check ladder match participants
        for ladder in self.ladder_matches:
            if any(w.id == wrestler_id for w in ladder.wrestlers):
                return True
        # Check iron man match participants
        for iron_man in self.iron_man_matches:
            if iron_man.wrestler_a.id == wrestler_id or iron_man.wrestler_b.id == wrestler_id:
                return True
        # Check Elimination Chamber participants
        for chamber in self.chamber_matches:
            if any(w.id == wrestler_id for w in chamber.wrestlers):
                return True
        # Check Money in the Bank participants
        for mitb in self.mitb_matches:
            if any(w.id == wrestler_id for w in mitb.wrestlers):
                return True
        return False
    
    def get_booked_wrestlers(self) -> List['Wrestler']:
        """Returns a unique list of all wrestlers booked on the show."""
        booked = set()
        for match in self.matches:
            if match.match_type == "Tag Team":
                if match.team_a:
                    booked.update(match.team_a.get_members(match.roster))
                if match.team_b:
                    booked.update(match.team_b.get_members(match.roster))
            else:
                if match.p1:
                    booked.add(match.p1)
                if match.p2:
                    booked.add(match.p2)
        # Include Royal Rumble participants
        for rumble in self.rumble_matches:
            booked.update(rumble.wrestlers)
        # Include multi-man match participants
        for multi_man in self.multi_man_matches:
            booked.update(multi_man.wrestlers)
        # Include ladder match participants
        for ladder in self.ladder_matches:
            booked.update(ladder.wrestlers)
        # Include iron man match participants
        for iron_man in self.iron_man_matches:
            booked.add(iron_man.wrestler_a)
            booked.add(iron_man.wrestler_b)
        # Include Elimination Chamber participants
        for chamber in self.chamber_matches:
            booked.update(chamber.wrestlers)
        # Include Money in the Bank participants
        for mitb in self.mitb_matches:
            booked.update(mitb.wrestlers)
        return list(booked)

    @property
    def match_count(self) -> int:
        return len(self.matches) + len(self.rumble_matches) + len(self.multi_man_matches) + len(self.ladder_matches) + len(self.iron_man_matches) + len(self.chamber_matches) + len(self.mitb_matches)

    def _apply_stable_heat(self, winner: 'Wrestler', loser: 'Wrestler', game_state: 'GameState') -> None:
        """
        Apply shared heat effects to stablemates after a singles match.
        - Winner's stablemates gain +2 heat
        - Loser's stablemates lose -1 heat
        """
        if not game_state:
            return

        # Get winner's stable
        winner_stable = game_state.get_wrestler_stable(winner.id)
        if winner_stable:
            for member_id in winner_stable.member_ids:
                if member_id != winner.id:  # Don't double-apply to the winner
                    member = game_state.get_wrestler_by_id(member_id)
                    if member:
                        member.heat = min(100, member.heat + 2)

        # Get loser's stable
        loser_stable = game_state.get_wrestler_stable(loser.id)
        if loser_stable:
            for member_id in loser_stable.member_ids:
                if member_id != loser.id:  # Don't double-apply to the loser
                    member = game_state.get_wrestler_by_id(member_id)
                    if member:
                        member.heat = max(0, member.heat - 1)

    def _record_match_history(
        self,
        game_state: 'GameState',
        match_type: str,
        participant_ids: List[int],
        participant_names: List[str],
        winner_ids: List[int],
        winner_names: List[str],
        loser_ids: List[int],
        loser_names: List[str],
        rating: int,
        is_title_match: bool = False,
        title_id: Optional[int] = None,
        title_name: str = "",
        title_changed: bool = False,
    ) -> None:
        """Record a match to history and update wrestler records."""
        if not game_state:
            return

        # Get current date
        date = {
            "year": game_state.year,
            "month": game_state.month,
            "week": game_state.week,
        }

        # Create match history entry
        entry = MatchHistoryEntry(
            id=game_state.records.get_next_match_id(),
            date=date,
            show_name=self.name,
            is_ppv=self.is_ppv,
            match_type=match_type,
            participant_ids=participant_ids,
            participant_names=participant_names,
            winner_ids=winner_ids,
            winner_names=winner_names,
            loser_ids=loser_ids,
            loser_names=loser_names,
            rating=rating,
            stars=rating / 20,
            is_title_match=is_title_match,
            title_id=title_id,
            title_name=title_name,
            title_changed=title_changed,
        )
        game_state.records.add_match(entry)

        # Update wrestler records (streaks, PPV/TV stats)
        for winner_id in winner_ids:
            game_state.records.record_wrestler_win(winner_id, self.is_ppv)

        for loser_id in loser_ids:
            game_state.records.record_wrestler_loss(loser_id, self.is_ppv)

    def _handle_title_change(
        self,
        game_state: 'GameState',
        title_id: int,
        title_name: str,
        old_holder_id: Optional[int],
        new_holder_id: int,
        new_holder_name: str,
        holder_type: str,  # "wrestler" or "tag_team"
    ) -> None:
        """Handle title reign tracking when a title changes hands."""
        if not game_state:
            return

        date = {
            "year": game_state.year,
            "month": game_state.month,
            "week": game_state.week,
        }

        # End the previous reign if there was a holder
        if old_holder_id is not None:
            game_state.records.end_title_reign(title_id, old_holder_id, date)

        # Start the new reign
        game_state.records.start_title_reign(
            title_id=title_id,
            title_name=title_name,
            holder_id=new_holder_id,
            holder_name=new_holder_name,
            holder_type=holder_type,
            date=date,
        )

    def _record_title_defense(
        self,
        game_state: 'GameState',
        title_id: int,
        holder_id: int,
    ) -> None:
        """Record a successful title defense."""
        if not game_state:
            return
        game_state.records.record_title_defense(title_id, holder_id)

    def run(self, game_state: 'GameState') -> ShowResult:
        """
        Simulates all matches, updates wrestler stats, and calculates finances.
        Returns a ShowResult with all match data.
        """
        match_results: List[Union[MatchResult, TagMatchResult]] = []
        total_score = 0
        roster = game_state.roster

        for match in self.matches:
            # Track original title holder before match (for title change detection)
            original_holder_id = None
            title_name = ""
            if match.is_title_match and match.title_id and game_state:
                title = next((t for t in game_state.titles if t.id == match.title_id), None)
                if title:
                    original_holder_id = title.current_holder_id
                    title_name = title.name

            # Check for feud between wrestlers (singles matches only)
            if match.match_type != "Tag Team" and match.p1 and match.p2:
                feud = game_state.get_feud_between(match.p1.id, match.p2.id)
                if feud:
                    match.feud = feud

            # Run the simulation and get results, including commentary
            winner, loser, winning_team, losing_team, pinned_wrestler, rating, commentary = match.simulate()

            if match.match_type == "Tag Team":
                # Detect title change for tag matches
                title_changed = False
                new_champion_name = ""
                if match.is_title_match and match.title_id and game_state:
                    title = next((t for t in game_state.titles if t.id == match.title_id), None)
                    if title and title.current_holder_id != original_holder_id:
                        title_changed = True
                        new_champion_name = winning_team.name if winning_team else ""

                # Create tag match result data
                result = TagMatchResult(
                    team_a_name=match.team_a.name,
                    team_b_name=match.team_b.name,
                    winning_team_name=winning_team.name,
                    losing_team_name=losing_team.name,
                    pinned_wrestler_name=pinned_wrestler.name if pinned_wrestler else "Unknown",
                    rating=rating,
                    stars=rating / 20,
                    commentary=commentary,
                    is_title_match=match.is_title_match,
                    title_name=title_name,
                    title_changed=title_changed,
                    new_champion_name=new_champion_name
                )
                match_results.append(result)

                # Update team chemistry and records
                winning_team.update_after_match(is_winner=True)
                losing_team.update_after_match(is_winner=False)

                # Apply consequences to all 4 wrestlers
                winning_members = winning_team.get_members(roster)
                losing_members = losing_team.get_members(roster)

                for wrestler in winning_members:
                    wrestler.update_after_match(is_winner=True, match_rating=rating)
                for wrestler in losing_members:
                    wrestler.update_after_match(is_winner=False, match_rating=rating)

                # Record match history (tag team)
                self._record_match_history(
                    game_state=game_state,
                    match_type="Tag Team",
                    participant_ids=winning_team.member_ids + losing_team.member_ids,
                    participant_names=[w.name for w in winning_members + losing_members],
                    winner_ids=winning_team.member_ids,
                    winner_names=[w.name for w in winning_members],
                    loser_ids=losing_team.member_ids,
                    loser_names=[w.name for w in losing_members],
                    rating=rating,
                    is_title_match=match.is_title_match,
                    title_id=match.title_id,
                    title_name=title_name,
                    title_changed=title_changed,
                )

                # Handle title reign tracking
                if match.is_title_match and match.title_id:
                    if title_changed:
                        self._handle_title_change(
                            game_state=game_state,
                            title_id=match.title_id,
                            title_name=title_name,
                            old_holder_id=original_holder_id,
                            new_holder_id=winning_team.id,
                            new_holder_name=winning_team.name,
                            holder_type="tag_team",
                        )
                    elif original_holder_id is not None:
                        # Successful title defense
                        self._record_title_defense(game_state, match.title_id, original_holder_id)
            else:
                # Detect title change for singles matches
                title_changed = False
                new_champion_name = ""
                if match.is_title_match and match.title_id and game_state:
                    title = next((t for t in game_state.titles if t.id == match.title_id), None)
                    if title and title.current_holder_id != original_holder_id:
                        title_changed = True
                        new_champion_name = winner.name if winner else ""

                # Process feud state
                is_feud_match = False
                feud_intensity = ""
                feud_ended = False
                if match.feud and match.feud.is_active:
                    is_feud_match = True
                    feud_intensity = match.feud.intensity
                    feud_ended = match.feud.record_match(winner.id)

                # Add interference commentary if it occurred
                if match.interference_occurred and match.interference_by:
                    # Determine the opponent (the one not in the interfering stable)
                    opponent = loser if match.interference_helped else winner
                    interference_lines = generate_interference_commentary(
                        match.interference_by,
                        opponent.name,
                        match.interference_helped
                    )
                    commentary = list(commentary) + interference_lines

                # Create singles result data
                result = MatchResult(
                    wrestler_a_name=match.p1.name,
                    wrestler_b_name=match.p2.name,
                    winner_name=winner.name,
                    loser_name=loser.name,
                    rating=rating,
                    stars=rating / 20,
                    commentary=commentary,
                    is_title_match=match.is_title_match,
                    title_name=title_name,
                    title_changed=title_changed,
                    new_champion_name=new_champion_name,
                    is_feud_match=is_feud_match,
                    feud_intensity=feud_intensity,
                    feud_ended=feud_ended,
                    interference_occurred=match.interference_occurred,
                    interference_by=match.interference_by or "",
                    interference_helped=match.interference_helped
                )
                match_results.append(result)

                # Apply consequences to wrestlers
                is_p1_winner = (winner == match.p1)
                match.p1.update_after_match(is_winner=is_p1_winner, match_rating=rating)
                match.p2.update_after_match(is_winner=(not is_p1_winner), match_rating=rating)

                # Apply shared heat to stablemates
                self._apply_stable_heat(winner, loser, game_state)

                # Record match history (singles)
                self._record_match_history(
                    game_state=game_state,
                    match_type="Singles",
                    participant_ids=[match.p1.id, match.p2.id],
                    participant_names=[match.p1.name, match.p2.name],
                    winner_ids=[winner.id],
                    winner_names=[winner.name],
                    loser_ids=[loser.id],
                    loser_names=[loser.name],
                    rating=rating,
                    is_title_match=match.is_title_match,
                    title_id=match.title_id,
                    title_name=title_name,
                    title_changed=title_changed,
                )

                # Handle title reign tracking
                if match.is_title_match and match.title_id:
                    if title_changed:
                        self._handle_title_change(
                            game_state=game_state,
                            title_id=match.title_id,
                            title_name=title_name,
                            old_holder_id=original_holder_id,
                            new_holder_id=winner.id,
                            new_holder_name=winner.name,
                            holder_type="wrestler",
                        )
                    elif original_holder_id is not None:
                        # Successful title defense
                        self._record_title_defense(game_state, match.title_id, original_holder_id)

            total_score += rating

        # Process Royal Rumble matches
        for rumble in self.rumble_matches:
            winner, eliminations, rating, commentary = rumble.simulate()

            # Create elimination info for result
            elimination_data = []
            for elim in eliminations:
                elimination_data.append({
                    'wrestler_name': elim['wrestler'].name,
                    'eliminated_by': elim['eliminated_by'].name,
                    'entry_number': elim['entry_number'],
                    'elimination_order': elim['elimination_order']
                })

            result = RumbleResult(
                winner_name=winner.name,
                eliminations=elimination_data,
                rating=rating,
                stars=rating / 20,
                commentary=commentary
            )
            match_results.append(result)

            # Update all participants - winner gets a win, others get a loss
            losers = [w for w in rumble.wrestlers if w != winner]
            for wrestler in rumble.wrestlers:
                is_winner = (wrestler == winner)
                wrestler.update_after_match(is_winner=is_winner, match_rating=rating, duration_cost=15)

            # Record match history (Royal Rumble)
            self._record_match_history(
                game_state=game_state,
                match_type="Royal Rumble",
                participant_ids=[w.id for w in rumble.wrestlers],
                participant_names=[w.name for w in rumble.wrestlers],
                winner_ids=[winner.id],
                winner_names=[winner.name],
                loser_ids=[w.id for w in losers],
                loser_names=[w.name for w in losers],
                rating=rating,
            )

            total_score += rating

        # Process multi-man matches (Triple Threat, Fatal 4-Way)
        for multi_man in self.multi_man_matches:
            # Track original title holder before match (for title change detection)
            original_holder_id = None
            title_name = ""
            if multi_man.is_title_match and multi_man.title_id and game_state:
                title = next((t for t in game_state.titles if t.id == multi_man.title_id), None)
                if title:
                    original_holder_id = title.current_holder_id
                    title_name = title.name

            winner, losers, pinned_wrestler, rating, commentary = multi_man.simulate()

            # Detect title change
            title_changed = False
            new_champion_name = ""
            if multi_man.is_title_match and multi_man.title_id and game_state:
                title = next((t for t in game_state.titles if t.id == multi_man.title_id), None)
                if title and title.current_holder_id != original_holder_id:
                    title_changed = True
                    new_champion_name = winner.name if winner else ""

            result = MultiManResult(
                match_type=multi_man.match_type,
                participant_names=[w.name for w in multi_man.wrestlers],
                winner_name=winner.name,
                loser_names=[l.name for l in losers],
                pinned_wrestler_name=pinned_wrestler.name if pinned_wrestler else "Unknown",
                rating=rating,
                stars=rating / 20,
                commentary=commentary,
                is_title_match=multi_man.is_title_match,
                title_name=title_name,
                title_changed=title_changed,
                new_champion_name=new_champion_name
            )
            match_results.append(result)

            # Update all participants - winner gets a win, others get a loss
            for wrestler in multi_man.wrestlers:
                is_winner = (wrestler == winner)
                wrestler.update_after_match(is_winner=is_winner, match_rating=rating)

            # Record match history (multi-man)
            self._record_match_history(
                game_state=game_state,
                match_type=multi_man.match_type,
                participant_ids=[w.id for w in multi_man.wrestlers],
                participant_names=[w.name for w in multi_man.wrestlers],
                winner_ids=[winner.id],
                winner_names=[winner.name],
                loser_ids=[l.id for l in losers],
                loser_names=[l.name for l in losers],
                rating=rating,
                is_title_match=multi_man.is_title_match,
                title_id=multi_man.title_id,
                title_name=title_name,
                title_changed=title_changed,
            )

            # Handle title reign tracking
            if multi_man.is_title_match and multi_man.title_id:
                if title_changed:
                    self._handle_title_change(
                        game_state=game_state,
                        title_id=multi_man.title_id,
                        title_name=title_name,
                        old_holder_id=original_holder_id,
                        new_holder_id=winner.id,
                        new_holder_name=winner.name,
                        holder_type="wrestler",
                    )
                elif original_holder_id is not None:
                    # Successful title defense
                    self._record_title_defense(game_state, multi_man.title_id, original_holder_id)

            total_score += rating

        # Process ladder matches
        for ladder in self.ladder_matches:
            # Track original title holder before match (for title change detection)
            original_holder_id = None
            title_name = ""
            if ladder.is_title_match and ladder.title_id and game_state:
                title = next((t for t in game_state.titles if t.id == ladder.title_id), None)
                if title:
                    original_holder_id = title.current_holder_id
                    title_name = title.name

            winner, losers, rating, commentary = ladder.simulate()

            # Detect title change
            title_changed = False
            new_champion_name = ""
            if ladder.is_title_match and ladder.title_id and game_state:
                title = next((t for t in game_state.titles if t.id == ladder.title_id), None)
                if title and title.current_holder_id != original_holder_id:
                    title_changed = True
                    new_champion_name = winner.name if winner else ""

            result = LadderMatchResult(
                match_type=ladder.match_type,
                participant_names=[w.name for w in ladder.wrestlers],
                winner_name=winner.name,
                loser_names=[l.name for l in losers],
                rating=rating,
                stars=rating / 20,
                commentary=commentary,
                is_title_match=ladder.is_title_match,
                title_name=title_name,
                title_changed=title_changed,
                new_champion_name=new_champion_name
            )
            match_results.append(result)

            # Update all participants - winner gets a win, others get a loss
            for wrestler in ladder.wrestlers:
                is_winner = (wrestler == winner)
                # Ladder matches are more grueling
                wrestler.update_after_match(is_winner=is_winner, match_rating=rating, duration_cost=15)

            # Record match history (ladder)
            self._record_match_history(
                game_state=game_state,
                match_type=ladder.match_type,
                participant_ids=[w.id for w in ladder.wrestlers],
                participant_names=[w.name for w in ladder.wrestlers],
                winner_ids=[winner.id],
                winner_names=[winner.name],
                loser_ids=[l.id for l in losers],
                loser_names=[l.name for l in losers],
                rating=rating,
                is_title_match=ladder.is_title_match,
                title_id=ladder.title_id,
                title_name=title_name,
                title_changed=title_changed,
            )

            # Handle title reign tracking
            if ladder.is_title_match and ladder.title_id:
                if title_changed:
                    self._handle_title_change(
                        game_state=game_state,
                        title_id=ladder.title_id,
                        title_name=title_name,
                        old_holder_id=original_holder_id,
                        new_holder_id=winner.id,
                        new_holder_name=winner.name,
                        holder_type="wrestler",
                    )
                elif original_holder_id is not None:
                    # Successful title defense
                    self._record_title_defense(game_state, ladder.title_id, original_holder_id)

            total_score += rating

        # Process Iron Man matches
        for iron_man in self.iron_man_matches:
            # Track original title holder before match
            original_holder_id = None
            title_name = ""
            if iron_man.is_title_match and iron_man.title_id and game_state:
                title = next((t for t in game_state.titles if t.id == iron_man.title_id), None)
                if title:
                    original_holder_id = title.current_holder_id
                    title_name = title.name

            winner, loser, is_draw, falls_a, falls_b, fall_log, rating, commentary = iron_man.simulate()

            # Detect title change
            title_changed = False
            new_champion_name = ""
            if iron_man.is_title_match and iron_man.title_id and game_state and winner:
                title = next((t for t in game_state.titles if t.id == iron_man.title_id), None)
                if title and title.current_holder_id != original_holder_id:
                    title_changed = True
                    new_champion_name = winner.name

            result = IronManResult(
                match_type=iron_man.match_type,
                wrestler_a_name=iron_man.wrestler_a.name,
                wrestler_b_name=iron_man.wrestler_b.name,
                winner_name=winner.name if winner else "",
                loser_name=loser.name if loser else "",
                is_draw=is_draw,
                falls_a=falls_a,
                falls_b=falls_b,
                fall_log=fall_log,
                rating=rating,
                stars=rating / 20,
                commentary=commentary,
                is_title_match=iron_man.is_title_match,
                title_name=title_name,
                title_changed=title_changed,
                new_champion_name=new_champion_name
            )
            match_results.append(result)

            # Update participants - Iron Man matches are grueling
            if winner and loser:
                winner.update_after_match(is_winner=True, match_rating=rating, duration_cost=20)
                loser.update_after_match(is_winner=False, match_rating=rating, duration_cost=20)

                # Record match history (Iron Man - with winner)
                self._record_match_history(
                    game_state=game_state,
                    match_type=iron_man.match_type,
                    participant_ids=[iron_man.wrestler_a.id, iron_man.wrestler_b.id],
                    participant_names=[iron_man.wrestler_a.name, iron_man.wrestler_b.name],
                    winner_ids=[winner.id],
                    winner_names=[winner.name],
                    loser_ids=[loser.id],
                    loser_names=[loser.name],
                    rating=rating,
                    is_title_match=iron_man.is_title_match,
                    title_id=iron_man.title_id,
                    title_name=title_name,
                    title_changed=title_changed,
                )

                # Handle title reign tracking
                if iron_man.is_title_match and iron_man.title_id:
                    if title_changed:
                        self._handle_title_change(
                            game_state=game_state,
                            title_id=iron_man.title_id,
                            title_name=title_name,
                            old_holder_id=original_holder_id,
                            new_holder_id=winner.id,
                            new_holder_name=winner.name,
                            holder_type="wrestler",
                        )
                    elif original_holder_id is not None:
                        # Successful title defense
                        self._record_title_defense(game_state, iron_man.title_id, original_holder_id)
            else:
                # Draw - both get a "tie" update (no wins/losses recorded)
                iron_man.wrestler_a.update_after_match(is_winner=False, match_rating=rating, duration_cost=20)
                iron_man.wrestler_b.update_after_match(is_winner=False, match_rating=rating, duration_cost=20)

                # Record match history (Iron Man - draw, no winner/loser for streaks)
                # For draws, we don't record wins/losses to streaks
                if game_state:
                    date = {
                        "year": game_state.year,
                        "month": game_state.month,
                        "week": game_state.week,
                    }
                    entry = MatchHistoryEntry(
                        id=game_state.records.get_next_match_id(),
                        date=date,
                        show_name=self.name,
                        is_ppv=self.is_ppv,
                        match_type=iron_man.match_type,
                        participant_ids=[iron_man.wrestler_a.id, iron_man.wrestler_b.id],
                        participant_names=[iron_man.wrestler_a.name, iron_man.wrestler_b.name],
                        winner_ids=[],  # No winner in draw
                        winner_names=[],
                        loser_ids=[],  # No loser in draw
                        loser_names=[],
                        rating=rating,
                        stars=rating / 20,
                        is_title_match=iron_man.is_title_match,
                        title_id=iron_man.title_id,
                        title_name=title_name,
                        title_changed=False,  # Title doesn't change on draw
                    )
                    game_state.records.add_match(entry)

            total_score += rating

        # Process Elimination Chamber matches
        for chamber in self.chamber_matches:
            # Track original title holder before match
            original_holder_id = None
            title_name = ""
            if chamber.is_title_match and chamber.title_id and game_state:
                title = next((t for t in game_state.titles if t.id == chamber.title_id), None)
                if title:
                    original_holder_id = title.current_holder_id
                    title_name = title.name

            winner, losers, eliminations, rating, commentary = chamber.simulate()

            # Create elimination info for result
            elimination_data = []
            for elim in eliminations:
                elimination_data.append({
                    'wrestler_name': elim['wrestler'].name,
                    'eliminated_by': elim['eliminated_by'].name,
                    'entry_number': elim['entry_number'],
                    'elimination_order': elim['elimination_order']
                })

            # Detect title change
            title_changed = False
            new_champion_name = ""
            if chamber.is_title_match and chamber.title_id and game_state:
                title = next((t for t in game_state.titles if t.id == chamber.title_id), None)
                if title and title.current_holder_id != original_holder_id:
                    title_changed = True
                    new_champion_name = winner.name if winner else ""

            result = EliminationChamberResult(
                match_type=chamber.match_type,
                participant_names=[w.name for w in chamber.wrestlers],
                winner_name=winner.name,
                loser_names=[l.name for l in losers],
                eliminations=elimination_data,
                rating=rating,
                stars=rating / 20,
                commentary=commentary,
                is_title_match=chamber.is_title_match,
                title_name=title_name,
                title_changed=title_changed,
                new_champion_name=new_champion_name
            )
            match_results.append(result)

            # Update all participants - Chamber is brutal
            for wrestler in chamber.wrestlers:
                is_winner = (wrestler == winner)
                wrestler.update_after_match(is_winner=is_winner, match_rating=rating, duration_cost=20)

            # Record match history
            self._record_match_history(
                game_state=game_state,
                match_type=chamber.match_type,
                participant_ids=[w.id for w in chamber.wrestlers],
                participant_names=[w.name for w in chamber.wrestlers],
                winner_ids=[winner.id],
                winner_names=[winner.name],
                loser_ids=[l.id for l in losers],
                loser_names=[l.name for l in losers],
                rating=rating,
                is_title_match=chamber.is_title_match,
                title_id=chamber.title_id,
                title_name=title_name,
                title_changed=title_changed,
            )

            # Handle title reign tracking
            if chamber.is_title_match and chamber.title_id:
                if title_changed:
                    self._handle_title_change(
                        game_state=game_state,
                        title_id=chamber.title_id,
                        title_name=title_name,
                        old_holder_id=original_holder_id,
                        new_holder_id=winner.id,
                        new_holder_name=winner.name,
                        holder_type="wrestler",
                    )
                elif original_holder_id is not None:
                    self._record_title_defense(game_state, chamber.title_id, original_holder_id)

            total_score += rating

        # Process Money in the Bank matches
        for mitb in self.mitb_matches:
            winner, losers, rating, commentary = mitb.simulate()

            result = MoneyInTheBankResult(
                match_type=mitb.match_type,
                participant_names=[w.name for w in mitb.wrestlers],
                winner_name=winner.name,
                loser_names=[l.name for l in losers],
                rating=rating,
                stars=rating / 20,
                commentary=commentary
            )
            match_results.append(result)

            # Update all participants - MITB is grueling
            for wrestler in mitb.wrestlers:
                is_winner = (wrestler == winner)
                wrestler.update_after_match(is_winner=is_winner, match_rating=rating, duration_cost=15)

            # Record match history
            self._record_match_history(
                game_state=game_state,
                match_type=mitb.match_type,
                participant_ids=[w.id for w in mitb.wrestlers],
                participant_names=[w.name for w in mitb.wrestlers],
                winner_ids=[winner.id],
                winner_names=[winner.name],
                loser_ids=[l.id for l in losers],
                loser_names=[l.name for l in losers],
                rating=rating,
            )

            total_score += rating

        # Calculate finances
        booked_wrestlers = self.get_booked_wrestlers()
        wrestler_pay = sum(w.contract.per_appearance_fee for w in booked_wrestlers)
        avg_heat = sum(w.heat for w in booked_wrestlers) / len(booked_wrestlers) if booked_wrestlers else 0

        # Calculate final show rating
        total_matches = (len(self.matches) + len(self.rumble_matches) +
                        len(self.multi_man_matches) + len(self.ladder_matches) +
                        len(self.iron_man_matches) + len(self.chamber_matches) +
                        len(self.mitb_matches))
        final_rating = int(total_score / total_matches) if total_matches > 0 else 0

        # TV Rating
        tv_rating = calculate_tv_rating(final_rating)

        # Attendance
        attendance = calculate_attendance(
            prestige=game_state.company.prestige,
            avg_heat=avg_heat,
            is_ppv=self.is_ppv,
            viewers=game_state.company.viewers
        )

        # Revenue
        ticket_revenue, ppv_revenue = calculate_revenue(
            attendance=attendance,
            is_ppv=self.is_ppv,
            viewers=game_state.company.viewers,
            prestige=game_state.company.prestige
        )
        total_revenue = ticket_revenue + ppv_revenue
        profit = total_revenue - wrestler_pay

        # Viewer change
        viewer_change = calculate_viewer_change(
            final_rating=final_rating,
            prestige=game_state.company.prestige,
            current_viewers=game_state.company.viewers
        )

        # Prestige change
        prestige_change = calculate_prestige_change(
            final_rating=final_rating,
            current_prestige=game_state.company.prestige
        )

        # Apply changes to company
        game_state.company.bank_account += profit
        game_state.company.viewers = max(100000, game_state.company.viewers + viewer_change)
        game_state.company.prestige = max(0, min(100, game_state.company.prestige + prestige_change))

        self.is_finished = True

        return ShowResult(
            show_name=self.name,
            match_results=match_results,
            final_rating=final_rating,
            profit=profit,
            tv_rating=tv_rating,
            attendance=attendance,
            ticket_revenue=ticket_revenue,
            ppv_revenue=ppv_revenue,
            viewer_change=viewer_change,
            prestige_change=prestige_change
        )

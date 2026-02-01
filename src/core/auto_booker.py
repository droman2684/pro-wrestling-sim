"""AI Auto-Booking system for generating match card suggestions."""
import random
from dataclasses import dataclass, field
from typing import List, Optional, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from core.game_state import GameState
    from core.wrestler import Wrestler
    from core.tag_team import TagTeam
    from core.title import Title
    from core.feud import Feud
    from core.brand import Brand

from core.ranking import calculate_wrestler_rankings, calculate_tag_team_rankings


@dataclass
class MatchSuggestion:
    """A suggested match for the card."""
    match_type: str  # "singles", "tag", "triple_threat", "fatal_four_way", "ladder", "iron_man", "chamber", "mitb"
    participant_ids: List[int]  # Wrestler IDs (or TagTeam IDs for tag matches)
    reason: str  # Why this match was suggested
    is_title_match: bool = False
    title_id: Optional[int] = None
    is_steel_cage: bool = False
    time_limit: int = 30  # For iron man matches
    card_position: str = "midcard"  # "opener", "midcard", "main_event"
    estimated_rating: int = 70
    is_accepted: bool = True  # User can toggle off

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "match_type": self.match_type,
            "participant_ids": self.participant_ids,
            "reason": self.reason,
            "is_title_match": self.is_title_match,
            "title_id": self.title_id,
            "is_steel_cage": self.is_steel_cage,
            "time_limit": self.time_limit,
            "card_position": self.card_position,
            "estimated_rating": self.estimated_rating,
            "is_accepted": self.is_accepted
        }


@dataclass
class FeudSuggestion:
    """A suggested new feud to start."""
    wrestler_a_id: int
    wrestler_b_id: int
    reason: str
    storyline_hook: str

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "wrestler_a_id": self.wrestler_a_id,
            "wrestler_b_id": self.wrestler_b_id,
            "reason": self.reason,
            "storyline_hook": self.storyline_hook
        }


@dataclass
class CardSuggestion:
    """Complete card suggestion for a show."""
    show_name: str
    is_ppv: bool
    matches: List[MatchSuggestion] = field(default_factory=list)
    feud_suggestions: List[FeudSuggestion] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    estimated_rating: int = 70

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "show_name": self.show_name,
            "is_ppv": self.is_ppv,
            "matches": [m.to_dict() for m in self.matches],
            "feud_suggestions": [f.to_dict() for f in self.feud_suggestions],
            "warnings": self.warnings,
            "estimated_rating": self.estimated_rating
        }


class AutoBooker:
    """AI booking engine that generates match card suggestions."""

    def __init__(self):
        self._booked_wrestler_ids: Set[int] = set()
        self._booked_team_ids: Set[int] = set()
        self._brand_id: Optional[int] = None
        self._brand_wrestler_ids: Optional[Set[int]] = None
        self._brand_title_ids: Optional[Set[int]] = None

    def _is_wrestler_on_brand(self, wrestler_id: int) -> bool:
        """Check if a wrestler is on the current brand (or no brand filter)."""
        if self._brand_wrestler_ids is None:
            return True
        return wrestler_id in self._brand_wrestler_ids

    def _is_title_on_brand(self, title_id: int) -> bool:
        """Check if a title is on the current brand (or no brand filter)."""
        if self._brand_title_ids is None:
            return True
        return title_id in self._brand_title_ids

    def _filter_roster(self, roster: List['Wrestler']) -> List['Wrestler']:
        """Filter roster by brand if applicable."""
        if self._brand_wrestler_ids is None:
            return roster
        return [w for w in roster if w.id in self._brand_wrestler_ids]

    def _filter_tag_teams(self, teams: List['TagTeam']) -> List['TagTeam']:
        """Filter tag teams by brand (both members must be on brand)."""
        if self._brand_wrestler_ids is None:
            return teams
        return [
            t for t in teams
            if all(mid in self._brand_wrestler_ids for mid in t.member_ids)
        ]

    def _filter_titles(self, titles: List['Title']) -> List['Title']:
        """Filter titles by brand if applicable."""
        if self._brand_title_ids is None:
            return titles
        return [t for t in titles if t.id in self._brand_title_ids]

    def generate_card(
        self,
        game_state: 'GameState',
        is_ppv: bool,
        show_name: str,
        brand_id: Optional[int] = None
    ) -> CardSuggestion:
        """
        Generate a complete card suggestion for a show.

        Args:
            game_state: Current game state with roster, titles, feuds, etc.
            is_ppv: Whether this is a PPV show
            show_name: Name of the show
            brand_id: Optional brand ID to filter roster, titles, and teams

        Returns:
            CardSuggestion with matches, feud suggestions, and warnings
        """
        self._booked_wrestler_ids = set()
        self._booked_team_ids = set()
        self._brand_id = brand_id
        self._brand_wrestler_ids: Optional[Set[int]] = None
        self._brand_title_ids: Optional[Set[int]] = None

        # If brand filtering is enabled, get the brand's wrestlers and titles
        if brand_id is not None:
            brand = game_state.calendar_manager.get_brand_by_id(brand_id)
            if brand:
                self._brand_wrestler_ids = set(brand.assigned_wrestlers)
                self._brand_title_ids = set(brand.assigned_titles)

        matches: List[MatchSuggestion] = []
        warnings: List[str] = []

        # Determine target match count
        target_matches = 7 if is_ppv else 5

        # Priority 1: Blowoff matches (MANDATORY)
        blowoff_matches = self._book_blowoff_matches(game_state)
        matches.extend(blowoff_matches)

        # Priority 2: Title defenses (PPV only - ALL held titles)
        title_matches = self._book_title_matches(game_state, is_ppv, warnings)
        matches.extend(title_matches)

        # Priority 3: Tag team matches (book early to ensure they get on card)
        # On PPV: up to 2 tag matches, on TV: 1 tag match
        tag_match_target = 2 if is_ppv else 1
        if not any(m.match_type == "tag" for m in matches):
            tag_matches = self._book_tag_matches(game_state, tag_match_target)
            matches.extend(tag_matches)

        # Priority 4: Active feud matches (non-blowoff)
        feud_matches = self._book_feud_matches(game_state)
        matches.extend(feud_matches)

        # Priority 5: Rankings-based matches (leave room for variety)
        remaining = target_matches - len(matches)
        # Don't fill all remaining slots - leave at least 1 for variety on PPV
        rankings_limit = max(0, remaining - 1) if is_ppv else remaining
        if rankings_limit > 0:
            rankings_matches = self._book_rankings_matches(game_state, rankings_limit)
            matches.extend(rankings_matches)

        # Priority 6: Fill with variety
        remaining = target_matches - len(matches)
        if remaining > 0:
            variety_matches = self._fill_variety_matches(game_state, remaining, is_ppv)
            matches.extend(variety_matches)

        # Assign card positions
        self._assign_card_positions(matches)

        # Generate feud suggestions
        feud_suggestions = self._suggest_feuds(game_state)

        # Calculate estimated show rating
        estimated_rating = self._calculate_show_rating(matches)

        return CardSuggestion(
            show_name=show_name,
            is_ppv=is_ppv,
            matches=matches,
            feud_suggestions=feud_suggestions,
            warnings=warnings,
            estimated_rating=estimated_rating
        )

    def _book_blowoff_matches(self, game_state: 'GameState') -> List[MatchSuggestion]:
        """Book all feuds that have blowoff scheduled - these are mandatory."""
        matches = []

        for feud in game_state.feuds:
            if not feud.is_active or not feud.blowoff_match_scheduled:
                continue

            w_a = game_state.get_wrestler_by_id(feud.wrestler_a_id)
            w_b = game_state.get_wrestler_by_id(feud.wrestler_b_id)

            if not w_a or not w_b:
                continue

            # Skip if wrestlers not on brand (when brand filtering)
            if not self._is_wrestler_on_brand(w_a.id) or not self._is_wrestler_on_brand(w_b.id):
                continue

            if w_a.id in self._booked_wrestler_ids or w_b.id in self._booked_wrestler_ids:
                continue

            # Blood feuds get steel cage
            is_cage = feud.intensity == "blood"

            match = MatchSuggestion(
                match_type="singles",
                participant_ids=[w_a.id, w_b.id],
                reason=f"BLOWOFF MATCH - {feud.intensity.upper()} feud finale",
                is_steel_cage=is_cage,
                estimated_rating=self._estimate_match_rating(w_a, w_b, feud)
            )

            matches.append(match)
            self._booked_wrestler_ids.add(w_a.id)
            self._booked_wrestler_ids.add(w_b.id)

        return matches

    def _book_title_matches(
        self,
        game_state: 'GameState',
        is_ppv: bool,
        warnings: List[str]
    ) -> List[MatchSuggestion]:
        """Book title matches. Only on PPV - no title matches on TV shows."""
        matches = []

        # Title matches only on PPV
        if not is_ppv:
            return matches

        # Filter titles by brand
        titles = self._filter_titles(game_state.titles)

        for title in titles:
            if title.current_holder_id is None:
                # Vacant title - can't defend
                continue

            # Check if this is a tag team title (by name)
            is_tag_title = "tag" in title.name.lower()

            if is_tag_title:
                # Book as tag team title match
                tag_match = self._book_tag_title_match(game_state, title, warnings)
                if tag_match:
                    matches.append(tag_match)
            else:
                # Book as singles title match
                singles_match = self._book_singles_title_match(game_state, title, warnings)
                if singles_match:
                    matches.append(singles_match)

        return matches

    def _book_tag_title_match(
        self,
        game_state: 'GameState',
        title: 'Title',
        warnings: List[str]
    ) -> Optional[MatchSuggestion]:
        """Book a tag team title defense."""
        # Find the defending team (team containing the holder)
        defending_team = None
        # Filter tag teams by brand
        teams = self._filter_tag_teams(game_state.tag_teams)
        for team in teams:
            if team.is_active and title.current_holder_id in team.member_ids:
                defending_team = team
                break

        if not defending_team:
            warnings.append(f"No defending team found for {title.name}")
            return None

        if defending_team.id in self._booked_team_ids:
            return None

        # Check if team members are already booked
        if any(mid in self._booked_wrestler_ids for mid in defending_team.member_ids):
            return None

        # Find a challenging team (filtered by brand)
        challenger_team = None
        available_teams = [
            t for t in teams
            if t.is_active and t.id != defending_team.id
            and t.id not in self._booked_team_ids
            and t.is_available(game_state.roster)
            and all(mid not in self._booked_wrestler_ids for mid in t.member_ids)
        ]

        # Prefer ranked teams
        ranked_teams = calculate_tag_team_rankings(available_teams, game_state.roster)
        if ranked_teams:
            challenger_team = ranked_teams[0]
        elif available_teams:
            challenger_team = available_teams[0]

        if not challenger_team:
            warnings.append(f"No challenger team found for {title.name}")
            return None

        match = MatchSuggestion(
            match_type="tag",
            participant_ids=[defending_team.id, challenger_team.id],
            reason=f"{title.name} defense",
            is_title_match=True,
            title_id=title.id,
            estimated_rating=self._estimate_tag_rating(defending_team, challenger_team, game_state)
        )

        # Mark as booked
        self._booked_team_ids.add(defending_team.id)
        self._booked_team_ids.add(challenger_team.id)
        for mid in defending_team.member_ids + challenger_team.member_ids:
            self._booked_wrestler_ids.add(mid)

        return match

    def _book_singles_title_match(
        self,
        game_state: 'GameState',
        title: 'Title',
        warnings: List[str]
    ) -> Optional[MatchSuggestion]:
        """Book a singles title defense."""
        champion = game_state.get_wrestler_by_id(title.current_holder_id)
        if not champion:
            return None

        # Skip if champion not on brand (when brand filtering)
        if not self._is_wrestler_on_brand(champion.id):
            return None

        if champion.id in self._booked_wrestler_ids:
            return None

        # Find contender
        contender = self._find_contender(game_state, title, champion.id)
        if not contender:
            warnings.append(f"No contender found for {title.name}")
            return None

        if contender.id in self._booked_wrestler_ids:
            return None

        # Check for feud between champion and contender
        feud = game_state.get_feud_between(champion.id, contender.id)
        reason = f"{title.name} defense"
        if feud:
            reason += f" - {feud.intensity.upper()} feud"

        match = MatchSuggestion(
            match_type="singles",
            participant_ids=[champion.id, contender.id],
            reason=reason,
            is_title_match=True,
            title_id=title.id,
            estimated_rating=self._estimate_match_rating(champion, contender, feud)
        )

        self._booked_wrestler_ids.add(champion.id)
        self._booked_wrestler_ids.add(contender.id)

        return match

    def _book_feud_matches(self, game_state: 'GameState') -> List[MatchSuggestion]:
        """Book active feud matches that aren't blowoffs."""
        matches = []

        for feud in game_state.feuds:
            if not feud.is_active or feud.blowoff_match_scheduled:
                continue

            w_a = game_state.get_wrestler_by_id(feud.wrestler_a_id)
            w_b = game_state.get_wrestler_by_id(feud.wrestler_b_id)

            if not w_a or not w_b:
                continue

            # Skip if wrestlers not on brand (when brand filtering)
            if not self._is_wrestler_on_brand(w_a.id) or not self._is_wrestler_on_brand(w_b.id):
                continue

            if w_a.id in self._booked_wrestler_ids or w_b.id in self._booked_wrestler_ids:
                continue

            match = MatchSuggestion(
                match_type="singles",
                participant_ids=[w_a.id, w_b.id],
                reason=f"Active feud ({feud.intensity.upper()}) - Match {feud.total_matches + 1}",
                estimated_rating=self._estimate_match_rating(w_a, w_b, feud)
            )

            matches.append(match)
            self._booked_wrestler_ids.add(w_a.id)
            self._booked_wrestler_ids.add(w_b.id)

        return matches

    def _book_rankings_matches(
        self,
        game_state: 'GameState',
        count: int
    ) -> List[MatchSuggestion]:
        """Book matches based on wrestler rankings."""
        matches = []

        # Get ranked wrestlers (filtered by brand)
        roster = self._filter_roster(game_state.roster)
        rankings = calculate_wrestler_rankings(roster)
        available = [w for w in rankings if w.id not in self._booked_wrestler_ids]

        # Book top-ranked wrestlers against each other
        while len(matches) < count and len(available) >= 2:
            w_a = available[0]

            # Find opponent from remaining available
            opponent = None
            for w in available[1:]:
                # Prefer someone close in rankings
                opponent = w
                break

            if not opponent:
                break

            match = MatchSuggestion(
                match_type="singles",
                participant_ids=[w_a.id, opponent.id],
                reason=f"Rankings match - Top contenders",
                estimated_rating=self._estimate_match_rating(w_a, opponent)
            )

            matches.append(match)
            self._booked_wrestler_ids.add(w_a.id)
            self._booked_wrestler_ids.add(opponent.id)
            available = [w for w in available if w.id not in self._booked_wrestler_ids]

        return matches

    def _book_tag_matches(
        self,
        game_state: 'GameState',
        count: int
    ) -> List[MatchSuggestion]:
        """Book tag team matches."""
        matches = []

        # Get available tag teams (filtered by brand)
        all_teams = self._filter_tag_teams(game_state.tag_teams)
        available_teams = [
            t for t in all_teams
            if t.is_active and t.is_available(game_state.roster)
            and t.id not in self._booked_team_ids
            and all(mid not in self._booked_wrestler_ids for mid in t.member_ids)
        ]

        # Rank available teams
        ranked_teams = calculate_tag_team_rankings(available_teams, game_state.roster)
        if len(ranked_teams) < 2:
            # Not enough ranked teams, use unranked
            ranked_teams = available_teams

        while len(matches) < count and len(ranked_teams) >= 2:
            team_a = ranked_teams[0]
            team_b = ranked_teams[1]

            match = MatchSuggestion(
                match_type="tag",
                participant_ids=[team_a.id, team_b.id],
                reason="Tag team showcase",
                estimated_rating=self._estimate_tag_rating(team_a, team_b, game_state)
            )

            matches.append(match)
            self._booked_team_ids.add(team_a.id)
            self._booked_team_ids.add(team_b.id)
            for mid in team_a.member_ids + team_b.member_ids:
                self._booked_wrestler_ids.add(mid)

            ranked_teams = [t for t in ranked_teams if t.id not in self._booked_team_ids]

        return matches

    def _fill_variety_matches(
        self,
        game_state: 'GameState',
        count: int,
        is_ppv: bool
    ) -> List[MatchSuggestion]:
        """Fill remaining slots with variety matches."""
        matches = []

        # Filter roster by brand
        roster = self._filter_roster(game_state.roster)
        available = [
            w for w in roster
            if w.id not in self._booked_wrestler_ids
            and w.condition >= 20
            and not w.is_injured
        ]

        # Sort by overall rating descending
        available.sort(key=lambda w: w.get_overall_rating(), reverse=True)

        while len(matches) < count and len(available) >= 2:
            # Decide match type based on available wrestlers and PPV status
            match_type = "singles"
            participants = []

            # On PPV, consider multi-man matches
            if is_ppv and len(available) >= 3 and random.random() < 0.4:
                num_participants = 3 if len(available) < 4 or random.random() < 0.5 else 4
                participants = [w.id for w in available[:num_participants]]
                match_type = "triple_threat" if num_participants == 3 else "fatal_four_way"

                for w in available[:num_participants]:
                    self._booked_wrestler_ids.add(w.id)
                available = available[num_participants:]

                match = MatchSuggestion(
                    match_type=match_type,
                    participant_ids=participants,
                    reason="Card variety - multi-man action",
                    estimated_rating=self._estimate_multi_man_rating(
                        [game_state.get_wrestler_by_id(pid) for pid in participants]
                    )
                )
            else:
                # Singles match
                w_a = available[0]
                w_b = available[1]
                participants = [w_a.id, w_b.id]

                self._booked_wrestler_ids.add(w_a.id)
                self._booked_wrestler_ids.add(w_b.id)
                available = available[2:]

                match = MatchSuggestion(
                    match_type="singles",
                    participant_ids=participants,
                    reason="Card variety",
                    estimated_rating=self._estimate_match_rating(w_a, w_b)
                )

            matches.append(match)

        return matches

    def _find_contender(
        self,
        game_state: 'GameState',
        title: 'Title',
        champion_id: int
    ) -> Optional['Wrestler']:
        """Find the best contender for a title match."""
        # Filter roster by brand
        roster = self._filter_roster(game_state.roster)

        # 1. Check if champion is in a feud
        champion_feud = game_state.get_wrestler_feud(champion_id)
        if champion_feud:
            rival_id = (
                champion_feud.wrestler_b_id
                if champion_feud.wrestler_a_id == champion_id
                else champion_feud.wrestler_a_id
            )
            rival = game_state.get_wrestler_by_id(rival_id)
            if rival and rival.id not in self._booked_wrestler_ids and self._is_wrestler_on_brand(rival.id):
                return rival

        # 2. Check rankings
        rankings = calculate_wrestler_rankings(roster)
        for ranked_wrestler in rankings[:5]:
            if (ranked_wrestler.id != champion_id and
                ranked_wrestler.id not in self._booked_wrestler_ids):
                return ranked_wrestler

        # 3. Check for hot wrestlers (high heat)
        hot_wrestlers = sorted(
            [w for w in roster if w.heat >= 60],
            key=lambda w: w.heat,
            reverse=True
        )
        for hot_w in hot_wrestlers:
            if (hot_w.id != champion_id and
                hot_w.id not in self._booked_wrestler_ids):
                return hot_w

        # 4. Random from top tier (70+ overall)
        top_tier = [
            w for w in roster
            if w.get_overall_rating() >= 70
            and w.id != champion_id
            and w.id not in self._booked_wrestler_ids
        ]
        if top_tier:
            return random.choice(top_tier)

        # 5. Anyone available
        anyone = [
            w for w in roster
            if w.id != champion_id
            and w.id not in self._booked_wrestler_ids
            and w.condition >= 20
            and not w.is_injured
        ]
        if anyone:
            return random.choice(anyone)

        return None

    def _suggest_feuds(self, game_state: 'GameState') -> List[FeudSuggestion]:
        """Generate suggestions for new feuds."""
        suggestions = []

        # Get wrestlers not in feuds (filtered by brand)
        roster = self._filter_roster(game_state.roster)
        available = [
            w for w in roster
            if not game_state.is_wrestler_in_feud(w.id)
            and w.condition >= 20
            and not w.is_injured
        ]

        # 1. High heat wrestlers need feuds
        hot_wrestlers = [w for w in available if w.heat >= 70]
        for hot_w in hot_wrestlers[:2]:  # Max 2 suggestions from hot wrestlers
            # Find a rival of similar caliber
            rivals = [
                w for w in available
                if w.id != hot_w.id
                and abs(w.get_overall_rating() - hot_w.get_overall_rating()) <= 15
            ]
            if rivals:
                rival = max(rivals, key=lambda w: w.get_overall_rating())
                suggestions.append(FeudSuggestion(
                    wrestler_a_id=hot_w.id,
                    wrestler_b_id=rival.id,
                    reason=f"{hot_w.name} is over with the crowd (Heat: {hot_w.heat})",
                    storyline_hook="Battle for supremacy"
                ))
                available = [w for w in available if w.id not in [hot_w.id, rival.id]]

        # 2. Rankings-based rivalries
        rankings = calculate_wrestler_rankings(roster)
        for i in range(min(2, len(rankings) - 1)):
            w1, w2 = rankings[i], rankings[i + 1]
            if (not game_state.is_wrestler_in_feud(w1.id) and
                not game_state.is_wrestler_in_feud(w2.id)):
                # Check if already suggested
                already_suggested = any(
                    (s.wrestler_a_id == w1.id and s.wrestler_b_id == w2.id) or
                    (s.wrestler_a_id == w2.id and s.wrestler_b_id == w1.id)
                    for s in suggestions
                )
                if not already_suggested:
                    suggestions.append(FeudSuggestion(
                        wrestler_a_id=w1.id,
                        wrestler_b_id=w2.id,
                        reason=f"#{i+1} vs #{i+2} in rankings",
                        storyline_hook="Who is the better competitor?"
                    ))

        return suggestions[:3]  # Max 3 suggestions

    def _assign_card_positions(self, matches: List[MatchSuggestion]) -> None:
        """Assign opener, midcard, main_event positions."""
        if not matches:
            return

        # Sort by estimated rating
        sorted_indices = sorted(
            range(len(matches)),
            key=lambda i: matches[i].estimated_rating
        )

        # Main event: highest rated match
        matches[sorted_indices[-1]].card_position = "main_event"

        # Opener: pick a solid but not top match
        if len(matches) >= 2:
            # Find a good opener (mid-range rating)
            mid_idx = len(sorted_indices) // 2
            matches[sorted_indices[mid_idx]].card_position = "opener"

        # Rest are midcard (already default)

    def _estimate_match_rating(
        self,
        w_a: 'Wrestler',
        w_b: 'Wrestler',
        feud: Optional['Feud'] = None
    ) -> int:
        """Estimate the match rating based on wrestlers and context."""
        # Base: average of overalls
        base = (w_a.get_overall_rating() + w_b.get_overall_rating()) // 2

        # Psychology bonus
        psych_avg = (w_a.psych + w_b.psych) / 2
        psych_bonus = int(psych_avg / 10)

        # Feud bonus
        feud_bonus = 0
        if feud:
            feud_bonus = feud.get_intensity_bonus()

        # Some variance
        variance = random.randint(-5, 5)

        return min(100, max(40, base + psych_bonus + feud_bonus + variance))

    def _estimate_tag_rating(
        self,
        team_a: 'TagTeam',
        team_b: 'TagTeam',
        game_state: 'GameState'
    ) -> int:
        """Estimate tag team match rating."""
        rating_a = team_a.get_team_rating(game_state.roster)
        rating_b = team_b.get_team_rating(game_state.roster)
        base = (rating_a + rating_b) // 2

        # Chemistry bonus
        chem_bonus = (team_a.chemistry + team_b.chemistry) // 40

        variance = random.randint(-5, 5)

        return min(100, max(40, base + chem_bonus + variance))

    def _estimate_multi_man_rating(self, wrestlers: List['Wrestler']) -> int:
        """Estimate multi-man match rating."""
        if not wrestlers:
            return 60

        avg_overall = sum(w.get_overall_rating() for w in wrestlers) // len(wrestlers)
        avg_psych = sum(w.psych for w in wrestlers) // len(wrestlers)

        psych_bonus = int(avg_psych / 10)
        variance = random.randint(-5, 5)

        return min(100, max(40, avg_overall + psych_bonus + variance))

    def _calculate_show_rating(self, matches: List[MatchSuggestion]) -> int:
        """Calculate estimated overall show rating."""
        if not matches:
            return 50

        total = sum(m.estimated_rating for m in matches)
        return total // len(matches)

import random
from typing import TYPE_CHECKING, List, Optional, Tuple
from core.commentary import generate_commentary

if TYPE_CHECKING:
    from core.wrestler import Wrestler
    from core.tag_team import TagTeam
    from core.game_state import GameState
    from core.title import Title
    from core.feud import Feud
    from core.stable import Stable


def _condition_penalty(wrestlers: list) -> float:
    """
    Calculate match rating penalty based on participant condition.
    Returns a negative modifier (0 to -15) applied to final_score.
    """
    if not wrestlers:
        return 0.0
    avg_condition = sum(w.condition for w in wrestlers) / len(wrestlers)
    if avg_condition >= 50:
        return 0.0
    elif avg_condition >= 25:
        return -10.0 * (50 - avg_condition) / 25
    else:
        return -10.0 - (5.0 * (25 - avg_condition) / 25)


class Match:
    """
    Core match simulation logic.
    Determines winners and calculates match ratings.
    Supports both singles and tag team matches.
    """

    def __init__(self, wrestler_a: 'Wrestler' = None, wrestler_b: 'Wrestler' = None,
                 match_type: str = "Singles",
                 team_a: 'TagTeam' = None, team_b: 'TagTeam' = None,
                 roster: List['Wrestler'] = None,
                 is_steel_cage: bool = False,
                 is_title_match: bool = False,
                 title_id: Optional[int] = None,
                 game_state: 'GameState' = None):
        self.match_type = match_type
        self.rating = 0
        self.is_steel_cage = is_steel_cage
        self.is_title_match = is_title_match
        self.title_id = title_id
        self.game_state = game_state
        self.feud: Optional['Feud'] = None

        # Singles match attributes
        self.p1 = wrestler_a
        self.p2 = wrestler_b
        self.winner = None
        self.loser = None

        # Tag team match attributes
        self.team_a = team_a
        self.team_b = team_b
        self.roster = roster or []
        self.winning_team = None
        self.losing_team = None
        self.pinned_wrestler = None

        # Interference tracking
        self.interference_occurred = False
        self.interference_by: Optional[str] = None  # Stable name
        self.interference_helped = False  # True = helped, False = DQ backfire
        self.interference_beneficiary: Optional['Wrestler'] = None  # Who the interference was for

    def simulate(self) -> Tuple[
        Optional['Wrestler'], Optional['Wrestler'], Optional['TagTeam'], Optional['TagTeam'], Optional['Wrestler'], int, List[str]
    ]:
        """
        Runs the match simulation logic.
        Returns match results including commentary.
        """
        if self.match_type == "Tag Team":
            self._determine_tag_winner()
            self._calculate_tag_match_rating()
            team_a_name = self.team_a.name if self.team_a else "Team A"
            team_b_name = self.team_b.name if self.team_b else "Team B"
            
            winner_name = self.winning_team.name if self.winning_team else None
            # Tag finish logic could be improved, but for now generic finish
            
            match_commentary = generate_commentary(
                team_a_name, team_b_name, self.rating, 
                is_steel_cage=self.is_steel_cage,
                winner_name=winner_name
            )
            
            if self.is_title_match:
                self._handle_title_change()
            return (None, None, self.winning_team, self.losing_team, self.pinned_wrestler, self.rating, match_commentary)
        else:
            self._determine_winner()
            self._calculate_match_rating()
            feud_intensity = self.feud.intensity if self.feud and self.feud.is_active else ""
            
            winner_name = self.winner.name if self.winner else None
            finisher_name = None
            if self.winner:
                finisher = self.winner.get_primary_finisher()
                if finisher:
                    finisher_name = finisher["name"]

            match_commentary = generate_commentary(
                self.p1.name, self.p2.name, self.rating, 
                wrestler_a_style=self.p1.primary_style,
                wrestler_b_style=self.p2.primary_style,
                is_steel_cage=self.is_steel_cage, 
                feud_intensity=feud_intensity,
                winner_name=winner_name,
                finisher_name=finisher_name
            )
            
            if self.is_title_match:
                self._handle_title_change()
            return (self.winner, self.loser, None, None, None, self.rating, match_commentary)

    def _determine_winner(self) -> None:
        """
        Decides the winner based on Overall Rating + Variance.
        This allows for upsets.
        Includes stable interference mechanics.
        """
        score_p1 = self.p1.get_overall_rating() + random.randint(-10, 10)
        score_p2 = self.p2.get_overall_rating() + random.randint(-10, 10)

        # Check for stable interference (only in singles matches with game_state)
        if self.game_state:
            self._check_stable_interference(score_p1, score_p2)

        # If interference resulted in DQ, winner was already set
        if self.interference_occurred and not self.interference_helped:
            # DQ loss - the stable member loses
            return

        # Apply interference modifier if it helped
        if self.interference_occurred and self.interference_helped:
            if self.interference_beneficiary == self.p1:
                score_p2 -= 5  # Opponent distracted
            else:
                score_p1 -= 5  # Opponent distracted

        if score_p1 >= score_p2:
            self.winner = self.p1
            self.loser = self.p2
        else:
            self.winner = self.p2
            self.loser = self.p1

    def _check_stable_interference(self, score_p1: int, score_p2: int) -> None:
        """
        Check if stable interference occurs in this match.
        - 20% base chance (higher if losing)
        - 70% helps stable member (distraction)
        - 30% backfires (DQ loss for stable member)
        """
        # Get stables for both wrestlers
        p1_stable = self.game_state.get_wrestler_stable(self.p1.id)
        p2_stable = self.game_state.get_wrestler_stable(self.p2.id)

        # No interference if neither wrestler is in a stable
        if not p1_stable and not p2_stable:
            return

        # Determine which stable might interfere (prefer the one that's losing)
        interfering_stable = None
        beneficiary = None

        if p1_stable and p2_stable:
            # Both in stables - the one losing is more likely to get help
            if score_p1 < score_p2:
                interfering_stable = p1_stable
                beneficiary = self.p1
            else:
                interfering_stable = p2_stable
                beneficiary = self.p2
        elif p1_stable:
            interfering_stable = p1_stable
            beneficiary = self.p1
        else:
            interfering_stable = p2_stable
            beneficiary = self.p2

        # Calculate interference chance
        # 20% base, +20% if the stable member is losing
        base_chance = 0.20
        is_losing = (beneficiary == self.p1 and score_p1 < score_p2) or \
                    (beneficiary == self.p2 and score_p2 < score_p1)
        if is_losing:
            base_chance += 0.20

        # Roll for interference
        if random.random() > base_chance:
            return  # No interference

        # Interference happens!
        self.interference_occurred = True
        self.interference_by = interfering_stable.name
        self.interference_beneficiary = beneficiary

        # 70% chance it helps, 30% chance it backfires (DQ)
        if random.random() < 0.70:
            # Interference helps!
            self.interference_helped = True
        else:
            # Backfires - DQ loss for the stable member
            self.interference_helped = False
            if beneficiary == self.p1:
                self.winner = self.p2
                self.loser = self.p1
            else:
                self.winner = self.p1
                self.loser = self.p2

    def _determine_tag_winner(self) -> None:
        """
        Decides the winning tag team based on team ratings + variance.
        Also determines which wrestler gets pinned.
        """
        score_a = self.team_a.get_team_rating(self.roster) + random.randint(-10, 10)
        score_b = self.team_b.get_team_rating(self.roster) + random.randint(-10, 10)

        if score_a >= score_b:
            self.winning_team = self.team_a
            self.losing_team = self.team_b
        else:
            self.winning_team = self.team_b
            self.losing_team = self.team_a

        # Determine who gets pinned (random member of losing team)
        losing_members = self.losing_team.get_members(self.roster)
        if losing_members:
            self.pinned_wrestler = random.choice(losing_members)

    def _handle_title_change(self):
        """Updates the title holder if a title change occurred."""
        if not self.is_title_match or not self.game_state:
            return

        title = next((t for t in self.game_state.titles if t.id == self.title_id), None)
        if not title:
            return

        if self.match_type == "Tag Team":
            if self.winning_team:
                title.current_holder_id = self.winning_team.id
        else:
            if self.winner:
                title.current_holder_id = self.winner.id


    def _calculate_match_rating(self) -> None:
        """
        The Secret Sauce: How good was the match?
        Formula: (Avg Workrate + Avg Psychology) * CrowdModifier
        """
        # Base Workrate (Physical Action)
        work_p1 = (self.p1.brawl + self.p1.tech + self.p1.air) / 3
        work_p2 = (self.p2.brawl + self.p2.tech + self.p2.air) / 3

        # Psychology (The "Glue" that holds the match together)
        psych_avg = (self.p1.psych + self.p2.psych) / 2

        # Base Score Calculation
        base_score = (work_p1 + work_p2 + psych_avg + psych_avg) / 4

        # Crowd Heat / Charisma Bonus
        charisma_bonus = (self.p1.charisma + self.p2.charisma) / 10

        final_score = base_score + charisma_bonus

        # Steel Cage bonus
        if self.is_steel_cage:
            final_score += 5 # Rating bump for Steel Cage
        
        # Title match bonus
        if self.is_title_match:
            final_score += 5

        # Feud bonus
        if self.feud and self.feud.is_active:
            final_score += self.feud.get_intensity_bonus()

        # Interference modifier
        if self.interference_occurred:
            if self.interference_helped:
                final_score += 3  # Clean interference adds drama
            else:
                final_score -= 5  # DQ finish is a cheap ending

        # Condition penalty (fatigued wrestlers perform worse)
        final_score += _condition_penalty([self.p1, self.p2])

        # The "Random Chaos" Factor (Botches or Magic Moments)
        rng = random.uniform(0.9, 1.1)
        final_score = final_score * rng

        # Cap at 100 (5 Stars)
        self.rating = min(100, max(0, int(final_score)))

    def _calculate_tag_match_rating(self) -> None:
        """
        Calculate match rating for tag team matches.
        Uses average of all 4 wrestlers + chemistry bonus/penalty.
        """
        members_a = self.team_a.get_members(self.roster)
        members_b = self.team_b.get_members(self.roster)
        all_wrestlers = members_a + members_b

        if len(all_wrestlers) != 4:
            self.rating = 50  # Default if something's wrong
            return

        # Average workrate across all 4 wrestlers
        total_work = sum((w.brawl + w.tech + w.air) / 3 for w in all_wrestlers)
        avg_work = total_work / 4

        # Average psychology
        avg_psych = sum(w.psych for w in all_wrestlers) / 4
        
        # Base score
        base_score = (avg_work + avg_psych) / 2

        # Average charisma bonus
        avg_charisma = sum(w.charisma for w in all_wrestlers) / 4
        charisma_bonus = avg_charisma / 10

        # Chemistry modifier (averaged between both teams)
        avg_chemistry = (self.team_a.chemistry + self.team_b.chemistry) / 2

        # Chemistry bonus/penalty: +5 at 80+, -5 at 20-
        if avg_chemistry >= 80:
            chemistry_modifier = 5
        elif avg_chemistry <= 20:
            chemistry_modifier = -5
        else:
            chemistry_modifier = 0

        final_score = base_score + charisma_bonus + chemistry_modifier

        # Steel Cage bonus
        if self.is_steel_cage:
            final_score += 5 # Rating bump for Steel Cage

        # Title match bonus
        if self.is_title_match:
            final_score += 5

        # Condition penalty
        final_score += _condition_penalty(all_wrestlers)

        # Random chaos factor
        rng = random.uniform(0.9, 1.1)
        final_score = final_score * rng

        # Cap at 100
        self.rating = min(100, max(0, int(final_score)))


class MultiManMatch:
    """
    Multi-man match simulation (Triple Threat, Fatal 4-Way).
    All wrestlers compete simultaneously, first pinfall wins.
    """

    def __init__(self, wrestlers: List['Wrestler'], game_state: 'GameState' = None,
                 is_title_match: bool = False, title_id: Optional[int] = None):
        """
        wrestlers: List of 3-4 Wrestler objects
        """
        if len(wrestlers) < 3 or len(wrestlers) > 4:
            raise ValueError("Multi-man match requires 3-4 wrestlers")

        self.wrestlers = wrestlers
        self.game_state = game_state
        self.is_title_match = is_title_match
        self.title_id = title_id

        self.match_type = "Triple Threat" if len(wrestlers) == 3 else "Fatal 4-Way"
        self.winner: Optional['Wrestler'] = None
        self.losers: List['Wrestler'] = []
        self.pinned_wrestler: Optional['Wrestler'] = None
        self.rating = 0
        self.commentary: List[str] = []

    def simulate(self):
        """
        Run the multi-man match simulation.
        Returns (winner, losers, pinned_wrestler, rating, commentary)
        """
        # Calculate score for each wrestler
        scores = []
        for wrestler in self.wrestlers:
            # Base score: overall rating + random variance
            base = wrestler.get_overall_rating()
            rng = random.randint(-15, 15)
            # Multi-man matches favor high psychology (chaos management)
            psych_bonus = wrestler.psych / 20
            score = base + rng + psych_bonus
            scores.append((wrestler, score))

        # Sort by score - highest wins, lowest gets pinned
        scores.sort(key=lambda x: x[1], reverse=True)

        self.winner = scores[0][0]
        self.pinned_wrestler = scores[-1][0]
        self.losers = [s[0] for s in scores[1:]]

        # Generate commentary
        names = [w.name for w in self.wrestlers]
        self.commentary.append(f"{self.match_type}: {' vs '.join(names)}")
        self.commentary.append(f"All {len(self.wrestlers)} competitors battling for supremacy!")

        # Mid-match highlights
        highlight_wrestler = random.choice(self.wrestlers)
        highlights = [
            f"{highlight_wrestler.name} with a huge move that takes out multiple opponents!",
            f"Near fall! {random.choice(self.losers).name} almost steals the victory!",
            f"The action is non-stop in this {self.match_type}!",
        ]
        self.commentary.append(random.choice(highlights))

        # Finish
        self.commentary.append(f"{self.winner.name} pins {self.pinned_wrestler.name} for the win!")

        # Calculate rating
        self._calculate_rating()

        # Handle title change
        if self.is_title_match and self.title_id and self.game_state:
            title = next((t for t in self.game_state.titles if t.id == self.title_id), None)
            if title:
                title.current_holder_id = self.winner.id

        return (self.winner, self.losers, self.pinned_wrestler, self.rating, self.commentary)

    def _calculate_rating(self):
        """Calculate match rating based on all participants."""
        n = len(self.wrestlers)

        # Average workrate
        total_work = sum((w.brawl + w.tech + w.air) / 3 for w in self.wrestlers)
        avg_work = total_work / n

        # Average psychology (extra important in multi-man)
        avg_psych = sum(w.psych for w in self.wrestlers) / n

        # Base score weighted toward psychology
        base_score = (avg_work + avg_psych * 1.5) / 2.5

        # Average charisma bonus
        avg_charisma = sum(w.charisma for w in self.wrestlers) / n
        charisma_bonus = avg_charisma / 10

        # Multi-man match bonus (more action, more spots)
        match_bonus = 3 if self.match_type == "Triple Threat" else 5

        # Title match bonus
        title_bonus = 5 if self.is_title_match else 0

        final_score = base_score + charisma_bonus + match_bonus + title_bonus

        # Condition penalty
        final_score += _condition_penalty(self.wrestlers)

        # Random chaos factor
        rng = random.uniform(0.9, 1.1)
        final_score = final_score * rng

        self.rating = min(100, max(0, int(final_score)))


class IronManMatch:
    """
    Iron Man match simulation.
    Timed match where the wrestler with the most falls wins.
    """

    def __init__(self, wrestler_a: 'Wrestler', wrestler_b: 'Wrestler',
                 time_limit: int = 30, game_state: 'GameState' = None,
                 is_title_match: bool = False, title_id: Optional[int] = None):
        """
        time_limit: Match duration in minutes (default 30)
        """
        self.wrestler_a = wrestler_a
        self.wrestler_b = wrestler_b
        self.time_limit = time_limit
        self.game_state = game_state
        self.is_title_match = is_title_match
        self.title_id = title_id

        self.match_type = f"{time_limit}-Minute Iron Man Match"
        self.winner: Optional['Wrestler'] = None
        self.loser: Optional['Wrestler'] = None
        self.is_draw = False
        self.falls_a = 0
        self.falls_b = 0
        self.fall_log: List[dict] = []  # {wrestler, time, type}
        self.rating = 0
        self.commentary: List[str] = []

    def simulate(self):
        """
        Run the Iron Man match simulation.
        Returns (winner, loser, is_draw, falls_a, falls_b, fall_log, rating, commentary)
        """
        # Commentary start
        self.commentary.append(f"{self.match_type}: {self.wrestler_a.name} vs {self.wrestler_b.name}")
        self.commentary.append(f"The clock is set for {self.time_limit} minutes!")

        # Simulate falls over the time period
        # Number of fall opportunities based on time limit and wrestlers' stamina
        avg_stamina = (self.wrestler_a.stamina + self.wrestler_b.stamina) / 2
        num_fall_chances = max(3, int(self.time_limit / 10) + int(avg_stamina / 40))

        current_time = 0
        time_per_segment = self.time_limit / (num_fall_chances + 1)

        for i in range(num_fall_chances):
            current_time += time_per_segment

            # Determine if a fall happens and who scores
            # Factors: overall rating, psychology (pacing), stamina (endurance in long match)
            score_a = self.wrestler_a.get_overall_rating() + random.randint(-15, 15)
            score_b = self.wrestler_b.get_overall_rating() + random.randint(-15, 15)

            # Stamina bonus becomes more important as time goes on
            time_factor = current_time / self.time_limit
            score_a += self.wrestler_a.stamina * time_factor * 0.2
            score_b += self.wrestler_b.stamina * time_factor * 0.2

            # Psychology bonus (working the match)
            score_a += self.wrestler_a.psych / 10
            score_b += self.wrestler_b.psych / 10

            # Only score a fall if there's a big enough gap (close = no fall)
            score_diff = abs(score_a - score_b)
            if random.random() < (score_diff / 100):
                fall_time = int(current_time)
                fall_type = random.choice(["pinfall", "submission"])

                if score_a > score_b:
                    self.falls_a += 1
                    self.fall_log.append({
                        'wrestler': self.wrestler_a.name,
                        'time': fall_time,
                        'type': fall_type,
                        'score': f"{self.falls_a}-{self.falls_b}"
                    })
                    self.commentary.append(f"[{fall_time}:00] {self.wrestler_a.name} scores via {fall_type}! ({self.falls_a}-{self.falls_b})")
                else:
                    self.falls_b += 1
                    self.fall_log.append({
                        'wrestler': self.wrestler_b.name,
                        'time': fall_time,
                        'type': fall_type,
                        'score': f"{self.falls_a}-{self.falls_b}"
                    })
                    self.commentary.append(f"[{fall_time}:00] {self.wrestler_b.name} scores via {fall_type}! ({self.falls_a}-{self.falls_b})")

        # Determine winner
        self.commentary.append(f"TIME! Final score: {self.wrestler_a.name} {self.falls_a} - {self.falls_b} {self.wrestler_b.name}")

        if self.falls_a > self.falls_b:
            self.winner = self.wrestler_a
            self.loser = self.wrestler_b
            self.commentary.append(f"{self.winner.name} WINS the Iron Man Match!")
        elif self.falls_b > self.falls_a:
            self.winner = self.wrestler_b
            self.loser = self.wrestler_a
            self.commentary.append(f"{self.winner.name} WINS the Iron Man Match!")
        else:
            self.is_draw = True
            self.commentary.append("IT'S A DRAW! Neither wrestler could gain the advantage!")

        # Calculate rating
        self._calculate_rating()

        # Handle title change (only if there's a winner)
        if self.is_title_match and self.title_id and self.game_state and self.winner:
            title = next((t for t in self.game_state.titles if t.id == self.title_id), None)
            if title:
                title.current_holder_id = self.winner.id

        return (self.winner, self.loser, self.is_draw, self.falls_a, self.falls_b,
                self.fall_log, self.rating, self.commentary)

    def _calculate_rating(self):
        """Calculate match rating - Iron Man matches reward psychology and stamina."""
        # Base workrate average
        work_a = (self.wrestler_a.brawl + self.wrestler_a.tech + self.wrestler_a.air) / 3
        work_b = (self.wrestler_b.brawl + self.wrestler_b.tech + self.wrestler_b.air) / 3
        avg_work = (work_a + work_b) / 2

        # Psychology heavily weighted (working a long match)
        avg_psych = (self.wrestler_a.psych + self.wrestler_b.psych) / 2

        # Stamina important for long matches
        avg_stamina = (self.wrestler_a.stamina + self.wrestler_b.stamina) / 2

        base_score = (avg_work + avg_psych * 1.5 + avg_stamina * 0.5) / 3

        # Charisma bonus
        avg_charisma = (self.wrestler_a.charisma + self.wrestler_b.charisma) / 2
        charisma_bonus = avg_charisma / 10

        # Iron Man bonus (epic match feel)
        iron_man_bonus = 8

        # More falls = more drama = higher rating
        total_falls = self.falls_a + self.falls_b
        falls_bonus = min(10, total_falls * 2)

        # Title match bonus
        title_bonus = 5 if self.is_title_match else 0

        final_score = base_score + charisma_bonus + iron_man_bonus + falls_bonus + title_bonus

        # Condition penalty
        final_score += _condition_penalty([self.wrestler_a, self.wrestler_b])

        # Random chaos factor
        rng = random.uniform(0.9, 1.1)
        final_score = final_score * rng

        self.rating = min(100, max(0, int(final_score)))


class LadderMatch:
    """
    Ladder match simulation.
    Win by climbing the ladder and retrieving the prize.
    Favors high-flyers and risk-takers.
    """

    def __init__(self, wrestlers: List['Wrestler'], game_state: 'GameState' = None,
                 is_title_match: bool = False, title_id: Optional[int] = None):
        """
        wrestlers: List of 2+ Wrestler objects
        """
        if len(wrestlers) < 2:
            raise ValueError("Ladder match requires at least 2 wrestlers")

        self.wrestlers = wrestlers
        self.game_state = game_state
        self.is_title_match = is_title_match
        self.title_id = title_id

        # Determine match type name based on participant count
        if len(wrestlers) == 2:
            self.match_type = "Ladder Match"
        elif len(wrestlers) <= 4:
            self.match_type = f"{len(wrestlers)}-Way Ladder Match"
        else:
            self.match_type = "Money in the Bank Ladder Match"

        self.winner: Optional['Wrestler'] = None
        self.losers: List['Wrestler'] = []
        self.rating = 0
        self.commentary: List[str] = []

    def simulate(self):
        """
        Run the ladder match simulation.
        Returns (winner, losers, rating, commentary)
        """
        # Calculate score for each wrestler
        # Ladder matches favor: Air (climbing), Psychology (timing), Stamina (endurance)
        scores = []
        for wrestler in self.wrestlers:
            base = wrestler.get_overall_rating()
            # Air bonus (climbing ability)
            air_bonus = wrestler.air / 10
            # Psychology (timing the climb)
            psych_bonus = wrestler.psych / 15
            # Random variance (high risk = high variance)
            rng = random.randint(-20, 20)
            score = base + air_bonus + psych_bonus + rng
            scores.append((wrestler, score))

        # Sort by score - highest wins
        scores.sort(key=lambda x: x[1], reverse=True)

        self.winner = scores[0][0]
        self.losers = [s[0] for s in scores[1:]]

        # Generate commentary
        names = [w.name for w in self.wrestlers]
        self.commentary.append(f"{self.match_type}: {' vs '.join(names)}")
        self.commentary.append("The ladder is set up in the center of the ring!")

        # Dramatic moments
        dramatic_wrestler = random.choice(self.wrestlers)
        drama_options = [
            f"{dramatic_wrestler.name} takes a huge dive off the ladder!",
            f"{dramatic_wrestler.name} pushes the ladder over with their opponent on top!",
            f"Both wrestlers trading blows on top of the ladder!",
            f"{random.choice(self.losers).name} with a HUGE spot off the ladder!",
            f"The ladder is bent in half from the punishment!",
        ]
        self.commentary.append(random.choice(drama_options))
        self.commentary.append(random.choice(drama_options))  # Two big spots

        # Finish
        self.commentary.append(f"{self.winner.name} climbs the ladder and retrieves the prize!")

        # Calculate rating
        self._calculate_rating()

        # Handle title change
        if self.is_title_match and self.title_id and self.game_state:
            title = next((t for t in self.game_state.titles if t.id == self.title_id), None)
            if title:
                title.current_holder_id = self.winner.id

        return (self.winner, self.losers, self.rating, self.commentary)

    def _calculate_rating(self):
        """Calculate match rating - ladder matches get bonus for spectacle."""
        n = len(self.wrestlers)

        # Average workrate (Air weighted heavily)
        total_work = sum((w.brawl + w.tech + w.air * 2) / 4 for w in self.wrestlers)
        avg_work = total_work / n

        # Psychology average
        avg_psych = sum(w.psych for w in self.wrestlers) / n

        base_score = (avg_work + avg_psych) / 2

        # Average charisma bonus
        avg_charisma = sum(w.charisma for w in self.wrestlers) / n
        charisma_bonus = avg_charisma / 10

        # Ladder match bonus (spectacle)
        ladder_bonus = 8

        # More wrestlers = more chaos = slightly higher rating
        participant_bonus = (n - 2) * 2

        # Title match bonus
        title_bonus = 5 if self.is_title_match else 0

        final_score = base_score + charisma_bonus + ladder_bonus + participant_bonus + title_bonus

        # Condition penalty
        final_score += _condition_penalty(self.wrestlers)

        # Random chaos factor (higher variance for ladder matches)
        rng = random.uniform(0.85, 1.15)
        final_score = final_score * rng

        self.rating = min(100, max(0, int(final_score)))


class EliminationChamberMatch:
    """
    Elimination Chamber match simulation.
    6 wrestlers compete - 2 start in the ring, 4 in pods.
    Pod releases at timed intervals. Last wrestler standing wins.
    Brutal match that favors stamina and brawling.
    """

    def __init__(self, wrestlers: List['Wrestler'], game_state: 'GameState' = None,
                 is_title_match: bool = False, title_id: Optional[int] = None):
        """
        wrestlers: List of 6 Wrestler objects in entry order (index 0-1 start, 2-5 in pods)
        """
        if len(wrestlers) != 6:
            raise ValueError("Elimination Chamber requires exactly 6 wrestlers")

        self.wrestlers = wrestlers  # Entry order
        self.game_state = game_state
        self.is_title_match = is_title_match
        self.title_id = title_id

        self.match_type = "Elimination Chamber"
        self.eliminations: List[dict] = []  # {wrestler, eliminated_by, entry_number, elimination_order}
        self.winner: Optional['Wrestler'] = None
        self.losers: List['Wrestler'] = []
        self.rating = 0
        self.commentary: List[str] = []

    def simulate(self):
        """
        Run the Elimination Chamber simulation.
        Returns (winner, losers, eliminations, rating, commentary)
        """
        # Track active wrestlers in the ring
        # Each wrestler has: wrestler object, entry_number, damage_taken
        active = []

        # Entry 1 and 2 start in the ring
        active.append({'wrestler': self.wrestlers[0], 'entry': 1, 'damage': 0})
        active.append({'wrestler': self.wrestlers[1], 'entry': 2, 'damage': 0})

        self.commentary.append(f"ELIMINATION CHAMBER: 6 wrestlers, one survivor!")
        self.commentary.append(f"#{1} {self.wrestlers[0].name} and #{2} {self.wrestlers[1].name} start the match!")

        next_pod = 2  # Next pod to release (index)
        pod_interval = 0  # Cycles between releases

        # Simulate until one remains
        while len(active) > 1:
            pod_interval += 1

            # Release next pod every 2-3 cycles
            if next_pod < 6 and pod_interval >= 2:
                new_wrestler = self.wrestlers[next_pod]
                entry_num = next_pod + 1
                active.append({'wrestler': new_wrestler, 'entry': entry_num, 'damage': 0})
                self.commentary.append(f"POD #{entry_num} OPENS! {new_wrestler.name} enters the Chamber!")
                next_pod += 1
                pod_interval = 0

            # Apply damage to all active wrestlers (chamber is brutal)
            for w in active:
                # Earlier entrants take more cumulative damage
                w['damage'] += random.randint(5, 15)

            # Attempt elimination if more than 1 wrestler and we have 3+ in ring
            if len(active) > 1 and (len(active) >= 3 or random.random() < 0.3):
                # Calculate survival scores
                scores = []
                for w in active:
                    wrestler = w['wrestler']
                    # Base survival: stamina + brawl (chamber is brutal)
                    base = (wrestler.stamina * 1.5 + wrestler.brawl + wrestler.psych) / 3.5
                    # Damage penalty
                    damage_penalty = w['damage'] * 0.5
                    # Random factor
                    rng = random.randint(-15, 15)
                    survival_score = base - damage_penalty + rng
                    scores.append((w, survival_score))

                # Lowest score gets eliminated
                scores.sort(key=lambda x: x[1])
                eliminated = scores[0][0]

                # Pick who eliminated them (someone with high brawl from remaining)
                remaining = [s[0] for s in scores[1:]]
                # Weighted toward high brawl wrestlers
                eliminator_scores = [(r, r['wrestler'].brawl + random.randint(0, 20)) for r in remaining]
                eliminator_scores.sort(key=lambda x: x[1], reverse=True)
                eliminator = eliminator_scores[0][0]

                self.eliminations.append({
                    'wrestler': eliminated['wrestler'],
                    'eliminated_by': eliminator['wrestler'],
                    'entry_number': eliminated['entry'],
                    'elimination_order': len(self.eliminations) + 1
                })

                self.commentary.append(
                    f"ELIMINATED! {eliminated['wrestler'].name} (#{eliminated['entry']}) eliminated by {eliminator['wrestler'].name}!"
                )

                active.remove(eliminated)

        # Winner is the last one standing
        self.winner = active[0]['wrestler']
        self.losers = [e['wrestler'] for e in self.eliminations]
        self.commentary.append(f"{self.winner.name} survives the Elimination Chamber!")

        # Calculate match rating
        self._calculate_rating()

        # Handle title change
        if self.is_title_match and self.title_id and self.game_state:
            title = next((t for t in self.game_state.titles if t.id == self.title_id), None)
            if title:
                title.current_holder_id = self.winner.id

        return (self.winner, self.losers, self.eliminations, self.rating, self.commentary)

    def _calculate_rating(self):
        """Calculate match rating - Chamber matches are brutal spectacles."""
        # Average brawl (chamber is physical)
        total_brawl = sum(w.brawl for w in self.wrestlers)
        avg_brawl = total_brawl / 6

        # Average stamina (endurance matters)
        total_stamina = sum(w.stamina for w in self.wrestlers)
        avg_stamina = total_stamina / 6

        # Average psychology (working together in chaos)
        total_psych = sum(w.psych for w in self.wrestlers)
        avg_psych = total_psych / 6

        # Average charisma
        total_charisma = sum(w.charisma for w in self.wrestlers)
        avg_charisma = total_charisma / 6

        base_score = (avg_brawl + avg_stamina + avg_psych) / 3
        charisma_bonus = avg_charisma / 10

        # Elimination Chamber bonus (massive spectacle)
        chamber_bonus = 12

        # Title match bonus
        title_bonus = 5 if self.is_title_match else 0

        final_score = base_score + charisma_bonus + chamber_bonus + title_bonus

        # Condition penalty
        final_score += _condition_penalty(self.wrestlers)

        # Random chaos factor
        rng = random.uniform(0.9, 1.1)
        final_score = final_score * rng

        self.rating = min(100, max(0, int(final_score)))


class MoneyInTheBankMatch:
    """
    Money in the Bank ladder match simulation.
    6-8 wrestlers compete to climb a ladder and retrieve a briefcase.
    Winner gets a contract for a future title shot anytime.
    High-risk, high-reward match that favors Air stat.
    """

    def __init__(self, wrestlers: List['Wrestler'], game_state: 'GameState' = None):
        """
        wrestlers: List of 6-8 Wrestler objects
        """
        if len(wrestlers) < 6 or len(wrestlers) > 8:
            raise ValueError("Money in the Bank requires 6-8 wrestlers")

        self.wrestlers = wrestlers
        self.game_state = game_state

        self.match_type = "Money in the Bank"
        self.winner: Optional['Wrestler'] = None
        self.losers: List['Wrestler'] = []
        self.rating = 0
        self.commentary: List[str] = []
        self.highlight_spots: List[str] = []

    def simulate(self):
        """
        Run the Money in the Bank simulation.
        Returns (winner, losers, rating, commentary)
        """
        # Calculate score for each wrestler
        # MITB matches heavily favor: Air (climbing), Psychology (timing), Risk-taking
        scores = []
        for wrestler in self.wrestlers:
            base = wrestler.get_overall_rating()
            # Air bonus (climbing ability) - very important
            air_bonus = wrestler.air / 5
            # Psychology (timing the climb)
            psych_bonus = wrestler.psych / 10
            # Charisma bonus (big moments)
            charisma_bonus = wrestler.charisma / 15
            # High variance - anything can happen
            rng = random.randint(-25, 25)
            score = base + air_bonus + psych_bonus + charisma_bonus + rng
            scores.append((wrestler, score))

        # Sort by score - highest wins
        scores.sort(key=lambda x: x[1], reverse=True)

        self.winner = scores[0][0]
        self.losers = [s[0] for s in scores[1:]]

        # Generate commentary
        names = [w.name for w in self.wrestlers]
        self.commentary.append(f"MONEY IN THE BANK LADDER MATCH!")
        self.commentary.append(f"Competitors: {', '.join(names)}")
        self.commentary.append("The briefcase hangs high above the ring!")

        # Generate highlight spots
        spot_wrestlers = random.sample(self.wrestlers, min(4, len(self.wrestlers)))
        spot_templates = [
            "{name} takes a HUGE dive off the ladder onto everyone outside!",
            "{name} is pushed off a 20-foot ladder through the announce table!",
            "Two ladders collapse with {name} caught in between!",
            "{name} with a SUNSET FLIP POWERBOMB off the ladder!",
            "{name} lands a flying elbow off the top of the ladder!",
            "The ladder breaks in half under {name}'s weight!",
            "{name} gets knocked off the ladder through a table at ringside!",
            "All {count} competitors are down after a massive ladder collapse!",
        ]

        for i, w in enumerate(spot_wrestlers):
            spot = random.choice(spot_templates)
            if "{count}" in spot:
                self.commentary.append(spot.format(count=len(self.wrestlers)))
            else:
                self.commentary.append(spot.format(name=w.name))

        # Final climb
        # Sometimes there's a contested finish
        runner_up = scores[1][0]
        if random.random() < 0.4:
            self.commentary.append(f"{self.winner.name} and {runner_up.name} are both climbing!")
            self.commentary.append(f"{self.winner.name} knocks {runner_up.name} off and grabs the briefcase!")
        else:
            self.commentary.append(f"{self.winner.name} climbs the ladder with no one to stop them!")

        self.commentary.append(f"{self.winner.name} WINS MONEY IN THE BANK!")
        self.commentary.append(f"{self.winner.name} now has a guaranteed title shot anytime, anywhere!")

        # Calculate rating
        self._calculate_rating()

        # Mark the winner as MITB holder in game state
        if self.game_state and self.winner:
            self.winner.has_mitb_briefcase = True

        return (self.winner, self.losers, self.rating, self.commentary)

    def _calculate_rating(self):
        """Calculate match rating - MITB is a career-defining spectacle."""
        n = len(self.wrestlers)

        # Air stat is king in ladder matches
        total_air = sum(w.air for w in self.wrestlers)
        avg_air = total_air / n

        # Average workrate
        total_work = sum((w.brawl + w.tech + w.air) / 3 for w in self.wrestlers)
        avg_work = total_work / n

        # Psychology
        avg_psych = sum(w.psych for w in self.wrestlers) / n

        # Weighted toward Air
        base_score = (avg_air * 1.5 + avg_work + avg_psych) / 3.5

        # Average charisma bonus
        avg_charisma = sum(w.charisma for w in self.wrestlers) / n
        charisma_bonus = avg_charisma / 10

        # MITB bonus (huge spectacle match)
        mitb_bonus = 15

        # More wrestlers = more chaos = higher rating
        participant_bonus = (n - 6) * 2

        final_score = base_score + charisma_bonus + mitb_bonus + participant_bonus

        # Condition penalty
        final_score += _condition_penalty(self.wrestlers)

        # High variance for ladder matches
        rng = random.uniform(0.85, 1.15)
        final_score = final_score * rng

        self.rating = min(100, max(0, int(final_score)))


class RoyalRumbleMatch:
    """
    Royal Rumble match simulation.
    10 wrestlers compete, 2 start in the ring, 8 enter at intervals.
    Last wrestler standing wins.
    """

    def __init__(self, wrestlers: list, game_state: 'GameState' = None):
        """
        wrestlers: List of 10 Wrestler objects in entry order (index 0-1 start, 2-9 enter later)
        """
        if len(wrestlers) != 10:
            raise ValueError("Royal Rumble requires exactly 10 wrestlers")

        self.wrestlers = wrestlers  # Entry order
        self.game_state = game_state
        self.eliminations = []  # List of (eliminated_wrestler, eliminated_by, entry_number)
        self.winner = None
        self.rating = 0
        self.commentary = []

    def simulate(self):
        """
        Run the Royal Rumble simulation.
        Returns (winner, eliminations, rating, commentary)
        """
        # Track active wrestlers in the ring
        # Each wrestler has: wrestler object, entry_number, fatigue_penalty
        active = []

        # Entry 1 and 2 start in the ring
        active.append({'wrestler': self.wrestlers[0], 'entry': 1, 'fatigue': 0})
        active.append({'wrestler': self.wrestlers[1], 'entry': 2, 'fatigue': 0})

        self.commentary.append(f"#{1} {self.wrestlers[0].name} and #{2} {self.wrestlers[1].name} start the match!")

        next_entry = 2  # Next wrestler to enter (index)

        # Simulate until one remains
        while len(active) > 1 or next_entry < 10:
            # New entrant every "interval" (when we have eliminations or periodically)
            if next_entry < 10 and (len(active) < 6 or random.random() < 0.4):
                new_wrestler = self.wrestlers[next_entry]
                entry_num = next_entry + 1
                active.append({'wrestler': new_wrestler, 'entry': entry_num, 'fatigue': 0})
                self.commentary.append(f"#{entry_num} {new_wrestler.name} enters the match!")
                next_entry += 1

            # Apply fatigue to all active wrestlers (early entrants suffer more)
            for w in active:
                w['fatigue'] += 1

            # Attempt elimination if more than 1 wrestler
            if len(active) > 1:
                # Calculate survival scores
                scores = []
                for w in active:
                    wrestler = w['wrestler']
                    # Base survival: stamina + brawl + psychology
                    base = (wrestler.stamina + wrestler.brawl + wrestler.psych) / 3
                    # Fatigue penalty (early entrants have higher fatigue)
                    fatigue_penalty = w['fatigue'] * 1.5
                    # Random factor
                    rng = random.randint(-15, 15)
                    survival_score = base - fatigue_penalty + rng
                    scores.append((w, survival_score))

                # Lowest score gets eliminated
                scores.sort(key=lambda x: x[1])
                eliminated = scores[0][0]

                # Pick who eliminated them (random from remaining)
                remaining = [s[0] for s in scores[1:]]
                eliminator = random.choice(remaining)

                self.eliminations.append({
                    'wrestler': eliminated['wrestler'],
                    'eliminated_by': eliminator['wrestler'],
                    'entry_number': eliminated['entry'],
                    'elimination_order': len(self.eliminations) + 1
                })

                self.commentary.append(
                    f"{eliminated['wrestler'].name} (#{eliminated['entry']}) eliminated by {eliminator['wrestler'].name}!"
                )

                active.remove(eliminated)

        # Winner is the last one standing
        self.winner = active[0]['wrestler']
        self.commentary.append(f"{self.winner.name} wins the Royal Rumble!")

        # Calculate match rating
        self._calculate_rating()

        return (self.winner, self.eliminations, self.rating, self.commentary)

    def _calculate_rating(self):
        """Calculate match rating based on participants."""
        # Average star quality and charisma of all participants
        total_star = sum(w.star_power for w in self.wrestlers)
        total_charisma = sum(w.charisma for w in self.wrestlers)
        total_psych = sum(w.psych for w in self.wrestlers)

        avg_star = total_star / 10
        avg_charisma = total_charisma / 10
        avg_psych = total_psych / 10

        base_score = (avg_star + avg_charisma + avg_psych) / 3

        # Royal Rumble bonus (big match feel)
        base_score += 10

        # Condition penalty
        base_score += _condition_penalty(self.wrestlers)

        # Random factor
        rng = random.uniform(0.9, 1.1)
        final_score = base_score * rng

        self.rating = min(100, max(0, int(final_score)))
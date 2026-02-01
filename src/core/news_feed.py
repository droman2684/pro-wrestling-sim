"""
PWInsider Elite - Backstage News Feed System

Generates news entries from game events (title changes, injuries, classic matches,
feud developments, morale shifts, etc.) and displays them on the dashboard and
wrestler profile pages.
"""
import random
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Set, Union


@dataclass
class NewsEntry:
    """A single news feed entry."""
    id: int
    date: str  # "Year X, Month Y, Week Z"
    category: str  # e.g. "title_change", "injury", "classic_match"
    headline: str
    body: str
    importance: str  # "breaking", "major", "minor"
    related_wrestler_ids: List[int] = field(default_factory=list)
    show_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "date": self.date,
            "category": self.category,
            "headline": self.headline,
            "body": self.body,
            "importance": self.importance,
            "related_wrestler_ids": self.related_wrestler_ids,
            "show_name": self.show_name,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'NewsEntry':
        return NewsEntry(
            id=data["id"],
            date=data["date"],
            category=data["category"],
            headline=data["headline"],
            body=data["body"],
            importance=data["importance"],
            related_wrestler_ids=data.get("related_wrestler_ids", []),
            show_name=data.get("show_name", ""),
        )


class NewsFeedManager:
    """Manages the collection of news feed entries."""

    MAX_ENTRIES = 100

    def __init__(self):
        self.feed_entries: List[NewsEntry] = []
        self._next_id: int = 1

    def add_entry(self, entry: NewsEntry) -> None:
        self.feed_entries.insert(0, entry)
        if len(self.feed_entries) > self.MAX_ENTRIES:
            self.feed_entries = self.feed_entries[:self.MAX_ENTRIES]

    def create_entry(
        self,
        date: str,
        category: str,
        headline: str,
        body: str,
        importance: str,
        related_wrestler_ids: List[int] = None,
        show_name: str = "",
    ) -> NewsEntry:
        entry = NewsEntry(
            id=self._next_id,
            date=date,
            category=category,
            headline=headline,
            body=body,
            importance=importance,
            related_wrestler_ids=related_wrestler_ids or [],
            show_name=show_name,
        )
        self._next_id += 1
        self.add_entry(entry)
        return entry

    def get_recent(self, limit: int = 20) -> List[NewsEntry]:
        return self.feed_entries[:limit]

    def get_wrestler_news(self, wrestler_id: int, limit: int = 10) -> List[NewsEntry]:
        results = []
        for entry in self.feed_entries:
            if wrestler_id in entry.related_wrestler_ids:
                results.append(entry)
                if len(results) >= limit:
                    break
        return results

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feed_entries": [e.to_dict() for e in self.feed_entries],
            "_next_id": self._next_id,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'NewsFeedManager':
        manager = NewsFeedManager()
        manager._next_id = data.get("_next_id", 1)
        for entry_data in data.get("feed_entries", []):
            manager.feed_entries.append(NewsEntry.from_dict(entry_data))
        return manager


# ---------------------------------------------------------------------------
# Headline templates  (3-4 per category, randomly selected)
# ---------------------------------------------------------------------------

HEADLINE_TEMPLATES = {
    "title_change": [
        "NEW CHAMPION: {winner} captures the {title}!",
        "TITLE CHANGE! {winner} dethrones {loser} for the {title}!",
        "We have a new {title} champion: {winner}!",
        "Shocking upset! {winner} wins the {title} from {loser}!",
    ],
    "title_defense": [
        "{winner} retains the {title} against {loser}",
        "Successful defense: {winner} holds onto the {title}",
        "{winner} proves too much for {loser}, retains {title}",
    ],
    "injury": [
        "INJURY REPORT: {wrestler} suffers injury at {show}",
        "{wrestler} injured during {show}, expected out {weeks} weeks",
        "Bad news: {wrestler} goes down with an injury",
        "Medical update: {wrestler} sidelined for {weeks} weeks",
    ],
    "injury_return": [
        "{wrestler} cleared to compete after injury recovery",
        "RETURN: {wrestler} is back and ready for action",
        "{wrestler} has been medically cleared to return to the ring",
    ],
    "classic_match": [
        "MATCH OF THE NIGHT: {wrestler_a} vs {wrestler_b} ({stars} stars)",
        "Instant classic! {wrestler_a} and {wrestler_b} tear the house down",
        "{wrestler_a} vs {wrestler_b} steals the show with a {stars}-star classic",
        "Standing ovation for {wrestler_a} vs {wrestler_b}!",
    ],
    "feud_escalation": [
        "TENSIONS RISE: {wrestler_a} vs {wrestler_b} feud turns {intensity}",
        "The rivalry between {wrestler_a} and {wrestler_b} has escalated to {intensity}",
        "Things are getting personal: {wrestler_a}/{wrestler_b} feud now {intensity}",
    ],
    "feud_conclusion": [
        "{winner} settles the score with {loser} as their rivalry comes to an end",
        "FEUD OVER: {winner} gets the last word against {loser}",
        "The {wrestler_a} vs {wrestler_b} chapter is finally closed",
    ],
    "morale_low": [
        "Backstage sources say {wrestler} is unhappy with current booking",
        "Morale concerns: {wrestler} reportedly frustrated",
        "{wrestler} said to be considering their options due to low morale",
    ],
    "morale_high": [
        "{wrestler} is reportedly in the best spirits of their career",
        "Backstage morale high: {wrestler} thriving under current booking",
        "Sources say {wrestler} is very happy with their current position",
    ],
    "condition_critical": [
        "CONCERN: {wrestler} is working through significant wear and tear",
        "Sources say {wrestler} is banged up, could be an injury risk",
        "{wrestler} reportedly working hurt, condition is a concern",
    ],
    "show_rating": [
        "{show} draws a {tv_rating} TV rating - {verdict}",
        "{show} scores {tv_rating} rating with {attendance} in attendance",
        "Ratings report: {show} pulls a {tv_rating} - {verdict}",
    ],
    "interference": [
        "CHAOS: {stable} interferes in the {wrestler_a} vs {wrestler_b} match",
        "{stable} gets involved, costing {victim} the match",
        "Outside interference from {stable} mars {wrestler_a} vs {wrestler_b}",
    ],
    "viewer_milestone": [
        "MILESTONE: Viewership crosses {milestone} viewers!",
        "Company reaches {milestone} viewers for the first time!",
        "Big number: weekly audience now at {milestone}!",
    ],
}

SHOW_VERDICTS = {
    "disaster": [
        "an absolute disaster",
        "a dumpster fire",
        "one to forget",
    ],
    "poor": [
        "a disappointing night",
        "below expectations",
        "a rough watch",
    ],
    "average": [
        "a solid if unspectacular outing",
        "a decent show",
        "an acceptable broadcast",
    ],
    "good": [
        "a strong show",
        "a very good night of wrestling",
        "a crowd-pleasing event",
    ],
    "great": [
        "an excellent show top to bottom",
        "must-see television",
        "one of the best shows of the year",
    ],
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _get_date_string(game_state) -> str:
    return f"Year {game_state.year}, Month {game_state.month}, Week {game_state.week}"


def _get_show_verdict(final_rating: int) -> str:
    if final_rating >= 85:
        return random.choice(SHOW_VERDICTS["great"])
    elif final_rating >= 70:
        return random.choice(SHOW_VERDICTS["good"])
    elif final_rating >= 50:
        return random.choice(SHOW_VERDICTS["average"])
    elif final_rating >= 25:
        return random.choice(SHOW_VERDICTS["poor"])
    else:
        return random.choice(SHOW_VERDICTS["disaster"])


def _get_winner_name(match_result) -> str:
    """Extract the winner name from any result type."""
    if hasattr(match_result, 'winner_name'):
        return match_result.winner_name
    if hasattr(match_result, 'winning_team_name'):
        return match_result.winning_team_name
    return ""


def _get_loser_name(match_result) -> str:
    """Extract the loser name from any result type."""
    if hasattr(match_result, 'loser_name'):
        return match_result.loser_name
    if hasattr(match_result, 'losing_team_name'):
        return match_result.losing_team_name
    if hasattr(match_result, 'loser_names') and match_result.loser_names:
        return match_result.loser_names[0]
    return ""


def _get_participant_pair(match_result) -> tuple:
    """Get a (wrestler_a_name, wrestler_b_name) tuple from any result type."""
    if hasattr(match_result, 'wrestler_a_name'):
        return match_result.wrestler_a_name, match_result.wrestler_b_name
    if hasattr(match_result, 'team_a_name'):
        return match_result.team_a_name, match_result.team_b_name
    if hasattr(match_result, 'participant_names') and len(match_result.participant_names) >= 2:
        return match_result.participant_names[0], match_result.participant_names[1]
    return "Unknown", "Unknown"


def _extract_wrestler_ids(match_result, game_state) -> List[int]:
    """Get wrestler IDs involved in a match result."""
    ids = []
    names_to_find = []

    if hasattr(match_result, 'wrestler_a_name'):
        names_to_find.extend([match_result.wrestler_a_name, match_result.wrestler_b_name])
    elif hasattr(match_result, 'participant_names'):
        names_to_find.extend(match_result.participant_names)
    elif hasattr(match_result, 'team_a_name'):
        # For tag matches, try to get winner/loser names
        names_to_find.append(_get_winner_name(match_result))
        names_to_find.append(_get_loser_name(match_result))

    for name in names_to_find:
        if name:
            w = game_state.get_wrestler_by_name(name)
            if w:
                ids.append(w.id)

    return ids


def _pick_template(category: str) -> str:
    templates = HEADLINE_TEMPLATES.get(category, ["{show}"])
    return random.choice(templates)


# ---------------------------------------------------------------------------
# Main generation functions
# ---------------------------------------------------------------------------

def generate_show_news(
    show_result,
    game_state,
    news_feed: NewsFeedManager,
    pre_show_snapshot: Dict[str, Any],
) -> None:
    """
    Scan a ShowResult and generate news entries for notable events.
    Called after Show.run() completes.
    """
    date = _get_date_string(game_state)
    show_name = show_result.show_name

    for mr in show_result.match_results:
        # --- Title Change ---
        if getattr(mr, 'is_title_match', False) and getattr(mr, 'title_changed', False):
            winner = _get_winner_name(mr)
            loser = _get_loser_name(mr)
            title = getattr(mr, 'title_name', 'the championship')
            headline = _pick_template("title_change").format(
                winner=winner, loser=loser, title=title
            )
            wrestler_ids = _extract_wrestler_ids(mr, game_state)
            news_feed.create_entry(
                date=date,
                category="title_change",
                headline=headline,
                body=f"{winner} defeated {loser} to win the {title} at {show_name}.",
                importance="breaking",
                related_wrestler_ids=wrestler_ids,
                show_name=show_name,
            )

        # --- Title Defense ---
        elif getattr(mr, 'is_title_match', False) and not getattr(mr, 'title_changed', False):
            winner = _get_winner_name(mr)
            loser = _get_loser_name(mr)
            title = getattr(mr, 'title_name', 'the championship')
            if winner and title:
                headline = _pick_template("title_defense").format(
                    winner=winner, loser=loser, title=title
                )
                wrestler_ids = _extract_wrestler_ids(mr, game_state)
                news_feed.create_entry(
                    date=date,
                    category="title_defense",
                    headline=headline,
                    body=f"{winner} successfully defended the {title} against {loser} at {show_name}.",
                    importance="major",
                    related_wrestler_ids=wrestler_ids,
                    show_name=show_name,
                )

        # --- Classic Match (rating >= 85) ---
        if getattr(mr, 'rating', 0) >= 85:
            a_name, b_name = _get_participant_pair(mr)
            stars = f"{mr.rating / 20:.1f}"
            headline = _pick_template("classic_match").format(
                wrestler_a=a_name, wrestler_b=b_name, stars=stars
            )
            wrestler_ids = _extract_wrestler_ids(mr, game_state)
            news_feed.create_entry(
                date=date,
                category="classic_match",
                headline=headline,
                body=f"An incredible {stars}-star match between {a_name} and {b_name} at {show_name}.",
                importance="major",
                related_wrestler_ids=wrestler_ids,
                show_name=show_name,
            )

        # --- Feud Conclusion ---
        if getattr(mr, 'feud_ended', False):
            winner = _get_winner_name(mr)
            loser = _get_loser_name(mr)
            a_name, b_name = _get_participant_pair(mr)
            headline = _pick_template("feud_conclusion").format(
                winner=winner, loser=loser, wrestler_a=a_name, wrestler_b=b_name
            )
            wrestler_ids = _extract_wrestler_ids(mr, game_state)
            news_feed.create_entry(
                date=date,
                category="feud_conclusion",
                headline=headline,
                body=f"The rivalry between {a_name} and {b_name} has concluded at {show_name}. {winner} came out on top.",
                importance="major",
                related_wrestler_ids=wrestler_ids,
                show_name=show_name,
            )

        # --- Interference ---
        if getattr(mr, 'interference_occurred', False) and getattr(mr, 'interference_by', ''):
            a_name, b_name = _get_participant_pair(mr)
            stable_name = mr.interference_by
            loser = _get_loser_name(mr)
            victim = loser if getattr(mr, 'interference_helped', False) else _get_winner_name(mr)
            headline = _pick_template("interference").format(
                stable=stable_name, wrestler_a=a_name, wrestler_b=b_name, victim=victim
            )
            wrestler_ids = _extract_wrestler_ids(mr, game_state)
            news_feed.create_entry(
                date=date,
                category="interference",
                headline=headline,
                body=f"{stable_name} interfered during {a_name} vs {b_name} at {show_name}.",
                importance="minor",
                related_wrestler_ids=wrestler_ids,
                show_name=show_name,
            )

    # --- Feud Escalation (compare intensities) ---
    pre_intensities = pre_show_snapshot.get("feud_intensities", {})
    for feud in game_state.feuds:
        if not feud.is_active:
            continue
        old_intensity = pre_intensities.get(feud.id)
        if old_intensity and old_intensity != feud.intensity:
            w_a = game_state.get_wrestler_by_id(feud.wrestler_a_id)
            w_b = game_state.get_wrestler_by_id(feud.wrestler_b_id)
            a_name = w_a.name if w_a else "Unknown"
            b_name = w_b.name if w_b else "Unknown"
            headline = _pick_template("feud_escalation").format(
                wrestler_a=a_name, wrestler_b=b_name, intensity=feud.intensity.upper()
            )
            wrestler_ids = [fid for fid in [feud.wrestler_a_id, feud.wrestler_b_id]]
            news_feed.create_entry(
                date=date,
                category="feud_escalation",
                headline=headline,
                body=f"The feud between {a_name} and {b_name} has escalated from {old_intensity} to {feud.intensity}.",
                importance="major",
                related_wrestler_ids=wrestler_ids,
                show_name=show_name,
            )

    # --- New Injuries (not injured before show, injured after) ---
    pre_injured_ids = pre_show_snapshot.get("injured_ids", set())
    for wrestler in game_state.roster:
        if wrestler.is_injured and wrestler.id not in pre_injured_ids:
            weeks = wrestler.injury_weeks_remaining
            headline = _pick_template("injury").format(
                wrestler=wrestler.name, show=show_name, weeks=weeks
            )
            news_feed.create_entry(
                date=date,
                category="injury",
                headline=headline,
                body=f"{wrestler.name} was injured at {show_name} and is expected to miss {weeks} week{'s' if weeks != 1 else ''}.",
                importance="breaking",
                related_wrestler_ids=[wrestler.id],
                show_name=show_name,
            )

    # --- Morale Checks ---
    for wrestler in game_state.roster:
        if wrestler.morale < 30:
            headline = _pick_template("morale_low").format(wrestler=wrestler.name)
            news_feed.create_entry(
                date=date,
                category="morale_low",
                headline=headline,
                body=f"{wrestler.name}'s morale has dropped to {wrestler.morale}. Management may need to address this.",
                importance="minor",
                related_wrestler_ids=[wrestler.id],
                show_name=show_name,
            )
        elif wrestler.morale > 90:
            headline = _pick_template("morale_high").format(wrestler=wrestler.name)
            news_feed.create_entry(
                date=date,
                category="morale_high",
                headline=headline,
                body=f"{wrestler.name}'s morale is at an excellent {wrestler.morale}.",
                importance="minor",
                related_wrestler_ids=[wrestler.id],
                show_name=show_name,
            )

    # --- Condition Critical ---
    for wrestler in game_state.roster:
        if wrestler.condition < 25 and not wrestler.is_injured:
            headline = _pick_template("condition_critical").format(wrestler=wrestler.name)
            news_feed.create_entry(
                date=date,
                category="condition_critical",
                headline=headline,
                body=f"{wrestler.name}'s condition has dropped to {wrestler.condition}. Injury risk is elevated.",
                importance="minor",
                related_wrestler_ids=[wrestler.id],
                show_name=show_name,
            )

    # --- Viewer Milestone ---
    pre_viewers = pre_show_snapshot.get("viewers", 0)
    current_viewers = game_state.company.viewers
    pre_million = pre_viewers // 1_000_000
    cur_million = current_viewers // 1_000_000
    if cur_million > pre_million and cur_million > 0:
        milestone = f"{cur_million},000,000"
        headline = _pick_template("viewer_milestone").format(milestone=milestone)
        news_feed.create_entry(
            date=date,
            category="viewer_milestone",
            headline=headline,
            body=f"The company's weekly viewership has crossed the {milestone} mark!",
            importance="major",
            show_name=show_name,
        )

    # --- Show Rating (always one per show) ---
    verdict = _get_show_verdict(show_result.final_rating)
    headline = _pick_template("show_rating").format(
        show=show_name,
        tv_rating=show_result.tv_rating,
        attendance=f"{show_result.attendance:,}",
        verdict=verdict,
    )
    news_feed.create_entry(
        date=date,
        category="show_rating",
        headline=headline,
        body=f"{show_name} scored a {show_result.tv_rating} TV rating with {show_result.attendance:,} in attendance. Verdict: {verdict}.",
        importance="minor",
        show_name=show_name,
    )


def generate_weekly_news(
    game_state,
    news_feed: NewsFeedManager,
    pre_advance_injured: Set[int],
) -> None:
    """
    Generate news for events that happen during advance_week().
    Currently: injury returns.
    """
    date = _get_date_string(game_state)

    for wrestler in game_state.roster:
        # Wrestler was injured before advance, now healed
        if wrestler.id in pre_advance_injured and not wrestler.is_injured:
            headline = _pick_template("injury_return").format(wrestler=wrestler.name)
            news_feed.create_entry(
                date=date,
                category="injury_return",
                headline=headline,
                body=f"{wrestler.name} has recovered from injury and is cleared to compete.",
                importance="major",
                related_wrestler_ids=[wrestler.id],
            )

import sys
import os
from services.game_service import GameService
from core.game_state import ShowResult, MatchResult, TagMatchResult, RumbleResult, MultiManResult, LadderMatchResult, IronManResult, EliminationChamberResult, MoneyInTheBankResult
from core.auto_booker import CardSuggestion, MatchSuggestion, FeudSuggestion
from core.calendar import is_ppv_week, get_ppv_for_week


class CLIApp:
    """
    Command-line interface for the wrestling simulation.
    All print/input operations are isolated here.
    """

    def __init__(self):
        self.game = GameService()

    def run(self):
        """Main application loop."""
        while True:
            game_started = self._screen_start_menu()
            if game_started:
                self._game_loop()

    # --- Utility Methods ---

    def _clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def _press_enter(self):
        input("\nPress Enter to continue...")

    def _print_header(self, title: str):
        print(f"--- {title} ---")

    # --- Start Menu ---

    def _screen_start_menu(self) -> bool:
        """Main menu. Returns True if a game was loaded."""
        while True:
            self._clear_screen()
            print("=== SIMPLE SIM SPORTS: PRO WRESTLING ===")
            print("1. New Game")
            print("2. Load Game")
            print("3. Exit")

            choice = input("\nSelect: ")

            if choice == '1':
                return self._handle_new_game()
            elif choice == '2':
                return self._handle_load_game()
            elif choice == '3':
                sys.exit()

    def _handle_new_game(self) -> bool:
        """New game creation flow."""
        self._clear_screen()
        self._print_header("SELECT DATABASE")

        databases = self.game.list_databases()

        if not databases:
            print("\n[ERROR] No databases found in data/databases/")
            print("Make sure 'wrestlers.json' is inside a subfolder (e.g., 'default').")
            self._press_enter()
            return False

        for i, db in enumerate(databases):
            print(f"{i+1}. {db}")

        try:
            idx = int(input("\nSelect Database: ")) - 1
            if idx < 0 or idx >= len(databases):
                raise ValueError()
            selected_db = databases[idx]
        except (ValueError, IndexError):
            print("\n[ERROR] Invalid Selection.")
            self._press_enter()
            return False

        save_name = input("Name your save file (e.g., 'TestFed'): ").strip()
        if not save_name:
            return False

        success, message = self.game.create_new_game(selected_db, save_name)
        print(f"\n{message}")

        if success:
            self._press_enter()
            return True
        else:
            print("\n[ERROR] Could not start game.")
            self._press_enter()
            return False

    def _handle_load_game(self) -> bool:
        """Load game flow."""
        self._clear_screen()
        self._print_header("LOAD GAME")

        saves = self.game.list_saves()

        if not saves:
            print("No save files found.")
            self._press_enter()
            return False

        for i, save in enumerate(saves):
            print(f"{i+1}. {save}")

        try:
            idx = int(input("\nSelect Save: ")) - 1
            if idx < 0 or idx >= len(saves):
                raise ValueError()
            selected_save = saves[idx]
        except (ValueError, IndexError):
            print("Invalid Selection.")
            self._press_enter()
            return False

        success, message = self.game.load_game(selected_save)
        print(f"\n{message}")
        self._press_enter()
        return success

    # --- Main Game Loop ---

    def _game_loop(self):
        """The main booking/management loop."""
        while True:
            self._clear_screen()
            save_name = self.game.get_save_name()
            self._print_header(f"HEAD OFFICE: {save_name}")
            print("1. View Roster")
            print("2. Book a New Show")
            print("3. Tag Team Management")
            print("4. Feud Management")
            print("5. Stable Management")
            print("6. View Rankings")
            print("7. View Titles")
            print("8. View Records & History")
            print("9. Return to Main Menu")

            choice = input("\nSelect: ")

            if choice == '1':
                self._view_roster_screen()
            elif choice == '2':
                self._book_show_screen()
            elif choice == '3':
                self._tag_team_management_screen()
            elif choice == '4':
                self._feud_management_screen()
            elif choice == '5':
                self._stable_management_screen()
            elif choice == '6':
                self._view_rankings_screen()
            elif choice == '7':
                self._view_titles_screen()
            elif choice == '8':
                self._records_menu_screen()
            elif choice == '9':
                break

    def _view_roster_screen(self):
        """Display the current roster with management options."""
        while True:
            self._clear_screen()
            self._print_header("ACTIVE ROSTER")

            roster = self.game.get_roster()

            for w in roster:
                print(f"[{w.get_overall_rating()}] {w.name} ({w.gimmick}) W:{w.wins} L:{w.losses}")
                print(f"    Stamina: {w.stamina} | Morale: {w.morale} | Heat: {w.heat}")

            print(f"\nTotal: {len(roster)} wrestlers")
            print("\n1. Add New Wrestler")
            print("2. Back")

            choice = input("\nSelect: ")

            if choice == '1':
                self._add_wrestler_flow()
            elif choice == '2':
                break

    def _add_wrestler_flow(self):
        """Flow for creating a new wrestler."""
        self._clear_screen()
        self._print_header("CREATE NEW WRESTLER")

        # Required fields
        name = input("Wrestler Name: ").strip()
        if not name:
            print("Name is required.")
            self._press_enter()
            return

        gimmick = input("Gimmick (e.g., 'The Icon'): ").strip()
        if not gimmick:
            gimmick = "The Newcomer"

        # Optional: Bio
        print("\n--- BIO (press Enter for defaults) ---")
        age_str = input("Age [25]: ").strip()
        age = int(age_str) if age_str.isdigit() else 25

        region = input("Home Region [Unknown]: ").strip()
        if not region:
            region = "Unknown"

        # Optional: Stats
        print("\n--- RING STATS (1-100, Enter for 50) ---")
        brawl = self._get_stat_input("Brawl", 50)
        tech = self._get_stat_input("Technical", 50)
        air = self._get_stat_input("Aerial", 50)
        psych = self._get_stat_input("Psychology", 50)

        print("\n--- ENTERTAINMENT STATS (1-100, Enter for 50) ---")
        mic = self._get_stat_input("Mic Skills", 50)
        charisma = self._get_stat_input("Charisma", 50)
        look = self._get_stat_input("Look", 50)
        star_quality = self._get_stat_input("Star Quality", 50)

        # Alignment
        print("\n--- ALIGNMENT ---")
        print("1. Face (Fan Favorite)")
        print("2. Heel (Villain)")
        print("3. Tweener (Neutral)")
        align_choice = input("Select [1]: ").strip()
        if align_choice == '2':
            alignment = "Heel"
        elif align_choice == '3':
            alignment = "Tweener"
        else:
            alignment = "Face"

        # Confirm
        print(f"\n--- CONFIRM ---")
        print(f"Name: {name}")
        print(f"Gimmick: {gimmick}")
        print(f"Age: {age} | Region: {region} | Alignment: {alignment}")
        print(f"Ring: Brawl {brawl}, Tech {tech}, Air {air}, Psych {psych}")
        print(f"Entertainment: Mic {mic}, Charisma {charisma}, Look {look}, Star {star_quality}")

        confirm = input("\nCreate this wrestler? (y/n): ").lower()
        if confirm != 'y':
            print("Cancelled.")
            self._press_enter()
            return

        success, message = self.game.create_wrestler(
            name=name, gimmick=gimmick, age=age, region=region,
            brawl=brawl, tech=tech, air=air, psych=psych,
            mic=mic, charisma=charisma, look=look, star_quality=star_quality,
            alignment=alignment
        )
        print(f"\n{message}")
        self._press_enter()

    def _get_stat_input(self, stat_name: str, default: int) -> int:
        """Helper to get a stat value with validation."""
        val_str = input(f"{stat_name} [{default}]: ").strip()
        if not val_str:
            return default
        try:
            val = int(val_str)
            return max(1, min(100, val))
        except ValueError:
            return default

    def _view_rankings_screen(self):
        """Display wrestler and tag team rankings."""
        self._clear_screen()
        self._print_header("RANKINGS")

        print("\n--- SINGLES RANKINGS (TOP 5) ---")
        wrestler_rankings = self.game.get_wrestler_rankings()
        if not wrestler_rankings:
            print("No wrestlers currently ranked.")
        else:
            for i, wrestler in enumerate(wrestler_rankings[:5]):
                print(f"#{i+1}. {wrestler.name} ({wrestler.gimmick}) - {wrestler.wins}W / {wrestler.losses}L")

        print("\n--- TAG TEAM RANKINGS (TOP 5) ---")
        tag_team_rankings = self.game.get_tag_team_rankings()
        # Ensure we have state.roster for get_members in TagTeam
        if self.game.is_game_loaded:
            roster = self.game.state.roster
        else:
            roster = [] # Or handle error appropriately

        if not tag_team_rankings:
            print("No tag teams currently ranked.")
        else:
            for i, team in enumerate(tag_team_rankings[:5]):
                members = team.get_members(roster)
                member_names = " & ".join([m.name for m in members])
                print(f"#{i+1}. {team.name} - {team.wins}W / {team.losses}L ({member_names})")

        self._press_enter()

    def _view_titles_screen(self):
        """Display all championships and their holders."""
        while True:
            self._clear_screen()
            self._print_header("CHAMPIONSHIPS")

            titles = self.game.get_titles()

            if not titles:
                print("\nNo championships exist.")
            else:
                for title in titles:
                    print(f"\n[{title.prestige}] {title.name}")
                    if title.current_holder_id:
                        # Check if it's a tag team title (holder could be wrestler or team)
                        holder = self.game.get_wrestler_by_id(title.current_holder_id)
                        if holder:
                            print(f"    Current Holder: {holder.name}")
                        else:
                            # Try tag team
                            team = self.game.get_tag_team_by_id(title.current_holder_id)
                            if team:
                                members = team.get_members(self.game.state.roster)
                                member_names = " & ".join([m.name for m in members])
                                print(f"    Current Holders: {team.name} ({member_names})")
                            else:
                                print("    Current Holder: Unknown")
                    else:
                        print("    Current Holder: Vacant")

            print(f"\nTotal: {len(titles)} championships")
            print("\n1. Create New Title")
            print("2. Back")

            choice = input("\nSelect: ")

            if choice == '1':
                self._add_title_flow()
            elif choice == '2':
                break

    def _add_title_flow(self):
        """Flow for creating a new championship title."""
        self._clear_screen()
        self._print_header("CREATE NEW CHAMPIONSHIP")

        # Name
        name = input("Title Name (e.g., 'Intercontinental Championship'): ").strip()
        if not name:
            print("Name is required.")
            self._press_enter()
            return

        # Prestige
        print("\nPrestige determines title importance (1-100)")
        print("  90-100: World/Main Event title")
        print("  70-89:  Secondary title")
        print("  50-69:  Midcard title")
        print("  Below 50: Lower card title")
        prestige_str = input("Prestige [50]: ").strip()
        try:
            prestige = int(prestige_str) if prestige_str else 50
            prestige = max(1, min(100, prestige))
        except ValueError:
            prestige = 50

        # Confirm
        print(f"\n--- CONFIRM ---")
        print(f"Name: {name}")
        print(f"Prestige: {prestige}")
        print("Status: Vacant")

        confirm = input("\nCreate this championship? (y/n): ").lower()
        if confirm != 'y':
            print("Cancelled.")
            self._press_enter()
            return

        success, message = self.game.create_title(name=name, prestige=prestige)
        print(f"\n{message}")
        self._press_enter()

    def _book_show_screen(self):
        """Book and run a show - choose AI or manual booking."""
        self._clear_screen()
        state = self.game.state
        is_ppv = is_ppv_week(state.month, state.week)
        show_type = "PPV" if is_ppv else "TV Show"

        if is_ppv:
            ppv = get_ppv_for_week(state.month, state.week)
            default_name = ppv['name'] if ppv else "PPV"
        else:
            default_name = f"Weekly Show"

        self._print_header(f"BOOK {show_type.upper()}")
        print(f"Date: {self.game.get_current_date_string()}")

        print("\n1. AI Suggest Card (Recommended)")
        print("2. Manual Booking")
        print("3. Back")

        choice = input("\nSelect: ")

        if choice == '1':
            self._ai_booking_flow()
        elif choice == '2':
            self._manual_booking_flow()
        elif choice == '3':
            return

    def _ai_booking_flow(self):
        """AI-assisted booking with user overrides."""
        self._clear_screen()
        self._print_header("AI BOOKING ASSISTANT")

        print("\nGenerating card suggestions...")
        suggestion = self.game.get_card_suggestions()

        if not suggestion:
            print("\n[ERROR] Could not generate suggestions.")
            self._press_enter()
            return

        while True:
            self._clear_screen()
            self._print_header("AI BOOKING ASSISTANT")

            # Display the suggestion
            print(f"\nSuggested Card: {suggestion.show_name}")
            print(f"Type: {'PPV' if suggestion.is_ppv else 'TV Show'}")
            print(f"Estimated Rating: {suggestion.estimated_rating}/100")

            # Show warnings
            if suggestion.warnings:
                print("\n--- WARNINGS ---")
                for warning in suggestion.warnings:
                    print(f"  ! {warning}")

            # Show each match suggestion
            print("\n--- SUGGESTED MATCHES ---")
            accepted_count = sum(1 for m in suggestion.matches if m.is_accepted)
            print(f"({accepted_count} of {len(suggestion.matches)} accepted)\n")

            for i, match in enumerate(suggestion.matches):
                self._display_match_suggestion(i + 1, match)

            # Show feud suggestions
            if suggestion.feud_suggestions:
                print("\n--- SUGGESTED NEW FEUDS ---")
                for i, feud in enumerate(suggestion.feud_suggestions):
                    w_a = self.game.get_wrestler_by_id(feud.wrestler_a_id)
                    w_b = self.game.get_wrestler_by_id(feud.wrestler_b_id)
                    a_name = w_a.name if w_a else "Unknown"
                    b_name = w_b.name if w_b else "Unknown"
                    print(f"  {i+1}. {a_name} vs {b_name}")
                    print(f"     Reason: {feud.reason}")

            # Options
            print("\n--- OPTIONS ---")
            print("A. Accept and run show")
            print("T. Toggle match on/off")
            print("F. Start a suggested feud")
            print("R. Regenerate suggestions")
            print("M. Switch to manual booking")
            print("C. Cancel")

            action = input("\nSelect: ").upper()

            if action == 'A':
                accepted = [m for m in suggestion.matches if m.is_accepted]
                if not accepted:
                    print("\nNo matches accepted! Toggle some matches on first.")
                    self._press_enter()
                    continue
                success, msg = self.game.apply_card_suggestions(suggestion)
                print(f"\n{msg}")
                if success:
                    self._run_show()
                    return
                else:
                    self._press_enter()
            elif action == 'T':
                self._toggle_match_flow(suggestion)
            elif action == 'F':
                if suggestion.feud_suggestions:
                    self._start_feud_from_suggestion(suggestion.feud_suggestions)
                else:
                    print("\nNo feud suggestions available.")
                    self._press_enter()
            elif action == 'R':
                print("\nRegenerating suggestions...")
                suggestion = self.game.get_card_suggestions()
                if not suggestion:
                    print("[ERROR] Could not regenerate suggestions.")
                    self._press_enter()
                    return
            elif action == 'M':
                self._manual_booking_flow()
                return
            elif action == 'C':
                return

    def _display_match_suggestion(self, num: int, match: MatchSuggestion):
        """Display a single match suggestion with reasoning."""
        # Get participant names
        participants = []
        if match.match_type == "tag":
            for tid in match.participant_ids:
                team = self.game.get_tag_team_by_id(tid)
                participants.append(team.name if team else "Unknown Team")
        else:
            for wid in match.participant_ids:
                w = self.game.get_wrestler_by_id(wid)
                participants.append(w.name if w else "Unknown")

        # Build match type string
        match_type_str = match.match_type.replace("_", " ").title()
        if match.is_title_match and match.title_id:
            title = self.game.get_title_by_id(match.title_id)
            if title:
                match_type_str += f" for {title.name}"
        if match.is_steel_cage:
            match_type_str += " (Steel Cage)"

        # Status indicator
        status = "[X]" if match.is_accepted else "[ ]"

        print(f"{status} {num}. [{match.card_position.upper()}] {match_type_str}")
        print(f"       {' vs '.join(participants)}")
        print(f"       Reason: {match.reason}")
        print(f"       Est. Rating: {match.estimated_rating}/100")

    def _toggle_match_flow(self, suggestion: CardSuggestion):
        """Toggle matches on/off in a card suggestion."""
        print("\nEnter match number to toggle (or 0 to cancel): ", end="")
        try:
            idx = int(input()) - 1
            if idx == -1:
                return
            if 0 <= idx < len(suggestion.matches):
                match = suggestion.matches[idx]
                match.is_accepted = not match.is_accepted
                status = "ACCEPTED" if match.is_accepted else "REMOVED"
                print(f"\nMatch {idx+1} {status}")
            else:
                print("\nInvalid match number.")
        except ValueError:
            print("\nInvalid input.")
        self._press_enter()

    def _start_feud_from_suggestion(self, feud_suggestions):
        """Start a feud from suggestions."""
        print("\nEnter feud number to start (or 0 to cancel): ", end="")
        try:
            idx = int(input()) - 1
            if idx == -1:
                return
            if 0 <= idx < len(feud_suggestions):
                feud = feud_suggestions[idx]
                success, msg = self.game.start_suggested_feud(feud)
                print(f"\n{msg}")
            else:
                print("\nInvalid feud number.")
        except ValueError:
            print("\nInvalid input.")
        self._press_enter()

    def _manual_booking_flow(self):
        """Manual booking flow - original implementation."""
        self._clear_screen()
        show_name = input("Name of the Event (e.g. 'Monday Nitro'): ")

        if not self.game.create_show(show_name):
            print("[ERROR] Could not create show.")
            self._press_enter()
            return

        while True:
            self._clear_screen()
            show = self.game.get_current_show()
            print(f"--- BOOKING CARD: {show_name} ---")
            print(f"Current Matches: {show.match_count}")
            print("\n1. Add a Singles Match")
            print("2. Add a Tag Team Match")
            print("3. Add a Triple Threat (3 wrestlers)")
            print("4. Add a Fatal 4-Way (4 wrestlers)")
            print("5. Add a Ladder Match (2+ wrestlers)")
            print("6. Add an Iron Man Match (timed)")
            print("7. Add a Royal Rumble (10 wrestlers)")
            print("8. Add an Elimination Chamber (6 wrestlers)")
            print("9. Add Money in the Bank (6-8 wrestlers)")
            print("10. Start the Show (Finalize Card)")
            print("0. Cancel & Exit")

            choice = input("\nSelect: ")

            if choice == '1':
                self._add_match_flow()
            elif choice == '2':
                self._add_tag_match_flow()
            elif choice == '3':
                self._add_multi_man_match_flow(3)
            elif choice == '4':
                self._add_multi_man_match_flow(4)
            elif choice == '5':
                self._add_ladder_match_flow()
            elif choice == '6':
                self._add_iron_man_match_flow()
            elif choice == '7':
                self._add_rumble_flow()
            elif choice == '8':
                self._add_chamber_match_flow()
            elif choice == '9':
                self._add_mitb_match_flow()
            elif choice == '10':
                if show.match_count == 0:
                    print("You can't start an empty show!")
                    self._press_enter()
                else:
                    self._run_show()
                    return
            elif choice == '0':
                self.game.cancel_show()
                return

    def _add_match_flow(self):
        """Flow for adding a singles match to the current show."""
        roster = self.game.state.roster

        # Filter out already booked wrestlers
        available = [w for w in roster if not self.game.is_wrestler_booked_on_show(w.id)]

        if len(available) < 2:
            print("Not enough available wrestlers!")
            self._press_enter()
            return

        print("\n--- SELECT WRESTLER A ---")
        for i, w in enumerate(available):
            feud_indicator = ""
            if self.game.state.is_wrestler_in_feud(w.id):
                feud = self.game.state.get_wrestler_feud(w.id)
                if feud:
                    rival_id = feud.wrestler_b_id if feud.wrestler_a_id == w.id else feud.wrestler_a_id
                    rival = self.game.get_wrestler_by_id(rival_id)
                    rival_name = rival.name if rival else "Unknown"
                    feud_indicator = f" [FEUD vs {rival_name}]"
            print(f"{i+1}. {w.name} (Stam: {w.stamina}){feud_indicator}")

        try:
            idx_a = int(input("Select: ")) - 1
            if idx_a < 0 or idx_a >= len(available):
                raise ValueError()
            wrestler_a = available[idx_a]
        except (ValueError, IndexError):
            return

        # Filter out selected wrestler from opponents
        opponents = [w for w in available if w != wrestler_a]

        # Check if wrestler_a is in a feud
        feud_between = None
        print(f"\n--- OPPONENT FOR {wrestler_a.name} ---")
        for i, w in enumerate(opponents):
            feud_indicator = ""
            feud = self.game.state.get_feud_between(wrestler_a.id, w.id)
            if feud:
                feud_indicator = f" [FEUD MATCH - {feud.intensity.upper()}!]"
            print(f"{i+1}. {w.name} (Stam: {w.stamina}){feud_indicator}")

        try:
            idx_b = int(input("Select: ")) - 1
            if idx_b < 0 or idx_b >= len(opponents):
                raise ValueError()
            wrestler_b = opponents[idx_b]
        except (ValueError, IndexError):
            return

        is_steel_cage_str = input(f"Make {wrestler_a.name} vs {wrestler_b.name} a Steel Cage Match? (y/n): ").lower()
        is_steel_cage = (is_steel_cage_str == 'y')

        # Check if either wrestler holds a singles title
        is_title_match = False
        title_id = None
        titles = self.game.get_titles()
        held_titles = []
        for title in titles:
            if title.current_holder_id in [wrestler_a.id, wrestler_b.id]:
                held_titles.append(title)

        if held_titles:
            is_title_str = input("Make this a Title Match? (y/n): ").lower()
            if is_title_str == 'y':
                is_title_match = True
                if len(held_titles) == 1:
                    title_id = held_titles[0].id
                    print(f"{held_titles[0].name} is on the line!")
                else:
                    print("\n--- SELECT TITLE ---")
                    for i, title in enumerate(held_titles):
                        holder = self.game.get_wrestler_by_id(title.current_holder_id)
                        holder_name = holder.name if holder else "Unknown"
                        print(f"{i+1}. {title.name} (held by {holder_name})")
                    try:
                        idx = int(input("\nSelect: ")) - 1
                        if idx < 0 or idx >= len(held_titles):
                            raise ValueError()
                        title_id = held_titles[idx].id
                        print(f"{held_titles[idx].name} is on the line!")
                    except (ValueError, IndexError):
                        print("Invalid selection. Booking as non-title match.")
                        is_title_match = False

        if self.game.add_match_to_show(wrestler_a, wrestler_b, is_steel_cage=is_steel_cage, is_title_match=is_title_match, title_id=title_id):
            match_type_str = "Steel Cage Match" if is_steel_cage else "Singles Match"
            if is_title_match:
                title = next((t for t in titles if t.id == title_id), None)
                match_type_str += f" for the {title.name}" if title else " (Title Match)"
            print(f"Added {match_type_str}: {wrestler_a.name} vs {wrestler_b.name} to the card.")
        else:
            print("Could not add match.")
        self._press_enter()

    def _run_show(self):
        """Execute the show and display results."""
        self._clear_screen()
        show = self.game.get_current_show()
        print(f"\n--- STARTING SHOW: {show.name.upper()} ---")

        result = self.game.play_show()

        if result is None:
            print("[ERROR] Could not run show.")
            self._press_enter()
            return

        # Display match results one by one
        for i, match_result in enumerate(result.match_results):
            if isinstance(match_result, RumbleResult):
                # Royal Rumble result
                print(f"\n{'='*40}")
                print(f"ROYAL RUMBLE")
                print(f"{'='*40}")
                print(f"Rating: {match_result.rating}/100 ({match_result.stars:.1f} Stars)")
                print(f"\n*** {match_result.winner_name} WINS THE ROYAL RUMBLE! ***")
                print("\nElimination Order:")
                for elim in match_result.eliminations:
                    print(f"  {elim['elimination_order']}. {elim['wrestler_name']} (Entry #{elim['entry_number']}) - by {elim['eliminated_by']}")
            elif isinstance(match_result, MultiManResult):
                # Triple Threat / Fatal 4-Way result
                match_header = f"{match_result.match_type}"
                if match_result.is_title_match:
                    match_header += f" for the {match_result.title_name}"
                print(f"\n{'='*40}")
                print(match_header.upper())
                print(f"{'='*40}")
                print(f"Participants: {' vs '.join(match_result.participant_names)}")
                print(f"Winner: {match_result.winner_name}")
                print(f"Pinned: {match_result.pinned_wrestler_name}")
                print(f"Rating: {match_result.rating}/100 ({match_result.stars:.1f} Stars)")
                if match_result.title_changed:
                    print(f"\n*** NEW CHAMPION! {match_result.new_champion_name} wins the {match_result.title_name}! ***")
                elif match_result.is_title_match:
                    print(f"(Champion retains)")
            elif isinstance(match_result, LadderMatchResult):
                # Ladder match result
                match_header = f"{match_result.match_type}"
                if match_result.is_title_match:
                    match_header += f" for the {match_result.title_name}"
                print(f"\n{'='*40}")
                print(match_header.upper())
                print(f"{'='*40}")
                print(f"Participants: {' vs '.join(match_result.participant_names)}")
                print(f"Winner: {match_result.winner_name} retrieves the prize!")
                print(f"Rating: {match_result.rating}/100 ({match_result.stars:.1f} Stars)")
                if match_result.title_changed:
                    print(f"\n*** NEW CHAMPION! {match_result.new_champion_name} wins the {match_result.title_name}! ***")
                elif match_result.is_title_match:
                    print(f"(Champion retains)")
            elif isinstance(match_result, IronManResult):
                # Iron Man match result
                match_header = f"{match_result.match_type}"
                if match_result.is_title_match:
                    match_header += f" for the {match_result.title_name}"
                print(f"\n{'='*40}")
                print(match_header.upper())
                print(f"{'='*40}")
                print(f"{match_result.wrestler_a_name} vs {match_result.wrestler_b_name}")
                print(f"Final Score: {match_result.falls_a} - {match_result.falls_b}")
                if match_result.is_draw:
                    print(f"RESULT: TIME LIMIT DRAW!")
                else:
                    print(f"Winner: {match_result.winner_name}")
                print(f"Rating: {match_result.rating}/100 ({match_result.stars:.1f} Stars)")
                if match_result.fall_log:
                    print("\nFall Breakdown:")
                    for fall in match_result.fall_log:
                        print(f"  [{fall['time']}:00] {fall['wrestler']} ({fall['type']}) - Score: {fall['score']}")
                if match_result.title_changed:
                    print(f"\n*** NEW CHAMPION! {match_result.new_champion_name} wins the {match_result.title_name}! ***")
                elif match_result.is_title_match and not match_result.is_draw:
                    print(f"(Champion retains)")
            elif isinstance(match_result, EliminationChamberResult):
                # Elimination Chamber result
                match_header = f"{match_result.match_type}"
                if match_result.is_title_match:
                    match_header += f" for the {match_result.title_name}"
                print(f"\n{'='*40}")
                print(match_header.upper())
                print(f"{'='*40}")
                print(f"Participants: {', '.join(match_result.participant_names)}")
                print(f"\nElimination Order:")
                for elim in match_result.eliminations:
                    print(f"  #{elim['elimination_order']}: {elim['wrestler_name']} eliminated by {elim['eliminated_by']} (Entry #{elim['entry_number']})")
                print(f"\nWINNER: {match_result.winner_name}")
                print(f"Rating: {match_result.rating}/100 ({match_result.stars:.1f} Stars)")
                if match_result.title_changed:
                    print(f"\n*** NEW CHAMPION! {match_result.new_champion_name} wins the {match_result.title_name}! ***")
                elif match_result.is_title_match:
                    print(f"(Champion retains)")
            elif isinstance(match_result, MoneyInTheBankResult):
                # Money in the Bank result
                print(f"\n{'='*40}")
                print(f"{match_result.match_type.upper()}")
                print(f"{'='*40}")
                print(f"Participants: {', '.join(match_result.participant_names)}")
                print(f"\nWINNER: {match_result.winner_name}")
                print(f"{match_result.winner_name} now holds the Money in the Bank briefcase!")
                print(f"Rating: {match_result.rating}/100 ({match_result.stars:.1f} Stars)")
            elif isinstance(match_result, TagMatchResult):
                # Tag team match result
                match_header = f"Tag Team Match #{i + 1}"
                if match_result.is_title_match:
                    match_header += f" - {match_result.title_name}"
                print(f"\n{match_header}: {match_result.team_a_name} vs. {match_result.team_b_name}")
                print(f"Winners: {match_result.winning_team_name}")
                print(f"Pinned: {match_result.pinned_wrestler_name}")
                print(f"Rating: {match_result.rating}/100 ({match_result.stars:.1f} Stars)")
                if match_result.title_changed:
                    print(f"\n*** NEW CHAMPIONS! {match_result.new_champion_name} win the {match_result.title_name}! ***")
                elif match_result.is_title_match:
                    print(f"(Champions retain)")
            else:
                # Singles match result
                match_header = f"Match #{i + 1}"
                if match_result.is_title_match:
                    match_header += f" - {match_result.title_name}"
                if match_result.is_feud_match:
                    match_header += f" [FEUD - {match_result.feud_intensity.upper()}]"
                print(f"\n{match_header}: {match_result.wrestler_a_name} vs. {match_result.wrestler_b_name}")
                print(f"Winner: {match_result.winner_name}")
                print(f"Rating: {match_result.rating}/100 ({match_result.stars:.1f} Stars)")
                if match_result.interference_occurred:
                    if match_result.interference_helped:
                        print(f"\n*** INTERFERENCE! {match_result.interference_by} helped their stablemate! ***")
                    else:
                        print(f"\n*** DQ! {match_result.interference_by}'s interference backfired! ***")
                if match_result.title_changed:
                    print(f"\n*** NEW CHAMPION! {match_result.new_champion_name} wins the {match_result.title_name}! ***")
                elif match_result.is_title_match:
                    print(f"(Champion retains)")
                if match_result.feud_ended:
                    print(f"\n*** FEUD CONCLUDED! The rivalry between {match_result.wrestler_a_name} and {match_result.wrestler_b_name} has ended! ***")
            
            # Display commentary
            if match_result.commentary:
                print("\n    --- Highlights ---")
                for line in match_result.commentary:
                    print(f"    - {line}")
            input("(Press Enter for next segment...)")

        # Show final report
        print("\n" + "=" * 40)
        print(f"SHOW REPORT: {result.show_name}")
        print(f"Final Rating: {result.final_rating}/100")
        print("=" * 40)
        print(f"\nRESULT: {result.feedback}")
        print("\n[Game auto-saved]")

        self._press_enter()

    # --- Tag Team Operations ---

    def _tag_team_management_screen(self):
        """Tag team management menu."""
        while True:
            self._clear_screen()
            self._print_header("TAG TEAM MANAGEMENT")

            teams = self.game.get_tag_teams()
            active_teams = [t for t in teams if t.is_active]

            print(f"Active Teams: {len(active_teams)}")
            print("\n1. View Tag Teams")
            print("2. Create New Tag Team")
            print("3. Disband Tag Team")
            print("4. Back to Main Menu")

            choice = input("\nSelect: ")

            if choice == '1':
                self._view_tag_teams()
            elif choice == '2':
                self._create_tag_team_flow()
            elif choice == '3':
                self._disband_tag_team_flow()
            elif choice == '4':
                break

    def _view_tag_teams(self):
        """Display all active tag teams."""
        self._clear_screen()
        self._print_header("ACTIVE TAG TEAMS")

        teams = [t for t in self.game.get_tag_teams() if t.is_active]
        roster = self.game.state.roster

        if not teams:
            print("\nNo active tag teams.")
        else:
            for team in teams:
                members = team.get_members(roster)
                member_names = " & ".join([m.name for m in members])
                rating = team.get_team_rating(roster)
                print(f"\n[{rating}] {team.name}")
                print(f"    Members: {member_names}")
                print(f"    Chemistry: {team.chemistry} | Record: {team.wins}W - {team.losses}L")

        self._press_enter()

    def _create_tag_team_flow(self):
        """Flow for creating a new tag team."""
        self._clear_screen()
        self._print_header("CREATE TAG TEAM")

        roster = self.game.state.roster

        # Filter wrestlers not already on a team
        available = [w for w in roster if not self.game.state.is_wrestler_on_team(w.id)]

        if len(available) < 2:
            print("\nNot enough available wrestlers to form a team!")
            print("(Wrestlers can only be on one team at a time)")
            self._press_enter()
            return

        print("\n--- SELECT FIRST MEMBER ---")
        for i, w in enumerate(available):
            print(f"{i+1}. {w.name} [{w.get_overall_rating()}]")

        try:
            idx_a = int(input("\nSelect: ")) - 1
            if idx_a < 0 or idx_a >= len(available):
                raise ValueError()
            member_a = available[idx_a]
        except (ValueError, IndexError):
            return

        # Filter out selected wrestler
        remaining = [w for w in available if w != member_a]

        print(f"\n--- SELECT PARTNER FOR {member_a.name} ---")
        for i, w in enumerate(remaining):
            print(f"{i+1}. {w.name} [{w.get_overall_rating()}]")

        try:
            idx_b = int(input("\nSelect: ")) - 1
            if idx_b < 0 or idx_b >= len(remaining):
                raise ValueError()
            member_b = remaining[idx_b]
        except (ValueError, IndexError):
            return

        # Get team name
        team_name = input(f"\nTeam name for {member_a.name} & {member_b.name}: ").strip()
        if not team_name:
            print("Team name cannot be empty.")
            self._press_enter()
            return

        success, message = self.game.create_tag_team(team_name, member_a.id, member_b.id)
        print(f"\n{message}")
        self._press_enter()

    def _disband_tag_team_flow(self):
        """Flow for disbanding a tag team."""
        self._clear_screen()
        self._print_header("DISBAND TAG TEAM")

        teams = [t for t in self.game.get_tag_teams() if t.is_active]
        roster = self.game.state.roster

        if not teams:
            print("\nNo active tag teams to disband.")
            self._press_enter()
            return

        print("\n--- SELECT TEAM TO DISBAND ---")
        for i, team in enumerate(teams):
            members = team.get_members(roster)
            member_names = " & ".join([m.name for m in members])
            print(f"{i+1}. {team.name} ({member_names})")

        try:
            idx = int(input("\nSelect: ")) - 1
            if idx < 0 or idx >= len(teams):
                raise ValueError()
            team = teams[idx]
        except (ValueError, IndexError):
            return

        # Confirm
        confirm = input(f"\nAre you sure you want to disband '{team.name}'? (y/n): ").lower()
        if confirm != 'y':
            print("Cancelled.")
            self._press_enter()
            return

        success, message = self.game.disband_tag_team(team.id)
        print(f"\n{message}")
        self._press_enter()

    def _tag_team_rankings_screen(self):
        """Display tag team rankings."""
        self._clear_screen()
        self._print_header("TAG TEAM RANKINGS")

        teams = self.game.get_tag_team_rankings()
        roster = self.game.state.roster

        if not teams:
            print("\nNo active tag teams.")
        else:
            for i, team in enumerate(teams):
                members = team.get_members(roster)
                member_names = " & ".join([m.name for m in members])
                rating = team.get_team_rating(roster)
                print(f"\n#{i+1}. {team.name} [{rating}]")
                print(f"    {member_names}")
                print(f"    Chemistry: {team.chemistry} | Record: {team.wins}W - {team.losses}L")

        self._press_enter()

    def _add_tag_match_flow(self):
        """Flow for adding a tag team match to the current show."""
        teams = self.game.get_available_tag_teams()
        roster = self.game.state.roster

        # Filter out teams with members already booked
        available_teams = [
            t for t in teams
            if not any(self.game.is_wrestler_booked_on_show(mid) for mid in t.member_ids)
        ]

        if len(available_teams) < 2:
            print("\nNot enough available tag teams!")
            print("(Need at least 2 teams with available members)")
            self._press_enter()
            return

        print("\n--- SELECT TEAM A ---")
        for i, team in enumerate(available_teams):
            members = team.get_members(roster)
            member_names = " & ".join([m.name for m in members])
            rating = team.get_team_rating(roster)
            print(f"{i+1}. {team.name} [{rating}] - {member_names}")

        try:
            idx_a = int(input("\nSelect: ")) - 1
            if idx_a < 0 or idx_a >= len(available_teams):
                raise ValueError()
            team_a = available_teams[idx_a]
        except (ValueError, IndexError):
            return

        # Filter out selected team
        opponents = [t for t in available_teams if t != team_a]

        print(f"\n--- OPPONENT FOR {team_a.name} ---")
        for i, team in enumerate(opponents):
            members = team.get_members(roster)
            member_names = " & ".join([m.name for m in members])
            rating = team.get_team_rating(roster)
            print(f"{i+1}. {team.name} [{rating}] - {member_names}")

        try:
            idx_b = int(input("\nSelect: ")) - 1
            if idx_b < 0 or idx_b >= len(opponents):
                raise ValueError()
            team_b = opponents[idx_b]
        except (ValueError, IndexError):
            return

        is_steel_cage_str = input(f"Make {team_a.name} vs {team_b.name} a Steel Cage Match? (y/n): ").lower()
        is_steel_cage = (is_steel_cage_str == 'y')

        # Check if either team holds a tag team title
        is_title_match = False
        title_id = None
        titles = self.game.get_titles()
        held_titles = []
        for title in titles:
            if title.current_holder_id in [team_a.id, team_b.id]:
                held_titles.append(title)

        if held_titles:
            is_title_str = input("Make this a Title Match? (y/n): ").lower()
            if is_title_str == 'y':
                is_title_match = True
                if len(held_titles) == 1:
                    title_id = held_titles[0].id
                    print(f"{held_titles[0].name} is on the line!")
                else:
                    print("\n--- SELECT TITLE ---")
                    for i, title in enumerate(held_titles):
                        holder = self.game.get_tag_team_by_id(title.current_holder_id)
                        holder_name = holder.name if holder else "Unknown"
                        print(f"{i+1}. {title.name} (held by {holder_name})")
                    try:
                        idx = int(input("\nSelect: ")) - 1
                        if idx < 0 or idx >= len(held_titles):
                            raise ValueError()
                        title_id = held_titles[idx].id
                        print(f"{held_titles[idx].name} is on the line!")
                    except (ValueError, IndexError):
                        print("Invalid selection. Booking as non-title match.")
                        is_title_match = False

        if self.game.add_tag_match_to_show(team_a, team_b, is_steel_cage=is_steel_cage, is_title_match=is_title_match, title_id=title_id):
            match_type_str = "Steel Cage Match" if is_steel_cage else "Tag Team Match"
            if is_title_match:
                title = next((t for t in titles if t.id == title_id), None)
                match_type_str += f" for the {title.name}" if title else " (Title Match)"
            print(f"\nAdded {match_type_str}: {team_a.name} vs {team_b.name} to the card.")
        else:
            print("\nCould not add match.")
        self._press_enter()

    def _add_multi_man_match_flow(self, num_wrestlers: int):
        """Flow for adding a Triple Threat (3) or Fatal 4-Way (4) match."""
        match_type = "Triple Threat" if num_wrestlers == 3 else "Fatal 4-Way"
        roster = self.game.state.roster

        # Filter out already booked wrestlers
        available = [w for w in roster if not self.game.is_wrestler_booked_on_show(w.id)]

        if len(available) < num_wrestlers:
            print(f"\nNot enough available wrestlers! Need {num_wrestlers}, have {len(available)}.")
            self._press_enter()
            return

        self._clear_screen()
        self._print_header(f"{match_type.upper()} - SELECT {num_wrestlers} WRESTLERS")

        selected = []
        while len(selected) < num_wrestlers:
            print(f"\n--- SELECT WRESTLER {len(selected) + 1} of {num_wrestlers} ---")
            remaining = [w for w in available if w not in selected]

            for i, w in enumerate(remaining):
                print(f"{i+1}. {w.name} [{w.get_overall_rating()}] (Stam: {w.stamina})")

            try:
                idx = int(input("\nSelect: ")) - 1
                if idx < 0 or idx >= len(remaining):
                    raise ValueError()
                wrestler = remaining[idx]
                selected.append(wrestler)
                print(f"Added: {wrestler.name}")
            except (ValueError, IndexError):
                print("Invalid selection.")
                continue

        # Show summary
        print(f"\n--- {match_type.upper()} MATCH ---")
        names = [w.name for w in selected]
        print(f"  {' vs '.join(names)}")

        # Check for title match
        is_title_match = False
        title_id = None
        titles = self.game.get_titles()

        # Check if any selected wrestler holds a singles title
        held_titles = []
        for t in titles:
            if t.is_tag_team:
                continue
            holder = self.game.get_wrestler_by_id(t.current_holder_id)
            if holder and holder in selected:
                held_titles.append(t)

        if held_titles:
            print("\n--- TITLE MATCH? ---")
            print("A champion is in this match!")
            for i, t in enumerate(held_titles):
                holder = self.game.get_wrestler_by_id(t.current_holder_id)
                print(f"{i+1}. {t.name} (held by {holder.name if holder else 'Unknown'})")
            print(f"{len(held_titles) + 1}. No title on the line")

            try:
                title_choice = int(input("Select: "))
                if 1 <= title_choice <= len(held_titles):
                    is_title_match = True
                    title_id = held_titles[title_choice - 1].id
                    print(f"{held_titles[title_choice - 1].name} is on the line!")
            except (ValueError, IndexError):
                print("Invalid selection. Booking as non-title match.")

        confirm = input(f"\nConfirm this {match_type}? (y/n): ").lower()
        if confirm != 'y':
            print("Cancelled.")
            self._press_enter()
            return

        success, message = self.game.add_multi_man_match_to_show(selected, is_title_match=is_title_match, title_id=title_id)
        print(f"\n{message}")
        self._press_enter()

    def _add_ladder_match_flow(self):
        """Flow for adding a Ladder match to the current show."""
        roster = self.game.state.roster

        # Filter out already booked wrestlers
        available = [w for w in roster if not self.game.is_wrestler_booked_on_show(w.id)]

        if len(available) < 2:
            print("\nNot enough available wrestlers! Need at least 2.")
            self._press_enter()
            return

        self._clear_screen()
        self._print_header("LADDER MATCH - SELECT WRESTLERS")
        print("Select 2-6 wrestlers (type 'done' when finished)\n")

        selected = []
        while len(selected) < 6:
            print(f"\n--- SELECT WRESTLER {len(selected) + 1} (or 'done' if finished) ---")
            remaining = [w for w in available if w not in selected]

            for i, w in enumerate(remaining):
                print(f"{i+1}. {w.name} [{w.get_overall_rating()}] (Air: {w.air})")

            choice = input("\nSelect (or 'done'): ").strip().lower()

            if choice == 'done':
                if len(selected) < 2:
                    print("Need at least 2 wrestlers!")
                    continue
                break

            try:
                idx = int(choice) - 1
                if idx < 0 or idx >= len(remaining):
                    raise ValueError()
                wrestler = remaining[idx]
                selected.append(wrestler)
                print(f"Added: {wrestler.name}")
            except (ValueError, IndexError):
                print("Invalid selection.")
                continue

        # Determine match type name
        if len(selected) == 2:
            match_type = "Ladder Match"
        elif len(selected) <= 4:
            match_type = f"{len(selected)}-Way Ladder Match"
        else:
            match_type = "Money in the Bank Ladder Match"

        # Show summary
        print(f"\n--- {match_type.upper()} ---")
        names = [w.name for w in selected]
        print(f"  {' vs '.join(names)}")

        # Check for title match
        is_title_match = False
        title_id = None
        titles = self.game.get_titles()

        # Check if any selected wrestler holds a singles title
        held_titles = []
        for t in titles:
            if t.is_tag_team:
                continue
            holder = self.game.get_wrestler_by_id(t.current_holder_id)
            if holder and holder in selected:
                held_titles.append(t)

        if held_titles:
            print("\n--- TITLE MATCH? ---")
            print("A champion is in this match!")
            for i, t in enumerate(held_titles):
                holder = self.game.get_wrestler_by_id(t.current_holder_id)
                print(f"{i+1}. {t.name} (held by {holder.name if holder else 'Unknown'})")
            print(f"{len(held_titles) + 1}. No title on the line")

            try:
                title_choice = int(input("Select: "))
                if 1 <= title_choice <= len(held_titles):
                    is_title_match = True
                    title_id = held_titles[title_choice - 1].id
                    print(f"{held_titles[title_choice - 1].name} is on the line!")
            except (ValueError, IndexError):
                print("Invalid selection. Booking as non-title match.")

        confirm = input(f"\nConfirm this {match_type}? (y/n): ").lower()
        if confirm != 'y':
            print("Cancelled.")
            self._press_enter()
            return

        success, message = self.game.add_ladder_match_to_show(selected, is_title_match=is_title_match, title_id=title_id)
        print(f"\n{message}")
        self._press_enter()

    def _add_iron_man_match_flow(self):
        """Flow for adding an Iron Man match to the current show."""
        roster = self.game.state.roster

        # Filter out already booked wrestlers
        available = [w for w in roster if not self.game.is_wrestler_booked_on_show(w.id)]

        if len(available) < 2:
            print("\nNot enough available wrestlers! Need at least 2.")
            self._press_enter()
            return

        self._clear_screen()
        self._print_header("IRON MAN MATCH")

        # Select wrestler A
        print("\n--- SELECT WRESTLER A ---")
        for i, w in enumerate(available):
            print(f"{i+1}. {w.name} [{w.get_overall_rating()}] (Stam: {w.stamina}, Psych: {w.psych})")

        try:
            idx_a = int(input("Select: ")) - 1
            if idx_a < 0 or idx_a >= len(available):
                raise ValueError()
            wrestler_a = available[idx_a]
        except (ValueError, IndexError):
            print("Invalid selection.")
            self._press_enter()
            return

        # Select wrestler B
        opponents = [w for w in available if w != wrestler_a]
        print(f"\n--- OPPONENT FOR {wrestler_a.name} ---")
        for i, w in enumerate(opponents):
            print(f"{i+1}. {w.name} [{w.get_overall_rating()}] (Stam: {w.stamina}, Psych: {w.psych})")

        try:
            idx_b = int(input("Select: ")) - 1
            if idx_b < 0 or idx_b >= len(opponents):
                raise ValueError()
            wrestler_b = opponents[idx_b]
        except (ValueError, IndexError):
            print("Invalid selection.")
            self._press_enter()
            return

        # Select time limit
        print("\n--- TIME LIMIT ---")
        print("1. 30 Minutes (Standard)")
        print("2. 60 Minutes (Classic)")
        print("3. Custom")

        try:
            time_choice = int(input("Select: "))
            if time_choice == 1:
                time_limit = 30
            elif time_choice == 2:
                time_limit = 60
            elif time_choice == 3:
                time_limit = int(input("Enter time in minutes (15-90): "))
                time_limit = max(15, min(90, time_limit))
            else:
                time_limit = 30
        except ValueError:
            time_limit = 30

        print(f"\n{time_limit}-Minute Iron Man Match: {wrestler_a.name} vs {wrestler_b.name}")

        # Check for title match
        is_title_match = False
        title_id = None
        titles = self.game.get_titles()

        # Check if either wrestler holds a singles title
        held_titles = []
        for t in titles:
            if t.is_tag_team:
                continue
            holder = self.game.get_wrestler_by_id(t.current_holder_id)
            if holder and holder in [wrestler_a, wrestler_b]:
                held_titles.append(t)

        if held_titles:
            print("\n--- TITLE MATCH? ---")
            print("A champion is in this match!")
            for i, t in enumerate(held_titles):
                holder = self.game.get_wrestler_by_id(t.current_holder_id)
                print(f"{i+1}. {t.name} (held by {holder.name if holder else 'Unknown'})")
            print(f"{len(held_titles) + 1}. No title on the line")

            try:
                title_choice = int(input("Select: "))
                if 1 <= title_choice <= len(held_titles):
                    is_title_match = True
                    title_id = held_titles[title_choice - 1].id
                    print(f"{held_titles[title_choice - 1].name} is on the line!")
            except (ValueError, IndexError):
                print("Invalid selection. Booking as non-title match.")

        confirm = input(f"\nConfirm this Iron Man Match? (y/n): ").lower()
        if confirm != 'y':
            print("Cancelled.")
            self._press_enter()
            return

        success, message = self.game.add_iron_man_match_to_show(wrestler_a, wrestler_b, time_limit,
                                                                 is_title_match=is_title_match, title_id=title_id)
        print(f"\n{message}")
        self._press_enter()

    def _add_rumble_flow(self):
        """Flow for adding a Royal Rumble match to the current show."""
        roster = self.game.state.roster

        # Filter out already booked wrestlers
        available = [w for w in roster if not self.game.is_wrestler_booked_on_show(w.id)]

        if len(available) < 10:
            print(f"\nNot enough available wrestlers! Need 10, have {len(available)}.")
            self._press_enter()
            return

        self._clear_screen()
        self._print_header("ROYAL RUMBLE - SELECT 10 WRESTLERS")
        print("Select wrestlers in entry order (1st selected = Entry #1, etc.)\n")

        selected = []

        while len(selected) < 10:
            print(f"\n--- SELECT ENTRY #{len(selected) + 1} ---")
            remaining = [w for w in available if w not in selected]

            for i, w in enumerate(remaining):
                print(f"{i+1}. {w.name} [{w.get_overall_rating()}] (Stam: {w.stamina})")

            try:
                idx = int(input("\nSelect: ")) - 1
                if idx < 0 or idx >= len(remaining):
                    raise ValueError()
                wrestler = remaining[idx]
                selected.append(wrestler)
                print(f"Entry #{len(selected)}: {wrestler.name}")
            except (ValueError, IndexError):
                print("Invalid selection.")
                continue

        # Show summary
        print("\n--- ROYAL RUMBLE CARD ---")
        for i, w in enumerate(selected):
            print(f"  #{i+1}: {w.name}")

        confirm = input("\nConfirm this Royal Rumble? (y/n): ").lower()
        if confirm != 'y':
            print("Cancelled.")
            self._press_enter()
            return

        success, message = self.game.add_rumble_to_show(selected)
        print(f"\n{message}")
        self._press_enter()

    def _add_chamber_match_flow(self):
        """Flow for adding an Elimination Chamber match to the current show."""
        roster = self.game.state.roster

        # Filter out already booked wrestlers
        available = [w for w in roster if not self.game.is_wrestler_booked_on_show(w.id)]

        if len(available) < 6:
            print(f"\nNot enough available wrestlers! Need 6, have {len(available)}.")
            self._press_enter()
            return

        self._clear_screen()
        self._print_header("ELIMINATION CHAMBER - SELECT 6 WRESTLERS")
        print("Select wrestlers in entry order (1-2 start in ring, 3-6 in pods)\n")

        selected = []

        while len(selected) < 6:
            position = "START IN RING" if len(selected) < 2 else f"POD #{len(selected) - 1}"
            print(f"\n--- SELECT ENTRY #{len(selected) + 1} ({position}) ---")
            remaining = [w for w in available if w not in selected]

            for i, w in enumerate(remaining):
                print(f"{i+1}. {w.name} [{w.get_overall_rating()}] (Stam: {w.stamina})")

            try:
                idx = int(input("\nSelect: ")) - 1
                if idx < 0 or idx >= len(remaining):
                    raise ValueError()
                wrestler = remaining[idx]
                selected.append(wrestler)
                print(f"Entry #{len(selected)}: {wrestler.name} ({position})")
            except (ValueError, IndexError):
                print("Invalid selection.")
                continue

        # Show summary
        print("\n--- ELIMINATION CHAMBER CARD ---")
        print("Starting in ring:")
        for i, w in enumerate(selected[:2]):
            print(f"  #{i+1}: {w.name}")
        print("In pods:")
        for i, w in enumerate(selected[2:]):
            print(f"  Pod #{i+1}: {w.name}")

        # Check for title match
        is_title_match = False
        title_id = None
        titles = self.game.get_titles()
        held_titles = [t for t in titles if t.current_holder_id is not None]

        # Check if any selected wrestler holds a title
        participant_ids = [w.id for w in selected]
        relevant_titles = [t for t in held_titles if t.current_holder_id in participant_ids]

        if relevant_titles:
            print("\nA champion is in this match! Make it a title match?")
            for i, t in enumerate(relevant_titles):
                holder = self.game.get_wrestler_by_id(t.current_holder_id)
                print(f"{i+1}. {t.name} (held by {holder.name if holder else 'Unknown'})")
            print(f"{len(relevant_titles) + 1}. No title on the line")

            try:
                title_choice = int(input("Select: "))
                if 1 <= title_choice <= len(relevant_titles):
                    is_title_match = True
                    title_id = relevant_titles[title_choice - 1].id
                    print(f"{relevant_titles[title_choice - 1].name} is on the line!")
            except (ValueError, IndexError):
                print("Invalid selection. Booking as non-title match.")

        confirm = input("\nConfirm this Elimination Chamber? (y/n): ").lower()
        if confirm != 'y':
            print("Cancelled.")
            self._press_enter()
            return

        success, message = self.game.add_chamber_match_to_show(selected, is_title_match=is_title_match, title_id=title_id)
        print(f"\n{message}")
        self._press_enter()

    def _add_mitb_match_flow(self):
        """Flow for adding a Money in the Bank ladder match to the current show."""
        roster = self.game.state.roster

        # Filter out already booked wrestlers
        available = [w for w in roster if not self.game.is_wrestler_booked_on_show(w.id)]

        if len(available) < 6:
            print(f"\nNot enough available wrestlers! Need 6-8, have {len(available)}.")
            self._press_enter()
            return

        self._clear_screen()
        self._print_header("MONEY IN THE BANK - SELECT 6-8 WRESTLERS")
        print("Winner earns a championship contract for a future title shot!\n")

        # Check if there's already an MITB holder
        mitb_holder = self.game.get_mitb_holder()
        if mitb_holder:
            print(f"NOTE: {mitb_holder.name} currently holds the Money in the Bank briefcase.")
            print("If a new winner is crowned, the old briefcase will be replaced.\n")

        selected = []
        max_wrestlers = min(8, len(available))

        while len(selected) < max_wrestlers:
            print(f"\n--- SELECT WRESTLER #{len(selected) + 1} (Need {6 - len(selected)} more minimum) ---")
            remaining = [w for w in available if w not in selected]

            for i, w in enumerate(remaining):
                print(f"{i+1}. {w.name} [{w.get_overall_rating()}] (Air: {w.air})")

            if len(selected) >= 6:
                print(f"{len(remaining) + 1}. Done selecting (proceed with {len(selected)} wrestlers)")

            try:
                choice = input("\nSelect: ")
                if len(selected) >= 6 and choice == str(len(remaining) + 1):
                    break  # Done selecting

                idx = int(choice) - 1
                if idx < 0 or idx >= len(remaining):
                    raise ValueError()
                wrestler = remaining[idx]
                selected.append(wrestler)
                print(f"Added: {wrestler.name}")
            except (ValueError, IndexError):
                if len(selected) >= 6:
                    print("Invalid selection. Enter a number or done option.")
                else:
                    print("Invalid selection.")
                continue

        if len(selected) < 6:
            print("Not enough wrestlers selected. Cancelled.")
            self._press_enter()
            return

        # Show summary
        print("\n--- MONEY IN THE BANK LADDER MATCH ---")
        for i, w in enumerate(selected):
            print(f"  {i+1}. {w.name} (Air: {w.air})")

        confirm = input("\nConfirm this Money in the Bank match? (y/n): ").lower()
        if confirm != 'y':
            print("Cancelled.")
            self._press_enter()
            return

        success, message = self.game.add_mitb_match_to_show(selected)
        print(f"\n{message}")
        self._press_enter()

    # --- Feud Operations ---

    def _feud_management_screen(self):
        """Feud management menu."""
        while True:
            self._clear_screen()
            self._print_header("FEUD MANAGEMENT")

            active_feuds = self.game.get_active_feuds()
            print(f"Active Feuds: {len(active_feuds)}")

            print("\n1. View Active Feuds")
            print("2. View All Feuds (including ended)")
            print("3. Start New Feud")
            print("4. End Feud")
            print("5. Schedule Blowoff Match")
            print("6. Back to Main Menu")

            choice = input("\nSelect: ")

            if choice == '1':
                self._view_feuds(active_only=True)
            elif choice == '2':
                self._view_feuds(active_only=False)
            elif choice == '3':
                self._create_feud_flow()
            elif choice == '4':
                self._end_feud_flow()
            elif choice == '5':
                self._schedule_blowoff_flow()
            elif choice == '6':
                break

    def _view_feuds(self, active_only: bool = True):
        """Display feuds."""
        self._clear_screen()
        if active_only:
            self._print_header("ACTIVE FEUDS")
            feuds = self.game.get_active_feuds()
        else:
            self._print_header("ALL FEUDS")
            feuds = self.game.get_feuds()

        if not feuds:
            print("\nNo feuds to display.")
        else:
            for feud in feuds:
                wrestler_a = self.game.get_wrestler_by_id(feud.wrestler_a_id)
                wrestler_b = self.game.get_wrestler_by_id(feud.wrestler_b_id)
                a_name = wrestler_a.name if wrestler_a else "Unknown"
                b_name = wrestler_b.name if wrestler_b else "Unknown"

                status = "ACTIVE" if feud.is_active else "ENDED"
                blowoff = " [BLOWOFF SCHEDULED]" if feud.blowoff_match_scheduled and feud.is_active else ""

                print(f"\n[{status}] {a_name} vs {b_name}{blowoff}")
                print(f"    Intensity: {feud.intensity.upper()} (+{feud.get_intensity_bonus()} rating bonus)")
                print(f"    Score: {feud.get_score_string()} | Matches: {feud.total_matches} (Remaining: {feud.matches_remaining})")

        self._press_enter()

    def _create_feud_flow(self):
        """Flow for creating a new feud."""
        self._clear_screen()
        self._print_header("START NEW FEUD")

        roster = self.game.state.roster

        # Filter wrestlers not already in a feud
        available = [w for w in roster if not self.game.state.is_wrestler_in_feud(w.id)]

        if len(available) < 2:
            print("\nNot enough available wrestlers to start a feud!")
            print("(Each wrestler can only be in one active feud at a time)")
            self._press_enter()
            return

        print("\n--- SELECT FIRST WRESTLER ---")
        for i, w in enumerate(available):
            print(f"{i+1}. {w.name} [{w.get_overall_rating()}]")

        try:
            idx_a = int(input("\nSelect: ")) - 1
            if idx_a < 0 or idx_a >= len(available):
                raise ValueError()
            wrestler_a = available[idx_a]
        except (ValueError, IndexError):
            return

        # Filter out selected wrestler
        remaining = [w for w in available if w != wrestler_a]

        print(f"\n--- SELECT RIVAL FOR {wrestler_a.name} ---")
        for i, w in enumerate(remaining):
            print(f"{i+1}. {w.name} [{w.get_overall_rating()}]")

        try:
            idx_b = int(input("\nSelect: ")) - 1
            if idx_b < 0 or idx_b >= len(remaining):
                raise ValueError()
            wrestler_b = remaining[idx_b]
        except (ValueError, IndexError):
            return

        # Select intensity
        print("\n--- SELECT INTENSITY ---")
        print("1. Heated (+3 rating bonus) - Default starting point")
        print("2. Intense (+6 rating bonus) - Established rivalry")
        print("3. Blood Feud (+10 rating bonus) - Personal and violent")
        intensity_choice = input("Select [1]: ").strip()
        if intensity_choice == '2':
            intensity = "intense"
        elif intensity_choice == '3':
            intensity = "blood"
        else:
            intensity = "heated"

        # Select duration
        print("\n--- SELECT DURATION ---")
        print("How many matches before the feud auto-resolves?")
        matches_str = input("Number of matches [3]: ").strip()
        try:
            matches = int(matches_str) if matches_str else 3
            matches = max(1, min(10, matches))
        except ValueError:
            matches = 3

        # Confirm
        print(f"\n--- CONFIRM ---")
        print(f"Feud: {wrestler_a.name} vs {wrestler_b.name}")
        print(f"Intensity: {intensity.upper()} (+{3 if intensity == 'heated' else 6 if intensity == 'intense' else 10} bonus)")
        print(f"Duration: {matches} matches")

        confirm = input("\nStart this feud? (y/n): ").lower()
        if confirm != 'y':
            print("Cancelled.")
            self._press_enter()
            return

        success, message = self.game.create_feud(wrestler_a.id, wrestler_b.id, intensity, matches)
        print(f"\n{message}")
        self._press_enter()

    def _end_feud_flow(self):
        """Flow for manually ending a feud."""
        self._clear_screen()
        self._print_header("END FEUD")

        feuds = self.game.get_active_feuds()

        if not feuds:
            print("\nNo active feuds to end.")
            self._press_enter()
            return

        print("\n--- SELECT FEUD TO END ---")
        for i, feud in enumerate(feuds):
            wrestler_a = self.game.get_wrestler_by_id(feud.wrestler_a_id)
            wrestler_b = self.game.get_wrestler_by_id(feud.wrestler_b_id)
            a_name = wrestler_a.name if wrestler_a else "Unknown"
            b_name = wrestler_b.name if wrestler_b else "Unknown"
            print(f"{i+1}. {a_name} vs {b_name} ({feud.intensity.upper()}, Score: {feud.get_score_string()})")

        try:
            idx = int(input("\nSelect: ")) - 1
            if idx < 0 or idx >= len(feuds):
                raise ValueError()
            feud = feuds[idx]
        except (ValueError, IndexError):
            return

        wrestler_a = self.game.get_wrestler_by_id(feud.wrestler_a_id)
        wrestler_b = self.game.get_wrestler_by_id(feud.wrestler_b_id)
        a_name = wrestler_a.name if wrestler_a else "Unknown"
        b_name = wrestler_b.name if wrestler_b else "Unknown"

        confirm = input(f"\nAre you sure you want to end the feud between {a_name} and {b_name}? (y/n): ").lower()
        if confirm != 'y':
            print("Cancelled.")
            self._press_enter()
            return

        success, message = self.game.end_feud(feud.id)
        print(f"\n{message}")
        self._press_enter()

    def _schedule_blowoff_flow(self):
        """Flow for scheduling a blowoff match."""
        self._clear_screen()
        self._print_header("SCHEDULE BLOWOFF MATCH")

        feuds = [f for f in self.game.get_active_feuds() if not f.blowoff_match_scheduled]

        if not feuds:
            print("\nNo active feuds available for blowoff scheduling.")
            print("(Feuds with blowoff already scheduled are excluded)")
            self._press_enter()
            return

        print("\n--- SELECT FEUD FOR BLOWOFF ---")
        print("(The next match between these wrestlers will end the feud)")
        for i, feud in enumerate(feuds):
            wrestler_a = self.game.get_wrestler_by_id(feud.wrestler_a_id)
            wrestler_b = self.game.get_wrestler_by_id(feud.wrestler_b_id)
            a_name = wrestler_a.name if wrestler_a else "Unknown"
            b_name = wrestler_b.name if wrestler_b else "Unknown"
            print(f"{i+1}. {a_name} vs {b_name} ({feud.intensity.upper()}, Score: {feud.get_score_string()})")

        try:
            idx = int(input("\nSelect: ")) - 1
            if idx < 0 or idx >= len(feuds):
                raise ValueError()
            feud = feuds[idx]
        except (ValueError, IndexError):
            return

        success, message = self.game.schedule_blowoff_match(feud.id)
        print(f"\n{message}")
        self._press_enter()

    # --- Stable Operations ---

    def _stable_management_screen(self):
        """Stable management menu."""
        while True:
            self._clear_screen()
            self._print_header("STABLE MANAGEMENT")

            active_stables = self.game.get_active_stables()
            print(f"Active Stables: {len(active_stables)}")

            print("\n1. View All Stables")
            print("2. Create Stable")
            print("3. Manage Stable")
            print("4. Back to Main Menu")

            choice = input("\nSelect: ")

            if choice == '1':
                self._view_stables()
            elif choice == '2':
                self._create_stable_flow()
            elif choice == '3':
                self._manage_stable_flow()
            elif choice == '4':
                break

    def _view_stables(self):
        """Display all active stables."""
        self._clear_screen()
        self._print_header("ACTIVE STABLES")

        stables = self.game.get_active_stables()
        roster = self.game.state.roster

        if not stables:
            print("\nNo active stables.")
        else:
            for stable in stables:
                members = stable.get_members(roster)
                leader = stable.get_leader(roster)
                power_rating = stable.get_power_rating(roster)

                print(f"\n[{power_rating}] {stable.name}")
                print(f"    Leader: {leader.name if leader else 'Unknown'}")
                print(f"    Members ({len(members)}):")
                for member in members:
                    leader_mark = " (LEADER)" if member.id == stable.leader_id else ""
                    print(f"      - {member.name} [{member.get_overall_rating()}]{leader_mark}")

        self._press_enter()

    def _create_stable_flow(self):
        """Flow for creating a new stable (minimum 3 members)."""
        self._clear_screen()
        self._print_header("CREATE STABLE")

        roster = self.game.state.roster

        # Filter wrestlers not already in a stable
        available = [w for w in roster if not self.game.state.is_wrestler_in_stable(w.id)]

        if len(available) < 3:
            print("\nNot enough available wrestlers to form a stable!")
            print("(A stable requires at least 3 members)")
            print("(Wrestlers can only be in one stable at a time)")
            self._press_enter()
            return

        # Get stable name
        stable_name = input("Stable name (e.g., 'nWo', 'Hart Foundation'): ").strip()
        if not stable_name:
            print("Stable name cannot be empty.")
            self._press_enter()
            return

        selected_members = []

        # Select members (minimum 3)
        print(f"\n--- SELECT MEMBERS (minimum 3) ---")
        print("(First selected will be the leader)")

        while True:
            remaining = [w for w in available if w not in selected_members]

            if not remaining:
                break

            print(f"\nCurrent members ({len(selected_members)}): ", end="")
            if selected_members:
                print(", ".join([m.name for m in selected_members]))
            else:
                print("None")

            for i, w in enumerate(remaining):
                print(f"{i+1}. {w.name} [{w.get_overall_rating()}]")

            print("\nD. Done selecting (if 3+ selected)")
            print("C. Cancel")

            choice = input("\nSelect: ").strip().upper()

            if choice == 'C':
                print("Cancelled.")
                self._press_enter()
                return
            elif choice == 'D':
                if len(selected_members) >= 3:
                    break
                else:
                    print(f"Need at least 3 members. Currently have {len(selected_members)}.")
                    continue
            else:
                try:
                    idx = int(choice) - 1
                    if idx < 0 or idx >= len(remaining):
                        raise ValueError()
                    wrestler = remaining[idx]
                    selected_members.append(wrestler)
                    role = "LEADER" if len(selected_members) == 1 else "member"
                    print(f"Added {wrestler.name} as {role}.")
                except (ValueError, IndexError):
                    print("Invalid selection.")
                    continue

        if len(selected_members) < 3:
            print("Not enough members selected. Cancelled.")
            self._press_enter()
            return

        # Show summary
        leader = selected_members[0]
        member_ids = [m.id for m in selected_members]

        print(f"\n--- CONFIRM ---")
        print(f"Stable Name: {stable_name}")
        print(f"Leader: {leader.name}")
        print(f"Members: {', '.join([m.name for m in selected_members])}")

        confirm = input("\nCreate this stable? (y/n): ").lower()
        if confirm != 'y':
            print("Cancelled.")
            self._press_enter()
            return

        success, message = self.game.create_stable(stable_name, leader.id, member_ids)
        print(f"\n{message}")
        self._press_enter()

    def _manage_stable_flow(self):
        """Flow for managing an existing stable."""
        self._clear_screen()
        self._print_header("MANAGE STABLE")

        stables = self.game.get_active_stables()
        roster = self.game.state.roster

        if not stables:
            print("\nNo active stables to manage.")
            self._press_enter()
            return

        print("\n--- SELECT STABLE ---")
        for i, stable in enumerate(stables):
            members = stable.get_members(roster)
            power = stable.get_power_rating(roster)
            print(f"{i+1}. {stable.name} [{power}] ({len(members)} members)")

        try:
            idx = int(input("\nSelect: ")) - 1
            if idx < 0 or idx >= len(stables):
                raise ValueError()
            stable = stables[idx]
        except (ValueError, IndexError):
            return

        # Manage selected stable
        while True:
            self._clear_screen()
            self._print_header(f"MANAGE: {stable.name}")

            members = stable.get_members(roster)
            leader = stable.get_leader(roster)
            power = stable.get_power_rating(roster)

            print(f"Power Rating: {power}")
            print(f"Leader: {leader.name if leader else 'Unknown'}")
            print(f"\nMembers ({len(members)}):")
            for member in members:
                leader_mark = " (LEADER)" if member.id == stable.leader_id else ""
                print(f"  - {member.name} [{member.get_overall_rating()}]{leader_mark}")

            print("\n1. Add Member")
            print("2. Remove Member")
            print("3. Change Leader")
            print("4. Disband Stable")
            print("5. Back")

            choice = input("\nSelect: ")

            if choice == '1':
                self._add_stable_member_flow(stable)
            elif choice == '2':
                self._remove_stable_member_flow(stable)
            elif choice == '3':
                self._change_stable_leader_flow(stable)
            elif choice == '4':
                if self._disband_stable_flow(stable):
                    break  # Stable was disbanded, exit management
            elif choice == '5':
                break

    def _add_stable_member_flow(self, stable):
        """Flow for adding a member to a stable."""
        roster = self.game.state.roster

        # Filter wrestlers not in any stable
        available = [w for w in roster if not self.game.state.is_wrestler_in_stable(w.id)]

        if not available:
            print("\nNo available wrestlers to add!")
            print("(All wrestlers are already in stables)")
            self._press_enter()
            return

        print(f"\n--- ADD MEMBER TO {stable.name} ---")
        for i, w in enumerate(available):
            print(f"{i+1}. {w.name} [{w.get_overall_rating()}]")

        try:
            idx = int(input("\nSelect: ")) - 1
            if idx < 0 or idx >= len(available):
                raise ValueError()
            wrestler = available[idx]
        except (ValueError, IndexError):
            return

        success, message = self.game.add_member_to_stable(stable.id, wrestler.id)
        print(f"\n{message}")
        self._press_enter()

    def _remove_stable_member_flow(self, stable):
        """Flow for removing a member from a stable."""
        roster = self.game.state.roster
        members = stable.get_members(roster)

        if len(members) <= 3:
            print("\nCannot remove members - stable must have at least 3 members!")
            self._press_enter()
            return

        print(f"\n--- REMOVE MEMBER FROM {stable.name} ---")
        for i, member in enumerate(members):
            leader_mark = " (LEADER)" if member.id == stable.leader_id else ""
            print(f"{i+1}. {member.name}{leader_mark}")

        try:
            idx = int(input("\nSelect: ")) - 1
            if idx < 0 or idx >= len(members):
                raise ValueError()
            wrestler = members[idx]
        except (ValueError, IndexError):
            return

        confirm = input(f"\nRemove {wrestler.name} from '{stable.name}'? (y/n): ").lower()
        if confirm != 'y':
            print("Cancelled.")
            self._press_enter()
            return

        success, message = self.game.remove_member_from_stable(stable.id, wrestler.id)
        print(f"\n{message}")
        self._press_enter()

    def _change_stable_leader_flow(self, stable):
        """Flow for changing the leader of a stable."""
        roster = self.game.state.roster
        members = stable.get_members(roster)

        # Filter out current leader
        candidates = [m for m in members if m.id != stable.leader_id]

        if not candidates:
            print("\nNo other members to promote!")
            self._press_enter()
            return

        current_leader = stable.get_leader(roster)
        print(f"\n--- CHANGE LEADER OF {stable.name} ---")
        print(f"Current Leader: {current_leader.name if current_leader else 'Unknown'}")
        print("\nSelect new leader:")

        for i, member in enumerate(candidates):
            print(f"{i+1}. {member.name} [{member.get_overall_rating()}]")

        try:
            idx = int(input("\nSelect: ")) - 1
            if idx < 0 or idx >= len(candidates):
                raise ValueError()
            new_leader = candidates[idx]
        except (ValueError, IndexError):
            return

        confirm = input(f"\nMake {new_leader.name} the new leader of '{stable.name}'? (y/n): ").lower()
        if confirm != 'y':
            print("Cancelled.")
            self._press_enter()
            return

        success, message = self.game.set_stable_leader(stable.id, new_leader.id)
        print(f"\n{message}")
        self._press_enter()

    def _disband_stable_flow(self, stable) -> bool:
        """Flow for disbanding a stable. Returns True if disbanded."""
        confirm = input(f"\nAre you sure you want to disband '{stable.name}'? (y/n): ").lower()
        if confirm != 'y':
            print("Cancelled.")
            self._press_enter()
            return False

        success, message = self.game.disband_stable(stable.id)
        print(f"\n{message}")
        self._press_enter()
        return success

    # --- Records & History ---

    def _records_menu_screen(self):
        """Records and history menu."""
        while True:
            self._clear_screen()
            self._print_header("RECORDS & HISTORY")

            match_count = len(self.game.get_match_history(limit=0))
            print(f"Total Matches Recorded: {match_count}")

            print("\n1. View Recent Matches")
            print("2. Wrestler Records")
            print("3. Head-to-Head Lookup")
            print("4. Title History")
            print("5. Back to Main Menu")

            choice = input("\nSelect: ")

            if choice == '1':
                self._view_recent_matches()
            elif choice == '2':
                self._view_wrestler_records()
            elif choice == '3':
                self._head_to_head_lookup()
            elif choice == '4':
                self._view_title_history()
            elif choice == '5':
                break

    def _view_recent_matches(self):
        """Display recent match history."""
        self._clear_screen()
        self._print_header("RECENT MATCHES")

        matches = self.game.get_match_history(limit=20)

        if not matches:
            print("\nNo match history yet. Run some shows!")
        else:
            # Display in reverse order (most recent first)
            for match in reversed(matches):
                ppv_tag = "[PPV] " if match.is_ppv else ""
                date_str = f"Y{match.date['year']} M{match.date['month']} W{match.date['week']}"

                print(f"\n{ppv_tag}{match.show_name} ({date_str})")
                print(f"  {match.match_type}: {' vs '.join(match.participant_names)}")

                if match.winner_names:
                    print(f"  Winner: {', '.join(match.winner_names)}")
                else:
                    print(f"  Result: DRAW")

                print(f"  Rating: {match.rating}/100 ({match.stars:.1f} stars)")

                if match.is_title_match:
                    if match.title_changed:
                        print(f"  *** TITLE CHANGE: {match.title_name} ***")
                    else:
                        print(f"  Title Defense: {match.title_name}")

        self._press_enter()

    def _view_wrestler_records(self):
        """View detailed records for a specific wrestler."""
        self._clear_screen()
        self._print_header("WRESTLER RECORDS")

        roster = self.game.get_roster()

        print("\n--- SELECT WRESTLER ---")
        for i, w in enumerate(roster):
            # Get records for streak indicator
            records = self.game.get_wrestler_records(w.id)
            streak_str = ""
            if records:
                if records.current_win_streak >= 3:
                    streak_str = f" [W{records.current_win_streak}]"
                elif records.current_loss_streak >= 3:
                    streak_str = f" [L{records.current_loss_streak}]"
            print(f"{i+1}. {w.name} ({w.wins}W-{w.losses}L){streak_str}")

        try:
            idx = int(input("\nSelect: ")) - 1
            if idx < 0 or idx >= len(roster):
                raise ValueError()
            wrestler = roster[idx]
        except (ValueError, IndexError):
            return

        # Display wrestler records
        self._clear_screen()
        self._print_header(f"RECORDS: {wrestler.name}")

        records = self.game.get_wrestler_records(wrestler.id)

        print(f"\n--- OVERALL ---")
        print(f"  Total Record: {wrestler.wins}W - {wrestler.losses}L")

        print(f"\n--- STREAKS ---")
        print(f"  Current Win Streak: {records.current_win_streak}")
        print(f"  Current Loss Streak: {records.current_loss_streak}")
        print(f"  Longest Win Streak: {records.longest_win_streak}")
        print(f"  Longest Loss Streak: {records.longest_loss_streak}")

        print(f"\n--- PPV vs TV ---")
        print(f"  PPV Record: {records.ppv_wins}W - {records.ppv_losses}L")
        print(f"  TV Record: {records.tv_wins}W - {records.tv_losses}L")

        # Recent matches
        recent = self.game.get_wrestler_match_history(wrestler.id, limit=5)
        if recent:
            print(f"\n--- RECENT MATCHES ---")
            for match in reversed(recent):
                result = "W" if wrestler.id in match.winner_ids else ("L" if wrestler.id in match.loser_ids else "D")
                ppv_tag = "[PPV]" if match.is_ppv else "[TV]"
                print(f"  {ppv_tag} {result} - {match.match_type} vs {', '.join([n for n in match.participant_names if n != wrestler.name])}")

        self._press_enter()

    def _head_to_head_lookup(self):
        """Look up head-to-head record between two wrestlers."""
        self._clear_screen()
        self._print_header("HEAD-TO-HEAD LOOKUP")

        roster = self.game.get_roster()

        print("\n--- SELECT WRESTLER A ---")
        for i, w in enumerate(roster):
            print(f"{i+1}. {w.name}")

        try:
            idx_a = int(input("\nSelect: ")) - 1
            if idx_a < 0 or idx_a >= len(roster):
                raise ValueError()
            wrestler_a = roster[idx_a]
        except (ValueError, IndexError):
            return

        remaining = [w for w in roster if w != wrestler_a]

        print(f"\n--- SELECT OPPONENT FOR {wrestler_a.name} ---")
        for i, w in enumerate(remaining):
            print(f"{i+1}. {w.name}")

        try:
            idx_b = int(input("\nSelect: ")) - 1
            if idx_b < 0 or idx_b >= len(remaining):
                raise ValueError()
            wrestler_b = remaining[idx_b]
        except (ValueError, IndexError):
            return

        # Get head-to-head data
        h2h = self.game.get_head_to_head(wrestler_a.id, wrestler_b.id)

        self._clear_screen()
        self._print_header(f"HEAD-TO-HEAD: {wrestler_a.name} vs {wrestler_b.name}")

        print(f"\n--- OVERALL RECORD ---")
        print(f"  {wrestler_a.name}: {h2h['wins_a']} wins")
        print(f"  {wrestler_b.name}: {h2h['wins_b']} wins")
        print(f"  Total Matches: {h2h['total_matches']}")

        if h2h['matches']:
            print(f"\n--- MATCH HISTORY ---")
            for match in reversed(h2h['matches']):
                date_str = f"Y{match.date['year']} M{match.date['month']} W{match.date['week']}"
                winner = match.winner_names[0] if match.winner_names else "DRAW"
                ppv_tag = "[PPV]" if match.is_ppv else "[TV]"
                print(f"  {ppv_tag} {date_str}: {match.match_type} - Winner: {winner} ({match.stars:.1f}*)")
                if match.title_changed:
                    print(f"        *** {match.title_name} changed hands ***")

        self._press_enter()

    def _view_title_history(self):
        """View reign history for a specific title."""
        self._clear_screen()
        self._print_header("TITLE HISTORY")

        titles = self.game.get_titles()

        if not titles:
            print("\nNo championships exist.")
            self._press_enter()
            return

        print("\n--- SELECT TITLE ---")
        for i, title in enumerate(titles):
            print(f"{i+1}. {title.name} [Prestige: {title.prestige}]")

        try:
            idx = int(input("\nSelect: ")) - 1
            if idx < 0 or idx >= len(titles):
                raise ValueError()
            title = titles[idx]
        except (ValueError, IndexError):
            return

        # Get title history
        history = self.game.get_title_history(title.id)

        self._clear_screen()
        self._print_header(f"TITLE HISTORY: {title.name}")

        # Current champion
        if title.current_holder_id:
            holder = self.game.get_wrestler_by_id(title.current_holder_id)
            if not holder:
                # Try tag team
                team = self.game.get_tag_team_by_id(title.current_holder_id)
                holder_name = team.name if team else "Unknown"
            else:
                holder_name = holder.name
            print(f"\nCurrent Champion: {holder_name}")
        else:
            print(f"\nCurrent Champion: VACANT")

        if not history:
            print("\nNo reign history recorded yet.")
        else:
            print(f"\n--- REIGN HISTORY ({len(history)} reigns) ---")
            for reign in reversed(history):
                won_date = f"Y{reign.won_date['year']} M{reign.won_date['month']} W{reign.won_date['week']}"
                if reign.lost_date:
                    lost_date = f"Y{reign.lost_date['year']} M{reign.lost_date['month']} W{reign.lost_date['week']}"
                    status = f"Lost: {lost_date}"
                else:
                    status = "CURRENT"

                print(f"\n  {reign.holder_name}")
                print(f"    Won: {won_date} | {status}")
                print(f"    Successful Defenses: {reign.successful_defenses}")

        self._press_enter()

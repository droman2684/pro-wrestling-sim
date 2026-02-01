import sys
import os

# Add the 'src' directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import flet as ft
from services.game_service import GameService # Import GameService

class MainApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Simple Sim Sports: Pro Wrestling"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.game_service = GameService() # Initialize GameService

        self.page.on_route_change = self.route_change
        self.page.route = "/"
        self.route_change(None)
        self.page.update()
        
    def route_change(self, route):
        self.page.views.clear()
        self.page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(title=ft.Text("Simple Sim Sports: Pro Wrestling")),
                    self._init_start_menu_view()
                ]
            )
        )
        if self.page.route == "/head_office":
            self.page.views.append(
                ft.View(
                    "/head_office",
                    [
                        ft.AppBar(title=ft.Text("Head Office"), leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: self.go_to("/"))),
                        self._init_head_office_view()
                    ]
                )
            )
        elif self.page.route == "/roster":
            self.page.views.append(
                ft.View(
                    "/roster",
                    [
                        ft.AppBar(title=ft.Text("Roster"), leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: self.go_to("/head_office"))),
                        self._init_roster_view()
                    ]
                )
            )
        elif self.page.route == "/rankings":
            self.page.views.append(
                ft.View(
                    "/rankings",
                    [
                        ft.AppBar(title=ft.Text("Rankings"), leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: self.go_to("/head_office"))),
                        self._init_rankings_view()
                    ]
                )
            )
        elif self.page.route == "/book_show":
            self.page.views.append(
                ft.View(
                    "/book_show",
                    [
                        ft.AppBar(title=ft.Text("Book a Show"), leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: self._cancel_booking_and_go_head_office(e))),
                        self._init_book_show_view()
                    ]
                )
            )
        elif self.page.route == "/show_results":
            # Retrieve the ShowResult from session or client_storage
            # self.page.client_storage is generally persistent, self.page.session is per session
            show_result = self.page.client_storage.get("current_show_result") 
            self.page.views.append(
                ft.View(
                    "/show_results",
                    [
                        ft.AppBar(title=ft.Text("Show Results"), leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: self.go_to("/head_office"))),
                        self._init_show_results_view(show_result)
                    ]
                )
            )
        elif self.page.route == "/tag_team_management":
            self.page.views.append(
                ft.View(
                    "/tag_team_management",
                    [
                        ft.AppBar(title=ft.Text("Tag Team Management"), leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: self.go_to("/head_office"))),
                        self._init_tag_team_management_view()
                    ]
                )
            )
        elif self.page.route == "/calendar":
            self.page.views.append(
                ft.View(
                    "/calendar",
                    [
                        ft.AppBar(title=ft.Text("Calendar"), leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: self.go_to("/head_office"))),
                        self._init_calendar_view()
                    ]
                )
            )
        elif self.page.route == "/champions":
            self.page.views.append(
                ft.View(
                    "/champions",
                    [
                        ft.AppBar(title=ft.Text("Champions"), leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: self.go_to("/head_office"))),
                        self._init_champions_view()
                    ]
                )
            )
        elif self.page.route == "/finances":
            self.page.views.append(
                ft.View(
                    "/finances",
                    [
                        ft.AppBar(title=ft.Text("Finances"), leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: self.go_to("/head_office"))),
                        self._init_finances_view()
                    ]
                )
            )
        self.page.update()
        
    def go_to(self, route):
        self.page.route = route
        self.route_change(None)
        self.page.update()
    
    def _show_message_dialog(self, title: str, message: str):
        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("Ok", on_click=lambda e: self._close_dialog(e)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

    def _close_dialog(self, e):
        self.page.dialog.open = False
        self.page.update()

    def _init_start_menu_view(self) -> ft.Control:
        """Creates the content for the Start Menu screen."""
        def new_game_click(e):
            self._show_new_game_dialog()

        def load_game_click(e):
            self._show_load_game_dialog()

        return ft.Column(
            [
                ft.Text("Welcome to Simple Sim Sports: Pro Wrestling!", size=30),
                ft.ElevatedButton("New Game", on_click=new_game_click),
                ft.ElevatedButton("Load Game", on_click=load_game_click),
                ft.ElevatedButton("Exit", on_click=lambda e: self.page.window.close())
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )

    def _show_new_game_dialog(self):
        db_options = self.game_service.list_databases()
        if not db_options:
            self._show_message_dialog("Error", "No database templates found. Please check 'data/databases/'.")
            return

        selected_db = ft.Dropdown(
            label="Select Database",
            options=[ft.dropdown.Option(db) for db in db_options],
            width=200
        )
        save_name_field = ft.TextField(label="Save Game Name", width=200)

        def create_game(e):
            if not selected_db.value:
                self._show_message_dialog("Error", "Please select a database.")
                return
            if not save_name_field.value:
                self._show_message_dialog("Error", "Please enter a save game name.")
                return

            success, message = self.game_service.create_new_game(selected_db.value, save_name_field.value)
            self._close_dialog(e)
            self._show_message_dialog("New Game", message)
            if success:
                self.go_to("/head_office")

        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Create New Game"),
            content=ft.Column([selected_db, save_name_field], tight=True),
            actions=[
                ft.TextButton("Create", on_click=create_game),
                ft.TextButton("Cancel", on_click=self._close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

    def _show_load_game_dialog(self):
        save_options = self.game_service.list_saves()
        if not save_options:
            self._show_message_dialog("Error", "No save games found.")
            return

        selected_save = ft.Dropdown(
            label="Select Save Game",
            options=[ft.dropdown.Option(save) for save in save_options],
            width=200
        )

        def load_game(e):
            if not selected_save.value:
                self._show_message_dialog("Error", "Please select a save game.")
                return

            success, message = self.game_service.load_game(selected_save.value)
            self._close_dialog(e)
            self._show_message_dialog("Load Game", message)
            if success:
                self.go_to("/head_office")

        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Load Game"),
            content=ft.Column([selected_save], tight=True),
            actions=[
                ft.TextButton("Load", on_click=load_game),
                ft.TextButton("Cancel", on_click=self._close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

    def _save_game_click(self, e):
        """Saves the current game state and shows a confirmation dialog."""
        success, message = self.game_service.save_game()
        self._show_message_dialog("Save Game", message)

    def _sim_to_next_ppv_click(self, e):
        """Simulates all weeks until the next PPV and shows a summary."""
        results = self.game_service.sim_to_next_ppv()
        if not results:
            self._show_message_dialog("Simulate to PPV", "No upcoming PPV found or simulation failed.")
            return
        
        summary = f"Simulated {len(results)} weeks. Reached {self.game_service.get_current_date_string()}."
        self._show_message_dialog("Simulate to PPV", summary)
        self.go_to("/head_office")


    def _init_head_office_view(self) -> ft.Control:
        """Creates the content for the Head Office screen."""
        return ft.Column(
            [
                ft.Text(f"Head Office - {self.game_service.get_save_name()} Loaded!", size=30),
                ft.Text(self.game_service.get_current_date_string(), size=20),
                ft.Text(self.game_service.get_next_ppv_string(), size=16),
                ft.ElevatedButton("View Roster", on_click=lambda e: self.go_to("/roster")),
                ft.ElevatedButton("Play This Week's Show", on_click=lambda e: self.go_to("/book_show")),
                ft.ElevatedButton("Sim to Next PPV", on_click=self._sim_to_next_ppv_click),
                ft.ElevatedButton("Champions", on_click=lambda e: self.go_to("/champions")),
                ft.ElevatedButton("Tag Team Management", on_click=lambda e: self.go_to("/tag_team_management")),
                ft.ElevatedButton("View Rankings", on_click=lambda e: self.go_to("/rankings")),
                ft.ElevatedButton("Calendar", on_click=lambda e: self.go_to("/calendar")),
                ft.ElevatedButton("Finances", on_click=lambda e: self.go_to("/finances")),
                ft.ElevatedButton("Save Game", on_click=self._save_game_click),
                ft.ElevatedButton("Exit to Main Menu", on_click=lambda e: self.go_to("/")),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )

    def _init_roster_view(self) -> ft.Control:
        """Creates the content for the Roster screen."""
        roster = self.game_service.get_roster()
        
        if not roster:
            return ft.Column([ft.Text("No wrestlers in the roster.")], alignment=ft.MainAxisAlignment.CENTER)

        rows = []
        for wrestler in roster:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(wrestler.name)),
                        ft.DataCell(ft.Text(wrestler.gimmick)),
                        ft.DataCell(ft.Text(str(wrestler.get_overall_rating()))),
                        ft.DataCell(ft.Text(str(wrestler.wins))),
                        ft.DataCell(ft.Text(str(wrestler.losses))),
                    ]
                )
            )

        return ft.Column(
            [
                ft.Text("Current Roster", size=30),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Name")),
                        ft.DataColumn(ft.Text("Gimmick")),
                        ft.DataColumn(ft.Text("Overall")),
                        ft.DataColumn(ft.Text("W")),
                        ft.DataColumn(ft.Text("L")),
                    ],
                    rows=rows,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )

    def _init_rankings_view(self) -> ft.Control:
        """Creates the content for the Rankings screen."""
        wrestler_rankings = self.game_service.get_wrestler_rankings()
        tag_team_rankings = self.game_service.get_tag_team_rankings()
        roster = self.game_service.state.roster if self.game_service.is_game_loaded else []

        rankings_content = []

        # Singles Rankings
        rankings_content.append(ft.Text("SINGLES RANKINGS (TOP 5)", size=24, weight=ft.FontWeight.BOLD))
        if not wrestler_rankings:
            rankings_content.append(ft.Text("No wrestlers currently ranked."))
        else:
            for i, wrestler in enumerate(wrestler_rankings[:5]):
                rankings_content.append(ft.Text(f"#{i+1}. {wrestler.name} ({wrestler.gimmick}) - {wrestler.wins}W / {wrestler.losses}L"))
        
        rankings_content.append(ft.Divider()) # Separator

        # Tag Team Rankings
        rankings_content.append(ft.Text("TAG TEAM RANKINGS (TOP 5)", size=24, weight=ft.FontWeight.BOLD))
        if not tag_team_rankings:
            rankings_content.append(ft.Text("No tag teams currently ranked."))
        else:
            for i, team in enumerate(tag_team_rankings[:5]):
                members = team.get_members(roster)
                member_names = " & ".join([m.name for m in members])
                rankings_content.append(ft.Text(f"#{i+1}. {team.name} - {team.wins}W / {team.losses}L ({member_names})"))

        return ft.Column(
            rankings_content,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.START,
            expand=True,
            scroll=ft.ScrollMode.ALWAYS,
        )

    def _init_calendar_view(self) -> ft.Control:
        """Creates the content for the Calendar screen."""
        ppv_schedule = self.game_service.get_ppv_schedule()
        
        rows = []
        for ppv in ppv_schedule:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"Month {ppv['month']}")),
                        ft.DataCell(ft.Text(ppv['name'])),
                        ft.DataCell(ft.Text(ppv['tier'])),
                    ]
                )
            )

        return ft.Column(
            [
                ft.Text("PPV Calendar", size=30),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Month")),
                        ft.DataColumn(ft.Text("Event")),
                        ft.DataColumn(ft.Text("Tier")),
                    ],
                    rows=rows,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.START,
            expand=True,
        )
    
    def _init_champions_view(self) -> ft.Control:
        """Creates the content for the Champions screen."""
        titles = self.game_service.get_titles()
        
        if not titles:
            return ft.Column([ft.Text("No titles found.")], alignment=ft.MainAxisAlignment.CENTER)

        champions_content = [ft.Text("Champions", size=30)]
        for title in titles:
            holder = self.game_service.get_wrestler_by_id(title.current_holder_id) if title.current_holder_id else None
            holder_name = holder.name if holder else "Vacant"
            champions_content.append(ft.Text(f"{title.name}: {holder_name}", size=20))
            
        return ft.Column(
            champions_content,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.START,
            expand=True,
        )
        
    def _init_finances_view(self) -> ft.Control:
        """Creates the content for the Finances screen."""
        company = self.game_service.get_company()
        if not company:
            return ft.Column([ft.Text("No company data available.")], alignment=ft.MainAxisAlignment.CENTER)

        return ft.Column(
            [
                ft.Text("Finances", size=30),
                ft.Text(f"Bank Account: ${company.bank_account:,}", size=24),
                ft.Text(f"Prestige: {company.prestige}", size=24),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        )

    # --- Book Show View ---
    def _cancel_booking_and_go_head_office(self, e):
        """Cancels any current show booking and navigates back to Head Office."""
        self.game_service.cancel_show()
        self.go_to("/head_office")

    def _update_book_show_view(self):
        """Re-navigates to the book_show route to refresh the view."""
        self.go_to("/book_show")

    def _show_add_singles_match_dialog(self):
        if not self.game_service.is_game_loaded:
            self._show_message_dialog("Error", "No game loaded.")
            return

        available_wrestlers = [w for w in self.game_service.state.roster if not self.game_service.is_wrestler_booked_on_show(w.id)]
        
        if len(available_wrestlers) < 2:
            self._show_message_dialog("Error", "Not enough available wrestlers to book a singles match.")
            return

        wrestler_options = [ft.dropdown.Option(str(w.id), text=f"{w.name} ({w.gimmick})") for w in available_wrestlers]

        wrestler_a_dropdown = ft.Dropdown(
            label="Wrestler A",
            options=wrestler_options,
            width=300
        )
        wrestler_b_dropdown = ft.Dropdown(
            label="Wrestler B",
            options=wrestler_options,
            width=300
        )
        is_steel_cage_checkbox = ft.Checkbox(label="Steel Cage Match", value=False)
        
        title_options = [ft.dropdown.Option(str(t.id), text=t.name) for t in self.game_service.get_titles()]
        title_dropdown = ft.Dropdown(label="Title on the line", options=title_options, width=300)


        def add_match(e):
            if not wrestler_a_dropdown.value or not wrestler_b_dropdown.value:
                self._show_message_dialog("Error", "Please select both wrestlers.")
                return
            
            wrestler_a_id = int(wrestler_a_dropdown.value)
            wrestler_b_id = int(wrestler_b_dropdown.value)

            if wrestler_a_id == wrestler_b_id:
                self._show_message_dialog("Error", "A wrestler cannot fight themselves!")
                return
            
            wrestler_a = self.game_service.get_wrestler_by_id(wrestler_a_id)
            wrestler_b = self.game_service.get_wrestler_by_id(wrestler_b_id)
            
            is_title = title_dropdown.value is not None
            title_id = int(title_dropdown.value) if is_title else None

            success = self.game_service.add_match_to_show(wrestler_a, wrestler_b, is_steel_cage=is_steel_cage_checkbox.value, is_title_match=is_title, title_id=title_id)
            self._close_dialog(e)
            if success:
                self._show_message_dialog("Success", f"Singles match added: {wrestler_a.name} vs {wrestler_b.name}")
                self._update_book_show_view() # Refresh the view
            else:
                self._show_message_dialog("Error", "Could not add singles match.")

        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add Singles Match"),
            content=ft.Column([
                wrestler_a_dropdown,
                wrestler_b_dropdown,
                is_steel_cage_checkbox,
                title_dropdown
            ], tight=True),
            actions=[
                ft.TextButton("Add Match", on_click=add_match),
                ft.TextButton("Cancel", on_click=self._close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

    def _show_add_tag_match_dialog(self):
        if not self.game_service.is_game_loaded:
            self._show_message_dialog("Error", "No game loaded.")
            return

        available_teams = [t for t in self.game_service.get_available_tag_teams()]
        
        if len(available_teams) < 2:
            self._show_message_dialog("Error", "Not enough available tag teams to book a tag match.")
            return

        team_options = []
        for team in available_teams:
            members = team.get_members(self.game_service.state.roster)
            member_names = " & ".join([m.name for m in members])
            team_options.append(ft.dropdown.Option(str(team.id), text=f"{team.name} ({member_names})"))

        team_a_dropdown = ft.Dropdown(
            label="Team A",
            options=team_options,
            width=300
        )
        team_b_dropdown = ft.Dropdown(
            label="Team B",
            options=team_options,
            width=300
        )
        is_steel_cage_checkbox = ft.Checkbox(label="Steel Cage Match", value=False)
        
        title_options = [ft.dropdown.Option(str(t.id), text=t.name) for t in self.game_service.get_titles()]
        title_dropdown = ft.Dropdown(label="Title on the line", options=title_options, width=300)

        def add_tag_match(e):
            if not team_a_dropdown.value or not team_b_dropdown.value:
                self._show_message_dialog("Error", "Please select both teams.")
                return
            
            team_a_id = int(team_a_dropdown.value)
            team_b_id = int(team_b_dropdown.value)

            if team_a_id == team_b_id:
                self._show_message_dialog("Error", "A team cannot fight themselves!")
                return
            
            team_a = self.game_service.get_tag_team_by_id(team_a_id)
            team_b = self.game_service.get_tag_team_by_id(team_b_id)
            
            is_title = title_dropdown.value is not None
            title_id = int(title_dropdown.value) if is_title else None

            success = self.game_service.add_tag_match_to_show(team_a, team_b, is_steel_cage=is_steel_cage_checkbox.value, is_title_match=is_title, title_id=title_id)
            self._close_dialog(e)
            if success:
                self._show_message_dialog("Success", f"Tag match added: {team_a.name} vs {team_b.name}")
                self._update_book_show_view() # Refresh the view
            else:
                self._show_message_dialog("Error", "Could not add tag match.")

        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add Tag Team Match"),
            content=ft.Column([
                team_a_dropdown,
                team_b_dropdown,
                is_steel_cage_checkbox,
                title_dropdown
            ], tight=True),
            actions=[
                ft.TextButton("Add Match", on_click=add_tag_match),
                ft.TextButton("Cancel", on_click=self._close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()


    def _init_book_show_view(self) -> ft.Control:
        """Creates the content for booking a new show."""
        current_show = self.game_service.get_current_show()
        
        show_name_field = ft.TextField(label="Show Name", width=300, value=current_show.name if current_show else "")
        show_name_field.disabled = current_show is not None # Disable if show already created

        def start_booking(e):
            if not show_name_field.value:
                self._show_message_dialog("Error", "Please enter a show name.")
                return
            success = self.game_service.create_show(show_name_field.value)
            if success:
                self._show_message_dialog("Success", f"Show '{show_name_field.value}' created. Start adding matches!")
                self._update_book_show_view() # Refresh the view
            else:
                self._show_message_dialog("Error", "Could not create show. Is one already active?")
            self.page.update()
        
        def run_show_click(e):
            result = self.game_service.play_show()
            if result:
                # Store the result in client_storage for the results view to pick up
                self.page.client_storage.set("current_show_result", result) 
                self.go_to("/show_results")
            else:
                self._show_message_dialog("Error", "Could not run show. Make sure matches are booked.")


        match_list_controls = []
        if current_show and current_show.matches:
            for i, match in enumerate(current_show.matches):
                if match.match_type == "Tag Team":
                    match_title = f"Tag: {match.team_a.name} vs {match.team_b.name}"
                else:
                    match_title = f"Singles: {match.p1.name} vs {match.p2.name}"
                if match.is_steel_cage:
                    match_title += " (Steel Cage)"
                match_list_controls.append(ft.Text(f"{i+1}. {match_title}"))
        else:
            match_list_controls.append(ft.Text("No matches booked yet."))
        
        matches_on_card = ft.Column(match_list_controls)

        return ft.Column(
            [
                ft.Text("Book a New Show", size=30),
                show_name_field,
                ft.ElevatedButton("Create Show", on_click=start_booking, disabled=current_show is not None),
                ft.Divider(),
                ft.Text("Matches on Card:", size=20),
                matches_on_card, # This will be dynamically updated later
                ft.Row(
                    [
                        ft.ElevatedButton("Add Singles Match", on_click=lambda e: self._show_add_singles_match_dialog(), disabled=current_show is None),
                        ft.ElevatedButton("Add Tag Team Match", on_click=lambda e: self._show_add_tag_match_dialog(), disabled=current_show is None),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.ElevatedButton("Run Show", on_click=run_show_click, disabled=current_show is None or current_show.match_count == 0),
                # Back button is in AppBar
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.START,
            expand=True,
            scroll=ft.ScrollMode.ALWAYS,
        )

    def _init_show_results_view(self, result: 'ShowResult') -> ft.Control:
        """Creates the content for displaying show results."""
        if not result:
            return ft.Column([ft.Text("No show results to display.")], alignment=ft.MainAxisAlignment.CENTER)

        results_content = [
            ft.Text(f"SHOW REPORT: {result.show_name.upper()}", size=30, weight=ft.FontWeight.BOLD),
            ft.Text(f"Final Rating: {result.final_rating}/100", size=24),
            ft.Text(f"Show Profit: ${result.profit:,}", size=20),
            ft.Text(f"Overall Feedback: {result.feedback}", size=20),
            ft.Divider(),
        ]

        for i, match_result in enumerate(result.match_results):
            match_summary = []
            if isinstance(match_result, TagMatchResult):
                match_summary.append(ft.Text(f"Match #{i + 1}: {match_result.team_a_name} vs. {match_result.team_b_name}"))
                match_summary.append(ft.Text(f"Winners: {match_result.winning_team_name}"))
                match_summary.append(ft.Text(f"Pinned: {match_result.pinned_wrestler_name}"))
            else:
                match_summary.append(ft.Text(f"Match #{i + 1}: {match_result.wrestler_a_name} vs. {match_result.wrestler_b_name}"))
                match_summary.append(ft.Text(f"Winner: {match_result.winner_name}"))
            
            match_summary.append(ft.Text(f"Rating: {match_result.rating}/100 ({match_result.stars:.1f} Stars)"))
            
            if match_result.commentary:
                match_summary.append(ft.Text("--- Highlights ---", weight=ft.FontWeight.BOLD))
                for line in match_result.commentary:
                    match_summary.append(ft.Text(f"- {line}", size=14))
            
            results_content.append(ft.Column(match_summary, spacing=5))
            results_content.append(ft.Divider())

        return ft.Column(
            results_content,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.START,
            expand=True,
            scroll=ft.ScrollMode.ALWAYS,
        )


    def _init_tag_team_management_view(self) -> ft.Control:
        """Creates the content for the Tag Team Management screen."""
        if not self.game_service.is_game_loaded:
            return ft.Column([ft.Text("No game loaded.")], alignment=ft.MainAxisAlignment.CENTER)

        tag_teams = self.game_service.get_tag_teams()
        roster = self.game_service.state.roster # Assuming roster is available if game is loaded

        team_display_controls = []
        if not tag_teams:
            team_display_controls.append(ft.Text("No tag teams created yet."))
        else:
            for team in tag_teams:
                members = team.get_members(roster)
                member_names = " & ".join([m.name for m in members])
                status = "Active" if team.is_active else "Disbanded"
                team_display_controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=10,
                            content=ft.Column(
                                [
                                    ft.Text(f"{team.name} (ID: {team.id})", size=20, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Members: {member_names}"),
                                    ft.Text(f"Chemistry: {team.chemistry} | Record: {team.wins}W - {team.losses}L"),
                                    ft.Text(f"Status: {status}"),
                                ]
                            )
                        )
                    )
                )

        return ft.Column(
            [
                ft.Text("Tag Team Management", size=30),
                ft.Row(
                    [
                        ft.ElevatedButton("Create New Tag Team", on_click=lambda e: self._show_create_tag_team_dialog()),
                        ft.ElevatedButton("Disband Tag Team", on_click=lambda e: self._show_disband_tag_team_dialog()),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Divider(),
                ft.Text("Existing Tag Teams:", size=20),
                ft.Column(team_display_controls, expand=True, scroll=ft.ScrollMode.ALWAYS),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.START,
            expand=True,
        )

    def _show_create_tag_team_dialog(self):
        """Shows a dialog to create a new tag team."""
        if not self.game_service.is_game_loaded:
            return

        available_wrestlers = [w for w in self.game_service.state.roster if not self.game_service.state.is_wrestler_on_team(w.id)]
        
        if len(available_wrestlers) < 2:
            self._show_message_dialog("Error", "Not enough available wrestlers to form a team.")
            return

        wrestler_options = [ft.dropdown.Option(str(w.id), text=w.name) for w in available_wrestlers]

        wrestler_a_dropdown = ft.Dropdown(label="Select First Member", options=wrestler_options, width=300)
        wrestler_b_dropdown = ft.Dropdown(label="Select Second Member", options=wrestler_options, width=300)
        team_name_field = ft.TextField(label="Team Name", width=300)

        def create_team(e):
            if not wrestler_a_dropdown.value or not wrestler_b_dropdown.value or not team_name_field.value:
                self._show_message_dialog("Error", "Please fill all fields.")
                return

            member_a_id = int(wrestler_a_dropdown.value)
            member_b_id = int(wrestler_b_dropdown.value)

            success, message = self.game_service.create_tag_team(team_name_field.value, member_a_id, member_b_id)
            self._close_dialog(e)
            self._show_message_dialog("Create Tag Team", message)
            if success:
                self.go_to("/tag_team_management")

        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Create New Tag Team"),
            content=ft.Column([team_name_field, wrestler_a_dropdown, wrestler_b_dropdown], tight=True),
            actions=[
                ft.TextButton("Create", on_click=create_team),
                ft.TextButton("Cancel", on_click=self._close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

    def _show_disband_tag_team_dialog(self):
        """Shows a dialog to disband an existing tag team."""
        if not self.game_service.is_game_loaded:
            return

        active_teams = [t for t in self.game_service.get_tag_teams() if t.is_active]
        
        if not active_teams:
            self._show_message_dialog("Error", "No active tag teams to disband.")
            return

        team_options = [ft.dropdown.Option(str(t.id), text=t.name) for t in active_teams]

        team_dropdown = ft.Dropdown(label="Select Team to Disband", options=team_options, width=300)

        def disband_team(e):
            if not team_dropdown.value:
                self._show_message_dialog("Error", "Please select a team.")
                return
            
            team_id = int(team_dropdown.value)
            success, message = self.game_service.disband_tag_team(team_id)
            self._close_dialog(e)
            self._show_message_dialog("Disband Tag Team", message)
            if success:
                self.go_to("/tag_team_management")

        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Disband Tag Team"),
            content=ft.Column([team_dropdown], tight=True),
            actions=[
                ft.TextButton("Disband", on_click=disband_team),
                ft.TextButton("Cancel", on_click=self._close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog.open = True
        self.page.update()

def main(page: ft.Page):
    app = MainApp(page)

if __name__ == "__main__":
    ft.run(main)
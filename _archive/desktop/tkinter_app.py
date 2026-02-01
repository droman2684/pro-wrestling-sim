import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# Add the 'src' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from services.game_service import GameService
from core.game_state import MatchResult, TagMatchResult, RumbleResult, MultiManResult, LadderMatchResult, IronManResult, EliminationChamberResult, MoneyInTheBankResult
from core.auto_booker import CardSuggestion, MatchSuggestion, FeudSuggestion
from core.calendar import is_ppv_week, get_ppv_for_week


class WrestlingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Sim Sports: Pro Wrestling")
        self.root.geometry("800x600")

        self.game = GameService()

        # Container for all frames
        self.container = ttk.Frame(root)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        # Show start menu
        self.show_start_menu()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # --- START MENU ---
    def show_start_menu(self):
        self.clear_container()

        ttk.Label(self.container, text="Simple Sim Sports: Pro Wrestling", font=("Arial", 24)).pack(pady=40)

        ttk.Button(self.container, text="New Game", command=self.new_game_dialog, width=20).pack(pady=10)
        ttk.Button(self.container, text="Load Game", command=self.load_game_dialog, width=20).pack(pady=10)
        ttk.Button(self.container, text="Exit", command=self.root.quit, width=20).pack(pady=10)

    def new_game_dialog(self):
        databases = self.game.list_databases()
        if not databases:
            messagebox.showerror("Error", "No databases found in data/databases/")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("New Game")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Select Database:").pack(pady=5)
        db_var = tk.StringVar()
        db_combo = ttk.Combobox(dialog, textvariable=db_var, values=databases, state="readonly")
        db_combo.pack(pady=5)
        if databases:
            db_combo.current(0)

        ttk.Label(dialog, text="Save Name:").pack(pady=5)
        save_entry = ttk.Entry(dialog)
        save_entry.pack(pady=5)

        def create():
            if not db_var.get() or not save_entry.get():
                messagebox.showerror("Error", "Please fill all fields")
                return
            success, msg = self.game.create_new_game(db_var.get(), save_entry.get())
            messagebox.showinfo("New Game", msg)
            if success:
                dialog.destroy()
                self.show_head_office()

        ttk.Button(dialog, text="Create", command=create).pack(pady=20)

    def load_game_dialog(self):
        saves = self.game.list_saves()
        if not saves:
            messagebox.showerror("Error", "No save games found")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Load Game")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Select Save:").pack(pady=10)
        save_var = tk.StringVar()
        save_combo = ttk.Combobox(dialog, textvariable=save_var, values=saves, state="readonly")
        save_combo.pack(pady=5)
        if saves:
            save_combo.current(0)

        def load():
            if not save_var.get():
                messagebox.showerror("Error", "Please select a save")
                return
            success, msg = self.game.load_game(save_var.get())
            messagebox.showinfo("Load Game", msg)
            if success:
                dialog.destroy()
                self.show_head_office()

        ttk.Button(dialog, text="Load", command=load).pack(pady=20)

    # --- HEAD OFFICE ---
    def show_head_office(self):
        self.clear_container()

        ttk.Label(self.container, text=f"Head Office: {self.game.get_save_name()}", font=("Arial", 20)).pack(pady=10)
        ttk.Label(self.container, text=self.game.get_current_date_string(), font=("Arial", 14)).pack()
        ttk.Label(self.container, text=self.game.get_next_ppv_string(), font=("Arial", 12)).pack(pady=5)

        btn_frame = ttk.Frame(self.container)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="View Roster", command=self.show_roster, width=25).pack(pady=5)
        ttk.Button(btn_frame, text="AI Book Show", command=self.show_ai_booking, width=25).pack(pady=5)
        ttk.Button(btn_frame, text="Manual Book Show", command=self.show_book_show, width=25).pack(pady=5)
        ttk.Button(btn_frame, text="View Titles", command=self.show_titles, width=25).pack(pady=5)
        ttk.Button(btn_frame, text="View Rankings", command=self.show_rankings, width=25).pack(pady=5)
        ttk.Button(btn_frame, text="Records & History", command=self.show_records, width=25).pack(pady=5)
        ttk.Button(btn_frame, text="Tag Team Management", command=self.show_tag_teams, width=25).pack(pady=5)
        ttk.Button(btn_frame, text="Feud Management", command=self.show_feuds, width=25).pack(pady=5)
        ttk.Button(btn_frame, text="Stable Management", command=self.show_stables, width=25).pack(pady=5)
        ttk.Button(btn_frame, text="Save Game", command=self.save_game, width=25).pack(pady=5)
        ttk.Button(btn_frame, text="Exit to Main Menu", command=self.show_start_menu, width=25).pack(pady=5)

    def save_game(self):
        success, msg = self.game.save_game()
        messagebox.showinfo("Save Game", msg)

    # --- ROSTER ---
    def show_roster(self):
        self.clear_container()

        ttk.Label(self.container, text="Roster", font=("Arial", 20)).pack(pady=10)

        # Treeview for roster
        columns = ("Name", "Gimmick", "Overall", "W", "L", "Stamina")
        tree = ttk.Treeview(self.container, columns=columns, show="headings", height=15)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        for w in self.game.get_roster():
            tree.insert("", "end", values=(w.name, w.gimmick, w.get_overall_rating(), w.wins, w.losses, w.stamina))

        tree.pack(fill="both", expand=True, pady=10)

        ttk.Button(self.container, text="Add Wrestler", command=self.add_wrestler_dialog).pack(pady=5)
        ttk.Button(self.container, text="Back", command=self.show_head_office).pack(pady=5)

    def add_wrestler_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Wrestler")
        dialog.geometry("350x500")
        dialog.transient(self.root)
        dialog.grab_set()

        fields = {}

        ttk.Label(dialog, text="Name:").pack()
        fields['name'] = ttk.Entry(dialog, width=30)
        fields['name'].pack(pady=2)

        ttk.Label(dialog, text="Gimmick:").pack()
        fields['gimmick'] = ttk.Entry(dialog, width=30)
        fields['gimmick'].pack(pady=2)

        ttk.Label(dialog, text="--- Ring Stats (1-100) ---").pack(pady=5)
        for stat in ['Brawl', 'Tech', 'Air', 'Psych']:
            ttk.Label(dialog, text=f"{stat}:").pack()
            fields[stat.lower()] = ttk.Entry(dialog, width=10)
            fields[stat.lower()].insert(0, "50")
            fields[stat.lower()].pack(pady=2)

        ttk.Label(dialog, text="--- Entertainment Stats ---").pack(pady=5)
        for stat in ['Mic', 'Charisma', 'Look', 'Star Quality']:
            key = stat.lower().replace(' ', '_')
            ttk.Label(dialog, text=f"{stat}:").pack()
            fields[key] = ttk.Entry(dialog, width=10)
            fields[key].insert(0, "50")
            fields[key].pack(pady=2)

        def create():
            name = fields['name'].get().strip()
            if not name:
                messagebox.showerror("Error", "Name is required")
                return

            success, msg = self.game.create_wrestler(
                name=name,
                gimmick=fields['gimmick'].get() or "The Newcomer",
                brawl=int(fields['brawl'].get() or 50),
                tech=int(fields['tech'].get() or 50),
                air=int(fields['air'].get() or 50),
                psych=int(fields['psych'].get() or 50),
                mic=int(fields['mic'].get() or 50),
                charisma=int(fields['charisma'].get() or 50),
                look=int(fields['look'].get() or 50),
                star_quality=int(fields['star_quality'].get() or 50)
            )
            messagebox.showinfo("Add Wrestler", msg)
            if success:
                dialog.destroy()
                self.show_roster()

        ttk.Button(dialog, text="Create", command=create).pack(pady=20)

    # --- TITLES ---
    def show_titles(self):
        self.clear_container()

        ttk.Label(self.container, text="Championships", font=("Arial", 20)).pack(pady=10)

        titles = self.game.get_titles()

        if not titles:
            ttk.Label(self.container, text="No championships exist.").pack(pady=20)
        else:
            for title in titles:
                frame = ttk.LabelFrame(self.container, text=f"[{title.prestige}] {title.name}")
                frame.pack(fill="x", padx=20, pady=5)

                if title.current_holder_id:
                    holder = self.game.get_wrestler_by_id(title.current_holder_id)
                    if holder:
                        ttk.Label(frame, text=f"Champion: {holder.name}").pack(padx=10, pady=5)
                    else:
                        team = self.game.get_tag_team_by_id(title.current_holder_id)
                        if team:
                            ttk.Label(frame, text=f"Champions: {team.name}").pack(padx=10, pady=5)
                        else:
                            ttk.Label(frame, text="Champion: Unknown").pack(padx=10, pady=5)
                else:
                    ttk.Label(frame, text="Champion: VACANT").pack(padx=10, pady=5)

        ttk.Button(self.container, text="Create New Title", command=self.add_title_dialog).pack(pady=10)
        ttk.Button(self.container, text="Back", command=self.show_head_office).pack(pady=5)

    def add_title_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Title")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Title Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.pack(pady=5)

        ttk.Label(dialog, text="Prestige (1-100):").pack(pady=5)
        prestige_entry = ttk.Entry(dialog, width=10)
        prestige_entry.insert(0, "50")
        prestige_entry.pack(pady=5)

        def create():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Name is required")
                return
            success, msg = self.game.create_title(name, int(prestige_entry.get() or 50))
            messagebox.showinfo("Create Title", msg)
            if success:
                dialog.destroy()
                self.show_titles()

        ttk.Button(dialog, text="Create", command=create).pack(pady=20)

    # --- RANKINGS ---
    def show_rankings(self):
        self.clear_container()

        ttk.Label(self.container, text="Rankings", font=("Arial", 20)).pack(pady=10)

        # Singles
        ttk.Label(self.container, text="--- SINGLES TOP 5 ---", font=("Arial", 14, "bold")).pack(pady=5)
        for i, w in enumerate(self.game.get_wrestler_rankings()[:5]):
            ttk.Label(self.container, text=f"#{i+1}. {w.name} - {w.wins}W / {w.losses}L").pack()

        # Tag Teams
        ttk.Label(self.container, text="--- TAG TEAMS TOP 5 ---", font=("Arial", 14, "bold")).pack(pady=10)
        for i, t in enumerate(self.game.get_tag_team_rankings()[:5]):
            ttk.Label(self.container, text=f"#{i+1}. {t.name} - {t.wins}W / {t.losses}L").pack()

        ttk.Button(self.container, text="Back", command=self.show_head_office).pack(pady=20)

    # --- TAG TEAMS ---
    def show_tag_teams(self):
        self.clear_container()

        ttk.Label(self.container, text="Tag Team Management", font=("Arial", 20)).pack(pady=10)

        teams = [t for t in self.game.get_tag_teams() if t.is_active]
        roster = self.game.state.roster if self.game.is_game_loaded else []

        if not teams:
            ttk.Label(self.container, text="No active tag teams.").pack(pady=20)
        else:
            for team in teams:
                members = team.get_members(roster)
                member_names = " & ".join([m.name for m in members])
                frame = ttk.LabelFrame(self.container, text=team.name)
                frame.pack(fill="x", padx=20, pady=5)
                ttk.Label(frame, text=f"Members: {member_names}").pack(padx=10, pady=2)
                ttk.Label(frame, text=f"Chemistry: {team.chemistry} | Record: {team.wins}W - {team.losses}L").pack(padx=10, pady=2)

        btn_frame = ttk.Frame(self.container)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Create Tag Team", command=self.create_tag_team_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Back", command=self.show_head_office).pack(side="left", padx=5)

    def create_tag_team_dialog(self):
        roster = self.game.state.roster
        available = [w for w in roster if not self.game.state.is_wrestler_on_team(w.id)]

        if len(available) < 2:
            messagebox.showerror("Error", "Not enough available wrestlers")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Create Tag Team")
        dialog.geometry("300x250")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Team Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=25)
        name_entry.pack(pady=5)

        names = [w.name for w in available]

        ttk.Label(dialog, text="Member 1:").pack(pady=5)
        m1_var = tk.StringVar()
        m1_combo = ttk.Combobox(dialog, textvariable=m1_var, values=names, state="readonly")
        m1_combo.pack(pady=5)

        ttk.Label(dialog, text="Member 2:").pack(pady=5)
        m2_var = tk.StringVar()
        m2_combo = ttk.Combobox(dialog, textvariable=m2_var, values=names, state="readonly")
        m2_combo.pack(pady=5)

        def create():
            if not name_entry.get() or not m1_var.get() or not m2_var.get():
                messagebox.showerror("Error", "Fill all fields")
                return
            if m1_var.get() == m2_var.get():
                messagebox.showerror("Error", "Select different wrestlers")
                return

            m1 = next(w for w in available if w.name == m1_var.get())
            m2 = next(w for w in available if w.name == m2_var.get())

            success, msg = self.game.create_tag_team(name_entry.get(), m1.id, m2.id)
            messagebox.showinfo("Create Tag Team", msg)
            if success:
                dialog.destroy()
                self.show_tag_teams()

        ttk.Button(dialog, text="Create", command=create).pack(pady=20)

    # --- FEUDS ---
    def show_feuds(self):
        self.clear_container()

        ttk.Label(self.container, text="Feud Management", font=("Arial", 20)).pack(pady=10)

        active_feuds = self.game.get_active_feuds()
        ttk.Label(self.container, text=f"Active Feuds: {len(active_feuds)}").pack()

        # Display feuds
        feuds = self.game.get_feuds()
        if not feuds:
            ttk.Label(self.container, text="No feuds exist.").pack(pady=20)
        else:
            for feud in feuds:
                wrestler_a = self.game.get_wrestler_by_id(feud.wrestler_a_id)
                wrestler_b = self.game.get_wrestler_by_id(feud.wrestler_b_id)
                a_name = wrestler_a.name if wrestler_a else "Unknown"
                b_name = wrestler_b.name if wrestler_b else "Unknown"

                status = "ACTIVE" if feud.is_active else "ENDED"
                blowoff_txt = " [BLOWOFF]" if feud.blowoff_match_scheduled and feud.is_active else ""

                frame = ttk.LabelFrame(self.container, text=f"[{status}] {a_name} vs {b_name}{blowoff_txt}")
                frame.pack(fill="x", padx=20, pady=5)
                ttk.Label(frame, text=f"Intensity: {feud.intensity.upper()} (+{feud.get_intensity_bonus()} rating bonus)").pack(padx=10, pady=2)
                ttk.Label(frame, text=f"Score: {feud.get_score_string()} | Matches: {feud.total_matches} (Remaining: {feud.matches_remaining})").pack(padx=10, pady=2)

        btn_frame = ttk.Frame(self.container)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Start New Feud", command=self.create_feud_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="End Feud", command=self.end_feud_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Schedule Blowoff", command=self.schedule_blowoff_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Back", command=self.show_head_office).pack(side="left", padx=5)

    def create_feud_dialog(self):
        roster = self.game.state.roster
        available = [w for w in roster if not self.game.state.is_wrestler_in_feud(w.id)]

        if len(available) < 2:
            messagebox.showerror("Error", "Not enough available wrestlers (each can only be in one active feud)")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Start New Feud")
        dialog.geometry("350x350")
        dialog.transient(self.root)
        dialog.grab_set()

        names = [f"{w.name} [{w.get_overall_rating()}]" for w in available]

        ttk.Label(dialog, text="Wrestler 1:").pack(pady=5)
        w1_var = tk.StringVar()
        w1_combo = ttk.Combobox(dialog, textvariable=w1_var, values=names, state="readonly", width=30)
        w1_combo.pack(pady=5)

        ttk.Label(dialog, text="Wrestler 2:").pack(pady=5)
        w2_var = tk.StringVar()
        w2_combo = ttk.Combobox(dialog, textvariable=w2_var, values=names, state="readonly", width=30)
        w2_combo.pack(pady=5)

        ttk.Label(dialog, text="Intensity:").pack(pady=5)
        intensity_var = tk.StringVar(value="heated")
        intensity_combo = ttk.Combobox(dialog, textvariable=intensity_var,
                                       values=["heated (+3)", "intense (+6)", "blood (+10)"],
                                       state="readonly", width=20)
        intensity_combo.current(0)
        intensity_combo.pack(pady=5)

        ttk.Label(dialog, text="Duration (matches):").pack(pady=5)
        matches_entry = ttk.Entry(dialog, width=10)
        matches_entry.insert(0, "3")
        matches_entry.pack(pady=5)

        def create():
            if not w1_var.get() or not w2_var.get():
                messagebox.showerror("Error", "Select both wrestlers")
                return
            if w1_var.get() == w2_var.get():
                messagebox.showerror("Error", "Select different wrestlers")
                return

            idx1 = names.index(w1_var.get())
            idx2 = names.index(w2_var.get())
            w1 = available[idx1]
            w2 = available[idx2]

            intensity_str = intensity_var.get().split()[0]  # Extract "heated", "intense", or "blood"
            try:
                matches = int(matches_entry.get())
            except ValueError:
                matches = 3

            success, msg = self.game.create_feud(w1.id, w2.id, intensity_str, matches)
            messagebox.showinfo("Create Feud", msg)
            if success:
                dialog.destroy()
                self.show_feuds()

        ttk.Button(dialog, text="Start Feud", command=create).pack(pady=20)

    def end_feud_dialog(self):
        feuds = self.game.get_active_feuds()
        if not feuds:
            messagebox.showerror("Error", "No active feuds to end")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("End Feud")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()

        feud_names = []
        for f in feuds:
            w_a = self.game.get_wrestler_by_id(f.wrestler_a_id)
            w_b = self.game.get_wrestler_by_id(f.wrestler_b_id)
            a_name = w_a.name if w_a else "Unknown"
            b_name = w_b.name if w_b else "Unknown"
            feud_names.append(f"{a_name} vs {b_name} ({f.intensity.upper()})")

        ttk.Label(dialog, text="Select feud to end:").pack(pady=10)
        feud_var = tk.StringVar()
        feud_combo = ttk.Combobox(dialog, textvariable=feud_var, values=feud_names, state="readonly", width=35)
        feud_combo.pack(pady=10)

        def end():
            if not feud_var.get():
                messagebox.showerror("Error", "Select a feud")
                return
            idx = feud_names.index(feud_var.get())
            feud = feuds[idx]
            success, msg = self.game.end_feud(feud.id)
            messagebox.showinfo("End Feud", msg)
            if success:
                dialog.destroy()
                self.show_feuds()

        ttk.Button(dialog, text="End Feud", command=end).pack(pady=20)

    def schedule_blowoff_dialog(self):
        feuds = [f for f in self.game.get_active_feuds() if not f.blowoff_match_scheduled]
        if not feuds:
            messagebox.showerror("Error", "No feuds available for blowoff scheduling")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Schedule Blowoff Match")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()

        feud_names = []
        for f in feuds:
            w_a = self.game.get_wrestler_by_id(f.wrestler_a_id)
            w_b = self.game.get_wrestler_by_id(f.wrestler_b_id)
            a_name = w_a.name if w_a else "Unknown"
            b_name = w_b.name if w_b else "Unknown"
            feud_names.append(f"{a_name} vs {b_name} ({f.intensity.upper()})")

        ttk.Label(dialog, text="Select feud for blowoff:").pack(pady=5)
        ttk.Label(dialog, text="(Next match between them will end the feud)", font=("Arial", 9)).pack()
        feud_var = tk.StringVar()
        feud_combo = ttk.Combobox(dialog, textvariable=feud_var, values=feud_names, state="readonly", width=35)
        feud_combo.pack(pady=10)

        def schedule():
            if not feud_var.get():
                messagebox.showerror("Error", "Select a feud")
                return
            idx = feud_names.index(feud_var.get())
            feud = feuds[idx]
            success, msg = self.game.schedule_blowoff_match(feud.id)
            messagebox.showinfo("Schedule Blowoff", msg)
            if success:
                dialog.destroy()
                self.show_feuds()

        ttk.Button(dialog, text="Schedule Blowoff", command=schedule).pack(pady=20)

    # --- AI BOOKING ---
    def show_ai_booking(self):
        """Show AI booking suggestion screen."""
        self.clear_container()

        state = self.game.state
        is_ppv = is_ppv_week(state.month, state.week)
        show_type = "PPV" if is_ppv else "TV Show"

        ttk.Label(self.container, text="AI Booking Assistant", font=("Arial", 20)).pack(pady=10)
        ttk.Label(self.container, text=f"Generating {show_type} suggestions...", font=("Arial", 12)).pack()

        # Get suggestions
        self.current_suggestion = self.game.get_card_suggestions()

        if not self.current_suggestion:
            ttk.Label(self.container, text="Could not generate suggestions.", foreground="red").pack(pady=20)
            ttk.Button(self.container, text="Back", command=self.show_head_office).pack(pady=10)
            return

        self._display_ai_booking_screen()

    def _display_ai_booking_screen(self):
        """Display the AI booking suggestions."""
        self.clear_container()

        suggestion = self.current_suggestion

        ttk.Label(self.container, text="AI Booking Assistant", font=("Arial", 20)).pack(pady=5)

        # Header info
        info_frame = ttk.Frame(self.container)
        info_frame.pack(fill="x", padx=20, pady=5)

        ttk.Label(info_frame, text=f"Show: {suggestion.show_name}", font=("Arial", 14)).pack()
        ttk.Label(info_frame, text=f"Type: {'PPV' if suggestion.is_ppv else 'TV Show'} | Est. Rating: {suggestion.estimated_rating}/100").pack()

        # Warnings
        if suggestion.warnings:
            warn_frame = ttk.LabelFrame(self.container, text="Warnings")
            warn_frame.pack(fill="x", padx=20, pady=5)
            for warning in suggestion.warnings:
                ttk.Label(warn_frame, text=f"! {warning}", foreground="orange").pack(padx=10, pady=2)

        # Match list with checkboxes
        match_frame = ttk.LabelFrame(self.container, text="Suggested Matches")
        match_frame.pack(fill="both", expand=True, padx=20, pady=5)

        # Create scrollable frame
        canvas = tk.Canvas(match_frame, height=200)
        scrollbar = ttk.Scrollbar(match_frame, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)

        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Store checkbox variables
        self.match_vars = []

        for i, match in enumerate(suggestion.matches):
            var = tk.BooleanVar(value=match.is_accepted)
            self.match_vars.append((var, match))

            frame = ttk.Frame(scrollable)
            frame.pack(fill="x", padx=5, pady=3, anchor="w")

            cb = ttk.Checkbutton(frame, variable=var, command=lambda m=match, v=var: self._toggle_match_var(m, v))
            cb.pack(side="left")

            # Match description
            desc = self._format_match_description(match)
            ttk.Label(frame, text=desc, font=("Arial", 10)).pack(side="left", padx=5)

            # Reason
            ttk.Label(frame, text=f"[{match.reason[:40]}...]" if len(match.reason) > 40 else f"[{match.reason}]",
                     foreground="gray", font=("Arial", 9)).pack(side="right", padx=5)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Feud suggestions section
        if suggestion.feud_suggestions:
            feud_frame = ttk.LabelFrame(self.container, text="Suggested New Feuds")
            feud_frame.pack(fill="x", padx=20, pady=5)

            for feud in suggestion.feud_suggestions:
                w_a = self.game.get_wrestler_by_id(feud.wrestler_a_id)
                w_b = self.game.get_wrestler_by_id(feud.wrestler_b_id)
                a_name = w_a.name if w_a else "Unknown"
                b_name = w_b.name if w_b else "Unknown"

                row = ttk.Frame(feud_frame)
                row.pack(fill="x", padx=10, pady=3)

                ttk.Label(row, text=f"{a_name} vs {b_name} - {feud.reason}").pack(side="left")
                ttk.Button(row, text="Start Feud",
                          command=lambda f=feud: self._start_suggested_feud(f)).pack(side="right")

        # Action buttons
        btn_frame = ttk.Frame(self.container)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Accept & Run Show",
                  command=self._apply_ai_suggestion, width=20).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Regenerate",
                  command=self._regenerate_suggestions, width=15).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Manual Booking",
                  command=self.show_book_show, width=15).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel",
                  command=self.show_head_office, width=10).pack(side="left", padx=5)

    def _toggle_match_var(self, match, var):
        """Update match acceptance when checkbox is toggled."""
        match.is_accepted = var.get()

    def _format_match_description(self, match: MatchSuggestion) -> str:
        """Format a match for display."""
        participants = []
        if match.match_type == "tag":
            for tid in match.participant_ids:
                team = self.game.get_tag_team_by_id(tid)
                participants.append(team.name if team else "?")
        else:
            for wid in match.participant_ids:
                w = self.game.get_wrestler_by_id(wid)
                participants.append(w.name if w else "?")

        match_type = match.match_type.replace("_", " ").title()
        desc = f"[{match.card_position.upper()}] {match_type}: {' vs '.join(participants)}"

        if match.is_title_match and match.title_id:
            title = self.game.get_title_by_id(match.title_id)
            desc += f" ({title.name})" if title else " [TITLE]"

        if match.is_steel_cage:
            desc += " (Cage)"

        return desc

    def _apply_ai_suggestion(self):
        """Apply the AI suggestion and run the show."""
        # Update match acceptance based on checkboxes
        for var, match in self.match_vars:
            match.is_accepted = var.get()

        accepted = [m for m in self.current_suggestion.matches if m.is_accepted]
        if not accepted:
            messagebox.showerror("Error", "No matches accepted! Check at least one match.")
            return

        success, msg = self.game.apply_card_suggestions(self.current_suggestion)

        if success:
            result = self.game.play_show()
            if result:
                self.show_results(result)
            else:
                messagebox.showerror("Error", "Could not run show")
                self.show_head_office()
        else:
            messagebox.showerror("Error", msg)

    def _regenerate_suggestions(self):
        """Regenerate AI suggestions."""
        self.current_suggestion = self.game.get_card_suggestions()
        if self.current_suggestion:
            self._display_ai_booking_screen()
        else:
            messagebox.showerror("Error", "Could not regenerate suggestions")
            self.show_head_office()

    def _start_suggested_feud(self, feud: FeudSuggestion):
        """Start a feud from an AI suggestion."""
        success, msg = self.game.start_suggested_feud(feud)
        messagebox.showinfo("Start Feud", msg)
        if success:
            # Refresh the screen to update suggestions
            self._regenerate_suggestions()

    # --- BOOK SHOW ---
    def show_book_show(self):
        self.clear_container()

        ttk.Label(self.container, text="Book a Show", font=("Arial", 20)).pack(pady=10)

        # Show name
        name_frame = ttk.Frame(self.container)
        name_frame.pack(pady=10)
        ttk.Label(name_frame, text="Show Name:").pack(side="left")
        self.show_name_entry = ttk.Entry(name_frame, width=30)
        self.show_name_entry.pack(side="left", padx=5)

        current_show = self.game.get_current_show()
        if current_show:
            self.show_name_entry.insert(0, current_show.name)
            self.show_name_entry.config(state="disabled")

        ttk.Button(self.container, text="Create Show", command=self.create_show).pack(pady=5)

        # Match list
        ttk.Label(self.container, text="--- Matches on Card ---", font=("Arial", 12, "bold")).pack(pady=10)

        self.match_listbox = tk.Listbox(self.container, width=60, height=8)
        self.match_listbox.pack(pady=5)

        self.refresh_match_list()

        # Buttons
        btn_frame = ttk.Frame(self.container)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Add Singles", command=self.add_singles_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Add Tag Match", command=self.add_tag_match_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Triple Threat", command=lambda: self.add_multi_man_dialog(3)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Fatal 4-Way", command=lambda: self.add_multi_man_dialog(4)).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Ladder Match", command=self.add_ladder_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Iron Man", command=self.add_iron_man_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Royal Rumble", command=self.add_rumble_dialog).pack(side="left", padx=5)

        btn_frame2 = ttk.Frame(self.container)
        btn_frame2.pack(pady=5)
        ttk.Button(btn_frame2, text="Elimination Chamber", command=self.add_chamber_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame2, text="Money in the Bank", command=self.add_mitb_dialog).pack(side="left", padx=5)

        btn_frame3 = ttk.Frame(self.container)
        btn_frame3.pack(pady=10)
        ttk.Button(btn_frame3, text="Run Show", command=self.run_show).pack(side="left", padx=5)
        ttk.Button(btn_frame3, text="Cancel", command=self.cancel_show).pack(side="left", padx=5)

    def refresh_match_list(self):
        self.match_listbox.delete(0, tk.END)
        show = self.game.get_current_show()
        if show:
            match_num = 0
            for i, m in enumerate(show.matches):
                match_num += 1
                if m.match_type == "Tag Team":
                    txt = f"{match_num}. Tag: {m.team_a.name} vs {m.team_b.name}"
                else:
                    txt = f"{match_num}. Singles: {m.p1.name} vs {m.p2.name}"
                if m.is_steel_cage:
                    txt += " (Steel Cage)"
                if m.is_title_match:
                    txt += " [TITLE]"
                self.match_listbox.insert(tk.END, txt)
            for mm in show.multi_man_matches:
                match_num += 1
                names = " vs ".join([w.name for w in mm.wrestlers])
                txt = f"{match_num}. {mm.match_type}: {names}"
                if mm.is_title_match:
                    txt += " [TITLE]"
                self.match_listbox.insert(tk.END, txt)
            for ladder in show.ladder_matches:
                match_num += 1
                names = " vs ".join([w.name for w in ladder.wrestlers])
                txt = f"{match_num}. {ladder.match_type}: {names}"
                if ladder.is_title_match:
                    txt += " [TITLE]"
                self.match_listbox.insert(tk.END, txt)
            for iron_man in show.iron_man_matches:
                match_num += 1
                txt = f"{match_num}. {iron_man.match_type}: {iron_man.wrestler_a.name} vs {iron_man.wrestler_b.name}"
                if iron_man.is_title_match:
                    txt += " [TITLE]"
                self.match_listbox.insert(tk.END, txt)
            for r in show.rumble_matches:
                match_num += 1
                self.match_listbox.insert(tk.END, f"{match_num}. ROYAL RUMBLE (10 wrestlers)")
            for chamber in show.chamber_matches:
                match_num += 1
                txt = f"{match_num}. ELIMINATION CHAMBER (6 wrestlers)"
                if chamber.is_title_match:
                    txt += " [TITLE]"
                self.match_listbox.insert(tk.END, txt)
            for mitb in show.mitb_matches:
                match_num += 1
                self.match_listbox.insert(tk.END, f"{match_num}. MONEY IN THE BANK ({len(mitb.wrestlers)} wrestlers)")

    def create_show(self):
        name = self.show_name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Enter show name")
            return
        if self.game.create_show(name):
            self.show_name_entry.config(state="disabled")
            messagebox.showinfo("Success", f"Show '{name}' created")

    def cancel_show(self):
        self.game.cancel_show()
        self.show_head_office()

    def add_singles_dialog(self):
        if not self.game.get_current_show():
            messagebox.showerror("Error", "Create a show first")
            return

        available = [w for w in self.game.state.roster if not self.game.is_wrestler_booked_on_show(w.id)]
        if len(available) < 2:
            messagebox.showerror("Error", "Not enough available wrestlers")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Add Singles Match")
        dialog.geometry("350x300")
        dialog.transient(self.root)
        dialog.grab_set()

        names = [f"{w.name} [{w.get_overall_rating()}]" for w in available]

        ttk.Label(dialog, text="Wrestler A:").pack(pady=5)
        w1_var = tk.StringVar()
        w1_combo = ttk.Combobox(dialog, textvariable=w1_var, values=names, state="readonly", width=30)
        w1_combo.pack(pady=5)

        ttk.Label(dialog, text="Wrestler B:").pack(pady=5)
        w2_var = tk.StringVar()
        w2_combo = ttk.Combobox(dialog, textvariable=w2_var, values=names, state="readonly", width=30)
        w2_combo.pack(pady=5)

        cage_var = tk.BooleanVar()
        ttk.Checkbutton(dialog, text="Steel Cage Match", variable=cage_var).pack(pady=5)

        # Title match
        titles = self.game.get_titles()
        title_names = ["None"] + [t.name for t in titles]
        ttk.Label(dialog, text="Title on the line:").pack(pady=5)
        title_var = tk.StringVar(value="None")
        title_combo = ttk.Combobox(dialog, textvariable=title_var, values=title_names, state="readonly", width=25)
        title_combo.pack(pady=5)

        def add():
            if not w1_var.get() or not w2_var.get():
                messagebox.showerror("Error", "Select both wrestlers")
                return
            if w1_var.get() == w2_var.get():
                messagebox.showerror("Error", "Select different wrestlers")
                return

            idx1 = names.index(w1_var.get())
            idx2 = names.index(w2_var.get())
            w1 = available[idx1]
            w2 = available[idx2]

            is_title = title_var.get() != "None"
            title_id = None
            if is_title:
                title = next((t for t in titles if t.name == title_var.get()), None)
                title_id = title.id if title else None

            self.game.add_match_to_show(w1, w2, is_steel_cage=cage_var.get(), is_title_match=is_title, title_id=title_id)
            dialog.destroy()
            self.refresh_match_list()

        ttk.Button(dialog, text="Add Match", command=add).pack(pady=20)

    def add_tag_match_dialog(self):
        if not self.game.get_current_show():
            messagebox.showerror("Error", "Create a show first")
            return

        available = [t for t in self.game.get_available_tag_teams()
                     if not any(self.game.is_wrestler_booked_on_show(mid) for mid in t.member_ids)]

        if len(available) < 2:
            messagebox.showerror("Error", "Not enough available tag teams")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Add Tag Match")
        dialog.geometry("350x300")
        dialog.transient(self.root)
        dialog.grab_set()

        names = [t.name for t in available]

        ttk.Label(dialog, text="Team A:").pack(pady=5)
        t1_var = tk.StringVar()
        t1_combo = ttk.Combobox(dialog, textvariable=t1_var, values=names, state="readonly", width=25)
        t1_combo.pack(pady=5)

        ttk.Label(dialog, text="Team B:").pack(pady=5)
        t2_var = tk.StringVar()
        t2_combo = ttk.Combobox(dialog, textvariable=t2_var, values=names, state="readonly", width=25)
        t2_combo.pack(pady=5)

        cage_var = tk.BooleanVar()
        ttk.Checkbutton(dialog, text="Steel Cage Match", variable=cage_var).pack(pady=5)

        titles = self.game.get_titles()
        title_names = ["None"] + [t.name for t in titles]
        ttk.Label(dialog, text="Title on the line:").pack(pady=5)
        title_var = tk.StringVar(value="None")
        title_combo = ttk.Combobox(dialog, textvariable=title_var, values=title_names, state="readonly", width=25)
        title_combo.pack(pady=5)

        def add():
            if not t1_var.get() or not t2_var.get():
                messagebox.showerror("Error", "Select both teams")
                return
            if t1_var.get() == t2_var.get():
                messagebox.showerror("Error", "Select different teams")
                return

            team1 = next(t for t in available if t.name == t1_var.get())
            team2 = next(t for t in available if t.name == t2_var.get())

            is_title = title_var.get() != "None"
            title_id = None
            if is_title:
                title = next((t for t in titles if t.name == title_var.get()), None)
                title_id = title.id if title else None

            self.game.add_tag_match_to_show(team1, team2, is_steel_cage=cage_var.get(), is_title_match=is_title, title_id=title_id)
            dialog.destroy()
            self.refresh_match_list()

        ttk.Button(dialog, text="Add Match", command=add).pack(pady=20)

    def add_multi_man_dialog(self, num_wrestlers: int):
        """Dialog for adding Triple Threat (3) or Fatal 4-Way (4) match."""
        match_type = "Triple Threat" if num_wrestlers == 3 else "Fatal 4-Way"

        if not self.game.get_current_show():
            messagebox.showerror("Error", "Create a show first")
            return

        available = [w for w in self.game.state.roster if not self.game.is_wrestler_booked_on_show(w.id)]
        if len(available) < num_wrestlers:
            messagebox.showerror("Error", f"Need {num_wrestlers} wrestlers, only {len(available)} available")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title(f"{match_type} - Select {num_wrestlers} Wrestlers")
        dialog.geometry("400x450")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text=f"Select {num_wrestlers} wrestlers:", font=("Arial", 12)).pack(pady=10)

        # Listbox with multi-select
        frame = ttk.Frame(dialog)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(frame, selectmode="multiple", yscrollcommand=scrollbar.set, height=12)
        for w in available:
            listbox.insert(tk.END, f"{w.name} [{w.get_overall_rating()}]")
        listbox.pack(fill="both", expand=True)
        scrollbar.config(command=listbox.yview)

        selected_label = ttk.Label(dialog, text=f"Selected: 0/{num_wrestlers}")
        selected_label.pack(pady=5)

        def update_count(e=None):
            count = len(listbox.curselection())
            selected_label.config(text=f"Selected: {count}/{num_wrestlers}")

        listbox.bind("<<ListboxSelect>>", update_count)

        # Title match option
        titles = self.game.get_titles()
        singles_titles = [t for t in titles if not t.is_tag_team]

        title_var = tk.StringVar(value="none")
        if singles_titles:
            ttk.Label(dialog, text="Title Match?").pack(pady=(10, 0))
            title_frame = ttk.Frame(dialog)
            title_frame.pack(pady=5)
            ttk.Radiobutton(title_frame, text="No", variable=title_var, value="none").pack(side="left", padx=5)
            for t in singles_titles:
                holder = self.game.get_wrestler_by_id(t.current_holder_id)
                holder_name = holder.name if holder else "Vacant"
                ttk.Radiobutton(title_frame, text=f"{t.name} ({holder_name})", variable=title_var, value=str(t.id)).pack(side="left", padx=5)

        def add():
            selected_indices = listbox.curselection()
            if len(selected_indices) != num_wrestlers:
                messagebox.showerror("Error", f"Select exactly {num_wrestlers} wrestlers (selected: {len(selected_indices)})")
                return

            wrestlers = [available[i] for i in selected_indices]

            is_title = title_var.get() != "none"
            title_id = int(title_var.get()) if is_title else None

            # If title match, verify champion is in the match
            if is_title:
                title = next((t for t in titles if t.id == title_id), None)
                if title:
                    holder_in_match = any(w.id == title.current_holder_id for w in wrestlers)
                    if not holder_in_match:
                        messagebox.showerror("Error", "Champion must be in a title match!")
                        return

            success, msg = self.game.add_multi_man_match_to_show(wrestlers, is_title_match=is_title, title_id=title_id)
            messagebox.showinfo(match_type, msg)
            if success:
                dialog.destroy()
                self.refresh_match_list()

        ttk.Button(dialog, text=f"Add {match_type}", command=add).pack(pady=10)

    def add_ladder_dialog(self):
        """Dialog for adding a Ladder match."""
        if not self.game.get_current_show():
            messagebox.showerror("Error", "Create a show first")
            return

        available = [w for w in self.game.state.roster if not self.game.is_wrestler_booked_on_show(w.id)]
        if len(available) < 2:
            messagebox.showerror("Error", f"Need at least 2 wrestlers, only {len(available)} available")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Ladder Match - Select 2-6 Wrestlers")
        dialog.geometry("400x500")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Select 2-6 wrestlers:", font=("Arial", 12)).pack(pady=10)

        # Listbox with multi-select
        frame = ttk.Frame(dialog)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(frame, selectmode="multiple", yscrollcommand=scrollbar.set, height=12)
        for w in available:
            listbox.insert(tk.END, f"{w.name} [{w.get_overall_rating()}] (Air: {w.air})")
        listbox.pack(fill="both", expand=True)
        scrollbar.config(command=listbox.yview)

        selected_label = ttk.Label(dialog, text="Selected: 0 (need 2-6)")
        selected_label.pack(pady=5)

        def update_count(e=None):
            count = len(listbox.curselection())
            selected_label.config(text=f"Selected: {count} (need 2-6)")

        listbox.bind("<<ListboxSelect>>", update_count)

        # Title match option
        titles = self.game.get_titles()
        singles_titles = [t for t in titles if not t.is_tag_team]

        title_var = tk.StringVar(value="none")
        if singles_titles:
            ttk.Label(dialog, text="Title Match?").pack(pady=(10, 0))
            title_frame = ttk.Frame(dialog)
            title_frame.pack(pady=5)
            ttk.Radiobutton(title_frame, text="No", variable=title_var, value="none").pack(side="left", padx=5)
            for t in singles_titles:
                holder = self.game.get_wrestler_by_id(t.current_holder_id)
                holder_name = holder.name if holder else "Vacant"
                ttk.Radiobutton(title_frame, text=f"{t.name}", variable=title_var, value=str(t.id)).pack(side="left", padx=5)

        def add():
            selected_indices = listbox.curselection()
            if len(selected_indices) < 2 or len(selected_indices) > 6:
                messagebox.showerror("Error", f"Select 2-6 wrestlers (selected: {len(selected_indices)})")
                return

            wrestlers = [available[i] for i in selected_indices]

            is_title = title_var.get() != "none"
            title_id = int(title_var.get()) if is_title else None

            # If title match, verify champion is in the match
            if is_title:
                title = next((t for t in titles if t.id == title_id), None)
                if title:
                    holder_in_match = any(w.id == title.current_holder_id for w in wrestlers)
                    if not holder_in_match:
                        messagebox.showerror("Error", "Champion must be in a title match!")
                        return

            success, msg = self.game.add_ladder_match_to_show(wrestlers, is_title_match=is_title, title_id=title_id)
            messagebox.showinfo("Ladder Match", msg)
            if success:
                dialog.destroy()
                self.refresh_match_list()

        ttk.Button(dialog, text="Add Ladder Match", command=add).pack(pady=10)

    def add_iron_man_dialog(self):
        """Dialog for adding an Iron Man match."""
        if not self.game.get_current_show():
            messagebox.showerror("Error", "Create a show first")
            return

        available = [w for w in self.game.state.roster if not self.game.is_wrestler_booked_on_show(w.id)]
        if len(available) < 2:
            messagebox.showerror("Error", f"Need at least 2 wrestlers, only {len(available)} available")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Iron Man Match")
        dialog.geometry("400x400")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Iron Man Match", font=("Arial", 14, "bold")).pack(pady=10)

        # Wrestler A selection
        ttk.Label(dialog, text="Wrestler A:").pack(pady=(10, 0))
        wrestler_a_var = tk.StringVar()
        wrestler_a_combo = ttk.Combobox(dialog, textvariable=wrestler_a_var, state="readonly", width=30)
        wrestler_a_combo['values'] = [f"{w.name} [{w.get_overall_rating()}]" for w in available]
        wrestler_a_combo.pack(pady=5)

        # Wrestler B selection
        ttk.Label(dialog, text="Wrestler B:").pack(pady=(10, 0))
        wrestler_b_var = tk.StringVar()
        wrestler_b_combo = ttk.Combobox(dialog, textvariable=wrestler_b_var, state="readonly", width=30)
        wrestler_b_combo['values'] = [f"{w.name} [{w.get_overall_rating()}]" for w in available]
        wrestler_b_combo.pack(pady=5)

        # Time limit selection
        ttk.Label(dialog, text="Time Limit:").pack(pady=(10, 0))
        time_var = tk.StringVar(value="30")
        time_frame = ttk.Frame(dialog)
        time_frame.pack(pady=5)
        ttk.Radiobutton(time_frame, text="30 min", variable=time_var, value="30").pack(side="left", padx=10)
        ttk.Radiobutton(time_frame, text="60 min", variable=time_var, value="60").pack(side="left", padx=10)

        # Title match option
        titles = self.game.get_titles()
        singles_titles = [t for t in titles if not t.is_tag_team]

        title_var = tk.StringVar(value="none")
        if singles_titles:
            ttk.Label(dialog, text="Title Match?").pack(pady=(10, 0))
            title_frame = ttk.Frame(dialog)
            title_frame.pack(pady=5)
            ttk.Radiobutton(title_frame, text="No", variable=title_var, value="none").pack(side="left", padx=5)
            for t in singles_titles:
                ttk.Radiobutton(title_frame, text=t.name, variable=title_var, value=str(t.id)).pack(side="left", padx=5)

        def add():
            idx_a = wrestler_a_combo.current()
            idx_b = wrestler_b_combo.current()

            if idx_a < 0 or idx_b < 0:
                messagebox.showerror("Error", "Select both wrestlers")
                return

            if idx_a == idx_b:
                messagebox.showerror("Error", "Select different wrestlers")
                return

            wrestler_a = available[idx_a]
            wrestler_b = available[idx_b]
            time_limit = int(time_var.get())

            is_title = title_var.get() != "none"
            title_id = int(title_var.get()) if is_title else None

            # Verify champion is in match if title match
            if is_title:
                title = next((t for t in titles if t.id == title_id), None)
                if title:
                    if wrestler_a.id != title.current_holder_id and wrestler_b.id != title.current_holder_id:
                        messagebox.showerror("Error", "Champion must be in a title match!")
                        return

            success, msg = self.game.add_iron_man_match_to_show(wrestler_a, wrestler_b, time_limit,
                                                                 is_title_match=is_title, title_id=title_id)
            messagebox.showinfo("Iron Man Match", msg)
            if success:
                dialog.destroy()
                self.refresh_match_list()

        ttk.Button(dialog, text="Add Iron Man Match", command=add).pack(pady=20)

    def add_rumble_dialog(self):
        if not self.game.get_current_show():
            messagebox.showerror("Error", "Create a show first")
            return

        available = [w for w in self.game.state.roster if not self.game.is_wrestler_booked_on_show(w.id)]
        if len(available) < 10:
            messagebox.showerror("Error", f"Need 10 wrestlers, only {len(available)} available")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Royal Rumble - Select 10 Wrestlers")
        dialog.geometry("400x500")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Select 10 wrestlers (entry order):", font=("Arial", 12)).pack(pady=10)

        # Listbox with multi-select
        frame = ttk.Frame(dialog)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(frame, selectmode="multiple", yscrollcommand=scrollbar.set, height=15)
        for w in available:
            listbox.insert(tk.END, f"{w.name} [{w.get_overall_rating()}]")
        listbox.pack(fill="both", expand=True)
        scrollbar.config(command=listbox.yview)

        selected_label = ttk.Label(dialog, text="Selected: 0/10")
        selected_label.pack(pady=5)

        def update_count(e=None):
            count = len(listbox.curselection())
            selected_label.config(text=f"Selected: {count}/10")

        listbox.bind("<<ListboxSelect>>", update_count)

        def add():
            selected_indices = listbox.curselection()
            if len(selected_indices) != 10:
                messagebox.showerror("Error", f"Select exactly 10 wrestlers (selected: {len(selected_indices)})")
                return

            wrestlers = [available[i] for i in selected_indices]
            success, msg = self.game.add_rumble_to_show(wrestlers)
            messagebox.showinfo("Royal Rumble", msg)
            if success:
                dialog.destroy()
                self.refresh_match_list()

        ttk.Button(dialog, text="Add Royal Rumble", command=add).pack(pady=10)

    def add_chamber_dialog(self):
        """Dialog for adding an Elimination Chamber match."""
        if not self.game.get_current_show():
            messagebox.showerror("Error", "Create a show first")
            return

        available = [w for w in self.game.state.roster if not self.game.is_wrestler_booked_on_show(w.id)]
        if len(available) < 6:
            messagebox.showerror("Error", f"Need 6 wrestlers, only {len(available)} available")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Elimination Chamber - Select 6 Wrestlers")
        dialog.geometry("450x550")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Elimination Chamber", font=("Arial", 14, "bold")).pack(pady=10)
        ttk.Label(dialog, text="Select 6 wrestlers (first 2 start in ring, 3-6 in pods):").pack()

        # Listbox with multi-select
        frame = ttk.Frame(dialog)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(frame, selectmode="multiple", yscrollcommand=scrollbar.set, height=12)
        for w in available:
            listbox.insert(tk.END, f"{w.name} [{w.get_overall_rating()}] (Stam: {w.stamina})")
        listbox.pack(fill="both", expand=True)
        scrollbar.config(command=listbox.yview)

        selected_label = ttk.Label(dialog, text="Selected: 0/6")
        selected_label.pack(pady=5)

        def update_count(e=None):
            count = len(listbox.curselection())
            selected_label.config(text=f"Selected: {count}/6")

        listbox.bind("<<ListboxSelect>>", update_count)

        # Title match option
        title_frame = ttk.Frame(dialog)
        title_frame.pack(pady=5)

        is_title_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(title_frame, text="Title Match", variable=is_title_var).pack(side="left")

        titles = self.game.get_titles()
        held_titles = [t for t in titles if t.current_holder_id is not None]
        title_names = ["Select Title..."] + [t.name for t in held_titles]
        title_var = tk.StringVar(value=title_names[0])
        title_combo = ttk.Combobox(title_frame, textvariable=title_var, values=title_names, state="readonly", width=25)
        title_combo.pack(side="left", padx=5)

        def add():
            selected_indices = listbox.curselection()
            if len(selected_indices) != 6:
                messagebox.showerror("Error", f"Select exactly 6 wrestlers (selected: {len(selected_indices)})")
                return

            wrestlers = [available[i] for i in selected_indices]

            is_title = is_title_var.get()
            title_id = None
            if is_title:
                title_name = title_var.get()
                if title_name == "Select Title...":
                    messagebox.showerror("Error", "Select a title for the title match")
                    return
                title = next((t for t in held_titles if t.name == title_name), None)
                if title:
                    title_id = title.id
                    # Verify champion is in the match
                    if title.current_holder_id not in [w.id for w in wrestlers]:
                        messagebox.showerror("Error", "Champion must be in the match!")
                        return

            success, msg = self.game.add_chamber_match_to_show(wrestlers, is_title_match=is_title, title_id=title_id)
            messagebox.showinfo("Elimination Chamber", msg)
            if success:
                dialog.destroy()
                self.refresh_match_list()

        ttk.Button(dialog, text="Add Elimination Chamber", command=add).pack(pady=10)

    def add_mitb_dialog(self):
        """Dialog for adding a Money in the Bank ladder match."""
        if not self.game.get_current_show():
            messagebox.showerror("Error", "Create a show first")
            return

        available = [w for w in self.game.state.roster if not self.game.is_wrestler_booked_on_show(w.id)]
        if len(available) < 6:
            messagebox.showerror("Error", f"Need 6-8 wrestlers, only {len(available)} available")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Money in the Bank - Select 6-8 Wrestlers")
        dialog.geometry("450x500")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Money in the Bank", font=("Arial", 14, "bold")).pack(pady=10)
        ttk.Label(dialog, text="Select 6-8 wrestlers for the ladder match:").pack()

        # Check if there's already an MITB holder
        mitb_holder = self.game.get_mitb_holder()
        if mitb_holder:
            ttk.Label(dialog, text=f"Note: {mitb_holder.name} currently holds MITB", foreground="orange").pack()

        # Listbox with multi-select
        frame = ttk.Frame(dialog)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(frame, selectmode="multiple", yscrollcommand=scrollbar.set, height=12)
        for w in available:
            listbox.insert(tk.END, f"{w.name} [{w.get_overall_rating()}] (Air: {w.air})")
        listbox.pack(fill="both", expand=True)
        scrollbar.config(command=listbox.yview)

        selected_label = ttk.Label(dialog, text="Selected: 0 (need 6-8)")
        selected_label.pack(pady=5)

        def update_count(e=None):
            count = len(listbox.curselection())
            color = "green" if 6 <= count <= 8 else "red"
            selected_label.config(text=f"Selected: {count} (need 6-8)", foreground=color)

        listbox.bind("<<ListboxSelect>>", update_count)

        def add():
            selected_indices = listbox.curselection()
            if len(selected_indices) < 6 or len(selected_indices) > 8:
                messagebox.showerror("Error", f"Select 6-8 wrestlers (selected: {len(selected_indices)})")
                return

            wrestlers = [available[i] for i in selected_indices]

            success, msg = self.game.add_mitb_match_to_show(wrestlers)
            messagebox.showinfo("Money in the Bank", msg)
            if success:
                dialog.destroy()
                self.refresh_match_list()

        ttk.Button(dialog, text="Add Money in the Bank", command=add).pack(pady=10)

    def run_show(self):
        show = self.game.get_current_show()
        if not show or show.match_count == 0:
            messagebox.showerror("Error", "Add at least one match")
            return

        result = self.game.play_show()
        if result:
            self.show_results(result)
        else:
            messagebox.showerror("Error", "Could not run show")

    # --- SHOW RESULTS ---
    def show_results(self, result):
        self.clear_container()

        ttk.Label(self.container, text=f"SHOW REPORT: {result.show_name}", font=("Arial", 20, "bold")).pack(pady=10)
        ttk.Label(self.container, text=f"Final Rating: {result.final_rating}/100", font=("Arial", 16)).pack()
        ttk.Label(self.container, text=result.feedback, font=("Arial", 12)).pack(pady=5)

        # Scrollable results
        canvas = tk.Canvas(self.container)
        scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for i, match_result in enumerate(result.match_results):
            frame = ttk.LabelFrame(scrollable_frame, text=f"Match #{i+1}")
            frame.pack(fill="x", padx=10, pady=5)

            if isinstance(match_result, RumbleResult):
                ttk.Label(frame, text="ROYAL RUMBLE", font=("Arial", 12, "bold")).pack()
                ttk.Label(frame, text=f"Winner: {match_result.winner_name}", font=("Arial", 11, "bold")).pack()
                ttk.Label(frame, text=f"Rating: {match_result.rating}/100 ({match_result.stars:.1f} Stars)").pack()
                ttk.Label(frame, text="Eliminations:").pack()
                for elim in match_result.eliminations:
                    ttk.Label(frame, text=f"  {elim['elimination_order']}. {elim['wrestler_name']} (#{elim['entry_number']}) by {elim['eliminated_by']}").pack()
            elif isinstance(match_result, MultiManResult):
                title_txt = f" for {match_result.title_name}" if match_result.is_title_match else ""
                ttk.Label(frame, text=f"{match_result.match_type.upper()}{title_txt}", font=("Arial", 12, "bold")).pack()
                ttk.Label(frame, text=f"Participants: {' vs '.join(match_result.participant_names)}").pack()
                ttk.Label(frame, text=f"Winner: {match_result.winner_name}", font=("Arial", 11, "bold")).pack()
                ttk.Label(frame, text=f"Pinned: {match_result.pinned_wrestler_name}").pack()
                ttk.Label(frame, text=f"Rating: {match_result.rating}/100 ({match_result.stars:.1f} Stars)").pack()
                if match_result.title_changed:
                    ttk.Label(frame, text=f"*** NEW CHAMPION: {match_result.new_champion_name}! ***", foreground="green").pack()
            elif isinstance(match_result, LadderMatchResult):
                title_txt = f" for {match_result.title_name}" if match_result.is_title_match else ""
                ttk.Label(frame, text=f"{match_result.match_type.upper()}{title_txt}", font=("Arial", 12, "bold")).pack()
                ttk.Label(frame, text=f"Participants: {' vs '.join(match_result.participant_names)}").pack()
                ttk.Label(frame, text=f"Winner: {match_result.winner_name} retrieves the prize!", font=("Arial", 11, "bold")).pack()
                ttk.Label(frame, text=f"Rating: {match_result.rating}/100 ({match_result.stars:.1f} Stars)").pack()
                if match_result.title_changed:
                    ttk.Label(frame, text=f"*** NEW CHAMPION: {match_result.new_champion_name}! ***", foreground="green").pack()
            elif isinstance(match_result, IronManResult):
                title_txt = f" for {match_result.title_name}" if match_result.is_title_match else ""
                ttk.Label(frame, text=f"{match_result.match_type.upper()}{title_txt}", font=("Arial", 12, "bold")).pack()
                ttk.Label(frame, text=f"{match_result.wrestler_a_name} vs {match_result.wrestler_b_name}").pack()
                ttk.Label(frame, text=f"Final Score: {match_result.falls_a} - {match_result.falls_b}", font=("Arial", 11)).pack()
                if match_result.is_draw:
                    ttk.Label(frame, text="RESULT: TIME LIMIT DRAW!", font=("Arial", 11, "bold"), foreground="orange").pack()
                else:
                    ttk.Label(frame, text=f"Winner: {match_result.winner_name}", font=("Arial", 11, "bold")).pack()
                ttk.Label(frame, text=f"Rating: {match_result.rating}/100 ({match_result.stars:.1f} Stars)").pack()
                if match_result.title_changed:
                    ttk.Label(frame, text=f"*** NEW CHAMPION: {match_result.new_champion_name}! ***", foreground="green").pack()
            elif isinstance(match_result, EliminationChamberResult):
                title_txt = f" for {match_result.title_name}" if match_result.is_title_match else ""
                ttk.Label(frame, text=f"{match_result.match_type.upper()}{title_txt}", font=("Arial", 12, "bold")).pack()
                ttk.Label(frame, text=f"Participants: {', '.join(match_result.participant_names[:3])}...").pack()
                ttk.Label(frame, text=f"Winner: {match_result.winner_name}", font=("Arial", 11, "bold")).pack()
                ttk.Label(frame, text=f"Rating: {match_result.rating}/100 ({match_result.stars:.1f} Stars)").pack()
                if match_result.title_changed:
                    ttk.Label(frame, text=f"*** NEW CHAMPION: {match_result.new_champion_name}! ***", foreground="green").pack()
            elif isinstance(match_result, MoneyInTheBankResult):
                ttk.Label(frame, text=f"{match_result.match_type.upper()}", font=("Arial", 12, "bold")).pack()
                ttk.Label(frame, text=f"Participants: {', '.join(match_result.participant_names[:3])}...").pack()
                ttk.Label(frame, text=f"Winner: {match_result.winner_name}", font=("Arial", 11, "bold")).pack()
                ttk.Label(frame, text=f"{match_result.winner_name} holds the MITB Briefcase!", foreground="gold").pack()
                ttk.Label(frame, text=f"Rating: {match_result.rating}/100 ({match_result.stars:.1f} Stars)").pack()
            elif isinstance(match_result, TagMatchResult):
                title_txt = f" - {match_result.title_name}" if match_result.is_title_match else ""
                ttk.Label(frame, text=f"Tag Match{title_txt}: {match_result.team_a_name} vs {match_result.team_b_name}").pack()
                ttk.Label(frame, text=f"Winners: {match_result.winning_team_name}").pack()
                ttk.Label(frame, text=f"Rating: {match_result.rating}/100 ({match_result.stars:.1f} Stars)").pack()
                if match_result.title_changed:
                    ttk.Label(frame, text=f"*** NEW CHAMPIONS: {match_result.new_champion_name}! ***", foreground="green").pack()
            else:
                title_txt = f" - {match_result.title_name}" if match_result.is_title_match else ""
                feud_txt = f" [FEUD - {match_result.feud_intensity.upper()}]" if match_result.is_feud_match else ""
                ttk.Label(frame, text=f"Singles{title_txt}{feud_txt}: {match_result.wrestler_a_name} vs {match_result.wrestler_b_name}").pack()
                ttk.Label(frame, text=f"Winner: {match_result.winner_name}").pack()
                ttk.Label(frame, text=f"Rating: {match_result.rating}/100 ({match_result.stars:.1f} Stars)").pack()
                if match_result.interference_occurred:
                    if match_result.interference_helped:
                        ttk.Label(frame, text=f"*** INTERFERENCE! {match_result.interference_by} helped their stablemate! ***", foreground="orange").pack()
                    else:
                        ttk.Label(frame, text=f"*** DQ! {match_result.interference_by}'s interference backfired! ***", foreground="red").pack()
                if match_result.title_changed:
                    ttk.Label(frame, text=f"*** NEW CHAMPION: {match_result.new_champion_name}! ***", foreground="green").pack()
                if match_result.feud_ended:
                    ttk.Label(frame, text=f"*** FEUD CONCLUDED! ***", foreground="blue").pack()

        canvas.pack(side="left", fill="both", expand=True, pady=10)
        scrollbar.pack(side="right", fill="y")

        ttk.Label(self.container, text="[Game auto-saved]").pack(pady=5)
        ttk.Button(self.container, text="Back to Head Office", command=self.show_head_office).pack(pady=10)

    # --- STABLES ---
    def show_stables(self):
        self.clear_container()

        ttk.Label(self.container, text="Stable Management", font=("Arial", 20)).pack(pady=10)

        stables = self.game.get_active_stables()
        roster = self.game.state.roster if self.game.is_game_loaded else []

        ttk.Label(self.container, text=f"Active Stables: {len(stables)}").pack()

        if not stables:
            ttk.Label(self.container, text="No active stables.").pack(pady=20)
        else:
            for stable in stables:
                members = stable.get_members(roster)
                leader = stable.get_leader(roster)
                power = stable.get_power_rating(roster)

                frame = ttk.LabelFrame(self.container, text=f"[{power}] {stable.name}")
                frame.pack(fill="x", padx=20, pady=5)

                ttk.Label(frame, text=f"Leader: {leader.name if leader else 'Unknown'}").pack(padx=10, pady=2)
                member_names = ", ".join([m.name for m in members])
                ttk.Label(frame, text=f"Members ({len(members)}): {member_names}").pack(padx=10, pady=2)

        btn_frame = ttk.Frame(self.container)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Create Stable", command=self.create_stable_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Manage Stable", command=self.manage_stable_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Back", command=self.show_head_office).pack(side="left", padx=5)

    def create_stable_dialog(self):
        roster = self.game.state.roster
        available = [w for w in roster if not self.game.state.is_wrestler_in_stable(w.id)]

        if len(available) < 3:
            messagebox.showerror("Error", "Not enough available wrestlers (need at least 3)")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Create Stable")
        dialog.geometry("400x500")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Stable Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.pack(pady=5)

        ttk.Label(dialog, text="Select members (min 3, first is leader):", font=("Arial", 10)).pack(pady=5)

        # Listbox with multi-select
        frame = ttk.Frame(dialog)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        listbox = tk.Listbox(frame, selectmode="multiple", yscrollcommand=scrollbar.set, height=12)
        for w in available:
            listbox.insert(tk.END, f"{w.name} [{w.get_overall_rating()}]")
        listbox.pack(fill="both", expand=True)
        scrollbar.config(command=listbox.yview)

        selected_label = ttk.Label(dialog, text="Selected: 0 (min 3)")
        selected_label.pack(pady=5)

        def update_count(e=None):
            count = len(listbox.curselection())
            selected_label.config(text=f"Selected: {count} (min 3)")

        listbox.bind("<<ListboxSelect>>", update_count)

        def create():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Enter stable name")
                return

            selected_indices = listbox.curselection()
            if len(selected_indices) < 3:
                messagebox.showerror("Error", f"Select at least 3 members (selected: {len(selected_indices)})")
                return

            wrestlers = [available[i] for i in selected_indices]
            leader = wrestlers[0]
            member_ids = [w.id for w in wrestlers]

            success, msg = self.game.create_stable(name, leader.id, member_ids)
            messagebox.showinfo("Create Stable", msg)
            if success:
                dialog.destroy()
                self.show_stables()

        ttk.Button(dialog, text="Create Stable", command=create).pack(pady=10)

    def manage_stable_dialog(self):
        stables = self.game.get_active_stables()
        if not stables:
            messagebox.showerror("Error", "No active stables to manage")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Manage Stable")
        dialog.geometry("400x400")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Select Stable:").pack(pady=10)

        stable_names = [s.name for s in stables]
        stable_var = tk.StringVar()
        stable_combo = ttk.Combobox(dialog, textvariable=stable_var, values=stable_names, state="readonly", width=30)
        stable_combo.pack(pady=5)

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=20)

        def add_member():
            if not stable_var.get():
                messagebox.showerror("Error", "Select a stable")
                return
            stable = next(s for s in stables if s.name == stable_var.get())
            self.add_stable_member_dialog(stable, dialog)

        def remove_member():
            if not stable_var.get():
                messagebox.showerror("Error", "Select a stable")
                return
            stable = next(s for s in stables if s.name == stable_var.get())
            self.remove_stable_member_dialog(stable, dialog)

        def change_leader():
            if not stable_var.get():
                messagebox.showerror("Error", "Select a stable")
                return
            stable = next(s for s in stables if s.name == stable_var.get())
            self.change_stable_leader_dialog(stable, dialog)

        def disband():
            if not stable_var.get():
                messagebox.showerror("Error", "Select a stable")
                return
            stable = next(s for s in stables if s.name == stable_var.get())
            if messagebox.askyesno("Confirm", f"Disband '{stable.name}'?"):
                success, msg = self.game.disband_stable(stable.id)
                messagebox.showinfo("Disband Stable", msg)
                if success:
                    dialog.destroy()
                    self.show_stables()

        ttk.Button(btn_frame, text="Add Member", command=add_member, width=15).pack(pady=5)
        ttk.Button(btn_frame, text="Remove Member", command=remove_member, width=15).pack(pady=5)
        ttk.Button(btn_frame, text="Change Leader", command=change_leader, width=15).pack(pady=5)
        ttk.Button(btn_frame, text="Disband", command=disband, width=15).pack(pady=5)

    def add_stable_member_dialog(self, stable, parent_dialog):
        roster = self.game.state.roster
        available = [w for w in roster if not self.game.state.is_wrestler_in_stable(w.id)]

        if not available:
            messagebox.showerror("Error", "No available wrestlers to add")
            return

        dialog = tk.Toplevel(parent_dialog)
        dialog.title(f"Add Member to {stable.name}")
        dialog.geometry("300x200")
        dialog.transient(parent_dialog)
        dialog.grab_set()

        names = [f"{w.name} [{w.get_overall_rating()}]" for w in available]

        ttk.Label(dialog, text="Select wrestler to add:").pack(pady=10)
        w_var = tk.StringVar()
        w_combo = ttk.Combobox(dialog, textvariable=w_var, values=names, state="readonly", width=25)
        w_combo.pack(pady=10)

        def add():
            if not w_var.get():
                messagebox.showerror("Error", "Select a wrestler")
                return
            idx = names.index(w_var.get())
            wrestler = available[idx]
            success, msg = self.game.add_member_to_stable(stable.id, wrestler.id)
            messagebox.showinfo("Add Member", msg)
            if success:
                dialog.destroy()
                parent_dialog.destroy()
                self.show_stables()

        ttk.Button(dialog, text="Add", command=add).pack(pady=20)

    def remove_stable_member_dialog(self, stable, parent_dialog):
        roster = self.game.state.roster
        members = stable.get_members(roster)

        if len(members) <= 3:
            messagebox.showerror("Error", "Cannot remove - stable must have at least 3 members")
            return

        dialog = tk.Toplevel(parent_dialog)
        dialog.title(f"Remove Member from {stable.name}")
        dialog.geometry("300x200")
        dialog.transient(parent_dialog)
        dialog.grab_set()

        names = []
        for m in members:
            leader_mark = " (LEADER)" if m.id == stable.leader_id else ""
            names.append(f"{m.name}{leader_mark}")

        ttk.Label(dialog, text="Select wrestler to remove:").pack(pady=10)
        w_var = tk.StringVar()
        w_combo = ttk.Combobox(dialog, textvariable=w_var, values=names, state="readonly", width=25)
        w_combo.pack(pady=10)

        def remove():
            if not w_var.get():
                messagebox.showerror("Error", "Select a wrestler")
                return
            idx = names.index(w_var.get())
            wrestler = members[idx]
            success, msg = self.game.remove_member_from_stable(stable.id, wrestler.id)
            messagebox.showinfo("Remove Member", msg)
            if success:
                dialog.destroy()
                parent_dialog.destroy()
                self.show_stables()

        ttk.Button(dialog, text="Remove", command=remove).pack(pady=20)

    def change_stable_leader_dialog(self, stable, parent_dialog):
        roster = self.game.state.roster
        members = stable.get_members(roster)
        candidates = [m for m in members if m.id != stable.leader_id]

        if not candidates:
            messagebox.showerror("Error", "No other members to promote")
            return

        dialog = tk.Toplevel(parent_dialog)
        dialog.title(f"Change Leader of {stable.name}")
        dialog.geometry("300x200")
        dialog.transient(parent_dialog)
        dialog.grab_set()

        current_leader = stable.get_leader(roster)
        ttk.Label(dialog, text=f"Current Leader: {current_leader.name if current_leader else 'Unknown'}").pack(pady=5)

        names = [f"{m.name} [{m.get_overall_rating()}]" for m in candidates]

        ttk.Label(dialog, text="Select new leader:").pack(pady=5)
        w_var = tk.StringVar()
        w_combo = ttk.Combobox(dialog, textvariable=w_var, values=names, state="readonly", width=25)
        w_combo.pack(pady=10)

        def change():
            if not w_var.get():
                messagebox.showerror("Error", "Select a wrestler")
                return
            idx = names.index(w_var.get())
            wrestler = candidates[idx]
            success, msg = self.game.set_stable_leader(stable.id, wrestler.id)
            messagebox.showinfo("Change Leader", msg)
            if success:
                dialog.destroy()
                parent_dialog.destroy()
                self.show_stables()

        ttk.Button(dialog, text="Set as Leader", command=change).pack(pady=20)

    # --- RECORDS & HISTORY ---
    def show_records(self):
        self.clear_container()

        ttk.Label(self.container, text="Records & History", font=("Arial", 20)).pack(pady=10)

        match_count = len(self.game.get_match_history(limit=0))
        ttk.Label(self.container, text=f"Total Matches Recorded: {match_count}", font=("Arial", 12)).pack(pady=5)

        btn_frame = ttk.Frame(self.container)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Recent Matches", command=self.show_recent_matches, width=25).pack(pady=5)
        ttk.Button(btn_frame, text="Wrestler Records", command=self.show_wrestler_records_dialog, width=25).pack(pady=5)
        ttk.Button(btn_frame, text="Head-to-Head", command=self.show_head_to_head_dialog, width=25).pack(pady=5)
        ttk.Button(btn_frame, text="Title History", command=self.show_title_history_dialog, width=25).pack(pady=5)
        ttk.Button(btn_frame, text="Back", command=self.show_head_office, width=25).pack(pady=10)

    def show_recent_matches(self):
        self.clear_container()

        ttk.Label(self.container, text="Recent Matches", font=("Arial", 20)).pack(pady=10)

        matches = self.game.get_match_history(limit=20)

        if not matches:
            ttk.Label(self.container, text="No match history yet. Run some shows!").pack(pady=20)
        else:
            # Scrollable frame
            canvas = tk.Canvas(self.container, height=400)
            scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Display matches in reverse order (most recent first)
            for match in reversed(matches):
                ppv_tag = "[PPV] " if match.is_ppv else ""
                date_str = f"Y{match.date['year']} M{match.date['month']} W{match.date['week']}"

                frame = ttk.LabelFrame(scrollable_frame, text=f"{ppv_tag}{match.show_name} ({date_str})")
                frame.pack(fill="x", padx=10, pady=5)

                ttk.Label(frame, text=f"{match.match_type}: {' vs '.join(match.participant_names)}").pack(padx=10, pady=2)

                if match.winner_names:
                    ttk.Label(frame, text=f"Winner: {', '.join(match.winner_names)}").pack(padx=10)
                else:
                    ttk.Label(frame, text="Result: DRAW").pack(padx=10)

                ttk.Label(frame, text=f"Rating: {match.rating}/100 ({match.stars:.1f} stars)").pack(padx=10, pady=2)

                if match.is_title_match:
                    if match.title_changed:
                        ttk.Label(frame, text=f"*** TITLE CHANGE: {match.title_name} ***", foreground="green").pack(padx=10)
                    else:
                        ttk.Label(frame, text=f"Title Defense: {match.title_name}").pack(padx=10)

            canvas.pack(side="left", fill="both", expand=True, pady=10)
            scrollbar.pack(side="right", fill="y")

        ttk.Button(self.container, text="Back", command=self.show_records).pack(pady=10)

    def show_wrestler_records_dialog(self):
        roster = self.game.get_roster()

        if not roster:
            messagebox.showerror("Error", "No wrestlers on roster")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Wrestler Records")
        dialog.geometry("500x550")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Select Wrestler:", font=("Arial", 12)).pack(pady=10)

        # Create wrestler list with streak indicators
        wrestler_names = []
        for w in roster:
            records = self.game.get_wrestler_records(w.id)
            streak_str = ""
            if records:
                if records.current_win_streak >= 3:
                    streak_str = f" [W{records.current_win_streak}]"
                elif records.current_loss_streak >= 3:
                    streak_str = f" [L{records.current_loss_streak}]"
            wrestler_names.append(f"{w.name} ({w.wins}W-{w.losses}L){streak_str}")

        wrestler_var = tk.StringVar()
        wrestler_combo = ttk.Combobox(dialog, textvariable=wrestler_var, values=wrestler_names, state="readonly", width=40)
        wrestler_combo.pack(pady=5)

        # Results frame
        results_frame = ttk.LabelFrame(dialog, text="Records")
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        result_text = tk.Text(results_frame, width=55, height=20, state="disabled")
        result_text.pack(fill="both", expand=True, padx=5, pady=5)

        def show_records():
            if not wrestler_var.get():
                return

            idx = wrestler_names.index(wrestler_var.get())
            wrestler = roster[idx]
            records = self.game.get_wrestler_records(wrestler.id)

            result_text.config(state="normal")
            result_text.delete(1.0, tk.END)

            result_text.insert(tk.END, f"=== {wrestler.name} ===\n\n")
            result_text.insert(tk.END, f"--- OVERALL ---\n")
            result_text.insert(tk.END, f"  Total Record: {wrestler.wins}W - {wrestler.losses}L\n\n")

            result_text.insert(tk.END, f"--- STREAKS ---\n")
            result_text.insert(tk.END, f"  Current Win Streak: {records.current_win_streak}\n")
            result_text.insert(tk.END, f"  Current Loss Streak: {records.current_loss_streak}\n")
            result_text.insert(tk.END, f"  Longest Win Streak: {records.longest_win_streak}\n")
            result_text.insert(tk.END, f"  Longest Loss Streak: {records.longest_loss_streak}\n\n")

            result_text.insert(tk.END, f"--- PPV vs TV ---\n")
            result_text.insert(tk.END, f"  PPV Record: {records.ppv_wins}W - {records.ppv_losses}L\n")
            result_text.insert(tk.END, f"  TV Record: {records.tv_wins}W - {records.tv_losses}L\n\n")

            # Recent matches
            recent = self.game.get_wrestler_match_history(wrestler.id, limit=5)
            if recent:
                result_text.insert(tk.END, f"--- RECENT MATCHES ---\n")
                for match in reversed(recent):
                    result_char = "W" if wrestler.id in match.winner_ids else ("L" if wrestler.id in match.loser_ids else "D")
                    ppv_tag = "[PPV]" if match.is_ppv else "[TV]"
                    opponents = [n for n in match.participant_names if n != wrestler.name]
                    result_text.insert(tk.END, f"  {ppv_tag} {result_char} - {match.match_type} vs {', '.join(opponents)}\n")

            result_text.config(state="disabled")

        wrestler_combo.bind("<<ComboboxSelected>>", lambda e: show_records())

        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)

    def show_head_to_head_dialog(self):
        roster = self.game.get_roster()

        if len(roster) < 2:
            messagebox.showerror("Error", "Need at least 2 wrestlers")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Head-to-Head")
        dialog.geometry("550x500")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Head-to-Head Lookup", font=("Arial", 14, "bold")).pack(pady=10)

        names = [f"{w.name} [{w.get_overall_rating()}]" for w in roster]

        select_frame = ttk.Frame(dialog)
        select_frame.pack(pady=10)

        ttk.Label(select_frame, text="Wrestler A:").pack(side="left", padx=5)
        w1_var = tk.StringVar()
        w1_combo = ttk.Combobox(select_frame, textvariable=w1_var, values=names, state="readonly", width=20)
        w1_combo.pack(side="left", padx=5)

        ttk.Label(select_frame, text="vs").pack(side="left", padx=10)

        ttk.Label(select_frame, text="Wrestler B:").pack(side="left", padx=5)
        w2_var = tk.StringVar()
        w2_combo = ttk.Combobox(select_frame, textvariable=w2_var, values=names, state="readonly", width=20)
        w2_combo.pack(side="left", padx=5)

        # Results frame
        results_frame = ttk.LabelFrame(dialog, text="Results")
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        result_text = tk.Text(results_frame, width=60, height=18, state="disabled")
        result_text.pack(fill="both", expand=True, padx=5, pady=5)

        def lookup():
            if not w1_var.get() or not w2_var.get():
                messagebox.showerror("Error", "Select both wrestlers")
                return
            if w1_var.get() == w2_var.get():
                messagebox.showerror("Error", "Select different wrestlers")
                return

            idx1 = names.index(w1_var.get())
            idx2 = names.index(w2_var.get())
            wrestler_a = roster[idx1]
            wrestler_b = roster[idx2]

            h2h = self.game.get_head_to_head(wrestler_a.id, wrestler_b.id)

            result_text.config(state="normal")
            result_text.delete(1.0, tk.END)

            result_text.insert(tk.END, f"=== {wrestler_a.name} vs {wrestler_b.name} ===\n\n")
            result_text.insert(tk.END, f"--- OVERALL RECORD ---\n")
            result_text.insert(tk.END, f"  {wrestler_a.name}: {h2h['wins_a']} wins\n")
            result_text.insert(tk.END, f"  {wrestler_b.name}: {h2h['wins_b']} wins\n")
            result_text.insert(tk.END, f"  Total Matches: {h2h['total_matches']}\n\n")

            if h2h['matches']:
                result_text.insert(tk.END, f"--- MATCH HISTORY ---\n")
                for match in reversed(h2h['matches']):
                    date_str = f"Y{match.date['year']} M{match.date['month']} W{match.date['week']}"
                    winner = match.winner_names[0] if match.winner_names else "DRAW"
                    ppv_tag = "[PPV]" if match.is_ppv else "[TV]"
                    result_text.insert(tk.END, f"  {ppv_tag} {date_str}: {match.match_type} - Winner: {winner} ({match.stars:.1f}*)\n")
                    if match.title_changed:
                        result_text.insert(tk.END, f"        *** {match.title_name} changed hands ***\n")
            else:
                result_text.insert(tk.END, "No matches between these wrestlers yet.\n")

            result_text.config(state="disabled")

        ttk.Button(dialog, text="Look Up", command=lookup).pack(pady=5)
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=5)

    def show_title_history_dialog(self):
        titles = self.game.get_titles()

        if not titles:
            messagebox.showerror("Error", "No championships exist")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Title History")
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Title History", font=("Arial", 14, "bold")).pack(pady=10)

        ttk.Label(dialog, text="Select Title:").pack(pady=5)
        title_names = [f"{t.name} [Prestige: {t.prestige}]" for t in titles]
        title_var = tk.StringVar()
        title_combo = ttk.Combobox(dialog, textvariable=title_var, values=title_names, state="readonly", width=35)
        title_combo.pack(pady=5)

        # Results frame
        results_frame = ttk.LabelFrame(dialog, text="Reign History")
        results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        result_text = tk.Text(results_frame, width=55, height=18, state="disabled")
        result_text.pack(fill="both", expand=True, padx=5, pady=5)

        def show_history():
            if not title_var.get():
                return

            idx = title_names.index(title_var.get())
            title = titles[idx]
            history = self.game.get_title_history(title.id)

            result_text.config(state="normal")
            result_text.delete(1.0, tk.END)

            result_text.insert(tk.END, f"=== {title.name} ===\n\n")

            # Current champion
            if title.current_holder_id:
                holder = self.game.get_wrestler_by_id(title.current_holder_id)
                if not holder:
                    team = self.game.get_tag_team_by_id(title.current_holder_id)
                    holder_name = team.name if team else "Unknown"
                else:
                    holder_name = holder.name
                result_text.insert(tk.END, f"Current Champion: {holder_name}\n\n")
            else:
                result_text.insert(tk.END, f"Current Champion: VACANT\n\n")

            if not history:
                result_text.insert(tk.END, "No reign history recorded yet.\n")
            else:
                result_text.insert(tk.END, f"--- REIGN HISTORY ({len(history)} reigns) ---\n\n")
                for reign in reversed(history):
                    won_date = f"Y{reign.won_date['year']} M{reign.won_date['month']} W{reign.won_date['week']}"
                    if reign.lost_date:
                        lost_date = f"Y{reign.lost_date['year']} M{reign.lost_date['month']} W{reign.lost_date['week']}"
                        status = f"Lost: {lost_date}"
                    else:
                        status = "CURRENT"

                    result_text.insert(tk.END, f"  {reign.holder_name}\n")
                    result_text.insert(tk.END, f"    Won: {won_date} | {status}\n")
                    result_text.insert(tk.END, f"    Successful Defenses: {reign.successful_defenses}\n\n")

            result_text.config(state="disabled")

        title_combo.bind("<<ComboboxSelected>>", lambda e: show_history())

        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)


def main():
    root = tk.Tk()
    app = WrestlingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

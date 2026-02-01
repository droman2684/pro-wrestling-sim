"""
Flask Web UI for Pro Wrestling Sim
"""
import sys
import os

# Add the 'src' directory to the Python path
# We determine it relative to this file's location
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

def get_base_path():
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        return sys._MEIPASS
    # Running in normal Python environment
    return os.path.abspath(os.path.dirname(__file__))

base_path = get_base_path()
template_dir = os.path.join(base_path, 'templates')
static_dir = os.path.join(base_path, 'static')

from flask import Flask, render_template, request, redirect, url_for, flash, session
from services.game_service import GameService
from core.calendar import is_ppv_week, get_ppv_for_week, DayOfWeek, ShowTier

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = 'pro-wrestling-sim-2026'

# Global game service instance
game = GameService()

# Store last show result (for display after running show)
last_show_result = None


# --- Helper Functions ---

def get_game():
    """Get the game service instance."""
    return game


def require_game_loaded(f):
    """Decorator to require a game to be loaded."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not game.is_game_loaded:
            flash('Please load or create a game first.', 'warning')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# --- Routes: Start Menu ---

@app.route('/')
def index():
    """Start menu - new game or load game."""
    databases = game.list_databases()
    saves = game.list_saves()
    return render_template('index.html', databases=databases, saves=saves)


@app.route('/new-game', methods=['POST'])
def new_game():
    """Create a new game."""
    db_name = request.form.get('database')
    save_name = request.form.get('save_name')

    if not db_name or not save_name:
        flash('Please fill all fields.', 'error')
        return redirect(url_for('index'))

    success, msg = game.create_new_game(db_name, save_name)
    flash(msg, 'success' if success else 'error')

    if success:
        return redirect(url_for('dashboard'))
    return redirect(url_for('index'))


@app.route('/load-game', methods=['POST'])
def load_game():
    """Load an existing game."""
    save_name = request.form.get('save_name')

    if not save_name:
        flash('Please select a save.', 'error')
        return redirect(url_for('index'))

    success, msg = game.load_game(save_name)
    flash(msg, 'success' if success else 'error')

    if success:
        return redirect(url_for('dashboard'))
    return redirect(url_for('index'))


# --- Routes: Dashboard ---

@app.route('/dashboard')
@require_game_loaded
def dashboard():
    """Main dashboard / head office."""
    # Get all data for dashboard
    rankings = game.get_wrestler_rankings()[:5]
    tag_rankings = game.get_tag_team_rankings()[:5]
    titles = game.get_titles()
    feuds = game.get_active_feuds()
    stables = game.get_active_stables()
    company = game.get_company()
    mitb_holder = game.get_mitb_holder()

    # Check if PPV week (using new method)
    state = game.state
    is_ppv = state.calendar_manager.is_ppv_week(state.month, state.week)
    ppv_info = state.calendar_manager.get_ppv_for_week(state.month, state.week) if is_ppv else None
    
    # Get remaining shows for this week
    remaining_shows = game.get_remaining_shows_this_week()
    total_shows_week = len(game.get_week_schedule())
    completed_shows_week = total_shows_week - len(remaining_shows)

    # Get news
    news = game.get_news(limit=5)
    print(f"DEBUG: Dashboard loading with {len(news)} news items.")

    return render_template('dashboard.html',
        save_name=game.get_save_name(),
        date_string=game.get_current_date_string(),
        next_ppv=game.get_next_ppv_string(),
        rankings=rankings,
        tag_rankings=tag_rankings,
        titles=titles,
        feuds=feuds,
        stables=stables,
        company=company,
        mitb_holder=mitb_holder,
        is_ppv=is_ppv,
        ppv_info=ppv_info,
        roster=game.get_roster(),
        remaining_shows=remaining_shows,
        week_progress=f"{completed_shows_week}/{total_shows_week}",
        news=news,
        game=game
    )


@app.route('/save-game', methods=['POST'])
@require_game_loaded
def save_game():
    """Save the current game."""
    success, msg = game.save_game()
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('dashboard'))


@app.route('/exit-game')
def exit_game():
    """Exit to main menu."""
    return redirect(url_for('index'))


# --- Routes: Roster ---

@app.route('/roster')
@require_game_loaded
def roster():
    """View roster."""
    wrestlers = game.get_roster()
    return render_template('roster.html', wrestlers=wrestlers, game=game)


@app.route('/wrestler/<int:wrestler_id>')
@require_game_loaded
def wrestler_profile(wrestler_id):
    """View wrestler profile."""
    wrestler = game.get_wrestler_by_id(wrestler_id)
    if not wrestler:
        flash('Wrestler not found.', 'error')
        return redirect(url_for('roster'))

    # Get additional info
    feud = game.get_wrestler_feud(wrestler_id)
    stable = game.get_wrestler_stable(wrestler_id)
    records = game.get_wrestler_records(wrestler_id)

    # Get titles held
    titles_held = [t for t in game.get_titles() if t.current_holder_id == wrestler_id]

    return render_template('wrestler.html',
        wrestler=wrestler,
        feud=feud,
        stable=stable,
        records=records,
        titles_held=titles_held,
        game=game
    )


@app.route('/create-wrestler', methods=['GET', 'POST'])
@require_game_loaded
def create_wrestler():
    """Create a new wrestler with the new 27-attribute system."""
    if request.method == 'POST':
        # Get optional secondary style (can be empty string)
        secondary_style = request.form.get('secondary_style', '')
        if not secondary_style:
            secondary_style = None

        success, msg = game.create_wrestler(
            # Identity
            name=request.form.get('name', ''),
            nickname=request.form.get('nickname', ''),
            age=int(request.form.get('age', 25)),
            height=int(request.form.get('height', 72)),
            weight=int(request.form.get('weight', 220)),
            region=request.form.get('region', 'Unknown'),
            alignment=request.form.get('alignment', 'Face'),
            # Styles
            primary_style=request.form.get('primary_style', 'all_rounder'),
            secondary_style=secondary_style,
            # Finisher
            finisher_name=request.form.get('finisher_name', ''),
            finisher_type=request.form.get('finisher_type', 'power'),
            # Physical
            strength=int(request.form.get('strength', 50)),
            speed=int(request.form.get('speed', 50)),
            agility=int(request.form.get('agility', 50)),
            durability=int(request.form.get('durability', 50)),
            recovery=int(request.form.get('recovery', 50)),
            # Offense
            striking=int(request.form.get('striking', 50)),
            grappling=int(request.form.get('grappling', 50)),
            submission=int(request.form.get('submission', 50)),
            high_flying=int(request.form.get('high_flying', 50)),
            hardcore=int(request.form.get('hardcore', 50)),
            power_moves=int(request.form.get('power_moves', 50)),
            technical=int(request.form.get('technical', 50)),
            dirty_tactics=int(request.form.get('dirty_tactics', 50)),
            # Defense
            strike_defense=int(request.form.get('strike_defense', 50)),
            grapple_defense=int(request.form.get('grapple_defense', 50)),
            aerial_defense=int(request.form.get('aerial_defense', 50)),
            ring_awareness=int(request.form.get('ring_awareness', 50)),
            # Entertainment
            mic_skills=int(request.form.get('mic_skills', 50)),
            charisma=int(request.form.get('charisma', 50)),
            look=int(request.form.get('look', 50)),
            star_power=int(request.form.get('star_power', 50)),
            entrance=int(request.form.get('entrance', 50)),
            # Intangibles
            psychology=int(request.form.get('psychology', 50)),
            consistency=int(request.form.get('consistency', 75)),
            big_match=int(request.form.get('big_match', 50)),
            clutch=int(request.form.get('clutch', 50))
        )
        flash(msg, 'success' if success else 'error')
        if success:
            return redirect(url_for('roster'))

    return render_template('create_wrestler.html', game=game)


# --- Routes: Titles ---

@app.route('/titles')
@require_game_loaded
def titles():
    """View titles."""
    all_titles = game.get_titles()
    return render_template('titles.html', titles=all_titles, game=game)


@app.route('/title/<int:title_id>')
@require_game_loaded
def title_history(title_id):
    """View title history."""
    title = game.get_title_by_id(title_id)
    if not title:
        flash('Title not found.', 'error')
        return redirect(url_for('titles'))

    history = game.get_title_history(title_id)
    holder = game.get_wrestler_by_id(title.current_holder_id) if title.current_holder_id else None

    return render_template('title_history.html', title=title, history=history, holder=holder, game=game)


@app.route('/create-title', methods=['GET', 'POST'])
@require_game_loaded
def create_title():
    """Create a new title."""
    if request.method == 'POST':
        success, msg = game.create_title(
            name=request.form.get('name', ''),
            prestige=int(request.form.get('prestige', 50))
        )
        flash(msg, 'success' if success else 'error')
        if success:
            return redirect(url_for('titles'))

    return render_template('create_title.html', game=game)


# --- Routes: Rankings ---

@app.route('/rankings')
@require_game_loaded
def rankings():
    """View rankings."""
    wrestler_rankings = game.get_wrestler_rankings()[:10]
    tag_rankings = game.get_tag_team_rankings()[:10]
    title_rankings = game.get_title_rankings()
    
    return render_template('rankings.html',
        wrestler_rankings=wrestler_rankings,
        tag_rankings=tag_rankings,
        title_rankings=title_rankings,
        game=game
    )


# --- Routes: Booking ---

@app.route('/booking')
@require_game_loaded
def booking():
    """Book a show."""
    # Check if there's a current show
    current_show = game.get_current_show()

    # Get current week's scheduled shows that aren't booked yet
    week_shows = game.get_week_schedule()
    unbooked_shows = [s for s in week_shows if not s.is_booked and not s.is_completed]

    # Get selected show from session, or auto-select first available
    selected_show_id = session.get('selected_show_id')
    
    if not selected_show_id and unbooked_shows:
        selected_show_id = unbooked_shows[0].id
        session['selected_show_id'] = selected_show_id
        
    selected_show = None
    selected_brand = None

    if selected_show_id:
        selected_show = game.get_scheduled_show_by_id(selected_show_id)
        if selected_show and selected_show.brand_id:
            selected_brand = game.get_brand_by_id(selected_show.brand_id)

    # Filter wrestlers/teams/titles by brand if show has brand_id
    if selected_show and selected_show.brand_id:
        wrestlers = game.get_brand_roster(selected_show.brand_id)
        tag_teams = game.get_available_tag_teams(brand_id=selected_show.brand_id)
        titles = game.get_brand_titles(selected_show.brand_id)
        
        # Filter rankings for this brand
        all_wrestler_rankings = game.get_wrestler_rankings()
        wrestler_rankings = [w for w in all_wrestler_rankings if game.get_wrestler_brand(w.id).id == selected_show.brand_id]
        
        all_tag_rankings = game.get_tag_team_rankings()
        # Filter tag teams where both members are in this brand (already handled by get_available_tag_teams logic mostly, but let's be safe)
        # Actually simplest is to check if the team object is in the filtered tag_teams list
        tag_team_ids = [t.id for t in tag_teams]
        tag_rankings = [t for t in all_tag_rankings if t.id in tag_team_ids]
        
    else:
        wrestlers = game.get_roster()
        tag_teams = game.get_available_tag_teams()
        titles = game.get_titles()
        wrestler_rankings = game.get_wrestler_rankings()
        tag_rankings = game.get_tag_team_rankings()

    # Check if PPV
    state = game.state
    is_ppv = state.calendar_manager.is_ppv_week(state.month, state.week)
    ppv_info = state.calendar_manager.get_ppv_for_week(state.month, state.week) if is_ppv else None

    return render_template('booking.html',
        current_show=current_show,
        wrestlers=wrestlers,
        tag_teams=tag_teams,
        titles=titles,
        wrestler_rankings=wrestler_rankings,
        tag_rankings=tag_rankings,
        is_ppv=is_ppv,
        ppv_info=ppv_info,
        unbooked_shows=unbooked_shows,
        selected_show=selected_show,
        selected_brand=selected_brand,
        game=game
    )


@app.route('/booking/select-show', methods=['POST'])
@require_game_loaded
def select_show():
    """Select a scheduled show to book."""
    show_id = request.form.get('show_id')
    if show_id:
        session['selected_show_id'] = int(show_id)
        scheduled = game.get_scheduled_show_by_id(int(show_id))
        if scheduled:
            flash(f'Selected show: {scheduled.name}', 'success')
    else:
        session.pop('selected_show_id', None)
        flash('Cleared show selection', 'info')
    return redirect(url_for('booking'))


@app.route('/booking/clear-selection', methods=['POST'])
@require_game_loaded
def clear_show_selection():
    """Clear the selected show."""
    session.pop('selected_show_id', None)
    flash('Cleared show selection', 'info')
    return redirect(url_for('booking'))


@app.route('/booking/create-show', methods=['POST'])
@require_game_loaded
def create_show():
    """Create a new show."""
    show_name = request.form.get('show_name', 'Weekly Show')
    scheduled_show_id = session.get('selected_show_id')

    # Use scheduled show if selected
    game.create_show(show_name, scheduled_show_id=scheduled_show_id)
    flash(f'Created show: {show_name}', 'success')
    return redirect(url_for('booking'))


@app.route('/booking/add-singles', methods=['POST'])
@require_game_loaded
def add_singles_match():
    """Add a singles match."""
    wrestler_a_id = int(request.form.get('wrestler_a'))
    wrestler_b_id = int(request.form.get('wrestler_b'))
    is_steel_cage = request.form.get('steel_cage') == 'on'
    is_title_match = request.form.get('title_match') == 'on'
    title_id = int(request.form.get('title_id')) if request.form.get('title_id') else None

    w1 = game.get_wrestler_by_id(wrestler_a_id)
    w2 = game.get_wrestler_by_id(wrestler_b_id)

    if not w1 or not w2:
        flash('Invalid wrestlers selected.', 'error')
        return redirect(url_for('booking'))

    if game.add_match_to_show(w1, w2, is_steel_cage=is_steel_cage, is_title_match=is_title_match, title_id=title_id):
        flash(f'Added: {w1.name} vs {w2.name}', 'success')
    else:
        flash('Could not add match.', 'error')

    return redirect(url_for('booking'))


@app.route('/booking/add-tag', methods=['POST'])
@require_game_loaded
def add_tag_match():
    """Add a tag team match."""
    team_a_id = int(request.form.get('team_a'))
    team_b_id = int(request.form.get('team_b'))
    is_title_match = request.form.get('title_match') == 'on'
    title_id = int(request.form.get('title_id')) if request.form.get('title_id') else None

    t1 = game.get_tag_team_by_id(team_a_id)
    t2 = game.get_tag_team_by_id(team_b_id)

    if not t1 or not t2:
        flash('Invalid teams selected.', 'error')
        return redirect(url_for('booking'))

    if game.add_tag_match_to_show(t1, t2, is_title_match=is_title_match, title_id=title_id):
        flash(f'Added: {t1.name} vs {t2.name}', 'success')
    else:
        flash('Could not add match.', 'error')

    return redirect(url_for('booking'))


@app.route('/booking/add-multi', methods=['POST'])
@require_game_loaded
def add_multi_match():
    """Add a multi-man match (triple threat / fatal 4-way)."""
    wrestler_ids = request.form.getlist('wrestlers')
    is_title_match = request.form.get('title_match') == 'on'
    title_id = int(request.form.get('title_id')) if request.form.get('title_id') else None

    wrestlers = [game.get_wrestler_by_id(int(wid)) for wid in wrestler_ids]
    wrestlers = [w for w in wrestlers if w is not None]

    if len(wrestlers) < 3 or len(wrestlers) > 4:
        flash('Select 3-4 wrestlers for multi-man match.', 'error')
        return redirect(url_for('booking'))

    success, msg = game.add_multi_man_match_to_show(wrestlers, is_title_match=is_title_match, title_id=title_id)
    flash(msg, 'success' if success else 'error')

    return redirect(url_for('booking'))


@app.route('/booking/add-ladder', methods=['POST'])
@require_game_loaded
def add_ladder_match():
    """Add a ladder match."""
    wrestler_ids = request.form.getlist('wrestlers')
    is_title_match = request.form.get('title_match') == 'on'
    title_id = int(request.form.get('title_id')) if request.form.get('title_id') else None

    wrestlers = [game.get_wrestler_by_id(int(wid)) for wid in wrestler_ids]
    wrestlers = [w for w in wrestlers if w is not None]

    if len(wrestlers) < 2:
        flash('Select at least 2 wrestlers for ladder match.', 'error')
        return redirect(url_for('booking'))

    success, msg = game.add_ladder_match_to_show(wrestlers, is_title_match=is_title_match, title_id=title_id)
    flash(msg, 'success' if success else 'error')

    return redirect(url_for('booking'))


@app.route('/booking/add-ironman', methods=['POST'])
@require_game_loaded
def add_ironman_match():
    """Add an Iron Man match."""
    wrestler_a_id = int(request.form.get('wrestler_a'))
    wrestler_b_id = int(request.form.get('wrestler_b'))
    time_limit = int(request.form.get('time_limit', 30))
    is_title_match = request.form.get('title_match') == 'on'
    title_id = int(request.form.get('title_id')) if request.form.get('title_id') else None

    w1 = game.get_wrestler_by_id(wrestler_a_id)
    w2 = game.get_wrestler_by_id(wrestler_b_id)

    if not w1 or not w2:
        flash('Invalid wrestlers selected.', 'error')
        return redirect(url_for('booking'))

    success, msg = game.add_iron_man_match_to_show(w1, w2, time_limit, is_title_match=is_title_match, title_id=title_id)
    flash(msg, 'success' if success else 'error')

    return redirect(url_for('booking'))


@app.route('/booking/add-chamber', methods=['POST'])
@require_game_loaded
def add_chamber_match():
    """Add an Elimination Chamber match."""
    wrestler_ids = request.form.getlist('wrestlers')
    is_title_match = request.form.get('title_match') == 'on'
    title_id = int(request.form.get('title_id')) if request.form.get('title_id') else None

    wrestlers = [game.get_wrestler_by_id(int(wid)) for wid in wrestler_ids]
    wrestlers = [w for w in wrestlers if w is not None]

    if len(wrestlers) != 6:
        flash('Select exactly 6 wrestlers for Elimination Chamber.', 'error')
        return redirect(url_for('booking'))

    success, msg = game.add_chamber_match_to_show(wrestlers, is_title_match=is_title_match, title_id=title_id)
    flash(msg, 'success' if success else 'error')

    return redirect(url_for('booking'))


@app.route('/booking/add-mitb', methods=['POST'])
@require_game_loaded
def add_mitb_match():
    """Add a Money in the Bank match."""
    wrestler_ids = request.form.getlist('wrestlers')

    wrestlers = [game.get_wrestler_by_id(int(wid)) for wid in wrestler_ids]
    wrestlers = [w for w in wrestlers if w is not None]

    if len(wrestlers) < 6 or len(wrestlers) > 8:
        flash('Select 6-8 wrestlers for Money in the Bank.', 'error')
        return redirect(url_for('booking'))

    success, msg = game.add_mitb_match_to_show(wrestlers)
    flash(msg, 'success' if success else 'error')

    return redirect(url_for('booking'))


@app.route('/booking/add-rumble', methods=['POST'])
@require_game_loaded
def add_rumble_match():
    """Add a Royal Rumble match."""
    wrestler_ids = request.form.getlist('wrestlers')

    wrestlers = [game.get_wrestler_by_id(int(wid)) for wid in wrestler_ids]
    wrestlers = [w for w in wrestlers if w is not None]

    if len(wrestlers) != 10:
        flash('Select exactly 10 wrestlers for Royal Rumble.', 'error')
        return redirect(url_for('booking'))

    success, msg = game.add_rumble_to_show(wrestlers)
    flash(msg, 'success' if success else 'error')

    return redirect(url_for('booking'))


@app.route('/booking/run-show', methods=['POST'])
@require_game_loaded
def run_show():
    """Run the booked show."""
    global last_show_result
    result = game.play_show()

    if result:
        # Clear show selection
        session.pop('selected_show_id', None)
        # Store result for display
        last_show_result = result
        return redirect(url_for('show_results'))
    else:
        flash('Could not run show. Make sure matches are booked.', 'error')
        return redirect(url_for('booking'))


@app.route('/booking/cancel', methods=['POST'])
@require_game_loaded
def cancel_show():
    """Cancel current show."""
    game.cancel_show()
    session.pop('selected_show_id', None)
    flash('Show cancelled.', 'info')
    return redirect(url_for('booking'))


@app.route('/booking/ai-book')
@require_game_loaded
def ai_booking():
    """AI booking suggestions."""
    # Get selected show for brand filtering
    selected_show_id = session.get('selected_show_id')
    selected_show = None
    brand_id = None
    show_name = None

    if selected_show_id:
        selected_show = game.get_scheduled_show_by_id(selected_show_id)
        if selected_show:
            brand_id = selected_show.brand_id
            show_name = selected_show.name

    suggestions = game.get_card_suggestions(show_name=show_name, brand_id=brand_id)

    if not suggestions:
        flash('Could not generate suggestions.', 'error')
        return redirect(url_for('booking'))

    return render_template('ai_booking.html',
        suggestions=suggestions,
        selected_show=selected_show,
        game=game
    )


@app.route('/booking/apply-ai', methods=['POST'])
@require_game_loaded
def apply_ai_booking():
    """Apply AI booking suggestions."""
    # Get selected show for brand filtering
    selected_show_id = session.get('selected_show_id')
    selected_show = None
    brand_id = None
    show_name = None

    if selected_show_id:
        selected_show = game.get_scheduled_show_by_id(selected_show_id)
        if selected_show:
            brand_id = selected_show.brand_id
            show_name = selected_show.name

    suggestions = game.get_card_suggestions(show_name=show_name, brand_id=brand_id)

    if not suggestions:
        flash('Could not generate suggestions.', 'error')
        return redirect(url_for('booking'))

    # Get selected match indices
    selected = request.form.getlist('matches')

    # Mark selected as accepted
    for i, match in enumerate(suggestions.matches):
        match.is_accepted = str(i) in selected

    success, msg = game.apply_card_suggestions(suggestions)
    flash(msg, 'success' if success else 'error')

    if success:
        return redirect(url_for('booking'))
    return redirect(url_for('ai_booking'))


# --- Routes: Show Results ---

@app.route('/results')
@require_game_loaded
def show_results():
    """View last show results."""
    global last_show_result
    if not last_show_result:
        flash('No recent show results.', 'info')
        return redirect(url_for('dashboard'))

    return render_template('results.html', result=last_show_result, game=game)


# --- Routes: Feuds ---

@app.route('/feuds')
@require_game_loaded
def feuds():
    """View feuds."""
    all_feuds = game.get_feuds()
    return render_template('feuds.html', feuds=all_feuds, game=game)


@app.route('/create-feud', methods=['GET', 'POST'])
@require_game_loaded
def create_feud():
    """Create a new feud."""
    if request.method == 'POST':
        success, msg = game.create_feud(
            wrestler_a_id=int(request.form.get('wrestler_a')),
            wrestler_b_id=int(request.form.get('wrestler_b')),
            intensity=request.form.get('intensity', 'heated'),
            matches=int(request.form.get('matches', 3))
        )
        flash(msg, 'success' if success else 'error')
        if success:
            return redirect(url_for('feuds'))

    wrestlers = game.get_roster()
    return render_template('create_feud.html', wrestlers=wrestlers, game=game)


@app.route('/feud/<int:feud_id>/end', methods=['POST'])
@require_game_loaded
def end_feud(feud_id):
    """End a feud."""
    success, msg = game.end_feud(feud_id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('feuds'))


@app.route('/feud/<int:feud_id>/blowoff', methods=['POST'])
@require_game_loaded
def schedule_blowoff(feud_id):
    """Schedule a blowoff match."""
    success, msg = game.schedule_blowoff_match(feud_id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('feuds'))


# --- Routes: Stables ---

@app.route('/stables')
@require_game_loaded
def stables():
    """View stables."""
    all_stables = game.get_stables()
    return render_template('stables.html', stables=all_stables, game=game)


@app.route('/create-stable', methods=['GET', 'POST'])
@require_game_loaded
def create_stable():
    """Create a new stable."""
    if request.method == 'POST':
        member_ids = [int(m) for m in request.form.getlist('members')]
        leader_id = int(request.form.get('leader'))

        success, msg = game.create_stable(
            name=request.form.get('name', ''),
            leader_id=leader_id,
            member_ids=member_ids
        )
        flash(msg, 'success' if success else 'error')
        if success:
            return redirect(url_for('stables'))

    wrestlers = game.get_roster()
    return render_template('create_stable.html', wrestlers=wrestlers, game=game)


@app.route('/stable/<int:stable_id>/disband', methods=['POST'])
@require_game_loaded
def disband_stable(stable_id):
    """Disband a stable."""
    success, msg = game.disband_stable(stable_id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('stables'))


@app.route('/stable/<int:stable_id>/add-member', methods=['POST'])
@require_game_loaded
def add_stable_member(stable_id):
    """Add a member to a stable."""
    wrestler_id = int(request.form.get('wrestler_id'))
    success, msg = game.add_member_to_stable(stable_id, wrestler_id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('stables'))


@app.route('/stable/<int:stable_id>/remove-member', methods=['POST'])
@require_game_loaded
def remove_stable_member(stable_id):
    """Remove a member from a stable."""
    wrestler_id = int(request.form.get('wrestler_id'))
    success, msg = game.remove_member_from_stable(stable_id, wrestler_id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('stables'))


# --- Routes: Tag Teams ---

@app.route('/tag-teams')
@require_game_loaded
def tag_teams():
    """View tag teams."""
    all_teams = game.get_tag_teams()
    return render_template('tag_teams.html', teams=all_teams, game=game)


@app.route('/create-tag-team', methods=['GET', 'POST'])
@require_game_loaded
def create_tag_team():
    """Create a new tag team."""
    if request.method == 'POST':
        success, msg = game.create_tag_team(
            name=request.form.get('name', ''),
            member_a_id=int(request.form.get('member_a')),
            member_b_id=int(request.form.get('member_b'))
        )
        flash(msg, 'success' if success else 'error')
        if success:
            return redirect(url_for('tag_teams'))

    wrestlers = game.get_roster()
    return render_template('create_tag_team.html', wrestlers=wrestlers, game=game)


@app.route('/tag-team/<int:team_id>/disband', methods=['POST'])
@require_game_loaded
def disband_tag_team(team_id):
    """Disband a tag team."""
    success, msg = game.disband_tag_team(team_id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('tag_teams'))


# --- Routes: Records ---

@app.route('/records')
@require_game_loaded
def records():
    """View records and history."""
    match_history = game.get_match_history(limit=20)
    return render_template('records.html', match_history=match_history, game=game)


@app.route('/records/head-to-head', methods=['GET', 'POST'])
@require_game_loaded
def head_to_head():
    """Head-to-head records."""
    wrestlers = game.get_roster()
    h2h = None
    w1 = None
    w2 = None

    if request.method == 'POST':
        wrestler_a_id = int(request.form.get('wrestler_a'))
        wrestler_b_id = int(request.form.get('wrestler_b'))
        h2h = game.get_head_to_head(wrestler_a_id, wrestler_b_id)
        w1 = game.get_wrestler_by_id(wrestler_a_id)
        w2 = game.get_wrestler_by_id(wrestler_b_id)

    return render_template('head_to_head.html', wrestlers=wrestlers, h2h=h2h, w1=w1, w2=w2, game=game)


# --- Routes: Calendar ---

@app.route('/calendar')
@app.route('/calendar/<int:year>/<int:month>')
@require_game_loaded
def calendar_view(year=None, month=None):
    """Display calendar view for a month."""
    if year is None:
        year = game.state.year
    if month is None:
        month = game.state.month

    calendar_data = game.get_calendar_month(year, month)
    upcoming = game.get_upcoming_shows(10)
    brands = game.get_active_brands()

    # Calculate prev/next month
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    return render_template('calendar.html',
        calendar=calendar_data,
        upcoming_shows=upcoming,
        brands=brands,
        prev_year=prev_year,
        prev_month=prev_month,
        next_year=next_year,
        next_month=next_month,
        game=game
    )


# --- Routes: PPV Settings ---

@app.route('/ppv-settings')
@require_game_loaded
def ppv_settings():
    """View and edit PPV settings."""
    # Get direct list of PPVDefinition objects (not dicts) so attributes work in template
    ppv_calendar = game.state.calendar_manager.get_ppv_calendar()
    return render_template('ppv_settings.html', ppv_calendar=ppv_calendar, game=game)


@app.route('/ppv/add', methods=['POST'])
@require_game_loaded
def add_ppv_route():
    """Add a new PPV."""
    name = request.form.get('name')
    month = int(request.form.get('month'))
    week = int(request.form.get('week'))
    tier = request.form.get('tier')
    
    success, msg = game.add_ppv(name, month, week, tier)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('ppv_settings'))


@app.route('/ppv/<int:ppv_id>/update', methods=['POST'])
@require_game_loaded
def update_ppv_route(ppv_id):
    """Update a PPV name."""
    new_name = request.form.get('name', '')
    if game.state.calendar_manager.edit_ppv(ppv_id, name=new_name):
        game.save_game()
        flash('PPV updated.', 'success')
    else:
        flash('Could not update PPV.', 'error')
    return redirect(url_for('ppv_settings'))


@app.route('/ppv/<int:ppv_id>/delete', methods=['POST'])
@require_game_loaded
def delete_ppv_route(ppv_id):
    """Delete a PPV."""
    success, msg = game.remove_ppv(ppv_id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('ppv_settings'))


# --- Routes: Weekly Shows ---

@app.route('/weekly-shows')
@require_game_loaded
def weekly_shows():
    """List all weekly shows."""
    shows = game.get_weekly_shows()
    brands = game.get_active_brands()
    return render_template('weekly_shows.html', shows=shows, brands=brands, game=game)


@app.route('/create-weekly-show', methods=['GET', 'POST'])
@require_game_loaded
def create_weekly_show():
    """Create a new weekly show."""
    if request.method == 'POST':
        brand_id = request.form.get('brand_id')
        if brand_id:
            brand_id = int(brand_id)
        else:
            brand_id = None

        success, msg = game.create_weekly_show(
            name=request.form.get('name', ''),
            short_name=request.form.get('short_name', ''),
            day_of_week=int(request.form.get('day_of_week', 0)),
            tier=request.form.get('tier', 'major'),
            brand_id=brand_id,
            match_slots=int(request.form.get('match_slots', 5)),
            segment_slots=int(request.form.get('segment_slots', 3)),
            runtime_minutes=int(request.form.get('runtime', 120))
        )
        flash(msg, 'success' if success else 'error')
        if success:
            return redirect(url_for('weekly_shows'))

    brands = game.get_active_brands()
    return render_template('create_weekly_show.html', brands=brands, game=game)


@app.route('/weekly-show/<int:show_id>/cancel', methods=['POST'])
@require_game_loaded
def cancel_weekly_show(show_id):
    """Cancel a weekly show."""
    success, msg = game.deactivate_weekly_show(show_id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('weekly_shows'))


# --- Routes: Brands ---

@app.route('/brands')
@require_game_loaded
def brands():
    """Brand management page."""
    all_brands = game.get_brands()
    titles = game.get_titles()
    roster = game.get_roster()
    return render_template('brands.html', brands=all_brands, titles=titles, roster=roster, game=game)


@app.route('/create-brand', methods=['GET', 'POST'])
@require_game_loaded
def create_brand():
    """Create a new brand."""
    if request.method == 'POST':
        success, msg = game.create_brand(
            name=request.form.get('name', ''),
            short_name=request.form.get('short_name', ''),
            color=request.form.get('color', '#FF0000')
        )
        flash(msg, 'success' if success else 'error')
        if success:
            return redirect(url_for('brands'))

    return render_template('create_brand.html', game=game)


@app.route('/brand/<int:brand_id>/roster')
@require_game_loaded
def brand_roster(brand_id):
    """View wrestlers assigned to a brand."""
    brand = game.get_brand_by_id(brand_id)
    if not brand:
        flash('Brand not found.', 'error')
        return redirect(url_for('brands'))

    roster = game.get_brand_roster(brand_id)
    titles = game.get_brand_titles(brand_id)
    return render_template('brand_roster.html', brand=brand, roster=roster, titles=titles, game=game)


@app.route('/brand/<int:brand_id>/assign-wrestlers', methods=['GET', 'POST'])
@require_game_loaded
def assign_wrestlers(brand_id):
    """Assign wrestlers to a brand."""
    brand = game.get_brand_by_id(brand_id)
    if not brand:
        flash('Brand not found.', 'error')
        return redirect(url_for('brands'))

    if request.method == 'POST':
        wrestler_ids = request.form.getlist('wrestlers')
        for wid in wrestler_ids:
            game.assign_wrestler_to_brand(int(wid), brand_id)
        flash(f'Assigned {len(wrestler_ids)} wrestlers to {brand.name}.', 'success')
        return redirect(url_for('brand_roster', brand_id=brand_id))

    # Get unassigned wrestlers
    unassigned = game.get_unassigned_wrestlers()
    all_wrestlers = game.get_roster()
    return render_template('assign_wrestlers.html',
        brand=brand,
        unassigned=unassigned,
        all_wrestlers=all_wrestlers,
        game=game
    )


@app.route('/brand/<int:brand_id>/assign-titles', methods=['GET', 'POST'])
@require_game_loaded
def assign_titles(brand_id):
    """Assign titles to a brand."""
    brand = game.get_brand_by_id(brand_id)
    if not brand:
        flash('Brand not found.', 'error')
        return redirect(url_for('brands'))

    if request.method == 'POST':
        title_ids = request.form.getlist('titles')
        for tid in title_ids:
            game.assign_title_to_brand(int(tid), brand_id)
        flash(f'Assigned {len(title_ids)} titles to {brand.name}.', 'success')
        return redirect(url_for('brand_roster', brand_id=brand_id))

    # Get unassigned titles
    unassigned = game.get_unassigned_titles()
    all_titles = game.get_titles()
    return render_template('assign_titles.html',
        brand=brand,
        unassigned=unassigned,
        all_titles=all_titles,
        game=game
    )


@app.route('/brand/<int:brand_id>/remove-wrestler/<int:wrestler_id>', methods=['POST'])
@require_game_loaded
def remove_wrestler_from_brand(brand_id, wrestler_id):
    """Remove a wrestler from a brand (make free agent)."""
    success, msg = game.unassign_wrestler_from_brand(wrestler_id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('brand_roster', brand_id=brand_id))


@app.route('/brand/<int:brand_id>/remove-title/<int:title_id>', methods=['POST'])
@require_game_loaded
def remove_title_from_brand(brand_id, title_id):
    """Remove a title from a brand (make floating)."""
    success, msg = game.unassign_title_from_brand(title_id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('brand_roster', brand_id=brand_id))


# --- Run the app ---

if __name__ == '__main__':
    print("=" * 50)
    print("  Pro Wrestling Sim - Web UI")
    print("  Open http://127.0.0.1:5000 in your browser")
    print("=" * 50)
    app.run(debug=True, port=5000)

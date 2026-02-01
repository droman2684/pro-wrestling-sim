# Pro Wrestling Sim - UI Enhancement Roadmap

**Created:** January 18, 2026
**Status:** Planning Document
**Current UI:** CLI + Basic Tkinter Desktop

---

## Current UI State

### CLI (`src/ui/cli/cli_app.py`)
- Text-based menu navigation
- Functional but utilitarian
- Good for quick testing and development
- ~1450 lines

### Tkinter Desktop (`src/ui/desktop/tkinter_app.py`)
- Basic GUI with buttons and dialogs
- Functional but visually plain
- Default system styling
- ~1145 lines

---

## UI Enhancement Phases

### Phase UI-1: Tkinter Visual Polish (LOW EFFORT)

**Goal:** Make the existing Tkinter app more visually appealing without major restructuring.

#### Tasks
| Task | Description | Priority |
|------|-------------|----------|
| Custom Theme | Apply ttkbootstrap or custom ttk theme | High |
| Color Scheme | Wrestling-themed colors (black/gold/red) | High |
| Font Improvements | Better typography hierarchy | Medium |
| Icon Integration | Add icons to buttons and menus | Medium |
| Wrestler Cards | Visual cards instead of plain text lists | Medium |
| Status Indicators | Color-coded heat/morale/stamina bars | Medium |
| Logo/Branding | Add app logo to header | Low |

#### Libraries to Consider
- `ttkbootstrap` - Modern Bootstrap-style themes for ttk
- `customtkinter` - Modern UI widgets for Tkinter
- `Pillow` - Image handling for wrestler photos/logos

#### Estimated Effort: 1-2 sessions

---

### Phase UI-2: Dashboard & Overview Screens (MEDIUM EFFORT)

**Goal:** Add information-dense overview screens for at-a-glance status.

#### New Screens

**Main Dashboard**
```
+------------------------------------------+
|  FEDERATION NAME         Week 3, Month 2 |
|  Bank: $50,000           Next PPV: 2 wks |
+------------------------------------------+
|  TOP 5 SINGLES  |  TOP 5 TAG TEAMS       |
|  1. Bret Hart   |  1. High Flyers        |
|  2. HBK         |  2. The Monsters       |
|  ...            |  ...                   |
+------------------------------------------+
|  ACTIVE FEUDS (2)  |  ACTIVE STABLES (1) |
|  Hart vs HBK       |  Hart Foundation    |
|  Diesel vs Razor   |                     |
+------------------------------------------+
|  TITLE HOLDERS                           |
|  World: Bret Hart  |  Tag: High Flyers   |
|  IC: Razor Ramon   |                     |
+------------------------------------------+
```

**Wrestler Profile Screen**
```
+------------------------------------------+
|  [PHOTO]  BRET HART                      |
|           "The Excellence of Execution"  |
|           Face | Age 38 | Calgary, AB    |
+------------------------------------------+
|  RING STATS        |  ENTERTAINMENT      |
|  Brawl: 75   ████  |  Mic: 70      ████  |
|  Tech: 95    █████ |  Charisma: 80 ████  |
|  Air: 60     ███   |  Look: 85     ████  |
|  Psych: 98   █████ |  Star: 95     █████ |
+------------------------------------------+
|  STATUS                                  |
|  Heat: 85 ████████░░  Morale: 90 ████████|
|  Stamina: 75 ███████░░░                  |
+------------------------------------------+
|  Record: 15W - 3L  |  Current Title: World|
|  Stable: Hart Foundation (LEADER)        |
|  Feud: vs Shawn Michaels (INTENSE)       |
+------------------------------------------+
```

**Stable Overview Screen**
```
+------------------------------------------+
|  HART FOUNDATION                         |
|  Power Rating: 82  |  Status: Active     |
+------------------------------------------+
|  LEADER: Bret Hart [92]                  |
|  MEMBERS:                                |
|    - Owen Hart [78]                      |
|    - British Bulldog [75]                |
|    - Jim Neidhart [70]                   |
+------------------------------------------+
|  RECENT RESULTS                          |
|  Bret def. HBK (interference helped)     |
|  Owen lost to Razor (heat -1 to stable)  |
+------------------------------------------+
```

#### Estimated Effort: 2-3 sessions

---

### Phase UI-3: Match Presentation Overhaul (MEDIUM EFFORT)

**Goal:** Make match results more visually engaging and dramatic.

#### Improvements

**Pre-Match Card**
```
+------------------------------------------+
|           SINGLES MATCH                  |
|      [WORLD CHAMPIONSHIP]                |
+------------------------------------------+
|                                          |
|   BRET HART        vs      SHAWN MICHAELS|
|   "Hitman"                 "Heartbreak"  |
|   [92]                           [90]    |
|                                          |
|   Hart Foundation          (No Stable)   |
|                                          |
|   >>> FEUD MATCH - INTENSE <<<           |
|   Score: 2-1 (Bret leads)                |
+------------------------------------------+
```

**Match Result Presentation**
```
+==========================================+
|              MATCH RESULT                |
+==========================================+
|                                          |
|   BRET HART  defeats  SHAWN MICHAELS     |
|                                          |
|   Match Rating: 94/100  ★★★★★            |
|                                          |
+------------------------------------------+
|   >>> INTERFERENCE! <<<                  |
|   Hart Foundation distracted HBK!        |
+------------------------------------------+
|   HIGHLIGHTS:                            |
|   - WHAT A COUNTER! Bret turns the tide! |
|   - This rivalry is getting personal!    |
|   - NEAR FALL after devastating DDT!     |
+------------------------------------------+
|   CONSEQUENCES:                          |
|   - Bret Heat: 85 -> 94 (+9)             |
|   - Stablemates: Owen +2, Bulldog +2     |
|   - Feud continues (1 match remaining)   |
+------------------------------------------+
```

**Show Summary**
```
+==========================================+
|     MONDAY NITRO - SHOW COMPLETE         |
|     Final Rating: 78/100                 |
+==========================================+
|                                          |
|   MATCH RESULTS                          |
|   1. Owen Hart def. Razor Ramon   [72]   |
|   2. Diesel def. Lex Luger        [68]   |
|   3. Bret Hart def. HBK (TITLE)   [94]   |
|                                          |
|   PROFIT: +$12,500                       |
|   Bank Balance: $62,500                  |
|                                          |
+==========================================+
```

#### Estimated Effort: 2 sessions

---

### Phase UI-4: Booking Flow Improvements (MEDIUM EFFORT)

**Goal:** Make the show booking process more intuitive and visual.

#### Improvements

**Drag-and-Drop Match Card Builder**
- Visual card layout
- Drag wrestlers into match slots
- Auto-detect feuds and suggest matchups
- Show warnings (low stamina, already booked, etc.)

**Smart Suggestions**
- "Feud match available: Bret vs HBK"
- "Title defense due: Razor hasn't defended IC in 3 weeks"
- "Hot streak: Diesel is 5-0, consider push"

**Match Order Optimization**
- Suggest opener (high energy, mid-card)
- Suggest main event (highest combined heat)
- Warn if main event is weak

**Pre-Show Preview**
```
+------------------------------------------+
|  SHOW PREVIEW: MONDAY NITRO              |
+------------------------------------------+
|  Expected Rating: 75-85                  |
|  Projected Profit: $10,000 - $15,000     |
|                                          |
|  CARD ANALYSIS:                          |
|  [!] No title matches booked             |
|  [+] Feud match will boost rating        |
|  [+] Good variety (2 singles, 1 tag)     |
|  [-] Main event heat is low              |
+------------------------------------------+
```

#### Estimated Effort: 3-4 sessions

---

### Phase UI-5: Web UI (HIGH EFFORT)

**Goal:** Create a modern web-based interface as an alternative to Tkinter.

#### Technology Options

**Option A: Flask + Jinja2 (Server-side rendering)**
- Pros: Simple, Python-only, easy to integrate
- Cons: Less interactive, page refreshes
- Effort: Medium

**Option B: Flask + HTMX (Enhanced server-side)**
- Pros: Interactive without full JS framework, stays Python-focused
- Cons: Learning curve for HTMX patterns
- Effort: Medium

**Option C: FastAPI + React/Vue (Full SPA)**
- Pros: Modern, highly interactive, best UX
- Cons: Requires JS knowledge, more complex
- Effort: High

**Recommended:** Option B (Flask + HTMX) - Good balance of interactivity and simplicity.

#### Web UI Structure
```
src/
  ui/
    web/
      app.py              # Flask application
      templates/
        base.html         # Base template with nav
        dashboard.html    # Main dashboard
        roster.html       # Roster management
        booking.html      # Show booking
        results.html      # Show results
        stables.html      # Stable management
        feuds.html        # Feud management
      static/
        css/
          style.css       # Custom styles
        js/
          app.js          # Minimal JS (HTMX handles most)
        images/
          logo.png
```

#### Estimated Effort: 5-8 sessions

---

### Phase UI-6: Data Visualization (MEDIUM EFFORT)

**Goal:** Add charts and graphs for trends and statistics.

#### Visualizations to Add

**Wrestler Trends**
- Heat over time (line chart)
- Win rate by month (bar chart)
- Rating average trend

**Federation Overview**
- Revenue over time
- Average show rating trend
- Title reign timeline

**Rankings History**
- Position changes over time
- Head-to-head records matrix

**Stable/Feud Analytics**
- Interference success rate
- Feud intensity vs match ratings

#### Libraries
- `matplotlib` - Static charts (export as images)
- `plotly` - Interactive charts (for web UI)
- `Chart.js` - Web-based charts (if using web UI)

#### Estimated Effort: 2-3 sessions

---

## Implementation Priority Matrix

| Phase | Impact | Effort | Priority |
|-------|--------|--------|----------|
| UI-1: Visual Polish | Medium | Low | **HIGH** |
| UI-2: Dashboards | High | Medium | **HIGH** |
| UI-3: Match Presentation | Medium | Medium | MEDIUM |
| UI-4: Booking Flow | High | Medium | MEDIUM |
| UI-5: Web UI | High | High | LOW (future) |
| UI-6: Data Viz | Medium | Medium | LOW |

---

## Recommended Order

1. **UI-1: Visual Polish** - Quick wins, immediate improvement
2. **UI-2: Dashboards** - Major UX improvement
3. **UI-3: Match Presentation** - Makes core gameplay more engaging
4. **UI-4: Booking Flow** - Quality of life improvements
5. **UI-6: Data Viz** - Nice to have, adds depth
6. **UI-5: Web UI** - Major undertaking, do last if desired

---

## Design Guidelines

### Color Palette (Wrestling Theme)
```
Primary:    #1a1a2e (Dark Navy)
Secondary:  #c9a227 (Championship Gold)
Accent:     #e63946 (Ring Red)
Success:    #2a9d8f (Face Green)
Danger:     #e76f51 (Heel Orange)
Background: #0f0f1a (Near Black)
Text:       #f1faee (Off White)
```

### Typography
- Headers: Bold, uppercase for titles
- Body: Clean sans-serif (Segoe UI, Arial)
- Stats: Monospace for numbers (alignment)

### UX Principles
1. **Scannable** - Key info visible at a glance
2. **Contextual** - Show relevant actions based on current screen
3. **Feedback** - Clear confirmation of actions
4. **Consistency** - Same patterns across all screens
5. **Wrestling Feel** - Dramatic presentation for results

---

## Notes for Implementation

### Tkinter Modernization Tips
```python
# Using ttkbootstrap for modern look
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

root = ttk.Window(themename="darkly")  # Dark theme
```

### Progress Bars for Stats
```python
# Visual stat bars
def create_stat_bar(parent, label, value, max_val=100):
    frame = ttk.Frame(parent)
    ttk.Label(frame, text=f"{label}:").pack(side="left")
    progress = ttk.Progressbar(frame, value=value, maximum=max_val, length=100)
    progress.pack(side="left", padx=5)
    ttk.Label(frame, text=str(value)).pack(side="left")
    return frame
```

### Color-Coded Heat Indicator
```python
def get_heat_color(heat):
    if heat >= 80: return "#e63946"  # Hot red
    if heat >= 60: return "#f4a261"  # Warm orange
    if heat >= 40: return "#e9c46a"  # Neutral yellow
    if heat >= 20: return "#2a9d8f"  # Cool teal
    return "#264653"  # Cold blue
```

---

## Dependencies to Add

### For UI-1 (Visual Polish)
```
ttkbootstrap>=1.10.0
Pillow>=10.0.0
```

### For UI-5 (Web UI)
```
Flask>=3.0.0
htmx (CDN, no pip install)
```

### For UI-6 (Data Viz)
```
matplotlib>=3.8.0
# or for web
plotly>=5.18.0
```

---

## Session Estimates

| Phase | Sessions | Cumulative |
|-------|----------|------------|
| UI-1 | 1-2 | 1-2 |
| UI-2 | 2-3 | 3-5 |
| UI-3 | 2 | 5-7 |
| UI-4 | 3-4 | 8-11 |
| UI-6 | 2-3 | 10-14 |
| UI-5 | 5-8 | 15-22 |

**Total for full UI overhaul:** ~15-22 sessions

**Recommended MVP UI upgrade (UI-1 + UI-2):** ~3-5 sessions

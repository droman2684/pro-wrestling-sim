# Web UI Improvement TODO

**Created:** January 22, 2026
**Status:** Functional but needs visual polish

---

## Current State

The Flask web UI is **fully functional** - all game features work:
- New/Load game
- Dashboard with rankings, titles, feuds, stables
- Roster management with wrestler profiles
- All match type booking (singles, tag, triple threat, fatal 4-way, ladder, iron man, chamber, MITB, rumble)
- AI-assisted booking
- Show results display
- Title/Feud/Stable/Tag Team management
- Records & history

**Problem:** The UI looks generic/ugly. Uses default Bootstrap 5 dark theme which feels bland.

---

## Files to Modify

| File | Purpose |
|------|---------|
| `src/ui/web/templates/base.html` | Main layout, navbar, global styles |
| `src/ui/web/templates/*.html` | Individual page templates |

All styling is currently inline in `base.html` `<style>` block (lines ~10-180).

---

## UI Improvement Options

### Option A: Polish Current Bootstrap Theme
- Better color usage (more gold accents, dramatic reds)
- Improved typography hierarchy
- Better card designs with gradients/shadows
- More spacing and visual breathing room
- Wrestling-themed icons/decorations

### Option B: Switch to Different Framework
- **Tailwind CSS** - More utility-first, easier custom styling
- **DaisyUI** - Tailwind components with themes
- **Custom CSS** - Full control, wrestling-specific design

### Option C: Completely Different Aesthetic
- **Retro wrestling poster style** - Bold colors, vintage feel
- **Modern sports broadcast** - Clean, ESPN-like
- **Dark dramatic** - Like WWE Network UI

---

## Specific Issues to Fix

1. **Cards look flat** - Need better borders, shadows, hover effects
2. **Text hierarchy weak** - Headers don't stand out enough
3. **Color usage inconsistent** - Gold accent underused
4. **Match cards boring** - Should look more like wrestling match graphics
5. **Forms are plain** - Input fields need better styling
6. **Navbar generic** - Needs wrestling branding feel
7. **Dashboard cramped** - Needs better layout/spacing
8. **Wrestler profiles** - Stat bars could be more visual

---

## Design Reference

Current color palette (defined in base.html):
```css
--gold: #c9a227;
--ring-red: #e63946;
--face-green: #2a9d8f;
--heel-orange: #e76f51;
--bs-body-bg: #0f0f1a;
--bs-body-color: #f1faee;
```

---

## How to Run

```bash
cd D:\simple_sim_sports\pro-wrestling\src\ui\web
python app.py
```
Open http://127.0.0.1:5000

---

## Next Session

1. Ask user which direction they want (A, B, or C above)
2. Get specific feedback on what they dislike most
3. Implement improvements iteratively
4. Consider adding wrestler images/avatars for visual interest

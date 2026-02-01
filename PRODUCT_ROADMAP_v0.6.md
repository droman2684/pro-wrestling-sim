# Pro Wrestling Sim: Product Roadmap v0.6
**Author:** Head of Product
**Objective:** Transform the simulation from a booking tool into a strategic management game.

---

## 1. Dynamic Fatigue & Injury System (The Stakes)
**Why first?** This adds the primary "Resource Management" challenge. Currently, booking has no long-term cost.
*   **The Mechanic:** 
    *   Every match type has a "Stamina Drain" value (e.g., Cage matches drain more than Squash matches).
    *   Condition < 50% = Reduced Match Rating performance.
    *   Condition < 25% = High Injury Risk (determined by the wrestler's *Durability* stat).
*   **Impact:** Forces players to rotate their roster and build new stars instead of overusing one champion.

## 2. TV Ratings & Attendance (The Scoreboard)
**Why second?** Now that booking has a cost (Fatigue), players need a "Reward" for taking risks.
*   **The Mechanic:** 
    *   Match Ratings are converted into a TV Rating (e.g., 1.5 to 5.0).
    *   Cumulative show quality determines "Viewer Growth" or "Viewer Loss."
    *   Attendance generates revenue based on the show's "Heat."
*   **Impact:** Provides a clear metric for success and progression.

## 3. "Wrestling Observer" Match Logs (The Narrative)
**Why third?** Now that we have ratings, players will want to know *why* a match succeeded or failed.
*   **The Mechanic:** 
    *   A procedural text generator that looks at wrestler stats.
    *   *High Flyer* vs *Technician* log: "Wrestler A hits a 450 splash but Wrestler B rolls away and applies a Fujiwara Armbar!"
    *   *Heel* vs *Face* log: "The ref was down! Wrestler A used a chair!"
*   **Impact:** Greatly increases player engagement and makes the "27 attributes" feel meaningful.

## 4. Backstage News & Rumor Feed (The Living World)
**Why fourth?** This connects the Fatigue, Ratings, and Roster status into a cohesive story.
*   **The Mechanic:** 
    *   A ticker on the dashboard that reacts to game events.
    *   "Wrestler X is frustrated with their mid-card status." (Morale trigger).
    *   "Last night's main event is being hailed as a 5-star classic!" (Ratings reaction).
    *   "Medical Update: Wrestler Y expected to be out 4 months with a torn ACL."
*   **Impact:** Makes the world feel alive and independent of the player's immediate actions.

## 5. Visual "Card Canvas" Booking (The UX Overhaul)
**Why last?** This is a high-effort UI change. It should be built once the features above are stable.
*   **The UI:** 
    *   Replace dropdown menus with a drag-and-drop or grid-based "Storyboard."
    *   Display wrestler "Portraits" (or colored cards with initials/stats).
    *   Visual indicators for Face/Heel balance on the card.
*   **Impact:** Dramatically speeds up the booking process and makes the game feel like a modern "Desktop App."

---

### Sprint Prioritization
| Feature | Difficulty | Impact | Priority |
| :--- | :--- | :--- | :--- |
| **Fatigue/Injury** | Medium | High | **Critical** |
| **Ratings/Score** | Low | High | **High** |
| **Match Logs** | High | High | **Medium** |
| **News Feed** | Medium | Medium | **Low** |
| **Card Canvas** | High | Medium | **Future** |

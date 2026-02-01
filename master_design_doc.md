# Project: Simple Sim Sports - Pro Wrestling
**Version:** 1.0 (Master Design Document)
**Target Platform:** PC (Text-Based/Console)
**Core Concept:** A deep, "living world" Pro Wrestling management simulator focusing on strategy, narrative control, and financial survival.

---

## PART 1: GAME ARCHITECTURE

### 1. Technical Stack
* **Language:** Python 3.10+ (Selected for logic depth and library support).
* **Data Format:** JSON (Human-readable, fully moddable).
* **UI Paradigm:** Text-Based / Menu Driven (Console or Simple GUI).
* **Save System:** JSON serialization of the Game State object.

### 2. Core Philosophy
* **Role:** The player is the **Promoter/Booker**.
* **The "Fog of War":** In Career Mode, exact stat numbers may be hidden (e.g., "Brawling: A+" instead of "95") to simulate scouting uncertainty. In Sandbox Mode, all data is visible.
* **The "Living" Database:** Talent is not static; they age, get injured, and develop based on usage.

---

## PART 2: FEATURE SPECIFICATIONS

### Pillar I: The Talent Model (The DNA)
*Workers are defined by "Fluid Stats," not rigid classes.*

#### 1. Data Structure (`Wrestler.json`)
* **Bio:** `ID`, `Name`, `GimmickName`, `Age`, `Height`, `Weight`, `Nationality`, `HomeRegion`.
* **In-Ring Ability (0-100):**
    * `Brawl`: Striking and hardcore affinity.
    * `Tech`: Submissions and chain wrestling.
    * `Air`: Agility and top-rope capability.
    * `Psychology`: The ability to structure a match (Critical for Main Events).
    * `Stamina`: Durability in long matches.
* **Entertainment (0-100):**
    * `Mic`: Speaking ability.
    * `Charisma`: Natural crowd connection.
    * `Look`: Physical intimidation or appeal.
    * `StarQuality`: Rare multiplier for draw power.
* **Status (Dynamic):**
    * `Morale`: (0-100) Affects contract negotiations and "No Show" chance.
    * `Condition`: (0-100) Physical health. <50 significantly increases Injury Risk.
    * `Heat`: (0-100) Momentum.
    * `Alignment`: Face (Good) / Heel (Bad) / Tweener (Neutral).

#### 2. The Gimmick System
* **Mechanic:** Each worker has a `Gimmick` object (e.g., "Patriot", "Monster", "Comedy").
* **Logic:** The Gimmick has a `Risk` and `Reward` factor.
    * *Example:* A "Monster" gimmick requires High Size/Power. If assigned to a Cruiserweight, it applies a penalty to `Charisma`.

---

### Pillar II: The Booking Engine (The Loop)

#### 1. The Card Screen
* **Segments:** Players build a show by adding `Matches` or `Angles` (Interviews/Skits).
* **Brand Split:** The player can subdivide their roster into Brands (e.g., Brand A, Brand B).
    * *Constraint:* Workers assigned to Brand A cannot appear on Brand B shows without a morale penalty.

#### 2. Match Configuration
For every match, the player controls:
* **Participants:** 1v1, Tag, Multi-man.
* **Stipulation:** Standard, Cage, Ladder, Hardcore, Submission.
* **Time Limit:** 10m, 20m, 60m, No Limit.
* **Winner Determination:**
    * *Option A (Booker):* Player selects the winner.
    * *Option B (Sim):* Engine decides based on Stats + RNG (Upset chance).
* **Finish Type:** Clean Pin, Dirty Pin, DQ, Countout.
* **Call Level:**
    * *Safe:* Low Injury Risk, cap on Match Rating.
    * *All Out:* High Injury Risk, bonus to Match Rating.

#### 3. Feuds & Storylines
* **Manual Tracking:** Player creates a Storyline Container (e.g., "World Title Feud") and adds workers.
* **Heat Meter:** (0-100). Matches between feuding workers receive a `StoryBonus` to the final rating.

---

### Pillar III: The Simulation Engine (The Math)

#### 1. Match Rating Algorithm
The formula to determine the "Star Rating" (0-5 Stars).
> `BaseRating` = (WorkerA_AvgStats + WorkerB_AvgStats) / 2
> `StyleClash` = Lookup Table (e.g., Giant vs. Cruiserweight = Penalty, unless `Psychology` > 80).
> `CrowdMod` = Regional Preferences (see below).
> `RNG` = Random Variance (0.9 to 1.1).
> **FinalScore** = `BaseRating` * `StyleClash` * `CrowdMod` * `RNG`

#### 2. Regional Crowds
The world is divided into regions with specific tastes:
* **Tri-State:** Bonus to `Brawl` and `Tech`. Hates `Comedy`.
* **Deep South:** Bonus to `Psychology` and `Storylines`.
* **West Coast:** Bonus to `Aerial` and `Workrate`.
* **National:** Bonus to `Look` and `StarQuality`.

---

### Pillar IV: The Living World (Economy)

#### 1. Financials
* **Revenue:** Ticket Sales (Venue Size * Ticket Price * Hype), Merchandise, Sponsorships.
* **Expenses:** Worker Contracts (Per Appearance or Salary), Venue Rental, Production Costs.
* **Game Over:** Bankruptcy (Cash < 0 for 3 consecutive months).

#### 2. Media
* **TV Model:** Contracts are per-Brand.
* **Streaming:** Unified platform for PPVs. Requires monthly upkeep cost but yields higher upside.

---

## PART 3: DEVELOPMENT ROADMAP (Agile)

### Epic 1: The Foundation (Data & Core)
* **1.1:** Build `Wrestler` class and JSON loader.
* **1.2:** Build `Match` engine (The math logic).
* **1.3:** Create a script to simulate 100 matches and verify stat balance.

### Epic 2: The Booker's Interface
* **2.1:** Build the CLI (Command Line Interface) Main Menu.
* **2.2:** Build the `BookingScreen` (Add Match, Select Winner).
* **2.3:** Implement the `ShowReport` (End of show summary).

### Epic 3: The Living World
* **3.1:** Implement `Brand` logic and Roster Split.
* **3.2:** Implement `CompanyFinances` (Revenue/Expense tracking).
* **3.3:** Implement `Injury` and `Morale` systems.

### Epic 4: Polish & Modes
* **4.1:** Add **Sandbox Mode** (God Mode toggle).
* **4.2:** Add Save/Load functionality.
* **4.3:** Add "Pre-Game Editor" (Create a wrestler).
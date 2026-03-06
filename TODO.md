# 🦇 Dracula Survival App - Implementation Specifications

## Role and Objective
You are Claude, an expert AI software engineer. Your task is to implement the "Dracula Survival App" (ドラキュラ生存アプリ) perfectly according to this specification. Ensure the code is flawless, beautiful, and immediately usable.

## App Concept
A gamified life-logging web app targeting people who hate the sun (or have severe sun allergies). The user roleplays as a "Sugar Glider Dracula" (モモンガドラキュラ) who must track their sun exposure, equip protective UV gear, avoid garlic, and earn ranks by staying safely in the shadows.

---

## Core Features to Implement

### 1. UV Index & Geo-location Engine
- **Location Tracking**: Secure the user's current location (latitude/longitude) via browser Geolocation API.
- **Weather API**: Fetch the real-time UV Index using OpenWeatherMap API (or build a robust mock system if the API key is not immediately available).
- **Dracula Danger Level Calculation**:
  `Danger Level = (UV Index * Elevation Correction) * Reflectance Factor`
- **Dramatic Alerts**: Based on the Danger Level, display urgent messages such as:
  - "You have X minutes until you turn to ash!"
  - "Lethal sunlight detected! Evacuate to a coffin (indoors) immediately!"

### 2. Main Dashboard UI
The main screen must be a visually stunning summary of the user's vampiric stats:
- **Today's UV Index**: e.g., "Level 8 (Extremely High)"
- **Time outside**: e.g., "0 minutes"
- **Current Rank & Stamps**: Display title and current Dracula Stamp (🦇) count.
- **Daily Survival Reward**: A dynamic message component. Example: *"Congratulations! You completely avoided the harsh desert-like sunlight today. Awarding 1 Dracula Stamp. 🦇"*

### 3. Equipment & Status System
Users can equip items in specific character slots. Active items reduce UV damage and grant bonus stamps:
- **100% Light-blocking Parasol** | `Slot: Both Hands` | *[Absolute Defense] 100% UV Cut. Nullifies ash timer.* (+2.0 Stamps)
- **Wide-brimmed Hat** | `Slot: Head` | *[Sight Protection] Prevents direct face damage.* (+1.0 Stamp)
- **UV Cut Long Sleeves** | `Slot: Body` | *[Full Body Protection] Prevents arms from turning to ash.* (+1.0 Stamp)
- **Sunglasses** | `Slot: Eyes` | *[Evil Eye Protection] Reduces glare damage.* (+0.5 Stamps)
*(Implement an inventory/equipment UI where the user can toggle these items and see their stats update in real-time.)*

### 4. The "Garlic Confession" Penalty System
- **The Button**: Add a dramatic, ominous button labeled "I accidentally ate garlic..." (懺悔ボタン).
- **Penalty Effects**:
  - The screen flashes deep CRITICAL RED.
  - Play a visual/audio cue representing an agonizing scream ("Uwaaaaaah!").
  - Trigger a CSS animation where 5 Dracula Stamps graphically shatter and scatter away from the total score.
- **Salvation (Tomato Juice)**: Provide a way to undo this penalty. E.g., pressing a "Drink Tomato Juice (Holy Blood)" button/taking a photo, which acts as an antidote and restores the lost points.

### 5. Rank & Title Progression
A localized leveling system based on the user's total Dracula Stamps:
- **0 - 9 pts**: `Just a Sugar Glider` (ただのフクロモモンガ) - Cannot speak human language. Instantly vanishes in sunlight.
- **10 - 24 pts**: `Baby Dracula` (赤ちゃんドラキュラ) - Fangs just starting to grow. Needs "sunscreen" milk.
- **25 - 39 pts**: `Dark Knight` (闇の騎士) - Mid-tier. Accustomed to wielding the physical shield (Parasol).
- **40 - 49 pts**: `Vampire Aristocrat` (吸血貴族/エリート) - Avoids garlic traps and sips tomato juice with elegance.
- **50 - 99 pts**: `Dracula King` (ドラキュラ王 🫅) - Ruler of the night. No longer needs to leave the house.
- **100+ pts**: `Ancient / True Ancestor` (真祖) - Historical legend. The sun actively avoids them.

---

## Technical & Design Requirements
1. **Aesthetics**: The design MUST be premium and heavily themed. Use dark mode by default: deep blacks, dark crimsons, gothic-inspired fonts, and glassmorphism. It should not look like a generic dashboard.
2. **Interactivity**: The UI should feel alive. Hover effects on equipment, smooth transitions for rank-ups, and dramatic micro-animations for the garlic button are absolutely required.
3. **Execution**: Write flawless, production-ready code. Ensure all state management (points, items, logs) functions seamlessly so the user can immediately test the logic.
4. **Educational Sourcing (Anti-Copy-Paste Policy)**: The user is studying programming and wants to deeply understand the code. For any significant implementation (e.g., Geolocation API, API fetching, complex CSS Animations, state management), you MUST include a comment block above the code referencing the official English technical documentation (e.g., MDN, official framework docs). Provide the URL and a 1-line quote from the official docs that justifies your code. This is a strict requirement for a stoic learning experience.

**Claude, please read this entirely and implement the complete application!**

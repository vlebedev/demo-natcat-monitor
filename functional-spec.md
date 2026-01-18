# Feature Specification: NatCat Event Monitor Dashboard

**Feature ID:** 001-natcat-dashboard
**Status:** Draft
**Created:** 2024-12-17

---

## Overview

### Problem Statement
After a natural catastrophe event, reinsurance professionals need to quickly understand their portfolio exposure. Currently, this requires manually cross-referencing event data with treaty information across multiple systems.

### Solution
A real-time dashboard that automatically fetches earthquake events from USGS, overlays them with treaty exposure zones, and highlights potential losses — giving underwriters and cat managers an instant view of "are we exposed?"

### Target Users
- NatCat Analysts
- Treaty Underwriters
- Cat Management / Accumulation Control

---

## User Stories

### US-1: View Recent Earthquake Events
**As a** NatCat analyst
**I want to** see recent significant earthquakes on a map
**So that** I can quickly identify events that may affect our portfolio

**Acceptance Criteria:**
- [ ] Display earthquakes from last 7 days with magnitude ≥ 4.0
- [ ] Show events as markers on an interactive map
- [ ] Marker size/color indicates magnitude
- [ ] Click marker to see event details (location, magnitude, depth, time)

---

### US-2: View Treaty Exposure Zones
**As a** treaty underwriter
**I want to** see our treaty coverage zones overlaid on the map  
**So that** I can understand our geographic exposure

**Acceptance Criteria:**
- [ ] Display predefined treaty zones as colored polygons/circles on map
- [ ] Each zone shows treaty name on hover
- [ ] Zones are visually distinct from event markers
- [ ] Can toggle zone visibility on/off

---

### US-3: Identify Exposed Treaties
**As a** NatCat manager  
**I want to** see which treaties are potentially affected by an event  
**So that** I can prioritize loss assessment

**Acceptance Criteria:**
- [ ] When an earthquake falls within a treaty zone, highlight both
- [ ] Show "Exposure Alert" panel listing affected treaties
- [ ] Display estimated exposure amount per affected treaty
- [ ] Sort alerts by exposure amount (highest first)

---

### US-4: View Event Summary Statistics
**As a** NatCat analyst  
**I want to** see summary statistics of recent events  
**So that** I can report on activity levels

**Acceptance Criteria:**
- [ ] Show total event count for selected period
- [ ] Show count of events by magnitude band (4-5, 5-6, 6+)
- [ ] Show count of events affecting our treaties
- [ ] Display total exposed treaty limit

---

## Functional Requirements

### FR-1: Event Data Integration
- **Source:** USGS Earthquake API (https://earthquake.usgs.gov/fdsnws/event/1/)
- **Refresh:** On page load + manual refresh button
- **Filter:** Magnitude ≥ 4.0, last 7 days
- **Fields Required:** id, magnitude, location (lat/lon), place name, time, depth

### FR-2: Mock Treaty Data
The system shall include mock treaty data representing realistic NatCat exposures:

| Treaty ID | Name                | Peril | Region | Zone Center        | Radius (km) | Limit (USD) |
|-----------|---------------------|-------|--------|--------------------|-------------|-------------|
| T001      | California Quake XL | EQ    | US-CA  | 36.7783, -119.4179 | 400         | 50,000,000  |
| T002      | Japan Quake QS      | EQ    | JP     | 35.6762, 139.6503  | 500         | 75,000,000  |
| T003      | Chile Quake XL      | EQ    | CL     | -33.4489, -70.6693 | 300         | 30,000,000  |
| T004      | Pacific Ring Cat    | EQ    | APAC   | 0, 150             | 3000        | 100,000,000 |
| T005      | Turkey Quake Fac    | EQ    | TR     | 39.9334, 32.8597   | 400         | 25,000,000  |

### FR-3: Exposure Calculation
- An event "affects" a treaty if the event epicenter is within the treaty's zone radius
- Exposure = Treaty Limit (simplified; real world would apply layers, retention, etc.)
- Multiple treaties can be affected by single event

### FR-4: Map Visualization
- World map centered on Pacific (to show Ring of Fire)
- Zoom and pan controls
- Event markers: circles sized by magnitude, colored by recency
- Treaty zones: semi-transparent colored circles
- Affected zones: highlighted border/fill when event inside

### FR-5: Alert Panel
- Fixed panel (sidebar or bottom) showing exposure alerts
- Updates automatically when events loaded
- Shows: Event name, Affected treaty, Exposure amount
- Link to click and center map on event

---

## Non-Functional Requirements

### Performance
- Initial page load: < 3 seconds
- Event data fetch: < 2 seconds
- Map interactions: 60fps

### Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Desktop viewport (responsive not required for demo)

### Accessibility
- Not prioritized for demo (time constraint)

---

## Out of Scope (v1 Demo)

- [ ] User authentication
- [ ] Historical event analysis
- [ ] Loss estimation models (e.g., RMS, AIR integration)
- [ ] Multiple peril types (flood, wind) — earthquake only
- [ ] Real treaty data / database
- [ ] Email/Slack notifications
- [ ] PDF report generation
- [ ] Mobile responsiveness

---

## Success Criteria

The demo is successful if:
1. ✅ Real earthquake data appears on the map within 5 seconds of load
2. ✅ Treaty zones are visible and distinguishable
3. ✅ At least one "exposure alert" is triggered (may need to adjust mock zone locations)
4. ✅ Clicking an event shows its details
5. ✅ The audience understands the concept without explanation

---

## Mockup / Wireframe

```
┌─────────────────────────────────────────────────────────────────┐
│  🌍 NatCat Event Monitor                    [Refresh] [7 days ▼]│
├─────────────────────────────────────┬───────────────────────────┤
│                                     │ 📊 Summary                │
│                                     │ ───────────────────────── │
│         [Interactive Map]           │ Events: 47                │
│                                     │ M4-5: 38  M5-6: 7  M6+: 2 │
│      ● Event marker                 │ Treaties at risk: 3       │
│      ◯ Treaty zone                  │ Total exposure: $155M     │
│                                     │                           │
│                                     ├───────────────────────────┤
│                                     │ ⚠️ Exposure Alerts         │
│                                     │ ───────────────────────── │
│                                     │ 🔴 M6.2 Japan Sea         │
│                                     │    → Japan Quake QS       │
│                                     │    Exposure: $75M         │
│                                     │                           │
│                                     │ 🟡 M5.1 Central CA        │
│                                     │    → California Quake XL  │
│                                     │    Exposure: $50M         │
│                                     │                           │
├─────────────────────────────────────┴───────────────────────────┤
│ Last updated: 2024-12-17 14:32 UTC    Data: USGS Earthquake API │
└─────────────────────────────────────────────────────────────────┘
```

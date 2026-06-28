# Logo Click → Home Navigation

**Date:** 2026-06-28
**Status:** Approved for Implementation

---

## Problem

Users need a consistent, intuitive way to return to the home screen from anywhere in the app (programs, trainings, WOD mode, timer). Currently, back navigation is scattered: some views have back buttons, some don't, and there's no single "home" exit point.

---

## Solution

Make the Woddy logo in the header clickable from all app views. Clicking the logo returns the user to the onboarding/home screen.

---

## Design Details

### Visual Changes

**Logo element:** The header already contains the Woddy logo (`#app-header .logo`). No new HTML element needed.

**Interactivity:**
- Add `cursor: pointer` CSS to the logo to signal clickability
- Add subtle hover effect (opacity or scale) for visual feedback
- Logo remains visible in the header across all app views

### Navigation Behavior

**Trigger:** User clicks the Woddy logo in the header

**Flow:**
1. Clear active timer state (if running)
2. Hide all current views (programs, trainings, WOD, program details, timer overlay)
3. Show the onboarding screen (`#view-onboarding`)
4. Reset app state to initial state (but preserve localStorage — program data remains if user resumes)

**Applies to:**
- Programs selection view
- Program configuration view
- Trainings list view
- Program details / workout view
- WOD mode (category selector and WOD display)
- Timer overlay (mid-session)

**Does NOT apply to:**
- Onboarding screen (logo click disabled when already at home)

### Data Persistence

- Clicking the logo does **not** clear localStorage or delete the active program
- If a user was in the middle of a program, that program data remains in localStorage
- When they return to the app later, the saved program will auto-load (existing behavior)
- If they start a new program/WOD from onboarding, it overwrites the previous one

### Error Handling

- If timer is running when logo is clicked, it stops cleanly (no error state)
- No confirmation dialog needed — return to home is a low-friction action

---

## Implementation Checklist

- [ ] Add CSS for logo hover state (`cursor: pointer`, opacity/scale effect)
- [ ] Add click event listener to the logo in the header
- [ ] Create a `goHome()` function that handles the navigation flow
- [ ] Stop timer if running (same cleanup as "Stop Session" button)
- [ ] Hide all views and show onboarding
- [ ] Test from all views: programs, trainings, WOD, timer
- [ ] Test that localStorage is preserved (program can resume if user returns later)
- [ ] Verify logo click is disabled/ineffective on onboarding screen

---

## Edge Cases

**Mid-session timer:** User clicks logo while timer is running → timer stops, overlay closes, returns to onboarding. Next time they load the app, the program is still there.

**WOD mode:** User is browsing WODs, clicks logo → returns to onboarding, WOD state is cleared.

**Program config:** User is selecting duration/frequency, clicks logo → returns to onboarding, config is cleared.

---

## Success Criteria

✅ Logo is clickable and visually indicates interactivity
✅ Clicking logo returns to onboarding from any app view
✅ Timer stops cleanly if running
✅ localStorage is not cleared (program data persists)
✅ Logo click has no effect on onboarding screen
✅ Works on all screen sizes (mobile, tablet)


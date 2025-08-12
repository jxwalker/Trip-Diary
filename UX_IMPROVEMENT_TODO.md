# UX Improvement TODO Plan

## ✅ MVP Launch Readiness (Code Review Findings)
Concrete tasks to fix before MVP, based on current code.

### Flow and Navigation
- [ ] Consolidate to a single flow: Upload → Summary → Preferences → Progress → Guide
- [ ] Remove/deprecate legacy preferences routes from navigation; keep `preferences-modern` as canonical
- [ ] Add consistent CTAs across the app:
  - [ ] Restaurants: "Reserve Table"
  - [ ] Attractions: "Get Tickets"
  - [ ] Events: "Get Tickets"
  - [ ] Hotels: "Book Now" + "Compare Prices"
  - [ ] Always show secondary "Open in Maps"

### Preferences UX and Data Model
- [ ] Eliminate food/meal duplication in Interests; keep all dining in Dining section only (`travel-pack/app/preferences/page.tsx`)
- [ ] Canonicalize preferences schema (server-side) using Pydantic model similar to `travel-pack/backend/models/user_profile.py`
- [ ] Add backend transformer to accept both legacy and modern payloads and normalize to canonical model
- [ ] Validate preferences input (enums, unknown keys, defaults) and reject invalid requests
- [ ] Decide naming convention: camelCase in frontend, snake_case in backend; add server-side map between them

### Guide Content and Booking URLs
- [ ] After guide generation, enrich with booking URLs using `EnhancedRecommendationsService.enhance_all_recommendations`
  - [ ] Wire this enrichment into `POST /api/preferences/{trip_id}` before storing `enhanced_guide`
  - [ ] Ensure daily itinerary items include `type`, `name`, and `address` so activities get `booking_url` and `map_url`
- [ ] Replace any placeholder UI data in guide (weather, tips, amenities). If real data isn’t available, hide the section
- [ ] Wire "Download PDF" in `guide-modern` to the existing PDF API (reuse logic from `app/itinerary/page.tsx`)
- [ ] Add empty states (no events/restaurants) with helpful copy
- [ ] Normalize date placeholders: avoid "TBD" in final guide when dates exist; prefer explicit messages otherwise (see `itinerary_generator.py`)

### Profiles (Save/Load)
- [ ] Implement backend endpoints to save/load/list profiles using `ProfileManager` (see `travel-pack/backend/models/user_profile.py`)
- [ ] Wire `preferences-modern` "Saved" tab to list and load real profiles
- [ ] Support saving current preferences as a named profile
- [ ] Update frontend calls posting to `/api/proxy/profile/save` to use real backend endpoints

### API and Services
- [ ] Add preferences request model in `backend/main.py` to normalize modern/legacy payloads into canonical structure
- [ ] Provide a small update endpoint to persist edits from `summary` page back into `trip_data`
- [ ] Expose weather endpoint (or reuse existing service) and call it from guide sidebar instead of static values
- [ ] Ensure events contain date/venue/ticket URLs; use URL generators when missing
- [ ] Add `/api/profiles` (GET list), `/api/profile/{profile_id}` (GET), `/api/profile` (POST/PUT) endpoints
- [ ] Verify proxy behavior for SSE and downloads is consistent across both `/api/proxy/[...path]` and `/api/proxy/generation-stream/[tripId]` routes

### Progress and Reliability
- [ ] Use SSE (`/api/generation-stream/{trip_id}`) on the generate-itinerary page with retry on transient errors
- [ ] Debounce/batch preference updates if switching to autosave later (post-MVP)
- [ ] Ensure SSE proxy uses `BACKEND_URL` env consistently and gracefully falls back to polling

### Testing (Pre-MVP)
- [ ] Integration test: posting preferences triggers guide generation and items contain `booking_urls` and `map_url`
- [ ] Unit test: preferences transformer (legacy and modern → canonical)
- [ ] E2E happy path: Upload sample → Summary confirm → Preferences → Progress → Guide with working CTAs
- [ ] Test SSE path and fallback polling path (simulate SSE failure)
- [ ] Test PDF generation from guide-modern and download via proxy

### Ops, Security, Cleanup
- [ ] Add TTL cleanup for `uploads/` and `output/` to prevent disk bloat
- [ ] Tighten CORS for prod (no `*`); keep permissive only in dev
- [ ] Ensure no secrets are logged; remove key prints outside test utilities
- [ ] Remove duplicate/old directories (`Trip-Diary/`, `trip-diary/`) and unused files
- [ ] Fix stray `requirements.tx`; ensure `server-manager.sh` installs all required backend deps
- [ ] Update `server-manager.sh` and docs to use consistent project naming (no mixed `Trip-Diary`/`trip-diary`)

### Accessibility and Visual Polish
- [ ] Replace badge-toggles with accessible buttons/checkbox groups (aria-pressed, roles)
- [ ] Standardize spacing/typography scale; reduce icon noise where not informative

## 🚀 Phase 1: Quick Wins (Week 1)
*High impact, low effort improvements*

### Day 1-2: Progress & State Management
- [ ] **Progress Persistence**
  - [ ] Implement localStorage for processing state in `/travel-pack/app/upload-new/page.tsx`
  - [ ] Add "Resume Upload" notification banner when returning user has pending process
  - [ ] Create recovery mechanism for interrupted uploads
  - [ ] Test across browser refresh, navigation, and tab close scenarios

- [ ] **Loading State Messages**
  - [ ] Create array of contextual loading messages for each processing step
  - [ ] Implement rotating messages during document processing
  - [ ] Add progress-specific messages ("Extracting flight details...", "Finding hotels...")
  - [ ] Update `/travel-pack/app/components/ProcessingStatus.tsx` (create if needed)

### Day 3-4: Empty States & Onboarding
- [ ] **Empty State Improvements**
  - [ ] Design and add illustrated empty state for `/travel-pack/app/trips/page.tsx`
  - [ ] Add "Upload Your First Trip" CTA button
  - [ ] Include 3 quick tips about the app's capabilities
  - [ ] Add sample trip data option for new users

- [ ] **First-Time User Onboarding**
  - [ ] Create `useFirstVisit` hook to detect new users
  - [ ] Build 3-step tooltip tour for upload page
  - [ ] Add "Skip tour" option with localStorage preference
  - [ ] Highlight key features: document types, AI processing, real recommendations

### Day 5: Smart Defaults
- [ ] **Preference Optimization**
  - [ ] Add "Quick Start" button to preferences page
  - [ ] Implement destination-based smart defaults (e.g., Paris = museums, cafes)
  - [ ] Add "Skip & Use Defaults" option with clear indication of what defaults are
  - [ ] Create preference templates: "Foodie", "Adventure", "Culture", "Relaxation"

---

## 📱 Phase 2: Mobile Experience (Week 2)
*Critical mobile UX improvements*

### Day 6-7: Touch Targets & Interactions
- [ ] **Touch Target Optimization**
  - [ ] Audit all buttons/links for 44px minimum touch target
  - [ ] Update preference checkboxes to have larger tap areas
  - [ ] Increase spacing between interactive elements
  - [ ] Add CSS for better touch feedback (`-webkit-tap-highlight-color`)

- [ ] **Gesture Support**
  - [ ] Implement swipe between itinerary days using `react-swipeable`
  - [ ] Add pull-to-refresh on trips list page
  - [ ] Enable swipe-to-dismiss for modals and overlays
  - [ ] Test gesture conflicts with browser navigation

### Day 8-9: Mobile-First Patterns
- [ ] **Bottom Sheet Implementation**
  - [ ] Install and configure `react-spring-bottom-sheet` or similar
  - [ ] Convert preference selection to bottom sheet on mobile
  - [ ] Implement filter options as bottom sheet in guide view
  - [ ] Add drag handle and smooth animations

- [ ] **Responsive Navigation**
  - [ ] Create mobile-optimized navigation with hamburger menu
  - [ ] Add bottom navigation bar for key actions (Upload, Trips, Guide)
  - [ ] Implement breadcrumb navigation for multi-step flows
  - [ ] Ensure back button behavior is predictable

### Day 10: Performance Optimization
- [ ] **Scroll & Loading Performance**
  - [ ] Add `scroll-behavior: smooth` to scrollable containers
  - [ ] Implement `-webkit-overflow-scrolling: touch` for iOS
  - [ ] Add Intersection Observer for lazy loading guide sections
  - [ ] Optimize image loading with next/image blur placeholders

---

## 🔄 Phase 3: User Flow Enhancement (Week 3)
*Improving core user journeys*

### Day 11-12: Edit & Review Capabilities
- [ ] **Post-Extraction Review**
  - [ ] Add review step after document extraction
  - [ ] Create editable form for extracted data (flights, hotels, dates)
  - [ ] Implement "Looks good" and "Edit details" options
  - [ ] Add validation for edited data before proceeding

- [ ] **Undo/Redo System**
  - [ ] Implement undo for preference selections
  - [ ] Add "Reset to defaults" option
  - [ ] Create confirmation dialogs for destructive actions
  - [ ] Store action history in session storage

### Day 13-14: Navigation & Wayfinding
- [ ] **Breadcrumb System**
  - [ ] Create Breadcrumb component
  - [ ] Implement on all multi-step flows
  - [ ] Add step indicators (1 of 4, 2 of 4, etc.)
  - [ ] Include "Save & Continue Later" at each step

- [ ] **Search & Filter**
  - [ ] Add search bar to trips page
  - [ ] Implement filter by date, destination, status
  - [ ] Add category filters to guide page (Food, Activities, Hotels)
  - [ ] Store recent searches in localStorage

### Day 15: Help & Context
- [ ] **Contextual Help System**
  - [ ] Add tooltip component with "?" icons
  - [ ] Write help text for all preference options
  - [ ] Create "Why we ask" explanations
  - [ ] Implement keyboard shortcuts help modal

---

## 💡 Phase 4: Delight & Polish (Week 4)
*Making the experience memorable*

### Day 16-17: Micro-Interactions
- [ ] **Animation Polish**
  - [ ] Add subtle hover animations to cards
  - [ ] Implement smooth preference toggle animations
  - [ ] Add success animations (confetti for trip generation)
  - [ ] Create loading skeleton animations

- [ ] **Feedback Improvements**
  - [ ] Add haptic feedback hooks for mobile
  - [ ] Implement sound effects toggle (optional)
  - [ ] Create toast notifications for actions
  - [ ] Add progress celebration milestones

### Day 18-19: Trust & Social Proof
- [ ] **Trust Indicators**
  - [ ] Add "Powered by real-time data" badges
  - [ ] Create "X trips planned this week" counter
  - [ ] Implement "Last updated" timestamps for recommendations
  - [ ] Add data source attributions (Perplexity, OpenAI, etc.)

- [ ] **Sample Content**
  - [ ] Create 3 sample itineraries for popular destinations
  - [ ] Add "Try sample trip" option for new users
  - [ ] Build destination showcase carousel
  - [ ] Include testimonial or use case section

### Day 20: Visual Hierarchy
- [ ] **Information Architecture**
  - [ ] Implement progressive disclosure in guide view
  - [ ] Add collapsible sections with smooth animations
  - [ ] Create "Highlight must-sees" toggle
  - [ ] Improve visual hierarchy with better typography scale

---

## 🎯 Phase 5: Advanced Features (Week 5+)
*Next-level enhancements*

### Collaborative Features
- [ ] **Sharing & Collaboration**
  - [ ] Add "Share with travel companions" feature
  - [ ] Implement unique share links
  - [ ] Create read-only view for shared trips
  - [ ] Add voting mechanism for group preferences

### Smart Suggestions
- [ ] **AI-Powered Recommendations**
  - [ ] Implement "Users also liked" suggestions
  - [ ] Add weather-based activity recommendations
  - [ ] Create "Hidden gems" section based on preferences
  - [ ] Build "Similar trips" discovery feature

### Optimistic Updates
- [ ] **Performance Perception**
  - [ ] Implement optimistic UI updates for all user actions
  - [ ] Add rollback mechanism for failed operations
  - [ ] Create smooth state transitions
  - [ ] Implement incremental data loading

---

## 📊 Measurement & Testing

### Analytics Setup
- [ ] Implement analytics tracking for:
  - [ ] Upload → Generation completion rate
  - [ ] Time to first itinerary view
  - [ ] Preference completion vs. skip rate
  - [ ] Mobile vs. desktop usage patterns
  - [ ] Feature adoption rates

### A/B Testing
- [ ] Set up A/B testing framework
- [ ] Test: Skip preferences vs. Required preferences
- [ ] Test: Single-step vs. Multi-step upload
- [ ] Test: Different loading message strategies
- [ ] Test: Bottom sheet vs. Full page on mobile

### User Testing
- [ ] Conduct usability testing with 5 users
- [ ] Create feedback collection mechanism
- [ ] Implement feedback widget
- [ ] Schedule weekly review of user feedback
- [ ] Iterate based on findings

---

## 🏁 Success Criteria

### Week 1 Goals
- ✅ 0% lost progress due to navigation
- ✅ 50% reduction in time to first itinerary
- ✅ 80% of users understand app purpose immediately

### Week 2 Goals
- ✅ 100% mobile touch targets meet 44px minimum
- ✅ Mobile engagement rate increases by 30%
- ✅ Mobile scroll performance < 16ms frame time

### Week 3 Goals
- ✅ 90% of users successfully complete full flow
- ✅ Support ticket reduction by 40%
- ✅ User-reported errors decrease by 50%

### Week 4 Goals
- ✅ Net Promoter Score > 8.0
- ✅ 60% of users return within 30 days
- ✅ 40% of users try multiple trips

### Week 5+ Goals
- ✅ 25% of trips are shared with others
- ✅ AI suggestions have 70% acceptance rate
- ✅ Page load time < 1 second perceived

---

## 🚨 Priority Order

### Must-Have (Do First)
1. Progress Persistence
2. Touch Target Optimization
3. Smart Defaults
4. Loading State Enhancement
5. Post-Extraction Review

### Should-Have (Do Second)
6. Onboarding Flow
7. Bottom Sheet Pattern
8. Breadcrumb Navigation
9. Search & Filter
10. Contextual Help

### Nice-to-Have (Do Last)
11. Micro-interactions
12. Social Proof
13. Collaborative Features
14. Smart Suggestions
15. A/B Testing Framework

---

## 🛠 Technical Requirements

### Dependencies to Add
```json
{
  "react-spring-bottom-sheet": "^3.4.0",
  "react-swipeable": "^7.0.0",
  "react-intersection-observer": "^9.5.0",
  "react-confetti": "^6.1.0",
  "react-hotkeys-hook": "^4.4.0",
  "react-joyride": "^2.5.0"
}
```

### Browser Support
- Chrome 90+
- Safari 14+
- Firefox 88+
- Edge 90+
- iOS Safari 14+
- Chrome Android 90+

### Performance Targets
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3.0s
- Cumulative Layout Shift: < 0.1
- Largest Contentful Paint: < 2.5s

---

## 📝 Notes

- Each item should be tested on both mobile and desktop
- Maintain "no mocks" policy throughout all improvements
- Keep accessibility in mind (WCAG 2.1 AA compliance)
- Document all new patterns in component library
- Update CLAUDE.md with any new architectural decisions
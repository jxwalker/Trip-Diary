# MVP Design - Ultimate Travel Pack

## MVP Scope Definition

### Core Features for MVP
1. **Document Upload** - PDF parsing for flights and hotels
2. **Smart Extraction** - LLM-powered data extraction
3. **Basic Itinerary** - Chronological timeline generation
4. **Simple Recommendations** - Food & attractions near hotel
5. **Beautiful PDF Export** - Professional travel pack with maps
6. **Modern UI** - Stunning interface with animations

### Deferred to V2
- Email forwarding
- Advanced preferences learning
- Real-time collaboration
- Multiple trip management
- Expense tracking

## UI/UX Design System

### Brand Identity
- **Name**: TripCraft AI
- **Tagline**: "Your AI Travel Companion"
- **Personality**: Smart, Elegant, Trustworthy, Delightful

### Color Palette
```css
--primary: #0ea5e9 (Sky Blue)
--primary-dark: #0284c7
--secondary: #f97316 (Orange)
--accent: #8b5cf6 (Purple)
--success: #10b981 (Green)
--neutral: #64748b (Slate)
--background: #ffffff
--surface: #f8fafc
--text: #0f172a
```

### Typography
- **Headings**: Inter (Bold)
- **Body**: Inter (Regular)
- **Accent**: Cal Sans (or similar display font)

## Page Designs

### 1. Landing Page
```
┌────────────────────────────────────┐
│  TripCraft AI  [Upload] [Sign In]  │
├────────────────────────────────────┤
│                                    │
│    ✈️ Transform Your Travel Docs   │
│    Into Beautiful Itineraries      │
│                                    │
│    [Get Started] [View Demo]       │
│                                    │
│  ┌──────┐ ┌──────┐ ┌──────┐      │
│  │Upload│→│  AI   │→│ PDF  │      │
│  │ Docs │ │Process│ │Export│      │
│  └──────┘ └──────┘ └──────┘      │
│                                    │
│  Features:                         │
│  • Smart PDF Extraction            │
│  • AI-Powered Recommendations      │
│  • Beautiful Maps & Weather        │
│  • One-Click PDF Generation        │
└────────────────────────────────────┘
```

### 2. Upload Interface
```
┌────────────────────────────────────┐
│  Step 1: Upload Documents          │
├────────────────────────────────────┤
│                                    │
│  ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐       │
│  │                         │       │
│  │   📄 Drop files here    │       │
│  │   or click to browse    │       │
│  │                         │       │
│  └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘       │
│                                    │
│  Uploaded Files:                   │
│  ✅ flight_confirmation.pdf        │
│  ✅ hotel_booking.pdf              │
│  ⏳ Processing rental_car.pdf      │
│                                    │
│  [Continue →]                      │
└────────────────────────────────────┘
```

### 3. Trip Builder
```
┌────────────────────────────────────┐
│  Your Trip: NYC Adventure          │
│  Dec 15-20, 2024                   │
├────────────────────────────────────┤
│  ┌─────────┐ ┌─────────────────┐  │
│  │Timeline │ │     Map View     │  │
│  │         │ │                  │  │
│  │Day 1    │ │  [Interactive    │  │
│  │✈️ Arrive│ │   Map with       │  │
│  │🏨 Check │ │   Markers]       │  │
│  │   In    │ │                  │  │
│  │         │ │                  │  │
│  │Day 2    │ │                  │  │
│  │🎨 Museum│ │                  │  │
│  │🍽️ Dinner│ │                  │  │
│  └─────────┘ └─────────────────┘  │
│                                    │
│  [Customize] [Add Event] [Export]  │
└────────────────────────────────────┘
```

### 4. Preferences Panel
```
┌────────────────────────────────────┐
│  Customize Your Experience         │
├────────────────────────────────────┤
│  Interests:                        │
│  🍽️ Food & Dining     [███████░]  │
│  🎨 Art & Culture      [█████░░░]  │
│  🎭 Entertainment      [████░░░░]  │
│  🛍️ Shopping          [██░░░░░░]  │
│                                    │
│  Budget Range:                     │
│  [$] [$$] [$$$ selected] [$$$$]   │
│                                    │
│  Dietary Preferences:              │
│  [✓] Vegetarian [ ] Vegan         │
│  [ ] Gluten-Free [ ] Halal        │
│                                    │
│  Walking Preference:               │
│  ○ Light ● Moderate ○ Heavy       │
│                                    │
│  [Apply Preferences]               │
└────────────────────────────────────┘
```

### 5. Results Dashboard
```
┌────────────────────────────────────┐
│  Your Travel Pack is Ready! 🎉     │
├────────────────────────────────────┤
│  ┌─────────────┐ ┌──────────────┐ │
│  │ PDF Preview │ │  Quick Stats │ │
│  │             │ │              │ │
│  │  [Cover]    │ │ 5 Days       │ │
│  │  [Page 2]   │ │ 2 Hotels     │ │
│  │  [Page 3]   │ │ 4 Flights    │ │
│  │             │ │ 15 Places    │ │
│  │             │ │ 8 Events     │ │
│  └─────────────┘ └──────────────┘ │
│                                    │
│  Includes:                         │
│  ✓ Day-by-day itinerary           │
│  ✓ Interactive maps               │
│  ✓ Weather forecast               │
│  ✓ Restaurant recommendations     │
│  ✓ Local events & tickets         │
│                                    │
│  [Download PDF] [Share] [Edit]     │
└────────────────────────────────────┘
```

## Component Library

### Core Components Needed
1. **Navigation**
   - Sticky header with progress indicator
   - Mobile hamburger menu
   - User avatar dropdown

2. **Upload**
   - Drag-and-drop zone
   - File type icons
   - Upload progress bars
   - Success/error states

3. **Cards**
   - Document card
   - Event card
   - Restaurant card
   - Hotel card
   - Flight card

4. **Forms**
   - Preference sliders
   - Toggle switches
   - Date pickers
   - Search inputs

5. **Feedback**
   - Loading spinners
   - Progress steps
   - Toast notifications
   - Empty states

6. **Actions**
   - Primary/secondary buttons
   - Icon buttons
   - Floating action buttons

## Animation Strategy

### Micro-interactions
- Button hover effects
- Card lift on hover
- Smooth transitions
- Progress animations
- Success checkmarks

### Page Transitions
- Fade in/out
- Slide between steps
- Parallax scrolling on landing
- Stagger animations for lists

### Loading States
- Skeleton screens
- Shimmer effects
- Progress indicators
- Animated placeholders

## Responsive Breakpoints
- Mobile: 320px - 768px
- Tablet: 768px - 1024px
- Desktop: 1024px+
- Wide: 1440px+

## MVP Technical Stack

### Frontend
```json
{
  "framework": "Next.js 14",
  "ui": "shadcn/ui",
  "styling": "Tailwind CSS",
  "animations": "Framer Motion",
  "forms": "React Hook Form + Zod",
  "state": "Zustand",
  "http": "Axios/Fetch",
  "icons": "Lucide React"
}
```

### File Structure
```
/app
  /(auth)
    /signin
    /signup
  /(dashboard)
    /upload
    /builder
    /preview
  /api
    /upload
    /process
    /generate
  /page.tsx (landing)
/components
  /ui (shadcn)
  /upload
  /builder
  /cards
  /animations
/lib
  /utils
  /api
  /types
/public
  /images
  /fonts
```
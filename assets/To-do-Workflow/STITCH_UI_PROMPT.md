# OrkestrAI - Stitch UI Generation Prompt

## Product Overview

**OrkestrAI** is a futuristic AI-powered multi-agent software development orchestration platform that transforms hackathon ideas into execution-ready projects automatically. It's an AI operating system where 5 specialized AI agents collaborate in real-time to generate complete project deliverables: product strategy, system architecture, production code, GitHub workflows, and pitch materials.

**Core Value Proposition**: Reduces 8 hours of hackathon planning to 5 minutes through intelligent AI orchestration.

---

## Design Philosophy

Create a **futuristic AI-native orchestration dashboard** that feels like:
- **Cursor AI** - Clean, developer-focused, intelligent
- **Linear** - Smooth animations, polished interactions, modern aesthetics
- **Vercel** - Minimalist, fast, beautiful gradients
- **Sci-Fi AI OS** - Glowing elements, particle effects, agent personalities

### Visual Identity
- **Color Palette**: Deep space blacks (#0a0a0f), electric blues (#0ea5e9), neon purples (#8b5cf6), cyber greens (#10b981), warm oranges (#f59e0b), hot pinks (#ec4899)
- **Typography**: Inter for UI, JetBrains Mono for code
- **Motion**: Smooth 60fps animations, spring physics, micro-interactions
- **Lighting**: Subtle glows, gradient overlays, depth through shadows

---

## Application Architecture

### Tech Stack
- **Frontend**: Next.js 14 (App Router), React 18, TypeScript
- **Styling**: Tailwind CSS with custom design system
- **State**: Zustand for global state management
- **Real-time**: WebSocket connections for live updates
- **Animations**: Framer Motion for complex animations
- **Code Display**: React Syntax Highlighter with custom themes

### Backend Integration
- **API Base**: FastAPI backend at `/api/v1`
- **WebSocket**: Real-time orchestration updates at `ws://backend/ws/orchestration/{projectId}`
- **Authentication**: GitHub OAuth (future)
- **Data Flow**: REST for CRUD, WebSocket for streaming

---

## Page Structure & Routing

### 1. Landing Page (`/`)
**Purpose**: Hero section that sells the vision

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│  Header: Logo | Features | Pricing | GitHub             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│              HERO SECTION                               │
│   "Your AI Team for Hackathon Success"                 │
│   [Animated gradient background with particles]        │
│   [Large CTA: "Start Building →"]                      │
│                                                         │
├─────────────────────────────────────────────────────────┤
│              FEATURES GRID (3 columns)                  │
│   [5 AI Agents] [Real-time] [Production Code]         │
│                                                         │
├─────────────────────────────────────────────────────────┤
│              HOW IT WORKS (Timeline)                    │
│   Input Idea → AI Orchestration → Get Deliverables    │
│                                                         │
├─────────────────────────────────────────────────────────┤
│              DEMO VIDEO / SCREENSHOT                    │
│   [Embedded video or animated showcase]                │
│                                                         │
├─────────────────────────────────────────────────────────┤
│              FINAL CTA                                  │
│   "Ready to transform your hackathon?"                 │
│   [Button: "Get Started Free"]                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Key Elements**:
- **Animated gradient background**: Slow-moving mesh gradient (blue → purple → pink)
- **Particle system**: Floating dots connecting in constellation patterns
- **Typing effect**: Hero text types out character by character
- **Hover states**: Cards lift with glow effects
- **Scroll animations**: Elements fade in as you scroll

---

### 2. Create Project Page (`/create`)
**Purpose**: Input form for new project idea

**Layout**:
```
┌─────────────────────────────────────────────────────────┐
│  Header: Logo | Dashboard | Profile                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│              CREATE NEW PROJECT                         │
│                                                         │
│   ┌───────────────────────────────────────────────┐   │
│   │  Project Name                                  │   │
│   │  [Input field with subtle glow on focus]      │   │
│   └───────────────────────────────────────────────┘   │
│                                                         │
│   ┌───────────────────────────────────────────────┐   │
│   │  Describe Your Idea                           │   │
│   │  [Large textarea, 8 rows, character count]    │   │
│   │  "I want to build a social platform for..."   │   │
│   │                                                │   │
│   │  [Character count: 245/2000]                  │   │
│   └───────────────────────────────────────────────┘   │
│                                                         │
│   ┌───────────────────────────────────────────────┐   │
│   │  Preferences (Optional)                       │   │
│   │  [Collapsible section]                        │   │
│   │  • Tech Stack: [Multi-select chips]          │   │
│   │  • Deployment: [Dropdown]                     │   │
│   │  • Include Auth: [Toggle]                     │   │
│   └───────────────────────────────────────────────┘   │
│                                                         │
│   ┌───────────────────────────────────────────────┐   │
│   │  Example Prompts                              │   │
│   │  [3 clickable example cards]                  │   │
│   │  "Social network" | "SaaS tool" | "AI app"   │   │
│   └───────────────────────────────────────────────┘   │
│                                                         │
│              [Start Orchestration Button]              │
│              [Glowing, pulsing, large]                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Interactions**:
- **Focus states**: Input fields glow with brand color
- **Character counter**: Updates in real-time, changes color near limit
- **Example prompts**: Click to populate textarea
- **Button state**: Disabled until minimum input length
- **Loading state**: Button transforms to spinner on submit

---

### 3. Orchestration View (`/project/[id]`)
**Purpose**: Real-time visualization of AI agents working

**Layout** (Desktop):
```
┌─────────────────────────────────────────────────────────────────┐
│  Header: Project Name | Progress: ████░░ 60% | Status: Active  │
├──────────────┬──────────────────────────────────────────────────┤
│              │                                                  │
│   AGENT      │              MAIN CONTENT AREA                  │
│   PANEL      │                                                  │
│   (240px)    │  ┌────────────────────────────────────────────┐ │
│              │  │  PROGRESS TRACKER                          │ │
│  ┌────────┐  │  │  [5 steps with connecting lines]          │ │
│  │ [👤]   │  │  │  Strategy → Architecture → Code → ...     │ │
│  │Strategy│  │  └────────────────────────────────────────────┘ │
│  │ ✓      │  │                                                  │
│  └────────┘  │  ┌────────────────────────────────────────────┐ │
│              │  │  ACTIVITY TIMELINE                         │ │
│  ┌────────┐  │  │  [Vertical timeline with events]           │ │
│  │ [👤]   │  │  │                                            │ │
│  │Architect│  │  │  ● Strategy Agent started                │ │
│  │ ⚡     │  │  │  │  Analyzing requirements...             │ │
│  └────────┘  │  │  │  ✓ Completed in 2.3s                  │ │
│              │  │  │                                            │ │
│  ┌────────┐  │  │  ● Architecture Agent working              │ │
│  │ [👤]   │  │  │  │  Designing database schema...          │ │
│  │Builder │  │  │  │  [Pulsing indicator]                   │ │
│  │ ⏳     │  │  │                                            │ │
│  └────────┘  │  └────────────────────────────────────────────┘ │
│              │                                                  │
│  ┌────────┐  │  ┌────────────────────────────────────────────┐ │
│  │ [👤]   │  │  │  CODE STREAM                               │ │
│  │GitHub  │  │  │  [Live code generation with syntax]        │ │
│  │ ⏸      │  │  │                                            │ │
│  └────────┘  │  │  // app/main.py                           │ │
│              │  │  from fastapi import FastAPI              │ │
│  ┌────────┐  │  │  [Typing animation effect]                │ │
│  │ [👤]   │  │  │                                            │ │
│  │Pitch   │  │  └────────────────────────────────────────────┘ │
│  │ ⏸      │  │                                                  │
│  └────────┘  │  ┌────────────────────────────────────────────┐ │
│              │  │  OUTPUT PREVIEW                            │ │
│              │  │  [Tabbed cards showing agent outputs]      │ │
│              │  │  [Strategy] [Architecture] [Code]          │ │
│              │  └────────────────────────────────────────────┘ │
│              │                                                  │
└──────────────┴──────────────────────────────────────────────────┘
```

**Agent Panel Components**:
- **Agent Cards**: 
  - Avatar with unique color per agent
  - Agent name and role
  - Status indicator: ⏸ (pending), ⚡ (active), ✓ (complete), ✗ (failed)
  - Pulsing glow when active
  - Subtle bounce animation on state change

**Progress Tracker**:
- Horizontal stepper at top
- 5 steps with connecting lines
- Current step highlighted with glow
- Completed steps show checkmark
- Smooth progress bar animation

**Activity Timeline**:
- Vertical timeline with dots
- Each event shows:
  - Agent avatar (small)
  - Action description
  - Timestamp (relative: "2s ago")
  - Duration for completed tasks
- Auto-scroll to latest event
- Fade-in animation for new events
- Color-coded dots by status

**Code Stream**:
- Dark theme code editor appearance
- Syntax highlighting (language-specific)
- Typing animation effect (characters appear sequentially)
- Line numbers
- File path header
- Copy button on hover
- Smooth scroll as code generates

**Output Preview**:
- Tabbed interface
- Each tab shows agent output
- JSON formatted with collapsible sections
- Download button per output
- Smooth tab transitions

---

### 4. Results Page (`/project/[id]/results`)
**Purpose**: Display all generated artifacts

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  Header: Project Name | Status: ✓ Completed | [Download All]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  TABS                                                      │ │
│  │  [Strategy] [Architecture] [Code] [GitHub] [Pitch]        │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                                                            │ │
│  │              TAB CONTENT AREA                              │ │
│  │                                                            │ │
│  │  [Dynamic content based on selected tab]                  │ │
│  │                                                            │ │
│  │  Strategy Tab:                                             │ │
│  │  • Problem Statement                                       │ │
│  │  • Target Users                                            │ │
│  │  • Core Features (cards)                                   │ │
│  │  • MVP Scope                                               │ │
│  │                                                            │ │
│  │  Architecture Tab:                                         │ │
│  │  • Tech Stack (visual cards)                               │ │
│  │  • Database Schema (table view)                            │ │
│  │  • API Endpoints (list)                                    │ │
│  │  • System Diagram (Mermaid rendered)                       │ │
│  │                                                            │ │
│  │  Code Tab:                                                 │ │
│  │  • File tree (left sidebar)                                │ │
│  │  • Code viewer (right panel)                               │ │
│  │  • Download ZIP button                                     │ │
│  │                                                            │ │
│  │  GitHub Tab:                                               │ │
│  │  • Repository info                                         │ │
│  │  • Issues list (cards)                                     │ │
│  │  • Milestones                                              │ │
│  │  • [Create Repository] button                              │ │
│  │                                                            │ │
│  │  Pitch Tab:                                                │ │
│  │  • Elevator Pitch                                          │ │
│  │  • Demo Script (timeline)                                  │ │
│  │  • Judge Talking Points                                    │ │
│  │  • Slide Outline                                           │ │
│  │                                                            │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Tab-Specific Designs**:

**Strategy Tab**:
- Hero section with problem statement
- Feature cards in grid (3 columns)
- Priority badges (High/Medium/Low) with colors
- User stories in expandable accordions
- Success metrics as stat cards

**Architecture Tab**:
- Tech stack as icon cards with tooltips
- Database schema as interactive table
- API endpoints as collapsible list with method badges
- Mermaid diagram rendered with zoom controls
- Download architecture doc button

**Code Tab**:
- Split view: file tree + code viewer
- File tree with folder icons and expand/collapse
- Code viewer with syntax highlighting
- Search functionality
- Download as ZIP (prominent button)
- Copy individual files

**GitHub Tab**:
- Repository card with stats
- Issues as kanban-style cards
- Milestone progress bars
- "Create Repository" CTA (if not created)
- "View on GitHub" link (if created)

**Pitch Tab**:
- Elevator pitch in large, readable text
- Demo script as timeline with timestamps
- Talking points as categorized cards
- Slide outline as numbered list
- Export buttons (PDF, Markdown)

---

### 5. Dashboard Page (`/dashboard`)
**Purpose**: View all projects

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  Header: Logo | Dashboard | [+ New Project]                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MY PROJECTS                                                    │
│                                                                 │
│  [Search bar] [Filter: All | Active | Completed]               │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │  Project 1  │  │  Project 2  │  │  Project 3  │           │
│  │  [Preview]  │  │  [Preview]  │  │  [Preview]  │           │
│  │  Status: ✓  │  │  Status: ⚡  │  │  Status: ✓  │           │
│  │  2 days ago │  │  Active now │  │  1 week ago │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │  Project 4  │  │  Project 5  │  │  [+ New]    │           │
│  │  [Preview]  │  │  [Preview]  │  │  Create     │           │
│  │  Status: ✓  │  │  Status: ✗  │  │  Project    │           │
│  │  2 weeks ago│  │  Failed     │  │             │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Project Cards**:
- Thumbnail/preview image
- Project name
- Status badge with icon
- Timestamp (relative)
- Hover: Lift effect + glow
- Click: Navigate to results

---

## Component Design System

### 1. Agent Cards
```
┌──────────────────┐
│   [Avatar]       │  ← Circular avatar with agent color
│   Agent Name     │  ← Bold, 14px
│   Role           │  ← Light, 12px
│   [Status Icon]  │  ← Animated based on state
└──────────────────┘
```

**States**:
- **Pending**: Gray, no animation
- **Active**: Pulsing glow, rotating spinner
- **Thinking**: Blue glow, typing dots animation
- **Complete**: Green checkmark, success glow
- **Failed**: Red X, error shake

**Agent Colors**:
- Strategy: Purple (#8b5cf6)
- Architecture: Blue (#3b82f6)
- Builder: Green (#10b981)
- GitHub: Orange (#f59e0b)
- Pitch: Pink (#ec4899)

### 2. Progress Tracker
```
[●]━━━━[●]━━━━[○]━━━━[○]━━━━[○]
 ✓      ✓      ⚡     ⏸     ⏸
Strategy Arch  Code  GitHub Pitch
```

**Visual Design**:
- Filled circles for completed steps
- Glowing circle for active step
- Empty circles for pending steps
- Connecting lines (solid for complete, dashed for pending)
- Smooth progress animation

### 3. Activity Timeline Event
```
┌────────────────────────────────────┐
│ ● [Avatar] Agent Name              │
│ │  Action description              │
│ │  2 seconds ago                   │
│ │  ✓ Completed in 2.3s             │
└────────────────────────────────────┘
```

**Animation**:
- Slide in from bottom
- Fade in opacity
- Dot pulses when active
- Auto-scroll to latest

### 4. Code Stream Block
```
┌────────────────────────────────────┐
│ backend/app/main.py          [📋] │
├────────────────────────────────────┤
│  1  from fastapi import FastAPI   │
│  2  from fastapi.middleware...    │
│  3                                 │
│  4  app = FastAPI(                │
│  5      title="OrkestrAI"         │
│  6  )                              │
└────────────────────────────────────┘
```

**Features**:
- Dark theme (VS Code style)
- Syntax highlighting
- Line numbers
- Copy button (appears on hover)
- Typing animation effect
- Smooth scroll

### 5. Button Styles

**Primary Button** (CTA):
```css
background: linear-gradient(135deg, #0ea5e9, #8b5cf6)
padding: 12px 32px
border-radius: 8px
font-weight: 600
box-shadow: 0 4px 20px rgba(14, 165, 233, 0.3)
hover: scale(1.05), glow increases
active: scale(0.98)
```

**Secondary Button**:
```css
background: transparent
border: 1px solid rgba(255, 255, 255, 0.2)
padding: 10px 24px
border-radius: 8px
hover: border-color increases, background subtle
```

**Loading State**:
- Button content fades out
- Spinner fades in
- Button width maintains
- Disabled state

### 6. Input Fields
```
┌────────────────────────────────────┐
│ Label                              │
│ ┌────────────────────────────────┐ │
│ │ Placeholder text...            │ │
│ └────────────────────────────────┘ │
│ Helper text or character count     │
└────────────────────────────────────┘
```

**States**:
- **Default**: Border subtle gray
- **Focus**: Border glows with brand color, subtle shadow
- **Error**: Red border, shake animation
- **Success**: Green border, checkmark icon

### 7. Status Badges
```
[✓ Completed]  [⚡ Active]  [⏸ Pending]  [✗ Failed]
```

**Colors**:
- Completed: Green background, darker green text
- Active: Blue background, pulsing animation
- Pending: Gray background
- Failed: Red background

---

## Animation & Interaction Patterns

### Page Transitions
- **Enter**: Fade in + slide up (20px)
- **Exit**: Fade out + slide down (20px)
- **Duration**: 300ms
- **Easing**: cubic-bezier(0.4, 0, 0.2, 1)

### Micro-interactions
1. **Button Hover**: Scale 1.05, glow increases
2. **Card Hover**: Lift (translateY -4px), shadow increases
3. **Input Focus**: Border glow, label color change
4. **Tab Switch**: Slide content, fade transition
5. **Accordion**: Smooth height animation
6. **Toast Notifications**: Slide in from top-right

### Loading States
1. **Skeleton Screens**: Pulsing gray blocks
2. **Spinners**: Rotating gradient circle
3. **Progress Bars**: Smooth width animation
4. **Typing Effect**: Characters appear sequentially

### Real-time Updates
1. **New Event**: Slide in from bottom, pulse
2. **Status Change**: Color transition, icon swap
3. **Progress Update**: Smooth bar animation
4. **Code Generation**: Typing effect

---

## WebSocket Orchestration Behavior

### Connection Flow
1. User creates project → Redirected to orchestration view
2. Component mounts → Establish WebSocket connection
3. Connection opens → Subscribe to project events
4. Receive events → Update UI in real-time
5. Orchestration completes → Show completion animation
6. Connection closes → Cleanup

### Event Types & UI Updates

**1. `orchestration_start`**
- Show "Starting orchestration..." message
- Initialize progress tracker
- Reset all agent states to pending

**2. `agent_start`**
- Update agent card to "active" state
- Add timeline event: "Agent started"
- Pulse agent avatar
- Update progress tracker

**3. `agent_thinking`**
- Add timeline event with message
- Show typing dots animation
- Update agent card subtitle

**4. `agent_output`**
- Stream code to code viewer (if code output)
- Update output preview tab
- Add timeline event: "Generated output"

**5. `agent_complete`**
- Update agent card to "complete" state
- Add timeline event with duration
- Show success animation (checkmark)
- Move progress tracker forward

**6. `orchestration_complete`**
- Show completion modal/toast
- Confetti animation
- Enable "View Results" button
- Update project status

**7. `error`**
- Update agent card to "failed" state
- Show error toast
- Add timeline event with error details
- Offer "Retry" button

### Real-time Streaming UX

**Code Streaming**:
- Characters appear one by one (typing effect)
- Syntax highlighting applies in real-time
- Auto-scroll to bottom as code generates
- Line numbers update dynamically
- Smooth, not jarring

**Progress Updates**:
- Progress bar animates smoothly (not jumpy)
- Percentage updates every 100ms
- Estimated time remaining shown
- Visual feedback for each milestone

**Timeline Updates**:
- New events slide in from bottom
- Auto-scroll to latest event
- Older events fade slightly
- Maximum 50 events shown (virtualized)

---

## Responsive Design

### Breakpoints
- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

### Mobile Adaptations

**Orchestration View**:
```
┌─────────────────────┐
│ Header (sticky)     │
├─────────────────────┤
│ Progress Tracker    │
│ [Horizontal scroll] │
├─────────────────────┤
│ Agent Panel         │
│ [Horizontal cards]  │
├─────────────────────┤
│ Activity Timeline   │
│ [Collapsible]       │
├─────────────────────┤
│ Code Stream         │
│ [Full width]        │
└─────────────────────┘
```

**Changes**:
- Agent panel becomes horizontal scrollable cards
- Timeline collapses by default (expandable)
- Code stream takes full width
- Tabs become dropdown on mobile
- Touch-friendly tap targets (min 44px)

---

## Loading & Thinking States

### Initial Page Load
- Skeleton screens for content
- Pulsing gray blocks matching layout
- Logo animation in center
- "Loading..." text with dots animation

### Agent Thinking States
1. **Analyzing**: Rotating brain icon
2. **Designing**: Drafting compass icon
3. **Coding**: Typing keyboard icon
4. **Integrating**: Connecting nodes icon
5. **Finalizing**: Checkmark forming icon

### Empty States
- Friendly illustration
- Clear message: "No projects yet"
- CTA button: "Create your first project"
- Subtle animation (floating)

### Error States
- Error icon (not scary)
- Clear error message
- Suggested actions
- "Try again" button
- "Contact support" link

---

## Accessibility (WCAG 2.1 AA)

### Keyboard Navigation
- All interactive elements focusable
- Visible focus indicators (2px outline)
- Logical tab order
- Escape key closes modals
- Arrow keys navigate lists

### Screen Readers
- Semantic HTML (header, nav, main, section)
- ARIA labels for icons
- ARIA live regions for real-time updates
- Alt text for images
- Descriptive link text

### Color Contrast
- Text: Minimum 4.5:1 ratio
- Large text: Minimum 3:1 ratio
- Interactive elements: Clear visual distinction
- Don't rely on color alone for information

### Motion
- Respect `prefers-reduced-motion`
- Disable animations if user prefers
- Provide alternative static views
- No auto-playing videos

---

## Performance Optimizations

### Code Splitting
- Lazy load heavy components (syntax highlighter)
- Dynamic imports for routes
- Split vendor bundles
- Preload critical resources

### Image Optimization
- Next.js Image component
- WebP format with fallbacks
- Lazy loading below fold
- Responsive images

### State Management
- Memoize expensive calculations
- Use React.memo for pure components
- Optimize re-renders with useMemo/useCallback
- Debounce search inputs

### WebSocket
- Reconnect on disconnect
- Queue messages during reconnection
- Throttle high-frequency updates
- Close connection on unmount

---

## Futuristic Design Elements

### Particle System
- Floating particles in background
- Connect when close (constellation effect)
- Subtle, not distracting
- Responds to mouse movement
- Canvas-based for performance

### Gradient Overlays
- Animated mesh gradients
- Slow color transitions
- Depth through layering
- Blend modes for richness

### Glow Effects
- Subtle glows on active elements
- Pulsing for attention
- Color-coded by agent
- Box-shadow with blur

### Glass Morphism
- Frosted glass effect on cards
- Backdrop blur
- Semi-transparent backgrounds
- Subtle borders

### Neon Accents
- Bright accent colors
- Used sparingly for emphasis
- Glow effects on hover
- Cyberpunk aesthetic

---

## Hackathon Wow-Factor Features

### 1. Live Agent Avatars
- Animated SVG avatars
- Unique personality per agent
- React to events (happy, thinking, celebrating)
- Smooth transitions between states

### 2. Code Generation Animation
- Matrix-style code rain effect
- Typing animation with realistic speed
- Syntax highlighting appears progressively
- Sound effects (optional, toggleable)

### 3. Orchestration Timeline
- Beautiful vertical timeline
- Animated connections between events
- Color-coded by agent
- Smooth auto-scroll

### 4. Completion Celebration
- Confetti animation
- Success modal with stats
- Share buttons (Twitter, LinkedIn)
- Download all artifacts button

### 5. Real-time Collaboration Indicators
- Show when agents are "talking" to each other
- Animated data flow between agents
- Visual representation of context sharing

### 6. Interactive System Diagram
- Clickable architecture diagram
- Zoom and pan controls
- Highlight data flow on hover
- Export as image

---

## Technical Implementation Notes

### State Management Structure
```typescript
// Zustand stores
interface ProjectStore {
  projects: Project[]
  currentProject: Project | null
  isLoading: boolean
  error: string | null
}

interface OrchestrationStore {
  status: 'idle' | 'orchestrating' | 'completed' | 'failed'
  currentAgent: string | null
  progress: number
  logs: AgentLog[]
  outputs: Record<string, any>
}

interface UIStore {
  sidebarOpen: boolean
  activeTab: string
  theme: 'light' | 'dark'
}
```

### WebSocket Hook
```typescript
useWebSocket(projectId: string) {
  // Establish connection
  // Listen for events
  // Update Zustand stores
  // Handle reconnection
  // Cleanup on unmount
}
```

### Animation Library
```typescript
// Framer Motion variants
const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
}

const staggerChildren = {
  animate: {
    transition: {
      staggerChildren: 0.1
    }
  }
}
```

---

## Color Palette (Detailed)

### Primary Colors
```css
--primary-50: #f0f9ff
--primary-100: #e0f2fe
--primary-500: #0ea5e9
--primary-600: #0284c7
--primary-700: #0369a1
--primary-900: #0c4a6e
```

### Agent Colors
```css
--agent-strategy: #8b5cf6   /* Purple */
--agent-architecture: #3b82f6 /* Blue */
--agent-builder: #10b981     /* Green */
--agent-github: #f59e0b      /* Orange */
--agent-pitch: #ec4899       /* Pink */
```

### Semantic Colors
```css
--success: #10b981
--error: #ef4444
--warning: #f59e0b
--info: #3b82f6
```

### Neutral Colors
```css
--gray-50: #f9fafb
--gray-100: #f3f4f6
--gray-200: #e5e7eb
--gray-300: #d1d5db
--gray-400: #9ca3af
--gray-500: #6b7280
--gray-600: #4b5563
--gray-700: #374151
--gray-800: #1f2937
--gray-900: #111827
--gray-950: #0a0a0f
```

### Background Gradients
```css
--gradient-hero: linear-gradient(135deg, #0ea5e9 0%, #8b5cf6 50%, #ec4899 100%)
--gradient-card: linear-gradient(135deg, rgba(14, 165, 233, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)
--gradient-button: linear-gradient(135deg, #0ea5e9 0%, #8b5cf6 100%)
```

---

## Typography Scale

### Font Families
```css
--font-sans: 'Inter', system-ui, sans-serif
--font-mono: 'JetBrains Mono', 'Fira Code', monospace
```

### Font Sizes
```css
--text-xs: 0.75rem    /* 12px */
--text-sm: 0.875rem   /* 14px */
--text-base: 1rem     /* 16px */
--text-lg: 1.125rem   /* 18px */
--text-xl: 1.25rem    /* 20px */
--text-2xl: 1.5rem    /* 24px */
--text-3xl: 1.875rem  /* 30px */
--text-4xl: 2.25rem   /* 36px */
--text-5xl: 3rem      /* 48px */
--text-6xl: 3.75rem   /* 60px */
```

### Font Weights
```css
--font-normal: 400
--font-medium: 500
--font-semibold: 600
--font-bold: 700
```

---

## Spacing System

```css
--space-1: 0.25rem   /* 4px */
--space-2: 0.5rem    /* 8px */
--space-3: 0.75rem   /* 12px */
--space-4: 1rem      /* 16px */
--space-5: 1.25rem   /* 20px */
--space-6: 1.5rem    /* 24px */
--space-8: 2rem      /* 32px */
--space-10: 2.5rem   /* 40px */
--space-12: 3rem     /* 48px */
--space-16: 4rem     /* 64px */
--space-20: 5rem     /* 80px */
```

---

## Shadow System

```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05)
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1)
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1)
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1)
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25)
--shadow-glow: 0 0 20px rgba(14, 165, 233, 0.5)
```

---

## Border Radius

```css
--radius-sm: 0.25rem   /* 4px */
--radius-md: 0.375rem  /* 6px */
--radius-lg: 0.5rem    /* 8px */
--radius-xl: 0.75rem   /* 12px */
--radius-2xl: 1rem     /* 16px */
--radius-full: 9999px  /* Circular */
```

---

## Z-Index Scale

```css
--z-base: 0
--z-dropdown: 1000
--z-sticky: 1100
--z-fixed: 1200
--z-modal-backdrop: 1300
--z-modal: 1400
--z-popover: 1500
--z-tooltip: 1600
--z-toast: 1700
```

---

## Final Notes for Stitch AI

### Generation Priorities
1. **Visual Polish**: Make it look stunning first
2. **Smooth Animations**: 60fps, spring physics
3. **Real-time Updates**: WebSocket integration working
4. **Responsive**: Mobile-first, works on all devices
5. **Accessible**: WCAG 2.1 AA compliant

### Key Differentiators
- **Agent Personalities**: Each agent feels unique
- **Live Orchestration**: Real-time is the star feature
- **Code Streaming**: Matrix-style generation
- **Futuristic Aesthetic**: Sci-fi AI OS vibes
- **Hackathon Ready**: Designed to impress judges

### Must-Have Features
- ✅ Real-time WebSocket updates
- ✅ Animated agent avatars
- ✅ Code syntax highlighting with typing effect
- ✅ Activity timeline with smooth animations
- ✅ Progress tracker with visual feedback
- ✅ Responsive design (mobile + desktop)
- ✅ Dark theme with neon accents
- ✅ Particle effects and gradients
- ✅ Smooth page transitions
- ✅ Loading and error states

### Success Criteria
The UI should make judges say:
- "Wow, this looks professional!"
- "The real-time updates are so smooth!"
- "I love watching the agents work!"
- "This feels like the future of development!"
- "I want to use this for my next project!"

---

**Generate a visually stunning, futuristic AI orchestration dashboard that feels alive, intelligent, and production-ready. Make it the kind of interface that wins hackathons.**
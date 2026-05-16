---
name: OrkestrAI
colors:
  surface: '#131318'
  surface-dim: '#131318'
  surface-bright: '#39383e'
  surface-container-lowest: '#0e0e13'
  surface-container-low: '#1b1b20'
  surface-container: '#1f1f25'
  surface-container-high: '#2a292f'
  surface-container-highest: '#35343a'
  on-surface: '#e4e1e9'
  on-surface-variant: '#bec8d2'
  inverse-surface: '#e4e1e9'
  inverse-on-surface: '#303036'
  outline: '#88929b'
  outline-variant: '#3e4850'
  surface-tint: '#89ceff'
  primary: '#89ceff'
  on-primary: '#00344d'
  primary-container: '#0ea5e9'
  on-primary-container: '#003751'
  inverse-primary: '#006591'
  secondary: '#d0bcff'
  on-secondary: '#3c0091'
  secondary-container: '#571bc1'
  on-secondary-container: '#c4abff'
  tertiary: '#4edea3'
  on-tertiary: '#003824'
  tertiary-container: '#00b17b'
  on-tertiary-container: '#003b26'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#c9e6ff'
  primary-fixed-dim: '#89ceff'
  on-primary-fixed: '#001e2f'
  on-primary-fixed-variant: '#004c6e'
  secondary-fixed: '#e9ddff'
  secondary-fixed-dim: '#d0bcff'
  on-secondary-fixed: '#23005c'
  on-secondary-fixed-variant: '#5516be'
  tertiary-fixed: '#6ffbbe'
  tertiary-fixed-dim: '#4edea3'
  on-tertiary-fixed: '#002113'
  on-tertiary-fixed-variant: '#005236'
  background: '#131318'
  on-background: '#e4e1e9'
  surface-variant: '#35343a'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  body-base:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  code-sm:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 16px
  margin: 24px
  sidebar-width: 260px
  inspector-width: 320px
---

## Brand & Style
The design system is a high-performance, AI-native interface designed for developers and orchestration engineers. It bridges the gap between a traditional command-line interface and a sophisticated visual OS. The brand personality is "Autonomous Intelligence"—efficient, predictive, and cutting-edge.

The aesthetic follows a **Sci-Fi Modernist** approach. It combines the utility of developer tools like Cursor and Linear with the immersive depth of futuristic operating systems. Key stylistic drivers include:
- **Minimalist Technicality:** Heavy reliance on structured grids and precise typography.
- **Glassmorphism:** Contextual layers that use backdrop filters to maintain a sense of depth without clutter.
- **Subtle Luminescence:** Using light as a functional signifier (e.g., status glows, active traces) rather than just decoration.
- **Micro-interactions:** Spring-based motion that feels organic yet snappy, reinforcing the "living" nature of the AI orchestration.

## Colors
The palette is rooted in a "Deep Space" black foundation to maximize contrast and reduce eye strain during long sessions.
- **Primary (Electric Blue):** Used for primary actions, focus states, and active data streams.
- **Secondary (Neon Purple):** Signifies AI-generated content, logic branches, and orchestration nodes.
- **Cyber Green:** Indicates health, success, and active deployment states.
- **Accent Triggers:** Hot Pink and Warm Orange are reserved for critical errors and warnings respectively, cutting through the cool-toned UI.

Surface colors utilize a tiered system: `background_deep` for the application shell, `neutral_color_hex` for primary workspaces, and `surface_elevated` for floating panels and modals.

## Typography
Typography is split between human-readable UI elements and machine-readable data.
- **Inter** handles all structural UI, navigation, and body content. It is chosen for its exceptional legibility in dense interfaces.
- **JetBrains Mono** is the "functional" font, used for code blocks, terminal outputs, status labels, and metadata.

Hierarchy is maintained through weight and letter spacing rather than excessive size. Large displays (48px+) should only be used on landing or "Command Center" summary screens. For mobile, scale down `display-lg` to 32px.

## Layout & Spacing
The layout follows a **Hybrid Fluid-Modular** grid. The primary workspace is fluid, while sidebars (Navigation and Inspector) are fixed-width to ensure tool accessibility.
- **Grid:** A 12-column system is used for dashboard layouts.
- **Density:** High-density spacing (4px base unit) is used to accommodate complex data visualization.
- **Safe Areas:** Consistent 24px margins are applied to the outer edges of the application viewport.
- **Mobile Adaption:** Sidebars collapse into drawers; multi-column dashboard widgets stack vertically or convert into horizontal carousels.

## Elevation & Depth
Depth is created through a mix of **Tonal Layering** and **Glassmorphism**, avoiding traditional heavy shadows which feel dated in a futuristic context.
- **The "Glass" Layer:** Modals and dropdowns use a 12px backdrop blur with a 10% white border-top (inner stroke) to simulate a light-catching edge.
- **Inner Glows:** Active cards or focused inputs use a subtle 4px outer glow tinted with the primary blue color rather than a black shadow.
- **Stacking:**
  - `Level 0 (Base)`: Deep space black.
  - `Level 1 (Cards)`: Slightly lighter neutral with a 1px border.
  - `Level 2 (Popovers)`: Backdrop blur (20px) with 60% opacity background.

## Shapes
The shape language is **Soft-Technical**. We avoid the pill-shaped playfulness of consumer apps in favor of a precision-engineered look.
- **Primary UI Elements:** (Buttons, Inputs, Cards) use a 4px (0.25rem) radius.
- **Selection Markers:** Active states in the sidebar or tabs use sharp, 2px vertical lines on the left/bottom edge to indicate focus.
- **AI Nodes:** Visual graph nodes for orchestration may use a slightly softer 8px radius to differentiate them from the "frame" of the UI.

## Components
- **Buttons:** Low-profile, semi-transparent backgrounds with high-contrast text. "Primary" buttons use a solid Electric Blue with a subtle pulse animation on hover.
- **Inputs:** Minimalist bottom-border only or very thin 1px outlines. Focus states trigger a primary-colored "glow" trace around the perimeter.
- **Status Chips:** Small, mono-spaced text with a leading "indicator dot." The dot should have a CSS `box-shadow` to create a glowing LED effect (e.g., Green for `Online`).
- **Cards:** No shadows; instead, use a 1px border (`#ffffff10`) and a slight hover-state background shift.
- **Command Palette:** A centered, glassmorphic modal with an "always-on" input field and JetBrains Mono shortcuts (e.g., `⌘K`).
- **Graph Nodes:** Used for the orchestration view. These should be semi-transparent containers with connecting "poly-lines" that animate to show data flow direction.
---
name: Autonomous Recruitment Architecture
colors:
  surface: '#fcf8ff'
  surface-dim: '#dcd8e5'
  surface-bright: '#fcf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f5f2ff'
  surface-container: '#f0ecf9'
  surface-container-high: '#eae6f4'
  surface-container-highest: '#e4e1ee'
  on-surface: '#1b1b24'
  on-surface-variant: '#464555'
  inverse-surface: '#302f39'
  inverse-on-surface: '#f3effc'
  outline: '#777587'
  outline-variant: '#c7c4d8'
  surface-tint: '#4d44e3'
  primary: '#3525cd'
  on-primary: '#ffffff'
  primary-container: '#4f46e5'
  on-primary-container: '#dad7ff'
  inverse-primary: '#c3c0ff'
  secondary: '#4648d4'
  on-secondary: '#ffffff'
  secondary-container: '#6063ee'
  on-secondary-container: '#fffbff'
  tertiary: '#7e3000'
  on-tertiary: '#ffffff'
  tertiary-container: '#a44100'
  on-tertiary-container: '#ffd2be'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e2dfff'
  primary-fixed-dim: '#c3c0ff'
  on-primary-fixed: '#0f0069'
  on-primary-fixed-variant: '#3323cc'
  secondary-fixed: '#e1e0ff'
  secondary-fixed-dim: '#c0c1ff'
  on-secondary-fixed: '#07006c'
  on-secondary-fixed-variant: '#2f2ebe'
  tertiary-fixed: '#ffdbcc'
  tertiary-fixed-dim: '#ffb695'
  on-tertiary-fixed: '#351000'
  on-tertiary-fixed-variant: '#7b2f00'
  background: '#fcf8ff'
  on-background: '#1b1b24'
  surface-variant: '#e4e1ee'
  success-emerald: '#10B981'
  warning-amber: '#F59E0B'
  danger-rose: '#F43F5E'
  bg-surface: '#F8FAFC'
  border-subtle: '#E2E8F0'
  ai-intelligence-indigo: '#818CF8'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-caps:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
  code-data:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
  score-display:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '700'
    lineHeight: 24px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  container-max: 1440px
  gutter: 1.5rem
  margin-page: 2rem
  stack-sm: 0.5rem
  stack-md: 1rem
  stack-lg: 2rem
---

## Brand & Style
The design system is engineered for high-stakes enterprise recruitment, where speed must be balanced with ethical oversight. The brand personality is **Technical, Ethical, and Authoritative**, positioning the AI not as a black box, but as a transparent, reasoning-capable partner.

The visual style is **Corporate / Modern** with a focus on data density and clarity. It utilizes a "System-of-Record" aesthetic—relying on precise 1px borders, subtle functional elevations, and a rigorous adherence to a structured grid. The UI must feel like a high-performance command center, where "Human-in-the-Loop" checkpoints are visually distinct from automated processes to ensure the recruiter remains the ultimate decision-maker.

## Colors
This design system uses a logic-driven color palette. **Deep Indigo** is the primary anchor, conveying enterprise stability and professional rigor. **Slate Blue** acts as the interactive secondary, used for navigation and secondary actions.

Functional colors are critical for the AI pipeline:
- **Emerald** is reserved for high-scoring candidates and successful agent completions.
- **Amber** signals "Human-in-the-Loop" gates, requiring manual intervention or review.
- **Rose** is the high-priority "Bias Flag" or system error color, demanding immediate attention.
- **Neutral Grays** create a tiered surface system, using Clean White for primary cards and Slate Gray for the background environment to reduce eye strain in data-rich views.

## Typography
The system uses **Inter** for all primary UI elements to ensure maximum legibility and a modern, utilitarian feel. Typography is set with tight tracking and leading to accommodate the high density of information required in candidate comparison views.

A secondary font, **JetBrains Mono**, is introduced for "AI Reasoning" blocks and JSON metadata fields. This monospaced choice signals to the user that they are looking at "raw" system output or structured data, distinguishing it from human-authored prose.

- **Headlines:** Use tight letter-spacing (-0.02em) for a more technical, "locked-in" look.
- **Labels:** Small caps with increased letter spacing are used for table headers and metadata categories.
- **Mobile Adaptivity:** For small screens, `headline-lg` scales down to 24px to maintain layout integrity in the Pipeline View.

## Layout & Spacing
The layout follows a **Fixed Grid** philosophy for the main dashboard to ensure the 5-stage pipeline remains visible without horizontal scrolling on standard enterprise displays.

- **The Dashboard:** A 12-column grid with 24px gutters. The primary "Pipeline" view occupies a full-width container.
- **Kanban Columns:** The 5 agents (JD, Search, Assessment, Interview, Offer) are represented as five equal columns that reflow into a vertical stack on mobile devices.
- **The "Reasoning" Sidebar:** Contextual drawers and modals use a 400px fixed-width layout to surface AI insights (Strengths/Gaps) without obscuring the main candidate list.
- **Rhythm:** An 8px base unit governs all padding and margin, ensuring a mathematically consistent vertical rhythm.

## Elevation & Depth
Depth is conveyed through **Tonal Layers** and **Low-Contrast Outlines** rather than heavy shadows. This maintains a "flat-plus" professional aesthetic.

- **Base Layer:** `#F8FAFC` (Slate Gray) for the application background.
- **Surface Layer:** White (`#FFFFFF`) cards for candidate entries and agent status modules, using a 1px border of `#E2E8F0`.
- **Raised Layer:** Modals (e.g., `OfferModal`) use a 15% opacity Indigo tint in the backdrop blur and a soft, diffused shadow (12px blur, 4% opacity) to indicate temporary focus.
- **Intelligence Indicators:** NVIDIA NIM scores use a subtle inner glow or a 2px colored left-border to denote their "Live AI" status without breaking the flat design language.

## Shapes
The shape language is **Soft (0.25rem)**, emphasizing precision over playfulness. This subtle rounding provides a modern feel while maintaining the "technical" look of a professional tool.

- **Standard Elements:** Input fields, buttons, and small cards use a 4px (0.25rem) radius.
- **Containers:** Larger modules like the Kanban columns or the "Bias Check" panel use a 8px (0.5rem) radius.
- **Badges:** The `NimScoreBadge` is the only exception, using a **Pill-shaped** (full round) geometry to visually isolate numerical scores from the rectangular data around them.

## Components

### Buttons & Actions
- **Primary:** Solid `#4F46E5` with white text. 
- **Secondary:** Ghost style with `#E2E8F0` border and `#4F46E5` text.
- **AI-Trigger:** Gradient border (Indigo to Emerald) to distinguish buttons that initiate an AI agent process.

### AI Status Cards (`AgentStatusCard`)
Every agent card must display:
- **Status Indicator:** A pulsing dot for "In-Progress," a check for "Done," or an Amber gate icon for "Human Review."
- **Reasoning Area:** A background-tinted box using `code-data` typography to show the LLM's logic.
- **Safety Badge:** A persistent "Safety Guard" footer that turns Rose if a bias flag is triggered.

### NIM Score Badges
- **High (80-100):** Emerald background with white text.
- **Mid (50-79):** Indigo background with white text.
- **Low (0-49):** Slate background with white text.
- All badges include a small "spark" icon to denote NVIDIA NIM generation.

### Form Inputs & Gates
- **Human Gate:** A specific modal variant with a thick Amber header, designed to pause the automated pipeline. It must contain two clear actions: "Approve for Next Stage" or "Request Agent Re-run."
- **Standard Inputs:** 1px borders, turning Indigo on focus with a 2px outer ring.

### Lists & Tables
- **Candidate Row:** High-density rows with `body-sm` metadata. On hover, the row elevates slightly with a `#F1F5F9` background tint.
# MEZIE BRAND OS
## UI/UX FRONTEND DEVELOPMENT PLAN
### Rewritten to Match the Approved Dashboard Visual Direction

**Version:** 2.0  
**Product:** Mezie Brand OS  
**Product Type:** AI-powered Brand Engineering Harness  
**Primary Experience:** Premium dark-mode dashboard  
**Secondary Experiences:** Mobile PWA and Telegram agent interface  
**Design Reference:** Approved Mezie Brand OS dashboard images and user-flow visuals

---

# 1. FRONTEND PRODUCT VISION

Mezie Brand OS should feel like a premium brand command center built for one founder operating an entire personal-brand ecosystem.

The frontend must communicate:

- Intelligence
- Control
- Precision
- Premium craftsmanship
- Creative energy
- Brand consistency
- AI orchestration
- Data awareness
- Operational readiness

The experience should resemble a fusion of:

- Creative studio
- Editorial planning suite
- AI operating console
- Production management system
- Analytics platform
- Personal brand intelligence hub

It should not resemble:

- A generic project-management board
- A social scheduler clone
- A simple chatbot wrapper
- A brightly coloured creator app
- A cluttered enterprise admin panel

The dashboard must feel like:

> **A dark, elegant, gold-accented mission-control environment for building, operating, and growing the Mr. C. Mezie brand.**

---

# 2. APPROVED VISUAL DIRECTION

## 2.1 Core Visual Identity

The approved dashboard imagery establishes the following visual language:

### Primary Theme

- Deep black and navy-black canvas
- Charcoal and slate cards
- Warm gold highlights
- Soft blue, green, purple, and orange data accents
- Thin borders
- Compact data density
- Premium spacing
- Clear section hierarchy
- Subtle glow and shadow
- Technical but human interface

### Mood

- Executive
- Futuristic
- Calm
- High-performance
- Editorial
- Strategic
- Premium
- Trustworthy

### Design Character

The system should feel polished without appearing decorative.

The user should immediately understand:

- Where they are
- What needs attention
- What is in progress
- What the AI is doing
- What action comes next

---

# 3. DESIGN SYSTEM

# 3.1 Colour Tokens

## Brand Core

```css
--brand-black: #070A0E;
--brand-obsidian: #0B1016;
--brand-charcoal: #111821;
--brand-panel: #151E28;
--brand-panel-raised: #1A2530;
--brand-border: #263442;
--brand-gold: #F2B94B;
--brand-gold-deep: #B9862E;
--brand-cream: #F7F0E4;
--brand-white: #F8FAFC;
--brand-muted: #8C99A8;
--brand-subtle: #586675;
```

## Functional Colours

```css
--success: #28C76F;
--warning: #F5A524;
--danger: #EF5B5B;
--info: #4EA5FF;
--purple: #8B6CFF;
--cyan: #27D3C2;
--orange: #F58C45;
```

## Surface Hierarchy

```css
--surface-root: #070A0E;
--surface-sidebar: #0A0F15;
--surface-card: #111821;
--surface-card-hover: #16212C;
--surface-input: #0D141C;
--surface-modal: #131C26;
```

---

# 3.2 Typography

## Recommended Pairing

### Display and Section Titles

Use a strong modern sans-serif or editorial serif sparingly.

Recommended:

- Sora
- Manrope
- Inter Tight
- DM Sans
- Instrument Sans

### Interface Text

Use:

- Inter
- Manrope
- Geist Sans

## Type Scale

```css
--text-xs: 11px;
--text-sm: 12px;
--text-base: 14px;
--text-md: 16px;
--text-lg: 18px;
--text-xl: 22px;
--text-2xl: 28px;
--text-3xl: 36px;
```

## Typography Behaviour

- Uppercase micro-labels for categories
- Sentence case for actions and page titles
- Gold reserved for important highlights
- High-contrast white for key values
- Muted grey for secondary metadata
- Avoid oversized marketing-style text inside operational screens

---

# 3.3 Spacing and Grid

## Desktop Grid

- 12-column layout
- 24px page gutters
- 16px card gaps
- 24–32px section spacing
- Fixed sidebar width between 220px and 250px
- Main canvas should scale fluidly

## Card Padding

- Compact cards: 14–16px
- Standard cards: 18–20px
- Large workspaces: 24px

## Corner Radius

```css
--radius-sm: 8px;
--radius-md: 12px;
--radius-lg: 16px;
--radius-xl: 20px;
```

The visual reference uses mostly restrained rounded cards, not overly soft consumer-app shapes.

---

# 3.4 Borders, Shadows, and Glow

## Borders

- 1px solid muted blue-grey
- Use active gold borders sparingly
- Use colour-coded top or side accents for workflow status

## Shadows

- Soft, low-opacity
- No heavy floating-card shadows
- Focus on depth through contrast and borders

## Glow

Use subtle gold or blue glow only for:

- Primary actions
- Active navigation
- AI activity
- Important status
- Selected cards

---

# 4. GLOBAL APPLICATION SHELL

# 4.1 Desktop Shell

The approved images show a consistent desktop frame.

## Left Sidebar

The left sidebar is persistent.

### Sidebar Contents

- Mezie Brand OS logo
- Brand Engineering Harness subtitle
- Command Center
- Ideas Inbox
- Calendar
- Content Pipeline
- Script Studio
- Production Director
- Analytics
- Brand Intelligence
- Agent Console
- Asset Library
- Settings

### Sidebar Behaviour

- Fixed on desktop
- Collapsible into icon rail
- Active item highlighted with:
  - Soft dark-gold background
  - Gold icon
  - White label
- Inactive items remain muted
- Small status counters appear beside relevant items

Examples:

- Ideas Inbox: 12
- Scripts: 5
- Pending approvals: 3

---

# 4.2 Top Application Bar

The top bar should contain:

- Current page title
- Breadcrumb or short context
- Global search
- Notification icon
- Agent status indicator
- Founder profile
- Primary page action

Examples:

- New Idea
- New Content
- Generate Content Plan
- Save Script
- Export Report
- Run Research

The top bar should remain visually light and should not compete with the main content.

---

# 4.3 Right-Side Context Panels

Selected screens should include a right-side utility panel for:

- AI suggestions
- Content overview
- Calendar goals
- Script tools
- Agent status
- Analytics insights
- Review score
- Approval requirements

These panels should remain modular and collapsible.

---

# 5. CORE PAGE ARCHITECTURE

# 5.1 COMMAND CENTER

## Purpose

The Command Center is the primary home screen and should closely match the approved dashboard image.

## Layout

### Header

- Personalized greeting
- Small founder profile
- Primary CTA: New Idea

### Top KPI Row

Four or five compact metric cards:

- Ideas
- In Production
- Published
- Engagement
- Optional: Qualified Leads

Each metric card includes:

- Number
- Change indicator
- Small icon
- Mini chart or visual signal
- Status colour

### Main Grid

#### Today’s Plan

Checklist with time stamps:

- Research trending topics
- Script Builder Walk
- Record video
- Edit and publish Reel
- Daily review and analytics

#### Content Pipeline

Horizontal status bars:

- Ideation
- Scripting
- Production
- Editing
- Ready to Publish
- Published

#### Agent Status

- Brand Director Agent avatar
- Online indicator
- Current activity
- Current focus
- Open Agent Console button

### Lower Grid

#### Recent Activity

- Idea added
- Script generated
- Reel published
- Analytics updated

#### Upcoming Content

- Date
- Content title
- Platform icon
- Status

#### Optional Intelligence Brief

- Trending topic
- Recommended content angle
- Confidence score
- Research source count

## Development Components

```tsx
<DashboardHeader />
<MetricCard />
<TodayPlan />
<PipelineOverview />
<AgentStatusCard />
<ActivityFeed />
<UpcomingContent />
<IntelligenceBrief />
```

---

# 5.2 CONTENT CALENDAR

## Purpose

Provide a complete August–December planning environment.

## Layout

### Main Calendar

- Month view by default
- Week and agenda toggles
- Platform-coloured event cards
- Drag and drop
- Date hover states
- Selected content details

### Right Panel

#### Content Overview

- Total content
- Reels
- YouTube
- Carousels
- X threads
- Stories

#### Monthly Goals

- Post three Reels weekly
- Grow followers by target
- Publish YouTube videos
- Publish X threads
- Completion progress

### Top Actions

- Generate Content Plan
- New Content
- Filters
- Previous/next month
- Month selector

## Required Interactions

- Drag content between dates
- Duplicate content
- Open script
- Open production plan
- Filter by platform
- Filter by pillar
- Filter by status
- Show content density
- Warn about pillar imbalance

## Components

```tsx
<CalendarToolbar />
<MonthCalendar />
<ContentEventCard />
<CalendarFilters />
<ContentOverviewPanel />
<MonthlyGoalsPanel />
```

---

# 5.3 IDEAS INBOX

## Purpose

Capture and qualify raw content ideas.

## Layout

### Main List

Each idea row includes:

- Title
- Source
- Date
- Platform indicator
- Content pillar
- Priority score
- AI fit score
- Status

### Tabs

- All Ideas
- Captured
- Reviewed
- Approved
- Rejected

### Right Detail Panel

When an idea is selected:

- Full idea text
- Source
- Why it matters
- Potential series
- Platform fit
- CTA
- Score
- Generate Script button

## Primary Actions

- Capture Idea
- Research
- Convert to Brief
- Generate Script
- Reject
- Archive

## Components

```tsx
<IdeaList />
<IdeaRow />
<IdeaScore />
<IdeaDetailPanel />
<CaptureIdeaModal />
```

---

# 5.4 CREATOR BENCHMARK LAB

## Purpose

Analyze benchmark creators, content mechanics, hooks, and transferable patterns.

## Layout

### Creator Watchlist

Table or card list containing:

- Creator
- Platform
- Views
- Engagement rate
- Top hook
- Content style
- Relevance score

### Insight Panel

- Pattern observations
- Common hooks
- Production trends
- Style shifts
- Mezie adaptation opportunities

### Trend Score

Prominent circular score or gauge:

- Trend score
- Relevance
- Momentum
- Shelf life

### Tabs

- Creator Watchlist
- Content Analysis
- Hook Library
- Trends

## Components

```tsx
<CreatorTable />
<CreatorAvatar />
<CreatorPerformanceCell />
<InsightPanel />
<TrendGauge />
<BenchmarkTabs />
```

---

# 5.5 SCRIPT STUDIO

## Purpose

Provide an AI-assisted scriptwriting workspace.

## Layout

### Left Panel: Content Details

- Platform
- Content type
- Topic
- Tone
- Length
- Goal
- CTA

### Center Panel: AI Script Output

Structured script blocks:

- Hook
- Setup
- Value
- Example
- CTA

The script editor should support:

- Rich text
- Scene blocks
- Comments
- Version history
- Inline AI actions

### Right Panel: Script Tools

- Hook suggestions
- Platform adaptation
- CTA generator
- B-roll ideas
- Hashtag generator
- Save as template

### Top Actions

- New Script
- Save Script
- Regenerate
- Shorten
- Expand
- Change Hook

## Components

```tsx
<ScriptConfigurationPanel />
<ScriptEditor />
<ScriptSection />
<ScriptToolsPanel />
<VersionHistory />
<BrandAlignmentBadge />
```

---

# 5.6 PRODUCTION DIRECTOR

## Purpose

Turn approved scripts into production-ready video plans.

## Layout

### Tabs

- Shot List
- Scene Breakdown
- Equipment
- Shot Planner

### Main Table

Columns:

- Scene
- Shot type
- Visual
- Audio
- Notes
- Status

### Left Scene List

- Hook
- Setup
- Value
- Example
- CTA

### Right Checklist

- Script locked
- Shot list ready
- Location set
- Lighting ready
- Mic check
- B-roll planned

### Production Status

- Readiness score
- Completion progress
- Mark as Ready button

## Components

```tsx
<ProductionTabs />
<SceneList />
<ShotTable />
<ProductionChecklist />
<ReadinessMeter />
<MarkReadyButton />
```

---

# 5.7 ANALYTICS AND LEARNING

## Purpose

Show performance and convert metrics into strategic learning.

## Layout

### KPI Row

- Views
- Engagement
- Followers
- Average watch time

### Main Charts

- Views over time
- Content type performance
- Platform distribution
- Engagement comparison

### Lower Panels

#### Top Performing Content

- Rank
- Title
- Format
- Views

#### What We Learned

- Best performing format
- Best hook type
- Most effective CTA
- Consistency signal

### AI Insight Card

Use subtle brain or intelligence visual.

## Components

```tsx
<AnalyticsToolbar />
<KPICard />
<LineChart />
<DonutChart />
<TopContentTable />
<LearningInsightCard />
```

---

# 5.8 AGENT CONSOLE

## Purpose

Make the Brand Director Agent transparent and controllable.

## Layout

### Left Context Rail

- Memory status
- Current focus
- Loaded context
- Recent skills

### Main Conversation

- Founder messages
- Agent responses
- Research summaries
- Proposed actions
- Approval cards

### Header Actions

- Run Deep Research
- Change agent mode
- View memory
- View run history

### Agent Modes

- Assistant
- Planner
- Operator
- Autonomous Research

### Approval Cards

- Create scripts
- Add content to pipeline
- Update memory
- Use paid tools
- Schedule task

## Components

```tsx
<AgentHeader />
<MemoryStatus />
<AgentConversation />
<AgentMessage />
<ActionApprovalCard />
<AgentModeSelector />
<ResearchRunButton />
```

---

# 5.9 ASSET LIBRARY

## Purpose

Store all media and brand assets.

## Layout

### Tabs

- All
- Videos
- Images
- Audio
- Graphics
- Documents
- B-roll

### Asset Grid

Thumbnail cards with:

- File preview
- File name
- Type
- Date
- Project
- Usage count
- Status

### Actions

- Upload
- Filter
- Search
- Add tags
- Attach to content
- Archive

## Components

```tsx
<AssetToolbar />
<AssetGrid />
<AssetCard />
<AssetPreview />
<AssetMetadataPanel />
```

---

# 5.10 CONTENT PIPELINE

## Purpose

Manage the content lifecycle.

## Approved Columns

- Ideation
- Scripting
- In Production
- In Review
- Published

Optional expanded lifecycle:

- Ready to Publish
- Analytics Review
- Repurpose

## Card Contents

- Title
- Platform
- Due date
- Content pillar
- Owner
- Priority
- Status
- Thumbnail
- Script readiness

## Behaviours

- Drag and drop
- Multi-select
- Filter
- Sort
- Open details
- Quick status update

## Components

```tsx
<PipelineBoard />
<PipelineColumn />
<ContentCard />
<PipelineFilters />
<QuickStatusMenu />
```

---

# 5.11 HOOK LAB

## Purpose

Create and evaluate hooks.

## Layout

### Input Area

- Topic
- Idea
- Platform
- Generate Hooks button

### Hook List

Each hook shows:

- Text
- Score
- Hook type
- Platform fit
- Save action

### Right Analysis Panel

- Hook breakdown
- Pattern
- Emotion
- Curiosity
- Best use
- Recommended length

## Tabs

- Hook Generator
- Top Hooks
- By Platform
- Testing

## Components

```tsx
<HookPromptForm />
<HookResultList />
<HookScoreBadge />
<HookAnalysisPanel />
<SaveHookButton />
```

---

# 5.12 SETTINGS AND INTEGRATIONS

## Purpose

Manage connected tools, models, vaults, and heartbeat settings.

## Tabs

- Profile
- Brand Settings
- Integrations
- Team
- Vault Sync
- Agent Settings

## Integration List

- OpenAI API
- Telegram Bot
- YouTube
- Instagram
- X
- Google Drive
- Notion
- CCIS Memory System

Each row should show:

- Icon
- Connection status
- Manage button
- Last sync

## Agent Settings

- Daily heartbeat
- Trend research
- Content ideas
- Performance review
- Daily Telegram brief

## Components

```tsx
<SettingsTabs />
<IntegrationRow />
<ConnectionStatus />
<AgentSettingsPanel />
<ToggleField />
```

---

# 6. MOBILE PWA FRONTEND

The approved images show a mobile companion experience rather than a reduced desktop clone.

## Core Mobile Screens

- Home
- Calendar
- Ideas Inbox
- Script Studio
- Analytics
- Telegram companion

## Mobile Priority

Mobile should focus on:

- Capture
- Review
- Approval
- Daily tasks
- Script reading
- Quick performance
- Agent conversation

## Bottom Navigation

- Home
- Capture
- Calendar
- Content
- Agent

## Floating Action Button

Primary mobile action:

- Capture idea
- Record voice note
- Upload image
- Share link

## Mobile UI Principles

- One-column layouts
- Large touch targets
- Compact metrics
- Sticky action bars
- Swipeable cards
- Minimal tables
- Expandable details

---

# 7. TELEGRAM EXPERIENCE

Telegram should visually and functionally mirror the dashboard logic.

## Telegram Menu

- Idea
- Research
- Script
- Analyze
- Status
- Help

## Response Cards

Telegram responses should return:

- Idea count
- Hook options
- Script created
- Daily brief
- Dashboard link
- Approval request

## Dashboard Sync

Every Telegram action should create or update a dashboard object.

Examples:

```text
Telegram Idea
→ Ideas Inbox

Telegram Script Request
→ Script Studio

Telegram Research Link
→ Benchmark Lab

Telegram Approval
→ Pipeline Status Update
```

---

# 8. SHARED FRONTEND COMPONENT LIBRARY

## Navigation

- AppSidebar
- SidebarItem
- TopBar
- Breadcrumb
- MobileBottomNav
- CommandPalette

## Cards

- MetricCard
- StatusCard
- ContentCard
- AgentCard
- InsightCard
- AnalyticsCard
- GoalCard
- CreatorCard
- AssetCard

## Data Display

- DataTable
- MiniChart
- DonutChart
- LineChart
- ProgressBar
- ScoreGauge
- StatusBadge
- PlatformBadge

## Forms

- TextInput
- Select
- MultiSelect
- TextArea
- DatePicker
- TimePicker
- Toggle
- FileUploader
- VoiceRecorder

## AI Components

- AIStatusIndicator
- ModelBadge
- ConfidenceScore
- ContextLoadedPanel
- AgentActionCard
- ApprovalCard
- AIInlineAction

## Workflow

- KanbanBoard
- KanbanColumn
- DraggableCard
- WorkflowStepper
- Checklist
- Timeline
- ActivityFeed

## Content Creation

- ScriptEditor
- HookCard
- BriefBuilder
- ShotList
- SceneRow
- ProductionChecklist
- CaptionEditor
- ContentPreview

---

# 9. FRONTEND ROUTE STRUCTURE

```text
/
├── /dashboard
├── /ideas
├── /calendar
├── /pipeline
├── /scripts
│   ├── /new
│   └── /[scriptId]
├── /production
│   └── /[contentId]
├── /benchmarks
│   ├── /creators
│   ├── /content
│   ├── /hooks
│   └── /trends
├── /analytics
├── /brand
├── /agent
├── /assets
├── /proof
├── /settings
│   ├── /profile
│   ├── /brand
│   ├── /integrations
│   ├── /vault
│   └── /agent
└── /mobile
```

---

# 10. FRONTEND STATE MODEL

## Global State

- Current user
- Active brand
- Agent status
- Notifications
- Connected tools
- Theme
- Search
- Current date range

## Feature State

- Ideas
- Calendar
- Scripts
- Pipeline
- Assets
- Analytics
- Benchmarks
- Settings

## Recommended Tools

- TanStack Query for server state
- Zustand for light client state
- React Hook Form
- Zod
- DnD Kit
- Recharts
- TipTap
- Framer Motion
- Lucide icons

---

# 11. INTERACTION DESIGN

## Hover

- Subtle surface lift
- Border brightening
- Gold icon emphasis

## Selection

- Gold left border
- Brighter panel background
- Clear active state

## Loading

Use branded loaders:

- Gold progress line
- Pulsing AI status
- Skeleton cards
- “Brand Director is thinking” state

## Empty States

Empty states should guide action.

Example:

> No scripts yet. Turn one of your approved ideas into your first script.

## Success Feedback

- Small toast
- Status update
- Check animation
- Pipeline card movement

---

# 12. RESPONSIVE BREAKPOINTS

```css
--mobile: 0–639px;
--tablet: 640–1023px;
--desktop: 1024–1439px;
--wide: 1440px+;
```

## Desktop

- Full sidebar
- Multi-column layouts
- Data tables
- Persistent context panels

## Tablet

- Collapsible sidebar
- Two-column layouts
- Simplified analytics

## Mobile

- Bottom navigation
- One-column content
- Drawer-based filters
- Sticky action footer

---

# 13. ACCESSIBILITY

- WCAG AA contrast
- Keyboard navigation
- Visible focus states
- Semantic headings
- ARIA labels
- Captions and transcripts
- Colour-independent status communication
- 44px minimum mobile targets
- Reduced-motion mode

Gold should never be the only method of communicating status.

---

# 14. FRONTEND DEVELOPMENT PHASES

# Phase 1 — Design Foundation

Build:

- Tokens
- Typography
- Theme
- Sidebar
- Top bar
- Card system
- Buttons
- Badges
- Form controls
- Page shell

Deliverable:

> Approved Storybook component foundation

---

# Phase 2 — Core Dashboard

Build:

- Command Center
- KPI cards
- Today Plan
- Pipeline overview
- Agent status
- Activity feed
- Upcoming content

Deliverable:

> Fully responsive dashboard landing page

---

# Phase 3 — Content Planning

Build:

- Calendar
- Ideas Inbox
- Content Pipeline
- Content detail drawer
- Filters
- Drag and drop

Deliverable:

> Complete planning and orchestration workflow

---

# Phase 4 — Content Creation

Build:

- Script Studio
- Hook Lab
- Content brief
- Script tools
- Version history

Deliverable:

> AI-assisted content creation workspace

---

# Phase 5 — Production

Build:

- Production Director
- Shot list
- Scene breakdown
- Checklist
- Asset attachment
- Mobile shoot mode

Deliverable:

> Shoot-ready production workflow

---

# Phase 6 — Research and Intelligence

Build:

- Creator Benchmark Lab
- Creator profiles
- Content teardowns
- Trend score
- Insight panel

Deliverable:

> Creator and trend intelligence interface

---

# Phase 7 — Analytics

Build:

- KPI cards
- Line charts
- Donut charts
- Top content table
- Learning insights
- Experiment tracking

Deliverable:

> Performance and learning dashboard

---

# Phase 8 — Agent and Settings

Build:

- Agent Console
- Memory status
- Approval cards
- Integrations
- Heartbeat settings
- Vault sync

Deliverable:

> Transparent AI operations layer

---

# Phase 9 — Mobile PWA

Build:

- Mobile dashboard
- Capture
- Calendar
- Ideas
- Script review
- Analytics
- Agent chat

Deliverable:

> Installable mobile companion

---

# 15. FRONTEND ACCEPTANCE CRITERIA

The frontend is ready when:

- The dashboard visually matches the approved dark/gold product direction.
- All main screens share one consistent shell.
- The interface remains readable despite high information density.
- Key actions are always visible.
- Every major workflow is accessible within two clicks.
- Mobile capture takes less than 15 seconds.
- The content pipeline supports drag-and-drop.
- Scripts support versioning and AI actions.
- Agent actions and memory writes are transparent.
- Analytics produce clear recommendations.
- The entire application is responsive.
- The UI feels like a premium proprietary product, not a template.

---

# 16. FINAL FRONTEND DESIGN PRINCIPLE

> **Mezie Brand OS should make a complex personal-brand operation feel controlled, visible, intelligent, and executable from one premium command center.**

The interface should repeatedly reinforce:

> **See the possibility. Build the system. Become the evidence.**

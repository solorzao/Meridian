# Meridian UX Recommendations

## Current Flow Issues Identified

### 1. No Authentication Flow
The app jumps directly from landing page to dashboard with no sign-in, sign-up, or onboarding. This breaks the experience for new users who need context and for returning users who expect their data to persist.

### 2. Static Sidebar Navigation
The dashboard sidebar has no active-state indicator. Users cannot tell which page they are currently on. The sidebar is also not collapsible, which wastes space on smaller screens and when the main content needs focus (e.g., during a full-screen chart view).

### 3. No Onboarding or First-Run Experience
When a user arrives at the dashboard for the first time, all stat cards show "--" with no guidance. A first-run wizard or progressive disclosure pattern would significantly improve activation rates.

### 4. Missing Error and Loading States
None of the pages currently handle loading, error, or empty states in a structured way. Components should have skeleton loaders and graceful fallbacks.

### 5. No Mobile Navigation
The sidebar layout is desktop-only. On mobile viewports, the sidebar would either overflow or be inaccessible. A responsive drawer or bottom navigation pattern is needed.

---

## Recommended Improvements for Follow-Up Agent

### High Priority

- **Authentication pages**: Create `/login`, `/signup`, and `/forgot-password` pages using the Meridian brand palette. Consider a split-layout with branding on the left and form on the right.

- **Active nav state**: The sidebar needs a `usePathname()` hook (from `next/navigation`) to highlight the current route. The `meridian-nav-link-active` CSS class is already defined and ready to use.

- **Mobile sidebar**: Implement a slide-out drawer for mobile using a `Sheet` component or a custom solution with `useState` and CSS transforms. Add a hamburger button in a top bar that only appears at `md` breakpoint and below.

- **Skeleton loaders**: Create a reusable `<Skeleton />` component for stat cards, trade lists, and agent insights. Use `animate-pulse` with the navy card colors.

### Medium Priority

- **Onboarding wizard**: A 3-step modal after first login: (1) Set trading goals, (2) Connect broker or import CSV, (3) Choose AI agent personality. This should be a modal overlay, not a separate route.

- **Trade entry form**: The Journal page needs a modal or slide-over form for logging trades. Fields: ticker/pair, direction (long/short), entry price, exit price, quantity, date, strategy tag, notes, screenshot upload.

- **Agent chat interface**: The AI Agents page should be a chat-style interface with a message input at the bottom, conversation history, and a sidebar for selecting different agent "personalities" (risk analyst, pattern finder, journal reviewer).

- **Notification system**: Toast notifications for trade logging confirmations, agent responses, and system alerts. Use crimson for errors, steel blue for info, emerald for success.

### Lower Priority

- **Theme customization**: While the app is dark-mode only, consider allowing accent color customization (crimson vs. emerald vs. gold) for personalization.

- **Keyboard shortcuts**: Power traders expect keyboard shortcuts. `N` for new trade, `A` for agents, `/` for search. Add a command palette (Cmd+K) for quick navigation.

- **Data export**: CSV/PDF export for trade history and analytics reports.

---

## New Pages and Components to Create

### Pages
| Route | Purpose |
|---|---|
| `/login` | Authentication - sign in |
| `/signup` | Authentication - create account |
| `/dashboard/journal` | Trade journal with list/grid view |
| `/dashboard/journal/[id]` | Individual trade detail view |
| `/dashboard/analytics` | Performance charts and breakdowns |
| `/dashboard/agents` | AI agent chat interface |
| `/dashboard/agents/[agentId]` | Specific agent conversation |
| `/dashboard/settings` | User preferences, API keys, profile |

### Shared Components
| Component | Location | Purpose |
|---|---|---|
| `Sidebar` | `components/layout/Sidebar.tsx` | Extract sidebar into client component with active state |
| `StatCard` | `components/dashboard/StatCard.tsx` | Reusable metric card with accent bar |
| `EmptyState` | `components/ui/EmptyState.tsx` | Configurable empty state with icon, text, and CTA |
| `Skeleton` | `components/ui/Skeleton.tsx` | Loading placeholder |
| `Modal` | `components/ui/Modal.tsx` | Reusable modal with backdrop |
| `Toast` | `components/ui/Toast.tsx` | Notification toast system |
| `TradeForm` | `components/journal/TradeForm.tsx` | Trade entry/edit form |
| `ChatMessage` | `components/agents/ChatMessage.tsx` | Single chat bubble |
| `ChatInput` | `components/agents/ChatInput.tsx` | Message input with send button |

---

## Mobile Responsiveness Considerations

1. **Breakpoint strategy**: Use `sm` (640px) for single-column stacking, `md` (768px) for sidebar collapse, `lg` (1024px) for two-column layouts, `xl` (1280px) for full dashboard width.

2. **Sidebar**: Should collapse to a hamburger menu below `md`. Consider a bottom tab bar as an alternative for the 5 main nav items on mobile.

3. **Stat cards**: Already responsive (1 column on mobile, 2 on sm, 4 on lg). This pattern should be maintained across all grid layouts.

4. **Landing page**: Hero text sizes scale down correctly with the `text-5xl sm:text-6xl lg:text-7xl` pattern. Feature cards stack to single column. The CTA buttons stack vertically on mobile via `flex-col sm:flex-row`.

5. **Charts (future)**: Analytics charts should be full-width on mobile with horizontal scroll for wide data tables. Consider using a chart library that handles responsive resizing (recharts or visx).

6. **Touch targets**: All interactive elements should maintain a minimum 44x44px touch target on mobile. The nav links and buttons are already sized appropriately.

7. **Safe areas**: Add `env(safe-area-inset-*)` padding for devices with notches or rounded corners, particularly for the bottom navigation and sidebar.

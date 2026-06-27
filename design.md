# Design System: Neo-Brutalism Website for Travy

## 1. Design Goal

Travy should look like a modern neo-brutalism travel product: bold, direct, social, and quick to scan. The design should help a group answer "What should we actually do today?" without making the experience feel like a long travel form.

The system should be:

- Modern neo-brutalism: thick black borders, hard offset shadows, flat color blocks, and confident typography.
- Bold but not messy: strong visual personality with strict spacing, consistent components, and limited accent usage.
- Hackathon-polished: memorable, fast to build, easy to explain, and polished enough for demos.
- High contrast: black outlines, readable type, clear states, and strong CTA hierarchy.
- Component-driven: built from reusable primitives and Travy-specific cards/panels.
- Suitable for landing pages, dashboards, forms, cards, maps, itinerary flows, group decision screens, budget summaries, and interactive travel app flows.
- Social, energetic, travel-friendly, and practical: the UI should feel like planning with friends, not filling tax forms.

The final implementation should likely use Next.js, TypeScript, Tailwind CSS, shadcn/ui-style local components, lucide icons, and a small set of Travy-specific composition components.

## 2. Visual References Studied

| Repo / Reference | What to study from it | What we will borrow conceptually | What we will avoid |
|---|---|---|---|
| `Bridgetamana/neobrutal-ui` | Base UI-inspired primitives, `components/ui` organization, `cva` variants, `border-2`, `shadow-brutal`, focus utilities, docs/examples structure. | Local UI primitives named clearly, variant-driven components, tokenized shadows, focus helpers, simple card/header/content composition. | Copying source code, using a purple-first palette, or making every component too library-like for Travy. |
| `Logging-Studio/RetroUI` | React + Tailwind component API, Base UI usage, button/card variants, theme CSS variables, docs registry, playful but controlled components. | Button variants with pressed states, theme tokens for shadows/radius/colors, playful colors with restrained usage, compound card APIs. | Overly decorative backgrounds, too many theme presets, or visual noise that competes with travel data. |
| `marieooq/neo-brutalism-ui-library` | High-contrast Tailwind components, Button/Card/IconButton/Input patterns, Storybook examples, color props. | Simple prop APIs, color variants, strong hover/active states, visual examples for standalone components. | Ad hoc class assembly as the long-term pattern, broad rainbow component usage, large card heights where data needs density. |
| `homayounmmdy/neo-brutalism-dashboard-template` | Full dashboard layout, navigation, stats cards, content frames, dashboard hierarchy, `border-4`, `shadow-[6px_6px_0]`, utility classes. | Dashboard shell inspiration, metric cards, hard shadows for major panels, quick utility class constants. | Applying `border-4` everywhere, heavy dashboard chrome on mobile, or making charts/cards visually overwhelming. |
| `arhamkhnz/next-shadcn-admin-dashboard` | Next.js + shadcn architecture, sidebar system, route groups, theme presets, brutalist CSS variables, app shell organization. | `src/app`, `src/components/ui`, `src/components/layout`, `src/components/travy`, tokenized brutalist theme, structured sidebar data. | Enterprise dashboard density on landing pages, too many admin-only patterns, or hidden travel CTAs. |
| `ekmas/neobrutalism-components` | Visual component reference, shadcn-style registry, thick borders, hard shadows, pressed states, strong component catalog. | Treat as visual inspiration for UI primitives and reusable registry thinking. | Using it as the main dependency, copying implementation, or inheriting unneeded component breadth. |
| `matifandy8/NeoBrutalismCSS` | Lightweight CSS utilities, cards, buttons, badges, alerts, navigation, forms, modular SCSS organization. | Small reusable class constants in `lib/styles/neo.ts`, simple utility names, CSS-first tokens for shadows and state. | Depending on a global CSS library, losing TypeScript component structure, or using generic class names that conflict with Tailwind/shadcn. |
| `ComradeAERGO/Awesome-Neobrutalism` | Broader trend references, production examples, cheatsheets, color direction, UI kit references. | General principles: bold color, high contrast, flat shapes, playful confidence, simple geometry. | Treating the trend as an excuse for clutter, inaccessible contrast, or arbitrary colors. |

## 3. Core Design Principles

- Use thick black borders as the visual backbone.
- Use hard offset shadows, never soft blurred card shadows.
- Use flat color blocks instead of heavy gradients.
- Use bold typography for decisions, CTAs, and place titles.
- Use minimal gradients only for subtle page backgrounds if needed; never for primary controls.
- Use high contrast sections so landing and dashboard areas are easy to parse.
- Use simple geometric layouts: grids, split panes, stacked cards, timelines, and map panels.
- Make hierarchy obvious: primary plan CTA, key recommendation, price/time/distance/safety metadata, then supporting explanation.
- Design responsive first; mobile should feel like the primary planning mode.
- Keep the mood fun but usable.
- Avoid cluttered rainbow UI; use one dominant action color per screen and small semantic accents.
- Travel information must be scannable: location, price, time, distance, safety, open status, and group match should be readable at a glance.

## 4. Color System

| Token name | Hex value | Usage |
|---|---:|---|
| `background.cream` | `#FFF7E8` | Main app/landing background. Warm, travel-friendly base. |
| `background.paper` | `#FFFFFF` | Cards, forms, dialogs, dashboard panels. |
| `background.ink` | `#111111` | Dark footer, inverted CTA bands, high-emphasis labels. |
| `background.sunwash` | `#FFEFB8` | Highlight bands, "today plan" areas, empty states. |
| `primary.yellow` | `#FFD84D` | Main CTAs, "Plan My Day", current plan highlights. |
| `primary.yellowHover` | `#FFC928` | Hover state for primary yellow controls. |
| `accent.blue` | `#4DA3FF` | Maps, routes, discovery, distance markers. |
| `accent.pink` | `#FF70B8` | Group energy, votes, social prompts, friend activity. |
| `accent.mint` | `#7CF7B3` | Safe, confirmed, budget-friendly, saved success states. |
| `accent.orange` | `#FF9F43` | Food, markets, events, activity highlights. |
| `accent.lavender` | `#B9A7FF` | AI assistant, smart recommendations, explanation panels. |
| `semantic.success` | `#3EE37A` | Confirmed plans, open places, safe routes, saved states. |
| `semantic.warning` | `#FFB020` | Budget caution, closing soon, crowded, time risk. |
| `semantic.danger` | `#FF4D4D` | Destructive actions, unsafe route warnings, closed states. |
| `semantic.info` | `#38BDF8` | Helpful tips, map hints, travel mode guidance. |
| `text.primary` | `#111111` | Main text and headings. |
| `text.secondary` | `#3F3F46` | Body copy and secondary metadata. |
| `text.muted` | `#71717A` | Helper text, captions, tertiary details. |
| `text.inverse` | `#FFFFFF` | Text on black or saturated dark panels. |
| `border.black` | `#000000` | Default border for all neo components. |
| `shadow.black` | `#000000` | Offset shadows. |
| `surface.disabled` | `#D4D4D8` | Disabled controls and inactive chips. |

Tailwind-friendly names should map to `travyCream`, `travyPaper`, `travyInk`, `travyYellow`, `travyBlue`, `travyPink`, `travyMint`, `travyOrange`, `travyLavender`, `travyDanger`, `travyWarning`, and `travyInfo`.

Color usage rule: every screen gets one main accent plus semantic state colors. Example: the plan dashboard may use yellow for decisions, blue for map/routes, mint for confirmed/safe, and red only for real warnings.

## 5. Typography

Recommended font stack:

- Headings: `Public Sans`, `Inter`, or `Geist Sans` with `font-black` or `font-extrabold`.
- Body: `Inter`, `Public Sans`, or `Geist Sans` with strong readability.
- Metadata: `Geist Mono`, `IBM Plex Mono`, or a system monospace for prices, time, distance, scores, and compact stats.

Type rules:

- Heading style: bold, compact, high contrast. Example: `text-4xl md:text-6xl font-black leading-[0.95] tracking-normal`.
- Body style: clear and calm. Example: `text-base md:text-lg leading-7 text-zinc-800`.
- Button text style: short, bold, no vague labels. Example: `text-sm md:text-base font-black uppercase tracking-normal`.
- Badge text style: compact and readable. Example: `text-xs font-black uppercase tracking-normal`.
- Dashboard number style: monospace or bold sans. Example: `font-mono text-3xl font-black tabular-nums`.
- Trip card title style: clear two-line max. Example: `text-xl font-black leading-tight line-clamp-2`.
- Price/time/distance label style: monospace metadata. Example: `font-mono text-xs font-bold uppercase text-zinc-700`.

Do not use negative letter spacing. Do not scale type with viewport width. On compact cards, prefer tighter component layout over huge text.

## 6. Spacing and Layout

Global layout:

- Page max width: `max-w-7xl` for landing content, `max-w-[1440px]` for app dashboards.
- Narrow content: `max-w-3xl` for text-heavy explanations.
- Section spacing: `py-16 md:py-24` for landing sections; `p-4 md:p-6` for app shells.
- Card padding: `p-4` for compact cards, `p-5 md:p-6` for feature cards and panels.
- Gap scale: `gap-3` for metadata, `gap-4` for card grids, `gap-6` for dashboard panels, `gap-8` for landing sections.

Layout examples:

- Landing hero layout: full-width band with off-white background, bold left-aligned headline, CTA row, and a large interactive-looking dashboard/map preview. On mobile, stack headline, controls, and preview.
- Feature grid: `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4`, each feature card with one accent block and one icon.
- Dashboard panel grid: `grid grid-cols-1 xl:grid-cols-[280px_1fr_360px] gap-4`, with sidebar, main recommendations, and right summary panel.
- Form layout: labels above inputs, `grid grid-cols-1 md:grid-cols-2 gap-4`, full-width CTA at mobile bottom.
- Navigation layout: sticky landing navbar; app sidebar on desktop; bottom tab or sheet drawer on mobile.
- Trip suggestion grid: `grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4`, with stable card heights and visible metadata row.
- Map + itinerary split layout: desktop `grid-cols-[1.15fr_0.85fr]`, mobile map first if planning location, itinerary first if reviewing a generated plan.
- Group preference layout: horizontal chips on mobile with wrap, panel grid on desktop.
- Budget summary layout: metric cards at top, category breakdown below, warnings inline with readable text.

Responsive rules:

- Mobile controls must have at least `44px` height.
- Cards should not rely on hover-only actions.
- Long place names should clamp to two lines.
- Map panels need a fixed min-height: `min-h-[320px] md:min-h-[520px]`.
- Dashboard sidebars collapse into a sheet or bottom navigation below `lg`.

## 7. Border and Shadow System

Base styles:

- Standard component: `border-2 border-black rounded-[6px]`.
- Strong panel: `border-4 border-black rounded-[8px]`.
- Small shadow: `shadow-[2px_2px_0px_#000]`.
- Medium shadow: `shadow-[4px_4px_0px_#000]`.
- Large shadow: `shadow-[6px_6px_0px_#000]`.
- Hero/display shadow: `shadow-[10px_10px_0px_#000]`, used rarely.
- Pressed/active state: `active:translate-x-1 active:translate-y-1 active:shadow-none`.
- Hover lift: `hover:-translate-x-0.5 hover:-translate-y-0.5 hover:shadow-[6px_6px_0px_#000]` for cards that are clickable.

Usage:

- Place cards: `border-2`, medium shadow, hover lift only if clickable.
- Itinerary cards: `border-2`, small or medium shadow, no dramatic hover if reorderable.
- Budget cards: `border-2`, medium shadow, mint/yellow/orange semantic fill based on state.
- Map panels: `border-4`, large shadow, blue header strip.
- AI recommendation panels: `border-2`, medium shadow, lavender fill or lavender header.
- Safety/Guardian Route panels: `border-4` when warning-critical, mint fill when safe, red fill only for unsafe/closed/avoid warnings.

Shadows should always point down-right. Do not mix soft drop shadows into the neo-brutalism layer.

## 8. Component System

All reusable components should support `className`, use `React.forwardRef` where appropriate, use `cva` for variants, and keep accessibility built in. UI primitives belong in `components/ui`; layout pieces in `components/layout`; Travy-specific components in `components/travy`.

| Component | Purpose | Visual style | Props to support | Variants | Tailwind styling notes | Accessibility requirements |
|---|---|---|---|---|---|---|
| `NeoButton` | Primary action primitive. | Thick border, bold text, hard shadow, pressed state. | `variant`, `size`, `loading`, `leftIcon`, `rightIcon`, `asChild`, `disabled`. | `primary`, `secondary`, `accent`, `danger`, `ghost`, `icon`, `cta`. | Base: `inline-flex items-center justify-center border-2 border-black font-black shadow-[4px_4px_0_#000]`. | Real `button` behavior, visible focus, loading label, disabled state. |
| `NeoCard` | General framed content container. | White or colored block, black border, offset shadow. | `variant`, `interactive`, `tone`, `asChild`. | `default`, `feature`, `dashboard`, `alert`, `empty`, `flat`. | Use compound `Header`, `Title`, `Content`, `Footer`. | If clickable, expose as link/button with name. |
| `NeoInput` | Text input primitive. | White fill, black border, strong focus ring. | `label`, `error`, `helperText`, `leftIcon`, `rightSlot`. | `default`, `error`, `success`. | `h-11 border-2 border-black px-3 font-bold focus:ring-4`. | Associated label, `aria-invalid`, `aria-describedby`. |
| `NeoTextarea` | Multi-line notes/preferences. | Same as input, larger min height. | `label`, `error`, `helperText`, `rows`. | `default`, `error`, `success`. | `min-h-28 resize-y border-2 border-black`. | Label and error semantics. |
| `NeoSelect` | Option selector. | Button-like trigger with black border. | `label`, `options`, `value`, `placeholder`, `error`. | `default`, `compact`, `filter`. | Use shadcn/Base UI select pattern with brutal trigger. | Keyboard navigation and `aria-expanded`. |
| `NeoBadge` | Metadata chip. | Small bold pill/rectangle with border. | `tone`, `size`, `icon`, `children`. | `price`, `time`, `distance`, `safe`, `warning`, `social`, `ai`. | Prefer `rounded-[4px]`, `border-2`, mono text for stats. | Text must explain state, not color alone. |
| `NeoNavbar` | Landing navigation. | Sticky white/cream bar, black bottom border. | `links`, `cta`, `logo`, `mobileMenu`. | `landing`, `appTopbar`. | `border-b-2 border-black bg-travyPaper`. | Keyboard menu, current page state. |
| `NeoSidebar` | App dashboard navigation. | Left rail with border-right and active blocks. | `items`, `collapsed`, `user`, `activePath`. | `expanded`, `collapsed`, `mobileSheet`. | `w-64 border-r-4 border-black bg-travyCream`. | Landmarks, focus trapping in mobile sheet. |
| `NeoModal` | Dialogs and decision confirmations. | Center panel with large shadow and colored header. | `open`, `onOpenChange`, `title`, `description`, `footer`. | `default`, `danger`, `decision`. | Use shadcn dialog internals with brutal panel. | ARIA dialog semantics, escape close. |
| `NeoTabs` | Switch between plan/explore/saved, etc. | Segmented tabs with active color block. | `tabs`, `value`, `onValueChange`. | `default`, `boxed`, `dashboard`. | Active: yellow or blue fill, black border. | Roving keyboard focus and tabpanel labels. |
| `NeoToast` | Feedback after save/add/split. | Small card with border and shadow. | `title`, `description`, `tone`, `action`. | `success`, `warning`, `danger`, `info`. | Bottom-right desktop, bottom mobile. | Live region and dismiss button. |
| `NeoTooltip` | Helper labels for icons/stat meanings. | Tiny bordered popover. | `content`, `children`, `side`. | `default`, `inverted`. | `border-2 border-black bg-black text-white`. | Trigger accessible by keyboard. |
| `NeoDashboardPanel` | Dashboard section wrapper. | Strong panel with header strip. | `title`, `action`, `tone`, `children`. | `default`, `map`, `ai`, `safety`. | `border-4 shadow-[6px_6px_0_#000]`. | Header hierarchy must be logical. |
| `NeoMetricCard` | Budget/time/group match stats. | Compact card with large stat. | `label`, `value`, `delta`, `tone`, `icon`. | `budget`, `time`, `distance`, `match`, `safety`. | Monospace `tabular-nums`; stable height. | Include text labels for trend/status. |
| `NeoFeatureCard` | Landing page feature. | Color header/icon block, white content. | `title`, `description`, `icon`, `tone`. | `yellow`, `blue`, `pink`, `mint`, `lavender`. | Avoid nested cards. | Decorative icons hidden from screen readers. |
| `NeoSection` | Landing section wrapper. | Full-width band with constrained inner content. | `tone`, `eyebrow`, `title`, `description`. | `cream`, `paper`, `yellow`, `ink`. | Sections are not floating cards. | Proper heading level. |
| `NeoHero` | Landing first viewport. | Big type, CTA row, dashboard/map preview. | `headline`, `subcopy`, `primaryCta`, `secondaryCta`, `preview`. | `landing`. | Brand/product must be first-viewport signal. | H1 only once. |
| `NeoMapPanel` | Map preview and route context. | Blue-tinted panel, thick border, route badges. | `places`, `route`, `selectedPlace`, `legend`, `actions`. | `preview`, `interactive`, `compact`. | Stable min height; metadata overlay must not block map. | Text alternatives for warnings and route status. |
| `NeoChartPanel` | Budget/time/group charts. | Dashboard panel with simple high-contrast chart. | `title`, `data`, `legend`, `tone`. | `budget`, `time`, `votes`. | Use flat chart colors from palette. | Chart values must also exist as text/table. |
| `NeoPlaceCard` | Recommended place result. | Scannable travel card with image/color header. | `name`, `category`, `cost`, `distance`, `time`, `status`, `match`, `safety`, `actions`. | `default`, `selected`, `saved`, `warning`. | Metadata grid visible before description. | CTA labels explicit; open/closed text included. |
| `NeoTripCard` | Saved/current trip summary. | Larger card with plan title and participants. | `title`, `date`, `budget`, `people`, `stops`, `status`, `actions`. | `today`, `saved`, `shared`, `draft`. | Yellow for today, mint for confirmed. | Participant avatars need labels. |
| `NeoBudgetBadge` | Cost marker. | Mono chip with semantic tone. | `amount`, `level`, `currency`, `label`. | `free`, `cheap`, `moderate`, `expensive`, `overBudget`. | Use mint/yellow/orange/red sequence. | Include human-readable budget label. |
| `NeoRouteCard` | Route option summary. | Blue route block with time/safety/cost. | `mode`, `duration`, `distance`, `cost`, `safety`, `steps`. | `walking`, `transit`, `rideshare`, `safer`. | Keep route warnings inline. | Route warnings not icon-only. |
| `NeoGroupPreferenceCard` | Group mood/budget/preference voter. | Pink/social card with vote chips. | `person`, `mood`, `budget`, `interests`, `vote`, `status`. | `active`, `waiting`, `matched`. | Avatar + chips + status. | Controls reachable by keyboard. |
| `NeoItineraryTimeline` | Ordered plan for the day. | Vertical timeline with numbered stops. | `items`, `activeId`, `reorderable`, `onReorder`. | `compact`, `detailed`, `editable`. | Stable rows; drag handle icon button. | Reordering must have keyboard fallback. |
| `NeoSafetyPanel` | Guardian Route/safety summary. | Mint safe state or red warning state with clear text. | `score`, `summary`, `warnings`, `route`, `actions`. | `safe`, `caution`, `danger`. | Use red sparingly for true risk. | Warnings must be readable text. |

## 9. Button Rules

Variants:

- Primary: yellow fill, black text, medium shadow. Use for the main decision action.
- Secondary: white fill, black text, medium shadow. Use for supporting actions.
- Accent: blue, pink, mint, orange, or lavender fill based on context.
- Danger: red fill, black or white text depending contrast. Use only for destructive or unsafe states.
- Ghost: no shadow, transparent or cream fill, black border optional. Use inside dense nav/toolbars.
- Icon: square `h-10 w-10`, lucide icon, tooltip when meaning is not obvious.
- Large CTA: `h-14 px-8 text-lg border-4 shadow-[6px_6px_0_#000]`.

Travy-specific examples:

- `Plan My Day`: primary large CTA, yellow fill, spark/map icon optional.
- `Add to Trip`: secondary or mint when selected.
- `Split Cost`: mint or orange depending context.
- `View Route`: blue accent.
- `Safer Route`: mint if recommended, red if responding to risk.
- `Save Place`: secondary with bookmark icon.
- `Ask Travy`: lavender accent with assistant icon.

Behavior:

- Hover: slight movement and stronger/clearer shadow, or `hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-[2px_2px_0_#000]`.
- Active: pressed button moves down-right and removes shadow.
- Disabled: gray fill, muted text, no shadow movement, `cursor-not-allowed`.
- Loading: keep width stable, show spinner/icon plus label such as `Planning...`.
- Icon placement: left icon for action identity, right icon for movement/next. Icon-only buttons need accessible labels and tooltips.

## 10. Card Rules

Card variants:

- Default card: white fill, `border-2`, medium shadow, `p-4`.
- Feature card: accent header or icon block, white body, one key message.
- Dashboard card: compact, stable height, stat-first hierarchy.
- Alert card: warning/danger/success tone with readable text, not icon-only.
- Pricing card: budget comparison, visible total, per-person estimate, and "over/under budget" status.
- Map/location card: blue or white card with location metadata and route CTA.
- Empty state card: cream/yellow fill with one action; no long paragraph.
- Place recommendation card: place title, category, cost, distance, time, open/closed, group match, safety, CTA.
- Itinerary card: stop number, title, time, duration, transit mode, notes, remove/reorder action.
- Group decision card: person/group preference, vote state, match contribution.
- Budget summary card: total, per-person, remaining, category breakdown, warning if needed.
- Guardian Route / safety card: route comfort, safer alternative, warnings, and "Safer Route" CTA.

Every travel card should expose these details where relevant:

- Place name
- Category
- Estimated cost
- Distance
- Time required
- Open/closed status
- Group match score
- Safety/comfort note
- CTA action

Descriptions should be short. Metadata should be chips, rows, or compact stat blocks, not buried in prose.

## 11. Forms and Inputs

Input style:

- `border-2 border-black bg-white rounded-[6px] h-11 px-3 font-bold shadow-[2px_2px_0_#000]`.
- Focus ring: `focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-travyBlue`.
- Labels: `text-sm font-black uppercase`.
- Helper text: `text-sm text-zinc-700`.
- Error: red border or red helper panel, `aria-invalid=true`.
- Success: mint border/helper when a location or preference is confirmed.
- Required fields: label includes visible `Required`; do not rely on asterisk only.
- Mobile: one field per row, large tap targets, sticky final CTA for long planning forms.

Travy form examples:

- Starting location input: place/search icon, location permission helper, selected place chip.
- Budget input: currency prefix, per-person toggle, quick chips like `Free`, `$`, `$$`.
- Group size input: stepper or segmented control, not a tiny number field.
- Mood selector: chips such as `Chill`, `Hungry`, `Adventure`, `Culture`, `Night out`.
- Time available selector: segmented buttons like `1 hr`, `2-3 hrs`, `Half day`, `All day`.
- Food/activity preference selector: multi-select chips with clear selected state.
- Travel mode selector: walking, transit, rideshare, driving, accessible route.
- Safety preference toggle: clear on/off label such as `Prefer well-lit routes`.

## 12. Navigation

Landing page navbar:

- Sticky top, cream or white fill, `border-b-2 border-black`.
- Logo left: `Travy` as bold text or compact mark.
- Links center/right: Product, How it works, Safety, Budget, Demo.
- CTA right: `Plan My Day` yellow button.
- Mobile: menu icon button opens a bordered sheet.

App dashboard sidebar:

- Desktop left sidebar with groups and icons.
- Active item uses yellow/blue fill with black border.
- User profile block at bottom with avatar, name, and settings action.
- Collapsed state can show icon-only nav with tooltips.

Mobile navigation:

- Use bottom nav for high-frequency sections or a sheet for full navigation.
- Keep `Plan` as the most prominent item.

Future Travy sections:

- Home
- Plan
- Explore
- Trips
- Groups
- Budget
- Map
- Safety
- Saved
- Settings

## 13. Landing Page Design

Hero section:

- Layout: full-width cream band with constrained content. H1 should foreground `Travy` and the question "What should we actually do today?"
- Component usage: `NeoHero`, `NeoButton`, `NeoMapPanel`, `NeoPlaceCard` preview.
- Color usage: yellow primary CTA, blue route/map accents, pink social chips.
- Responsive behavior: stack content; keep CTA visible before preview on mobile.

Problem section:

- Layout: three or four blunt cards showing group indecision, budget mismatch, too many tabs, and safety/time uncertainty.
- Component usage: `NeoSection`, `NeoFeatureCard`.
- Color usage: paper cards with red/orange warning accents.
- Responsive behavior: single column on mobile.

Feature section:

- Layout: grid of feature cards.
- Component usage: `NeoFeatureCard`.
- Color usage: each feature gets a restrained accent: budget mint, maps blue, group pink, AI lavender, food orange, today yellow.
- Responsive behavior: `1 -> 2 -> 3` columns.

How it works:

- Layout: numbered steps with hard-bordered timeline.
- Component usage: `NeoItineraryTimeline` in preview mode.
- Color usage: yellow numbers, white cards.
- Responsive behavior: vertical timeline on mobile, horizontal/zigzag on desktop.

Dashboard preview:

- Layout: large neo dashboard mock panel with map, recommendations, group votes, and budget summary.
- Component usage: `NeoDashboardPanel`, `NeoMapPanel`, `NeoMetricCard`, `NeoPlaceCard`.
- Color usage: cream background, blue map panel, yellow active plan, mint safe state.
- Responsive behavior: crop less important side panels on mobile; do not make text unreadable.

Social proof / impact section:

- Layout: bold stats such as `2 min to decide`, `3 budgets balanced`, `Safer route found`.
- Component usage: `NeoMetricCard`.
- Color usage: high-contrast alternating cards.
- Responsive behavior: two-column mobile if space allows, otherwise one-column.

Final CTA:

- Layout: full-width yellow or black band with direct CTA.
- Component usage: `NeoSection`, `NeoButton`.
- Color usage: yellow primary, black border top/bottom.
- Responsive behavior: CTA full-width on mobile.

Footer:

- Layout: dark or paper footer with simple links.
- Component usage: `NeoNavbar` footer variant or plain layout.
- Color usage: black background with white text or cream with top border.
- Responsive behavior: stacked link groups.

Landing messaging should repeatedly reinforce group travel planning, budget-aware suggestions, local discovery, map-based planning, safer route suggestions, and fast decision-making for friends, students, families, and tourists.

## 14. Dashboard/App Design

Main app shell:

- Desktop: sidebar, topbar, main content, optional right context panel.
- Mobile: topbar, primary content, bottom nav or planning action bar.
- Use `NeoSidebar`, `NeoNavbar` app topbar, `NeoDashboardPanel`, and Travy-specific cards.

Dashboard areas:

- Today's plan: primary yellow panel with the current recommendation and CTA.
- Recommended places: grid/list of `NeoPlaceCard` results.
- Group preferences: pink/social panel with current moods, budgets, and votes.
- Budget remaining: metric card plus breakdown chart.
- Map preview: blue `NeoMapPanel` with selected stops.
- Route summary: `NeoRouteCard` list for walking/transit/rideshare.
- Safety/Guardian Route panel: `NeoSafetyPanel` with readable status and safer alternative.
- Saved trips: `NeoTripCard` list.
- Recent searches: compact list with quick replay action.
- AI explanation panel: lavender card explaining why Travy suggested the plan.
- Cost breakdown panel: per-person and total cost with warnings.
- Itinerary timeline: ordered `NeoItineraryTimeline` with edit/reorder states.

States:

- Empty states: one-line explanation plus one action.
- Loading states: skeleton cards with brutal borders; do not flash layout.
- Error states: red alert card with retry action and readable reason.
- Offline/degraded states: warning card; preserve any cached/saved trip data.

Use dashboard inspiration from neo-brutalism dashboard layouts, but keep Travy lighter than a finance/admin tool. The product should feel like planning a day out, not managing a database.

## 15. Animation and Interaction

Keep animations simple and fast:

- Button press: translate down-right and remove shadow.
- Card hover lift: small movement only for clickable cards.
- Tab transitions: instant or `150ms`; no slow sliding.
- Toast entrance: quick bottom slide/fade.
- Modal entrance: small scale/translate, under `200ms`.
- Loading skeleton: subtle pulse or static blocks for reduced motion.
- Map panel hover: highlight selected marker/card pairing.
- Itinerary reorder feedback: clear drag handle, insertion line, and stable card sizes.

Animations should not make the app feel slow. Respect `prefers-reduced-motion`.

## 16. Accessibility Rules

- Keyboard focus states must be visible and high contrast.
- Maintain WCAG-friendly contrast, especially on yellow, mint, pink, and lavender fills.
- Use ARIA semantics for dialogs, tooltips, tabs, sheets, toasts, and menus.
- Buttons need clear accessible labels, especially icon buttons.
- Every form input needs a real label.
- Touch targets should be at least `44px`.
- Support reduced motion by disabling nonessential transitions.
- Map panels must not rely only on color; route status needs text, patterns, or labels.
- Price, safety, and route warnings must include readable text labels, not just icons.
- Do not hide critical travel details behind hover interactions.
- Avatars and group votes need accessible names.
- Charts should include visible values or a text/table equivalent.

## 17. Tailwind Implementation Notes

Suggested Tailwind theme tokens:

```ts
colors: {
  travyCream: "#FFF7E8",
  travyPaper: "#FFFFFF",
  travyInk: "#111111",
  travyYellow: "#FFD84D",
  travyYellowHover: "#FFC928",
  travyBlue: "#4DA3FF",
  travyPink: "#FF70B8",
  travyMint: "#7CF7B3",
  travyOrange: "#FF9F43",
  travyLavender: "#B9A7FF",
  travyDanger: "#FF4D4D",
  travyWarning: "#FFB020",
  travyInfo: "#38BDF8"
}
boxShadow: {
  neoSm: "2px 2px 0px #000",
  neo: "4px 4px 0px #000",
  neoLg: "6px 6px 0px #000",
  neoXl: "10px 10px 0px #000"
}
borderRadius: {
  neo: "6px",
  neoLg: "8px"
}
```

Suggested utility class constants in `lib/styles/neo.ts`:

```ts
export const neoBase = "border-2 border-black rounded-[6px] bg-white";
export const neoShadow = "shadow-[4px_4px_0px_#000]";
export const neoShadowLg = "shadow-[6px_6px_0px_#000]";
export const neoPress =
  "transition-all active:translate-x-1 active:translate-y-1 active:shadow-none";
export const neoFocus =
  "focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-travyBlue";
```

Suggested folder structure:

- `components/ui/neo-button.tsx`
- `components/ui/neo-card.tsx`
- `components/ui/neo-input.tsx`
- `components/layout/neo-navbar.tsx`
- `components/layout/neo-sidebar.tsx`
- `components/travy/neo-place-card.tsx`
- `components/travy/neo-trip-card.tsx`
- `components/travy/neo-map-panel.tsx`
- `components/travy/neo-route-card.tsx`
- `components/travy/neo-budget-badge.tsx`
- `components/travy/neo-itinerary-timeline.tsx`
- `components/travy/neo-safety-panel.tsx`
- `lib/styles/neo.ts`
- `app/globals.css`

Do not create these files until implementation begins. Start with `design.md`, then build primitives, then Travy-specific components, then pages.

## 18. Do and Don't List

Do:

- Use thick borders consistently.
- Use hard shadows consistently.
- Keep layouts clean.
- Use color blocks intentionally.
- Reuse components.
- Make mobile responsive.
- Make travel cards scannable.
- Keep budget, time, distance, and safety information visible.
- Use playful design without hurting usability.
- Keep primary decisions obvious.
- Use icons as support, not as the only explanation.
- Build variants with predictable names and limited choices.

Don't:

- Use random colors everywhere.
- Overuse gradients.
- Make every card a different style.
- Mix too many border radiuses.
- Use weak gray borders.
- Create inaccessible contrast.
- Copy entire repo code blindly.
- Hide important travel details inside long paragraphs.
- Make map/dashboard screens visually overwhelming.
- Use hover-only actions for mobile-critical flows.
- Turn the landing page into a generic marketing template.
- Make Travy feel like a boring form instead of a fast social planning assistant.

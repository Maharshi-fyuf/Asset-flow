# Product Requirements Document (PRD) - AssetFlow

## 1. Introduction & Goal
**AssetFlow** is an Enterprise Asset & Resource Management System designed to consolidate physical asset lifecycle tracking, maintenance reporting, resource bookings, and auditing into a single administrative portal.

This PRD outlines the scope, user personas, layout components, and functional requirements for the **Frontend & Dashboard Interface**. The development objective is to build a premium, responsive, and highly interactive user experience with complete client-side simulation (Mock APIs) prior to final backend integration.

---

## 2. Target Roles & User Access Matrix
The frontend must tailor views and permissions dynamically based on the active user role:

| Role | Core Responsibilities | Dashboard Access Level | Key UI Modules Accessed |
|---|---|---|---|
| **Admin** | Organization setup, overall monitoring, compliance. | Full Global Overview | Settings, Employee/Dept Management, All Reports |
| **Asset Manager** | Asset registration, request approvals, maintenance tracking. | Asset & Ops Performance | Asset CRUD, Approval Queues, Maintenance, Audits |
| **Dept Head** | Department resource usage, approval of intra-dept transfers. | Department Overview | Dept Assets, Transfer Requests |
| **Employee** | Request assets, reserve meeting rooms, report issues. | Individual Workspace | Bookings, My Assets, Request Forms |

---

## 3. Core Modules & Screen Specs

### 3.1. Landing Page
*   **Hero Section:** Direct entry point showcasing platform statistics (Total assets managed, active bookings today).
*   **Quick Actions:** Dynamic shortcuts depending on login status (e.g., "Request Asset", "Book a Room", "View Dashboard").
*   **Feature Grid:** Overview of the system modules (Asset Lifecycle, Bookings, Maintenance, Audit Logs).

### 3.2. Navigation (Sidebar & Navbar)
*   **Global Sidebar:**
    *   Collapsible structure with smooth transition.
    *   Role-based navigation menu items.
    *   State retention (maintains open/collapsed state across navigation).
*   **Global Navbar:**
    *   Breadcrumb navigation path.
    *   Notifications hub (bell icon with unread badge + dropdown list).
    *   Theme toggle switcher (Sun/Moon icon for Light/Dark modes).
    *   User profile avatar with status indicator and sign-out dropdown.

### 3.3. Dashboard View
*   **KPI Cards Row:**
    *   *Assets Available:* Active count, green glow indicator.
    *   *Assets Allocated:* Active count, blue glow indicator.
    *   *Under Maintenance:* Attention required count, amber indicator.
    *   *Pending Requests:* Urgency count, violet indicator.
    *   *Active Bookings:* Current room/equipment reservations, teal indicator.
    *   *Audit Summary:* Pass/Fail ratio of latest cycle, grey/slate indicator.
*   **Interactive Charts Grid:**
    *   *Utilization Chart (Doughnut):* Breakdown by asset category.
    *   *Maintenance Requests (Bar/Line):* Maintenance trends over the last 6 months.
    *   *Resource Availability (Calendar Grid/Timeline):* Interactive timeline showcasing rooms/equipment bookings.
*   **Recent Activity & Alerts Log:**
    *   Live feed of asset allocations, check-ins, and critical warnings (e.g., "Server Room AC maintenance past due").

### 3.4. Reports UI & Screen Setup
*   **Report Types:**
    *   *Asset Utilization:* Shows usage frequency, allocation age, depreciation.
    *   *Department Summary:* Costs and allocations grouped by department.
    *   *Maintenance Report:* Breakdowns by asset types, technicians, and average repair times.
    *   *Booking Overviews:* Room and vehicle occupancy rates.
*   **Features:**
    *   Comprehensive filter bars (Date ranges, categories, departments, search inputs).
    *   Datatable with pagination, sorting by column headers, and inline badges (e.g., Status: `Active`, `Draft`, `Closed`).
    *   "Export CSV/PDF" button actions that trigger dynamic UI download notifications.

### 3.5. Forms & Modals
*   **Asset Request Form:** Multi-step wizard or detailed form with fields for: Asset Category, Justification, Required From/To Date, and Urgency.
*   **Resource Booking Modal:** Time-slot selector grid displaying availability conflicts dynamically.
*   **Maintenance Ticket Form:** Category, Asset tag number, issue description text field, photo upload simulator, and urgency toggle.

---

## 4. Design Guidelines & Visual Standards
*   **Theme Continuity:** Seamless styling transitions between Light Mode and Dark Mode.
*   **Glassmorphism:** Use background blur filters (`backdrop-filter: blur()`), thin borders with low opacity, and subtle drop shadows for cards and overlays.
*   **Micro-Animations:** Hover lifts on cards, active button presses, loading skeletons, slide-in sidebar, and path drawing animations on SVG icons.
*   **Responsiveness:** Perfect scaling from 320px (Mobile) up to 2560px (Ultra-Wide screens). Flexbox and CSS Grid are mandatory frameworks.

---

## 5. Mock API & Frontend Integrity
The frontend developer will create mock service handlers (`/static/src/js/mocks/`) that return JSON payloads containing static and dynamic test records. This enables full dashboard interaction (sorting lists, filter changes, searching, booking validation) in a client-only environment before API integration.

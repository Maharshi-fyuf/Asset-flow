# Technical Requirements Document (TRD) - AssetFlow

## 1. Project Directory Structure
To support an independent, beautiful frontend-only development setup that can later be cleanly integrated with Odoo/Backend APIs, the following directory structure is established:

```
asset_flow_frontend/
├── index.html                   # Entry point (SPA shell containing Navbar, Sidebar, and View Container)
├── package.json                 # Project configuration for development (Vite, Dev-server, dependencies)
├── src/
│   ├── css/
│   │   ├── main.css             # Main stylesheet (Theme variables, reset, core layouts)
│   │   ├── components.css       # UI components (Buttons, forms, cards, modals, table style)
│   │   └── views.css            # View-specific stylings (Dashboard, Reports, Booking calendar)
│   ├── js/
│   │   ├── app.js               # Application coordinator (routing, theme initialization)
│   │   ├── components/
│   │   │   ├── sidebar.js       # Collapsible navigation handler
│   │   │   ├── theme.js         # Light/Dark mode toggler
│   │   │   └── modal.js         # Reusable modal open/close controller
│   │   ├── views/
│   │   │   ├── dashboardView.js # Chart compilation & KPI rendering
│   │   │   ├── reportsView.js   # Report tables, filters, and export logic
│   │   │   └── bookingsView.js  # Calendar slot reservation coordinator
│   │   └── mocks/
│   │       ├── mockDb.js        # In-memory datasets (JSON)
│   │       └── mockService.js   # Mock fetch implementation wrapper
│   └── assets/
│       ├── icons/               # Inline SVG icons or system assets
│       └── images/              # Custom brand items and mock user avatars
```

---

## 2. Technical Stack & Libraries
*   **HTML5 / ES6 Javascript:** Pure Javascript for DOM manipulation, dynamic page rendering, and event handlers.
*   **CSS3 (Vanilla):** Dynamic theme control via CSS variables (Custom Properties). Use CSS Flexbox/Grid for high-fidelity layouts.
*   **Vite:** Recommended development server for hot module reloading and build optimization.
*   **ApexCharts / Chart.js:** For data visualization. ApexCharts is recommended due to its extensive built-in responsiveness and dark mode compatibility.
*   **Lucide Icons (via CDN or SVG sprites):** Vector-based consistent iconography.

---

## 3. UI State & Local Storage Management

### 3.1. Theme State (Light vs. Dark Mode)
Theme configuration is stored in `localStorage` and applied as a CSS class attribute to the root `<html>` tag to prevent screen flashing.

```javascript
// theme.js
export function initializeTheme() {
    const currentTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeToggleUI(currentTheme);
}

export function toggleTheme() {
    const activeTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = activeTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeToggleUI(newTheme);
    // Notify charts to re-render using matching color configurations
    window.dispatchEvent(new CustomEvent('theme-changed', { detail: newTheme }));
}
```

### 3.2. Session & Routing State (Single Page App style)
The shell manages dynamic module changes by looking at URL hash anchors or dataset targets:
*   Use `<a href="#dashboard" data-target="dashboard">` to navigate.
*   The `app.js` routing listener captures the change, toggles active visibility states (`display: none` vs `display: block`), and initializes the target view component.

---

## 4. Chart Configuration & Styling Integration
To ensure charts match the high-end dark/light design system, customize ApexCharts colors programmatically:

```javascript
// dashboardView.js
let chartInstance = null;

export function renderUtilizationChart(theme) {
    const colors = theme === 'dark' 
        ? { text: '#a0aec0', grid: '#2d3748', primary: '#8b5cf6', secondary: '#06b6d4' }
        : { text: '#4a5568', grid: '#e2e8f0', primary: '#6d28d9', secondary: '#0891b2' };

    const options = {
        chart: {
            type: 'donut',
            foreColor: colors.text,
            background: 'transparent'
        },
        series: [44, 55, 13, 33],
        labels: ['Laptops', 'Monitors', 'AV Equipment', 'Vehicles'],
        colors: [colors.primary, colors.secondary, '#10b981', '#f59e0b'],
        theme: {
            mode: theme
        }
    };
    
    if(chartInstance) chartInstance.destroy();
    chartInstance = new ApexCharts(document.querySelector("#utilization-chart"), options);
    chartInstance.render();
}
```

---

## 5. Mock API & Data Schemas (JSON)
The mock API layer `mockService.js` simulates backend REST responses using a standard response payload format:
`{ status: 200, data: [...] }`.

### 5.1. Dashboard KPIs Schema
```json
{
  "assets_available": 142,
  "assets_allocated": 389,
  "under_maintenance": 18,
  "pending_requests": 24,
  "upcoming_returns": 7,
  "active_bookings": 12,
  "audit_compliance_rate": "98.4%"
}
```

### 5.2. Asset Request Schema
```json
{
  "id": "REQ-1002",
  "employee_name": "Jigar Vighani",
  "department": "Engineering",
  "asset_category": "MacBook Pro M3",
  "request_date": "2026-07-12",
  "urgency": "High",
  "status": "pending_approval"
}
```

### 5.3. Resource Booking Schema
```json
{
  "id": "BKG-509",
  "resource_name": "Conference Room A",
  "booked_by": "Maharshi Khamar",
  "date": "2026-07-13",
  "time_slot": "14:00 - 15:30",
  "purpose": "Sprint Review"
}
```

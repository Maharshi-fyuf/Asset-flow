# App Flow - AssetFlow

This document details the navigation flows, modal workflows, page-level routing rules, and structural wireframe layouts for the AssetFlow application using Mermaid diagrams.

---

## 1. Global Navigation Architecture

The diagram below details the screen transitions, user authentication entry, and page swapping architecture within the Single Page Application framework:

```mermaid
graph TD
    %% Base navigation nodes
    Start([Visitor Accesses URL]) --> Landing{User Authenticated?}
    
    %% Landing Page Routing
    Landing -- No --> LandPage[Landing Page / Brand Pitch]
    LandPage --> LoginBtn[Click 'Sign In']
    LoginBtn --> LoginModal[Login Modal Window]
    LoginModal -->|Success| DashboardRoute[Main Workspace Layout]
    
    Landing -- Yes --> DashboardRoute
    
    %% Main Workspace Shell
    subgraph DashboardShell [Main App Shell Container]
        DashboardRoute --> Sidebar[Global Sidebar Menu]
        DashboardRoute --> Navbar[Global Navbar Widget]
        DashboardRoute --> DisplayPane[Dynamic View Area]
    end

    %% Sidebar Routing Transitions
    Sidebar -->|Select Dashboard| V_Dash[Dashboard Screen]
    Sidebar -->|Select Assets| V_Assets[Asset Tracking Grid]
    Sidebar -->|Select Bookings| V_Book[Resource Booking Calendar]
    Sidebar -->|Select Maintenance| V_Maint[Maintenance Log]
    Sidebar -->|Select Reports| V_Rep[Reports & Analytics Dashboard]
    
    %% Actions within view areas
    V_Assets -->|Click 'Request Asset'| ReqModal[Asset Request Modal]
    V_Book -->|Select Grid Time-Slot| BookModal[Booking Request Modal]
    V_Maint -->|Click 'Report Issue'| MaintForm[Report Maintenance Modal]
    V_Rep -->|Select Filters & Export| CSVExport[Simulated CSV File Download]
```

---

## 2. Interactive Flow Workflows

### 2.1. Requesting an Asset Flow
This diagram maps out the client-side state machine handling field validation, UI states, and confirmation alerts during an asset request:

```mermaid
sequenceDiagram
    actor User as Employee / Manager
    participant Shell as App Routing Shell
    participant Modal as Request Modal
    participant Store as Local Mock DB
    
    User->>Shell: Clicks "Request Asset" button
    Shell->>Modal: Initialize inputs & render view layout
    Modal-->>User: Display Form (Asset Category, Urgency, Justification)
    User->>Modal: Selects category, enters data, clicks "Submit"
    
    alt Invalid Inputs (Empty fields or invalid dates)
        Modal->>Modal: Display validation messages inline
        Modal-->>User: Request correction
    else Valid Inputs
        Modal->>Store: Insert new request record (pending status)
        Store-->>Modal: Success response
        Modal->>Shell: Close Modal & trigger toast notification
        Shell-->>User: Render "Success Toast" notification
        Shell->>Shell: Refresh Dynamic Tables / Activity Feed
    end
```

### 2.2. Theme Toggling Event Pipeline
This diagram displays how CSS variables and JS-based chart redraws handle Light and Dark themes simultaneously:

```mermaid
graph LR
    Icon[Navbar Sun/Moon Toggle] -->|User Click| Handler[Theme Toggler Script]
    Handler -->|Update Attribute| DOM[Set attribute data-theme on HTML element]
    Handler -->|Save Preference| Storage[Save preference to localStorage]
    Handler -->|Broadcast Event| Event[Dispatch custom 'theme-changed' window event]
    
    DOM -->|CSS Selector Apply| UI[CSS changes backgrounds, text colors, and shadows]
    Event -->|Listener Triggered| Chart[ApexCharts dynamic redrawing with updated theme colors]
```

---

## 3. UI Layout & Grid Wireframe Spec

Below is the layout wireframe showing how the layout handles desktop resolutions:

```
+----------------------------------------------------------------------------------------+
|                                      GLOBAL NAVBAR                                     |
| [Logo] [Menu Toggle]    [Breadcrumbs: Assets > Grid]         (Notifications) (Avatar)  |
+------------------+---------------------------------------------------------------------+
|                  |                                                                     |
|  GLOBAL SIDEBAR  |  MAIN VIEWS CONTAINER                                               |
|                  |  +---------------------------------------------------------------+  |
|  [D] Dashboard   |  | PAGE HEADER & PRIMARY ACTION BUTTON                           |  |
|  [A] Asset Grid  |  +---------------------------------------------------------------+  |
|  [B] Bookings    |  |                                                               |  |
|  [M] Maintenance |  |  +---------------------+ +-----------------+ +-------------+  |  |
|  [R] Reports     |  |  | KPI Card: Available | | KPI Card: Alloc | | Card: Maint |  |  |
|                  |  |  +---------------------+ +-----------------+ +-------------+  |  |
|                  |  |                                                               |  |
|                  |  |  +-------------------------------------+ +-----------------+  |  |
|                  |  |  | Main Content: Datatable / Calendar  | | Side Chart Pane |  |  |
|                  |  |  |                                     | |                 |  |  |
|                  |  |  |                                     | |                 |  |  |
|                  |  |  +-------------------------------------+ +-----------------+  |  |
|                  |  +---------------------------------------------------------------+  |
|  [Collapse <]    |                                                                     |
+------------------+---------------------------------------------------------------------+
```
*Note: In tablet layouts, the global sidebar collapses to icons-only. In mobile screens, it transforms into an off-canvas overlay drawer toggled via the navbar burger menu icon.*

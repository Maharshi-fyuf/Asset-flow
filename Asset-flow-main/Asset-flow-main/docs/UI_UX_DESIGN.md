# UI/UX Design Specification - AssetFlow

This document defines the core visual guidelines, design tokens, color systems (for both Light and Dark mode), and interactive micro-animation patterns for the AssetFlow enterprise frontend.

---

## 1. Typography & General Settings

*   **Primary Font Family:** `'Outfit'`, sans-serif (Google Fonts) – clean, modern, slightly rounded geometric headers.
*   **Secondary Font Family:** `'Inter'`, sans-serif (Google Fonts) – optimized for dashboard datatables and code readouts.
*   **Base Styling Elements:**
    *   Smooth font-smoothing: `-webkit-font-smoothing: antialiased;`
    *   Transition-duration: `0.3s` ease-in-out on interactive background elements.

---

## 2. Color Palettes (HSL Systems)

To achieve a modern, premium aesthetic, colors are defined using HSL variables to allow for easy alpha-transparency overrides (`hsla()`).

### 2.1. Theme Variables Config

```css
/* main.css */

/* --- DARK MODE (Default Theme) --- */
[data-theme="dark"] {
    --bg-primary: hsl(222, 47%, 11%);      /* Sleek deep space blue-black */
    --bg-secondary: hsl(223, 47%, 15%);    /* Card and sidebar background */
    --bg-surface: hsl(223, 47%, 18%);      /* Dropdown / Modal panels */
    --border-color: hsla(217, 30%, 60%, 0.12); /* Glassmorphic border */
    
    --text-primary: hsl(210, 40%, 98%);    /* Crisp off-white */
    --text-secondary: hsl(215, 20%, 65%);  /* Slate grey */
    --text-muted: hsl(215, 16%, 47%);      /* Darker helper text */
    
    /* Accents & Status indicators */
    --accent-primary: hsl(263, 90%, 65%);  /* Neon Purple / Violet */
    --accent-secondary: hsl(187, 92%, 45%);/* Electric Cyan */
    
    --color-success: hsl(142, 70%, 45%);   /* Emerald Green */
    --color-warning: hsl(38, 92%, 50%);    /* Amber Yellow */
    --color-danger: hsl(350, 89%, 60%);    /* Crimson Red */
    
    --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    --glass-blur: blur(12px);
}

/* --- LIGHT MODE (Alternate Theme) --- */
[data-theme="light"] {
    --bg-primary: hsl(210, 40%, 96%);      /* Clean light grey-blue */
    --bg-secondary: hsl(0, 0%, 100%);      /* Solid white cards */
    --bg-surface: hsl(210, 40%, 98%);      /* Input overlays / Modals */
    --border-color: hsla(217, 20%, 30%, 0.08);
    
    --text-primary: hsl(222, 47%, 11%);    /* Deep Navy */
    --text-secondary: hsl(215, 25%, 27%);  /* Dark Slate */
    --text-muted: hsl(215, 16%, 47%);      
    
    --accent-primary: hsl(263, 70%, 50%);  
    --accent-secondary: hsl(187, 85%, 38%);
    
    --color-success: hsl(142, 72%, 29%);   
    --color-warning: hsl(38, 92%, 40%);    
    --color-danger: hsl(350, 75%, 45%);    
    
    --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.06);
    --glass-blur: blur(8px);
}
```

---

## 3. Glassmorphism & Shadow Foundations

Premium designs avoid solid harsh borders. Cards and view panes must apply the following CSS rules:

*   **Standard Card UI:**
    ```css
    .card {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        box-shadow: var(--glass-shadow);
        backdrop-filter: var(--glass-blur);
        transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.25s ease;
    }
    .card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.15);
    }
    ```

---

## 4. Key UI Components Specifications

### 4.1. Dashboard KPI Cards
*   Each KPI card features a top row with an inline SVG icon nested inside a glowing circular container.
*   *Active Glow states:*
    ```css
    .kpi-available { --card-glow: var(--color-success); }
    .kpi-allocated { --card-glow: var(--accent-secondary); }
    .kpi-maintenance { --card-glow: var(--color-warning); }
    .kpi-pending { --card-glow: var(--accent-primary); }
    
    .kpi-card {
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, transparent, var(--card-glow), transparent);
    }
    ```

### 4.2. Custom Sidebar & Links
*   Active nav items get a glassmorphic gradient background and a solid vertical bar on the left edge:
    ```css
    .sidebar-link.active {
        background: linear-gradient(90deg, hsla(263, 90%, 65%, 0.1) 0%, transparent 100%);
        border-left: 3px solid var(--accent-primary);
        color: var(--text-primary);
    }
    ```

### 4.3. Interactive Datatables
*   **Grid layout:** Horizontal dividing lines only (`border-bottom: 1px solid var(--border-color)`), no vertical borders.
*   **Row hover:** Rows change to `background-color: hsla(217, 30%, 60%, 0.04);` with a cursor pointer to indicate actionability.
*   **Badges:** Smooth background capsules matching state colours (e.g., status label pill):
    *   `Available` status pill: `background: hsla(142, 70%, 45%, 0.15); color: var(--color-success);`

### 4.4. Forms, Input fields, and Modals
*   **Inputs:** Large, clear inputs with `border-radius: 8px`, `background: var(--bg-surface)`, and focus glow state:
    ```css
    .form-input:focus {
        border-color: var(--accent-primary);
        box-shadow: 0 0 0 3px hsla(263, 90%, 65%, 0.2);
        outline: none;
    }
    ```
*   **Modals:** Full-screen backdrop blur overlays overlaying other components:
    ```css
    .modal-overlay {
        background: rgba(10, 15, 30, 0.6);
        backdrop-filter: blur(8px);
    }
    ```

---

## 5. Micro-Animations & Interactivity

To keep the page responsive and organic:
1.  **Sidebar Collapse Toggle:** Slide transition (`transition: width 0.3s cubic-bezier(0.2, 0.8, 0.2, 1)`).
2.  **Button Press Response:** Press scale down (`transform: scale(0.97)` on `:active`).
3.  **Skeleton Loading States:** Add a pulse background animation to grid cards during dashboard refresh/initial load.
    ```css
    @keyframes skeleton-loading {
        0% { background-color: var(--bg-surface); }
        50% { background-color: hsla(217, 30%, 60%, 0.08); }
        100% { background-color: var(--bg-surface); }
    }
    .skeleton {
        animation: skeleton-loading 1.5s infinite ease-in-out;
    }
    ```

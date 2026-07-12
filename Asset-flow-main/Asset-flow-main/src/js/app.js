// app.js
import { initializeTheme, toggleTheme } from './components/theme.js';
import { dashboardView } from './views/dashboardView.js';
import { assetsView } from './views/assetsView.js';
import { bookingsView } from './views/bookingsView.js';
import { maintenanceView } from './views/maintenanceView.js';
import { reportsView } from './views/reportsView.js';

// Central toast controller
export function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <i class="${type === 'success' ? 'lucide-check-circle' : 'lucide-alert-triangle'}" style="color: var(--${type === 'success' ? 'color-success' : 'color-danger'})"></i>
    <span>${message}</span>
  `;
  container.appendChild(toast);
  
  if (typeof lucide !== 'undefined') lucide.createIcons();

  // Auto remove toast
  setTimeout(() => {
    toast.style.transform = 'translateX(120%)';
    toast.style.opacity = '0';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Modal open/close helpers
export function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('active');
  }
}

export function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('active');
  }
}

// Router to handle page swapping
const routes = {
  landing: { title: 'Landing', init: () => {} }, // Static landing page
  dashboard: { title: 'Dashboard', init: dashboardView.init },
  assets: { title: 'Assets Grid', init: assetsView.init },
  bookings: { title: 'Resource Bookings', init: bookingsView.init },
  maintenance: { title: 'Maintenance Board', init: maintenanceView.init },
  reports: { title: 'Reports UI', init: reportsView.init }
};

function navigateTo(routeId) {
  // 1. Swap visibility classes
  const views = document.querySelectorAll('.view-pane');
  views.forEach(view => view.classList.remove('active'));
  
  const targetView = document.getElementById(`view-${routeId}`);
  if (targetView) {
    targetView.classList.add('active');
  }
  
  // 2. Highlight Sidebar selection
  const sidebarLinks = document.querySelectorAll('.sidebar-link');
  sidebarLinks.forEach(link => {
    link.classList.remove('active');
    if (link.getAttribute('data-target') === routeId) {
      link.classList.add('active');
    }
  });

  // 3. Update Breadcrumbs
  const currentBreadcrumb = document.getElementById('breadcrumb-current');
  if (currentBreadcrumb && routes[routeId]) {
    currentBreadcrumb.textContent = routes[routeId].title;
  }

  // 4. Initialize dynamic content
  if (routes[routeId] && routes[routeId].init) {
    routes[routeId].init();
  }

  // Auto-close sidebar on mobile after navigating
  if (window.innerWidth <= 768) {
    document.getElementById('app-sidebar').classList.remove('active');
  }
}

// Event Bindings
document.addEventListener('DOMContentLoaded', () => {
  // Init Theme
  initializeTheme();

  // Sidebar toggle
  const menuToggle = document.getElementById('menu-toggle');
  const sidebar = document.getElementById('app-sidebar');
  if (menuToggle && sidebar) {
    menuToggle.addEventListener('click', () => {
      if (window.innerWidth <= 768) {
        sidebar.classList.toggle('active');
      } else {
        sidebar.classList.toggle('collapsed');
      }
    });
  }

  // Theme switch button
  const themeToggleBtns = document.querySelectorAll('.theme-toggle');
  themeToggleBtns.forEach(btn => {
    btn.addEventListener('click', toggleTheme);
  });

  // Navigation Links
  const navLinks = document.querySelectorAll('[data-target]');
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const target = link.getAttribute('data-target');
      window.location.hash = target;
    });
  });

  // Handle Close Modal clicks automatically
  document.querySelectorAll('[data-close-modal]').forEach(btn => {
    btn.addEventListener('click', () => {
      const modal = btn.closest('.modal-overlay');
      if (modal) {
        modal.classList.remove('active');
      }
    });
  });

  // Hash change routing listener
  window.addEventListener('hashchange', () => {
    const route = window.location.hash.slice(1) || 'landing';
    if (routes[route]) {
      navigateTo(route);
    }
  });

  // Initial load navigation routing
  const initialRoute = window.location.hash.slice(1) || 'landing';
  navigateTo(initialRoute);

  // Initialize Lucide Icons inside the template
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
});

// dashboardView.js
import { mockService } from '../mocks/mockService.js';

let categoryChart = null;
let maintenanceChart = null;

export const dashboardView = {
  async init() {
    try {
      // 1. Fetch KPI Stats
      const kpis = await mockService.getDashboardKpis();
      updateKpiCards(kpis);

      // 2. Load and draw charts
      const activeTheme = document.documentElement.getAttribute('data-theme') || 'dark';
      renderCharts(activeTheme);

      // 3. Render Recent Activity Feed
      await renderActivityFeed();

      // 4. Register event listener for theme change
      window.removeEventListener('theme-changed', handleThemeChange);
      window.addEventListener('theme-changed', handleThemeChange);
    } catch (err) {
      console.error('Error initializing dashboard view:', err);
    }
  }
};

function handleThemeChange(e) {
  const newTheme = e.detail;
  renderCharts(newTheme);
}

function updateKpiCards(kpis) {
  document.getElementById('kpi-val-available').textContent = kpis.assets_available;
  document.getElementById('kpi-val-allocated').textContent = kpis.assets_allocated;
  document.getElementById('kpi-val-maintenance').textContent = kpis.under_maintenance;
  document.getElementById('kpi-val-requests').textContent = kpis.pending_requests;
  document.getElementById('kpi-val-bookings').textContent = kpis.active_bookings;
  document.getElementById('kpi-val-compliance').textContent = kpis.audit_compliance_rate;
}

async function renderCharts(theme) {
  if (typeof ApexCharts === 'undefined') return;

  const isDark = theme === 'dark';
  
  // Custom styles for matching themes
  const textClr = isDark ? '#a0aec0' : '#4a5568';
  const gridClr = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)';

  // Fetch Assets to calculate category statistics
  const assets = await mockService.getAssets();
  const categories = await mockService.getCategories();
  
  const categoryCounts = categories.map(cat => {
    return assets.filter(a => a.category_id === cat.id).length;
  });
  const categoryLabels = categories.map(c => c.name);

  // --- Category Utilization Doughnut Chart ---
  const catOptions = {
    chart: {
      type: 'donut',
      height: 320,
      background: 'transparent',
      foreColor: textClr
    },
    series: categoryCounts,
    labels: categoryLabels,
    colors: ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ec4899'],
    stroke: {
      show: true,
      colors: [isDark ? '#1e293b' : '#ffffff'],
      width: 2
    },
    legend: {
      position: 'bottom'
    },
    theme: {
      mode: theme
    },
    dataLabels: {
      enabled: false
    }
  };

  if (categoryChart) categoryChart.destroy();
  categoryChart = new ApexCharts(document.querySelector("#chart-categories"), catOptions);
  categoryChart.render();

  // --- Maintenance Requests Line/Bar Trend ---
  const maintLogs = await mockService.getMaintenanceLogs();
  
  // Simple grouping of tickets by urgency for representation
  const urgencyCounts = { Low: 0, Medium: 0, Critical: 0 };
  maintLogs.forEach(log => {
    if (urgencyCounts[log.urgency] !== undefined) {
      urgencyCounts[log.urgency]++;
    }
  });

  const trendOptions = {
    chart: {
      type: 'bar',
      height: 320,
      background: 'transparent',
      foreColor: textClr,
      toolbar: { show: false }
    },
    series: [{
      name: 'Tickets Raised',
      data: [urgencyCounts.Low, urgencyCounts.Medium, urgencyCounts.Critical]
    }],
    xaxis: {
      categories: ['Low Urgency', 'Medium Urgency', 'Critical Urgency'],
      axisBorder: { show: false },
      axisTicks: { show: false }
    },
    yaxis: {
      labels: {
        formatter: (val) => Math.round(val)
      }
    },
    grid: {
      borderColor: gridClr
    },
    colors: ['#3b82f6'],
    theme: {
      mode: theme
    },
    plotOptions: {
      bar: {
        borderRadius: 6,
        columnWidth: '50%'
      }
    }
  };

  if (maintenanceChart) maintenanceChart.destroy();
  maintenanceChart = new ApexCharts(document.querySelector("#chart-maintenance"), trendOptions);
  maintenanceChart.render();
}

async function renderActivityFeed() {
  const container = document.getElementById('activity-feed');
  if (!container) return;

  const requests = await mockService.getRequests();
  const bookings = await mockService.getBookings();
  const maintLogs = await mockService.getMaintenanceLogs();

  // Combine items to mock a dynamic chronological activity feed
  const feedItems = [];

  requests.slice(-3).forEach(req => {
    feedItems.push({
      type: 'request',
      title: 'New Asset Requested',
      description: `${req.employee_name} requested a ${req.category_name} (Urgency: ${req.urgency})`,
      time: req.request_date,
      icon: 'lucide-file-text',
      color: 'var(--accent-primary)',
      bg: 'hsla(263, 90%, 65%, 0.12)'
    });
  });

  bookings.slice(-2).forEach(bkg => {
    feedItems.push({
      type: 'booking',
      title: 'Resource Reserved',
      description: `${bkg.employee_name} booked ${bkg.resource_name} on ${bkg.booking_date}`,
      time: bkg.booking_date,
      icon: 'lucide-calendar',
      color: 'var(--accent-secondary)',
      bg: 'hsla(187, 92%, 45%, 0.12)'
    });
  });

  maintLogs.slice(-2).forEach(log => {
    feedItems.push({
      type: 'maintenance',
      title: 'Maintenance Log Raised',
      description: `[${log.asset_tag}] ${log.asset_name}: ${log.issue_category} (Urgency: ${log.urgency})`,
      time: 'Recently',
      icon: 'lucide-wrench',
      color: 'var(--color-warning)',
      bg: 'hsla(38, 92%, 50%, 0.12)'
    });
  });

  // Render list inside container
  container.innerHTML = feedItems.map(item => `
    <div class="activity-item">
      <div class="activity-icon" style="background-color: ${item.bg}; color: ${item.color}">
        <i class="${item.icon}" style="width: 16px; height: 16px;"></i>
      </div>
      <div class="activity-details">
        <p><strong>${item.title}</strong> - ${item.description}</p>
        <div class="activity-time">${item.time}</div>
      </div>
    </div>
  `).join('');

  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
}

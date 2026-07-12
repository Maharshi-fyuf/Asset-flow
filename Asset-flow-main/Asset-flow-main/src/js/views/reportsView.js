// reportsView.js
import { mockService } from '../mocks/mockService.js';
import { showToast } from '../app.js';

let activeReport = 'utilization';
let listenersBound = false;

export const reportsView = {
  async init() {
    try {
      // 1. Populate filters
      await populateFilters();

      // 2. Render report table
      await renderReportTable();

      // 3. Bind listeners
      registerListeners();
    } catch (err) {
      console.error('Error rendering reports view:', err);
    }
  }
};

function registerListeners() {
  if (listenersBound) return;

  // Report type change selector
  const repType = document.getElementById('report-type-select');
  if (repType) {
    repType.addEventListener('change', (e) => {
      activeReport = e.target.value;
      updateFilterVisibility();
      renderReportTable();
    });
  }

  // Bind filter change events
  const deptFilter = document.getElementById('report-dept-filter');
  if (deptFilter) deptFilter.addEventListener('change', renderReportTable);

  const statusFilter = document.getElementById('report-status-filter');
  if (statusFilter) statusFilter.addEventListener('change', renderReportTable);

  const searchInput = document.getElementById('report-search');
  if (searchInput) searchInput.addEventListener('input', renderReportTable);

  // CSV export button
  const exportBtn = document.getElementById('btn-export-csv');
  if (exportBtn) {
    exportBtn.addEventListener('click', handleCSVExport);
  }

  listenersBound = true;
}

async function populateFilters() {
  const depts = await mockService.getDepartments();
  const select = document.getElementById('report-dept-filter');
  if (select) {
    select.innerHTML = '<option value="">All Departments</option>' + 
      depts.map(d => `<option value="${d.id}">${d.name}</option>`).join('');
  }
}

function updateFilterVisibility() {
  const statusGroup = document.getElementById('filter-group-status');
  // Only show status filter for Utilization
  if (statusGroup) {
    if (activeReport === 'utilization') {
      statusGroup.style.display = 'flex';
    } else {
      statusGroup.style.display = 'none';
    }
  }
}

async function renderReportTable() {
  const head = document.getElementById('reports-table-head');
  const body = document.getElementById('reports-table-body');
  if (!head || !body) return;

  const deptVal = document.getElementById('report-dept-filter')?.value || '';
  const statusVal = document.getElementById('report-status-filter')?.value || '';
  const query = document.getElementById('report-search')?.value.toLowerCase() || '';

  if (activeReport === 'utilization') {
    // Columns: Tag, Name, Category, Status, Cost, Date
    head.innerHTML = `
      <tr>
        <th>Asset Tag</th>
        <th>Asset Name</th>
        <th>Category</th>
        <th>Status</th>
        <th>Cost</th>
        <th>Purchase Date</th>
      </tr>
    `;

    const assets = await mockService.getAssets();
    const filtered = assets.filter(a => {
      const matchSearch = a.name.toLowerCase().includes(query) || a.tag_number.toLowerCase().includes(query);
      const matchStatus = statusVal === '' || a.status === statusVal;
      // We don't filter assets directly by department in static seed (it requires employees query), so let's mock it
      return matchSearch && matchStatus;
    });

    if (filtered.length === 0) {
      body.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 32px 0;">No logs found.</td></tr>`;
      return;
    }

    body.innerHTML = filtered.map(a => `
      <tr>
        <td><strong>${a.tag_number}</strong></td>
        <td>${a.name}</td>
        <td>${a.category_name}</td>
        <td><span class="badge badge-${a.status.toLowerCase()}">${a.status}</span></td>
        <td>$${a.purchase_cost.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
        <td>${a.purchase_date}</td>
      </tr>
    `).join('');

  } else if (activeReport === 'maintenance') {
    // Columns: Ticket, Asset Name, Issue, Severity, Status, Reporter
    head.innerHTML = `
      <tr>
        <th>Ticket #</th>
        <th>Asset Name</th>
        <th>Issue Category</th>
        <th>Urgency</th>
        <th>Status</th>
        <th>Reporter</th>
      </tr>
    `;

    const logs = await mockService.getMaintenanceLogs();
    const filtered = logs.filter(log => {
      const matchSearch = log.asset_name.toLowerCase().includes(query) || log.issue_category.toLowerCase().includes(query);
      return matchSearch;
    });

    if (filtered.length === 0) {
      body.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 32px 0;">No records found.</td></tr>`;
      return;
    }

    body.innerHTML = filtered.map(log => `
      <tr>
        <td><strong>MNT-#${log.id}</strong></td>
        <td>${log.asset_name} (${log.asset_tag})</td>
        <td>${log.issue_category}</td>
        <td><span class="badge ${log.urgency === 'Critical' ? 'badge-rejected' : 'badge-maintenance'}">${log.urgency}</span></td>
        <td><span class="badge badge-${log.status.toLowerCase()}">${log.status}</span></td>
        <td>${log.reporter_name}</td>
      </tr>
    `).join('');

  } else if (activeReport === 'bookings') {
    // Columns: Booking ID, Resource, Date, Time Range, Reserved By
    head.innerHTML = `
      <tr>
        <th>Booking #</th>
        <th>Resource Name</th>
        <th>Booking Date</th>
        <th>Time Frame</th>
        <th>Status</th>
        <th>Reserved By</th>
      </tr>
    `;

    const bkgs = await mockService.getBookings();
    const filtered = bkgs.filter(b => b.resource_name.toLowerCase().includes(query));

    if (filtered.length === 0) {
      body.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 32px 0;">No bookings found.</td></tr>`;
      return;
    }

    body.innerHTML = filtered.map(b => `
      <tr>
        <td><strong>BKG-#${b.id}</strong></td>
        <td>${b.resource_name}</td>
        <td>${b.booking_date}</td>
        <td>${b.start_time} - ${b.end_time}</td>
        <td><span class="badge badge-available">Confirmed</span></td>
        <td>${b.employee_name}</td>
      </tr>
    `).join('');
  }
}

function handleCSVExport() {
  const table = document.querySelector('.custom-table');
  if (!table) return;

  const rows = Array.from(table.querySelectorAll('tr'));
  const csvContent = rows.map(row => {
    const cells = Array.from(row.querySelectorAll('th, td'));
    return cells.map(cell => `"${cell.textContent.trim().replace(/"/g, '""')}"`).join(',');
  }).join('\n');

  // Launch simulated download triggers
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', `asset_flow_report_${activeReport}_${Date.now()}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  showToast(`CSV data export triggered for ${activeReport.toUpperCase()} report.`);
}

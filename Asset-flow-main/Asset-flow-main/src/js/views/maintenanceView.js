// maintenanceView.js
import { mockService } from '../mocks/mockService.js';
import { showToast, openModal, closeModal } from '../app.js';

let listenersBound = false;

export const maintenanceView = {
  async init() {
    try {
      // 1. Populate asset options for reporting issues
      await populateAssetOptions();

      // 2. Render Kanban columns
      await renderBoard();

      // 3. Register listeners
      registerListeners();
    } catch (err) {
      console.error('Error rendering maintenance board:', err);
    }
  }
};

function registerListeners() {
  if (listenersBound) return;

  // Open maintenance issue modal btn
  const createBtn = document.getElementById('btn-open-maint-modal');
  if (createBtn) {
    createBtn.addEventListener('click', () => {
      openModal('modal-maintenance-report');
    });
  }

  // Handle ticket form submit
  const maintForm = document.getElementById('form-maintenance-report');
  if (maintForm) {
    maintForm.addEventListener('submit', handleTicketSubmit);
  }

  // Handle board column ticket action triggers
  const board = document.getElementById('maintenance-kanban-board');
  if (board) {
    board.addEventListener('click', handleTicketActionClick);
  }

  listenersBound = true;
}

async function populateAssetOptions() {
  const assets = await mockService.getAssets();
  const select = document.getElementById('form-maint-asset');
  if (select) {
    // Select assets that are Allocated or Available (can raise tickets for them)
    const validAssets = assets.filter(a => a.status === 'Allocated' || a.status === 'Available');
    select.innerHTML = validAssets.map(a => `<option value="${a.id}">[${a.tag_number}] ${a.name}</option>`).join('');
  }
}

async function renderBoard() {
  const lists = {
    Pending: document.getElementById('maint-col-pending'),
    Approved: document.getElementById('maint-col-approved'),
    In_Progress: document.getElementById('maint-col-progress'),
    Resolved: document.getElementById('maint-col-resolved')
  };

  if (!lists.Pending) return;

  // Clear columns
  Object.values(lists).forEach(col => col.innerHTML = '');

  const logs = await mockService.getMaintenanceLogs();

  // Columns status categories counts tracker
  const counts = { Pending: 0, Approved: 0, In_Progress: 0, Resolved: 0 };

  logs.forEach(log => {
    let colId = log.status; // 'Pending', 'In_Progress', 'Resolved'
    if (colId === 'Assigned') colId = 'In_Progress'; // Collapse Assigned into Progress for layout column consistency
    
    if (lists[colId]) {
      counts[colId]++;
      
      let badgeClass = 'badge-pending';
      if (log.urgency === 'Critical') badgeClass = 'badge-rejected'; // Red badge for critical
      else if (log.urgency === 'Medium') badgeClass = 'badge-maintenance';

      let actionsHtml = '';
      if (log.status === 'Pending') {
        actionsHtml = `<button class="btn btn-secondary btn-ticket-act" data-action="approve" data-id="${log.id}" style="padding: 4px 8px; font-size: 0.75rem;">Approve</button>`;
      } else if (log.status === 'Approved' || log.status === 'Assigned') {
        actionsHtml = `<button class="btn btn-primary btn-ticket-act" data-action="resolve" data-id="${log.id}" style="padding: 4px 8px; font-size: 0.75rem;">Resolve</button>`;
      }

      lists[colId].innerHTML += `
        <div class="maint-ticket-card">
          <div class="ticket-tag">${log.asset_tag}</div>
          <div class="ticket-asset-name">${log.asset_name}</div>
          <p style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 8px;">${log.description}</p>
          <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
            <span class="badge ${badgeClass}">${log.urgency}</span>
            <span style="font-size: 0.75rem; color: var(--text-muted);">By: ${log.reporter_name}</span>
          </div>
          ${actionsHtml ? `<div class="ticket-footer">${actionsHtml}</div>` : ''}
        </div>
      `;
    }
  });

  // Update counts in header labels
  document.getElementById('maint-count-pending').textContent = counts.Pending;
  document.getElementById('maint-count-approved').textContent = counts.Approved;
  document.getElementById('maint-count-progress').textContent = counts.In_Progress;
  document.getElementById('maint-count-resolved').textContent = counts.Resolved;
}

async function handleTicketSubmit(e) {
  e.preventDefault();

  const form = e.target;
  const assetId = form.elements['maint-asset'].value;
  const category = form.elements['maint-category'].value;
  const urgency = form.elements['maint-urgency'].value;
  const description = form.elements['maint-description'].value;

  if (!description) {
    showToast('Please provide a description of the issue.', 'error');
    return;
  }

  try {
    await mockService.createMaintenanceLog({
      asset_id: assetId,
      reported_by: 4,
      issue_category: category,
      urgency,
      description
    });

    showToast('Maintenance ticket reported successfully.');
    closeModal('modal-maintenance-report');
    form.reset();

    // Refresh layout view
    await renderBoard();
  } catch (err) {
    showToast(err.message || 'Error creating ticket.', 'error');
  }
}

async function handleTicketActionClick(e) {
  const btn = e.target.closest('.btn-ticket-act');
  if (!btn) return;

  const id = btn.getAttribute('data-id');
  const action = btn.getAttribute('data-action');

  try {
    if (action === 'approve') {
      await mockService.updateMaintenanceStatus(id, 'Approved', 1); // Assign to technician id 1 (Maharshi)
      showToast('Ticket approved and technician assigned.');
    } else if (action === 'resolve') {
      await mockService.updateMaintenanceStatus(id, 'Resolved');
      showToast('Maintenance issue marked as RESOLVED.');
    }

    // Refresh view
    await renderBoard();
  } catch (err) {
    showToast(err.message || 'Error updating status.', 'error');
  }
}

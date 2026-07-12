// =====================================================
// AssetFlow Frontend — Interactive SPA Router
// =====================================================

// ---- Navigation ----
function navigateTo(viewId) {
    const loginView = document.getElementById('view-login');
    const appLayout = document.getElementById('app-layout');

    // Transition from login to app
    if (loginView && !loginView.classList.contains('hidden')) {
        loginView.style.display = 'none';
        appLayout.style.display = 'flex';
    }

    // Hide all views inside the app
    document.querySelectorAll('#app-layout .view-container').forEach(v => v.classList.remove('active'));

    // Show the requested view
    const target = document.getElementById(viewId);
    if (target) target.classList.add('active');

    // Update sidebar active state
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('onclick') && item.getAttribute('onclick').includes(viewId)) {
            item.classList.add('active');
        }
    });

    // Push state for browser back-button support
    history.pushState({ view: viewId }, '', '#' + viewId);
}

window.addEventListener('popstate', (e) => {
    if (e.state && e.state.view) navigateTo(e.state.view);
});

// ---- Tab Switching (generic) ----
function switchTab(clickedTab, tabGroupClass, contentGroupClass) {
    clickedTab.closest('.' + tabGroupClass).querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    clickedTab.classList.add('active');
    const idx = Array.from(clickedTab.parentElement.children).indexOf(clickedTab);
    document.querySelectorAll('.' + contentGroupClass).forEach((panel, i) => {
        panel.style.display = (i === idx) ? 'block' : 'none';
    });
}

// ---- Org Setup Tabs ----
function initOrgTabs() {
    const tabs = document.querySelectorAll('#view-org-setup .tab');
    const panels = document.querySelectorAll('#view-org-setup .tab-panel');
    tabs.forEach((tab, idx) => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            panels.forEach((p, i) => p.style.display = i === idx ? 'block' : 'none');
        });
    });
}

// ---- Notification Filter Tabs ----
function initNotificationTabs() {
    const tabs = document.querySelectorAll('#view-notifications .tab');
    const items = document.querySelectorAll('#view-notifications .activity-item');
    const filterMap = { 0: null, 1: 'alert', 2: 'approval', 3: 'booking' };
    tabs.forEach((tab, idx) => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const filter = filterMap[idx];
            items.forEach(item => {
                item.style.display = (!filter || item.dataset.type === filter) ? 'flex' : 'none';
            });
        });
    });
}

// ---- Asset Search Filter ----
function initAssetSearch() {
    const input = document.getElementById('asset-search-input');
    if (!input) return;
    input.addEventListener('input', () => {
        const q = input.value.toLowerCase();
        document.querySelectorAll('#asset-table-body tr').forEach(row => {
            row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
        });
    });
}

// ---- Dashboard Quick Action Buttons ----
function initDashboardButtons() {
    const regBtn = document.getElementById('btn-register-asset');
    if (regBtn) regBtn.addEventListener('click', () => navigateTo('view-assets'));
    const bookBtn = document.getElementById('btn-book-resource');
    if (bookBtn) bookBtn.addEventListener('click', () => navigateTo('view-booking'));
    const reqBtn = document.getElementById('btn-raise-request');
    if (reqBtn) reqBtn.addEventListener('click', () => navigateTo('view-allocation'));
}

// ---- Booking Form Show/Hide ----
function showBookingForm() {
    const form = document.getElementById('booking-form-area');
    if (form) form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

// ---- New Audit Form Show/Hide ----
function showNewAuditForm() {
    const form = document.getElementById('new-audit-form-area');
    if (form) form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

// ---- Demo helpers for non-critical buttons ----
function demoOrgAdd(btn) {
    const originalText = btn.textContent;
    btn.textContent = '✓ Added';
    btn.disabled = true;
    setTimeout(() => { btn.textContent = originalText; btn.disabled = false; }, 2000);
}

function demoRegisterAsset(btn) {
    const originalText = btn.textContent;
    btn.textContent = '✓ Registered';
    btn.disabled = true;
    setTimeout(() => { btn.textContent = originalText; btn.disabled = false; }, 2000);
}

function demoToggleFilter(btn) {
    btn.classList.toggle('btn-primary');
}

// ---- Init on DOM Ready ----
document.addEventListener('DOMContentLoaded', () => {
    initOrgTabs();
    initNotificationTabs();
    initAssetSearch();
    initDashboardButtons();

    // Data fetching
    loadDashboard();
    loadAssets();
    loadDepartments();
    loadEmployees();
    loadAllocations();
    loadBookingAssets();
    loadMaintenance();
    loadAudits();
});

// =====================================================
// API Utilities
// =====================================================
const API_BASE = '/api';

async function fetchAPI(endpoint, options = {}) {
    try {
        const res = await fetch(`${API_BASE}${endpoint}`, options);
        if (!res.ok) {
            const errorBody = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(errorBody.detail || res.statusText);
        }
        return await res.json();
    } catch (err) {
        console.error(`API error [${endpoint}]:`, err);
        return null;
    }
}

async function fetchAPIWithError(endpoint, options = {}) {
    const res = await fetch(`${API_BASE}${endpoint}`, options);
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    if (!res.ok) throw new Error(body.detail || res.statusText);
    return body;
}

// =====================================================
// Dashboard — READS /api/dashboard
// =====================================================
async function loadDashboard() {
    const stats = await fetchAPI('/dashboard');
    if (!stats) return;
    const cards = document.querySelectorAll('#view-dashboard .card-value');
    if (cards.length >= 6) {
        cards[0].textContent = stats.available;
        cards[1].textContent = stats.allocated;
        cards[2].textContent = stats.maintenance;
        cards[3].textContent = stats.active_bookings;
        cards[4].textContent = stats.pending_transfers;
        cards[5].textContent = stats.upcoming_returns || 0;
    }
}

// =====================================================
// Assets — READS /api/assets
// =====================================================
async function loadAssets() {
    const assets = await fetchAPI('/assets');
    if (!assets) return;

    const tbody = document.getElementById('asset-table-body');
    if (!tbody) return;

    tbody.innerHTML = '';
    assets.forEach(asset => {
        let badgeClass = 'green';
        if (asset.state === 'allocated') badgeClass = 'blue';
        else if (asset.state === 'maintenance') badgeClass = 'yellow';
        else if (asset.state === 'retired' || asset.state === 'disposed') badgeClass = 'gray';
        else if (asset.state === 'lost') badgeClass = 'red';

        tbody.innerHTML += `
            <tr>
                <td class="mono">${asset.asset_tag}</td>
                <td>${asset.name}</td>
                <td>${asset.category ? asset.category.name : '–'}</td>
                <td><span class="badge ${badgeClass}">${asset.state}</span></td>
                <td>${asset.location || '–'}</td>
            </tr>
        `;
    });
}

// =====================================================
// Departments — READS /api/departments
// =====================================================
async function loadDepartments() {
    const depts = await fetchAPI('/departments');
    if (!depts) return;

    // Org setup table
    const tableContainer = document.querySelector('#view-org-setup .tab-panel .table-container tbody');
    if (tableContainer) {
        tableContainer.innerHTML = '';
        depts.forEach(dept => {
            const badgeClass = dept.active ? 'green' : 'gray';
            const status = dept.active ? 'Active' : 'Inactive';
            tableContainer.innerHTML += `
                <tr>
                    <td>${dept.name}</td>
                    <td>${dept.code || '–'}</td>
                    <td>–</td>
                    <td><span class="badge ${badgeClass}">${status}</span></td>
                </tr>
            `;
        });
    }

    // Audit dept dropdown
    const auditDeptSelect = document.getElementById('audit-dept-select');
    if (auditDeptSelect) {
        auditDeptSelect.innerHTML = '<option value="">All Departments</option>';
        depts.forEach(d => {
            auditDeptSelect.innerHTML += `<option value="${d.id}">${d.name}</option>`;
        });
    }
}

// =====================================================
// Employees — READS /api/employees, populates dropdowns
// =====================================================
async function loadEmployees() {
    const emps = await fetchAPI('/employees');
    if (!emps) return;

    // Populate all employee selects
    const selects = [
        'transfer-to-select',
        'transfer-from-select',
        'booking-employee-select',
        'audit-auditor-select',
    ];
    selects.forEach(id => {
        const sel = document.getElementById(id);
        if (!sel) return;
        const firstOption = sel.querySelector('option:first-child');
        sel.innerHTML = firstOption ? firstOption.outerHTML : '<option value="">Select...</option>';
        emps.forEach(emp => {
            sel.innerHTML += `<option value="${emp.id}">${emp.name}${emp.department ? ' — ' + emp.department.name : ''}</option>`;
        });
    });

    // Transfer asset dropdown — also load assets
    loadTransferAssets();
}

// =====================================================
// Allocation & Transfer
// =====================================================

// READS /api/assets → populates the asset selector in the transfer form
async function loadTransferAssets() {
    const assets = await fetchAPI('/assets');
    if (!assets) return;
    const sel = document.getElementById('transfer-asset-select');
    if (!sel) return;
    sel.innerHTML = '<option value="">Select Asset...</option>';
    assets.forEach(a => {
        sel.innerHTML += `<option value="${a.id}" data-state="${a.state}" data-employee="${a.current_employee_id || ''}">${a.asset_tag} — ${a.name} (${a.state})</option>`;
    });
    sel.addEventListener('change', () => {
        const opt = sel.options[sel.selectedIndex];
        const banner = document.getElementById('allocation-status-banner');
        if (banner) {
            if (opt.value && opt.dataset.state === 'allocated') {
                banner.style.display = 'block';
                banner.textContent = '⛔ Asset is currently allocated. Submit a transfer request below to reassign it.';
            } else {
                banner.style.display = 'none';
            }
        }
    });
}

// READS /api/requests → allocation history
async function loadAllocations() {
    const historyDiv = document.getElementById('allocation-history');
    if (!historyDiv) return;
    const reqs = await fetchAPI('/requests');
    if (!reqs) return;
    historyDiv.innerHTML = '';
    if (reqs.length === 0) {
        historyDiv.innerHTML = '<div style="color: var(--color-dark-500);">No allocation/transfer history found.</div>';
        return;
    }
    reqs.slice(0, 20).forEach(req => {
        let icon = '↔';
        let color = 'var(--color-info)';
        if (req.request_type === 'allocation') { icon = '✚'; color = 'var(--color-success)'; }
        if (req.request_type === 'return') { icon = '↩'; color = 'var(--color-warning)'; }
        historyDiv.innerHTML += `
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                <span style="color:${color}; font-size:1rem;">${icon}</span>
                <span><strong>${req.request_type.toUpperCase()}</strong> — ${req.notes || '–'}</span>
                <span class="badge ${req.state === 'submitted' ? 'yellow' : req.state === 'done' ? 'green' : 'gray'}" style="margin-left:auto;">${req.state}</span>
            </div>
        `;
    });
}

/**
 * WRITES to /api/requests/transfer — creates a real transfer request in the DB.
 * Fields: asset_id (from dropdown), from_employee_id (from dropdown), to_employee_id, reason.
 * ✅ REAL DATABASE WRITE
 */
async function submitTransferReal() {
    const btn = document.getElementById('btn-submit-transfer');
    const assetId = parseInt(document.getElementById('transfer-asset-select').value);
    const fromId = parseInt(document.getElementById('transfer-from-select').value);
    const toId = parseInt(document.getElementById('transfer-to-select').value);
    const reason = document.getElementById('transfer-reason').value;

    if (!assetId || !fromId || !toId) {
        alert('Please select an asset, the current employee (From), and the target employee (To).');
        return;
    }
    if (fromId === toId) {
        alert('From and To employees must be different.');
        return;
    }

    btn.textContent = 'Submitting...';
    btn.disabled = true;

    try {
        await fetchAPIWithError('/requests/transfer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                asset_id: assetId,
                from_employee_id: fromId,
                to_employee_id: toId,
                reason: reason || 'Transfer request'
            })
        });
        btn.textContent = '✓ Request Submitted';
        btn.style.background = 'var(--color-success-bg)';
        btn.style.color = 'var(--color-success-dark)';
        document.getElementById('transfer-success-note').style.display = 'block';
        loadAllocations();
        loadDashboard();
    } catch (err) {
        btn.textContent = 'Submit Transfer Request';
        btn.disabled = false;
        alert('Transfer failed: ' + err.message);
    }
}

// =====================================================
// Resource Booking
// =====================================================

// READS /api/assets → populates bookable resource dropdown (is_shared or category_type contains "resource")
async function loadBookingAssets() {
    const assets = await fetchAPI('/assets');
    if (!assets) return;
    const sel = document.getElementById('booking-asset-select');
    if (!sel) return;
    sel.innerHTML = '<option value="">Select a bookable resource...</option>';
    // Show all assets — ideally filter to is_shared or bookable category
    assets.forEach(a => {
        sel.innerHTML += `<option value="${a.id}">${a.asset_tag} — ${a.name}${a.location ? ' (' + a.location + ')' : ''}</option>`;
    });
    sel.addEventListener('change', () => {
        if (sel.value) loadBookings(parseInt(sel.value));
    });
}

// READS /api/bookings → filters by asset_id and renders timeline
async function loadBookings(assetId = null) {
    const timeline = document.getElementById('booking-timeline');
    if (!timeline) return;
    const bookings = await fetchAPI('/bookings');
    if (!bookings) return;

    const filtered = assetId ? bookings.filter(b => b.asset_id === assetId) : bookings;
    timeline.innerHTML = '';

    if (filtered.length === 0) {
        timeline.innerHTML = '<div style="color: var(--color-dark-500); font-size: 0.85rem;">No bookings found for this resource.</div>';
        return;
    }

    filtered.sort((a, b) => new Date(a.start_datetime) - new Date(b.start_datetime));
    filtered.forEach(b => {
        const start = new Date(b.start_datetime).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' });
        const end = new Date(b.end_datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        let stateColor = 'var(--color-info)';
        if (b.state === 'done') stateColor = 'var(--color-success)';
        if (b.state === 'cancelled') stateColor = 'var(--color-dark-500)';

        let cancelBtn = '';
        if (b.state === 'confirmed') {
            cancelBtn = `<button style="margin-left:8px; padding:2px 8px; font-size:0.75rem; background:transparent; border:1px solid var(--color-danger); color:var(--color-danger); border-radius:4px; cursor:pointer;" onclick="cancelBooking(${b.id})">Cancel</button>`;
        }

        timeline.innerHTML += `
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px; font-size: 0.85rem;">
                <div style="width: 55px; color: var(--color-dark-500); font-size:0.78rem;">${start}</div>
                <div style="flex: 1; background: ${stateColor}; padding: 8px 12px; border-radius: 4px; color: white; font-weight: 500; opacity: ${b.state === 'cancelled' ? '0.5' : '1'};">
                    ${b.purpose || '(No purpose)'} — until ${end}
                    <span style="font-size:0.78rem; opacity:0.8; margin-left:4px;">[${b.state}]</span>
                    ${b.employee ? '· ' + b.employee.name : ''}
                </div>
                ${cancelBtn}
            </div>
        `;
    });
}

/**
 * WRITES to /api/bookings — creates a confirmed resource booking in the DB.
 * Required fields: asset_id (from selector), employee_id (from selector), start/end datetime, purpose, name.
 * Validates overlap via the backend (returns 400 if overlap exists).
 * ✅ REAL DATABASE WRITE
 */
async function submitBookingReal(btn) {
    const assetId = parseInt(document.getElementById('booking-asset-select').value);
    const employeeId = parseInt(document.getElementById('booking-employee-select').value);
    const start = document.getElementById('booking-start').value;
    const end = document.getElementById('booking-end').value;
    const purpose = document.getElementById('booking-purpose').value.trim();
    const errorDiv = document.getElementById('booking-error');

    if (errorDiv) errorDiv.style.display = 'none';

    if (!assetId || !employeeId || !start || !end || !purpose) {
        if (errorDiv) { errorDiv.textContent = 'Please fill in all fields.'; errorDiv.style.display = 'block'; }
        return;
    }
    if (new Date(start) >= new Date(end)) {
        if (errorDiv) { errorDiv.textContent = 'End time must be after start time.'; errorDiv.style.display = 'block'; }
        return;
    }

    btn.textContent = 'Confirming...';
    btn.disabled = true;

    // Generate a booking name from purpose + asset
    const assetSel = document.getElementById('booking-asset-select');
    const assetLabel = assetSel.options[assetSel.selectedIndex].text.split(' — ')[0];
    const bookingName = `BKG-${assetLabel}-${new Date(start).toISOString().slice(0, 10)}`;

    try {
        await fetchAPIWithError('/bookings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: bookingName,
                asset_id: assetId,
                employee_id: employeeId,
                start_datetime: start,
                end_datetime: end,
                purpose: purpose
            })
        });

        btn.textContent = '✓ Booking Confirmed';
        setTimeout(() => {
            document.getElementById('booking-form-area').style.display = 'none';
            btn.textContent = 'Confirm Booking';
            btn.disabled = false;
            loadBookings(assetId);
            loadDashboard();
        }, 1500);
    } catch (err) {
        btn.textContent = 'Confirm Booking';
        btn.disabled = false;
        if (errorDiv) { errorDiv.textContent = 'Booking failed: ' + err.message; errorDiv.style.display = 'block'; }
    }
}

/**
 * WRITES to /api/bookings/{id}/state — sets state to "cancelled" in the DB.
 * ✅ REAL DATABASE WRITE
 */
async function cancelBooking(bookingId) {
    if (!confirm('Cancel this booking?')) return;
    const result = await fetchAPI(`/bookings/${bookingId}/state`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state: 'cancelled' })
    });
    if (result) {
        const assetSel = document.getElementById('booking-asset-select');
        const assetId = assetSel ? parseInt(assetSel.value) : null;
        loadBookings(assetId);
        loadDashboard();
    }
}

// =====================================================
// Maintenance — Kanban board
// =====================================================

// READS /api/maintenance → renders kanban cards with Start / Resolve action buttons
async function loadMaintenance() {
    const items = await fetchAPI('/maintenance');
    if (!items) return;
    const cols = {
        'pending': document.getElementById('mnt-pending'),
        'in_progress': document.getElementById('mnt-in_progress'),
        'resolved': document.getElementById('mnt-resolved')
    };

    // Clear content but keep headers
    Object.values(cols).forEach(c => {
        if (c) {
            const header = c.querySelector('.kanban-header');
            c.innerHTML = '';
            if (header) c.appendChild(header);
        }
    });

    if (items.length === 0) {
        const pending = cols['pending'];
        if (pending) pending.innerHTML += '<div style="font-size:0.85rem; color:var(--color-dark-500); padding:8px;">No pending items.</div>';
        return;
    }

    items.forEach(item => {
        // Route items to correct column; fall back to pending if unknown state
        const col = cols[item.state] || cols['pending'];
        if (!col) return;

        let badge = 'yellow';
        if (item.state === 'resolved') badge = 'green';
        else if (item.state === 'in_progress') badge = 'blue';
        else if (item.state === 'cancelled') badge = 'gray';

        let priorityColor = 'var(--color-dark-500)';
        if (item.priority === 'high') priorityColor = 'var(--color-warning)';
        if (item.priority === 'critical') priorityColor = 'var(--color-danger)';

        /**
         * "Start" button → WRITES PUT /api/maintenance/{id}/state with state=in_progress ✅
         * "Resolve" button → WRITES PUT /api/maintenance/{id}/state with state=resolved ✅
         */
        let actionHtml = '';
        if (item.state === 'pending' || item.state === 'approved' || item.state === 'assigned') {
            actionHtml = `<button class="btn btn-primary" style="margin-top:8px; padding:4px 8px; font-size:0.75rem;" onclick="updateMaintenance(${item.id}, 'in_progress')">▶ Start</button>`;
        } else if (item.state === 'in_progress') {
            actionHtml = `<button class="btn btn-success" style="margin-top:8px; padding:4px 8px; font-size:0.75rem;" onclick="updateMaintenance(${item.id}, 'resolved')">✓ Resolve</button>`;
        }

        col.innerHTML += `
            <div class="kanban-card">
                <div class="kanban-card-title">${item.name}</div>
                <div style="font-size: 0.78rem; color: var(--color-dark-500); margin-top: 4px;">${item.description || ''}</div>
                ${item.asset ? `<div style="font-size:0.78rem; color:var(--color-dark-400); margin-top:2px;">Asset: ${item.asset.asset_tag} — ${item.asset.name}</div>` : ''}
                <div style="margin-top: 8px; display:flex; gap:6px; align-items:center;">
                    <span class="badge ${badge}">${item.state}</span>
                    <span style="font-size:0.75rem; color:${priorityColor}; text-transform:uppercase;">${item.priority}</span>
                </div>
                ${actionHtml}
            </div>
        `;
    });
}

/**
 * WRITES to PUT /api/maintenance/{id}/state — updates maintenance state in the DB.
 * Called by "Start" (→ in_progress) and "Resolve" (→ resolved) buttons on kanban cards.
 * ✅ REAL DATABASE WRITE
 */
async function updateMaintenance(id, newState) {
    const result = await fetchAPI(`/maintenance/${id}/state`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state: newState })
    });
    if (result) loadMaintenance();
}

// =====================================================
// Audits
// =====================================================

// In-memory cache of all loaded audits
let _allAudits = [];

// READS /api/audits → populates the audit selector dropdown and cached array
async function loadAudits() {
    const audits = await fetchAPI('/audits');
    if (!audits) return;
    _allAudits = audits;

    const sel = document.getElementById('audit-select');
    if (!sel) return;
    sel.innerHTML = '<option value="">Choose an audit...</option>';
    audits.forEach(a => {
        const stateBadge = a.state === 'completed' ? ' ✓' : a.state === 'in_progress' ? ' ●' : '';
        sel.innerHTML += `<option value="${a.id}">${a.name}${stateBadge} (${a.state})</option>`;
    });

    // Auto-select the first non-completed audit
    const active = audits.find(a => a.state !== 'completed' && a.state !== 'cancelled');
    if (active) {
        sel.value = active.id;
        renderAuditDetail(active);
    }
}

// Renders the selected audit's detail (header + lines table)
function onAuditSelect() {
    const sel = document.getElementById('audit-select');
    const auditId = parseInt(sel.value);
    if (!auditId) {
        const tbody = document.getElementById('audit-table-body');
        if (tbody) tbody.innerHTML = '<tr><td colspan="3">Select an audit above to view its lines.</td></tr>';
        const badge = document.getElementById('audit-state-badge');
        if (badge) { badge.textContent = '–'; badge.className = 'badge gray'; }
        return;
    }
    const audit = _allAudits.find(a => a.id === auditId);
    if (audit) renderAuditDetail(audit);
}

function renderAuditDetail(audit) {
    // Update state badge
    const badge = document.getElementById('audit-state-badge');
    if (badge) {
        badge.textContent = audit.state;
        badge.className = 'badge ' + (audit.state === 'completed' ? 'green' : audit.state === 'in_progress' ? 'blue' : audit.state === 'cancelled' ? 'gray' : 'yellow');
    }

    // Update header text
    const header = document.getElementById('audit-detail-header');
    if (header) {
        const planned = audit.planned_date ? `Planned: ${audit.planned_date}` : '';
        const completed = audit.completed_date ? ` | Completed: ${audit.completed_date}` : '';
        header.textContent = `${audit.name}${planned ? ' | ' + planned : ''}${completed}`;
    }

    // Render lines
    const tbody = document.getElementById('audit-table-body');
    if (!tbody) return;
    tbody.innerHTML = '';

    const closeNote = document.getElementById('audit-close-note');
    if (closeNote) closeNote.style.display = 'none';

    if (!audit.lines || audit.lines.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" style="color:var(--color-dark-500);">No asset lines in this audit.</td></tr>';
        const banner = document.getElementById('audit-discrepancy-banner');
        if (banner) banner.style.display = 'none';
        return;
    }

    audit.lines.forEach(line => {
        let color = 'var(--color-dark-500)';
        if (line.status === 'verified') color = 'var(--color-success)';
        if (line.status === 'discrepancy') color = 'var(--color-danger)';

        const assetLabel = line.asset ? `${line.asset.asset_tag} — ${line.asset.name}` : `Asset #${line.asset_id}`;
        const holderLabel = line.expected_employee_id ? `Employee #${line.expected_employee_id}` : '–';

        tbody.innerHTML += `
            <tr>
                <td class="mono">${assetLabel}</td>
                <td>${holderLabel}</td>
                <td>
                    <button class="badge gray" data-id="${line.id}" data-state="${line.status}"
                        style="border: 1px solid ${color}; color: ${color}; background: transparent; cursor: pointer;"
                        onclick="toggleVerificationReal(this)">${line.status}</button>
                </td>
            </tr>
        `;
    });

    updateDiscrepancyBanner();
}

/**
 * WRITES to PUT /api/audits/lines/{id}/status — cycles through pending→verified→discrepancy
 * and persists the change to the DB immediately.
 * ✅ REAL DATABASE WRITE
 */
async function toggleVerificationReal(btn) {
    const states = ['pending', 'verified', 'discrepancy'];
    const labels = { pending: 'pending', verified: 'verified', discrepancy: 'discrepancy' };
    const colors = { pending: 'var(--color-dark-500)', verified: 'var(--color-success)', discrepancy: 'var(--color-danger)' };

    const current = btn.dataset.state || 'pending';
    const next = states[(states.indexOf(current) + 1) % states.length];
    const lineId = btn.dataset.id;

    if (!lineId) return;

    // Optimistic update
    btn.dataset.state = next;
    btn.textContent = labels[next];
    btn.style.color = colors[next];
    btn.style.borderColor = colors[next];

    const result = await fetchAPI(`/audits/lines/${lineId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: next })
    });

    if (!result) {
        // Revert on failure
        btn.dataset.state = current;
        btn.textContent = labels[current];
        btn.style.color = colors[current];
        btn.style.borderColor = colors[current];
    }

    updateDiscrepancyBanner();
}

function updateDiscrepancyBanner() {
    const discCount = document.querySelectorAll('[data-state="discrepancy"]').length;
    const banner = document.getElementById('audit-discrepancy-banner');
    if (banner) {
        banner.style.display = discCount > 0 ? 'block' : 'none';
        const countEl = banner.querySelector('#audit-disc-count');
        if (countEl) countEl.textContent = `${discCount} asset${discCount !== 1 ? 's' : ''} flagged — discrepancy report generated automatically`;
    }
}

/**
 * WRITES to POST /api/audits — creates a new audit record in the DB.
 * ✅ REAL DATABASE WRITE
 */
async function createAuditReal() {
    const name = document.getElementById('audit-name-input').value.trim();
    const deptId = document.getElementById('audit-dept-select').value;
    const auditorId = document.getElementById('audit-auditor-select').value;
    const plannedDate = document.getElementById('audit-planned-date').value;

    if (!name) { alert('Audit name is required.'); return; }

    const payload = {
        name,
        state: 'draft',
        department_id: deptId ? parseInt(deptId) : null,
        auditor_id: auditorId ? parseInt(auditorId) : null,
        planned_date: plannedDate || null,
    };

    try {
        const created = await fetchAPIWithError('/audits', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        document.getElementById('new-audit-form-area').style.display = 'none';
        document.getElementById('audit-name-input').value = '';
        await loadAudits();
        // Select the newly created audit
        const sel = document.getElementById('audit-select');
        if (sel && created.id) {
            sel.value = created.id;
            onAuditSelect();
        }
    } catch (err) {
        alert('Failed to create audit: ' + err.message);
    }
}

/**
 * WRITES to POST /api/audits/{id}/close — marks the selected audit as "completed" in the DB.
 * Uses the currently selected audit from the dropdown (not hardcoded ID 1).
 * ✅ REAL DATABASE WRITE
 */
async function closeAuditCycle() {
    const sel = document.getElementById('audit-select');
    const auditId = sel ? parseInt(sel.value) : null;

    if (!auditId) {
        alert('Please select an audit to close.');
        return;
    }

    const audit = _allAudits.find(a => a.id === auditId);
    if (audit && audit.state === 'completed') {
        alert('This audit is already closed.');
        return;
    }

    const btn = document.getElementById('btn-close-audit');
    if (!btn) return;
    btn.textContent = 'Closing...';
    btn.disabled = true;

    try {
        await fetchAPIWithError(`/audits/${auditId}/close`, { method: 'POST' });
        btn.textContent = '✓ Audit Closed';
        btn.style.background = 'var(--color-success-bg)';
        btn.style.color = 'var(--color-success-dark)';
        const note = document.getElementById('audit-close-note');
        if (note) note.style.display = 'block';
        await loadAudits();
    } catch (err) {
        btn.textContent = 'Close Audit Cycle';
        btn.disabled = false;
        alert('Failed to close audit: ' + err.message);
    }
}

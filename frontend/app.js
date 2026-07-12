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
    // Deactivate all tabs in the group
    clickedTab.closest('.' + tabGroupClass).querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    clickedTab.classList.add('active');

    // Show the matching content panel
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

    const filterMap = {
        0: null,          // All
        1: 'alert',       // Alerts (red dot)
        2: 'approval',    // Approvals (green dot)
        3: 'booking',     // Bookings
    };

    tabs.forEach((tab, idx) => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            const filter = filterMap[idx];
            items.forEach(item => {
                if (!filter) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = item.dataset.type === filter ? 'flex' : 'none';
                }
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

// ---- Audit Verification Toggles ----
function toggleVerification(btn) {
    const states = ['pending', 'verified', 'discrepancy'];
    const labels = { pending: 'Pending', verified: 'Verified', discrepancy: 'Missing/Damaged' };
    const colors = { pending: '', verified: 'var(--accent-green)', discrepancy: 'var(--accent-red)' };

    let current = btn.dataset.state || 'pending';
    let nextIdx = (states.indexOf(current) + 1) % states.length;
    let next = states[nextIdx];

    btn.dataset.state = next;
    btn.textContent = labels[next];
    btn.style.color = colors[next];
    btn.style.borderColor = colors[next] || 'var(--border-color)';

    // Count discrepancies
    const discCount = document.querySelectorAll('[data-state="discrepancy"]').length;
    const banner = document.getElementById('audit-discrepancy-banner');
    if (banner) {
        banner.style.display = discCount > 0 ? 'flex' : 'none';
        banner.querySelector('#audit-disc-count').textContent = discCount + ' asset' + (discCount > 1 ? 's' : '') + ' flagged — discrepancy report generated automatically';
    }
}

// ---- Booking Slot Demo ----
function showBookingForm() {
    const form = document.getElementById('booking-form-area');
    if (form) form.style.display = form.style.display === 'none' ? 'block' : 'none';
}

// ---- Submit Transfer ----
function submitTransferRequest() {
    const btn = document.getElementById('btn-submit-transfer');
    if (!btn) return;
    btn.textContent = '✓ Request Submitted';
    btn.disabled = true;
    btn.style.background = 'rgba(16,185,129,0.3)';
    btn.style.color = '#34d399';

    // Show success note
    const note = document.getElementById('transfer-success-note');
    if (note) note.style.display = 'block';
}

// ---- Close Audit ----
function closeAuditCycle() {
    const btn = document.getElementById('btn-close-audit');
    if (!btn) return;
    btn.textContent = '✓ Audit Closed';
    btn.disabled = true;
    btn.style.background = 'rgba(16,185,129,0.3)';
    btn.style.color = '#34d399';

    const note = document.getElementById('audit-close-note');
    if (note) note.style.display = 'block';
}

// ---- Init on DOM Ready ----
document.addEventListener('DOMContentLoaded', () => {
    initOrgTabs();
    initNotificationTabs();
    initAssetSearch();
    initDashboardButtons();
});

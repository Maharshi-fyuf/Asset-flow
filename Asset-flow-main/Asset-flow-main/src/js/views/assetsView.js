// assetsView.js
import { mockService } from '../mocks/mockService.js';
import { showToast, openModal, closeModal } from '../app.js';

export const assetsView = {
  async init() {
    try {
      // 1. Populate category drop-downs dynamically
      await populateCategories();
      
      // 2. Fetch and render Asset List Table
      await renderAssetsTable();

      // 3. Register Event Listeners
      registerListeners();
    } catch (err) {
      console.error('Error rendering asset view:', err);
    }
  }
};

let listenersBound = false;

function registerListeners() {
  if (listenersBound) return;

  // Search filter keyup
  const searchInput = document.getElementById('asset-search');
  if (searchInput) {
    searchInput.addEventListener('input', renderAssetsTable);
  }

  // Category filter change
  const categoryFilter = document.getElementById('asset-category-filter');
  if (categoryFilter) {
    categoryFilter.addEventListener('change', renderAssetsTable);
  }

  // Launch Request Asset Modal button
  const reqBtn = document.getElementById('btn-open-request-modal');
  if (reqBtn) {
    reqBtn.addEventListener('click', () => {
      openModal('modal-asset-request');
    });
  }

  // Request Asset Form Submission
  const reqForm = document.getElementById('form-asset-request');
  if (reqForm) {
    reqForm.addEventListener('submit', handleAssetRequestSubmit);
  }

  listenersBound = true;
}

async function populateCategories() {
  const categories = await mockService.getCategories();
  
  // Update Filter drop-down
  const filterSelect = document.getElementById('asset-category-filter');
  if (filterSelect) {
    // Keep first option (All Categories)
    filterSelect.innerHTML = '<option value="">All Categories</option>' + 
      categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
  }

  // Update Form dropdowns
  const requestSelect = document.getElementById('form-req-category');
  if (requestSelect) {
    requestSelect.innerHTML = categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
  }
}

async function renderAssetsTable() {
  const container = document.getElementById('assets-table-body');
  if (!container) return;

  // Render skeleton loaders initially
  container.innerHTML = Array(3).fill(0).map(() => `
    <tr>
      <td><div class="skeleton skeleton-text" style="width: 80px;"></div></td>
      <td><div class="skeleton skeleton-text" style="width: 140px;"></div></td>
      <td><div class="skeleton skeleton-text" style="width: 100px;"></div></td>
      <td><div class="skeleton skeleton-text" style="width: 70px;"></div></td>
      <td><div class="skeleton skeleton-text" style="width: 90px;"></div></td>
      <td><div class="skeleton skeleton-text" style="width: 60px;"></div></td>
    </tr>
  `).join('');

  const assets = await mockService.getAssets();
  
  // Filter assets based on search criteria
  const searchQuery = document.getElementById('asset-search')?.value.toLowerCase() || '';
  const catFilterId = document.getElementById('asset-category-filter')?.value || '';

  const filteredAssets = assets.filter(asset => {
    const matchesSearch = asset.name.toLowerCase().includes(searchQuery) || 
                          asset.tag_number.toLowerCase().includes(searchQuery);
    const matchesCategory = catFilterId === '' || asset.category_id === parseInt(catFilterId);
    return matchesSearch && matchesCategory;
  });

  if (filteredAssets.length === 0) {
    container.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 32px 0;">No assets match selected filters.</td></tr>`;
    return;
  }

  container.innerHTML = filteredAssets.map(asset => {
    let badgeClass = 'badge-available';
    if (asset.status === 'Allocated') badgeClass = 'badge-allocated';
    else if (asset.status === 'Maintenance') badgeClass = 'badge-maintenance';
    else if (asset.status === 'Retired') badgeClass = 'badge-retired';

    return `
      <tr>
        <td><strong>${asset.tag_number}</strong></td>
        <td>${asset.name}</td>
        <td>${asset.category_name}</td>
        <td><span class="badge ${badgeClass}">${asset.status}</span></td>
        <td>$${asset.purchase_cost.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
        <td>${asset.purchase_date}</td>
      </tr>
    `;
  }).join('');
}

async function handleAssetRequestSubmit(e) {
  e.preventDefault();
  
  const form = e.target;
  const categoryId = form.elements['req-category'].value;
  const urgency = form.elements['req-urgency'].value;
  const startDate = form.elements['req-start-date'].value;
  const endDate = form.elements['req-end-date'].value;
  const justification = form.elements['req-justification'].value;

  if (!startDate || !endDate) {
    showToast('Please fill in both start and end reservation dates.', 'error');
    return;
  }

  if (endDate < startDate) {
    showToast('End Date cannot be before Start Date.', 'error');
    return;
  }

  try {
    await mockService.createRequest({
      employee_id: 4, // Simulated logged in employee
      category_id: categoryId,
      urgency,
      start_date: startDate,
      end_date: endDate,
      justification
    });

    showToast('Asset request submitted successfully for approval.');
    closeModal('modal-asset-request');
    form.reset();

    // Redraw table if currently viewing assets view
    await renderAssetsTable();
  } catch (err) {
    showToast(err.message || 'Failed to submit request.', 'error');
  }
}

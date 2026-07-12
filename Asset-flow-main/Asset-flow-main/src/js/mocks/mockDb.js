// mockDb.js
// Local storage key for persistence
const LOCAL_STORAGE_KEY = 'asset_flow_db';

const initialSeed = {
  departments: [
    { id: 1, name: 'Information Technology', code: 'IT' },
    { id: 2, name: 'Human Resources', code: 'HR' },
    { id: 3, name: 'Finance & Accounts', code: 'FIN' },
    { id: 4, name: 'Marketing & Sales', code: 'MKT' },
    { id: 5, name: 'Operations', code: 'OPS' }
  ],
  employees: [
    { id: 1, name: 'Maharshi Khamar', email: 'maharshi@supernova.com', department_id: 1, role: 'Admin' },
    { id: 2, name: 'Jigar Vighani', email: 'jigar@supernova.com', department_id: 1, role: 'Asset Manager' },
    { id: 3, name: 'Rakshit Dave', email: 'rakshit@supernova.com', department_id: 4, role: 'Department Head' },
    { id: 4, name: 'Jaydev Bunkar', email: 'jaydev@supernova.com', department_id: 5, role: 'Employee' },
    { id: 5, name: 'Anik Roy', email: 'anik@supernova.com', department_id: 2, role: 'Employee' },
    { id: 6, name: 'Priya Sharma', email: 'priya@supernova.com', department_id: 3, role: 'Employee' }
  ],
  categories: [
    { id: 1, name: 'Laptops', code: 'LPT', description: 'Enterprise developer & business notebooks' },
    { id: 2, name: 'Monitors', code: 'MON', description: '4K ultra-wide and dual monitor displays' },
    { id: 3, name: 'Mobile Phones', code: 'PHN', description: 'Company test devices & smartphones' },
    { id: 4, name: 'AV Equipment', code: 'AVM', description: 'Projectors, speakers, and micro-conferencing units' },
    { id: 5, name: 'Vehicles', code: 'VEH', description: 'Company cars and site transit vans' }
  ],
  assets: [
    { id: 1, tag_number: 'AST-LPT-001', name: 'MacBook Pro M3 Max 16"', category_id: 1, status: 'Allocated', purchase_cost: 3499.00, purchase_date: '2025-01-10' },
    { id: 2, tag_number: 'AST-LPT-002', name: 'Dell XPS 15 9530', category_id: 1, status: 'Available', purchase_cost: 2199.00, purchase_date: '2025-02-15' },
    { id: 3, tag_number: 'AST-LPT-003', name: 'Lenovo ThinkPad X1 Carbon', category_id: 1, status: 'Maintenance', purchase_cost: 1899.00, purchase_date: '2024-11-05' },
    { id: 4, tag_number: 'AST-MON-001', name: 'LG 34" Curved UltraWide 4K', category_id: 2, status: 'Allocated', purchase_cost: 699.00, purchase_date: '2025-03-20' },
    { id: 5, tag_number: 'AST-MON-002', name: 'Dell UltraSharp 27" U2724D', category_id: 2, status: 'Available', purchase_cost: 399.00, purchase_date: '2025-03-22' },
    { id: 6, tag_number: 'AST-PHN-001', name: 'iPhone 15 Pro 256GB', category_id: 3, status: 'Allocated', purchase_cost: 1099.00, purchase_date: '2024-09-18' },
    { id: 7, tag_number: 'AST-AVM-001', name: 'Epson Pro EX11000 Projector', category_id: 4, status: 'Available', purchase_cost: 1299.00, purchase_date: '2024-05-12' },
    { id: 8, tag_number: 'AST-VEH-001', name: 'Tesla Model Y Long Range', category_id: 5, status: 'Available', purchase_cost: 47990.00, purchase_date: '2024-08-01' }
  ],
  requests: [
    { id: 1001, employee_id: 4, asset_id: 1, category_id: 1, start_date: '2025-01-11', end_date: '2026-01-11', urgency: 'High', status: 'Approved', justification: 'Required for active software development.' },
    { id: 1002, employee_id: 5, asset_id: null, category_id: 1, start_date: '2026-07-15', end_date: '2026-08-15', urgency: 'Medium', status: 'Pending', justification: 'Client presentation laptops.' },
    { id: 1003, employee_id: 6, asset_id: 4, category_id: 2, start_date: '2025-03-21', end_date: '2026-03-21', urgency: 'Low', status: 'Approved', justification: 'Need wide monitor for financial spreadsheets.' },
    { id: 1004, employee_id: 4, asset_id: null, category_id: 3, start_date: '2026-07-20', end_date: '2026-08-20', urgency: 'High', status: 'Pending', justification: 'App development testing target devices.' }
  ],
  bookings: [
    { id: 501, employee_id: 3, resource_type: 'Room', resource_name: 'Boardroom Alfa (Floor 2)', booking_date: '2026-07-13', start_time: '10:00', end_time: '11:30', status: 'Confirmed' },
    { id: 502, employee_id: 4, resource_type: 'Room', resource_name: 'Huddle Room Beta (Floor 1)', booking_date: '2026-07-13', start_time: '14:00', end_time: '15:00', status: 'Confirmed' },
    { id: 503, employee_id: 1, resource_type: 'Equipment', resource_name: 'Epson Pro EX11000 Projector', booking_date: '2026-07-14', start_time: '09:00', end_time: '12:00', status: 'Confirmed' },
    { id: 504, employee_id: 6, resource_type: 'Vehicle', resource_name: 'Tesla Model Y Long Range', booking_date: '2026-07-15', start_time: '08:00', end_time: '18:00', status: 'Confirmed' }
  ],
  maintenance: [
    { id: 801, asset_id: 3, reported_by: 4, issue_category: 'Hardware Failure', description: 'Screen flashes green line on startup, trackpad unresponsive.', urgency: 'Critical', status: 'In_Progress', technician_id: 2, resolved_date: null },
    { id: 802, asset_id: 1, reported_by: 4, issue_category: 'Software OS Upgrade', description: 'Upgrade macOS to Sequoia and restore local tools.', urgency: 'Low', status: 'Resolved', technician_id: 1, resolved_date: '2025-06-15' },
    { id: 803, asset_id: 6, reported_by: 5, issue_category: 'Physical Damage', description: 'Back camera lens shattered on office desk.', urgency: 'Medium', status: 'Pending', technician_id: null, resolved_date: null }
  ],
  auditCycles: [
    { id: 201, name: 'H1 2026 Asset Inventory', start_date: '2026-06-01', end_date: '2026-06-15', status: 'Completed' },
    { id: 202, name: 'Q3 2026 High Value Audits', start_date: '2026-09-01', end_date: '2026-09-07', status: 'Scheduled' }
  ],
  auditRecords: [
    { id: 301, audit_cycle_id: 201, asset_id: 1, auditor_id: 2, verified_date: '2026-06-05', status: 'Verified', notes: 'Excellent condition, employee confirmed.' },
    { id: 302, audit_cycle_id: 201, asset_id: 3, auditor_id: 2, verified_date: '2026-06-05', status: 'Discrepancy', notes: 'Reported under maintenance but physical laptop not found in IT closet.' }
  ],
  history: [
    { id: 1, asset_id: 1, employee_id: 4, allocated_date: '2025-01-11', returned_date: null, transfer_type: 'Initial' },
    { id: 2, asset_id: 4, employee_id: 6, allocated_date: '2025-03-21', returned_date: null, transfer_type: 'Initial' },
    { id: 3, asset_id: 6, employee_id: 5, allocated_date: '2024-09-18', returned_date: '2025-04-12', transfer_type: 'Return' }
  ]
};

// Initialize DB in LocalStorage if empty
export function getDb() {
  let db = localStorage.getItem(LOCAL_STORAGE_KEY);
  if (!db) {
    saveDb(initialSeed);
    return initialSeed;
  }
  return JSON.parse(db);
}

export function saveDb(data) {
  localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(data));
}

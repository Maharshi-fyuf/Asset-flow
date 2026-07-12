// mockService.js
import { getDb, saveDb } from './mockDb.js';

// Helper to simulate API network delay
const delay = (ms = 200) => new Promise(resolve => setTimeout(resolve, ms));

export const mockService = {
  // Master Data
  async getDepartments() {
    await delay();
    return getDb().departments;
  },

  async getEmployees() {
    await delay();
    const db = getDb();
    return db.employees.map(emp => {
      const dept = db.departments.find(d => d.id === emp.department_id);
      return { ...emp, department_name: dept ? dept.name : 'Unassigned' };
    });
  },

  async getCategories() {
    await delay();
    return getDb().categories;
  },

  // Assets Management
  async getAssets() {
    await delay();
    const db = getDb();
    return db.assets.map(asset => {
      const cat = db.categories.find(c => c.id === asset.category_id);
      return { ...asset, category_name: cat ? cat.name : 'Unknown' };
    });
  },

  async addAsset(assetData) {
    await delay();
    const db = getDb();
    const newId = db.assets.length ? Math.max(...db.assets.map(a => a.id)) + 1 : 1;
    const newAsset = {
      id: newId,
      tag_number: assetData.tag_number || `AST-${Date.now().toString().slice(-4)}`,
      name: assetData.name,
      category_id: parseInt(assetData.category_id),
      status: assetData.status || 'Available',
      purchase_cost: parseFloat(assetData.purchase_cost) || 0.0,
      purchase_date: assetData.purchase_date || new Date().toISOString().split('T')[0]
    };
    db.assets.push(newAsset);
    saveDb(db);
    return newAsset;
  },

  async updateAssetStatus(assetId, status) {
    await delay();
    const db = getDb();
    const asset = db.assets.find(a => a.id === parseInt(assetId));
    if (asset) {
      asset.status = status;
      saveDb(db);
      return asset;
    }
    throw new Error('Asset not found');
  },

  // Asset Requests & Lifecycle
  async getRequests() {
    await delay();
    const db = getDb();
    return db.requests.map(req => {
      const emp = db.employees.find(e => e.id === req.employee_id);
      const cat = db.categories.find(c => c.id === req.category_id);
      const asset = req.asset_id ? db.assets.find(a => a.id === req.asset_id) : null;
      return {
        ...req,
        employee_name: emp ? emp.name : 'Unknown',
        category_name: cat ? cat.name : 'Unknown',
        asset_name: asset ? asset.name : 'Not Assigned',
        asset_tag: asset ? asset.tag_number : 'N/A'
      };
    });
  },

  async createRequest(reqData) {
    await delay();
    const db = getDb();
    const newId = db.requests.length ? Math.max(...db.requests.map(r => r.id)) + 1 : 1001;
    const newReq = {
      id: newId,
      employee_id: parseInt(reqData.employee_id) || 4, // Default mock employee if unselected
      asset_id: reqData.asset_id ? parseInt(reqData.asset_id) : null,
      category_id: parseInt(reqData.category_id),
      start_date: reqData.start_date,
      end_date: reqData.end_date,
      urgency: reqData.urgency || 'Medium',
      status: 'Pending',
      justification: reqData.justification || ''
    };
    db.requests.push(newReq);
    saveDb(db);
    return newReq;
  },

  async approveRequest(requestId, assetId) {
    await delay();
    const db = getDb();
    const req = db.requests.find(r => r.id === parseInt(requestId));
    const asset = db.assets.find(a => a.id === parseInt(assetId));
    
    if (req && asset) {
      req.status = 'Approved';
      req.asset_id = asset.id;
      asset.status = 'Allocated';
      
      // Log assignment history
      const histId = db.history.length ? Math.max(...db.history.map(h => h.id)) + 1 : 1;
      db.history.push({
        id: histId,
        asset_id: asset.id,
        employee_id: req.employee_id,
        allocated_date: new Date().toISOString().split('T')[0],
        returned_date: null,
        transfer_type: 'Initial'
      });
      
      saveDb(db);
      return req;
    }
    throw new Error('Request or Asset not found');
  },

  async rejectRequest(requestId) {
    await delay();
    const db = getDb();
    const req = db.requests.find(r => r.id === parseInt(requestId));
    if (req) {
      req.status = 'Rejected';
      saveDb(db);
      return req;
    }
    throw new Error('Request not found');
  },

  // Resource Bookings
  async getBookings() {
    await delay();
    const db = getDb();
    return db.bookings.map(bkg => {
      const emp = db.employees.find(e => e.id === bkg.employee_id);
      return {
        ...bkg,
        employee_name: emp ? emp.name : 'Unknown'
      };
    });
  },

  async createBooking(bookingData) {
    await delay();
    const db = getDb();

    // Check for room/timeslot overlaps
    const hasOverlap = db.bookings.some(b => 
      b.status === 'Confirmed' &&
      b.resource_name === bookingData.resource_name &&
      b.booking_date === bookingData.booking_date &&
      !(bookingData.end_time <= b.start_time || bookingData.start_time >= b.end_time)
    );

    if (hasOverlap) {
      throw new Error('Booking conflict detected: The selected time slot is already reserved.');
    }

    const newId = db.bookings.length ? Math.max(...db.bookings.map(b => b.id)) + 1 : 501;
    const newBooking = {
      id: newId,
      employee_id: parseInt(bookingData.employee_id) || 4,
      resource_type: bookingData.resource_type,
      resource_name: bookingData.resource_name,
      booking_date: bookingData.booking_date,
      start_time: bookingData.start_time,
      end_time: bookingData.end_time,
      status: 'Confirmed'
    };

    db.bookings.push(newBooking);
    saveDb(db);
    return newBooking;
  },

  // Maintenance Management
  async getMaintenanceLogs() {
    await delay();
    const db = getDb();
    return db.maintenance.map(maint => {
      const asset = db.assets.find(a => a.id === maint.asset_id);
      const reporter = db.employees.find(e => e.id === maint.reported_by);
      const tech = maint.technician_id ? db.employees.find(e => e.id === maint.technician_id) : null;
      return {
        ...maint,
        asset_name: asset ? asset.name : 'Unknown',
        asset_tag: asset ? asset.tag_number : 'N/A',
        reporter_name: reporter ? reporter.name : 'Unknown',
        technician_name: tech ? tech.name : 'Unassigned'
      };
    });
  },

  async createMaintenanceLog(logData) {
    await delay();
    const db = getDb();
    const newId = db.maintenance.length ? Math.max(...db.maintenance.map(m => m.id)) + 1 : 801;
    const asset = db.assets.find(a => a.id === parseInt(logData.asset_id));
    
    if (!asset) throw new Error('Asset not found');
    
    const newLog = {
      id: newId,
      asset_id: asset.id,
      reported_by: parseInt(logData.reported_by) || 4,
      issue_category: logData.issue_category,
      description: logData.description,
      urgency: logData.urgency || 'Medium',
      status: 'Pending',
      technician_id: null,
      resolved_date: null
    };

    asset.status = 'Maintenance'; // Set asset status directly
    db.maintenance.push(newLog);
    saveDb(db);
    return newLog;
  },

  async updateMaintenanceStatus(logId, status, technicianId = null) {
    await delay();
    const db = getDb();
    const log = db.maintenance.find(m => m.id === parseInt(logId));
    if (log) {
      log.status = status;
      if (technicianId) log.technician_id = parseInt(technicianId);
      if (status === 'Resolved') {
        log.resolved_date = new Date().toISOString().split('T')[0];
        const asset = db.assets.find(a => a.id === log.asset_id);
        if (asset) asset.status = 'Available'; // Mark asset as back available
      }
      saveDb(db);
      return log;
    }
    throw new Error('Maintenance log entry not found');
  },

  // KPI Dashboard Compilation
  async getDashboardKpis() {
    await delay();
    const db = getDb();
    
    const available = db.assets.filter(a => a.status === 'Available').length;
    const allocated = db.assets.filter(a => a.status === 'Allocated').length;
    const maintenance = db.assets.filter(a => a.status === 'Maintenance').length;
    const pendingRequests = db.requests.filter(r => r.status === 'Pending').length;
    const activeBookings = db.bookings.filter(b => b.status === 'Confirmed').length;
    
    // Simple math for compliance rate
    const verified = db.auditRecords.filter(r => r.status === 'Verified').length;
    const totalAudited = db.auditRecords.length;
    const complianceRate = totalAudited ? `${((verified / totalAudited) * 100).toFixed(1)}%` : '100%';

    return {
      assets_available: available,
      assets_allocated: allocated,
      under_maintenance: maintenance,
      pending_requests: pendingRequests,
      active_bookings: activeBookings,
      audit_compliance_rate: complianceRate
    };
  }
};

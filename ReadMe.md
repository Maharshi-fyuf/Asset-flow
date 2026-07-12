# 📦 AssetFlow - Enterprise Asset & Resource Management System

> Odoo Hackathon 2026 Submission

AssetFlow is an Enterprise Asset & Resource Management System designed to help organizations efficiently manage their physical assets, shared resources, maintenance workflows, and audit processes through a centralized ERP platform.

---

# 👥 Team SuperNova

| Name | Role |
|------|------|
| Maharshi Khamar | Team Lead • System Architect • Backend Integration |
| Jigar Vighani | Asset Management Module |
| Rakshit Dave | Dashboard & Frontend |
| Jaydev Bunkar | Maintenance, Booking & Audit Modules |

---

# 📌 Problem Statement

Organizations still rely on spreadsheets and paper records to manage assets such as laptops, furniture, meeting rooms, and equipment.

This results in:

- Lost assets
- Double allocations
- Manual approvals
- Poor maintenance tracking
- Resource booking conflicts
- No centralized reporting

AssetFlow digitizes the complete asset lifecycle while providing approval workflows, maintenance management, resource booking, dashboards, and reporting.

---

# 🎯 Objectives

- Centralize asset management
- Prevent double allocation
- Simplify approval workflows
- Automate maintenance lifecycle
- Enable resource booking
- Maintain audit history
- Provide real-time dashboards
- Improve operational visibility

---

# 🏗 Architecture

The project follows a modular ERP architecture.

```
Authentication
        │
        ▼
Role Based Access Control
        │
        ▼
Master Data
 ├── Departments
 ├── Employees
 ├── Asset Categories
 └── Assets
        │
        ▼
Business Operations
 ├── Asset Requests
 ├── Allocation
 ├── Transfers
 ├── Returns
 ├── Resource Booking
 ├── Maintenance
 └── Audit
        │
        ▼
Reports & Dashboard
```

---

# 📂 Project Structure

```
asset_flow/

├── models/
│   ├── asset.py
│   ├── department.py
│   ├── employee.py
│   ├── asset_category.py
│   ├── asset_request.py
│   ├── maintenance.py
│   ├── booking.py
│   ├── audit.py
│   └── assignment_history.py
│
├── views/
│
├── security/
│
├── reports/
│
├── static/
│
└── data/
```

---

# 🧱 Core Modules

## Authentication

- Login
- Role Based Access
- Session Management

---

## Organization Setup

- Departments
- Employees
- Asset Categories

---

## Asset Management

- Register Assets
- Search Assets
- Asset Lifecycle
- QR Asset Tag
- Allocation History

---

## Asset Allocation

- Request Asset
- Approval Workflow
- Transfer Workflow
- Return Workflow
- Conflict Detection

---

## Resource Booking

- Meeting Rooms
- Projectors
- Vehicles
- Equipment

Features

- Calendar View
- Time Slot Booking
- Overlap Validation

---

## Maintenance

Workflow

```
Pending

↓

Approved

↓

Technician Assigned

↓

In Progress

↓

Resolved
```

---

## Audit

- Audit Cycles
- Auditor Assignment
- Asset Verification
- Discrepancy Reports

---

## Dashboard

KPIs

- Assets Available
- Assets Allocated
- Assets Under Maintenance
- Pending Requests
- Upcoming Returns
- Active Bookings
- Audit Summary

---

# 📊 Reports

- Asset Utilization
- Department Summary
- Maintenance Report
- Audit Report
- Booking Report
- Export CSV

---

# 🔒 User Roles

## Admin

- Manage Organization
- Create Departments
- Assign Roles
- View Reports

---

## Asset Manager

- Register Assets
- Approve Requests
- Manage Maintenance
- Manage Audits

---

## Department Head

- View Department Assets
- Approve Transfers

---

## Employee

- Request Assets
- Return Assets
- Raise Maintenance Requests
- Book Resources

---

# 🔄 Asset Lifecycle

```
Available
      │
      ▼
Allocated
      │
      ├────────► Returned
      │              │
      ▼              ▼
Maintenance     Available
      │
      ▼
Retired
```

---

# ⚙ Business Rules

- Asset cannot be allocated twice.
- Assets under maintenance cannot be allocated.
- Returned assets become Available.
- Booking overlaps are rejected.
- Transfers require approval.
- Every maintenance action is logged.
- Every allocation is recorded in assignment history.
- Audit discrepancies are tracked.

---

# 🚀 Team Responsibilities

## 👑 Maharshi Khamar

- Project Architecture
- Authentication
- RBAC
- Asset Request Workflow
- Integration
- Notifications
- Final Deployment

---

## 👨‍💻 Jigar Vighani

- Departments
- Employees
- Asset Categories
- Asset CRUD
- Search & Filters

---

## 👨‍💻 Rakshit Dave

- Dashboard
- UI Components
- Reports
- Charts
- Responsive Design and dynamic UI

---

## 👨‍💻 Jaydev Bunkar

- Maintenance
- Resource Booking
- Audit Module
- Activity Logs

---

# 🌿 Git Workflow

```
main

│

develop

├── feature/assets
├── feature/dashboard
├── feature/operations
└── feature/auth
```

Rules

- Never push directly to `main`
- Create feature branches
- Open Pull Requests
- Review before merging

---

# 🛠 Technology Stack

- Odoo
- Python
- PostgreSQL
- XML
- JavaScript
- HTML/CSS

---

# ⏳ Hackathon Timeline

| Hour | Goal |
|------|------|
| 1 | Setup & Architecture |
| 2 | Authentication + Master Data |
| 3 | Asset CRUD |
| 4 | Workflows |
| 5 | Maintenance + Booking |
| 6 | Dashboard |
| 7 | Integration & Testing |
| 8 | Deployment & Demo |

---

# 🎯 Demo Flow

1. Login
2. Register Department
3. Register Employee
4. Register Asset
5. Request Asset
6. Approve Request
7. Allocate Asset
8. Raise Maintenance Request
9. Resolve Maintenance
10. Book Meeting Room
11. Run Audit
12. View Dashboard
13. Export Report

---

# 📄 License

This project was developed as part of the **Odoo Hackathon 2026** for educational and competition purposes.

---

## ⭐ Team SuperNova

**Building smarter ERP solutions with clean architecture and real-world workflows.**

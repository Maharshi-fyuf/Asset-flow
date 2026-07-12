# Backend Schema - AssetFlow

This document defines the relational database schema design representing the PostgreSQL data structures backing the AssetFlow application. While the frontend development utilizes client-side mocks, these schemas define the data integrity rules and JSON API shapes.

---

## 1. Entity-Relationship Diagram (ERD)

The ERD below illustrates the entities, key attributes, constraints, and relationships:

```mermaid
erDiagram
    DEPARTMENT ||--o{ EMPLOYEE : "employs"
    ASSET_CATEGORY ||--o{ ASSET : "categorizes"
    EMPLOYEE ||--o{ ASSET_REQUEST : "requests"
    ASSET ||--o{ ASSET_REQUEST : "requested_for"
    EMPLOYEE ||--o{ BOOKING : "reserves"
    ASSET ||--o{ MAINTENANCE_LOG : "requires"
    EMPLOYEE ||--o{ MAINTENANCE_LOG : "reported_by"
    AUDIT_CYCLE ||--o{ AUDIT_RECORD : "contains"
    ASSET ||--o{ AUDIT_RECORD : "verified_in"
    EMPLOYEE ||--o{ AUDIT_RECORD : "audited_by"
    ASSET ||--o{ ASSIGNMENT_HISTORY : "tracked_in"
    EMPLOYEE ||--o{ ASSIGNMENT_HISTORY : "assigned_to"

    DEPARTMENT {
        int id PK
        string name
        string code UNIQUE
    }

    EMPLOYEE {
        int id PK
        string name
        string email UNIQUE
        int department_id FK
        string role "Admin | Manager | DeptHead | Employee"
    }

    ASSET_CATEGORY {
        int id PK
        string name
        string code UNIQUE
        string description
    }

    ASSET {
        int id PK
        string tag_number UNIQUE "QR Asset Code"
        string name
        int category_id FK
        string status "Available | Allocated | Maintenance | Retired"
        decimal purchase_cost
        date purchase_date
    }

    ASSET_REQUEST {
        int id PK
        int employee_id FK
        int asset_id FK "Nullable for Category requests"
        int category_id FK "Requested category"
        date start_date
        date end_date
        string urgency "Low | Medium | High"
        string status "Draft | Pending | Approved | Rejected | Returned"
        text justification
    }

    BOOKING {
        int id PK
        int employee_id FK
        string resource_type "Room | Vehicle | Equipment"
        string resource_name
        date booking_date
        time start_time
        time end_time
        string status "Confirmed | Cancelled"
    }

    MAINTENANCE_LOG {
        int id PK
        int asset_id FK
        int reported_by FK
        string issue_category
        text description
        string urgency "Low | Medium | Critical"
        string status "Pending | Approved | Assigned | In_Progress | Resolved"
        int technician_id FK "Nullable"
        date resolved_date
    }

    AUDIT_CYCLE {
        int id PK
        string name
        date start_date
        date end_date
        string status "Scheduled | Active | Completed"
    }

    AUDIT_RECORD {
        int id PK
        int audit_cycle_id FK
        int asset_id FK
        int auditor_id FK
        date verified_date
        string status "Verified | Discrepancy"
        text notes
    }

    ASSIGNMENT_HISTORY {
        int id PK
        int asset_id FK
        int employee_id FK
        date allocated_date
        date returned_date "Nullable"
        string transfer_type "Initial | Transfer | Return"
    }
```

---

## 2. Table Definitions & Constraints

### 2.1. Organization Setup Tables

```sql
-- Departments table
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Employees table
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    department_id INT REFERENCES departments(id) ON DELETE SET NULL,
    role VARCHAR(30) CHECK (role IN ('Admin', 'Asset Manager', 'Department Head', 'Employee')) DEFAULT 'Employee',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2.2. Asset Inventory Tables

```sql
-- Asset Categories table
CREATE TABLE asset_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Assets table
CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    tag_number VARCHAR(50) UNIQUE NOT NULL, -- Printed QR barcode value
    name VARCHAR(150) NOT NULL,
    category_id INT NOT NULL REFERENCES asset_categories(id) ON DELETE RESTRICT,
    status VARCHAR(20) CHECK (status IN ('Available', 'Allocated', 'Maintenance', 'Retired')) DEFAULT 'Available',
    purchase_cost DECIMAL(10, 2) NOT NULL CHECK (purchase_cost >= 0),
    purchase_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_assets_status ON assets(status);
CREATE INDEX idx_assets_category ON assets(category_id);
```

### 2.3. Operational Tables

```sql
-- Asset Allocation Requests table
CREATE TABLE asset_requests (
    id SERIAL PRIMARY KEY,
    employee_id INT NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    asset_id INT REFERENCES assets(id) ON DELETE SET NULL, -- Null if requesting any category member
    category_id INT NOT NULL REFERENCES asset_categories(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL CHECK (end_date >= start_date),
    urgency VARCHAR(15) CHECK (urgency IN ('Low', 'Medium', 'High')) DEFAULT 'Medium',
    status VARCHAR(20) CHECK (status IN ('Draft', 'Pending', 'Approved', 'Rejected', 'Returned')) DEFAULT 'Pending',
    justification TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resource Bookings table (with overlap validation index helper)
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    employee_id INT NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    resource_type VARCHAR(20) CHECK (resource_type IN ('Room', 'Vehicle', 'Equipment')),
    resource_name VARCHAR(100) NOT NULL,
    booking_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL CHECK (end_time > start_time),
    status VARCHAR(15) CHECK (status IN ('Confirmed', 'Cancelled')) DEFAULT 'Confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_bookings_overlap_check ON bookings(resource_name, booking_date, start_time, end_time);
```

### 2.4. Maintenance & Audit Tables

```sql
-- Maintenance Logs table
CREATE TABLE maintenance_logs (
    id SERIAL PRIMARY KEY,
    asset_id INT NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    reported_by INT NOT NULL REFERENCES employees(id),
    issue_category VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    urgency VARCHAR(15) CHECK (urgency IN ('Low', 'Medium', 'Critical')) DEFAULT 'Medium',
    status VARCHAR(20) CHECK (status IN ('Pending', 'Approved', 'Assigned', 'In_Progress', 'Resolved')) DEFAULT 'Pending',
    technician_id INT REFERENCES employees(id) ON DELETE SET NULL,
    resolved_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit Cycles table
CREATE TABLE audit_cycles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL CHECK (end_date >= start_date),
    status VARCHAR(20) CHECK (status IN ('Scheduled', 'Active', 'Completed')) DEFAULT 'Scheduled'
);

-- Audit Records table
CREATE TABLE audit_records (
    id SERIAL PRIMARY KEY,
    audit_cycle_id INT NOT NULL REFERENCES audit_cycles(id) ON DELETE CASCADE,
    asset_id INT NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    auditor_id INT NOT NULL REFERENCES employees(id),
    verified_date DATE NOT NULL DEFAULT CURRENT_DATE,
    status VARCHAR(20) CHECK (status IN ('Verified', 'Discrepancy')) DEFAULT 'Verified',
    notes TEXT,
    UNIQUE(audit_cycle_id, asset_id)
);
```

### 2.5. Historical Log Table

```sql
-- Assignment History table
CREATE TABLE assignment_history (
    id SERIAL PRIMARY KEY,
    asset_id INT NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    employee_id INT NOT NULL REFERENCES employees(id) ON DELETE RESTRICT,
    allocated_date DATE NOT NULL DEFAULT CURRENT_DATE,
    returned_date DATE CHECK (returned_date >= allocated_date),
    transfer_type VARCHAR(20) CHECK (transfer_type IN ('Initial', 'Transfer', 'Return')) DEFAULT 'Initial'
);
CREATE INDEX idx_assignment_history_asset ON assignment_history(asset_id);
```

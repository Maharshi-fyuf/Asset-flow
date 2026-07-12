import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime, Text, Float
from sqlalchemy.orm import relationship
from .database import Base

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    code = Column(String)
    manager_id = Column(Integer, ForeignKey("employees.id"))
    active = Column(Boolean, default=True)
    notes = Column(Text)

    employees = relationship("Employee", foreign_keys="[Employee.department_id]", back_populates="department")
    assets = relationship("Asset", back_populates="department")

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    manager_id = Column(Integer, ForeignKey("employees.id"))
    job_title = Column(String)
    work_email = Column(String)
    phone = Column(String)
    role = Column(String, default="employee") # employee, department_head, asset_manager, admin
    active = Column(Boolean, default=True)
    notes = Column(Text)

    department = relationship("Department", foreign_keys=[department_id], back_populates="employees")
    assets = relationship("Asset", back_populates="current_employee")
    managed_department = relationship("Department", foreign_keys="[Department.manager_id]", uselist=False)


class AssetCategory(Base):
    __tablename__ = "asset_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    code = Column(String)
    parent_id = Column(Integer, ForeignKey("asset_categories.id"))
    category_type = Column(String, default="asset") # asset, resource, both
    maintenance_required = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    notes = Column(Text)

    assets = relationship("Asset", back_populates="category")

class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    asset_tag = Column(String, unique=True, index=True, nullable=False)
    serial_number = Column(String)
    category_id = Column(Integer, ForeignKey("asset_categories.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    current_employee_id = Column(Integer, ForeignKey("employees.id"))
    state = Column(String, default="available", nullable=False) # available, allocated, reserved, maintenance, retired, lost, disposed
    location = Column(String)
    purchase_date = Column(Date)
    purchase_value = Column(Float)
    notes = Column(Text)
    active = Column(Boolean, default=True)
    is_shared = Column(Boolean, default=False)
    condition = Column(String, default="new") # new, good, fair, poor

    category = relationship("AssetCategory", back_populates="assets")
    department = relationship("Department", back_populates="assets")
    current_employee = relationship("Employee", back_populates="assets")

class AssetRequest(Base):
    __tablename__ = "asset_requests"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    request_type = Column(String, default="allocation", nullable=False) # allocation, transfer, return
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    requested_by_user_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("asset_categories.id"))
    asset_id = Column(Integer, ForeignKey("assets.id"))
    request_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    needed_by_date = Column(Date)
    expected_return_date = Column(Date)
    state = Column(String, default="draft", nullable=False) # draft, submitted, approved, rejected, done, cancelled
    notes = Column(Text)

class Maintenance(Base):
    __tablename__ = "maintenances"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    requested_by_id = Column(Integer, ForeignKey("employees.id"))
    assigned_to_id = Column(Integer, ForeignKey("employees.id"))
    maintenance_type = Column(String, default="corrective", nullable=False) # corrective, preventive, inspection
    priority = Column(String, default="normal", nullable=False) # low, normal, high, critical
    state = Column(String, default="pending", nullable=False) # pending, approved, assigned, in_progress, resolved, cancelled
    request_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    scheduled_date = Column(DateTime)
    resolved_date = Column(DateTime)
    description = Column(Text)
    resolution_notes = Column(Text)

    asset = relationship("Asset")

class ResourceBooking(Base):
    __tablename__ = "resource_bookings"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    state = Column(String, default="draft", nullable=False) # draft, confirmed, done, cancelled
    purpose = Column(String)
    notes = Column(Text)

    asset = relationship("Asset")
    employee = relationship("Employee")

class Audit(Base):
    __tablename__ = "audits"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    auditor_id = Column(Integer, ForeignKey("employees.id"))
    planned_date = Column(Date)
    completed_date = Column(Date)
    state = Column(String, default="draft", nullable=False) # draft, planned, in_progress, completed, cancelled
    notes = Column(Text)

    lines = relationship("AuditLine", back_populates="audit")
    department = relationship("Department")

class AuditLine(Base):
    __tablename__ = "audit_lines"
    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(Integer, ForeignKey("audits.id"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    expected_employee_id = Column(Integer, ForeignKey("employees.id"))
    actual_employee_id = Column(Integer, ForeignKey("employees.id"))
    condition = Column(String, default="good") # good, fair, damaged, missing
    status = Column(String, default="pending") # pending, verified, discrepancy
    notes = Column(Text)

    audit = relationship("Audit", back_populates="lines")
    asset = relationship("Asset")

class AssignmentHistory(Base):
    __tablename__ = "assignment_history"
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    request_id = Column(Integer, ForeignKey("asset_requests.id"))
    assigned_by_user_id = Column(Integer, ForeignKey("employees.id"))
    assigned_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    returned_date = Column(DateTime)
    state = Column(String, default="active", nullable=False) # active, returned, transferred
    notes = Column(Text)

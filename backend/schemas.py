from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class DepartmentBase(BaseModel):
    name: str
    code: Optional[str] = None
    manager_id: Optional[int] = None
    active: bool = True
    notes: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentResponse(DepartmentBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True

class EmployeeBase(BaseModel):
    name: str
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    job_title: Optional[str] = None
    work_email: Optional[str] = None
    phone: Optional[str] = None
    role: str = "employee"
    active: bool = True
    notes: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase):
    id: int
    department: Optional[DepartmentResponse] = None
    class Config:
        orm_mode = True
        from_attributes = True

class AssetCategoryBase(BaseModel):
    name: str
    code: Optional[str] = None
    parent_id: Optional[int] = None
    category_type: str = "asset"
    maintenance_required: bool = False
    active: bool = True
    notes: Optional[str] = None

class AssetCategoryCreate(AssetCategoryBase):
    pass

class AssetCategoryResponse(AssetCategoryBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True

class AssetBase(BaseModel):
    name: str
    asset_tag: str
    serial_number: Optional[str] = None
    category_id: int
    department_id: Optional[int] = None
    current_employee_id: Optional[int] = None
    state: str = "available"
    location: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_value: Optional[float] = None
    notes: Optional[str] = None
    active: bool = True
    is_shared: bool = False
    condition: str = "new"

class AssetCreate(AssetBase):
    pass

class AssetResponse(AssetBase):
    id: int
    category: Optional[AssetCategoryResponse] = None
    current_employee: Optional[EmployeeResponse] = None
    department: Optional[DepartmentResponse] = None
    class Config:
        orm_mode = True
        from_attributes = True

class AssetRequestBase(BaseModel):
    name: str
    request_type: str = "allocation"
    employee_id: int
    requested_by_user_id: int
    category_id: Optional[int] = None
    asset_id: Optional[int] = None
    needed_by_date: Optional[date] = None
    expected_return_date: Optional[date] = None
    state: str = "draft"
    notes: Optional[str] = None

class AssetRequestCreate(AssetRequestBase):
    pass

class AssetRequestResponse(AssetRequestBase):
    id: int
    request_date: datetime
    class Config:
        orm_mode = True
        from_attributes = True

class MaintenanceBase(BaseModel):
    name: str
    asset_id: int
    requested_by_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    maintenance_type: str = "corrective"
    priority: str = "normal"
    state: str = "pending"
    scheduled_date: Optional[datetime] = None
    resolved_date: Optional[datetime] = None
    description: Optional[str] = None
    resolution_notes: Optional[str] = None

class MaintenanceCreate(MaintenanceBase):
    pass

class MaintenanceResponse(MaintenanceBase):
    id: int
    request_date: datetime
    asset: Optional[AssetResponse] = None
    class Config:
        orm_mode = True
        from_attributes = True

class ResourceBookingBase(BaseModel):
    name: str
    asset_id: int
    employee_id: int
    start_datetime: datetime
    end_datetime: datetime
    state: str = "draft"
    purpose: Optional[str] = None
    notes: Optional[str] = None

class ResourceBookingCreate(ResourceBookingBase):
    pass

class ResourceBookingResponse(ResourceBookingBase):
    id: int
    asset: Optional[AssetResponse] = None
    employee: Optional[EmployeeResponse] = None
    class Config:
        orm_mode = True
        from_attributes = True

class AuditLineBase(BaseModel):
    asset_id: int
    expected_employee_id: Optional[int] = None
    actual_employee_id: Optional[int] = None
    condition: str = "good"
    status: str = "pending"
    notes: Optional[str] = None

class AuditLineCreate(AuditLineBase):
    pass

class AuditLineResponse(AuditLineBase):
    id: int
    audit_id: int
    asset: Optional[AssetResponse] = None
    class Config:
        orm_mode = True
        from_attributes = True

class AuditBase(BaseModel):
    name: str
    department_id: Optional[int] = None
    auditor_id: Optional[int] = None
    planned_date: Optional[date] = None
    completed_date: Optional[date] = None
    state: str = "draft"
    notes: Optional[str] = None

class AuditCreate(AuditBase):
    pass

class AuditResponse(AuditBase):
    id: int
    lines: List[AuditLineResponse] = []
    class Config:
        orm_mode = True
        from_attributes = True

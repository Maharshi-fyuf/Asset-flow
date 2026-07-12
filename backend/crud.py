from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime
from . import models, schemas

# Department
def get_departments(db: Session):
    return db.query(models.Department).all()

def create_department(db: Session, department: schemas.DepartmentCreate):
    db_obj = models.Department(**department.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# Employee
def get_employees(db: Session):
    return db.query(models.Employee).all()

def create_employee(db: Session, employee: schemas.EmployeeCreate):
    db_obj = models.Employee(**employee.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# Category
def get_categories(db: Session):
    return db.query(models.AssetCategory).all()

def create_category(db: Session, category: schemas.AssetCategoryCreate):
    db_obj = models.AssetCategory(**category.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# Asset
def get_assets(db: Session):
    return db.query(models.Asset).all()

def create_asset(db: Session, asset: schemas.AssetCreate):
    db_obj = models.Asset(**asset.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# Asset Request
def get_requests(db: Session):
    return db.query(models.AssetRequest).all()

def create_request(db: Session, request: schemas.AssetRequestCreate):
    db_obj = models.AssetRequest(**request.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def transfer_request(db: Session, asset_id: int, from_employee_id: int, to_employee_id: int, reason: str):
    # Dummy handling for transfer request logic
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if asset:
        req = models.AssetRequest(
            name=f"TRF-{asset.asset_tag}",
            request_type="transfer",
            employee_id=to_employee_id,
            requested_by_user_id=from_employee_id,
            asset_id=asset_id,
            state="submitted",
            notes=reason
        )
        db.add(req)
        db.commit()
        db.refresh(req)
        return req
    return None

# Maintenance
def get_maintenance(db: Session):
    return db.query(models.Maintenance).all()

def create_maintenance(db: Session, maintenance: schemas.MaintenanceCreate):
    db_obj = models.Maintenance(**maintenance.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_maintenance_state(db: Session, maintenance_id: int, state: str):
    db_obj = db.query(models.Maintenance).filter(models.Maintenance.id == maintenance_id).first()
    if db_obj:
        db_obj.state = state
        db.commit()
        db.refresh(db_obj)
    return db_obj

# Booking
def get_bookings(db: Session):
    return db.query(models.ResourceBooking).all()

def create_booking(db: Session, booking: schemas.ResourceBookingCreate):
    # Check overlap
    overlapping = db.query(models.ResourceBooking).filter(
        models.ResourceBooking.asset_id == booking.asset_id,
        models.ResourceBooking.state == "confirmed",
        models.ResourceBooking.start_datetime < booking.end_datetime,
        models.ResourceBooking.end_datetime > booking.start_datetime
    ).first()
    if overlapping:
        raise ValueError("Booking overlaps with an existing confirmed booking.")
    
    db_obj = models.ResourceBooking(**booking.dict())
    db_obj.state = "confirmed"  # Auto-confirm on creation
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_booking_state(db: Session, booking_id: int, state: str):
    db_obj = db.query(models.ResourceBooking).filter(models.ResourceBooking.id == booking_id).first()
    if db_obj:
        db_obj.state = state
        db.commit()
        db.refresh(db_obj)
    return db_obj

# Audits
def get_audits(db: Session):
    from sqlalchemy.orm import joinedload
    return db.query(models.Audit).options(joinedload(models.Audit.lines)).all()

def create_audit(db: Session, audit: schemas.AuditCreate):
    db_obj = models.Audit(**audit.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def close_audit(db: Session, audit_id: int):
    import datetime
    audit = db.query(models.Audit).filter(models.Audit.id == audit_id).first()
    if audit:
        audit.state = "completed"
        audit.completed_date = datetime.date.today()
        db.commit()
        db.refresh(audit)
    return audit

def verify_audit_line(db: Session, line_id: int, status: str):
    line = db.query(models.AuditLine).filter(models.AuditLine.id == line_id).first()
    if line:
        line.status = status
        db.commit()
        db.refresh(line)
    return line

# Dashboard Stats
def get_dashboard_stats(db: Session):
    available = db.query(models.Asset).filter(models.Asset.state == "available").count()
    allocated = db.query(models.Asset).filter(models.Asset.state == "allocated").count()
    maintenance = db.query(models.Asset).filter(models.Asset.state == "maintenance").count()
    active_bookings = db.query(models.ResourceBooking).filter(models.ResourceBooking.state == "confirmed").count()
    pending_transfers = db.query(models.AssetRequest).filter(models.AssetRequest.request_type == "transfer", models.AssetRequest.state == "submitted").count()
    
    return {
        "available": available,
        "allocated": allocated,
        "maintenance": maintenance,
        "active_bookings": active_bookings,
        "pending_transfers": pending_transfers,
        "upcoming_returns": 0 # Dummy
    }

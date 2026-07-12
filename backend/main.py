from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AssetFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API Endpoints
@app.get("/api/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    return crud.get_dashboard_stats(db)

@app.get("/api/departments", response_model=List[schemas.DepartmentResponse])
def get_departments(db: Session = Depends(get_db)):
    return crud.get_departments(db)

@app.post("/api/departments", response_model=schemas.DepartmentResponse)
def create_department(department: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    return crud.create_department(db, department)

@app.get("/api/employees", response_model=List[schemas.EmployeeResponse])
def get_employees(db: Session = Depends(get_db)):
    return crud.get_employees(db)

@app.post("/api/employees", response_model=schemas.EmployeeResponse)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    return crud.create_employee(db, employee)

@app.get("/api/categories", response_model=List[schemas.AssetCategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    return crud.get_categories(db)

@app.post("/api/categories", response_model=schemas.AssetCategoryResponse)
def create_category(category: schemas.AssetCategoryCreate, db: Session = Depends(get_db)):
    return crud.create_category(db, category)

@app.get("/api/assets", response_model=List[schemas.AssetResponse])
def get_assets(db: Session = Depends(get_db)):
    return crud.get_assets(db)

@app.post("/api/assets", response_model=schemas.AssetResponse)
def create_asset(asset: schemas.AssetCreate, db: Session = Depends(get_db)):
    return crud.create_asset(db, asset)

@app.get("/api/requests", response_model=List[schemas.AssetRequestResponse])
def get_requests(db: Session = Depends(get_db)):
    return crud.get_requests(db)

@app.post("/api/requests", response_model=schemas.AssetRequestResponse)
def create_request(request: schemas.AssetRequestCreate, db: Session = Depends(get_db)):
    return crud.create_request(db, request)

@app.post("/api/requests/transfer")
def create_transfer_request(
    asset_id: int = Body(...),
    from_employee_id: int = Body(...),
    to_employee_id: int = Body(...),
    reason: str = Body(...),
    db: Session = Depends(get_db)
):
    req = crud.transfer_request(db, asset_id, from_employee_id, to_employee_id, reason)
    if not req:
        raise HTTPException(status_code=400, detail="Transfer failed")
    return req

@app.get("/api/maintenance", response_model=List[schemas.MaintenanceResponse])
def get_maintenance(db: Session = Depends(get_db)):
    return crud.get_maintenance(db)

@app.post("/api/maintenance", response_model=schemas.MaintenanceResponse)
def create_maintenance(maintenance: schemas.MaintenanceCreate, db: Session = Depends(get_db)):
    return crud.create_maintenance(db, maintenance)

@app.put("/api/maintenance/{maintenance_id}/state")
def update_maintenance_state(maintenance_id: int, state: str = Body(..., embed=True), db: Session = Depends(get_db)):
    return crud.update_maintenance_state(db, maintenance_id, state)

@app.get("/api/bookings", response_model=List[schemas.ResourceBookingResponse])
def get_bookings(db: Session = Depends(get_db)):
    return crud.get_bookings(db)

@app.post("/api/bookings", response_model=schemas.ResourceBookingResponse)
def create_booking(booking: schemas.ResourceBookingCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_booking(db, booking)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/bookings/{booking_id}/state")
def update_booking_state(booking_id: int, state: str = Body(..., embed=True), db: Session = Depends(get_db)):
    result = crud.update_booking_state(db, booking_id, state)
    if not result:
        raise HTTPException(status_code=404, detail="Booking not found")
    return result

@app.get("/api/audits", response_model=List[schemas.AuditResponse])
def get_audits(db: Session = Depends(get_db)):
    return crud.get_audits(db)

@app.post("/api/audits", response_model=schemas.AuditResponse)
def create_audit(audit: schemas.AuditCreate, db: Session = Depends(get_db)):
    return crud.create_audit(db, audit)

@app.post("/api/audits/{audit_id}/close")
def close_audit(audit_id: int, db: Session = Depends(get_db)):
    result = crud.close_audit(db, audit_id)
    if not result:
        raise HTTPException(status_code=404, detail="Audit not found")
    return result

@app.put("/api/audits/lines/{line_id}/status")
def verify_audit_line(line_id: int, status: str = Body(..., embed=True), db: Session = Depends(get_db)):
    return crud.verify_audit_line(db, line_id, status)


# Mount frontend static files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(frontend_dir, "index.html"))

    @app.get("/{path:path}")
    def serve_files(path: str):
        file_path = os.path.join(frontend_dir, path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dir, "index.html"))

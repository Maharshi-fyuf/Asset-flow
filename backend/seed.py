from .database import SessionLocal, engine
from . import models
from datetime import datetime, timedelta

def seed_data():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Check if already seeded
    if db.query(models.Department).first():
        print("Database already seeded.")
        return
        
    print("Seeding data...")
    # Departments
    it_dept = models.Department(name="Engineering")
    fac_dept = models.Department(name="Facilities")
    fin_dept = models.Department(name="Finance")
    db.add_all([it_dept, fac_dept, fin_dept])
    db.commit()

    # Employees
    emp1 = models.Employee(name="Maharshi Khamar", department_id=it_dept.id, role="admin", work_email="maharshi@example.com")
    emp2 = models.Employee(name="Jigar Vighani", department_id=it_dept.id, role="employee", work_email="jigar@example.com")
    emp3 = models.Employee(name="Jaydev Bunkar", department_id=fac_dept.id, role="employee", work_email="jaydev@example.com")
    emp4 = models.Employee(name="Priya Shah", department_id=it_dept.id, role="employee", work_email="priya@example.com")
    emp5 = models.Employee(name="Rakshit Dave", department_id=fin_dept.id, role="employee", work_email="rakshit@example.com")
    db.add_all([emp1, emp2, emp3, emp4, emp5])
    db.commit()

    # Categories
    cat_laptop = models.AssetCategory(name="Equipment / Laptops", code="LTP", category_type="asset", maintenance_required=True)
    cat_proj = models.AssetCategory(name="Equipment / Projectors", code="PRJ", category_type="both", maintenance_required=True)
    cat_room = models.AssetCategory(name="Meeting Rooms", code="ROOM", category_type="resource", maintenance_required=False)
    db.add_all([cat_laptop, cat_proj, cat_room])
    db.commit()

    # Assets
    asset1 = models.Asset(name="Dell Laptop", asset_tag="AF-0114", category_id=cat_laptop.id, department_id=it_dept.id, current_employee_id=emp4.id, state="allocated", location="Desk 402")
    asset2 = models.Asset(name="Epson Projector", asset_tag="AF-0042", category_id=cat_proj.id, department_id=fac_dept.id, state="maintenance", location="HQ Floor 2", is_shared=True)
    asset3 = models.Asset(name="Meeting Room Alpha", asset_tag="AF-ROOM-001", category_id=cat_room.id, state="available", location="First Floor", is_shared=True)
    db.add_all([asset1, asset2, asset3])
    db.commit()

    # Maintenance
    m1 = models.Maintenance(name="AF-MNT-00062", asset_id=asset2.id, requested_by_id=emp3.id, state="pending", description="Projector bulb not turning on")
    db.add(m1)
    db.commit()
    
    # Booking
    b1 = models.ResourceBooking(name="BK-001", asset_id=asset3.id, employee_id=emp1.id, start_datetime=datetime.now() - timedelta(hours=1), end_datetime=datetime.now() + timedelta(hours=1), state="confirmed", purpose="Sprint Review")
    db.add(b1)
    db.commit()
    
    print("Seeding complete.")
    db.close()

if __name__ == "__main__":
    seed_data()

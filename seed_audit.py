from backend.database import SessionLocal
from backend import models

db = SessionLocal()
audit = models.Audit(name='Q3 Audit - Engineering Dept', state='in_progress')
db.add(audit)
db.commit()
db.refresh(audit)

l1 = models.AuditLine(audit_id=audit.id, asset_id=1, expected_employee_id=4, status='pending')
l2 = models.AuditLine(audit_id=audit.id, asset_id=2, expected_employee_id=3, status='pending')
db.add_all([l1, l2])
db.commit()
print('Audit seeded')
db.close()

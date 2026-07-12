from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AssetFlowReportWizard(models.TransientModel):
    _name = "asset.flow.report.wizard"
    _description = "AssetFlow Report Wizard"

    report_type = fields.Selection(
        [
            ("asset_utilization", "Asset Utilization Report"),
            ("department_summary", "Department Asset Summary"),
            ("maintenance", "Maintenance Report"),
            ("audit", "Audit Report"),
            ("booking", "Resource Booking Report"),
        ],
        required=True,
        default="asset_utilization",
        string="Report Type",
    )
    date_from = fields.Date(string="From Date")
    date_to = fields.Date(string="To Date")
    department_id = fields.Many2one("asset.flow.department", string="Department")
    category_id = fields.Many2one("asset.flow.asset.category", string="Category")
    employee_id = fields.Many2one("asset.flow.employee", string="Employee")

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
                raise ValidationError("'From Date' must be before 'To Date'.")

    def action_generate_report(self):
        """Generate a PDF report based on the selected report type."""
        self.ensure_one()

        # Build domain filters
        domain = []
        if self.department_id:
            domain.append(("department_id", "=", self.department_id.id))
        if self.category_id:
            domain.append(("category_id", "=", self.category_id.id))

        date_domain = []
        if self.date_from:
            date_domain.append(("create_date", ">=", fields.Datetime.to_datetime(self.date_from)))
        if self.date_to:
            date_domain.append(("create_date", "<=", fields.Datetime.to_datetime(self.date_to)))

        # Store context for the report template
        data = {
            "report_type": self.report_type,
            "date_from": self.date_from and str(self.date_from) or False,
            "date_to": self.date_to and str(self.date_to) or False,
            "department_id": self.department_id.id if self.department_id else False,
            "department_name": self.department_id.name if self.department_id else "All Departments",
            "category_id": self.category_id.id if self.category_id else False,
            "employee_id": self.employee_id.id if self.employee_id else False,
        }

        if self.report_type == "asset_utilization":
            asset_domain = list(domain)
            assets = self.env["asset.flow.asset"].search(asset_domain)
            data["record_ids"] = assets.ids
        elif self.report_type == "department_summary":
            assets = self.env["asset.flow.asset"].search(domain)
            data["record_ids"] = assets.ids
        elif self.report_type == "maintenance":
            maint_domain = []
            if self.department_id:
                maint_domain.append(("department_id", "=", self.department_id.id))
            maint_domain.extend(date_domain)
            records = self.env["asset.flow.maintenance"].search(maint_domain)
            data["record_ids"] = records.ids
        elif self.report_type == "audit":
            audit_domain = []
            if self.department_id:
                audit_domain.append(("department_id", "=", self.department_id.id))
            audit_domain.extend(date_domain)
            records = self.env["asset.flow.audit"].search(audit_domain)
            data["record_ids"] = records.ids
        elif self.report_type == "booking":
            booking_domain = []
            if self.department_id:
                booking_domain.append(("department_id", "=", self.department_id.id))
            booking_domain.extend(date_domain)
            records = self.env["asset.flow.resource.booking"].search(booking_domain)
            data["record_ids"] = records.ids

        return self.env.ref("asset_flow.action_report_asset_flow").report_action(self, data=data)

    def get_report_title(self):
        """Returns a human-readable title for the report header."""
        self.ensure_one()
        titles = dict(self.fields_get(["report_type"])["report_type"]["selection"])
        return titles.get(self.report_type, self.report_type)

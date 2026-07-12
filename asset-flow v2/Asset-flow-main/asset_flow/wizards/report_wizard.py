import base64
import io
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None
    _logger.warning(
        "xlsxwriter library not found. XLSX export will be unavailable."
    )


class AssetFlowReportWizard(models.TransientModel):
    _name = "asset.flow.report.wizard"
    _description = "AssetFlow Report Wizard"

    report_type = fields.Selection(
        [
            ("asset_utilization", "Asset Utilization"),
            ("department_summary", "Department Summary"),
            ("maintenance", "Maintenance Report"),
            ("audit", "Audit Report"),
            ("booking", "Booking Report"),
        ],
        required=True,
        default="asset_utilization",
    )
    date_from = fields.Date()
    date_to = fields.Date()
    department_id = fields.Many2one("asset.flow.department")
    category_id = fields.Many2one("asset.flow.asset.category")
    employee_id = fields.Many2one("asset.flow.employee")

    def _get_report_data(self):
        """Fetch data based on report_type and filters."""
        self.ensure_one()
        domain = []
        if self.department_id:
            domain.append(("department_id", "=", self.department_id.id))

        if self.report_type == "asset_utilization":
            asset_domain = list(domain)
            if self.category_id:
                asset_domain.append(
                    ("category_id", "=", self.category_id.id)
                )
            assets = self.env["asset.flow.asset"].search(asset_domain)
            return {
                "title": _("Asset Utilization Report"),
                "records": assets,
                "model": "asset",
            }

        elif self.report_type == "department_summary":
            dept_domain = []
            if self.department_id:
                dept_domain = [("id", "=", self.department_id.id)]
            departments = self.env["asset.flow.department"].search(
                dept_domain
            )
            return {
                "title": _("Department Summary Report"),
                "records": departments,
                "model": "department",
            }

        elif self.report_type == "maintenance":
            maint_domain = list(domain)
            if self.date_from:
                maint_domain.append(
                    ("request_date", ">=", self.date_from)
                )
            if self.date_to:
                maint_domain.append(
                    ("request_date", "<=", self.date_to)
                )
            records = self.env["asset.flow.maintenance"].search(
                maint_domain
            )
            return {
                "title": _("Maintenance Report"),
                "records": records,
                "model": "maintenance",
            }

        elif self.report_type == "audit":
            audit_domain = []
            if self.department_id:
                audit_domain.append(
                    ("department_id", "=", self.department_id.id)
                )
            if self.date_from:
                audit_domain.append(
                    ("planned_date", ">=", self.date_from)
                )
            if self.date_to:
                audit_domain.append(
                    ("planned_date", "<=", self.date_to)
                )
            records = self.env["asset.flow.audit"].search(audit_domain)
            return {
                "title": _("Audit Report"),
                "records": records,
                "model": "audit",
            }

        elif self.report_type == "booking":
            booking_domain = []
            if self.department_id:
                booking_domain.append(
                    ("department_id", "=", self.department_id.id)
                )
            if self.employee_id:
                booking_domain.append(
                    ("employee_id", "=", self.employee_id.id)
                )
            if self.date_from:
                booking_domain.append(
                    ("start_datetime", ">=", self.date_from)
                )
            if self.date_to:
                booking_domain.append(
                    ("end_datetime", "<=", self.date_to)
                )
            records = self.env["asset.flow.resource.booking"].search(
                booking_domain
            )
            return {
                "title": _("Booking Report"),
                "records": records,
                "model": "booking",
            }

        return {"title": "", "records": self.env["asset.flow.asset"], "model": "asset"}

    def action_generate_pdf(self):
        """Generate PDF report."""
        self.ensure_one()
        report_map = {
            "asset_utilization": "asset_flow.report_asset_utilization",
            "department_summary": "asset_flow.report_department_summary",
            "maintenance": "asset_flow.report_maintenance",
            "audit": "asset_flow.report_audit",
            "booking": "asset_flow.report_booking",
        }
        report_ref = report_map.get(self.report_type)
        if not report_ref:
            raise UserError(_("Unknown report type."))

        data = self._get_report_data()
        return self.env.ref(report_ref).report_action(
            data["records"],
            data={
                "title": data["title"],
                "date_from": str(self.date_from) if self.date_from else "",
                "date_to": str(self.date_to) if self.date_to else "",
                "department": self.department_id.name
                if self.department_id
                else "All",
                "category": self.category_id.complete_name
                if self.category_id
                else "All",
            },
        )

    def action_generate_xlsx(self):
        """Generate XLSX report and return download action."""
        self.ensure_one()
        if not xlsxwriter:
            raise UserError(
                _(
                    "xlsxwriter library is not installed. "
                    "Please install it to export XLSX reports."
                )
            )

        data = self._get_report_data()
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet(data["title"][:31])

        # Header format
        header_fmt = workbook.add_format(
            {"bold": True, "bg_color": "#4472C4", "font_color": "white"}
        )

        headers, rows = self._get_xlsx_data(data)

        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_fmt)

        for row_idx, row_data in enumerate(rows, start=1):
            for col_idx, cell in enumerate(row_data):
                worksheet.write(row_idx, col_idx, cell)

        # Auto-fit columns
        for col, header in enumerate(headers):
            max_len = max(
                len(str(header)),
                max((len(str(r[col])) for r in rows), default=0),
            )
            worksheet.set_column(col, col, min(max_len + 2, 40))

        workbook.close()
        xlsx_data = base64.b64encode(output.getvalue())
        output.close()

        attachment = self.env["ir.attachment"].create(
            {
                "name": "%s.xlsx" % data["title"],
                "type": "binary",
                "datas": xlsx_data,
                "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
        )
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % attachment.id,
            "target": "new",
        }

    def action_generate_csv(self):
        """Generate CSV report and return download action."""
        self.ensure_one()
        data = self._get_report_data()
        headers, rows = self._get_xlsx_data(data)

        output = io.StringIO()
        output.write(",".join('"%s"' % h for h in headers) + "\n")
        for row in rows:
            output.write(
                ",".join('"%s"' % str(c).replace('"', '""') for c in row)
                + "\n"
            )

        csv_data = base64.b64encode(output.getvalue().encode("utf-8"))
        output.close()

        attachment = self.env["ir.attachment"].create(
            {
                "name": "%s.csv" % data["title"],
                "type": "binary",
                "datas": csv_data,
                "mimetype": "text/csv",
            }
        )
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % attachment.id,
            "target": "new",
        }

    def _get_xlsx_data(self, data):
        """Return (headers, rows) for the given report data."""
        model = data["model"]
        records = data["records"]

        if model == "asset":
            headers = [
                "Asset Tag", "Name", "Category", "Department",
                "Employee", "State", "Location", "Purchase Date",
                "Purchase Value",
            ]
            rows = []
            for r in records:
                rows.append([
                    r.asset_tag or "",
                    r.name or "",
                    r.category_id.complete_name or "",
                    r.department_id.name or "",
                    r.current_employee_id.name or "",
                    dict(r._fields["state"].selection).get(r.state, ""),
                    r.location or "",
                    str(r.purchase_date) if r.purchase_date else "",
                    r.purchase_value or 0,
                ])
            return headers, rows

        elif model == "department":
            headers = [
                "Department", "Code", "Manager",
                "Employee Count", "Asset Count",
            ]
            rows = []
            for r in records:
                rows.append([
                    r.name or "",
                    r.code or "",
                    r.manager_id.name or "",
                    r.employee_count,
                    r.asset_count,
                ])
            return headers, rows

        elif model == "maintenance":
            headers = [
                "Reference", "Asset", "Department", "Type",
                "Priority", "State", "Technician",
                "Request Date", "Resolved Date",
            ]
            rows = []
            for r in records:
                rows.append([
                    r.name or "",
                    r.asset_id.name or "",
                    r.department_id.name or "",
                    dict(r._fields["maintenance_type"].selection).get(
                        r.maintenance_type, ""
                    ),
                    dict(r._fields["priority"].selection).get(
                        r.priority, ""
                    ),
                    dict(r._fields["state"].selection).get(r.state, ""),
                    r.assigned_to_id.name or "",
                    str(r.request_date) if r.request_date else "",
                    str(r.resolved_date) if r.resolved_date else "",
                ])
            return headers, rows

        elif model == "audit":
            headers = [
                "Reference", "Department", "Auditor",
                "Planned Date", "Completed Date", "State",
                "Total Lines", "Discrepancies",
            ]
            rows = []
            for r in records:
                rows.append([
                    r.name or "",
                    r.department_id.name or "",
                    r.auditor_id.name or "",
                    str(r.planned_date) if r.planned_date else "",
                    str(r.completed_date) if r.completed_date else "",
                    dict(r._fields["state"].selection).get(r.state, ""),
                    len(r.line_ids),
                    r.discrepancy_count,
                ])
            return headers, rows

        elif model == "booking":
            headers = [
                "Reference", "Resource", "Booked By",
                "Department", "Start", "End",
                "State", "Purpose",
            ]
            rows = []
            for r in records:
                rows.append([
                    r.name or "",
                    r.asset_id.name or "",
                    r.employee_id.name or "",
                    r.department_id.name or "",
                    str(r.start_datetime) if r.start_datetime else "",
                    str(r.end_datetime) if r.end_datetime else "",
                    dict(r._fields["state"].selection).get(r.state, ""),
                    r.purpose or "",
                ])
            return headers, rows

        return [], []

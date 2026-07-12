from odoo import fields, models


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
    notes = fields.Text(default="TODO: Implement report generation logic.")

    # TODO: Add action methods for PDF/XLSX/CSV exports.

from odoo import fields, models


class AssetFlowAudit(models.Model):
    _name = "asset.flow.audit"
    _description = "AssetFlow Audit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "planned_date desc, name desc"

    name = fields.Char(
        required=True,
        copy=False,
        default=lambda self: self.env["ir.sequence"].next_by_code("asset.flow.audit") or "New",
        tracking=True,
    )
    department_id = fields.Many2one(
        "asset.flow.department",
        tracking=True,
    )
    auditor_id = fields.Many2one(
        "asset.flow.employee",
        tracking=True,
    )
    planned_date = fields.Date(tracking=True)
    completed_date = fields.Date(tracking=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("planned", "Planned"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many(
        "asset.flow.audit.line",
        "audit_id",
        string="Audit Lines",
    )
    notes = fields.Text()

    # TODO: Implement audit cycle generation, discrepancy handling, and closure logic.


class AssetFlowAuditLine(models.Model):
    _name = "asset.flow.audit.line"
    _description = "AssetFlow Audit Line"
    _order = "audit_id, asset_id"

    audit_id = fields.Many2one(
        "asset.flow.audit",
        required=True,
        ondelete="cascade",
    )
    asset_id = fields.Many2one(
        "asset.flow.asset",
        required=True,
    )
    expected_employee_id = fields.Many2one(
        "asset.flow.employee",
        string="Expected Employee",
    )
    actual_employee_id = fields.Many2one(
        "asset.flow.employee",
        string="Actual Employee",
    )
    condition = fields.Selection(
        [
            ("good", "Good"),
            ("fair", "Fair"),
            ("damaged", "Damaged"),
            ("missing", "Missing"),
        ],
        default="good",
    )
    status = fields.Selection(
        [
            ("pending", "Pending"),
            ("verified", "Verified"),
            ("discrepancy", "Discrepancy"),
        ],
        default="pending",
    )
    notes = fields.Text()

    # TODO: Implement verification and discrepancy resolution logic.

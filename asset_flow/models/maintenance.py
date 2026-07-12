from odoo import fields, models


class AssetFlowMaintenance(models.Model):
    _name = "asset.flow.maintenance"
    _description = "AssetFlow Maintenance"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "request_date desc, name desc"

    name = fields.Char(
        required=True,
        copy=False,
        default=lambda self: self.env["ir.sequence"].next_by_code("asset.flow.maintenance") or "New",
        tracking=True,
    )
    asset_id = fields.Many2one(
        "asset.flow.asset",
        required=True,
        tracking=True,
    )
    department_id = fields.Many2one(
        related="asset_id.department_id",
        store=True,
        readonly=True,
    )
    requested_by_id = fields.Many2one(
        "asset.flow.employee",
        string="Requested By",
        tracking=True,
    )
    assigned_to_id = fields.Many2one(
        "asset.flow.employee",
        string="Technician",
        tracking=True,
    )
    maintenance_type = fields.Selection(
        [
            ("corrective", "Corrective"),
            ("preventive", "Preventive"),
            ("inspection", "Inspection"),
        ],
        default="corrective",
        required=True,
        tracking=True,
    )
    priority = fields.Selection(
        [
            ("low", "Low"),
            ("normal", "Normal"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        default="normal",
        required=True,
        tracking=True,
    )
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("assigned", "Technician Assigned"),
            ("in_progress", "In Progress"),
            ("resolved", "Resolved"),
            ("cancelled", "Cancelled"),
        ],
        default="pending",
        required=True,
        tracking=True,
    )
    request_date = fields.Datetime(default=fields.Datetime.now, required=True)
    scheduled_date = fields.Datetime()
    resolved_date = fields.Datetime()
    description = fields.Text()
    resolution_notes = fields.Text()

    # TODO: Implement maintenance workflow, technician assignment, and asset state sync.

from odoo import fields, models


class AssetFlowAsset(models.Model):
    _name = "asset.flow.asset"
    _description = "AssetFlow Asset"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "asset_tag, name"

    name = fields.Char(required=True, tracking=True)
    asset_tag = fields.Char(
        required=True,
        copy=False,
        default=lambda self: self.env["ir.sequence"].next_by_code("asset.flow.asset") or "New",
        tracking=True,
    )
    serial_number = fields.Char(copy=False, tracking=True)
    category_id = fields.Many2one(
        "asset.flow.asset.category",
        required=True,
        tracking=True,
    )
    department_id = fields.Many2one(
        "asset.flow.department",
        tracking=True,
    )
    current_employee_id = fields.Many2one(
        "asset.flow.employee",
        string="Assigned Employee",
        tracking=True,
    )
    state = fields.Selection(
        [
            ("available", "Available"),
            ("allocated", "Allocated"),
            ("maintenance", "Under Maintenance"),
            ("retired", "Retired"),
            ("lost", "Lost"),
        ],
        default="available",
        required=True,
        tracking=True,
    )
    location = fields.Char(tracking=True)
    purchase_date = fields.Date()
    purchase_value = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
    )
    notes = fields.Text()
    active = fields.Boolean(default=True)

    request_ids = fields.One2many(
        "asset.flow.asset.request",
        "asset_id",
        string="Requests",
    )
    booking_ids = fields.One2many(
        "asset.flow.resource.booking",
        "asset_id",
        string="Bookings",
    )
    maintenance_ids = fields.One2many(
        "asset.flow.maintenance",
        "asset_id",
        string="Maintenance",
    )
    assignment_history_ids = fields.One2many(
        "asset.flow.assignment.history",
        "asset_id",
        string="Assignment History",
    )
    audit_line_ids = fields.One2many(
        "asset.flow.audit.line",
        "asset_id",
        string="Audit Lines",
    )

    # TODO: Add lifecycle transitions, QR labels, allocation checks, and automation.

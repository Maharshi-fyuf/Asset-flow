from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AssetFlowAsset(models.Model):
    _name = "asset.flow.asset"
    _description = "AssetFlow Asset"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "asset_tag, name"

    _sql_constraints = [
        (
            "asset_tag_unique",
            "UNIQUE(asset_tag)",
            "Asset tag must be unique.",
        ),
        (
            "serial_number_unique",
            "UNIQUE(serial_number)",
            "Serial number must be unique when provided.",
        ),
    ]

    name = fields.Char(required=True, tracking=True)
    asset_tag = fields.Char(
        required=True,
        copy=False,
        default=lambda self: self.env["ir.sequence"].next_by_code(
            "asset.flow.asset"
        )
        or "New",
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

    def check_allocation_allowed(self):
        """Validate that this asset can be allocated."""
        for asset in self:
            if asset.state == "allocated":
                raise UserError(
                    _("Asset '%s' is already allocated to '%s'.")
                    % (asset.name, asset.current_employee_id.name or "")
                )
            if asset.state == "maintenance":
                raise UserError(
                    _("Asset '%s' is under maintenance and cannot be allocated.")
                    % asset.name
                )
            if asset.state == "retired":
                raise UserError(
                    _("Asset '%s' is retired and cannot be allocated.")
                    % asset.name
                )
            if asset.state == "lost":
                raise UserError(
                    _("Asset '%s' is marked as lost and cannot be allocated.")
                    % asset.name
                )

    def action_set_available(self):
        """Mark asset as available."""
        for asset in self:
            if asset.state == "allocated" and asset.current_employee_id:
                raise UserError(
                    _(
                        "Asset '%s' is currently allocated. "
                        "Process a return before marking as available."
                    )
                    % asset.name
                )
            asset.write({"state": "available", "current_employee_id": False})
            asset.message_post(body=_("Asset marked as available."))

    def action_retire(self):
        """Retire the asset permanently."""
        for asset in self:
            if asset.state == "allocated":
                raise UserError(
                    _(
                        "Asset '%s' is currently allocated. "
                        "Process a return before retiring."
                    )
                    % asset.name
                )
            if asset.state == "maintenance":
                raise UserError(
                    _(
                        "Asset '%s' is under maintenance. "
                        "Resolve maintenance before retiring."
                    )
                    % asset.name
                )
            asset.write({"state": "retired", "current_employee_id": False})
            asset.message_post(body=_("Asset has been retired."))

    def action_mark_lost(self):
        """Mark asset as lost."""
        for asset in self:
            asset.write({"state": "lost", "current_employee_id": False})
            asset.message_post(body=_("Asset has been marked as lost."))

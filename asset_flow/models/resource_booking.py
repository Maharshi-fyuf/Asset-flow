from odoo import fields, models


class AssetFlowResourceBooking(models.Model):
    _name = "asset.flow.resource.booking"
    _description = "AssetFlow Resource Booking"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_datetime desc, name desc"

    name = fields.Char(
        required=True,
        copy=False,
        default=lambda self: self.env["ir.sequence"].next_by_code("asset.flow.resource.booking") or "New",
        tracking=True,
    )
    asset_id = fields.Many2one(
        "asset.flow.asset",
        string="Resource",
        required=True,
        tracking=True,
    )
    category_id = fields.Many2one(
        related="asset_id.category_id",
        store=True,
        readonly=True,
    )
    employee_id = fields.Many2one(
        "asset.flow.employee",
        string="Booked By",
        required=True,
        tracking=True,
    )
    department_id = fields.Many2one(
        related="employee_id.department_id",
        store=True,
        readonly=True,
    )
    start_datetime = fields.Datetime(required=True, tracking=True)
    end_datetime = fields.Datetime(required=True, tracking=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    purpose = fields.Char()
    notes = fields.Text()

    # TODO: Implement booking confirmation, overlap validation, and calendar rules.

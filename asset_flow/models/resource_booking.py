from odoo import api, fields, models
from odoo.exceptions import ValidationError


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

    @api.constrains("asset_id")
    def _check_asset_is_shared(self):
        for booking in self:
            if booking.asset_id and not booking.asset_id.is_shared:
                raise ValidationError(f"The asset '{booking.asset_id.name}' is not marked as shared/bookable.")

    @api.constrains("start_datetime", "end_datetime", "asset_id", "state")
    def _check_booking_overlap(self):
        for booking in self:
            if booking.state not in ['cancelled', 'done'] and booking.asset_id and booking.start_datetime and booking.end_datetime:
                if booking.start_datetime >= booking.end_datetime:
                    raise ValidationError("End time must be strictly after start time.")
                
                # Check for overlapping bookings
                domain = [
                    ("asset_id", "=", booking.asset_id.id),
                    ("state", "in", ["confirmed", "draft"]),
                    ("id", "!=", booking.id),
                    ("start_datetime", "<", booking.end_datetime),
                    ("end_datetime", ">", booking.start_datetime),
                ]
                overlapping = self.search(domain, limit=1)
                if overlapping:
                    raise ValidationError(f"Booking overlaps with an existing booking ({overlapping.name}) from {overlapping.start_datetime} to {overlapping.end_datetime}.")

    def action_confirm(self):
        for booking in self:
            booking.state = "confirmed"

    def action_done(self):
        for booking in self:
            booking.state = "done"

    def action_cancel(self):
        for booking in self:
            booking.state = "cancelled"

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class AssetFlowResourceBooking(models.Model):
    _name = "asset.flow.resource.booking"
    _description = "AssetFlow Resource Booking"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_datetime desc, name desc"

    name = fields.Char(
        required=True,
        copy=False,
        default=lambda self: self.env["ir.sequence"].next_by_code(
            "asset.flow.resource.booking"
        )
        or "New",
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

    @api.constrains("start_datetime", "end_datetime")
    def _check_dates(self):
        for booking in self:
            if (
                booking.start_datetime
                and booking.end_datetime
                and booking.end_datetime <= booking.start_datetime
            ):
                raise ValidationError(
                    _("End time must be after start time.")
                )

    @api.constrains("asset_id", "start_datetime", "end_datetime", "state")
    def _check_booking_overlap(self):
        for booking in self:
            if booking.state not in ("confirmed", "done"):
                continue
            if not (
                booking.asset_id
                and booking.start_datetime
                and booking.end_datetime
            ):
                continue
            overlapping = self.search(
                [
                    ("id", "!=", booking.id),
                    ("asset_id", "=", booking.asset_id.id),
                    ("state", "in", ("confirmed", "done")),
                    ("start_datetime", "<", booking.end_datetime),
                    ("end_datetime", ">", booking.start_datetime),
                ],
                limit=1,
            )
            if overlapping:
                raise ValidationError(
                    _(
                        "Booking conflict: '%s' is already booked "
                        "from %s to %s (booking %s)."
                    )
                    % (
                        booking.asset_id.name,
                        overlapping.start_datetime,
                        overlapping.end_datetime,
                        overlapping.name,
                    )
                )

    def action_confirm(self):
        """Confirm the booking after validating no overlaps."""
        for booking in self:
            if booking.state != "draft":
                raise UserError(
                    _("Only draft bookings can be confirmed.")
                )
            booking.write({"state": "confirmed"})
            booking.message_post(
                body=_(
                    "Booking confirmed for '%s' from %s to %s."
                )
                % (
                    booking.asset_id.name,
                    booking.start_datetime,
                    booking.end_datetime,
                ),
                subtype_xmlid="mail.mt_note",
            )

    def action_done(self):
        """Mark the booking as completed."""
        for booking in self:
            if booking.state != "confirmed":
                raise UserError(
                    _("Only confirmed bookings can be marked as done.")
                )
            booking.write({"state": "done"})
            booking.message_post(
                body=_("Booking completed."),
                subtype_xmlid="mail.mt_note",
            )

    def action_cancel(self):
        """Cancel the booking."""
        for booking in self:
            if booking.state == "done":
                raise UserError(
                    _("Completed bookings cannot be cancelled.")
                )
            booking.write({"state": "cancelled"})
            booking.message_post(
                body=_("Booking has been cancelled."),
                subtype_xmlid="mail.mt_note",
            )

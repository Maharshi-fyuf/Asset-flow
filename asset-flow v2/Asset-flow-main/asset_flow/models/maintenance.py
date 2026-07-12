from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AssetFlowMaintenance(models.Model):
    _name = "asset.flow.maintenance"
    _description = "AssetFlow Maintenance"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "request_date desc, name desc"

    name = fields.Char(
        required=True,
        copy=False,
        default=lambda self: self.env["ir.sequence"].next_by_code(
            "asset.flow.maintenance"
        )
        or "New",
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

    def action_approve(self):
        """Approve the maintenance request."""
        for maintenance in self:
            if maintenance.state != "pending":
                raise UserError(
                    _("Only pending maintenance requests can be approved.")
                )
            maintenance.write({"state": "approved"})
            maintenance.message_post(
                body=_("Maintenance request approved."),
                subtype_xmlid="mail.mt_note",
            )

    def action_assign(self):
        """Assign a technician to the maintenance request."""
        for maintenance in self:
            if maintenance.state != "approved":
                raise UserError(
                    _(
                        "Only approved maintenance requests "
                        "can have a technician assigned."
                    )
                )
            if not maintenance.assigned_to_id:
                raise UserError(
                    _(
                        "Please select a technician before "
                        "assigning the maintenance request."
                    )
                )
            maintenance.write({"state": "assigned"})
            maintenance.message_post(
                body=_(
                    "Technician '%s' assigned to maintenance."
                )
                % maintenance.assigned_to_id.name,
                subtype_xmlid="mail.mt_note",
            )

    def action_start(self):
        """Start the maintenance work and set asset to maintenance state."""
        for maintenance in self:
            if maintenance.state != "assigned":
                raise UserError(
                    _(
                        "Only assigned maintenance requests "
                        "can be started."
                    )
                )
            maintenance.asset_id.write({"state": "maintenance"})
            maintenance.write({"state": "in_progress"})
            maintenance.message_post(
                body=_(
                    "Maintenance started. Asset '%s' is now under maintenance."
                )
                % maintenance.asset_id.name,
                subtype_xmlid="mail.mt_note",
            )

    def action_resolve(self):
        """Resolve the maintenance and restore asset state."""
        for maintenance in self:
            if maintenance.state != "in_progress":
                raise UserError(
                    _(
                        "Only in-progress maintenance requests "
                        "can be resolved."
                    )
                )
            maintenance.asset_id.write(
                {
                    "state": "available",
                    "current_employee_id": False,
                }
            )
            maintenance.write(
                {
                    "state": "resolved",
                    "resolved_date": fields.Datetime.now(),
                }
            )
            maintenance.message_post(
                body=_(
                    "Maintenance resolved. Asset '%s' is now available."
                )
                % maintenance.asset_id.name,
                subtype_xmlid="mail.mt_note",
            )

    def action_cancel(self):
        """Cancel the maintenance request."""
        for maintenance in self:
            if maintenance.state == "resolved":
                raise UserError(
                    _("Resolved maintenance requests cannot be cancelled.")
                )
            # Restore asset state if it was changed to maintenance
            if maintenance.state == "in_progress":
                maintenance.asset_id.write({"state": "available"})
            maintenance.write({"state": "cancelled"})
            maintenance.message_post(
                body=_("Maintenance request cancelled."),
                subtype_xmlid="mail.mt_note",
            )

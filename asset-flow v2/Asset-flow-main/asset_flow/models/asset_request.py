from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class AssetFlowAssetRequest(models.Model):
    _name = "asset.flow.asset.request"
    _description = "AssetFlow Asset Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "request_date desc, name desc"

    name = fields.Char(
        required=True,
        copy=False,
        default=lambda self: self.env["ir.sequence"].next_by_code(
            "asset.flow.asset.request"
        )
        or "New",
        tracking=True,
    )
    request_type = fields.Selection(
        [
            ("allocation", "Allocation"),
            ("transfer", "Transfer"),
            ("return", "Return"),
        ],
        default="allocation",
        required=True,
        tracking=True,
    )
    employee_id = fields.Many2one(
        "asset.flow.employee",
        string="Requested For",
        required=True,
        tracking=True,
    )
    requested_by_user_id = fields.Many2one(
        "res.users",
        string="Requested By",
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
    )
    department_id = fields.Many2one(
        related="employee_id.department_id",
        store=True,
        readonly=True,
    )
    category_id = fields.Many2one(
        "asset.flow.asset.category",
        string="Requested Category",
        tracking=True,
    )
    asset_id = fields.Many2one(
        "asset.flow.asset",
        tracking=True,
    )
    request_date = fields.Datetime(default=fields.Datetime.now, required=True)
    needed_by_date = fields.Date()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    assignment_history_ids = fields.One2many(
        "asset.flow.assignment.history",
        "request_id",
        string="Assignment History",
    )
    notes = fields.Text()

    @api.constrains("asset_id", "state")
    def _check_asset_available_for_allocation(self):
        for request in self:
            if (
                request.state == "approved"
                and request.request_type == "allocation"
                and request.asset_id
                and request.asset_id.state != "available"
            ):
                raise ValidationError(
                    _(
                        "Asset '%s' is not available for allocation "
                        "(current state: %s)."
                    )
                    % (request.asset_id.name, request.asset_id.state)
                )

    @api.onchange("category_id")
    def _onchange_category_id(self):
        """Filter assets by selected category."""
        if self.category_id:
            return {
                "domain": {
                    "asset_id": [
                        ("category_id", "=", self.category_id.id),
                        ("state", "=", "available"),
                    ]
                }
            }
        return {"domain": {"asset_id": [("state", "=", "available")]}}

    def action_submit(self):
        """Submit the request for approval."""
        for request in self:
            if request.state != "draft":
                raise UserError(_("Only draft requests can be submitted."))
            request.write({"state": "submitted"})
            request.message_post(
                body=_("Request submitted for approval."),
                subtype_xmlid="mail.mt_note",
            )

    def action_approve(self):
        """Approve the submitted request."""
        for request in self:
            if request.state != "submitted":
                raise UserError(_("Only submitted requests can be approved."))
            request.write({"state": "approved"})
            request.message_post(
                body=_("Request has been approved."),
                subtype_xmlid="mail.mt_note",
            )

    def action_reject(self):
        """Reject the submitted request."""
        for request in self:
            if request.state != "submitted":
                raise UserError(_("Only submitted requests can be rejected."))
            request.write({"state": "rejected"})
            request.message_post(
                body=_("Request has been rejected."),
                subtype_xmlid="mail.mt_note",
            )

    def action_allocate(self):
        """Allocate the asset to the employee."""
        for request in self:
            if request.state != "approved":
                raise UserError(
                    _("Only approved requests can be allocated.")
                )
            if not request.asset_id:
                raise UserError(
                    _("Please select an asset before allocating.")
                )
            request.asset_id.check_allocation_allowed()

            # Update asset
            request.asset_id.write(
                {
                    "state": "allocated",
                    "current_employee_id": request.employee_id.id,
                    "department_id": request.employee_id.department_id.id
                    or request.asset_id.department_id.id,
                }
            )

            # Create assignment history
            self.env["asset.flow.assignment.history"].create(
                {
                    "asset_id": request.asset_id.id,
                    "employee_id": request.employee_id.id,
                    "department_id": request.employee_id.department_id.id,
                    "request_id": request.id,
                    "assigned_by_user_id": self.env.user.id,
                    "state": "active",
                }
            )

            request.write({"state": "done"})
            request.message_post(
                body=_(
                    "Asset '%s' allocated to '%s'."
                )
                % (request.asset_id.name, request.employee_id.name),
                subtype_xmlid="mail.mt_note",
            )

    def action_return(self):
        """Process an asset return."""
        for request in self:
            if request.state != "done":
                raise UserError(
                    _("Only completed allocations can be returned.")
                )
            if not request.asset_id:
                raise UserError(_("No asset linked to this request."))
            if request.request_type == "return":
                raise UserError(
                    _("This request is already a return request.")
                )

            # Close active assignment history
            active_history = self.env[
                "asset.flow.assignment.history"
            ].search(
                [
                    ("asset_id", "=", request.asset_id.id),
                    ("employee_id", "=", request.employee_id.id),
                    ("state", "=", "active"),
                ],
                limit=1,
            )
            if active_history:
                active_history.action_return()

            # Update asset
            request.asset_id.write(
                {
                    "state": "available",
                    "current_employee_id": False,
                }
            )

            request.message_post(
                body=_(
                    "Asset '%s' returned by '%s'."
                )
                % (request.asset_id.name, request.employee_id.name),
                subtype_xmlid="mail.mt_note",
            )

    def action_cancel(self):
        """Cancel the request."""
        for request in self:
            if request.state == "done":
                raise UserError(
                    _(
                        "Completed requests cannot be cancelled. "
                        "Use the return action instead."
                    )
                )
            request.write({"state": "cancelled"})
            request.message_post(
                body=_("Request has been cancelled."),
                subtype_xmlid="mail.mt_note",
            )

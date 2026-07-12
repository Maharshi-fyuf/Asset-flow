from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AssetFlowAssetRequest(models.Model):
    _name = "asset.flow.asset.request"
    _description = "AssetFlow Asset Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "request_date desc, name desc"

    name = fields.Char(
        required=True,
        copy=False,
        default=lambda self: self.env["ir.sequence"].next_by_code("asset.flow.asset.request") or "New",
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
    expected_return_date = fields.Date()
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

    @api.constrains("asset_id", "request_type", "state")
    def _check_allocation_conflict(self):
        for req in self:
            if req.state not in ['draft', 'cancelled', 'rejected'] and req.request_type == 'allocation' and req.asset_id:
                if req.asset_id.state in ['allocated', 'maintenance', 'lost', 'retired', 'disposed']:
                    # For a draft request, warn that asset is already occupied.
                    raise ValidationError(f"Cannot allocate '{req.asset_id.name}' because it is currently {req.asset_id.state}. Use 'Transfer' if you wish to reassign it.")

    def action_submit(self):
        for req in self:
            req.state = "submitted"

    def action_approve(self):
        for req in self:
            req.state = "approved"

    def action_reject(self):
        for req in self:
            req.state = "rejected"

    def action_done(self):
        for req in self:
            if not req.asset_id:
                raise ValidationError("An asset must be selected to complete this request.")
            req.state = "done"
            if req.request_type in ["allocation", "transfer"]:
                # If transferring, close previous history
                previous_history = self.env["asset.flow.assignment.history"].search([
                    ("asset_id", "=", req.asset_id.id),
                    ("state", "=", "active")
                ])
                for hist in previous_history:
                    hist.write({
                        "state": "transferred" if req.request_type == "transfer" else "returned",
                        "returned_date": fields.Datetime.now(),
                    })
                
                req.asset_id.action_set_allocated(req.employee_id.id)
                self.env["asset.flow.assignment.history"].create({
                    "asset_id": req.asset_id.id,
                    "employee_id": req.employee_id.id,
                    "department_id": req.employee_id.department_id.id,
                    "request_id": req.id,
                    "assigned_date": fields.Datetime.now(),
                    "state": "active",
                })
            elif req.request_type == "return":
                previous_history = self.env["asset.flow.assignment.history"].search([
                    ("asset_id", "=", req.asset_id.id),
                    ("state", "=", "active")
                ])
                for hist in previous_history:
                    hist.write({
                        "state": "returned",
                        "returned_date": fields.Datetime.now(),
                    })
                req.asset_id.action_make_available()

    def action_cancel(self):
        for req in self:
            req.state = "cancelled"

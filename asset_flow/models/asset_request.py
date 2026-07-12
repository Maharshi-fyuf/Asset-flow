from odoo import fields, models


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

    # TODO: Implement approval workflow, allocation, transfer, and return actions.

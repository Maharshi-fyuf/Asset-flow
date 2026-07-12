from odoo import fields, models


class AssetFlowAssignmentHistory(models.Model):
    _name = "asset.flow.assignment.history"
    _description = "AssetFlow Assignment History"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "assigned_date desc, id desc"

    asset_id = fields.Many2one(
        "asset.flow.asset",
        required=True,
        tracking=True,
    )
    employee_id = fields.Many2one(
        "asset.flow.employee",
        required=True,
        tracking=True,
    )
    department_id = fields.Many2one(
        "asset.flow.department",
        tracking=True,
    )
    request_id = fields.Many2one(
        "asset.flow.asset.request",
        tracking=True,
    )
    assigned_by_user_id = fields.Many2one(
        "res.users",
        string="Assigned By",
        default=lambda self: self.env.user,
        tracking=True,
    )
    assigned_date = fields.Datetime(default=fields.Datetime.now, required=True)
    returned_date = fields.Datetime()
    state = fields.Selection(
        [
            ("active", "Active"),
            ("returned", "Returned"),
            ("transferred", "Transferred"),
        ],
        default="active",
        required=True,
        tracking=True,
    )
    notes = fields.Text()

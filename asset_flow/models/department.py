from odoo import fields, models


class AssetFlowDepartment(models.Model):
    _name = "asset.flow.department"
    _description = "AssetFlow Department"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(tracking=True)
    manager_id = fields.Many2one(
        "asset.flow.employee",
        string="Department Manager",
        tracking=True,
    )
    employee_ids = fields.One2many(
        "asset.flow.employee",
        "department_id",
        string="Employees",
    )
    asset_ids = fields.One2many(
        "asset.flow.asset",
        "department_id",
        string="Assets",
    )
    active = fields.Boolean(default=True)
    notes = fields.Text()

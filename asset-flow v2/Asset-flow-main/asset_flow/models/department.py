from odoo import api, fields, models


class AssetFlowDepartment(models.Model):
    _name = "asset.flow.department"
    _description = "AssetFlow Department"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    _sql_constraints = [
        (
            "code_unique",
            "UNIQUE(code)",
            "Department code must be unique.",
        ),
    ]

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

    employee_count = fields.Integer(
        compute="_compute_employee_count",
        string="Employee Count",
    )
    asset_count = fields.Integer(
        compute="_compute_asset_count",
        string="Asset Count",
    )

    @api.depends("employee_ids")
    def _compute_employee_count(self):
        for department in self:
            department.employee_count = len(department.employee_ids)

    @api.depends("asset_ids")
    def _compute_asset_count(self):
        for department in self:
            department.asset_count = len(department.asset_ids)

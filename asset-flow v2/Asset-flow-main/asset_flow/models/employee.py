from odoo import fields, models


class AssetFlowEmployee(models.Model):
    _name = "asset.flow.employee"
    _description = "AssetFlow Employee"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    user_id = fields.Many2one(
        "res.users",
        string="Related User",
        tracking=True,
        help="Reuse Odoo authentication by linking an employee profile to a user.",
    )
    department_id = fields.Many2one(
        "asset.flow.department",
        tracking=True,
    )
    manager_id = fields.Many2one(
        "asset.flow.employee",
        string="Manager",
        tracking=True,
    )
    job_title = fields.Char()
    work_email = fields.Char()
    phone = fields.Char()
    asset_ids = fields.One2many(
        "asset.flow.asset",
        "current_employee_id",
        string="Assigned Assets",
    )
    request_ids = fields.One2many(
        "asset.flow.asset.request",
        "employee_id",
        string="Asset Requests",
    )
    booking_ids = fields.One2many(
        "asset.flow.resource.booking",
        "employee_id",
        string="Resource Bookings",
    )
    active = fields.Boolean(default=True)
    notes = fields.Text()

    # TODO: Optionally sync with hr.employee when the HR app is installed.

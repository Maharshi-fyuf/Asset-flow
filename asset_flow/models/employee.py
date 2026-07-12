from odoo import api, fields, models
from odoo.exceptions import ValidationError


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
    role = fields.Selection(
        [
            ("employee", "Employee"),
            ("department_head", "Department Head"),
            ("asset_manager", "Asset Manager"),
            ("admin", "Administrator"),
        ],
        default="employee",
        tracking=True,
    )
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

    @api.model_create_multi
    def create(self, vals_list):
        employees = super().create(vals_list)
        for emp in employees:
            if emp.user_id and emp.role:
                emp._sync_user_role()
        return employees

    def write(self, vals):
        if "role" in vals and not self.env.user.has_group('asset_flow.group_asset_flow_admin'):
            raise ValidationError("Only Administrators can change employee roles.")
            
        res = super().write(vals)
        if "role" in vals or "user_id" in vals:
            for emp in self:
                if emp.user_id:
                    emp._sync_user_role()
        return res

    def _sync_user_role(self):
        self.ensure_one()
        group_mapping = {
            "employee": self.env.ref("asset_flow.group_asset_flow_employee", raise_if_not_found=False),
            "department_head": self.env.ref("asset_flow.group_asset_flow_department_head", raise_if_not_found=False),
            "asset_manager": self.env.ref("asset_flow.group_asset_flow_asset_manager", raise_if_not_found=False),
            "admin": self.env.ref("asset_flow.group_asset_flow_admin", raise_if_not_found=False),
        }
        all_groups = self.env["res.groups"]
        for g in group_mapping.values():
            if g:
                all_groups |= g
                
        target_group = group_mapping.get(self.role)
        if self.user_id and target_group:
            self.user_id.sudo().write({
                "groups_id": [(3, g.id) for g in all_groups if g.id and g.id != target_group.id] + [(4, target_group.id)]
            })


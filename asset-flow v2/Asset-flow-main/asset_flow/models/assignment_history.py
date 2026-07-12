from odoo import _, fields, models
from odoo.exceptions import UserError


class AssetFlowAssignmentHistory(models.Model):
    _name = "asset.flow.assignment.history"
    _description = "AssetFlow Assignment History"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "asset_id"
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

    def action_return(self):
        """Mark the assignment as returned."""
        for history in self:
            if history.state != "active":
                raise UserError(
                    _("Only active assignments can be returned.")
                )
            history.write(
                {
                    "state": "returned",
                    "returned_date": fields.Datetime.now(),
                }
            )
            history.message_post(
                body=_(
                    "Asset '%s' returned by '%s'."
                )
                % (history.asset_id.name, history.employee_id.name),
                subtype_xmlid="mail.mt_note",
            )

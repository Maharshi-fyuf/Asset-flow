from odoo import api, fields, models


class AssetFlowAssetCategory(models.Model):
    _name = "asset.flow.asset.category"
    _description = "AssetFlow Asset Category"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _parent_name = "parent_id"
    _parent_store = True
    _order = "complete_name"

    _sql_constraints = [
        (
            "code_parent_unique",
            "UNIQUE(code, parent_id)",
            "Category code must be unique within the same parent.",
        ),
    ]

    name = fields.Char(required=True, tracking=True)
    complete_name = fields.Char(
        compute="_compute_complete_name",
        recursive=True,
        store=True,
    )
    code = fields.Char(tracking=True)
    parent_id = fields.Many2one(
        "asset.flow.asset.category",
        string="Parent Category",
        index=True,
    )
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many(
        "asset.flow.asset.category",
        "parent_id",
        string="Child Categories",
    )
    category_type = fields.Selection(
        [
            ("asset", "Asset"),
            ("resource", "Bookable Resource"),
            ("both", "Asset and Resource"),
        ],
        default="asset",
        required=True,
        tracking=True,
    )
    maintenance_required = fields.Boolean(default=False)
    asset_ids = fields.One2many(
        "asset.flow.asset",
        "category_id",
        string="Assets",
    )
    active = fields.Boolean(default=True)
    notes = fields.Text()

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for category in self:
            names = []
            current = category
            while current:
                names.append(current.name or "")
                current = current.parent_id
            category.complete_name = " / ".join(
                reversed([name for name in names if name])
            )

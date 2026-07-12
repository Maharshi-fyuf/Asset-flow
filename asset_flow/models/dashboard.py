from odoo import fields, models


class AssetFlowDashboard(models.TransientModel):
    _name = "asset.flow.dashboard"
    _description = "AssetFlow Dashboard"

    total_assets = fields.Integer(readonly=True)
    available_assets = fields.Integer(readonly=True)
    allocated_assets = fields.Integer(readonly=True)
    maintenance_assets = fields.Integer(readonly=True)
    pending_requests = fields.Integer(readonly=True)
    active_bookings = fields.Integer(readonly=True)
    open_maintenance = fields.Integer(readonly=True)
    open_audits = fields.Integer(readonly=True)
    notes = fields.Text(
        default="TODO: Implement dashboard KPI computation and charts.",
        readonly=True,
    )

    # TODO: Replace placeholder fields with computed KPIs and dashboard actions.

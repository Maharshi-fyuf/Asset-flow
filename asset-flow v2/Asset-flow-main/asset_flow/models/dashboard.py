from odoo import api, fields, models


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
        default="Dashboard KPIs computed successfully.",
        readonly=True,
    )

    @api.model
    def default_get(self, fields_list):
        res = super(AssetFlowDashboard, self).default_get(fields_list)
        
        # Count assets
        Asset = self.env["asset.flow.asset"]
        res["total_assets"] = Asset.search_count([])
        res["available_assets"] = Asset.search_count([("state", "=", "available")])
        res["allocated_assets"] = Asset.search_count([("state", "=", "allocated")])
        res["maintenance_assets"] = Asset.search_count([("state", "=", "maintenance")])
        
        # Count pending requests
        Request = self.env["asset.flow.asset.request"]
        res["pending_requests"] = Request.search_count([("state", "in", ["submitted", "approved"])])
        
        # Count active bookings
        Booking = self.env["asset.flow.resource.booking"]
        res["active_bookings"] = Booking.search_count([("state", "=", "confirmed")])
        
        # Count open maintenance
        Maintenance = self.env["asset.flow.maintenance"]
        res["open_maintenance"] = Maintenance.search_count([("state", "in", ["pending", "approved", "assigned", "in_progress"])])
        
        # Count open audits
        Audit = self.env["asset.flow.audit"]
        res["open_audits"] = Audit.search_count([("state", "in", ["planned", "in_progress"])])
        
        return res

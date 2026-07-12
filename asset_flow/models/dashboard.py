from odoo import api, fields, models


class AssetFlowDashboard(models.TransientModel):
    _name = "asset.flow.dashboard"
    _description = "AssetFlow Dashboard"

    total_assets = fields.Integer(compute="_compute_kpis", string="Total Assets")
    available_assets = fields.Integer(compute="_compute_kpis", string="Available")
    allocated_assets = fields.Integer(compute="_compute_kpis", string="Allocated")
    maintenance_assets = fields.Integer(compute="_compute_kpis", string="Under Maintenance")
    reserved_assets = fields.Integer(compute="_compute_kpis", string="Reserved")
    pending_requests = fields.Integer(compute="_compute_kpis", string="Pending Requests")
    active_bookings = fields.Integer(compute="_compute_kpis", string="Active Bookings")
    open_maintenance = fields.Integer(compute="_compute_kpis", string="Open Maintenance")
    open_audits = fields.Integer(compute="_compute_kpis", string="Open Audits")
    overdue_allocations = fields.Integer(compute="_compute_kpis", string="Overdue Returns")

    @api.depends()
    def _compute_kpis(self):
        Asset = self.env["asset.flow.asset"]
        Request = self.env["asset.flow.asset.request"]
        Booking = self.env["asset.flow.resource.booking"]
        Maintenance = self.env["asset.flow.maintenance"]
        Audit = self.env["asset.flow.audit"]

        for rec in self:
            rec.total_assets = Asset.search_count([("active", "=", True)])
            rec.available_assets = Asset.search_count([("state", "=", "available")])
            rec.allocated_assets = Asset.search_count([("state", "=", "allocated")])
            rec.maintenance_assets = Asset.search_count([("state", "=", "maintenance")])
            rec.reserved_assets = Asset.search_count([("state", "=", "reserved")])
            rec.pending_requests = Request.search_count([("state", "in", ["submitted"])])
            rec.active_bookings = Booking.search_count([("state", "=", "confirmed")])
            rec.open_maintenance = Maintenance.search_count([
                ("state", "in", ["pending", "approved", "assigned", "in_progress"])
            ])
            rec.open_audits = Audit.search_count([
                ("state", "in", ["planned", "in_progress"])
            ])
            rec.overdue_allocations = Request.search_count([
                ("state", "=", "done"),
                ("request_type", "in", ["allocation", "transfer"]),
                ("expected_return_date", "<", fields.Date.today()),
            ])

    @api.model
    def action_open_dashboard(self):
        """Create a fresh transient record with live KPIs and open it."""
        record = self.create({})
        return {
            "type": "ir.actions.act_window",
            "name": "Dashboard",
            "res_model": "asset.flow.dashboard",
            "res_id": record.id,
            "view_mode": "form",
            "target": "current",
            "flags": {"form": {"action_buttons": False}},
        }

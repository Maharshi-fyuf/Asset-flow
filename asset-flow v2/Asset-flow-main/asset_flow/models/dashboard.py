from odoo import api, models


class AssetFlowDashboard(models.AbstractModel):
    _name = "asset.flow.dashboard"
    _description = "AssetFlow Dashboard Data Provider"

    @api.model
    def get_dashboard_data(self):
        """Return all KPI and chart data for the AssetFlow dashboard."""
        Asset = self.env["asset.flow.asset"]
        Request = self.env["asset.flow.asset.request"]
        Booking = self.env["asset.flow.resource.booking"]
        Maintenance = self.env["asset.flow.maintenance"]
        Audit = self.env["asset.flow.audit"]

        # --- KPIs ---
        kpis = {
            "total_assets": Asset.search_count([]),
            "available_assets": Asset.search_count(
                [("state", "=", "available")]
            ),
            "allocated_assets": Asset.search_count(
                [("state", "=", "allocated")]
            ),
            "maintenance_assets": Asset.search_count(
                [("state", "=", "maintenance")]
            ),
            "pending_requests": Request.search_count(
                [("state", "in", ["submitted", "approved"])]
            ),
            "active_bookings": Booking.search_count(
                [("state", "=", "confirmed")]
            ),
            "open_maintenance": Maintenance.search_count(
                [
                    (
                        "state",
                        "in",
                        ["pending", "approved", "assigned", "in_progress"],
                    )
                ]
            ),
            "open_audits": Audit.search_count(
                [("state", "in", ["planned", "in_progress"])]
            ),
        }

        # --- Chart: Assets by Category ---
        categories = self.env["asset.flow.asset.category"].search([])
        assets_by_category = []
        for cat in categories:
            count = Asset.search_count([("category_id", "=", cat.id)])
            if count:
                assets_by_category.append(
                    {"label": cat.complete_name or cat.name, "value": count}
                )

        # --- Chart: Assets by Department ---
        departments = self.env["asset.flow.department"].search([])
        assets_by_department = []
        for dept in departments:
            count = Asset.search_count([("department_id", "=", dept.id)])
            if count:
                assets_by_department.append(
                    {"label": dept.name, "value": count}
                )

        # --- Chart: Request Status ---
        request_states = [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ]
        request_by_status = []
        for state_key, state_label in request_states:
            count = Request.search_count([("state", "=", state_key)])
            if count:
                request_by_status.append(
                    {"label": state_label, "value": count}
                )

        # --- Chart: Maintenance Status ---
        maint_states = [
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("assigned", "Assigned"),
            ("in_progress", "In Progress"),
            ("resolved", "Resolved"),
            ("cancelled", "Cancelled"),
        ]
        maintenance_by_status = []
        for state_key, state_label in maint_states:
            count = Maintenance.search_count([("state", "=", state_key)])
            if count:
                maintenance_by_status.append(
                    {"label": state_label, "value": count}
                )

        return {
            "kpis": kpis,
            "assets_by_category": assets_by_category,
            "assets_by_department": assets_by_department,
            "request_by_status": request_by_status,
            "maintenance_by_status": maintenance_by_status,
        }

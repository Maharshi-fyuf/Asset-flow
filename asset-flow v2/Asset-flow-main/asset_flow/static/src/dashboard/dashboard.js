/** @odoo-module */
import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class AssetFlowDashboard extends Component {
    static template = "asset_flow.DashboardMain";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            kpis: {},
            assets_by_category: [],
            assets_by_department: [],
            request_by_status: [],
            maintenance_by_status: [],
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        const data = await this.orm.call(
            "asset.flow.dashboard",
            "get_dashboard_data",
            []
        );
        Object.assign(this.state, data);
    }

    openAssets(state) {
        const domain = state ? [["state", "=", state]] : [];
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Assets",
            res_model: "asset.flow.asset",
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            domain: domain,
            target: "current",
        });
    }

    openRequests() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Pending Requests",
            res_model: "asset.flow.asset.request",
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            domain: [["state", "in", ["submitted", "approved"]]],
            target: "current",
        });
    }

    openBookings() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Active Bookings",
            res_model: "asset.flow.resource.booking",
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            domain: [["state", "=", "confirmed"]],
            target: "current",
        });
    }

    openMaintenance() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Open Maintenance",
            res_model: "asset.flow.maintenance",
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            domain: [["state", "in", ["pending", "approved", "assigned", "in_progress"]]],
            target: "current",
        });
    }

    openAudits() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Open Audits",
            res_model: "asset.flow.audit",
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            domain: [["state", "in", ["planned", "in_progress"]]],
            target: "current",
        });
    }
}

registry.category("actions").add("asset_flow.dashboard", AssetFlowDashboard);

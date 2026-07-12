from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AssetFlowAudit(models.Model):
    _name = "asset.flow.audit"
    _description = "AssetFlow Audit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "planned_date desc, name desc"

    name = fields.Char(
        required=True,
        copy=False,
        default=lambda self: self.env["ir.sequence"].next_by_code(
            "asset.flow.audit"
        )
        or "New",
        tracking=True,
    )
    department_id = fields.Many2one(
        "asset.flow.department",
        tracking=True,
    )
    auditor_id = fields.Many2one(
        "asset.flow.employee",
        tracking=True,
    )
    planned_date = fields.Date(tracking=True)
    completed_date = fields.Date(tracking=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("planned", "Planned"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many(
        "asset.flow.audit.line",
        "audit_id",
        string="Audit Lines",
    )
    notes = fields.Text()

    discrepancy_count = fields.Integer(
        compute="_compute_discrepancy_count",
        string="Discrepancies",
    )

    @api.depends("line_ids.status")
    def _compute_discrepancy_count(self):
        for audit in self:
            audit.discrepancy_count = len(
                audit.line_ids.filtered(lambda l: l.status == "discrepancy")
            )

    def action_plan(self):
        """Move audit to planned state."""
        for audit in self:
            if audit.state != "draft":
                raise UserError(_("Only draft audits can be planned."))
            if not audit.auditor_id:
                raise UserError(
                    _("Please assign an auditor before planning.")
                )
            if not audit.planned_date:
                raise UserError(
                    _("Please set a planned date before planning.")
                )
            audit.write({"state": "planned"})
            audit.message_post(
                body=_(
                    "Audit planned for %s. Auditor: %s."
                )
                % (audit.planned_date, audit.auditor_id.name),
                subtype_xmlid="mail.mt_note",
            )

    def action_start(self):
        """Start the audit and auto-generate audit lines from department assets."""
        for audit in self:
            if audit.state != "planned":
                raise UserError(
                    _("Only planned audits can be started.")
                )
            # Auto-generate audit lines from department assets
            if audit.department_id and not audit.line_ids:
                assets = self.env["asset.flow.asset"].search(
                    [
                        ("department_id", "=", audit.department_id.id),
                        ("active", "=", True),
                        ("state", "!=", "retired"),
                    ]
                )
                lines_vals = []
                for asset in assets:
                    lines_vals.append(
                        {
                            "audit_id": audit.id,
                            "asset_id": asset.id,
                            "expected_employee_id": asset.current_employee_id.id
                            if asset.current_employee_id
                            else False,
                            "status": "pending",
                        }
                    )
                if lines_vals:
                    self.env["asset.flow.audit.line"].create(lines_vals)

            audit.write({"state": "in_progress"})
            audit.message_post(
                body=_(
                    "Audit started. %d asset lines generated."
                )
                % len(audit.line_ids),
                subtype_xmlid="mail.mt_note",
            )

    def action_complete(self):
        """Complete the audit after all lines are verified."""
        for audit in self:
            if audit.state != "in_progress":
                raise UserError(
                    _("Only in-progress audits can be completed.")
                )
            pending_lines = audit.line_ids.filtered(
                lambda l: l.status == "pending"
            )
            if pending_lines:
                raise UserError(
                    _(
                        "Cannot complete audit: %d asset lines "
                        "are still pending verification."
                    )
                    % len(pending_lines)
                )
            audit.write(
                {
                    "state": "completed",
                    "completed_date": fields.Date.today(),
                }
            )
            discrepancy_count = audit.discrepancy_count
            body = _("Audit completed.")
            if discrepancy_count:
                body += _(
                    " %d discrepancies found."
                ) % discrepancy_count
            audit.message_post(
                body=body,
                subtype_xmlid="mail.mt_note",
            )

    def action_cancel(self):
        """Cancel the audit."""
        for audit in self:
            if audit.state == "completed":
                raise UserError(
                    _("Completed audits cannot be cancelled.")
                )
            audit.write({"state": "cancelled"})
            audit.message_post(
                body=_("Audit has been cancelled."),
                subtype_xmlid="mail.mt_note",
            )


class AssetFlowAuditLine(models.Model):
    _name = "asset.flow.audit.line"
    _description = "AssetFlow Audit Line"
    _rec_name = "asset_id"
    _order = "audit_id, asset_id"

    audit_id = fields.Many2one(
        "asset.flow.audit",
        required=True,
        ondelete="cascade",
    )
    asset_id = fields.Many2one(
        "asset.flow.asset",
        required=True,
    )
    expected_employee_id = fields.Many2one(
        "asset.flow.employee",
        string="Expected Employee",
    )
    actual_employee_id = fields.Many2one(
        "asset.flow.employee",
        string="Actual Employee",
    )
    condition = fields.Selection(
        [
            ("good", "Good"),
            ("fair", "Fair"),
            ("damaged", "Damaged"),
            ("missing", "Missing"),
        ],
        default="good",
    )
    status = fields.Selection(
        [
            ("pending", "Pending"),
            ("verified", "Verified"),
            ("discrepancy", "Discrepancy"),
        ],
        default="pending",
    )
    notes = fields.Text()

    def action_verify(self):
        """Verify the audit line and auto-detect discrepancies."""
        for line in self:
            has_discrepancy = False
            messages = []

            if (
                line.expected_employee_id
                and line.actual_employee_id
                and line.expected_employee_id != line.actual_employee_id
            ):
                has_discrepancy = True
                messages.append(
                    _(
                        "Employee mismatch: expected '%s', found '%s'."
                    )
                    % (
                        line.expected_employee_id.name,
                        line.actual_employee_id.name,
                    )
                )

            if line.condition in ("damaged", "missing"):
                has_discrepancy = True
                messages.append(
                    _("Asset condition: %s.") % line.condition
                )

            if has_discrepancy:
                line.write({"status": "discrepancy"})
                note = _("Discrepancy detected: ") + "; ".join(messages)
            else:
                line.write({"status": "verified"})
                note = _("Asset verified successfully.")

            if line.audit_id:
                line.audit_id.message_post(
                    body=_(
                        "Audit line for '%s': %s"
                    )
                    % (line.asset_id.name, note),
                    subtype_xmlid="mail.mt_note",
                )

    def action_mark_discrepancy(self):
        """Manually mark a line as having a discrepancy."""
        for line in self:
            line.write({"status": "discrepancy"})

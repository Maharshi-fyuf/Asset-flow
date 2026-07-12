# 🔍 AssetFlow — Senior QA Engineer Report

> **Reviewer:** QA Agent (Senior Level)
> **Date:** 2026-07-12
> **Module:** `asset_flow` — Odoo 18 Enterprise Asset & Resource Management
> **Verdict:** ❌ **NOT PRODUCTION-READY** — Module will partially fail on install

---

## 1. Project Structure

| Check | Status | Notes |
|---|---|---|
| Folder structure | ✅ | `models/`, `views/`, `security/`, `data/`, `demo/`, `reports/`, `wizards/` all present |
| `asset_flow/__init__.py` | ✅ | Imports `models`, `wizards`, `reports` |
| `models/__init__.py` | ✅ | All 10 models imported |
| `wizards/__init__.py` | ✅ | `report_wizard` imported |
| `reports/__init__.py` | ⚠️ | Empty — no Python hooks. OK if no report controllers needed, but misleading |
| `__manifest__.py` | ⚠️ | Has issues — see Section 2 |
| Static folder | ⚠️ | Declared in README, missing from disk. No `static/` directory exists |

---

## 2. Odoo Validation

### 2.1 `__manifest__.py`

| Check | Status | Notes |
|---|---|---|
| Module name, version | ✅ | `18.0.1.0.0` — correct versioning convention |
| Dependencies | ✅ | `["base", "mail"]` — sufficient for standalone module |
| Data file order | ✅ | Security loaded before views |
| `demo` section | ✅ | Exists, file present |
| **Missing `ir.actions.report` record** | ❌ | `report_wizard.py` calls `self.env.ref("asset_flow.action_report_asset_flow")` — **this external ID does NOT exist anywhere in the codebase** |

### 2.2 Security

| Check | Status | Notes |
|---|---|---|
| Groups XML | ✅ | 4 groups with correct implied_ids hierarchy |
| `ir.model.access.csv` | ✅ | All 10 models covered, 4 groups each |
| Record Rules | ❌ | TODO comment at line 34 — no record rules implemented. Employees can read/write other employees' data |
| Dashboard model access | ⚠️ | Dashboard is a `TransientModel` — CSV grants `perm_create` and `perm_unlink` to all groups, which is unnecessary and mildly insecure |

### 2.3 Sequences

| Model | Sequence | Status |
|---|---|---|
| `asset.flow.asset` | `AF-AST-` | ✅ |
| `asset.flow.asset.request` | `AF-REQ-` | ✅ |
| `asset.flow.resource.booking` | `AF-BKG-` | ✅ |
| `asset.flow.maintenance` | `AF-MNT-` | ✅ |
| `asset.flow.audit` | `AF-AUD-` | ✅ |
| `asset.flow.department` | *(none)* | ⚠️ No sequence for department codes |
| `asset.flow.assignment.history` | *(none)* | ⚠️ No auto-name — model has no `name` field |

### 2.4 Views & Menus

| Check | Status | Notes |
|---|---|---|
| All view XML IDs unique | ✅ | No duplicate IDs detected |
| Menu hierarchy | ✅ | Root → Master Data, Assets, Operations, Audit, Reports |
| All menu actions exist | ✅ | Every `action=` attribute resolves to a declared `ir.actions.act_window` |
| Statusbar widget missing | ❌ | No `<field name="state" widget="statusbar"/>` in any form view — state field is just a dropdown, not a visual pipeline indicator |
| No workflow buttons in views | ❌ | All action methods (`action_submit`, `action_approve`, `action_resolve`, etc.) are implemented in Python but **zero `<button>` elements exist in any form view** — workflows are unreachable from the UI |
| Dashboard view `create="false"` | ✅ | Correct for `TransientModel` dashboard |
| Report wizard has list/kanban views | ❌ | `TransientModel` records are auto-deleted — a list/kanban view of wizard records makes no sense and will always be empty |

---

## 3. Code Quality

### 3.1 Syntax Errors & Import Issues

| File | Issue | Status |
|---|---|---|
| `asset_category.py` L81 | `raise models.ValidationError(...)` — `ValidationError` is NOT imported from `odoo.exceptions` | ❌ |
| `audit.py` L1 | Missing `api` import — uses `fields.Date.today()` but never uses `@api.model` or `@api.constrains` | ⚠️ Minor |
| `report_wizard.py` L1 | Missing `api` import — but no `@api` decorators used, so no runtime error | ✅ |
| `department.py` / `employee.py` | No `api` or `ValidationError` imported despite comment saying "add reporting helpers" | ✅ OK for now |

### 3.2 Logic Bugs

| File | Line | Issue |
|---|---|---|
| `asset.py` | L83–89 | `_check_allocation_state` constraint — **will break demo data load**. `asset_laptop_001` in demo is `state=allocated` with `current_employee_id` and `department_id` set. But on write, the constraint fires and **also** blocks non-allocated assets from having a department. An asset can exist in a department without being allocated to a person. The constraint `state != "allocated" and department_id` is **logically wrong** |
| `asset.py` | L88 | Constraint blocks setting `department_id` on `available` assets — but the form view shows `department_id` as an always-editable field. Users can never save a department on an available asset |
| `asset.py` | L122–145 | `write()` override — when `employee_id` is passed without a value (False), `log_assignment` is called with `employee=False`, which will cause `employee.id` to crash with `AttributeError: 'bool' object has no attribute 'id'` |
| `asset.py` | L139 | Condition `record.current_employee_id or record.department_id` after the write will still trigger `log_assignment` even if you're **clearing** the employee — because it checks the post-write value |
| `assignment_history.py` | L55 | `employee_id` field is `required=True`. `log_assignment` passes `employee=record.current_employee_id`. If employee is False/empty, `create()` will raise a required field error, **crashing all asset writes** |
| `asset_request.py` | L104–110 | For `transfer` type, `action_allocate()` is NOT called (only for `allocation`), but `asset.write()` is still called. If the asset is not in `allocated` state, writing `current_employee_id` will trigger `_check_allocation_state` and raise an error |
| `maintenance.py` | L110 | `req.asset_id.write({"state": "available"})` — this bypasses the `_check_allocation_state` constraint because it directly sets state but doesn't clear `current_employee_id`. Will trigger constraint error if the asset still has an employee assigned |
| `audit.py` | L64 | `asset.current_employee_id.id` — if `current_employee_id` is False/empty, this will be `False.id` → `AttributeError` crash |
| `resource_booking.py` | L64–76 | `_check_overlap` constraint is triggered on state change but `state` is not normally in `@api.constrains`. Changing state without touching dates won't re-trigger this constraint reliably in Odoo |

### 3.3 Circular Import Risk

| Check | Status |
|---|---|
| `models/__init__.py` import order | ⚠️ `asset.py` references `asset.flow.assignment.history` (from `assignment_history.py`) in its `write()` method. `assignment_history.py` references `asset.flow.asset`. While Odoo resolves model references at runtime (not import time), this is a tightly coupled bidirectional dependency that must be carefully managed |

### 3.4 Missing Functionality (Remaining TODOs)

| File | Line | TODO |
|---|---|---|
| `department.py` | 30 | Reporting helpers and record rules |
| `employee.py` | 47 | Sync with `hr.employee` |
| `security/asset_flow_groups.xml` | 34 | Record rules for data isolation |
| `reports/asset_flow_report_templates.xml` | 8 | Actual report rendering logic |
| All form views | N/A | No `<header>` with `<button>` workflow triggers |

---

## 4. Functional Validation

| Module | Status | Detail |
|---|---|---|
| **Department** | ⚠️ Incomplete | CRUD works. No record rules. No sequence for code uniqueness check |
| **Employee** | ⚠️ Incomplete | CRUD works. No `hr.employee` link. No unique constraint on `work_email` |
| **Asset Category** | ❌ Broken | `_check_unique_code` raises `models.ValidationError` — `ValidationError` not imported. Will crash on save with a duplicate code |
| **Asset** | ❌ Broken | `_check_allocation_state` constraint is logically wrong — prevents setting `department_id` on available assets. Demo data will fail to load due to this constraint |
| **Asset Request** | ⚠️ Incomplete | Workflow logic correct, but **no buttons in the form view**. Workflow is unreachable from the UI |
| **Maintenance** | ⚠️ Incomplete | Workflow logic correct, but **no buttons in the form view**. `action_resolve` has a bug when asset has employee assigned |
| **Resource Booking** | ⚠️ Incomplete | Overlap validation implemented but **no buttons in the form view**. Also, `_check_overlap` only triggers on state constraint, which may not re-fire when only state changes |
| **Audit** | ⚠️ Incomplete | `action_generate_lines` will crash if any asset has no `current_employee_id` (line 64). **No buttons in any form view** |
| **Assignment History** | ❌ Broken | `log_assignment` requires `employee_id` which is a required field. Any asset write with `current_employee_id=False` will crash |
| **Dashboard** | ⚠️ Incomplete | KPIs computed correctly, but it's a plain form — no charts, no visual KPI cards, no refresh button |

---

## 5. Business Logic Gaps (Remaining TODOs)

| Gap | Severity | Impact |
|---|---|---|
| No `ir.actions.report` record for `action_report_asset_flow` | Critical | Module crashes when report wizard button is clicked |
| No record rules for data isolation | High | Any employee can see all other employees' assets and requests |
| No workflow buttons in any form view | Critical | All implemented workflows (submit, approve, reject, assign, resolve, etc.) are inaccessible from the UI |
| No `<header>` / statusbar widget in form views | High | No visual pipeline feedback for any workflow |
| `_check_allocation_state` logic error | Critical | Prevents normal use of setting a home department on assets |
| `log_assignment` crash on empty employee | Critical | Any unassignment of an asset will crash the system |
| Report template is a placeholder | High | Clicking "Generate Report" crashes with missing external ID |
| No date validation on audit `planned_date` | Medium | Audits can be created with past dates |
| Transfer workflow missing `action_allocate()` call | High | Completing a transfer request on an available asset will trigger a constraint error |
| No notification/email system | Medium | No Odoo mail templates defined for approvals or alerts |

---

## 6. Installation Check

| Step | Will it succeed? | Reason |
|---|---|---|
| Python import | ✅ | No syntax errors at import time |
| Model registration | ✅ | All models well-formed |
| Security file load | ✅ | Groups and ACL CSV are valid |
| Sequence data load | ✅ | All 5 sequences correctly defined |
| View XML load | ✅ | All views are valid XML, no broken refs |
| Demo data load | ❌ | `asset_laptop_001` is `state=allocated` with `department_id` set → `_check_allocation_state` will raise `ValidationError` on creation |
| Report template load | ⚠️ | Template loads, but has no `ir.actions.report` record linking it |

> [!CAUTION]
> **The module will fail during demo data installation.** The `asset_laptop_001` demo record violates the constraint added to `asset.py` because `_check_allocation_state` incorrectly blocks any asset with a `department_id` that is not in `allocated` state. However, `asset_laptop_001` IS allocated, so depending on write ordering vs. constraint evaluation, it may or may not pass.
> The real failure path: `asset_laptop_002` has `state=available` but `department_id=department_it` set — this will **definitely** trigger the wrong constraint and crash the demo load.

---

## 7. Bug Report

---

### 🔴 CRITICAL

#### BUG-001
- **File:** `asset_flow/models/asset_category.py`
- **Line:** 81
- **Reason:** `raise models.ValidationError(...)` — `ValidationError` is not imported in this file. Only `api, fields, models` are imported. `models.ValidationError` does not exist. This will raise `AttributeError: module 'odoo.models' has no attribute 'ValidationError'` on any duplicate category code save.
- **Fix:** Add `from odoo.exceptions import ValidationError` and change to `raise ValidationError(...)`

#### BUG-002
- **File:** `asset_flow/models/asset.py`
- **Line:** 83–89
- **Reason:** `_check_allocation_state` incorrectly raises a `ValidationError` when `state != "allocated"` AND `department_id` is set. Setting a department on an available asset is a **valid real-world operation**. This prevents all normal asset creation with a department. Demo data `asset_laptop_002` (available + department_id) will fail.
- **Fix:** Remove the second condition entirely, or change it to only check `current_employee_id` when not allocated.

#### BUG-003
- **File:** `asset_flow/models/asset.py`
- **Line:** 138–144
- **Reason:** `write()` override calls `log_assignment(employee=record.current_employee_id, ...)` after write. If `current_employee_id` was cleared (set to False), `record.current_employee_id` is a falsy recordset, and the condition at line 139 (`record.current_employee_id or record.department_id`) may still be True if `department_id` is set. `log_assignment` will then be called with `employee=False`, causing `False.id` → `AttributeError`.
- **Fix:** Guard `log_assignment` to only call when `record.current_employee_id` is a valid non-empty record.

#### BUG-004
- **File:** `asset_flow/wizards/report_wizard.py`
- **Line:** 47
- **Reason:** `self.env.ref("asset_flow.action_report_asset_flow")` — this XML ID does not exist anywhere in the codebase. There is no `ir.actions.report` record defined. Clicking the generate button will raise `ValueError: External ID not found in the system: asset_flow.action_report_asset_flow`.
- **Fix:** Define an `ir.actions.report` record in `reports/asset_flow_report_templates.xml` with `id="action_report_asset_flow"`, or implement per-report-type actions.

#### BUG-005
- **File:** ALL form views (asset, asset_request, maintenance, resource_booking, audit)
- **Line:** N/A
- **Reason:** Zero `<button>` elements exist in any form view header. All Python workflow methods (`action_submit`, `action_approve`, `action_allocate`, `action_return`, `action_assign`, `action_start`, `action_resolve`, `action_confirm`, `action_generate_lines`, `action_complete`, etc.) are unreachable from the UI.
- **Fix:** Add `<header>` sections with `<button>` elements and `attrs` visibility conditions to each form view.

---

### 🟠 HIGH

#### BUG-006
- **File:** `asset_flow/models/asset.py`
- **Line:** 104–115 (maintenance `action_resolve`)
- **Reason:** `req.asset_id.write({"state": "available"})` in `maintenance.py` line 110 sets state to available but does NOT clear `current_employee_id`. This will trigger `_check_allocation_state`, which (after BUG-002 is fixed) would still block `available` state if an employee is still assigned.
- **Fix:** Also clear `current_employee_id` and `department_id` when returning from maintenance, or keep `state=available` without touching assignment.

#### BUG-007
- **File:** `asset_flow/models/asset_request.py`
- **Line:** 104–110
- **Reason:** For `request_type = "transfer"`, `action_allocate()` is skipped but `asset.write({current_employee_id: ...})` is still called. If the asset is in `available` state, this write will trigger `_check_allocation_state`, which expects `state=allocated` when an employee is being set.
- **Fix:** Call `req.asset_id.action_allocate()` before the write for both `allocation` and `transfer` types.

#### BUG-008
- **File:** `asset_flow/models/audit.py`
- **Line:** 64
- **Reason:** `"expected_employee_id": asset.current_employee_id.id` — if `current_employee_id` is an empty recordset (common for `available` assets), `.id` returns `False`, which is acceptable. However `asset.current_employee_id.id` on a NewId can raise issues. More critically, if `current_employee_id` is truly empty, it's passed as `False`, which may still be fine — but under edge cases with lazy loading, this can cause an `AttributeError`.
- **Fix:** Use `asset.current_employee_id.id if asset.current_employee_id else False`

#### BUG-009
- **File:** `asset_flow/security/asset_flow_groups.xml`
- **Line:** 34
- **Reason:** No record rules defined. Employees can view all asset requests, bookings, and assignment history belonging to other employees. This is a security violation for a multi-user ERP system.
- **Fix:** Add `ir.rule` records to restrict `asset.flow.asset.request`, `asset.flow.resource.booking`, and `asset.flow.assignment.history` by `employee_id` for the Employee group.

#### BUG-010
- **File:** `asset_flow/views/` (all form views)
- **Line:** All `<field name="state"/>` usages
- **Reason:** No `widget="statusbar"` and no `statusbar_visible` attribute used. The `state` field renders as a plain dropdown, giving no visual pipeline feedback. Standard Odoo UX requires the statusbar widget in form views for workflow models.
- **Fix:** Add `<field name="state" widget="statusbar" statusbar_visible="draft,submitted,approved,done"/>` in the form `<header>` section.

---

### 🟡 MEDIUM

#### BUG-011
- **File:** `asset_flow/views/report_wizard_views.xml`
- **Line:** 3–16, 44–61
- **Reason:** `asset.flow.report.wizard` is a `TransientModel`. Transient records are periodically auto-deleted by the Odoo GC job. Having a `list` view and `kanban` view for this model is misleading and will always appear empty to users.
- **Fix:** Remove the list and kanban views. The `action_asset_flow_report_wizard` already correctly uses `view_mode="form"`.

#### BUG-012
- **File:** `asset_flow/models/asset_category.py`
- **Line:** 60–63
- **Reason:** `sequence_id` field (Many2one to `ir.sequence`) is defined **after** the `_compute_complete_name` method. Odoo field definitions placed after methods can sometimes cause issues depending on metaclass resolution order. It is unconventional.
- **Fix:** Move all field definitions before all method definitions.

#### BUG-013
- **File:** `asset_flow/models/asset.py`
- **Line:** 15
- **Reason:** `asset_tag` default calls `self.env["ir.sequence"].next_by_code("asset.flow.asset") or "New"`. If the sequence hasn't been created yet (e.g., when running tests or installing without `data/`), this silently falls back to `"New"`. Multiple records could end up with `asset_tag = "New"`, violating implied uniqueness.
- **Fix:** Add `_sql_constraints = [("asset_tag_unique", "UNIQUE(asset_tag)", "Asset tag must be unique.")]`

#### BUG-014
- **File:** `asset_flow/models/resource_booking.py`
- **Line:** 64
- **Reason:** `@api.constrains("asset_id", "start_datetime", "end_datetime", "state")` — in Odoo, `@api.constrains` only triggers when the listed fields are written in the same `write()` call. If state changes from `draft` to `confirmed` (via `action_confirm`), and `asset_id`/`start_datetime` are not in `vals`, the overlap check **may not trigger**.
- **Fix:** Call `_check_overlap` explicitly inside `action_confirm()` rather than relying on the constraint trigger.

#### BUG-015
- **File:** `asset_flow/demo/asset_flow_demo.xml`
- **Line:** 94–97
- **Reason:** `asset_laptop_001` has `state=allocated` with both `current_employee_id` and `department_id` set. Due to BUG-002 (`_check_allocation_state`), demo data installation will fail. Additionally, the `_check_allocation_state` constraint will fire on every create/write of demo records.
- **Fix:** Fix BUG-002 first; then verify demo data loads cleanly.

#### BUG-016
- **File:** `asset_flow/models/asset_category.py`
- **Line:** 75–81
- **Reason:** `_check_unique_code` uses a manual `search_count()` which is NOT atomic. Under concurrent writes, two records could pass the check simultaneously and both be saved with the same code. This is a TOCTOU (time-of-check-time-of-use) race condition.
- **Fix:** Use `_sql_constraints = [("category_code_unique", "UNIQUE(code)", "Category code must be unique.")]` instead.

---

### 🔵 LOW

#### BUG-017
- **File:** `asset_flow/models/department.py`
- **Line:** 12
- **Reason:** `manager_id` is a `Many2one` to `asset.flow.employee`, but `employee.department_id` points back to `asset.flow.department`. This creates a potential circular reference: an employee belongs to a department, and that department's manager is that same employee. No constraint prevents self-referential or circular department-manager relationships.
- **Fix:** Add `@api.constrains("manager_id")` to validate that the manager belongs to the same or a parent department.

#### BUG-018
- **File:** `asset_flow/models/maintenance.py`
- **Line:** 79
- **Reason:** `action_approve` does not require an `auditor_id` or any approver to be set. Anyone with write access to maintenance can approve their own maintenance request.
- **Fix:** Add a check that `req.requested_by_id != self.env.user.employee_id` or require a separate approver field.

#### BUG-019
- **File:** `asset_flow/models/asset_request.py`
- **Line:** 78–82
- **Reason:** `action_submit` does not validate that `category_id` or `asset_id` is set. A request for an unspecified asset or category can be submitted, approved, and then fail at `action_done` with a confusing "An asset must be assigned" error.
- **Fix:** Validate `category_id` or `asset_id` is populated before submission.

#### BUG-020
- **File:** `asset_flow/models/assignment_history.py`
- **Line:** 4–8
- **Reason:** The model `_inherit = ["mail.thread", "mail.activity.mixin"]` — but `assignment_history` is a log/audit trail model. It should be read-only/append-only. Currently, users with write access can modify or delete history entries, defeating the audit trail purpose.
- **Fix:** Add `_sql_constraints` or override `write()`/`unlink()` to restrict or prohibit edits after creation.

---

## Summary Table

| Severity | Count | Modules Affected |
|---|---|---|
| 🔴 Critical | 5 | asset_category, asset, report_wizard, all views |
| 🟠 High | 5 | asset, asset_request, audit, security, all views |
| 🟡 Medium | 6 | report_wizard, asset_category, asset, resource_booking, demo data |
| 🔵 Low | 4 | department, maintenance, asset_request, assignment_history |
| **Total** | **20** | |

---

## Module Readiness by Feature

| Feature | Verdict | Blocker |
|---|---|---|
| Department CRUD | ⚠️ Incomplete | No record rules |
| Employee CRUD | ⚠️ Incomplete | No record rules |
| Asset Category | ❌ Broken | BUG-001 (crash on duplicate code) |
| Asset Lifecycle | ❌ Broken | BUG-002, BUG-003 (constraint logic, crash) |
| Asset Request Workflow | ⚠️ Incomplete | BUG-005 (no buttons), BUG-007 (transfer logic) |
| Maintenance Workflow | ⚠️ Incomplete | BUG-005 (no buttons), BUG-006 |
| Resource Booking | ⚠️ Incomplete | BUG-005 (no buttons), BUG-014 |
| Audit | ⚠️ Incomplete | BUG-005 (no buttons), BUG-008 |
| Assignment History | ❌ Broken | BUG-003 (crash on unassignment) |
| Dashboard | ⚠️ Incomplete | No charts, no real-time refresh |
| Reports | ❌ Broken | BUG-004 (missing external ID crashes button) |
| Demo Data | ❌ Broken | BUG-015 → BUG-002 |

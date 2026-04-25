# Admin Audit Log Implementation

## Task: Implement an admin audit log feature
- Update AuditLog model and related functionality
- Log admin actions (CRUD on elections, candidates, voters, and results exports)

## Steps
- [x] 1. Update `polls/models.py` — expand AuditLog model with granular action choices
- [x] 2. Update `polls/views_admin.py` — add `create_audit_log()` helper and log all admin actions
- [x] 3. Update `polls/views.py` — add logging to login, vote, password change
- [x] 4. Update `polls/urls.py` — add audit_log route
- [x] 5. Create `templates/polls/audit_log.html`
- [x] 6. Update `templates/polls/admin_dashboard.html` — add audit log link
- [x] 7. Generate and apply migrations
- [x] 8. Test functionality (syntax check passed, migrations applied)


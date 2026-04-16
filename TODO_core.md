# TODO: Complete Voting System - Core Requirements Plan

**Current:** Basic polls app with auth/register/login/email-login, one-vote-per-poll.

**High Priority (Refactor to match requirements):**
1. [ ] Rename Poll → Election models/views.
2. [ ] Add Voter model (unique ID like national_id, verified status).
3. [ ] Add Candidate model (name, photo, bio, position).
4. [ ] Role-based groups (is_admin, is_voter).
5. [ ] Admin voter registration/verification.
6. [ ] Election CRUD with start/end times.
7. [ ] Position grouping for candidates.
8. [ ] Vote per election per voter.
9. [ ] Results reporting (real-time, PDF).
10. [ ] Security: CSRF/XSS (Django default), audit logs.
11. [ ] UI: Dashboards, responsive templates.
12. [ ] Notifications (email setup).

**Followup:** Install django-crispy-forms bootstrap, reportlab for PDF, celery for notifications. Migrate after model changes.

Proceed step-by-step?

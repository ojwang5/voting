# Per-Election Voter Registration - Implementation Steps

- [x] Step 1: Add ElectionRegistration model to polls/models.py
- [x] Step 2: Create and run migration (0006_electionregistration.py)
- [x] Step 3: Update polls/views.py (_partition_elections_for_user, dashboard, vote, add register_for_election)
- [x] Step 4: Update polls/views_admin.py (admin election voter management views)
- [x] Step 5: Update polls/urls.py (new routes)
- [x] Step 6: Update templates/polls/dashboard.html (registration UI)
- [x] Step 7: Update templates/polls/admin_elections.html (manage voters link)
- [x] Step 8: Create templates/polls/admin_election_voters.html
- [x] Step 9: Syntax validation passed

## Summary of Changes

### New Model: `ElectionRegistration` (polls/models.py)
- Links `PoliceUser` ↔ `Election` with `registered_at` timestamp and `registered_by` audit trail
- Unique constraint prevents duplicate registrations

### Voter Dashboard (templates/polls/dashboard.html)
- **Active Elections**: Shows registered active elections with "Vote Now" button
- **Upcoming Registered**: Shows upcoming elections the voter is registered for
- **Available Elections**: Shows upcoming eligible elections with "Register" button
- **Past Elections**: Shows ended registered elections

### Voter Self-Registration (polls/views.py)
- New `register_for_election` view allows voters to register themselves for eligible upcoming elections
- Registration is required before voting (enforced in `vote` view)

### Admin Election Voter Management (polls/views_admin.py)
- `admin_election_voters`: View registered and eligible voters per election
- `admin_register_voter_to_election`: Admin can register voters
- `admin_unregister_voter_from_election`: Admin can unregister voters (blocked if already voted)

### URLs (polls/urls.py)
- `/elections/<id>/register/` - Self-registration for voters
- `/admin/elections/<id>/voters/` - Admin voter management
- `/admin/elections/<id>/voters/<vid>/register/` - Admin register voter
- `/admin/elections/<id>/voters/<vid>/unregister/` - Admin unregister voter

### Templates
- `templates/polls/admin_election_voters.html` - New admin interface for managing election voters
- `templates/polls/admin_elections.html` - Added "Manage Voters" button per election

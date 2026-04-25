with open('polls/views_admin.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = """def toggle_election_status(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    election.is_active = not election.is_active
    election.save()
    status = 'activated' if election.is_active else 'deactivated'
    create_audit_log(
        request.user, AuditLog.ACTION_ELECTION_TOGGLE,
        f\"Election {status}: {election.title} (ID: {election.id})\", request,
        target_model='Election', target_id=election.id
    )
    messages.success(request, f'Election {status} successfully!')
    return redirect('polls:admin_elections')"""

new = """def toggle_election_status(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    create_audit_log(
        request.user, AuditLog.ACTION_ELECTION_TOGGLE,
        f\"Election status viewed (auto-activation): {election.title} (ID: {election.id})\", request,
        target_model='Election', target_id=election.id
    )
    messages.info(request, 'Election activation is now automatic based on start/end times.')
    return redirect('polls:admin_elections')"""

if old in content:
    content = content.replace(old, new)
    with open('polls/views_admin.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Replaced successfully')
else:
    print('Old text not found')

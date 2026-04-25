import re

with open('polls/views_admin.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the corrupted edit_election -> delete_election transition
broken = '''
        for pos_id in selected_positions:
            try:
                pos = Position.objects.get(id=pos_id)
                ElectionPosition.objects.create(election=election, position=pos)
            except Position.DoesNotExist:
                pass
        

    election = get_object_or_404(Election, pk=election_id)
    if request.method == 'POST':
        create_audit_log(
            request.user, AuditLog.ACTION_ELECTION_DELETE,
            f"Deleted election: {election.title} (ID: {election.id})", request,
            target_model='Election', target_id=election.id
        )
        election.delete()
        messages.success(request, 'Election deleted successfully!')
    return redirect('polls:admin_elections')
'''

fixed = '''
        for pos_id in selected_positions:
            try:
                pos = Position.objects.get(id=pos_id)
                ElectionPosition.objects.create(election=election, position=pos)
            except Position.DoesNotExist:
                pass
        
        create_audit_log(
            request.user, AuditLog.ACTION_ELECTION_UPDATE,
            f"Updated election: {election.title} (ID: {election.id})", request,
            target_model='Election', target_id=election.id
        )
        messages.success(request, 'Election updated successfully!')
        return redirect('polls:admin_elections')
    
    return render(request, 'polls/create_election.html', {
        'election': election,
        'positions': positions,
        'selected_position_ids': selected_position_ids
    })

@login_required
@user_passes_test(is_superadmin)
def delete_election(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    if request.method == 'POST':
        create_audit_log(
            request.user, AuditLog.ACTION_ELECTION_DELETE,
            f"Deleted election: {election.title} (ID: {election.id})", request,
            target_model='Election', target_id=election.id
        )
        election.delete()
        messages.success(request, 'Election deleted successfully!')
    return redirect('polls:admin_elections')
'''

if broken in content:
    content = content.replace(broken, fixed)
    with open('polls/views_admin.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed successfully')
else:
    print('Pattern not found - file may already be fixed or differently formatted')

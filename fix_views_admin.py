import re

with open('polls/views_admin.py', 'r') as f:
    content = f.read()

old_func = """def export_results_csv(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    create_audit_log(request.user, AuditLog.ACTION_EXPORT_RESULTS,
        f'Exported results for election: {election.title} (ID: {election.id}) as CSV', request, 'Election', election.id)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="results_{election_id}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Candidate', 'Position', 'Rank', 'Force Number', 'Votes', 'Percentage'])
    total = election.vote_set.count()
    for candidate in election.candidates.all():
        votes = candidate.vote_set.count()
        pct = (votes / total * 100) if total > 0 else 0
        writer.writerow([candidate.name, candidate.position.name, candidate.get_rank_display(),
            candidate.force_number, votes, f'{pct:.1f}%'])
    return response"""

new_func = """def export_results_csv(request, election_id):
    election = get_object_or_404(Election.objects.prefetch_related('positions'), pk=election_id)
    create_audit_log(request.user, AuditLog.ACTION_EXPORT_RESULTS,
        f'Exported results for election: {election.title} (ID: {election.id}) as CSV', request, 'Election', election.id)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="results_{election_id}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Position', 'Candidate', 'Rank', 'Force Number', 'Votes', 'Percentage', 'Position Total Votes'])
    
    # Group candidates by position and calculate per-position stats
    from collections import defaultdict
    position_candidates = defaultdict(list)
    for candidate in election.candidates.select_related('position').all():
        position_candidates[candidate.position].append(candidate)
    
    for position in sorted(position_candidates.keys(), key=lambda p: p.id):
        candidates = position_candidates[position]
        total = sum(c.vote_set.count() for c in candidates)
        for candidate in candidates:
            votes = candidate.vote_set.count()
            pct = (votes / total * 100) if total > 0 else 0
            writer.writerow([position.name, candidate.name, candidate.get_rank_display(),
                candidate.force_number, votes, f'{pct:.1f}%', total])
    
    return response"""

if old_func in content:
    content = content.replace(old_func, new_func)
    with open('polls/views_admin.py', 'w') as f:
        f.write(content)
    print('SUCCESS')
else:
    print('NOT FOUND')


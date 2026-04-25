from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Count
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import csv
import json
import io
import secrets
import string
from .models import Position, Candidate, PoliceUser, Election, Vote, ElectionPosition, AuditLog, ElectionRegistration

from .forms import PoliceUserRegistrationForm, PoliceUserEditForm, PositionForm, CandidateForm, BulkVoterUploadForm


def is_admin(user):
    return user.role in ['SUPER_ADMIN', 'ADMIN']


def is_superadmin(user):
    return user.role == 'SUPER_ADMIN'


def create_audit_log(user, action, details, request=None, target_model='', target_id=None):
    ip_address = request.META.get('REMOTE_ADDR') if request else None
    AuditLog.objects.create(
        user=user, action=action, details=details,
        ip_address=ip_address, target_model=target_model, target_id=target_id
    )


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    now = timezone.now()
    return render(request, 'polls/admin_dashboard.html', {
        'positions_count': Position.objects.count(),
        'elections_count': Election.objects.count(),
        'active_elections': Election.objects.filter(start_time__lte=now, end_time__gte=now).count(),
        'candidates_count': Candidate.objects.count(),
        'voters_count': PoliceUser.objects.filter(role='VOTER').count(),
        'is_admin': request.user.role == 'ADMIN',
        'is_superadmin': request.user.role == 'SUPER_ADMIN',
    })


@login_required
@user_passes_test(is_admin)
def admin_positions(request):
    positions = Position.objects.all().order_by('name')
    if request.method == 'POST':
        if request.user.role != 'SUPER_ADMIN':
            messages.error(request, 'Only Super Admins can create positions.')
            return redirect('polls:admin_positions')
        form = PositionForm(request.POST)
        if form.is_valid():
            position = form.save()
            create_audit_log(request.user, AuditLog.ACTION_POSITION_CREATE,
                f'Created position: {position.name}', request, 'Position', position.id)
            messages.success(request, 'Position created successfully!')
            return redirect('polls:admin_positions')
    else:
        form = PositionForm()
    return render(request, 'polls/admin_positions.html', {
        'positions': positions, 'form': form,
        'is_superadmin': request.user.role == 'SUPER_ADMIN'
    })


@login_required
@user_passes_test(is_superadmin)
def edit_position(request, position_id):
    position = get_object_or_404(Position, pk=position_id)
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            form.save()
            create_audit_log(request.user, AuditLog.ACTION_POSITION_UPDATE,
                f'Updated position: {position.name}', request, 'Position', position.id)
            messages.success(request, 'Position updated successfully!')
            return redirect('polls:admin_positions')
    else:
        form = PositionForm(instance=position)
    return render(request, 'polls/admin_position_edit.html', {'form': form, 'position': position})


@login_required
@user_passes_test(is_superadmin)
def delete_position(request, position_id):
    position = get_object_or_404(Position, pk=position_id)
    if request.method == 'POST':
        create_audit_log(request.user, AuditLog.ACTION_POSITION_DELETE,
            f'Deleted position: {position.name}', request, 'Position', position.id)
        position.delete()
        messages.success(request, 'Position deleted successfully!')
    return redirect('polls:admin_positions')


@login_required
@user_passes_test(is_admin)
def admin_elections(request):
    elections = Election.objects.all().prefetch_related('positions').order_by('-start_time')
    return render(request, 'polls/admin_elections.html', {
        'elections': elections,
        'now': timezone.now(),
        'positions': Position.objects.all(),
        'is_superadmin': request.user.role == 'SUPER_ADMIN'
    })


@login_required
@user_passes_test(is_superadmin)
def create_election(request):
    from .models import ElectionPosition
    from datetime import datetime
    positions = Position.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        start_time = request.POST.get('start_time', '').strip()
        end_time = request.POST.get('end_time', '').strip()
        eligible_ranks = request.POST.get('eligible_ranks', '').strip()
        eligible_stations = request.POST.get('eligible_stations', '').strip()
        selected_positions = request.POST.getlist('positions')
        if not title:
            messages.error(request, 'Election title is required.')
            return render(request, 'polls/create_election.html', {'positions': positions, 'selected_position_ids': selected_positions})
        if not start_time or not end_time:
            messages.error(request, 'Start time and end time are required.')
            return render(request, 'polls/create_election.html', {'positions': positions, 'selected_position_ids': selected_positions})
        if not selected_positions:
            messages.error(request, 'At least one position must be selected.')
            return render(request, 'polls/create_election.html', {'positions': positions, 'selected_position_ids': selected_positions})
        try:
            start_dt = timezone.make_aware(datetime.strptime(start_time, '%Y-%m-%dT%H:%M'))
            end_dt = timezone.make_aware(datetime.strptime(end_time, '%Y-%m-%dT%H:%M'))
        except ValueError as e:
            messages.error(request, f'Invalid date/time format: {str(e)}')
            return render(request, 'polls/create_election.html', {'positions': positions, 'selected_position_ids': selected_positions})
        if start_dt >= end_dt:
            messages.error(request, 'End time must be after start time.')
            return render(request, 'polls/create_election.html', {'positions': positions, 'selected_position_ids': selected_positions})
        try:
            election = Election.objects.create(title=title, description=description,
                start_time=start_dt, end_time=end_dt, eligible_ranks=eligible_ranks,
                eligible_stations=eligible_stations, created_by=request.user)
            positions_added = 0
            for pos_id in selected_positions:
                try:
                    pos = Position.objects.get(id=pos_id)
                    ElectionPosition.objects.create(election=election, position=pos)
                    positions_added += 1
                except Position.DoesNotExist:
                    pass
            if positions_added == 0:
                election.delete()
                messages.error(request, 'No valid positions found. Election not created.')
                return render(request, 'polls/create_election.html', {'positions': positions, 'selected_position_ids': selected_positions})
            create_audit_log(request.user, AuditLog.ACTION_ELECTION_CREATE,
                f'Created election: {election.title} (ID: {election.id}, positions: {positions_added})', request, 'Election', election.id)
            messages.success(request, f'Election "{title}" created with {positions_added} position(s)!')
            return redirect('polls:admin_elections')
        except Exception as e:
            messages.error(request, f'Error creating election: {str(e)}')
            return render(request, 'polls/create_election.html', {'positions': positions, 'selected_position_ids': selected_positions})
    return render(request, 'polls/create_election.html', {'positions': positions, 'selected_position_ids': []})


@login_required
@user_passes_test(is_superadmin)
def edit_election(request, election_id):
    from .models import ElectionPosition
    from datetime import datetime
    election = get_object_or_404(Election.objects.prefetch_related('positions'), pk=election_id)
    positions = Position.objects.all()
    selected_position_ids = [str(pos.id) for pos in election.positions.all()]
    if request.method == 'POST':
        election.title = request.POST.get('title', election.title)
        election.description = request.POST.get('description', '')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        election.eligible_ranks = request.POST.get('eligible_ranks', '')
        election.eligible_stations = request.POST.get('eligible_stations', '')
        if start_time and end_time:
            try:
                election.start_time = timezone.make_aware(datetime.strptime(start_time, '%Y-%m-%dT%H:%M'))
                election.end_time = timezone.make_aware(datetime.strptime(end_time, '%Y-%m-%dT%H:%M'))
            except ValueError as e:
                messages.error(request, f'Invalid date/time format: {str(e)}')
                return render(request, 'polls/create_election.html', {'election': election, 'positions': positions, 'selected_position_ids': selected_position_ids})
        election.save()
        selected_positions = request.POST.getlist('positions')
        election.positions.clear()
        for pos_id in selected_positions:
            try:
                pos = Position.objects.get(id=pos_id)
                ElectionPosition.objects.create(election=election, position=pos)
            except Position.DoesNotExist:
                pass
        create_audit_log(request.user, AuditLog.ACTION_ELECTION_UPDATE,
            f'Updated election: {election.title} (ID: {election.id})', request, 'Election', election.id)
        messages.success(request, 'Election updated successfully!')
        return redirect('polls:admin_elections')
    return render(request, 'polls/create_election.html', {'election': election, 'positions': positions, 'selected_position_ids': selected_position_ids})


@login_required
@user_passes_test(is_superadmin)
def toggle_election_status(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    messages.info(request, f'Election status is automatically determined by start/end times. Currently: {"active" if election.is_open() else "inactive"}.')
    return redirect('polls:admin_elections')


@login_required
@user_passes_test(is_superadmin)
def delete_election(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    if request.method == 'POST':
        create_audit_log(request.user, AuditLog.ACTION_ELECTION_DELETE,
            f'Deleted election: {election.title} (ID: {election.id})', request, 'Election', election.id)
        election.delete()
        messages.success(request, 'Election deleted successfully!')
    return redirect('polls:admin_elections')


@login_required
@user_passes_test(is_admin)
@require_http_methods(['GET', 'POST'])
def admin_register_voter(request):
    if request.method == 'POST':
        form = PoliceUserRegistrationForm(request.POST)
        if form.is_valid():
            voter = form.save(commit=False)
            auto_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
            voter.username = str(voter.force_number)
            voter.role = 'VOTER'
            voter.is_staff = False
            voter.is_active_voter = True
            voter.set_password(auto_password)
            voter.is_active = True
            voter.must_change_password = True
            voter.save()
            create_audit_log(request.user, AuditLog.ACTION_VOTER_CREATE,
                f'Registered voter: {voter.username} (Force #{voter.force_number})', request, 'PoliceUser', voter.id)
            request.session['registered_voter_credentials'] = {
                'username': voter.username, 'password': auto_password,
                'force_number': voter.force_number, 'full_name': voter.get_full_name()
            }
            messages.success(request, f'Voter {voter.username} registered successfully!')
            return redirect('polls:admin_voter_credentials')
    else:
        form = PoliceUserRegistrationForm(initial={'role': 'VOTER', 'is_active_voter': True})
        form.fields['role'].disabled = True
    return render(request, 'polls/register_voter.html', {'form': form, 'title': 'Register New Voter'})


@login_required
@user_passes_test(is_admin)
def admin_voter_credentials(request):
    credentials = request.session.pop('registered_voter_credentials', None)
    if not credentials:
        credentials = request.session.pop('reset_voter_credentials', None)
    if not credentials:
        messages.error(request, 'No credentials to display.')
        return redirect('polls:admin_register_voter')
    return render(request, 'polls/voter_credentials.html', {'credentials': credentials})


@login_required
@user_passes_test(is_admin)
def admin_voters(request):
    voters = PoliceUser.objects.filter(role='VOTER').order_by('-date_joined')
    return render(request, 'polls/admin_voters.html', {
        'voters': voters, 'is_superadmin': request.user.role == 'SUPER_ADMIN'
    })


@login_required
@user_passes_test(is_admin)
def admin_edit_voter(request, voter_id):
    voter = get_object_or_404(PoliceUser, pk=voter_id)
    if request.method == 'POST':
        form = PoliceUserEditForm(request.POST, instance=voter)
        if form.is_valid():
            updated_voter = form.save(commit=False)
            updated_voter.role = 'VOTER'
            updated_voter.is_staff = False
            updated_voter.save()
            create_audit_log(request.user, AuditLog.ACTION_VOTER_UPDATE,
                f'Updated voter: {voter.username} (Force #{voter.force_number})', request, 'PoliceUser', voter.id)
            messages.success(request, f'Voter {voter.username} updated successfully!')
            return redirect('polls:admin_voters')
    else:
        form = PoliceUserEditForm(instance=voter)
        form.fields['role'].disabled = True
    return render(request, 'polls/edit_voter.html', {'form': form, 'voter': voter})


@login_required
@user_passes_test(is_admin)
def admin_delete_voter(request, voter_id):
    voter = get_object_or_404(PoliceUser, pk=voter_id)
    if request.method == 'POST':
        create_audit_log(request.user, AuditLog.ACTION_VOTER_DELETE,
            f'Deleted voter: {voter.username} (Force #{voter.force_number})', request, 'PoliceUser', voter.id)
        voter.delete()
        messages.success(request, 'Voter deleted successfully!')
    return redirect('polls:admin_voters')


@login_required
@user_passes_test(is_admin)
def admin_reset_voter_password(request, voter_id):
    voter = get_object_or_404(PoliceUser, pk=voter_id)
    if request.method == 'POST':
        new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
        voter.set_password(new_password)
        voter.must_change_password = True
        voter.save()
        create_audit_log(request.user, AuditLog.ACTION_VOTER_RESET_PASSWORD,
            f'Reset password for voter: {voter.username} (Force #{voter.force_number})', request, 'PoliceUser', voter.id)
        request.session['reset_voter_credentials'] = {
            'username': voter.username, 'password': new_password,
            'force_number': voter.force_number, 'full_name': voter.get_full_name()
        }
        messages.success(request, f'Password reset for {voter.username}!')
        return redirect('polls:admin_voter_credentials')
    return redirect('polls:admin_voters')


@login_required
@user_passes_test(is_superadmin)
def admin_register_candidate(request):
    elections = Election.objects.prefetch_related('positions').all()
    positions = Position.objects.all()
    election_positions_map = {}
    for election in elections:
        election_positions_map[str(election.id)] = [{'id': pos.id, 'name': pos.name} for pos in election.positions.all()]
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.created_by = request.user
            candidate.save()
            create_audit_log(request.user, AuditLog.ACTION_CANDIDATE_CREATE,
                f'Registered candidate: {candidate.name} (Force #{candidate.force_number}) for {candidate.election.title}',
                request, 'Candidate', candidate.id)
            messages.success(request, f'Candidate {candidate.name} registered successfully!')
            return redirect('polls:admin_candidates')
    else:
        form = CandidateForm()
    return render(request, 'polls/register_candidate.html', {
        'form': form, 'elections': elections, 'positions': positions,
        'election_positions_json': json.dumps(election_positions_map)
    })


@login_required
@user_passes_test(is_superadmin)
def admin_edit_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            form.save()
            create_audit_log(request.user, AuditLog.ACTION_CANDIDATE_UPDATE,
                f'Updated candidate: {candidate.name} (Force #{candidate.force_number})', request, 'Candidate', candidate.id)
            messages.success(request, f'Candidate {candidate.name} updated successfully!')
            return redirect('polls:admin_candidates')
    else:
        form = CandidateForm(instance=candidate)
    elections = Election.objects.prefetch_related('positions').all()
    election_positions_map = {}
    all_positions = Position.objects.all()
    for election in elections:
        election_positions = election.positions.all()
        positions_list = [{'id': pos.id, 'name': pos.name} for pos in election_positions]
        if not positions_list and candidate.election_id == election.id:
            positions_list.append({'id': candidate.position.id, 'name': f'{candidate.position.name} (Current)'})
        if not positions_list:
            positions_list = [{'id': pos.id, 'name': pos.name} for pos in all_positions]
        election_positions_map[str(election.id)] = positions_list
    return render(request, 'polls/edit_candidate.html', {
        'form': form, 'candidate': candidate, 'elections': elections,
        'positions': all_positions, 'election_positions_json': json.dumps(election_positions_map),
        'current_position_id': candidate.position.id
    })


@login_required
@user_passes_test(is_superadmin)
def admin_delete_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    if request.method == 'POST':
        create_audit_log(request.user, AuditLog.ACTION_CANDIDATE_DELETE,
            f'Deleted candidate: {candidate.name} (Force #{candidate.force_number}) from {candidate.election.title}',
            request, 'Candidate', candidate.id)
        candidate.delete()
        messages.success(request, 'Candidate deleted successfully!')
    return redirect('polls:admin_candidates')


@login_required
@user_passes_test(is_admin)
def admin_candidates(request):
    candidates = Candidate.objects.all().select_related('election', 'position').order_by('-id')
    return render(request, 'polls/admin_candidates.html', {
        'candidates': candidates, 'is_superadmin': request.user.role == 'SUPER_ADMIN'
    })


@login_required
def view_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    if request.user.role == 'VOTER':
        if not candidate.election.is_voter_eligible(request.user):
            messages.error(request, 'You are not eligible to view candidates for this election.')
            return redirect('polls:elections')
    votes_count = candidate.vote_set.count()
    election = candidate.election
    total_votes = election.vote_set.count()
    vote_percentage = (votes_count / total_votes * 100) if total_votes > 0 else 0
    return render(request, 'polls/view_candidate.html', {
        'candidate': candidate, 'votes_count': votes_count,
        'vote_percentage': vote_percentage, 'election': election,
        'is_admin': request.user.role in ['SUPER_ADMIN', 'ADMIN']
    })


@login_required
@user_passes_test(is_admin)
def export_voters_csv(request):
    create_audit_log(request.user, AuditLog.ACTION_EXPORT_VOTERS, 'Exported voters as CSV', request)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="voters.csv"'
    writer = csv.writer(response)
    writer.writerow(['Username', 'Force Number', 'Full Name', 'Rank', 'Station', 'Phone', 'Email', 'Votes Cast', 'Registered Date', 'Status'])
    for voter in PoliceUser.objects.filter(role='VOTER'):
        writer.writerow([voter.username, voter.force_number, voter.get_full_name(),
            voter.get_rank_display(), voter.station, voter.phone, voter.email,
            voter.votes.count(), voter.date_joined.strftime('%Y-%m-%d'),
            'Active' if voter.is_active else 'Inactive'])
    return response


@login_required
@user_passes_test(is_admin)
def export_voters_pdf(request):
    create_audit_log(request.user, AuditLog.ACTION_EXPORT_VOTERS, 'Exported voters as PDF', request)
    return HttpResponse('PDF export requires reportlab. Please use CSV export instead.', content_type='text/plain')


@login_required
@user_passes_test(is_admin)
def export_voters_docx(request):
    create_audit_log(request.user, AuditLog.ACTION_EXPORT_VOTERS, 'Exported voters as DOCX', request)
    return HttpResponse('DOCX export requires python-docx. Please use CSV export instead.', content_type='text/plain')


@login_required
@user_passes_test(is_admin)
def export_candidates_csv(request):
    create_audit_log(request.user, AuditLog.ACTION_EXPORT_CANDIDATES, 'Exported candidates as CSV', request)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="candidates.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Force Number', 'Rank', 'Position', 'Election', 'Votes'])
    for candidate in Candidate.objects.all().select_related('election', 'position'):
        writer.writerow([candidate.name, candidate.force_number, candidate.get_rank_display(),
            candidate.position.name, candidate.election.title, candidate.vote_set.count()])
    return response


@login_required
@user_passes_test(is_admin)
def export_candidates_pdf(request):
    create_audit_log(request.user, AuditLog.ACTION_EXPORT_CANDIDATES, 'Exported candidates as PDF', request)
    return HttpResponse('PDF export requires reportlab. Please use CSV export instead.', content_type='text/plain')


@login_required
@user_passes_test(is_admin)
def export_candidates_docx(request):
    create_audit_log(request.user, AuditLog.ACTION_EXPORT_CANDIDATES, 'Exported candidates as DOCX', request)
    return HttpResponse('DOCX export requires python-docx. Please use CSV export instead.', content_type='text/plain')


@login_required
@user_passes_test(is_admin)
def export_results_csv(request, election_id):
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
    return response


@login_required
@user_passes_test(is_admin)
def export_results_pdf(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    create_audit_log(request.user, AuditLog.ACTION_EXPORT_RESULTS,
        f'Exported results for election: {election.title} (ID: {election.id}) as PDF', request, 'Election', election.id)
    return HttpResponse('PDF export requires reportlab. Please use CSV export instead.', content_type='text/plain')


@login_required
@user_passes_test(is_admin)
def export_results_docx(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    create_audit_log(request.user, AuditLog.ACTION_EXPORT_RESULTS,
        f'Exported results for election: {election.title} (ID: {election.id}) as DOCX', request, 'Election', election.id)
    return HttpResponse('DOCX export requires python-docx. Please use CSV export instead.', content_type='text/plain')


def _normalize_bulk_key(value):
    return str(value).strip().lower() if value is not None else ''


def _normalize_bulk_value(value):
    return str(value).strip() if value is not None else ''


def _load_bulk_voter_rows(uploaded_file, extension):
    rows = []
    if extension == 'csv':
        decoded = uploaded_file.read().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(decoded))
        for row in reader:
            rows.append(row)
    elif extension in ('xlsx', 'xls'):
        try:
            import openpyxl
        except ImportError:
            raise ImportError('openpyxl is required for Excel support. Install: pip install openpyxl')
        wb = openpyxl.load_workbook(uploaded_file)
        ws = wb.active
        headers = [str(cell.value).strip() if cell.value else '' for cell in ws[1]]
        for row in ws.iter_rows(min_row=2, values_only=True):
            row_dict = {}
            for i, value in enumerate(row):
                if i < len(headers) and headers[i]:
                    row_dict[headers[i]] = str(value).strip() if value is not None else ''
            rows.append(row_dict)
    return rows


@login_required
@user_passes_test(is_admin)
def bulk_register_voters(request):
    created_voters = []
    errors = []
    if request.method == 'POST':
        form = BulkVoterUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            ext = uploaded_file.name.lower().split('.')[-1]
            try:
                rows = _load_bulk_voter_rows(uploaded_file, ext)
            except Exception as e:
                errors.append(f'Error reading file: {str(e)}')
                rows = []
            if rows:
                valid_ranks = {r[0] for r in PoliceUser._meta.get_field('rank').choices}
                for i, row in enumerate(rows, start=1):
                    try:
                        row_data = {_normalize_bulk_key(k): _normalize_bulk_value(v) for k, v in row.items() if k}
                        force_number = row_data.get('force_number', '')
                        first_name = row_data.get('first_name', '')
                        last_name = row_data.get('last_name', '')
                        email = row_data.get('email', '')
                        rank = row_data.get('rank', '').upper()
                        station = row_data.get('station', '')
                        phone = row_data.get('phone', '')
                        is_active_voter_str = row_data.get('is_active_voter', 'true')
                        if not force_number:
                            errors.append(f'Row {i}: force_number is required')
                            continue
                        try:
                            force_number = int(force_number)
                        except ValueError:
                            errors.append(f'Row {i}: force_number must be an integer')
                            continue
                        if PoliceUser.objects.filter(force_number=force_number).exists():
                            errors.append(f'Row {i}: Force number {force_number} already exists')
                            continue
                        if not first_name or not last_name:
                            errors.append(f'Row {i}: first_name and last_name are required')
                            continue
                        if not email:
                            errors.append(f'Row {i}: email is required')
                            continue
                        if not rank:
                            errors.append(f'Row {i}: rank is required')
                            continue
                        if rank not in valid_ranks:
                            errors.append(f'Row {i}: Invalid rank "{rank}". Valid: {", ".join(sorted(valid_ranks))}')
                            continue
                        if not station:
                            errors.append(f'Row {i}: station is required')
                            continue
                        auto_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
                        username = str(force_number)
                        voter = PoliceUser.objects.create(
                            username=username, first_name=first_name, last_name=last_name,
                            email=email, force_number=force_number, rank=rank, station=station,
                            phone=phone, role='VOTER',
                            is_active_voter=str(is_active_voter_str).lower() in ('true', '1', 'yes', 'on'),
                            is_active=True, is_staff=False, must_change_password=True
                        )
                        voter.set_password(auto_password)
                        voter.save()
                        created_voters.append({
                            'row': i, 'username': username, 'force_number': force_number,
                            'full_name': voter.get_full_name(), 'email': email, 'password': auto_password
                        })
                    except Exception as e:
                        errors.append(f'Row {i}: {str(e)}')
                if created_voters:
                    create_audit_log(request.user, AuditLog.ACTION_VOTER_BULK_CREATE,
                        f'Bulk registered {len(created_voters)} voters', request)
                    if not errors:
                        messages.success(request, f'Successfully registered {len(created_voters)} voters!')
                elif not errors:
                    errors.append('No valid voter data found in the file.')
        else:
            errors.append('Invalid form submission.')
    else:
        form = BulkVoterUploadForm()
    return render(request, 'polls/bulk_register_voters.html', {
        'form': form, 'errors': errors, 'created_voters': created_voters
    })


@login_required
@user_passes_test(is_admin)
def audit_log(request):
    logs = AuditLog.objects.all().select_related('user').order_by('-timestamp')[:500]
    return render(request, 'polls/audit_log.html', {'logs': logs})


@login_required
@user_passes_test(is_admin)
def admin_election_voters(request, election_id):
    election = get_object_or_404(Election.objects.prefetch_related('positions'), pk=election_id)
    registered_voter_ids = set(ElectionRegistration.objects.filter(
        election=election
    ).values_list('voter_id', flat=True))
    
    registered_voters = PoliceUser.objects.filter(
        id__in=registered_voter_ids, role='VOTER'
    ).order_by('force_number')
    
    eligible_voters = []
    for voter in PoliceUser.objects.filter(role='VOTER', is_active=True).order_by('force_number'):
        if election.is_voter_eligible(voter) and voter.id not in registered_voter_ids:
            eligible_voters.append(voter)
    
    return render(request, 'polls/admin_election_voters.html', {
        'election': election,
        'registered_voters': registered_voters,
        'eligible_voters': eligible_voters,
        'registered_count': registered_voters.count(),
        'eligible_count': len(eligible_voters),
    })


@login_required
@user_passes_test(is_admin)
def admin_register_voter_to_election(request, election_id, voter_id):
    election = get_object_or_404(Election, pk=election_id)
    voter = get_object_or_404(PoliceUser, pk=voter_id, role='VOTER')
    
    if not election.is_voter_eligible(voter):
        messages.error(request, f'Voter {voter.get_full_name()} is not eligible for this election.')
        return redirect('polls:admin_election_voters', election_id=election_id)
    
    if ElectionRegistration.objects.filter(voter=voter, election=election).exists():
        messages.info(request, f'Voter {voter.get_full_name()} is already registered for this election.')
        return redirect('polls:admin_election_voters', election_id=election_id)
    
    ElectionRegistration.objects.create(voter=voter, election=election, registered_by=request.user)
    create_audit_log(
        request.user, AuditLog.ACTION_VOTER_UPDATE,
        f'Registered voter {voter.username} for election: {election.title}', request,
        target_model='Election', target_id=election.id
    )
    messages.success(request, f'Voter {voter.get_full_name()} registered for "{election.title}".')
    return redirect('polls:admin_election_voters', election_id=election_id)


@login_required
@user_passes_test(is_admin)
def admin_unregister_voter_from_election(request, election_id, voter_id):
    election = get_object_or_404(Election, pk=election_id)
    voter = get_object_or_404(PoliceUser, pk=voter_id, role='VOTER')
    
    registration = ElectionRegistration.objects.filter(voter=voter, election=election).first()
    if not registration:
        messages.error(request, f'Voter {voter.get_full_name()} is not registered for this election.')
        return redirect('polls:admin_election_voters', election_id=election_id)
    
    if Vote.objects.filter(voter=voter, election=election).exists():
        messages.error(request, f'Cannot unregister {voter.get_full_name()} — they have already voted in this election.')
        return redirect('polls:admin_election_voters', election_id=election_id)
    
    registration.delete()
    create_audit_log(
        request.user, AuditLog.ACTION_VOTER_UPDATE,
        f'Unregistered voter {voter.username} from election: {election.title}', request,
        target_model='Election', target_id=election.id
    )
    messages.success(request, f'Voter {voter.get_full_name()} unregistered from "{election.title}".')
    return redirect('polls:admin_election_voters', election_id=election_id)

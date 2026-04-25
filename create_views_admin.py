with open('polls/views_admin.py', 'w', encoding='utf-8') as f:
    f.write('''from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Count
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
import csv
import json
import io
import secrets
import string
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from .models import Position, Candidate, PoliceUser, Election, Vote, ElectionPosition, AuditLog
from .forms import PoliceUserRegistrationForm, PoliceUserEditForm, PositionForm, ElectionForm, CandidateForm, BulkVoterUploadForm


def is_admin(user):
    return user.role in ['SUPER_ADMIN', 'ADMIN']


def is_superadmin(user):
    return user.role == 'SUPER_ADMIN'


def create_audit_log(user, action, details, request=None, target_model='', target_id=None):
    ip_address = request.META.get('REMOTE_ADDR') if request else None
    AuditLog.objects.create(
        user=user,
        action=action,
        details=details,
        ip_address=ip_address,
        target_model=target_model,
        target_id=target_id
    )


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    now = timezone.now()
    stats = {
        'positions_count': Position.objects.count(),
        'elections_count': Election.objects.count(),
        'active_elections': Election.objects.filter(start_time__lte=now, end_time__gte=now).count(),
        'candidates_count': Candidate.objects.count(),
        'voters_count': PoliceUser.objects.filter(role='VOTER').count(),
        'is_admin': request.user.role == 'ADMIN',
        'is_superadmin': request.user.role == 'SUPER_ADMIN',
    }
    return render(request, 'polls/admin_dashboard.html', stats)


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
            create_audit_log(
                request.user, AuditLog.ACTION_POSITION_CREATE,
                f"Created position: {position.name}", request,
                target_model='Position', target_id=position.id
            )
            messages.success(request, 'Position created successfully!')
            return redirect('polls:admin_positions')
    else:
        form = PositionForm()
    return render(request, 'polls/admin_positions.html', {
        'positions': positions,
        'form': form,
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
            create_audit_log(
                request.user, AuditLog.ACTION_POSITION_UPDATE,
                f"Updated position: {position.name}", request,
                target_model='Position', target_id=position.id
            )
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
        create_audit_log(
            request.user, AuditLog.ACTION_POSITION_DELETE,
            f"Deleted position: {position.name}", request,
            target_model='Position', target_id=position.id
        )
        position.delete()
        messages.success(request, 'Position deleted successfully!')
    return redirect('polls:admin_positions')


@login_required
@user_passes_test(is_admin)
def admin_elections(request):
    elections = Election.objects.all().prefetch_related('positions').order_by('-start_time')
    now = timezone.now()
    positions = Position.objects.all()
    return render(request, 'polls/admin_elections.html', {
        'elections': elections,
        'now': now,
        'positions': positions,
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
            return render(request, 'polls/create_election.html', {
                'positions': positions,
                'selected_position_ids': selected_positions
            })
        
        if not start_time or not end_time:
            messages.error(request, 'Start time and end time are required.')
            return render(request, 'polls/create_election.html', {
                'positions': positions,
                'selected_position_ids': selected_positions
            })
        
        if not selected_positions:
            messages.error(request, 'At least one position must be selected.')
            return render(request, 'polls/create_election.html', {
                'positions': positions,
                'selected_position_ids': selected_positions
            })
        
        try:
            start_dt = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
            end_dt = datetime.strptime(end_time, '%Y-%m-%dT%H:%M')
            start_dt = timezone.make_aware(start_dt)
            end_dt = timezone.make_aware(end_dt)
        except ValueError as e:
            messages.error(request, f'Invalid date/time format. Please use the date/time picker. Error: {str(e)}')
            return render(request, 'polls/create_election.html', {
                'positions': positions,
                'selected_position_ids': selected_positions
            })
        
        if start_dt >= end_dt:
            messages.error(request, 'End time must be after start time.')
            return render(request, 'polls/create_election.html', {
                'positions': positions,
                'selected_position_ids': selected_positions
            })
        
        try:
            election = Election.objects.create(
                title=title,
                description=description,
                start_time=start_dt,
                end_time=end_dt,
                eligible_ranks=eligible_ranks,
                eligible_stations=eligible_stations,
                created_by=request.user
            )
            
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
                return render(request, 'polls/create_election.html', {
                    'positions': positions,
                    'selected_position_ids': selected_positions
                })
            
            create_audit_log(
                request.user, AuditLog.ACTION_ELECTION_CREATE,
                f"Created election: {election.title} (ID: {election.id}, positions: {positions_added})", request,
                target_model='Election', target_id=election.id
            )
            messages.success(request, f'Election "{title}" created successfully with {positions_added} position(s)!')
            return redirect('polls:admin_elections')
        except Exception as e:
            messages.error(request, f'Error creating election: {str(e)}')
            return render(request, 'polls/create_election.html', {
                'positions': positions,
                'selected_position_ids': selected_positions
            })
    
    return render(request, 'polls/create_election.html', {
        'positions': positions,
        'selected_position_ids': []
    })


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
                start_dt = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
                end_dt = datetime.strptime(end_time, '%Y-%m-%dT%H:%M')
                election.start_time = timezone.make_aware(start_dt)
                election.end_time = timezone.make_aware(end_dt)
            except ValueError as e:
                messages.error(request, f'Invalid date/time format: {str(e)}')
                return render(request, 'polls/create_election.html', {
                    'election': election,
                    'positions': positions,
                    'selected_position_ids': selected_position_ids
                })
        
        election.save()
        
        selected_positions = request.POST.getlist('positions')
        election.positions.clear()
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
def toggle_election_status(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    now_active = election.is_open()
    messages.info(request, f'Election status is automatically determined by start/end times. Currently: {"active" if now_active else "inactive"}.')
    return redirect('polls:admin_elections')


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


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def admin_register_voter(request):
    import secrets
    import string
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
            create_audit_log(
                request.user, AuditLog.ACTION_VOTER_CREATE,
                f"Registered voter: {voter.username} (Force #{voter.force_number})", request,
                target_model='PoliceUser', target_id=voter.id
            )
            request.session['registered_voter_credentials'] = {
                'username': voter.username,
                'password': auto_password,
                'force_number': voter.force_number,
                'full_name': voter.get_full_name()
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

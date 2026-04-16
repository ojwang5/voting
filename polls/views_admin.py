from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Count
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
import csv
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from .models import Position, Candidate, PoliceUser, Election, Vote, ElectionPosition
from .forms import PoliceUserRegistrationForm, PoliceUserEditForm, PositionForm, ElectionForm, CandidateForm

def is_admin(user):
    return user.role in ['SUPER_ADMIN', 'ADMIN']

def is_superadmin(user):
    return user.role == 'SUPER_ADMIN'

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
    }
    return render(request, 'polls/admin_dashboard.html', stats)

@login_required
@user_passes_test(is_superadmin)
def admin_positions(request):
    positions = Position.objects.all().order_by('name')
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Position created successfully!')
            return redirect('polls:admin_positions')
    else:
        form = PositionForm()
    return render(request, 'polls/admin_positions.html', {'positions': positions, 'form': form})

@login_required
@user_passes_test(is_superadmin)
def edit_position(request, position_id):
    position = get_object_or_404(Position, pk=position_id)
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            form.save()
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
        'positions': positions
    })

@login_required
@user_passes_test(is_admin)
def create_election(request):
    from .models import ElectionPosition
    positions = Position.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        eligible_ranks = request.POST.get('eligible_ranks', '')
        eligible_stations = request.POST.get('eligible_stations', '')
        selected_positions = request.POST.getlist('positions')
        
        if not title or not start_time or not end_time:
            messages.error(request, 'Title, start time, and end time are required.')
            return render(request, 'polls/create_election.html', {'positions': positions})
        
        from datetime import datetime
        start_dt = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
        end_dt = datetime.strptime(end_time, '%Y-%m-%dT%H:%M')
        
        if start_dt >= end_dt:
            messages.error(request, 'End time must be after start time.')
            return render(request, 'polls/create_election.html', {'positions': positions})
        
        election = Election.objects.create(
            title=title,
            description=description,
            start_time=start_dt,
            end_time=end_dt,
            eligible_ranks=eligible_ranks,
            eligible_stations=eligible_stations,
            created_by=request.user
        )
        
        for pos_id in selected_positions:
            try:
                pos = Position.objects.get(id=pos_id)
                ElectionPosition.objects.create(election=election, position=pos)
            except Position.DoesNotExist:
                pass
        
        messages.success(request, 'Election created successfully!')
        return redirect('polls:admin_elections')
    
    return render(request, 'polls/create_election.html', {'positions': positions})

@login_required
@user_passes_test(is_admin)
def edit_election(request, election_id):
    from .models import ElectionPosition
    election = get_object_or_404(Election, pk=election_id)
    positions = Position.objects.all()
    
    if request.method == 'POST':
        election.title = request.POST.get('title', election.title)
        election.description = request.POST.get('description', '')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        election.eligible_ranks = request.POST.get('eligible_ranks', '')
        election.eligible_stations = request.POST.get('eligible_stations', '')
        
        if start_time and end_time:
            from datetime import datetime
            election.start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
            election.end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M')
        
        election.save()
        
        selected_positions = request.POST.getlist('positions')
        election.positions.clear()
        for pos_id in selected_positions:
            try:
                pos = Position.objects.get(id=pos_id)
                ElectionPosition.objects.create(election=election, position=pos)
            except Position.DoesNotExist:
                pass
        
        messages.success(request, 'Election updated successfully!')
        return redirect('polls:admin_elections')
    
    return render(request, 'polls/create_election.html', {
        'election': election,
        'positions': positions
    })

@login_required
@user_passes_test(is_admin)
def toggle_election_status(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    election.is_active = not election.is_active
    election.save()
    status = 'activated' if election.is_active else 'deactivated'
    messages.success(request, f'Election {status} successfully!')
    return redirect('polls:admin_elections')

@login_required
@user_passes_test(is_admin)
def delete_election(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    if request.method == 'POST':
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
            voter.set_password(auto_password)
            voter.is_active = True
            voter.is_staff = form.cleaned_data['role'] in ['SUPER_ADMIN', 'ADMIN']
            voter.must_change_password = True
            voter.save()
            request.session['registered_voter_credentials'] = {
                'username': voter.username,
                'password': auto_password,
                'force_number': voter.force_number,
                'full_name': voter.get_full_name()
            }
            messages.success(request, f'Voter {voter.username} registered successfully!')
            return redirect('polls:admin_voter_credentials')
    else:
        form = PoliceUserRegistrationForm(initial={'role': 'VOTER'})
    return render(request, 'polls/register_voter.html', {'form': form, 'title': 'Register New Voter'})

@login_required
@user_passes_test(is_admin)
def admin_voter_credentials(request):
    credentials = request.session.pop('registered_voter_credentials', None)
    if not credentials:
        messages.error(request, 'No credentials to display.')
        return redirect('polls:admin_register_voter')
    return render(request, 'polls/voter_credentials.html', {'credentials': credentials})

@login_required
@user_passes_test(is_admin)
def admin_voters(request):
    voters = PoliceUser.objects.filter(role='VOTER').order_by('-date_joined')
    return render(request, 'polls/admin_voters.html', {'voters': voters})

@login_required
@user_passes_test(is_admin)
def admin_edit_voter(request, voter_id):
    voter = get_object_or_404(PoliceUser, pk=voter_id)
    if request.method == 'POST':
        form = PoliceUserEditForm(request.POST, instance=voter)
        if form.is_valid():
            form.save()
            messages.success(request, f'Voter {voter.username} updated successfully!')
            return redirect('polls:admin_voters')
    else:
        form = PoliceUserEditForm(instance=voter)
    return render(request, 'polls/edit_voter.html', {'form': form, 'voter': voter})

@login_required
@user_passes_test(is_admin)
def admin_delete_voter(request, voter_id):
    voter = get_object_or_404(PoliceUser, pk=voter_id)
    if request.method == 'POST':
        voter.delete()
        messages.success(request, 'Voter deleted successfully!')
    return redirect('polls:admin_voters')

@login_required
@user_passes_test(is_admin)
def admin_reset_voter_password(request, voter_id):
    import secrets
    import string
    voter = get_object_or_404(PoliceUser, pk=voter_id)
    if request.method == 'POST':
        new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
        voter.set_password(new_password)
        voter.must_change_password = True
        voter.save()
        request.session['reset_voter_credentials'] = {
            'username': voter.username,
            'password': new_password,
            'force_number': voter.force_number,
            'full_name': voter.get_full_name()
        }
        messages.success(request, f'Password reset for {voter.username}!')
        return redirect('polls:admin_voter_credentials')
    return redirect('polls:admin_voters')

@login_required
@user_passes_test(is_admin)
def admin_register_candidate(request):
    elections = Election.objects.all()
    positions = Position.objects.all()
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.created_by = request.user
            candidate.save()
            messages.success(request, f'Candidate {candidate.name} registered successfully!')
            return redirect('polls:admin_candidates')
    else:
        form = CandidateForm()
    return render(request, 'polls/register_candidate.html', {
        'form': form,
        'elections': elections,
        'positions': positions
    })

@login_required
@user_passes_test(is_admin)
def admin_edit_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, f'Candidate {candidate.name} updated successfully!')
            return redirect('polls:admin_candidates')
    else:
        form = CandidateForm(instance=candidate)
    return render(request, 'polls/edit_candidate.html', {
        'form': form,
        'candidate': candidate,
        'elections': Election.objects.all(),
        'positions': Position.objects.all()
    })

@login_required
@user_passes_test(is_admin)
def admin_delete_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, pk=candidate_id)
    if request.method == 'POST':
        candidate.delete()
        messages.success(request, 'Candidate deleted successfully!')
    return redirect('polls:admin_candidates')

@login_required
@user_passes_test(is_admin)
def admin_candidates(request):
    candidates = Candidate.objects.all().select_related('election', 'position').order_by('-id')
    return render(request, 'polls/admin_candidates.html', {'candidates': candidates})

def export_voters_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="voters.csv"'
    writer = csv.writer(response)
    writer.writerow(['Username', 'Force Number', 'Full Name', 'Rank', 'Station', 'Phone', 'Email', 'Role', 'Votes Cast', 'Registered Date', 'Status'])
    voters = PoliceUser.objects.filter(role='VOTER').select_related()
    for voter in voters:
        writer.writerow([
            voter.username, voter.force_number, voter.get_full_name(),
            voter.get_rank_display(), voter.station, voter.phone, voter.email,
            voter.get_role_display(), voter.votes.count(), voter.date_joined.strftime('%Y-%m-%d'),
            'Active' if voter.is_active else 'Inactive'
        ])
    return response

def export_voters_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="voters.pdf"'
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    title = Paragraph("Voter Registration Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 20))
    
    voters = PoliceUser.objects.filter(role='VOTER').select_related()
    data = [['#', 'Force #', 'Name', 'Rank', 'Station', 'Phone', 'Votes']]
    for i, voter in enumerate(voters, 1):
        data.append([
            str(i), str(voter.force_number), voter.get_full_name(),
            voter.get_rank_display(), voter.station, voter.phone or '-', str(voter.votes.count())
        ])
    
    table = Table(data, colWidths=[0.5*inch, 1*inch, 2*inch, 1.2*inch, 1.5*inch, 1.3*inch, 0.7*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    elements.append(table)
    doc.build(elements)
    return HttpResponse(buffer.getvalue(), content_type='application/pdf')

def export_voters_docx(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename="voters.docx"'
    doc = Document()
    doc.add_heading('Voter Registration Report', 0)
    doc.add_paragraph(f'Generated: {timezone.now().strftime("%Y-%m-%d %H:%M")}')
    
    voters = PoliceUser.objects.filter(role='VOTER').select_related()
    table = doc.add_table(rows=1, cols=7)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = '#'
    hdr_cells[1].text = 'Force #'
    hdr_cells[2].text = 'Name'
    hdr_cells[3].text = 'Rank'
    hdr_cells[4].text = 'Station'
    hdr_cells[5].text = 'Phone'
    hdr_cells[6].text = 'Votes'
    
    for i, voter in enumerate(voters, 1):
        row_cells = table.add_row().cells
        row_cells[0].text = str(i)
        row_cells[1].text = str(voter.force_number)
        row_cells[2].text = voter.get_full_name()
        row_cells[3].text = voter.get_rank_display()
        row_cells[4].text = voter.station
        row_cells[5].text = voter.phone or '-'
        row_cells[6].text = str(voter.votes.count())
    
    doc.save(response)
    return response

def export_candidates_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="candidates.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Force Number', 'Rank', 'Position', 'Election', 'Biography', 'Votes'])
    for candidate in Candidate.objects.all().select_related('election', 'position'):
        writer.writerow([
            candidate.name, candidate.force_number, candidate.get_rank_display(),
            candidate.position.name, candidate.election.title,
            candidate.biography[:100], candidate.vote_set.count()
        ])
    return response

def export_candidates_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="candidates.pdf"'
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph("Candidates Report", styles['Title']))
    elements.append(Spacer(1, 20))
    
    candidates = Candidate.objects.all().select_related('election', 'position')
    data = [['Name', 'Position', 'Election', 'Votes']]
    for c in candidates:
        data.append([c.name, c.position.name, c.election.title, str(c.vote_set.count())])
    
    table = Table(data, colWidths=[2*inch, 1.5*inch, 2*inch, 0.8*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    elements.append(table)
    doc.build(elements)
    return HttpResponse(buffer.getvalue(), content_type='application/pdf')

def export_candidates_docx(request):
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename="candidates.docx"'
    doc = Document()
    doc.add_heading('Candidates Report', 0)
    
    candidates = Candidate.objects.all().select_related('election', 'position')
    table = doc.add_table(rows=1, cols=4)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Name'
    hdr_cells[1].text = 'Position'
    hdr_cells[2].text = 'Election'
    hdr_cells[3].text = 'Votes'
    
    for c in candidates:
        row_cells = table.add_row().cells
        row_cells[0].text = c.name
        row_cells[1].text = c.position.name
        row_cells[2].text = c.election.title
        row_cells[3].text = str(c.vote_set.count())
    
    doc.save(response)
    return response

def export_results_csv(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="results_{election_id}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Candidate', 'Position', 'Rank', 'Force Number', 'Votes', 'Percentage'])
    total = election.vote_set.count()
    for candidate in election.candidates.all():
        votes = candidate.vote_set.count()
        pct = (votes / total * 100) if total > 0 else 0
        writer.writerow([
            candidate.name, candidate.position.name, candidate.get_rank_display(),
            candidate.force_number, votes, f"{pct:.1f}%"
        ])
    return response

def export_results_pdf(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="results_{election_id}.pdf"'
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Election Results: {election.title}", styles['Title']))
    elements.append(Paragraph(f"Date: {election.start_time.strftime('%Y-%m-%d')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    total = election.vote_set.count()
    data = [['Candidate', 'Position', 'Votes', '%']]
    for candidate in election.candidates.all():
        votes = candidate.vote_set.count()
        pct = (votes / total * 100) if total > 0 else 0
        data.append([candidate.name, candidate.position.name, str(votes), f"{pct:.1f}%"])
    
    table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1*inch, 0.8*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)
    return HttpResponse(buffer.getvalue(), content_type='application/pdf')

def export_results_docx(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename="results_{election_id}.docx"'
    doc = Document()
    doc.add_heading(f"Election Results: {election.title}", 0)
    doc.add_paragraph(f"Date: {election.start_time.strftime('%Y-%m-%d')}")
    
    total = election.vote_set.count()
    table = doc.add_table(rows=1, cols=4)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Candidate'
    hdr_cells[1].text = 'Position'
    hdr_cells[2].text = 'Votes'
    hdr_cells[3].text = '%'
    
    for candidate in election.candidates.all():
        votes = candidate.vote_set.count()
        pct = (votes / total * 100) if total > 0 else 0
        row_cells = table.add_row().cells
        row_cells[0].text = candidate.name
        row_cells[1].text = candidate.position.name
        row_cells[2].text = str(votes)
        row_cells[3].text = f"{pct:.1f}%"
    
    doc.save(response)
    return response

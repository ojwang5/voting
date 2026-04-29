from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.db.models import Count
from .models import Election, Candidate, Vote, PoliceUser, AuditLog, ElectionRegistration
from .forms import PasswordResetForm, SetNewPasswordForm, ChangePasswordForm
from .forms import PhoneLoginForm
from .views_admin import is_admin, is_superadmin, create_audit_log


def home(request):
    """Landing page with featured elections."""
    now = timezone.now()
    latest_elections = Election.objects.filter(
        end_time__gte=now
    ).order_by('-start_time')[:6]
    return render(request, 'polls/index.html', {'latest_elections': latest_elections})


def _partition_elections_for_user(user):
    now = timezone.now()
    eligible_ids = [
        election.id
        for election in Election.objects.all().prefetch_related('positions')
        if election.is_voter_eligible(user)
    ]
    eligible_elections = Election.objects.filter(id__in=eligible_ids).prefetch_related('positions')
    
    registered_ids = set(ElectionRegistration.objects.filter(
        voter=user, election_id__in=eligible_ids
    ).values_list('election_id', flat=True))
    
    registered_elections = eligible_elections.filter(id__in=registered_ids)
    active_elections = registered_elections.filter(start_time__lte=now, end_time__gte=now).order_by('-start_time')
    upcoming_registered = registered_elections.filter(start_time__gt=now).order_by('start_time')
    ended_elections = registered_elections.filter(end_time__lt=now).order_by('-end_time')
    
    unregistered_ids = [eid for eid in eligible_ids if eid not in registered_ids]
    upcoming_unregistered = Election.objects.filter(
        id__in=unregistered_ids, start_time__gt=now
    ).prefetch_related('positions').order_by('start_time')
    
    return active_elections, upcoming_registered, upcoming_unregistered, ended_elections


def user_login(request):
    if request.user.is_authenticated:
        return redirect('polls:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'registration/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                create_audit_log(
                    user, AuditLog.ACTION_LOGIN,
                    f"User logged in via username/password", request
                )
                if user.must_change_password:
                    messages.warning(request, 'You must change your password before continuing.')
                    return redirect('polls:change_password')
                next_url = request.GET.get('next', 'polls:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Your account is inactive. Contact administrator.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'registration/login.html')


def phone_login_request(request):
    """Step 1: Voter submits phone number. If valid, proceed to set password."""
    if request.method == 'POST':
        form = PhoneLoginForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            user = PoliceUser.objects.get(phone=phone)
            request.session['phone_login_user_id'] = user.id
            return redirect('polls:phone_set_password')
    else:
        form = PhoneLoginForm()
    return render(request, 'registration/phone_login.html', {'form': form})


def phone_set_password(request):
    """Step 2: Voter sets a new password and is logged in."""
    user_id = request.session.get('phone_login_user_id')
    if not user_id:
        messages.error(request, 'Session expired or invalid. Please enter your phone again.')
        return redirect('polls:phone_login')
    user = get_object_or_404(PoliceUser, pk=user_id)

    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.must_change_password = False
            user.save()
            # Authenticate and login
            auth_user = authenticate(request, username=user.username, password=new_password)
            if auth_user:
                login(request, auth_user)
                create_audit_log(
                    auth_user, AuditLog.ACTION_LOGIN,
                    "User logged in via phone login", request
                )
                # cleanup session
                try:
                    del request.session['phone_login_user_id']
                except KeyError:
                    pass
                messages.success(request, 'Password set and logged in successfully.')
                return redirect('polls:dashboard')
            else:
                messages.error(request, 'Unable to log you in after password set. Please try logging in.')
                return redirect('polls:login')
    else:
        form = SetNewPasswordForm()
    return render(request, 'registration/phone_set_password.html', {'form': form, 'phone': user.phone})

def user_logout(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('polls:login')

@require_http_methods(["GET", "POST"])
def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            import secrets
            otp = ''.join(secrets.choice('0123456789') for _ in range(6))
            user.otp_code = otp
            user.otp_expiry = timezone.now() + timezone.timedelta(minutes=10)
            user.save()
            request.session['password_reset_user_id'] = user.id
            messages.success(request, f'OTP sent to registered phone. (Demo OTP: {otp})')
            return redirect('polls:password_reset_otp')
    else:
        form = PasswordResetForm()
    return render(request, 'registration/password_reset_request.html', {'form': form})

@require_http_methods(["GET", "POST"])
def password_reset_otp(request):
    user_id = request.session.get('password_reset_user_id')
    if not user_id:
        messages.error(request, 'Session expired. Please try again.')
        return redirect('polls:password_reset_request')
    
    user = get_object_or_404(PoliceUser, pk=user_id)
    
    if request.method == 'POST':
        otp = request.POST.get('otp')
        if otp == user.otp_code and user.is_otp_valid():
            return redirect('polls:password_reset_confirm')
        else:
            messages.error(request, 'Invalid or expired OTP.')
    
    return render(request, 'registration/password_reset_otp.html', {'force_number': user.force_number})

@require_http_methods(["GET", "POST"])
def password_reset_confirm(request):
    user_id = request.session.get('password_reset_user_id')
    if not user_id:
        messages.error(request, 'Session expired. Please try again.')
        return redirect('polls:password_reset_request')
    
    user = get_object_or_404(PoliceUser, pk=user_id)
    
    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password'])
            user.must_change_password = False
            user.otp_code = ''
            user.save()
            del request.session['password_reset_user_id']
            messages.success(request, 'Password reset successfully. Please login.')
            return redirect('polls:login')
    else:
        form = SetNewPasswordForm()
    return render(request, 'registration/password_reset_confirm.html', {'form': form})

@login_required
@require_http_methods(["GET", "POST"])
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.must_change_password = False
            request.user.save()
            create_audit_log(
                request.user, AuditLog.ACTION_PASSWORD_CHANGE,
                "Password changed successfully", request
            )
            from django.contrib.auth import get_backends
            backend = get_backends()[0]
            request.user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
            login(request, request.user)
            messages.success(request, 'Password changed successfully!')
            return redirect('polls:dashboard')
    else:
        form = ChangePasswordForm(user=request.user)
    return render(request, 'registration/change_password.html', {'form': form})

@login_required
def register_for_election(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    
    if request.user.role != 'VOTER' or not request.user.is_active_voter:
        messages.error(request, 'Only active voters can register for elections.')
        return redirect('polls:dashboard')
    
    if not election.is_voter_eligible(request.user):
        messages.error(request, 'You are not eligible for this election.')
        return redirect('polls:dashboard')
    
    if ElectionRegistration.objects.filter(voter=request.user, election=election).exists():
        messages.info(request, 'You are already registered for this election.')
        return redirect('polls:dashboard')
    
    if election.end_time < timezone.now():
        messages.error(request, 'This election has already ended.')
        return redirect('polls:dashboard')
    
    ElectionRegistration.objects.create(voter=request.user, election=election, registered_by=request.user)
    create_audit_log(
        request.user, AuditLog.ACTION_VOTER_UPDATE,
        f"Registered for election: {election.title}", request,
        target_model='Election', target_id=election.id
    )
    messages.success(request, f'You have successfully registered for "{election.title}".')
    return redirect('polls:dashboard')


@login_required
def detail(request, election_id):
    election = get_object_or_404(Election.objects.prefetch_related('positions'), pk=election_id)
    candidates = election.candidates.annotate(vote_count=Count('vote'))
    is_registered = ElectionRegistration.objects.filter(voter=request.user, election=election).exists()
    is_eligible = election.is_voter_eligible(request.user)

    # Group candidates by position
    positions_with_candidates = {}
    for candidate in candidates:
        pos = candidate.position
        if pos not in positions_with_candidates:
            positions_with_candidates[pos] = []
        positions_with_candidates[pos].append(candidate)

    user_votes = Vote.objects.filter(voter=request.user, election=election).select_related('position', 'candidate')
    voted_position_ids = set(vote.position_id for vote in user_votes)
    has_voted = len(voted_position_ids) > 0

    context = {
        'election': election,
        'positions_with_candidates': positions_with_candidates,
        'user_votes': user_votes,
        'voted_position_ids': voted_position_ids,
        'has_voted': has_voted,
        'is_registered': is_registered,
        'is_eligible': is_eligible,
        'now': timezone.now(),
    }
    return render(request, 'polls/detail.html', context)

@login_required
def dashboard(request):
    active_elections, upcoming_registered, upcoming_unregistered, ended_elections = _partition_elections_for_user(request.user)

    voted_elections = Vote.objects.filter(voter=request.user).values_list('election_id', flat=True)
    user_votes = Vote.objects.filter(voter=request.user).select_related('election', 'candidate')

    total_votes_cast = user_votes.count()
    
    registered_election_ids = set(ElectionRegistration.objects.filter(
        voter=request.user
    ).values_list('election_id', flat=True))

    # Determine fully voted elections (user voted for ALL positions in the election)
    votes_by_election = {}
    for vote in user_votes:
        votes_by_election.setdefault(vote.election_id, set()).add(vote.position_id)

    fully_voted_elections = set()
    for election in active_elections:
        election_position_ids = set(pos.id for pos in election.positions.all())
        if election_position_ids:
            voted_position_ids = votes_by_election.get(election.id, set())
            if voted_position_ids == election_position_ids:
                fully_voted_elections.add(election.id)

    context = {
        'active_elections': active_elections,
        'upcoming_registered': upcoming_registered,
        'upcoming_unregistered': upcoming_unregistered,
        'ended_elections': ended_elections,
        'voted_elections': voted_elections,
        'fully_voted_elections': fully_voted_elections,
        'user_votes': user_votes,
        'total_votes_cast': total_votes_cast,
        'registered_election_ids': registered_election_ids,
        'is_admin': is_admin(request.user),
        'is_superadmin': is_superadmin(request.user),
        'can_vote': request.user.role == 'VOTER' and request.user.is_active_voter,
        'user_profile': request.user
    }
    return render(request, 'polls/dashboard.html', context)

@login_required
def vote(request, election_id):
    election = get_object_or_404(Election.objects.prefetch_related('positions'), pk=election_id)
    now = timezone.now()

    if request.user.role != 'VOTER' or not request.user.is_active_voter:
        messages.error(request, 'Only registered voters can cast votes.')
        return redirect('polls:dashboard')

    if not election.is_voter_eligible(request.user):
        messages.error(request, 'You are not eligible for this election.')
        return redirect('polls:dashboard')

    if not ElectionRegistration.objects.filter(voter=request.user, election=election).exists():
        messages.error(request, 'You must register for this election before voting.')
        return redirect('polls:detail', election.id)

    if election.start_time > now:
        messages.warning(request, 'Voting has not started yet.')
        return redirect('polls:dashboard')

    if election.end_time < now:
        messages.warning(request, 'Voting period has ended.')
        return redirect('polls:results', election.id)

    all_candidates = election.candidates.select_related('position').all()
    if not all_candidates.exists():
        messages.error(request, 'No candidates available for this election.')
        return redirect('polls:dashboard')

    # Determine which positions the voter has already voted for
    existing_votes = Vote.objects.filter(voter=request.user, election=election).select_related('position')
    voted_position_ids = set(vote.position_id for vote in existing_votes)
    election_position_ids = set(pos.id for pos in election.positions.all())

    # If voter has voted for all positions, show results
    if voted_position_ids == election_position_ids:
        messages.info(request, 'You have completed voting for all positions in this election.')
        return redirect('polls:results', election.id)

    # Group candidates by position
    positions_with_candidates = {}
    for candidate in all_candidates:
        pos = candidate.position
        if pos not in positions_with_candidates:
            positions_with_candidates[pos] = []
        positions_with_candidates[pos].append(candidate)

    if request.method == 'POST':
        votes_cast = 0
        errors = []
        for position in election.positions.all():
            # Skip positions already voted for
            if position.id in voted_position_ids:
                continue
            field_name = f'candidate_{position.id}'
            candidate_id = request.POST.get(field_name)
            if candidate_id:
                try:
                    candidate = get_object_or_404(Candidate, pk=candidate_id, election=election, position=position)
                    Vote.objects.create(
                        voter=request.user,
                        election=election,
                        candidate=candidate,
                        position=position,
                        ip_address=request.META.get('REMOTE_ADDR')
                    )
                    create_audit_log(
                        request.user, AuditLog.ACTION_VOTE,
                        f"Voted for {candidate.name} ({position.name}) in {election.title}", request,
                        target_model='Election', target_id=election.id
                    )
                    votes_cast += 1
                except Exception:
                    errors.append(f"An error occurred for position {position.name}. Please try again.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('polls:vote', election.id)

        if votes_cast > 0:
            messages.success(request, f'Your vote(s) for {votes_cast} position(s) have been recorded successfully!')
        else:
            messages.warning(request, 'No votes were submitted. Please select a candidate for at least one position.')
        return redirect('polls:vote', election.id)

    context = {
        'election': election,
        'positions_with_candidates': positions_with_candidates,
        'voted_position_ids': voted_position_ids,
        'existing_votes': existing_votes,
        'all_positions_voted': voted_position_ids == election_position_ids,
    }
    return render(request, 'polls/vote.html', context)

@login_required
def results(request, election_id):
    election = get_object_or_404(Election.objects.prefetch_related('positions'), pk=election_id)
    candidates = election.candidates.select_related('position').annotate(vote_count=Count('vote'))

    # Group results by position
    results_by_position = {}
    position_totals = {}
    for candidate in candidates:
        pos = candidate.position
        if pos not in results_by_position:
            results_by_position[pos] = []
            position_totals[pos] = 0
        results_by_position[pos].append({
            'candidate': candidate,
            'votes': candidate.vote_count,
        })
        position_totals[pos] += candidate.vote_count

    # Calculate percentages per position and sort
    for pos, results_list in results_by_position.items():
        total = position_totals[pos]
        for item in results_list:
            item['percentage'] = round((item['votes'] / total * 100), 1) if total > 0 else 0.0
        results_list.sort(key=lambda x: x['votes'], reverse=True)

    # Sort positions by ID for consistent ordering
    sorted_positions = sorted(results_by_position.keys(), key=lambda p: p.id)
    results_by_position_ordered = {pos: results_by_position[pos] for pos in sorted_positions}

    total_votes = sum(position_totals.values())

    user_votes = Vote.objects.filter(voter=request.user, election=election).select_related('position', 'candidate')
    has_voted = user_votes.exists()
    voted_position_ids = set(vote.position_id for vote in user_votes)
    election_position_ids = set(pos.id for pos in election.positions.all())
    all_positions_voted = voted_position_ids == election_position_ids

    context = {
        'election': election,
        'results_by_position': results_by_position_ordered,
        'position_totals': position_totals,
        'total_votes': total_votes,
        'has_voted': has_voted,
        'user_votes': user_votes,
        'all_positions_voted': all_positions_voted,
    }
    return render(request, 'polls/results.html', context)

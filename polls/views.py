from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q
from .models import Election, Candidate, Vote, PoliceUser
from .forms import PasswordResetForm, SetNewPasswordForm, ChangePasswordForm
from .views_admin import is_admin, is_superadmin

def user_login(request):
    if request.user.is_authenticated:
        return redirect('polls:index')
    
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
                if user.must_change_password:
                    messages.warning(request, 'You must change your password before continuing.')
                    return redirect('polls:change_password')
                next_url = request.GET.get('next', 'polls:index')
                return redirect(next_url)
            else:
                messages.error(request, 'Your account is inactive. Contact administrator.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'registration/login.html')

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
            login(request, request.user)
            messages.success(request, 'Password changed successfully!')
            return redirect('polls:index')
    else:
        form = ChangePasswordForm()
    return render(request, 'registration/change_password.html', {'form': form})

@login_required
def dashboard(request):
    now = timezone.now()
    all_elections = Election.objects.filter(
        Q(eligible_ranks__isnull=True) | Q(eligible_ranks__icontains=request.user.rank)
    ).filter(
        Q(eligible_stations__isnull=True) | Q(eligible_stations__icontains=request.user.station)
    ).prefetch_related('positions')
    
    active_elections = all_elections.filter(start_time__lte=now, end_time__gte=now)
    upcoming_elections = all_elections.filter(start_time__gt=now)
    ended_elections = all_elections.filter(end_time__lt=now)
    
    voted_elections = Vote.objects.filter(voter=request.user).values_list('election_id', flat=True)
    user_votes = Vote.objects.filter(voter=request.user).select_related('election', 'candidate')
    
    total_votes_cast = user_votes.count()
    
    context = {
        'active_elections': active_elections,
        'upcoming_elections': upcoming_elections,
        'ended_elections': ended_elections,
        'voted_elections': voted_elections,
        'user_votes': user_votes,
        'total_votes_cast': total_votes_cast,
        'is_admin': is_admin(request.user),
        'is_superadmin': is_superadmin(request.user),
        'user_profile': request.user
    }
    return render(request, 'polls/dashboard.html', context)

@login_required
def vote(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    now = timezone.now()
    
    if not election.is_voter_eligible(request.user):
        messages.error(request, 'You are not eligible for this election.')
        return redirect('polls:index')
    
    if Vote.objects.filter(voter=request.user, election=election).exists():
        messages.warning(request, 'You have already voted in this election.')
        return redirect('polls:results', election.id)
    
    if election.start_time > now:
        messages.warning(request, 'Voting has not started yet.')
        return redirect('polls:index')
    
    if election.end_time < now:
        messages.warning(request, 'Voting period has ended.')
        return redirect('polls:results', election.id)

    candidates = election.candidates.all()
    if not candidates.exists():
        messages.error(request, 'No candidates available for this election.')
        return redirect('polls:index')

    if request.method == 'POST':
        candidate_id = request.POST.get('candidate')
        if candidate_id:
            try:
                candidate = get_object_or_404(Candidate, pk=candidate_id, election=election)
                Vote.objects.create(
                    voter=request.user,
                    election=election,
                    candidate=candidate,
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                messages.success(request, 'Your vote has been recorded successfully!')
                return redirect('polls:results', election.id)
            except Exception:
                messages.error(request, 'An error occurred. Please try again.')
                return redirect('polls:vote', election.id)

    context = {
        'election': election,
        'candidates': candidates,
        'has_voted': Vote.objects.filter(voter=request.user, election=election).exists()
    }
    return render(request, 'polls/vote.html', context)

@login_required
def results(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    candidates = election.candidates.annotate(vote_count=Count('vote'))
    total_votes = sum(c.vote_count for c in candidates)
    
    results_data = []
    for candidate in candidates:
        percentage = (candidate.vote_count / total_votes * 100) if total_votes > 0 else 0
        results_data.append({
            'candidate': candidate,
            'votes': candidate.vote_count,
            'percentage': round(percentage, 1)
        })
    
    results_data.sort(key=lambda x: x['votes'], reverse=True)
    
    user_vote = Vote.objects.filter(voter=request.user, election=election).first()
    has_voted = user_vote is not None
    
    context = {
        'election': election,
        'results': results_data,
        'total_votes': total_votes,
        'has_voted': has_voted,
        'user_vote': user_vote
    }
    return render(request, 'polls/results.html', context)

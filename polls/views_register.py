from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.conf import settings

def register(request):
    if request.user.is_authenticated:
        return redirect('polls:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        force_number = request.POST.get('force_number')
        rank = request.POST.get('rank')
        station = request.POST.get('station')
        
        if not all([username, email, password, force_number, rank, station]):
            messages.error(request, 'All fields are required.')
            return render(request, 'registration/register.html')
        
        from .models import PoliceUser
        from .forms import PoliceUserRegistrationForm
        
        data = request.POST.copy()
        form = PoliceUserRegistrationForm(data)
        
        if form.is_valid():
            user = form.save(commit=False)
            user.username = str(force_number)
            user.set_password(password)
            user.must_change_password = False
            user.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to VotingHub.')
            return redirect('polls:dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    
    return render(request, 'registration/register.html')

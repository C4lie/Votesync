
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from .models import Election, UserProfile
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
import uuid
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from .forms import ElectionForm, CandidateForm
from .decorators import role_required
from django.contrib.auth.decorators import login_required

# Election Create + List
@login_required
@role_required('admin')
def election_list(request):
    elections = Election.objects.all().order_by('-start_time')
    return render(request, 'elections/election_list.html', {'elections': elections})

@login_required
@role_required('admin')
def create_election(request):
    if request.method == 'POST':
        form = ElectionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Election created successfully!")
            return redirect('election_list')
    else:
        form = ElectionForm()
    return render(request, 'elections/create_election.html', {'form': form})

# Candidate Create
@login_required
@role_required('admin')
def create_candidate(request):
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Candidate added!")
            return redirect('election_list')
    else:
        form = CandidateForm()
    return render(request, 'elections/create_candidate.html', {'form': form})


@login_required
@role_required('admin')
def admin_dashboard(request):
    return render(request, 'dashboards/admin.html')

@login_required
@role_required('voter')
def voter_dashboard(request):
    return render(request, 'dashboards/voter.html')

@login_required
@role_required('auditor')
def auditor_dashboard(request):
    return render(request, 'dashboards/auditor.html')


# Temporary store for verification (in real use: token model or UUID field in UserProfile)
user_verification_tokens = {}


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = True  # ✅ Activate immediately
            user.save()

            # Assign role to UserProfile
            role = form.cleaned_data['role']
            user_profile = UserProfile.objects.get(user=user)
            user_profile.role = role
            user_profile.is_verified = True  # ✅ Mark as verified directly
            user_profile.save()

            messages.success(request, "Registration successful. You can now login.")
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

def home(request):
    return render(request, 'home.html')


def verify_email(request, token):
    username = user_verification_tokens.get(token)
    if not username:
        return render(request, 'verification_failed.html')

    try:
        user = User.objects.get(username=username)
        user.is_active = True
        user.save()
        user.userprofile.is_verified = True
        user.userprofile.save()
        del user_verification_tokens[token]
        return render(request, 'verification_success.html')
    except User.DoesNotExist:
        return render(request, 'verification_failed.html')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.userprofile.is_verified:
                messages.error(request, "Please verify your email before login.")
                return redirect('login')

            login(request, user)
            return redirect('home')
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            role = user.userprofile.role

            if role == 'admin':
                return redirect('admin_dashboard')
            elif role == 'voter':
                return redirect('voter_dashboard')
            elif role == 'auditor':
                return redirect('auditor_dashboard')
            else:
                return redirect('home')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')





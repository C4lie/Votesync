from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError
from django.utils import timezone
from .models import UserProfile, Election, Candidate, Vote
from .forms import RegisterForm, LoginForm, ElectionForm, CandidateForm, VoteForm
from .decorators import role_required

user_verification_tokens = {}

def home(request):
    return render(request, 'home.html')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = True
            user.save()
            role = form.cleaned_data['role']
            user_profile = UserProfile.objects.get(user=user)
            user_profile.role = role
            user_profile.is_verified = True
            user_profile.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
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



@login_required
@role_required('admin')
def admin_dashboard(request):
    latest_election = Election.objects.order_by('-start_time').first()
    return render(request, 'dashboards/admin.html', {
        'latest_election': latest_election
    })

@login_required
@role_required('voter')
def voter_dashboard(request):
    # TEMPORARY: fetch all elections to check if they show up
    elections = Election.objects.all()

    voted_ids = Vote.objects.filter(voter=request.user).values_list('election_id', flat=True)

    return render(request, 'voter/dashboard.html', {
        'elections': elections,
        'voted_ids': voted_ids,
    })

@login_required
@role_required('auditor')
def auditor_dashboard(request):
    return render(request, 'dashboards/auditor.html')

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

@login_required
@role_required('admin')
def create_candidate(request):
    if request.method == 'POST':
        form = CandidateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Candidate added!")
            return redirect('election_list')
    else:
        form = CandidateForm()
    return render(request, 'elections/create_candidate.html', {'form': form})

@login_required
@role_required('voter')
def vote_view(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    candidates = election.candidates.all()

    if Vote.objects.filter(voter=request.user, election=election).exists():
        messages.warning(request, "You have already voted.")
        return redirect('voter_dashboard')

    if request.method == 'POST':
        candidate_id = request.POST.get('candidate')
        candidate = get_object_or_404(Candidate, id=candidate_id)
        Vote.objects.create(voter=request.user, candidate=candidate, election=election)
        messages.success(request, "Your vote has been submitted!")
        return redirect('voter_dashboard')

    # ⛔️ BAD if you don't have templates/voter/vote.html
    # return render(request, 'voter/vote.html', {'election': election, 'candidates': candidates})

    # ✅ GOOD if your vote.html is inside just /templates/
    return render(request, 'voter/voter.html', {'election': election, 'candidates': candidates})


from django.db.models import Count

@login_required
@role_required('admin')
def election_results(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    candidates = Candidate.objects.filter(election=election).annotate(vote_count=Count('vote'))

    labels = [c.name for c in candidates]
    data = [c.vote_count for c in candidates]
    total_votes = sum(data)

    return render(request, 'admin/results.html', {
        'election': election,
        'candidates': candidates,
        'total_votes': total_votes,
        'labels': labels,
        'data': data
    })

from django.views.decorators.cache import never_cache

@never_cache
def auditor_dashboard(request):
    elections = Election.objects.all()
    return render(request, 'auditor/dashboard.html', {'elections': elections})

@never_cache
def auditor_results(request, election_id):
    election = get_object_or_404(Election, id=election_id)
    candidates = Candidate.objects.filter(election=election).annotate(vote_count=Count('vote'))
    total_votes = sum(c.vote_count for c in candidates)

    return render(request, 'auditor/results.html', {
        'election': election,
        'candidates': candidates,
        'total_votes': total_votes
    })






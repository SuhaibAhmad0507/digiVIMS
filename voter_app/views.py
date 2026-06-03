# voter_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from functools import wraps

from .models import Voters, Families, PollingStations, Users, AuditLogs
from .forms  import LoginForm, VoterForm, FamilyForm, PollingStationForm, UserForm


# ─────────────────────────────────────────────
# AUTH HELPERS
# ─────────────────────────────────────────────

def login_required_custom(view_func):
    """Redirect to login if no session exists."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Only Admins can access this view."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')
        if request.session.get('role') != 'Administrator':
            messages.error(request, "Admin access required.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def log_action(user_id, action, table, target_id):
    """Write one row to auditlogs."""
    try:
        AuditLogs.objects.create(
            user_id=user_id,
            action=action,
            target_table=table,
            target_id=target_id,
        )
    except Exception:
        pass  # Never crash the main flow for a log failure


# ─────────────────────────────────────────────
# AUTH VIEWS
# ─────────────────────────────────────────────

def login_view(request):
    if request.session.get('user_id'):
        return redirect('dashboard')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        try:
            user = Users.objects.get(username=username)
            if check_password(password, user.password_hash):
                request.session['user_id']  = user.user_id
                request.session['username'] = user.username
                request.session['role']     = user.role
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        except Users.DoesNotExist:
            messages.error(request, "Invalid username or password.")

    return render(request, 'voter_app/login.html', {'form': form})


def logout_view(request):
    request.session.flush()
    return redirect('login')


# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────

@login_required_custom
def dashboard(request):
    total_voters   = Voters.objects.count()
    total_families = Families.objects.count()
    total_stations = PollingStations.objects.count()

    male_count   = Voters.objects.filter(gender='Male').count()
    female_count = Voters.objects.filter(gender='Female').count()

    # Top 5 stations by registered voter count
    top_stations = (
        PollingStations.objects
        .annotate(voter_count=Count('voters'))
        .order_by('-voter_count')[:5]
    )

    # 10 most recent audit log entries
    recent_logs = AuditLogs.objects.select_related('user').order_by('-timestamp')[:10]

    context = {
        'total_voters':   total_voters,
        'total_families': total_families,
        'total_stations': total_stations,
        'male_count':     male_count,
        'female_count':   female_count,
        'top_stations':   top_stations,
        'recent_logs':    recent_logs,
    }
    return render(request, 'voter_app/dashboard.html', context)


# ─────────────────────────────────────────────
# VOTER VIEWS
# ─────────────────────────────────────────────

@login_required_custom
def voter_list(request):
    query      = request.GET.get('q', '').strip()
    gender_f   = request.GET.get('gender', '')
    station_f  = request.GET.get('station', '')

    voters = Voters.objects.select_related('family', 'station').all()

    if query:
        voters = voters.filter(
            Q(cnic__icontains=query) |
            Q(full_name__icontains=query) |
            Q(family__family_id__iexact=query)
        )
    if gender_f:
        voters = voters.filter(gender=gender_f)
    if station_f:
        voters = voters.filter(station__station_id=station_f)

    paginator = Paginator(voters, 25)
    page      = paginator.get_page(request.GET.get('page'))
    stations  = PollingStations.objects.all()

    return render(request, 'voter_app/voter_list.html', {
        'page':       page,
        'query':      query,
        'gender_f':   gender_f,
        'station_f':  station_f,
        'stations':   stations,
        'total':      voters.count(),
    })


@login_required_custom
def voter_detail(request, pk):
    voter = get_object_or_404(
        Voters.objects.select_related('family', 'station'), pk=pk
    )
    # Siblings: other voters in the same family
    siblings = Voters.objects.filter(family=voter.family).exclude(pk=pk)[:10]
    return render(request, 'voter_app/voter_detail.html', {
        'voter':    voter,
        'siblings': siblings,
    })


@admin_required
def voter_create(request):
    form = VoterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        voter = form.save()
        log_action(request.session['user_id'], 'INSERT', 'voters', voter.voter_id)
        messages.success(request, f"Voter '{voter.full_name}' added successfully.")
        return redirect('voter_detail', pk=voter.pk)
    return render(request, 'voter_app/voter_form.html', {'form': form, 'action': 'Add'})


@admin_required
def voter_update(request, pk):
    voter = get_object_or_404(Voters, pk=pk)
    form  = VoterForm(request.POST or None, instance=voter)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_action(request.session['user_id'], 'UPDATE', 'voters', pk)
        messages.success(request, "Voter record updated.")
        return redirect('voter_detail', pk=pk)
    return render(request, 'voter_app/voter_form.html', {'form': form, 'action': 'Edit', 'voter': voter})


@admin_required
def voter_delete(request, pk):
    voter = get_object_or_404(Voters, pk=pk)
    if request.method == 'POST':
        name = voter.full_name
        voter.delete()
        log_action(request.session['user_id'], 'DELETE', 'voters', pk)
        messages.success(request, f"Voter '{name}' deleted.")
        return redirect('voter_list')
    return render(request, 'voter_app/confirm_delete.html', {
        'object': voter, 'object_type': 'Voter', 'cancel_url': 'voter_list'
    })


# ─────────────────────────────────────────────
# FAMILY VIEWS
# ─────────────────────────────────────────────

@login_required_custom
def family_list(request):
    query    = request.GET.get('q', '').strip()
    families = Families.objects.annotate(member_count=Count('voters')).all()
    if query:
        families = families.filter(
            Q(head_name__icontains=query) |
            Q(permanent_address__icontains=query)
        )
    paginator = Paginator(families, 20)
    page      = paginator.get_page(request.GET.get('page'))
    return render(request, 'voter_app/family_list.html', {'page': page, 'query': query})


@login_required_custom
def family_detail(request, pk):
    family  = get_object_or_404(Families, pk=pk)
    members = Voters.objects.filter(family=family).select_related('station')
    return render(request, 'voter_app/family_detail.html', {
        'family': family, 'members': members
    })


@admin_required
def family_create(request):
    form = FamilyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        family = form.save()
        log_action(request.session['user_id'], 'INSERT', 'families', family.family_id)
        messages.success(request, "Family created.")
        return redirect('family_detail', pk=family.pk)
    return render(request, 'voter_app/family_form.html', {'form': form, 'action': 'Add'})


@admin_required
def family_update(request, pk):
    family = get_object_or_404(Families, pk=pk)
    form   = FamilyForm(request.POST or None, instance=family)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_action(request.session['user_id'], 'UPDATE', 'families', pk)
        messages.success(request, "Family updated.")
        return redirect('family_detail', pk=pk)
    return render(request, 'voter_app/family_form.html', {'form': form, 'action': 'Edit'})


@admin_required
def family_delete(request, pk):
    family = get_object_or_404(Families, pk=pk)
    if request.method == 'POST':
        family.delete()
        log_action(request.session['user_id'], 'DELETE', 'families', pk)
        messages.success(request, "Family deleted.")
        return redirect('family_list')
    return render(request, 'voter_app/confirm_delete.html', {
        'object': family, 'object_type': 'Family', 'cancel_url': 'family_list'
    })


# ─────────────────────────────────────────────
# POLLING STATION VIEWS
# ─────────────────────────────────────────────

@login_required_custom
def station_list(request):
    stations = (
        PollingStations.objects
        .annotate(voter_count=Count('voters'))
        .order_by('city', 'name')
    )
    return render(request, 'voter_app/station_list.html', {'stations': stations})


@login_required_custom
def station_detail(request, pk):
    station = get_object_or_404(PollingStations, pk=pk)
    voters  = Voters.objects.filter(station=station).select_related('family')
    return render(request, 'voter_app/station_detail.html', {
        'station': station, 'voters': voters,
        'capacity_pct': round((voters.count() / station.capacity) * 100) if station.capacity else 0,
    })


@admin_required
def station_create(request):
    form = PollingStationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        station = form.save()
        log_action(request.session['user_id'], 'INSERT', 'pollingstations', station.station_id)
        messages.success(request, "Polling station created.")
        return redirect('station_detail', pk=station.pk)
    return render(request, 'voter_app/station_form.html', {'form': form, 'action': 'Add'})


@admin_required
def station_update(request, pk):
    station = get_object_or_404(PollingStations, pk=pk)
    form    = PollingStationForm(request.POST or None, instance=station)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_action(request.session['user_id'], 'UPDATE', 'pollingstations', pk)
        messages.success(request, "Station updated.")
        return redirect('station_detail', pk=pk)
    return render(request, 'voter_app/station_form.html', {'form': form, 'action': 'Edit'})


@admin_required
def station_delete(request, pk):
    station = get_object_or_404(PollingStations, pk=pk)
    if request.method == 'POST':
        station.delete()
        log_action(request.session['user_id'], 'DELETE', 'pollingstations', pk)
        messages.success(request, "Station deleted.")
        return redirect('station_list')
    return render(request, 'voter_app/confirm_delete.html', {
        'object': station, 'object_type': 'Polling Station', 'cancel_url': 'station_list'
    })


# ─────────────────────────────────────────────
# AUDIT LOGS VIEW  (admin only)
# ─────────────────────────────────────────────

@admin_required
def audit_logs(request):
    logs      = AuditLogs.objects.select_related('user').order_by('-timestamp')
    paginator = Paginator(logs, 30)
    page      = paginator.get_page(request.GET.get('page'))
    return render(request, 'voter_app/audit_logs.html', {'page': page})

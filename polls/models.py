from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class PoliceUser(AbstractUser):
    force_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Force Number"
    )
    rank = models.CharField(
        max_length=50,
        choices=[
            ('CONSTABLE', 'Constable'),
            ('CORPORAL', 'Corporal'),
            ('SERGEANT', 'Sergeant'),
            ('INSPECTOR', 'Inspector'),
            ('ASP', 'Assistant Superintendent of Police'),
           
        ]
    )
    station = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    is_active_voter = models.BooleanField(default=False)
    role = models.CharField(
        max_length=20,
        choices=[
            ('SUPER_ADMIN', 'Super Admin'),
            ('ADMIN', 'Election Admin'),
            ('VOTER', 'Voter'),
        ],
        default='VOTER'
    )
    must_change_password = models.BooleanField(default=True)

    def is_otp_valid(self):
        if not self.otp_code or not self.otp_expiry:
            return False
        return timezone.now() < self.otp_expiry

    def __str__(self):
        return f"{self.get_full_name()} (Force #{self.force_number}) - {self.rank} - {self.station}"

class Position(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class Election(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    positions = models.ManyToManyField(Position, through='ElectionPosition', related_name='elections')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    eligible_ranks = models.CharField(max_length=500, blank=True, help_text="Comma-separated ranks")
    eligible_stations = models.CharField(max_length=500, blank=True, help_text="Comma-separated stations")
    created_by = models.ForeignKey(PoliceUser, on_delete=models.CASCADE, related_name='created_elections')
    logo = models.ImageField(upload_to='election_logos/', blank=True, null=True)

    @property
    def is_active(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    def _split_eligible_values(self, raw_value, *, upper=False):
        values = [value.strip() for value in raw_value.split(',') if value.strip()]
        if upper:
            return {value.upper() for value in values}
        return {value.casefold() for value in values}

    def eligible_rank_values(self):
        if not self.eligible_ranks:
            return set()
        return self._split_eligible_values(self.eligible_ranks, upper=True)

    def eligible_station_values(self):
        if not self.eligible_stations:
            return set()
        return self._split_eligible_values(self.eligible_stations)

    def is_open(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    def is_voter_eligible(self, voter):
        voter_rank = (voter.rank or '').strip().upper()
        voter_station = (voter.station or '').strip().casefold()

        eligible_ranks = self.eligible_rank_values()
        if eligible_ranks and voter_rank not in eligible_ranks:
            return False

        eligible_stations = self.eligible_station_values()
        if eligible_stations and voter_station not in eligible_stations:
            return False

        return True

    @property
    def status(self):
        now = timezone.now()
        if now < self.start_time:
            return 'UPCOMING'
        elif now > self.end_time:
            return 'ENDED'
        else:
            return 'ACTIVE'

    @property
    def time_remaining(self):
        now = timezone.now()
        if now < self.start_time:
            delta = self.start_time - now
            prefix = "Starts in"
        elif now <= self.end_time:
            delta = self.end_time - now
            prefix = "Closes in"
        else:
            return "Ended"

        total_seconds = int(delta.total_seconds())
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        parts = []
        if days > 0:
            parts.append(f"{days}d")
            parts.append(f"{hours}h")
            parts.append(f"{minutes}m")
            parts.append(f"{seconds}s")
        elif hours > 0:
            parts.append(f"{hours}h")
            parts.append(f"{minutes}m")
            parts.append(f"{seconds}s")
        elif minutes > 0:
            parts.append(f"{minutes}m")
            parts.append(f"{seconds}s")
        else:
            parts.append(f"{seconds}s")

        return f"{prefix} {' '.join(parts)}"

    @property
    def seconds_until_start(self):
        now = timezone.now()
        if now < self.start_time:
            return int((self.start_time - now).total_seconds())
        return 0

    @property
    def seconds_until_end(self):
        now = timezone.now()
        if now <= self.end_time:
            return int((self.end_time - now).total_seconds())
        return 0

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.title}"

class ElectionPosition(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('election', 'position')

class Candidate(models.Model):
    name = models.CharField(max_length=200)
    force_number = models.CharField(max_length=50)
    rank = models.CharField(
        max_length=50,
        choices=[
            ('CONSTABLE', 'Constable'),
            ('CORPORAL', 'Corporal'),
            ('SERGEANT', 'Sergeant'),
            ('INSPECTOR', 'Inspector'),
            ('ASP', 'Assistant Superintendent of Police'),
           
        ]
    )
    photo = models.ImageField(upload_to='candidates/', blank=True, null=True)
    biography = models.TextField(blank=True, help_text="Short manifesto")
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='candidates')
    created_by = models.ForeignKey(PoliceUser, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('election', 'force_number')
        ordering = ['position', 'name']

    def __str__(self):
        return f"{self.name} ({self.rank}) - {self.position.name}"

class Vote(models.Model):
    voter = models.ForeignKey(PoliceUser, on_delete=models.CASCADE, related_name='votes')
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        unique_together = ('voter', 'election', 'position')
        ordering = ['-voted_at']

    def __str__(self):
        return f"{self.voter.force_number} -> {self.candidate.name} ({self.position.name}) ({self.election})"

class ElectionRegistration(models.Model):
    voter = models.ForeignKey(PoliceUser, on_delete=models.CASCADE, related_name='election_registrations')
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='voter_registrations')
    registered_at = models.DateTimeField(default=timezone.now)
    registered_by = models.ForeignKey(PoliceUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='registrations_made')

    class Meta:
        unique_together = ('voter', 'election')
        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.voter.force_number} registered for {self.election.title}"


class AuditLog(models.Model):
    ACTION_LOGIN = 'LOGIN'
    ACTION_LOGOUT = 'LOGOUT'
    ACTION_VOTE = 'VOTE'
    ACTION_PASSWORD_CHANGE = 'PASSWORD_CHANGE'
    ACTION_ADMIN_CREATE = 'ADMIN_CREATE'
    ACTION_ADMIN_UPDATE = 'ADMIN_UPDATE'
    ACTION_ADMIN_DELETE = 'ADMIN_DELETE'

    ACTION_ELECTION_CREATE = 'ELECTION_CREATE'
    ACTION_ELECTION_UPDATE = 'ELECTION_UPDATE'
    ACTION_ELECTION_DELETE = 'ELECTION_DELETE'
    ACTION_ELECTION_TOGGLE = 'ELECTION_TOGGLE'

    ACTION_CANDIDATE_CREATE = 'CANDIDATE_CREATE'
    ACTION_CANDIDATE_UPDATE = 'CANDIDATE_UPDATE'
    ACTION_CANDIDATE_DELETE = 'CANDIDATE_DELETE'

    ACTION_VOTER_CREATE = 'VOTER_CREATE'
    ACTION_VOTER_UPDATE = 'VOTER_UPDATE'
    ACTION_VOTER_DELETE = 'VOTER_DELETE'
    ACTION_VOTER_RESET_PASSWORD = 'VOTER_RESET_PASSWORD'
    ACTION_VOTER_BULK_CREATE = 'VOTER_BULK_CREATE'

    ACTION_POSITION_CREATE = 'POSITION_CREATE'
    ACTION_POSITION_UPDATE = 'POSITION_UPDATE'
    ACTION_POSITION_DELETE = 'POSITION_DELETE'

    ACTION_EXPORT_VOTERS = 'EXPORT_VOTERS'
    ACTION_EXPORT_CANDIDATES = 'EXPORT_CANDIDATES'
    ACTION_EXPORT_RESULTS = 'EXPORT_RESULTS'

    ACTION_CHOICES = [
        (ACTION_LOGIN, 'Login'),
        (ACTION_LOGOUT, 'Logout'),
        (ACTION_VOTE, 'Vote Cast'),
        (ACTION_PASSWORD_CHANGE, 'Password Change'),
        (ACTION_ADMIN_CREATE, 'Admin Create (Legacy)'),
        (ACTION_ADMIN_UPDATE, 'Admin Update (Legacy)'),
        (ACTION_ADMIN_DELETE, 'Admin Delete (Legacy)'),
        (ACTION_ELECTION_CREATE, 'Election Created'),
        (ACTION_ELECTION_UPDATE, 'Election Updated'),
        (ACTION_ELECTION_DELETE, 'Election Deleted'),
        (ACTION_ELECTION_TOGGLE, 'Election Toggled'),
        (ACTION_CANDIDATE_CREATE, 'Candidate Created'),
        (ACTION_CANDIDATE_UPDATE, 'Candidate Updated'),
        (ACTION_CANDIDATE_DELETE, 'Candidate Deleted'),
        (ACTION_VOTER_CREATE, 'Voter Created'),
        (ACTION_VOTER_UPDATE, 'Voter Updated'),
        (ACTION_VOTER_DELETE, 'Voter Deleted'),
        (ACTION_VOTER_RESET_PASSWORD, 'Voter Password Reset'),
        (ACTION_VOTER_BULK_CREATE, 'Voters Bulk Created'),
        (ACTION_POSITION_CREATE, 'Position Created'),
        (ACTION_POSITION_UPDATE, 'Position Updated'),
        (ACTION_POSITION_DELETE, 'Position Deleted'),
        (ACTION_EXPORT_VOTERS, 'Voters Exported'),
        (ACTION_EXPORT_CANDIDATES, 'Candidates Exported'),
        (ACTION_EXPORT_RESULTS, 'Results Exported'),
    ]

    user = models.ForeignKey(PoliceUser, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    details = models.TextField()
    target_model = models.CharField(max_length=50, blank=True)
    target_id = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"

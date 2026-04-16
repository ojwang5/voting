from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class PoliceUser(AbstractUser):
    FORCE_NUMBER_RANGE = (62800, 73500)
    
    force_number = models.IntegerField(
        unique=True,
        validators=[
            MinValueValidator(FORCE_NUMBER_RANGE[0]),
            MaxValueValidator(FORCE_NUMBER_RANGE[1])
        ],
        help_text=f"Force Number (valid range: {FORCE_NUMBER_RANGE[0]} - {FORCE_NUMBER_RANGE[1]})"
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
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(PoliceUser, on_delete=models.CASCADE, related_name='created_elections')

    def save(self, *args, **kwargs):
        now = timezone.now()
        self.is_active = self.start_time <= now <= self.end_time
        super().save(*args, **kwargs)

    def is_open(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    def is_voter_eligible(self, voter):
        if self.eligible_ranks:
            ranks = [r.strip().upper() for r in self.eligible_ranks.split(',')]
            if voter.rank not in ranks:
                return False
        if self.eligible_stations:
            stations = [s.strip() for s in self.eligible_stations.split(',')]
            if voter.station not in stations:
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
            return f"Starts in {delta.days}d {delta.seconds // 3600}h"
        elif now <= self.end_time:
            delta = self.end_time - now
            return f"Closes in {delta.days}d {delta.seconds // 3600}h"
        else:
            return "Ended"

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
    force_number = models.IntegerField()
    rank = models.CharField(max_length=50)
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
    voted_at = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        unique_together = ('voter', 'election')
        ordering = ['-voted_at']

    def __str__(self):
        return f"{self.voter.force_number} -> {self.candidate.name} ({self.election})"

class AuditLog(models.Model):
    ACTION_LOGIN = 'LOGIN'
    ACTION_VOTE = 'VOTE'
    ACTION_ADMIN_CREATE = 'ADMIN_CREATE'
    ACTION_ADMIN_UPDATE = 'ADMIN_UPDATE'
    ACTION_PASSWORD_CHANGE = 'PASSWORD_CHANGE'
    
    ACTION_CHOICES = [
        (ACTION_LOGIN, 'Login'),
        (ACTION_VOTE, 'Vote Cast'),
        (ACTION_ADMIN_CREATE, 'Admin Create'),
        (ACTION_ADMIN_UPDATE, 'Admin Update'),
        (ACTION_PASSWORD_CHANGE, 'Password Change'),
    ]
    
    user = models.ForeignKey(PoliceUser, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    details = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"

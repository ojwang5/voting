from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator

class Position(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g. 'President', 'Secretary'
    
    def __str__(self):
        return self.name

class Election(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_elections')

    def save(self, *args, **kwargs):
        now = timezone.now()
        if self.end_time <= now:
            self.is_active = False
        super().save(*args, **kwargs)

    def is_open(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.title} ({self.position.name})"

class Candidate(models.Model):
    name = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='candidates/', blank=True, null=True)
    biography = models.TextField(blank=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='candidates')
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='candidates')

    def __str__(self):
        return f"{self.name} - {self.position.name}"

class Voter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='voter_profile')
    national_id = models.CharField(max_length=20, unique=True, validators=[RegexValidator(r'^\d{10,20}$', 'Enter valid ID')])
    phone = models.CharField(max_length=15, blank=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='verified_voters')

    def __str__(self):
        return f"{self.user.username} ({self.national_id})"

class Vote(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('voter', 'election')

    def __str__(self):
        return f"{self.voter} voted for {self.candidate} in {self.election}"

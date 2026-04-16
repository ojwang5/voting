from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .models import Election, Candidate, Vote, Position, ElectionPosition

User = get_user_model()

class ElectionModelTests(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name='President')
        self.admin = User.objects.create_user(
            username='admin', password='testpass123', role='ADMIN',
            force_number=62801, rank='INSPECTOR', station='HQ'
        )
    
    def test_election_is_open_during_active_period(self):
        election = Election.objects.create(
            title='Test Election',
            start_time=timezone.now() - timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=1),
            created_by=self.admin
        )
        ElectionPosition.objects.create(election=election, position=self.position)
        self.assertTrue(election.is_open())
    
    def test_election_is_closed_before_start(self):
        election = Election.objects.create(
            title='Test Election',
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=2),
            created_by=self.admin
        )
        self.assertFalse(election.is_open())
    
    def test_election_is_closed_after_end(self):
        election = Election.objects.create(
            title='Test Election',
            start_time=timezone.now() - timedelta(hours=2),
            end_time=timezone.now() - timedelta(hours=1),
            created_by=self.admin
        )
        self.assertFalse(election.is_open())
    
    def test_election_status(self):
        election = Election.objects.create(
            title='Test Election',
            start_time=timezone.now() - timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=1),
            created_by=self.admin
        )
        self.assertEqual(election.status, 'ACTIVE')


class VoteTests(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name='President')
        self.admin = User.objects.create_user(
            username='admin', password='testpass123', role='ADMIN',
            force_number=62801, rank='INSPECTOR', station='HQ'
        )
        self.voter = User.objects.create_user(
            username='voter', password='testpass123', role='VOTER',
            force_number=62900, rank='CONSTABLE', station='Kampala'
        )
        self.election = Election.objects.create(
            title='Test Election',
            start_time=timezone.now() - timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=1),
            created_by=self.admin
        )
        self.candidate = Candidate.objects.create(
            name='Test Candidate',
            force_number=62901,
            rank='CONSTABLE',
            position=self.position,
            election=self.election,
            created_by=self.admin
        )
    
    def test_user_can_vote_once(self):
        Vote.objects.create(
            voter=self.voter,
            election=self.election,
            candidate=self.candidate
        )
        self.assertEqual(Vote.objects.filter(voter=self.voter, election=self.election).count(), 1)
    
    def test_user_cannot_vote_twice(self):
        Vote.objects.create(
            voter=self.voter,
            election=self.election,
            candidate=self.candidate
        )
        with self.assertRaises(Exception):
            Vote.objects.create(
                voter=self.voter,
                election=self.election,
                candidate=self.candidate
            )


class PositionModelTests(TestCase):
    def test_position_creation(self):
        position = Position.objects.create(name='Vice President')
        self.assertEqual(str(position), 'Vice President')

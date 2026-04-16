from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import models
from .models import Election, Candidate, Vote, PoliceUser, AuditLog
from django.db.models import Q
from .serializers import ElectionSerializer, VoteSerializer

class ElectionList(generics.ListAPIView):
    serializer_class = ElectionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Election.objects.filter(is_active=True).filter(
            Q(eligible_ranks__isnull=True) | Q(eligible_ranks__icontains=user.rank)
        ).filter(
            Q(eligible_stations__isnull=True) | Q(eligible_stations__icontains=user.station)
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_vote(request):
    election_id = request.data.get('election_id')
    candidate_id = request.data.get('candidate_id')
    
    election = get_object_or_404(Election, pk=election_id)
    candidate = get_object_or_404(Candidate, pk=candidate_id, election=election)
    
    if not election.is_open():
        return Response({'error': 'Election not open'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not election.is_voter_eligible(request.user):
        return Response({'error': 'Not eligible'}, status=status.HTTP_403_FORBIDDEN)
    
    if Vote.objects.filter(voter=request.user, election=election).exists():
        return Response({'error': 'Already voted'}, status=status.HTTP_400_BAD_REQUEST)
    
    Vote.objects.create(
        voter=request.user,
        election=election,
        candidate=candidate,
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    # Audit log
    AuditLog.objects.create(
        user=request.user,
        action='VOTE',
        ip_address=request.META.get('REMOTE_ADDR'),
        details=f'API vote for {candidate.name} in {election.title}'
    )
    
    return Response({'message': 'Vote recorded successfully'}, status=status.HTTP_201_CREATED)


from rest_framework import serializers
from .models import Election, Candidate, Vote, PoliceUser

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'name', 'rank', 'photo', 'biography']

class ElectionSerializer(serializers.ModelSerializer):
    candidates = CandidateSerializer(many=True, read_only=True)
    total_votes = serializers.SerializerMethodField()
    position_name = serializers.CharField(source='position.name', read_only=True)
    voter_eligible = serializers.SerializerMethodField()

    class Meta:
        model = Election
        fields = ['id', 'title', 'description', 'position_name', 'start_time', 'end_time', 'is_active', 'candidates', 'total_votes', 'voter_eligible']

    def get_total_votes(self, obj):
        return Vote.objects.filter(election=obj).count()

    def get_voter_eligible(self, obj):
        user = self.context['request'].user
        return obj.is_voter_eligible(user)

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'election', 'candidate', 'voted_at']

class PoliceUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliceUser
        fields = ['id', 'username', 'force_number', 'rank', 'station', 'role', 'is_active_voter']
        read_only_fields = ['id', 'role']


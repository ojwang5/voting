from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import PoliceUser, Position, Election, ElectionPosition, Candidate, Vote, AuditLog
from django.utils.safestring import mark_safe

class PoliceUserAdmin(UserAdmin):
    list_display = ('username', 'force_number', 'rank', 'station', 'role', 'is_active', 'is_active_voter', 'must_change_password', 'date_joined')
    list_filter = ('rank', 'role', 'is_active_voter', 'is_staff', 'is_active')
    search_fields = ('username', 'force_number', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    
    # Use simple fieldsets without adding extra fields that might cause issues
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Police Force Details', {'fields': ('force_number', 'rank', 'station', 'phone', 'role', 'is_active_voter', 'must_change_password')}),
    )
    
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Police Force Details', {'fields': ('force_number', 'rank', 'station', 'phone', 'role', 'is_active_voter', 'must_change_password')}),
    )

admin.site.register(PoliceUser, PoliceUserAdmin)

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'election_count')
    search_fields = ('name',)
    
    def election_count(self, obj):
        return obj.elections.count()
    election_count.short_description = 'Number of Elections'

@admin.register(ElectionPosition)
class ElectionPositionAdmin(admin.ModelAdmin):
    list_display = ('election', 'position')
    list_filter = ('election', 'position')
    search_fields = ('election__title', 'position__name')

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'logo_preview', 'start_time', 'end_time', 'is_active_display', 'created_by', 'candidate_count', 'vote_count', 'election_status')
    readonly_fields = ('created_by', 'candidate_count', 'vote_count', 'is_active_display', 'logo_preview')
    
    def logo_preview(self, obj):
        if obj.logo:
            return mark_safe(f'<img src="{obj.logo.url}" style="max-height: 50px; max-width: 100px;" />')
        return "No logo"
    logo_preview.short_description = 'Logo Preview'
    logo_preview.allow_tags = True
    list_filter = ('start_time', 'created_by')
    date_hierarchy = 'start_time'
    search_fields = ('title', 'description', 'created_by__username')
    readonly_fields = ('created_by', 'candidate_count', 'vote_count', 'is_active_display')
    
    @admin.display(boolean=True, description='Is Active')
    def is_active_display(self, obj):
        return obj.is_active
    
    def candidate_count(self, obj):
        return obj.candidates.count()
    candidate_count.short_description = 'Total Candidates'
    
    def vote_count(self, obj):
        return obj.vote_set.count()
    vote_count.short_description = 'Total Votes'
    
    def election_status(self, obj):
        return obj.status
    election_status.short_description = 'Status'

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'election', 'position', 'force_number', 'rank', 'created_by', 'vote_count')
    list_filter = ('election', 'position', 'rank')
    search_fields = ('name', 'force_number', 'election__title')
    readonly_fields = ('created_by', 'vote_count')
    
    def vote_count(self, obj):
        return obj.vote_set.count()
    vote_count.short_description = 'Votes Received'

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('voter', 'election', 'position', 'candidate', 'voted_at', 'ip_address')
    list_filter = ('election', 'position', 'voted_at')
    date_hierarchy = 'voted_at'
    raw_id_fields = ('voter', 'election', 'candidate', 'position')
    search_fields = ('voter__username', 'candidate__name', 'election__title', 'position__name')
    readonly_fields = ('voter', 'election', 'candidate', 'position', 'voted_at', 'ip_address')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'target_model', 'target_id', 'timestamp', 'ip_address')
    list_filter = ('action', 'user', 'timestamp')
    date_hierarchy = 'timestamp'
    search_fields = ('user__username', 'action', 'details', 'target_model')
    readonly_fields = ('user', 'action', 'details', 'target_model', 'target_id', 'timestamp', 'ip_address')

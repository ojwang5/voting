from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import PoliceUser, Position, Election, ElectionPosition, Candidate, Vote, AuditLog

class PoliceUserAdmin(UserAdmin):
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Police Force Details', {
            'fields': ('force_number', 'rank', 'station', 'phone', 'role', 'is_active_voter', 'must_change_password', 'username'),
        }),
    )
    fieldsets = UserAdmin.fieldsets + (
        ('Police Force Details', {'fields': ('force_number', 'rank', 'station', 'phone', 'role', 'is_active_voter', 'must_change_password')}),
    )
    list_display = ('username', 'force_number', 'rank', 'station', 'role', 'is_active', 'is_active_voter', 'must_change_password', 'date_joined')
    list_filter = ('rank', 'role', 'is_active_voter', 'is_staff', 'is_active')
    search_fields = ('username', 'force_number', 'first_name', 'last_name', 'email')

admin.site.register(PoliceUser, PoliceUserAdmin)

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(ElectionPosition)
class ElectionPositionAdmin(admin.ModelAdmin):
    list_display = ('election', 'position')

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'is_active', 'created_by')
    list_filter = ('is_active', 'start_time')
    date_hierarchy = 'start_time'

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'election', 'position', 'force_number', 'rank', 'created_by')
    list_filter = ('election', 'position')
    search_fields = ('name', 'force_number')

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('voter', 'election', 'candidate', 'voted_at', 'ip_address')
    list_filter = ('election', 'voted_at')
    date_hierarchy = 'voted_at'
    raw_id_fields = ('voter', 'election', 'candidate')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp', 'ip_address')
    list_filter = ('action', 'user', 'timestamp')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)

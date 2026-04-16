from django.urls import path
from . import views, views_register, views_admin
from .views_api import ElectionList, api_vote

app_name = 'polls'

urlpatterns = [
    path('', views.dashboard, name='index'),
    path('elections/', views.dashboard, name='elections'),
    
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/otp/', views.password_reset_otp, name='password_reset_otp'),
    path('password-reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    path('change-password/', views.change_password, name='change_password'),
    
    path('register/', views_register.register, name='register'),
    path('elections/<int:election_id>/vote/', views.vote, name='vote'),
    path('elections/<int:election_id>/results/', views.results, name='results'),
    
    path('admin/dashboard/', views_admin.admin_dashboard, name='admin_dashboard'),
    path('admin/positions/', views_admin.admin_positions, name='admin_positions'),
    path('admin/positions/add/', views_admin.admin_positions, name='admin_position_add'),
    path('admin/positions/<int:position_id>/edit/', views_admin.edit_position, name='admin_position_edit'),
    path('admin/positions/<int:position_id>/delete/', views_admin.delete_position, name='admin_position_delete'),
    path('admin/elections/', views_admin.admin_elections, name='admin_elections'),
    path('admin/elections/create/', views_admin.create_election, name='create_election'),
    path('admin/elections/<int:election_id>/edit/', views_admin.edit_election, name='edit_election'),
    path('admin/elections/<int:election_id>/toggle/', views_admin.toggle_election_status, name='toggle_election_status'),
    path('admin/elections/<int:election_id>/delete/', views_admin.delete_election, name='delete_election'),
    
    path('admin/register-voter/', views_admin.admin_register_voter, name='admin_register_voter'),
    path('admin/register-voter/credentials/', views_admin.admin_voter_credentials, name='admin_voter_credentials'),
    path('admin/voters/', views_admin.admin_voters, name='admin_voters'),
    path('admin/voters/<int:voter_id>/edit/', views_admin.admin_edit_voter, name='admin_edit_voter'),
    path('admin/voters/<int:voter_id>/delete/', views_admin.admin_delete_voter, name='admin_delete_voter'),
    path('admin/voters/<int:voter_id>/reset-password/', views_admin.admin_reset_voter_password, name='admin_reset_voter_password'),
    
    path('admin/register-candidate/', views_admin.admin_register_candidate, name='admin_register_candidate'),
    path('admin/candidates/', views_admin.admin_candidates, name='admin_candidates'),
    path('admin/candidates/<int:candidate_id>/edit/', views_admin.admin_edit_candidate, name='admin_edit_candidate'),
    path('admin/candidates/<int:candidate_id>/delete/', views_admin.admin_delete_candidate, name='admin_delete_candidate'),
    
    path('admin/export/voters/csv/', views_admin.export_voters_csv, name='export_voters_csv'),
    path('admin/export/voters/pdf/', views_admin.export_voters_pdf, name='export_voters_pdf'),
    path('admin/export/voters/docx/', views_admin.export_voters_docx, name='export_voters_docx'),
    
    path('admin/export/candidates/csv/', views_admin.export_candidates_csv, name='export_candidates_csv'),
    path('admin/export/candidates/pdf/', views_admin.export_candidates_pdf, name='export_candidates_pdf'),
    path('admin/export/candidates/docx/', views_admin.export_candidates_docx, name='export_candidates_docx'),
    
    path('admin/export/results/<int:election_id>/csv/', views_admin.export_results_csv, name='export_results_csv'),
    path('admin/export/results/<int:election_id>/pdf/', views_admin.export_results_pdf, name='export_results_pdf'),
    path('admin/export/results/<int:election_id>/docx/', views_admin.export_results_docx, name='export_results_docx'),
    
    path('api/elections/', ElectionList.as_view(), name='api_elections'),
    path('api/vote/', api_vote, name='api_vote'),
]

# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('voter-dashboard/', views.voter_dashboard, name='voter_dashboard'),
    path('auditor-dashboard/', views.auditor_dashboard, name='auditor_dashboard'),

    # Elections
    path('elections/', views.election_list, name='election_list'),
    path('elections/create/', views.create_election, name='create_election'),
    path('candidates/create/', views.create_candidate, name='create_candidate'),

    # Voter routes
    path('voter/', views.voter_dashboard, name='voter_dashboard'),
    path('voter/vote/<int:election_id>/', views.vote_view, name='vote'),

   path('dashboard/elections/<int:election_id>/results/', views.election_results, name='election_results'),

#    path('auditor/', views.auditor_dashboard, name='auditor_dashboard'),
#    path('auditor/results/<int:election_id>/', views.auditor_results, name='auditor_results'),

   # Public access (no login required)
path('guest/', views.auditor_dashboard, name='guest_dashboard'),
path('guest/results/<int:election_id>/', views.auditor_results, name='guest_results'),



]



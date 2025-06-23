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
]



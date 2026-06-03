# voter_app/urls.py

from django.urls import path
from . import views

urlpatterns = [

    # ── Auth ──────────────────────────────
    path('',        views.login_view,  name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ── Dashboard ─────────────────────────
    path('dashboard/', views.dashboard, name='dashboard'),

    # ── Voters ────────────────────────────
    path('voters/',                views.voter_list,   name='voter_list'),
    path('voters/add/',            views.voter_create, name='voter_create'),
    path('voters/<int:pk>/',       views.voter_detail, name='voter_detail'),
    path('voters/<int:pk>/edit/',  views.voter_update, name='voter_update'),
    path('voters/<int:pk>/delete/',views.voter_delete, name='voter_delete'),

    # ── Families ──────────────────────────
    path('families/',                 views.family_list,   name='family_list'),
    path('families/add/',             views.family_create, name='family_create'),
    path('families/<int:pk>/',        views.family_detail, name='family_detail'),
    path('families/<int:pk>/edit/',   views.family_update, name='family_update'),
    path('families/<int:pk>/delete/', views.family_delete, name='family_delete'),

    # ── Polling Stations ──────────────────
    path('stations/',                 views.station_list,   name='station_list'),
    path('stations/add/',             views.station_create, name='station_create'),
    path('stations/<int:pk>/',        views.station_detail, name='station_detail'),
    path('stations/<int:pk>/edit/',   views.station_update, name='station_update'),
    path('stations/<int:pk>/delete/', views.station_delete, name='station_delete'),

    # ── Audit Logs ────────────────────────
    path('audit/', views.audit_logs, name='audit_logs'),
]

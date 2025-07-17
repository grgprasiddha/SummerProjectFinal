from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('browse/', views.browse_jobs, name='browse'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('post/', views.post_job, name='post_job'),
    path('my-jobs/', views.my_jobs, name='my_jobs'),
    path('job/<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('job/<int:job_id>/submit-proposal/', views.submit_proposal, name='submit_proposal'),
    path('proposal/<int:proposal_id>/approve/', views.approve_proposal, name='approve_proposal'),
    path('proposal/<int:proposal_id>/disapprove/', views.disapprove_proposal, name='disapprove_proposal'),
    # Dispute URLs
    path('contract/<int:contract_id>/raise-dispute/', views.raise_dispute, name='raise_dispute'),
    path('my-disputes/', views.my_disputes, name='my_disputes'),
    path('admin/disputes/', views.admin_disputes, name='admin_disputes'),
    path('admin/dispute/<int:dispute_id>/', views.admin_dispute_detail, name='admin_dispute_detail'),
    path('contract/<int:contract_id>/', views.contract_detail, name='contract_detail'),
    path('contract/<int:contract_id>/message/', views.contract_message, name='contract_message'),
    path('contract/<int:contract_id>/complete/', views.complete_job, name='complete_job'),
    path('contract/<int:contract_id>/confirm/', views.confirm_job_completion, name='confirm_job_completion'),
] 
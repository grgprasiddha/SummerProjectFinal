from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import IntegrityError
from .models import Job, Proposal, Contract, Dispute
from .forms import JobForm, ProposalForm, DisputeForm
from django.db import models
from payments.models import Payment
from users.models import Notification, Message
from django.views.decorators.http import require_POST

def is_admin(user):
    return user.is_superuser

def browse_jobs(request):
    category = request.GET.get('category')
    search = request.GET.get('search', '').strip()
    jobs = Job.objects.filter(status='open')

    if category:
        jobs = jobs.filter(category=category)
    if search:
        jobs = jobs.filter(models.Q(title__icontains=search) | models.Q(description__icontains=search))

    categories = Job.CATEGORY_CHOICES
    context = {
        'jobs': jobs,
        'selected_category': category,
        'search_query': search,
        'categories': categories,
    }
    return render(request, 'jobs/browse.html', context)

def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    proposals = job.proposals.all()
    
    # Check if current user has already submitted a proposal for this job
    user_has_proposal = False
    if request.user.is_authenticated:
        user_has_proposal = Proposal.objects.filter(job=job, freelancer=request.user).exists()
    
    # Check if there's an active contract for this job
    contract = None
    if hasattr(job, 'contract'):
        contract = job.contract
    
    context = {
        'job': job,
        'proposals': proposals,
        'user_has_proposal': user_has_proposal,
        'contract': contract,
    }
    return render(request, 'jobs/job_detail.html', context)

@login_required
def post_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.client = request.user
            job.save()

            # Notify all freelancers with job alerts enabled
            from users.models import UserProfile, Notification
            freelancers = UserProfile.objects.filter(user_type='freelancer', job_alerts=True).select_related('user')
            for freelancer in freelancers:
                Notification.objects.create(
                    recipient=freelancer.user,
                    notification_type='job_posted',
                    title=f'New Job Posted: "{job.title}"',
                    message=f'A new job "{job.title}" has been posted in {job.get_category_display()}.',
                    related_job=job
                )
            messages.success(request, 'Job posted successfully!')
            return redirect('jobs:job_detail', job_id=job.id)
    else:
        form = JobForm()
    
    return render(request, 'jobs/post_job.html', {'form': form})

@login_required
def my_jobs(request):
    posted_jobs = Job.objects.filter(client=request.user)
    applied_jobs = Proposal.objects.filter(freelancer=request.user)
    
    context = {
        'posted_jobs': posted_jobs,
        'applied_jobs': applied_jobs,
    }
    return render(request, 'jobs/my_jobs.html', context)

@login_required
def submit_proposal(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # Check if user has already submitted a proposal for this job
    existing_proposal = Proposal.objects.filter(job=job, freelancer=request.user).first()
    if existing_proposal:
        messages.warning(request, 'You have already submitted a job request for this gig.')
        return redirect('jobs:job_detail', job_id=job.id)
    
    if request.method == 'POST':
        form = ProposalForm(request.POST)
        if form.is_valid():
            try:
                proposal = form.save(commit=False)
                proposal.job = job
                proposal.freelancer = request.user
                proposal.save()
                
                # Create notification for the client
                Notification.objects.create(
                    recipient=job.client,
                    notification_type='job_request',
                    title=f'New Job Request for "{job.title}"',
                    message=f'{request.user.username} has submitted a job request for your gig "{job.title}" with a bid of NRS{proposal.bid_amount}.',
                    related_job=job,
                    related_proposal=proposal
                )
                
                messages.success(request, 'Job request submitted successfully!')
                return redirect('jobs:job_detail', job_id=job.id)
            except IntegrityError:
                messages.error(request, 'You have already submitted a job request for this gig.')
                return redirect('jobs:job_detail', job_id=job.id)
    else:
        form = ProposalForm()
    
    context = {
        'form': form,
        'job': job,
    }
    return render(request, 'jobs/submit_proposal.html', context)

@require_POST
@login_required
def approve_proposal(request, proposal_id):
    proposal = get_object_or_404(Proposal, id=proposal_id)
    job = proposal.job
    if request.user != job.client and not request.user.is_superuser:
        messages.error(request, 'You are not authorized to approve this proposal.')
        return redirect('jobs:job_detail', job_id=job.id)
    if proposal.status != 'pending':
        messages.warning(request, 'This proposal has already been processed.')
        return redirect('jobs:job_detail', job_id=job.id)
    
    # Check if employer has sufficient balance
    from payments.models import Wallet
    try:
        employer_wallet = request.user.wallet
    except Wallet.DoesNotExist:
        messages.error(request, 'You need to add funds to your wallet before approving a proposal.')
        return redirect('payments:add_funds')
    
    if employer_wallet.balance < proposal.bid_amount:
        messages.error(request, f'Insufficient balance. You need NRS{proposal.bid_amount} but have NRS{employer_wallet.balance}.')
        return redirect('payments:add_funds')
    
    # Get or create freelancer wallet
    freelancer_wallet, created = Wallet.objects.get_or_create(user=proposal.freelancer)
    
    # Deduct amount from employer's wallet
    if not employer_wallet.deduct_funds(proposal.bid_amount):
        messages.error(request, 'Failed to process payment. Please try again.')
        return redirect('jobs:job_detail', job_id=job.id)
    
    # Add amount to freelancer's pending balance (escrow)
    freelancer_wallet.add_pending_funds(proposal.bid_amount)
    
    # Create escrow payment record
    from payments.models import Payment, Transaction
    escrow_payment = Payment.objects.create(
        contract=None,  # Will be updated after contract creation
        payer=request.user,
        payee=proposal.freelancer,
        amount=proposal.bid_amount,
        payment_type='escrow',
        status='completed',
        description=f'Escrow payment for job "{job.title}"'
    )
    
    # Create transaction records
    Transaction.objects.create(
        wallet=employer_wallet,
        payment=escrow_payment,
        amount=proposal.bid_amount,
        transaction_type='debit',
        description=f'Payment for job "{job.title}" to {proposal.freelancer.username}',
        balance_after=employer_wallet.balance
    )
    
    Transaction.objects.create(
        wallet=freelancer_wallet,
        payment=escrow_payment,
        amount=proposal.bid_amount,
        transaction_type='credit',
        description=f'Pending payment for job "{job.title}" from {request.user.username}',
        balance_after=freelancer_wallet.pending_balance
    )
    
    # Approve proposal
    proposal.status = 'accepted'
    proposal.save()
    
    # Create contract
    contract = Contract.objects.create(
        job=job,
        freelancer=proposal.freelancer,
        proposal=proposal,
        terms=proposal.cover_letter,
        start_date=models.DateField().to_python(job.created_at.date()),
        end_date=job.deadline,
        status='active',
    )
    
    # Update payment with contract reference
    escrow_payment.contract = contract
    escrow_payment.save()
    
    # Notify freelancer
    Notification.objects.create(
        recipient=proposal.freelancer,
        notification_type='proposal_accepted',
        title=f'Proposal Accepted for "{job.title}"',
        message=f'Your proposal for the job "{job.title}" has been accepted. Payment of NRS{proposal.bid_amount} has been placed in escrow.',
        related_job=job,
        related_proposal=proposal
    )
    
    # Notify employer
    Notification.objects.create(
        recipient=request.user,
        notification_type='payment_made',
        title=f'Payment Processed for "{job.title}"',
        message=f'Payment of NRS{proposal.bid_amount} has been deducted from your wallet and placed in escrow for {proposal.freelancer.username}.',
        related_job=job,
        related_proposal=proposal
    )
    
    messages.success(request, f'Proposal approved! Payment of NRS{proposal.bid_amount} has been placed in escrow.')
    return redirect('jobs:job_detail', job_id=job.id)

@require_POST
@login_required
def disapprove_proposal(request, proposal_id):
    proposal = get_object_or_404(Proposal, id=proposal_id)
    job = proposal.job
    if request.user != job.client and not request.user.is_superuser:
        messages.error(request, 'You are not authorized to disapprove this proposal.')
        return redirect('jobs:job_detail', job_id=job.id)
    if proposal.status != 'pending':
        messages.warning(request, 'This proposal has already been processed.')
        return redirect('jobs:job_detail', job_id=job.id)
    # Disapprove proposal
    proposal.status = 'rejected'
    proposal.save()
    # Notify freelancer
    Notification.objects.create(
        recipient=proposal.freelancer,
        notification_type='proposal_rejected',
        title=f'Proposal Rejected for "{job.title}"',
        message=f'Your proposal for the job "{job.title}" has been rejected by the employer.',
        related_job=job,
        related_proposal=proposal
    )
    messages.success(request, 'Proposal disapproved.')
    return redirect('jobs:job_detail', job_id=job.id)

@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.user != job.client and not request.user.is_superuser:
        messages.error(request, 'You are not authorized to edit this job.')
        return redirect('jobs:job_detail', job_id=job.id)

    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job details updated successfully!')
            return redirect('jobs:job_detail', job_id=job.id)
    else:
        form = JobForm(instance=job)
    return render(request, 'jobs/edit_job.html', {'form': form, 'job': job})

@login_required
def raise_dispute(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    if request.method == 'POST':
        form = DisputeForm(request.POST, request.FILES)
        if form.is_valid():
            dispute = form.save(commit=False)
            dispute.contract = contract
            dispute.raised_by = request.user
            dispute.save()
            messages.success(request, 'Dispute raised successfully!')
            return redirect('jobs:contract_detail', contract_id=contract.id)
    else:
        form = DisputeForm()
    return render(request, 'jobs/raise_dispute.html', {'form': form, 'contract': contract})

@login_required
def my_disputes(request):
    disputes = Dispute.objects.filter(raised_by=request.user)
    return render(request, 'jobs/my_disputes.html', {'disputes': disputes})

@user_passes_test(is_admin)
def admin_disputes(request):
    disputes = Dispute.objects.all().order_by('-created_at')
    return render(request, 'jobs/admin_disputes.html', {'disputes': disputes})

@user_passes_test(is_admin)
def admin_dispute_detail(request, dispute_id):
    dispute = get_object_or_404(Dispute, id=dispute_id)
    if request.method == 'POST':
        resolution = request.POST.get('resolution')
        admin_decision = request.POST.get('admin_decision')
        status = request.POST.get('status')
        dispute.resolution = resolution
        dispute.admin_decision = admin_decision
        dispute.status = status
        dispute.decided_by = request.user
        dispute.save()
        messages.success(request, 'Dispute updated successfully!')
        return redirect('jobs:admin_disputes')
    return render(request, 'jobs/admin_dispute_detail.html', {'dispute': dispute})

@login_required
def contract_detail(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    disputes = contract.disputes.all().order_by('-created_at')
    
    # Get messages between the contract parties
    messages = Message.objects.filter(
        (models.Q(sender=contract.freelancer) & models.Q(recipient=contract.job.client)) |
        (models.Q(sender=contract.job.client) & models.Q(recipient=contract.freelancer))
    ).order_by('created_at')
    
    # Mark messages as read for the current user
    if request.user in [contract.freelancer, contract.job.client]:
        messages.filter(recipient=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'jobs/contract_detail.html', {
        'contract': contract, 
        'disputes': disputes,
        'messages': messages
    })

@require_POST
@login_required
def contract_message(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    
    # Check if user is part of this contract
    if request.user not in [contract.freelancer, contract.job.client]:
        messages.error(request, 'You are not authorized to send messages for this contract.')
        return redirect('jobs:contract_detail', contract_id=contract.id)
    
    content = request.POST.get('content', '').strip()
    if not content:
        messages.error(request, 'Message cannot be empty.')
        return redirect('jobs:contract_detail', contract_id=contract.id)
    
    # Determine recipient (the other party in the contract)
    recipient = contract.freelancer if request.user == contract.job.client else contract.job.client
    
    # Create the message
    message = Message.objects.create(
        sender=request.user,
        recipient=recipient,
        content=content
    )
    
    # Create notification for recipient
    Notification.objects.create(
        recipient=recipient,
        notification_type='system',
        title=f'New Message from {request.user.username}',
        message=f'You have received a new message regarding the contract for "{contract.job.title}".',
        related_job=contract.job
    )
    
    messages.success(request, 'Message sent successfully!')
    return redirect('jobs:contract_detail', contract_id=contract.id)

@require_POST
@login_required
def complete_job(request, contract_id):
    """Freelancer marks job as completed"""
    contract = get_object_or_404(Contract, id=contract_id)
    
    # Check if user is the freelancer for this contract
    if request.user != contract.freelancer:
        messages.error(request, 'You are not authorized to complete this job.')
        return redirect('jobs:contract_detail', contract_id=contract.id)
    
    # Check if job is already completed
    if contract.completed_by_freelancer:
        messages.warning(request, 'This job has already been marked as completed.')
        return redirect('jobs:contract_detail', contract_id=contract.id)
    
    # Mark job as completed by freelancer
    from django.utils import timezone
    contract.completed_by_freelancer = True
    contract.completed_at = timezone.now()
    contract.save()
    
    # Create notification for client
    Notification.objects.create(
        recipient=contract.job.client,
        notification_type='job_completed',
        title=f'Job Completed: "{contract.job.title}"',
        message=f'The freelancer {request.user.username} has marked the job "{contract.job.title}" as completed. Please review and confirm.',
        related_job=contract.job
    )
    
    messages.success(request, 'Job marked as completed successfully! The client will be notified to review and confirm.')
    return redirect('jobs:contract_detail', contract_id=contract.id)

@require_POST
@login_required
def confirm_job_completion(request, contract_id):
    """Client confirms job completion"""
    contract = get_object_or_404(Contract, id=contract_id)
    
    # Check if user is the client for this contract
    if request.user != contract.job.client:
        messages.error(request, 'You are not authorized to confirm this job completion.')
        return redirect('jobs:contract_detail', contract_id=contract.id)
    
    # Check if job was completed by freelancer
    if not contract.completed_by_freelancer:
        messages.error(request, 'The freelancer has not marked this job as completed yet.')
        return redirect('jobs:contract_detail', contract_id=contract.id)
    
    # Check if already confirmed
    if contract.confirmed_by_client:
        messages.warning(request, 'This job completion has already been confirmed.')
        return redirect('jobs:contract_detail', contract_id=contract.id)
    
    # Process payment release
    from payments.models import Wallet, Payment, Transaction
    
    # Get or create freelancer wallet
    freelancer_wallet, created = Wallet.objects.get_or_create(user=contract.freelancer)
    
    # Get the escrow payment for this contract
    try:
        escrow_payment = Payment.objects.get(
            payer=contract.job.client,
            payee=contract.freelancer,
            payment_type='escrow',
            status='completed'
        )
        # Update the payment with contract reference if not already set
        if not escrow_payment.contract:
            escrow_payment.contract = contract
            escrow_payment.save()
    except Payment.DoesNotExist:
        messages.error(request, 'Payment record not found. Please contact support.')
        return redirect('jobs:contract_detail', contract_id=contract.id)
    
    # Release pending funds to freelancer's available balance
    if not freelancer_wallet.release_pending_funds(escrow_payment.amount):
        messages.error(request, 'Failed to release payment. Please contact support.')
        return redirect('jobs:contract_detail', contract_id=contract.id)
    
    # Create release payment record
    release_payment = Payment.objects.create(
        contract=contract,
        payer=request.user,
        payee=contract.freelancer,
        amount=escrow_payment.amount,
        payment_type='release',
        status='completed',
        description=f'Payment release for completed job "{contract.job.title}"'
    )
    
    # Create transaction record for the release
    Transaction.objects.create(
        wallet=freelancer_wallet,
        payment=release_payment,
        amount=escrow_payment.amount,
        transaction_type='credit',
        description=f'Payment released for completed job "{contract.job.title}" from {request.user.username}',
        balance_after=freelancer_wallet.balance
    )
    
    # Confirm job completion
    from django.utils import timezone
    contract.confirmed_by_client = True
    contract.confirmed_at = timezone.now()
    contract.status = 'completed'
    contract.save()
    
    # Update job status
    contract.job.status = 'completed'
    contract.job.save()
    
    # Create notification for freelancer
    Notification.objects.create(
        recipient=contract.freelancer,
        notification_type='job_confirmed',
        title=f'Job Confirmed: "{contract.job.title}"',
        message=f'Your completion of the job "{contract.job.title}" has been confirmed. Payment of NRS{escrow_payment.amount} has been released to your wallet.',
        related_job=contract.job
    )
    
    # Create notification for client
    Notification.objects.create(
        recipient=request.user,
        notification_type='payment_released',
        title=f'Payment Released: "{contract.job.title}"',
        message=f'Payment of NRS{escrow_payment.amount} has been released to {contract.freelancer.username} for the completed job.',
        related_job=contract.job
    )
    
    messages.success(request, f'Job completion confirmed! Payment of NRS{escrow_payment.amount} has been released to the freelancer.')
    return redirect('jobs:contract_detail', contract_id=contract.id)

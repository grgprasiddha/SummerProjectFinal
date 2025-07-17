from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Job(models.Model):
    CATEGORY_CHOICES = (
        ('graphic-design', 'Graphic & Design'),
        ('digital-marketing', 'Digital Marketing'),
        ('writing-translation', 'Writing & Translation'),
        ('video-animation', 'Video & Animation'),
        ('programming', 'Programming & Tech'),
        ('business', 'Business'),
        ('lifestyle', 'Lifestyle'),
    )
    
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    image = models.ImageField(upload_to='job_images/', blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

class Proposal(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='proposals')
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proposals')
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cover_letter = models.TextField()
    estimated_days = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.freelancer.username} - {self.job.title}"
    
    class Meta:
        unique_together = ['job', 'freelancer']
        ordering = ['bid_amount']

class Contract(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed'),
    )
    
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name='contract')
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contracts')
    proposal = models.OneToOneField(Proposal, on_delete=models.CASCADE, related_name='contract')
    terms = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    completed_by_freelancer = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    confirmed_by_client = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Contract for {self.job.title}"

class Review(models.Model):
    contract = models.OneToOneField(Contract, on_delete=models.CASCADE, related_name='review')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.contract.job.title}"
    
    class Meta:
        unique_together = ['contract', 'reviewer']

class Dispute(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='disputes')
    payment = models.ForeignKey('payments.Payment', on_delete=models.SET_NULL, related_name='disputes', blank=True, null=True)
    raised_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disputes_raised')
    title = models.CharField(max_length=200)
    description = models.TextField()
    evidence = models.FileField(upload_to='dispute_evidence/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    resolution = models.TextField(blank=True, null=True)
    admin_decision = models.TextField(blank=True, null=True)
    decided_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='disputes_decided', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Dispute: {self.title}"

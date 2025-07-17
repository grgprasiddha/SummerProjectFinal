from django import forms
from .models import Job, Proposal, Contract, Dispute
from django.utils import timezone

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'category', 'budget', 'deadline', 'requirements', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_deadline(self):
        deadline = self.cleaned_data['deadline']
        if deadline < timezone.now().date():
            raise forms.ValidationError('Deadline cannot be in the past.')
        return deadline

class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['bid_amount', 'cover_letter', 'estimated_days']
        widgets = {
            'bid_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'cover_letter': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'estimated_days': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class DisputeForm(forms.ModelForm):
    class Meta:
        model = Dispute
        fields = ['title', 'description', 'evidence']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        } 
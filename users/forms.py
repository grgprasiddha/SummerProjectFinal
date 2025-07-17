from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    terms = forms.BooleanField(required=True, label="I agree to the Terms of Service and Privacy Policy.")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "terms")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, label='First Name')
    last_name = forms.CharField(max_length=30, required=False, label='Last Name')
    location = forms.CharField(max_length=200, required=False, label='Location')
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'bio', 'skills', 'hourly_rate', 'phone_number', 'address', 'website', 'profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            # Map location field to address field
            if self.instance and self.instance.address:
                self.fields['location'].initial = self.instance.address
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Save location to address field
        instance.address = self.cleaned_data.get('location', '')
        if commit:
            instance.save()
        return instance

class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

class UsernameChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username'] 
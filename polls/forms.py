from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth import get_user_model
from .models import PoliceUser, Election, Candidate, Position, ElectionPosition

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., President, Vice President, Secretary General',
                'required': True
            })
        }

class ElectionPositionForm(forms.ModelForm):
    position = forms.ModelChoiceField(queryset=Position.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    
    class Meta:
        model = ElectionPosition
        fields = ['position']

ElectionPositionFormSet = forms.inlineformset_factory(
    Election, ElectionPosition,
    form=ElectionPositionForm,
    extra=1,
    can_delete=True
)

class ElectionForm(forms.ModelForm):
    positions = forms.ModelMultipleChoiceField(
        queryset=Position.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select positions for this election"
    )
    
    class Meta:
        model = Election
        fields = ['title', 'description', 'start_time', 'end_time', 'eligible_ranks', 'eligible_stations']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'eligible_ranks': forms.TextInput(attrs={'placeholder': 'e.g. INSPECTOR, SP'}),
            'eligible_stations': forms.TextInput(attrs={'placeholder': 'e.g. Kampala, Central'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError('End time must be after start time.')
        return cleaned_data

    def save(self, commit=True):
        election = super().save(commit=False)
        if commit:
            election.save()
            election.positions.set(self.cleaned_data.get('positions', []))
        return election

class VoteForm(forms.Form):
    candidate = forms.ModelChoiceField(queryset=Candidate.objects.none(), widget=forms.RadioSelect, empty_label=None)

    def __init__(self, *args, **kwargs):
        election = kwargs.pop('election')
        super().__init__(*args, **kwargs)
        self.fields['candidate'].queryset = election.candidates.all()

class PoliceUserRegistrationForm(forms.ModelForm):
    force_number = forms.CharField(label='Force Number', max_length=50)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(), required=False)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(), required=False)

    class Meta:
        model = PoliceUser
        fields = ['username', 'email', 'first_name', 'last_name', 'force_number', 'rank', 'station', 'phone', 'role', 'is_active_voter']
        widgets = {
            'email': forms.EmailInput(attrs={'required': True}),
            'rank': forms.Select(choices=PoliceUser._meta.get_field('rank').choices),
        }

    def clean_force_number(self):
        force_number = self.cleaned_data.get('force_number')
        if self.instance.pk is None:
            if PoliceUser.objects.filter(force_number=force_number).exists():
                raise forms.ValidationError('Force number already registered.')
        return force_number

class PoliceUserEditForm(forms.ModelForm):
    class Meta:
        model = PoliceUser
        fields = ['username', 'email', 'first_name', 'last_name', 'force_number', 'rank', 'station', 'phone', 'role', 'is_active_voter', 'is_active', 'must_change_password']
        widgets = {
            'email': forms.EmailInput(attrs={'required': True}),
            'rank': forms.Select(choices=PoliceUser._meta.get_field('rank').choices),
        }

class PasswordResetForm(forms.Form):
    force_number = forms.CharField(label='Force Number', max_length=50)
    phone = forms.CharField(label='Registered Phone', max_length=15)
    
    def clean(self):
        cleaned_data = super().clean()
        force_number = cleaned_data.get('force_number')
        phone = cleaned_data.get('phone')
        try:
            user = PoliceUser.objects.get(force_number=force_number, phone=phone)
            cleaned_data['user'] = user
        except PoliceUser.DoesNotExist:
            raise forms.ValidationError('Force number and phone number do not match our records.')
        return cleaned_data

class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(label='New Password', widget=forms.PasswordInput(), min_length=8)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput())
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('new_password') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data


class PhoneLoginForm(forms.Form):
    phone = forms.CharField(label='Registered Phone', max_length=20)

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        try:
            user = PoliceUser.objects.get(phone=phone)
        except PoliceUser.DoesNotExist:
            raise forms.ValidationError('Phone number not found in our records.')
        if user.role != 'VOTER':
            raise forms.ValidationError('Only voters may use phone login.')
        return phone

class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(label='Current Password', widget=forms.PasswordInput())
    new_password = forms.CharField(label='New Password', widget=forms.PasswordInput(), min_length=8)
    confirm_password = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput())
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('new_password') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError('New passwords do not match.')
        if not self.user.check_password(cleaned_data.get('current_password')):
            raise forms.ValidationError('Current password is incorrect.')
        return cleaned_data


class AdminChangePasswordForm(forms.Form):
    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8,
        help_text='Minimum 8 characters.'
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    force_change = forms.BooleanField(
        label='Force password change on next login',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data


class BulkVoterUploadForm(forms.Form):
    file = forms.FileField(
        label='Upload File (CSV or Excel)',
        help_text='Supported formats: .csv, .xlsx',
        widget=forms.FileInput(attrs={'accept': '.csv,.xlsx'})
    )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            ext = file.name.lower().split('.')[-1]
            if ext not in ['csv', 'xlsx']:
                raise forms.ValidationError('Only CSV and Excel (.xlsx) files are supported.')
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                raise forms.ValidationError('File size must not exceed 10MB.')
        return file

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'force_number', 'rank', 'photo', 'biography', 'election', 'position']
        widgets = {
            'rank': forms.Select(choices=PoliceUser._meta.get_field('rank').choices),
            'biography': forms.Textarea(attrs={'rows': 3}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'election': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.FileInput(attrs={'accept': 'image/*'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default queryset for position - all positions
        self.fields['position'].queryset = Position.objects.all()
        
        # Ensure election field has proper queryset with positions prefetched
        self.fields['election'].queryset = Election.objects.all().prefetch_related('positions')

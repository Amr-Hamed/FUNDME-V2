from django import forms
from .models import UserProfile, ProjectDonations, ProjectComments
from django.contrib.auth.models import User

from .models import Project, ProjectPics, ProjectTags


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta():
        model = User
        fields = ('username', 'password', 'email')


class UserProfileInfoForm(forms.ModelForm):
    class Meta():
        model = UserProfile
        fields = ('portfolio_site', 'profile_pic')


def clean_email(self):
    data = self.cleaned_data['email']
    return data.lower()


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('category', 'title', 'start_date', 'end_date', 'total_target')


class ProjectPicsForm(forms.ModelForm):
    project_picture = forms.ImageField(required=False)

    class Meta:
        model = ProjectPics
        fields = ('project_picture',)


class ProjectTagsForm(forms.ModelForm):
    project_tag = forms.CharField(required=False)

    class Meta:
        model = ProjectTags
        fields = ('project_tag',)


class MakeDonationForm(forms.ModelForm):
    donation_amount = forms.IntegerField(required=True)

    class Meta:
        model = ProjectDonations
        fields = ('donation_amount',)


class AddCommentForm(forms.ModelForm):
    comment_body = forms.CharField(required=True)

    class Meta:
        model = ProjectComments
        fields = ('comment_reports',)

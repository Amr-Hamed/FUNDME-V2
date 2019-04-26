from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from .forms import UpdateProfile

from .forms import ProjectForm, ProjectPicsForm, ProjectTagsForm
from .forms import UserForm, UserProfileInfoForm, MakeDonationForm, AddCommentForm, ReportProjectForm, RateProjectForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .models import UserProfile, ProjectPics, Project, ProjectComments, ProjectDonations, ProjectRatings
from django.db.models import Sum, Avg


def index(request):
    return render(request, 'userProfile/index.html')


@login_required
def special(request):
    return HttpResponse("You are logged in !")


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'profile_pic' in request.FILES:
                print('found it')
                profile.profile_pic = request.FILES['profile_pic']
            profile.save()
            user.is_active = False
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('userProfile/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            to_email = user_form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
             #registered = True
            return HttpResponse('Please confirm your email address to complete the registration')

        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()
    return render(request, 'userProfile/registeration.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'registered': registered})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your account was inactive.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username, password))
            return HttpResponse("Invalid login details given")
    else:
        return render(request, 'userProfile/login.html', {})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = UserProfile.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, UserProfile.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        # return HttpResponseRedirect(reverse('index'))
        return HttpResponse('Activation link is invalid!')
    else:
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')


# create new project
@login_required
def create_project(request):
    if request.method == 'POST':
        project_form = ProjectForm(data=request.POST)
        project_pics_form = ProjectPicsForm(data=request.POST)
        project_tags_form = ProjectTagsForm(data=request.POST)
        if project_form.is_valid() and project_pics_form.is_valid() and project_tags_form.is_valid():
            project = project_form.save(commit=False)
            current_user = User.objects.get(id=request.user.id)
            # print(type(current_user))
            current_user_profile = UserProfile.objects.filter(user=current_user)
            # print(type(current_user_profile.first()))
            project.user = current_user_profile.first()
            project.save()
            if 'project_pictures' in request.FILES and request.FILES['project_pictures'] is not None:
                print(request.FILES.getlist('project_pictures')[0])
                for img in request.FILES.getlist('project_pictures'):
                    project_pic = ProjectPics()
                    project_pic.project = project
                    project_pic.project_picture = img
                    project_pic.save()
            project_tags = project_tags_form.save(commit=False)
            if 'project_tag' in request.POST and request.POST['project_tag'] is not "":
                project_tags.project = project
                project_tags.save()
            return render(request, 'userProfile/create_project.html', {
                'project_form': project_form,
                'project_pics_form': project_pics_form,
                'project_tags_form': project_tags_form,
                'errors': None
            })
        else:
            return render(request, 'userProfile/create_project.html', {
                'project_form': project_form,
                'errors': [project_form.errors, project_pics_form.errors, project_tags_form.errors]
            })
    else:
        project_form = ProjectForm()
        project_pics_form = ProjectPicsForm()
        project_tags_form = ProjectTagsForm()
    return render(request, 'userProfile/create_project.html', {
        'project_form': project_form,
        'project_pics_form': project_pics_form,
        'project_tags_form': project_tags_form,
        'errors': None
    })


# Show all projects
@login_required
def show_projects(request):
    projects = Project.objects.all
    return render(request, 'project/index.html', {'projects': projects})


@login_required
def get_donation_form(request, project, current_user_profile):
    donation_form = MakeDonationForm(data=request.POST)
    if donation_form.is_valid():
        donation = donation_form.save(commit=False)
        donation.project = project
        donation.user = current_user_profile.first()
        donation.save()
        donation_form = MakeDonationForm()
    return donation_form


@login_required
def get_comment_form(request, project, current_user_profile):
    comment_form = AddCommentForm(data=request.POST)
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.project = project
        comment.user = current_user_profile.first()
        comment.save()
        comment_form = AddCommentForm()
    return comment_form


@login_required
def get_report_form(request, project, current_user_profile):
    report_form = ReportProjectForm(data=request.POST)
    if report_form.is_valid():
        report = report_form.save(commit=False)
        report.project = project
        report.user = current_user_profile.first()
        report.save()
        report_form = ReportProjectForm()
    return report_form


@login_required
def get_rating_form(request, project, current_user_profile):
    rating_form = RateProjectForm(data=request.POST)
    if rating_form.is_valid():
        rate = rating_form.save(commit=False)
        rate.project = project
        rate.user = current_user_profile.first()
        rate.save()
        rating_form = RateProjectForm()
    return rating_form


# show a single project
@login_required
def show_a_project_details(request, id):
    project = get_object_or_404(Project, pk=id)
    comments = ProjectComments.objects.filter(project=project)
    pictures = ProjectPics.objects.filter(project=project)
    total_donations = ProjectDonations.objects.filter(project=project).aggregate(Sum("donation_amount"))
    average_rating = ProjectRatings.objects.filter(project=project).aggregate(Avg("user_rating"))

    return [project, comments, pictures, total_donations, average_rating]


@login_required
def show_a_project(request, id):
    project_details = show_a_project_details(request, id)
    current_user = User.objects.get(id=request.user.id)
    current_user_profile = UserProfile.objects.filter(user=current_user)
    donation_form = get_donation_form(request, project_details[0], current_user_profile)
    comment_form = get_comment_form(request, project_details[0], current_user_profile)
    report_form = get_report_form(request, project_details[0], current_user_profile)
    rating_form = get_rating_form(request, project_details[0], current_user_profile)

    return render(request, 'project/project.html', {
        'project': project_details[0],
        'donation_form': donation_form,
        'comment_form': comment_form,
        'report_form': report_form,
        'comments': project_details[1],
        'pictures': project_details[3],
        'total_donation': project_details[3],
        'rate_project': rating_form,
        'average_rating': project_details[4]
    })


def get_user_profile(request, username):
    user = User.objects.get(username=username)
    userprofile = UserProfile.objects.get(user=user)
    return render(request, 'userProfile/user_profile.html', {"user":user, "userprofile":userprofile})


def update_user_profile(request, username):
    user = User.objects.get(username=username)
    userprofile = UserProfile.objects.get(user=user)
    if request.method == 'POST':
        form = UpdateProfile(request.POST, instance=userprofile)
        if form.is_valid():
            updated= form.save(commit=False)
            updated.save()
            return render(request, 'userProfile/user_profile.html', {"user": user, "userprofile": userprofile})
    else:
        form = UpdateProfile(request.POST, instance=userprofile)

    context = {
        "form": form
    }
    return render(request, 'userProfile/update_user_profile.html', context)

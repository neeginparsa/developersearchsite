from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, ProfileForm, SkillForm
from django.contrib.auth.models import User
from .models import Profile, Skill
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage



def LoginUser(request):

    page = 'login'

    if request.user.is_authenticated:
        return redirect('profiles')


    if request.method == 'POST':
        username = request.POST['username'].lower()
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'username not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(request.GET['next']if 'next' in request.GET else 'account')
        else:
            messages.error(request, 'username or password incorect')

    return render(request, 'users/login-register.html', )

def LogoutUser(request):
    logout(request)
    messages.error(request, 'user logged out')
    return redirect('login')

def RegisterUser(request):
    page = 'register'
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            #2 khat payiin baraye tabdil matn karbar be lowercase va sepas save
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            messages.success(request, 'account was created')

            login(request, user)
            messages.success(request, 'complete your profile!!')
            return redirect('edit-account')

        else:
            messages.error(request, 'an error has accurred during registration')
    context = {'page': page, 'form': form}
    return render(request, 'users/login-register.html', context)

def Profiles(request):
    search_query = ''

    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')

    skills = Skill.objects.filter(name__icontains=search_query)
    profiles = Profile.objects.distinct().filter(Q(name__icontains=search_query) |
                                      Q(short_intro__icontains=search_query) |
                                      Q(skill__in=skills))


    # pagination
    page = request.GET.get('page')
    results = 3
    paginator = Paginator(profiles, results)
    try:
        profiles = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        profiles = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        profiles = paginator.page(page)

    leftIndex = (int(page) - 4)
    if leftIndex < 1:
        leftIndex = 1
    rightIndex = (int(page) + 5)
    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages + 1

    custom_range = range(leftIndex, rightIndex)

    context = {'profiles': profiles, 'search_query': search_query, 'paginator': paginator, 'custom_range': custom_range}
    return render(request, 'users/profiles.html', context)



def userProfile(request, pk):
    profile = Profile.objects.get(id=pk)
    topskill = profile.skill_set.exclude(description__exact="")
    otherskill = profile.skill_set.filter(description="")

    context = {'profile': profile, 'topskill': topskill, 'otherskill': otherskill}
    return render(request, 'users/user-profile.html', context)



@login_required(login_url='login')
def userAccount(request):
    profile = request.user.profile

    skills = profile.skill_set.all()
    projects = profile.project_set.all()

    context = {'profile': profile, 'skills': skills, 'projects':projects}
    return render(request, 'users/account.html', context)


@login_required(login_url='login')
def editAccount(request):
    profile = request.user.profile
    form = ProfileForm(instance=profile)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('account')

    context = {'form': form}
    return render(request, 'users/profile-form.html', context)


@login_required(login_url='login')
def createSkill(request):
    profile = request.user.profile
    form = SkillForm()

    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = profile
            skill.save()
            messages.success(request, 'skill was added successfully ')

            return redirect('account')

    context = {'form': form}
    return render(request, 'users/skill_form.html', context)


@login_required(login_url='login')
def updateSkill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    form = SkillForm(instance=skill)
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'skill was updated successfully')
            return redirect('account')

    context = {'form': form}
    return render(request, 'users/skill_form.html', context)


@login_required(login_url='login')
def deleteSkill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    if request.method == 'POST':
        skill.delete()
        messages.success(request, 'skill was deleted successfully')
        return redirect('account')

    context = {'object': skill}
    return render(request, 'delete_obj.html', context)

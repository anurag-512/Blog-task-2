from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from .forms import PatientSignupForm, DoctorSignupForm
from .models import Patient, Doctor, BlogPost, Category
from .forms import BlogPostForm
from django.contrib.auth.decorators import login_required

def signup(request):
    if request.method == 'POST':
        form_type = request.POST.get('user_type')
        if form_type == 'patient':
            form = PatientSignupForm(request.POST, request.FILES)
        elif form_type == 'doctor':
            form = DoctorSignupForm(request.POST, request.FILES)
        else:
            form = None
        if form is not None and form.is_valid():
            user = form.save(commit=False)
            if form_type == 'patient':
                user.is_patient = True
            elif form_type == 'doctor':
                user.is_doctor = True
            user.save()
            profile = None
            if user.is_patient:
                profile = Patient(user=user, address=form.cleaned_data['address'], profile_picture=form.cleaned_data['profile_picture'])
            elif user.is_doctor:
                profile = Doctor(user=user, address=form.cleaned_data['address'], profile_picture=form.cleaned_data['profile_picture'])
            profile.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = PatientSignupForm()
    return render(request, 'index.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_doctor:
                return redirect('view_own_blog_posts')
            elif user.is_patient:
                return redirect('view_blog_posts')
            # return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def dashboard(request):
    profile = None
    if request.user.is_patient:
        profile = Patient.objects.get(user=request.user)
    elif request.user.is_doctor:
        profile = Doctor.objects.get(user=request.user)
    
    if profile is None:
        return redirect('some_default_view')
    
    return render(request, 'dashboard.html', {'profile': profile})

@login_required
def create_blog_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.author = request.user
            blog_post.save()
            return redirect('view_own_blog_posts')
    else:
        form = BlogPostForm()
    return render(request, 'create_blog_post.html', {'form': form})

@login_required
def view_own_blog_posts(request):
    blog_posts = BlogPost.objects.filter(author=request.user)
    return render(request, 'view_own_blog_posts.html', {'blog_posts': blog_posts})

def view_blog_posts(request):
    categories = Category.objects.all()
    blog_posts = BlogPost.objects.filter(is_draft=False)
    return render(request, 'view_blog_posts.html', {'categories': categories, 'blog_posts': blog_posts})

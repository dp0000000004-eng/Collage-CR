from django.shortcuts import render, redirect, get_object_or_404
from .models import Students, Profile
from .forms import StudentForm, UsernameChangeForm, StyledPasswordChangeForm
from datetime import date
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required

# Create your views here.

def home_view(request):

    return render(request, 'home.html')

def student_view(request):

    students = Students.objects.all()

    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("students")
        else:
            form = StudentForm()

    return render(request, "students.html", {"students":students, "form":StudentForm(request.POST, request.FILES)})


@login_required
def record_view(request, student_id):

    student_data = Students.objects.get(id=student_id)

    today = date.today()
    year, month = today.year, today.month   

    att_data = student_data.monthly_attendance_percentage(year, month)
    att_log = student_data.present_logs(year, month)


    return render(request, 'student_data.html', {
        "student_data": student_data,
        "att_data":att_data,
        "att_log":att_log
    })

def create_user(request):
    if request.method == "POST":
        try:
            username = request.POST.get("username")
            email = request.POST.get("email")
            raw_password = request.POST.get("password")
            user = User(username=username, email=email)
            user.set_password(raw_password)
            user.save()
            return redirect("students")
        except IntegrityError:
            messages.info(request, message="IN The Same Credentials Account Already exist! ")
    else:
        messages.error(request, message="Something went wrong :(")
    
    return render(request, "create_user.html")



def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("students")
        else:
            messages.error(request, message="Invalid Credentials")
    
    return render(request, "login.html" )

def logout_view(request):
    logout(request)
    return redirect("students")


@login_required
def profile_view(request):
    username_form = UsernameChangeForm(user=request.user)
    password_form = StyledPasswordChangeForm(user=request.user)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "username":
            username_form = UsernameChangeForm(request.user, request.POST)
            if username_form.is_valid():
                username_form.save()
                messages.success(request, "Username updated successfully.")
                return redirect("profile")

        elif action == "password":
            password_form = StyledPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated successfully.")
                return redirect("profile")

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = None

    return render(request, "profile.html", {
        "username_form": username_form,
        "password_form": password_form,
        "profile": profile,
    })


@login_required
def delete(request, prof_id):
    user = get_object_or_404(User, id=prof_id)
    user.delete()

    return redirect("home")

@login_required
def delete_student(request, student_id):
    student = get_object_or_404(Students, id=student_id)
    student.delete()

    return redirect("home")
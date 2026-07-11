from django.shortcuts import render, redirect
from .models import Students
from .forms import StudentForm
from datetime import date
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
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
        username = request.POST.get("username")
        email = request.POST.get("email")
        raw_password = request.POST.get("password")
        user = User(username=username, email=email)
        user.set_password(raw_password)
        user.save()
        return redirect("students")
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
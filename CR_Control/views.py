from django.shortcuts import render, redirect
from .models import Students, Attendance
from .forms import StudentForm
from datetime import date

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
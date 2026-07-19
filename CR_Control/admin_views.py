from datetime import date

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.dateparse import parse_date

from .decorators import staff_or_teacher_required
from .forms import StudentForm, BranchForm, SubjectForm
from .models import (
    Students, Branch, Subject, AcademicSession, Attendance, Profile,
)


@staff_or_teacher_required
def panel_dashboard(request):
    today = date.today()
    return render(request, "panel/dashboard.html", {
        "student_count": Students.objects.count(),
        "branch_count": Branch.objects.count(),
        "subject_count": Subject.objects.count(),
        "sessions_today": AcademicSession.objects.filter(date=today).count(),
        "recent_sessions": AcademicSession.objects.select_related(
            "branch", "subject", "marked_by"
        )[:8],
    })


@staff_or_teacher_required
def panel_mark_attendance(request):
    branches = Branch.objects.all()
    branch_id = request.GET.get("branch") or request.POST.get("branch")
    subject_id = request.GET.get("subject") or request.POST.get("subject")
    date_str = request.GET.get("date") or request.POST.get("date") or date.today().isoformat()
    session_date = parse_date(date_str) or date.today()

    subjects = Subject.objects.filter(branch_id=branch_id) if branch_id else Subject.objects.none()
    students = []
    attendance_map = {}
    branch = None
    subject = None

    if branch_id and subject_id:
        branch = get_object_or_404(Branch, pk=branch_id)
        subject = get_object_or_404(Subject, pk=subject_id)
        students = Students.objects.filter(branch=branch)

        if request.method == "POST" and request.POST.get("action") == "save_attendance":
            session, _ = AcademicSession.objects.get_or_create(
                branch=branch,
                subject=subject,
                date=session_date,
                defaults={"marked_by": request.user},
            )
            if not session.marked_by:
                session.marked_by = request.user
                session.save(update_fields=["marked_by"])

            for student in students:
                status = (
                    Attendance.PRESENT
                    if request.POST.get(f"student_{student.id}") == Attendance.PRESENT
                    else Attendance.ABSENT
                )
                Attendance.objects.update_or_create(
                    session=session,
                    student=student,
                    defaults={"status": status},
                )

            messages.success(request, f"Attendance saved for {subject.code} on {session_date}.")
            return redirect(
                f"{reverse('panel_attendance')}?branch={branch_id}&subject={subject_id}&date={session_date.isoformat()}"
            )

        session = AcademicSession.objects.filter(
            branch=branch, subject=subject, date=session_date
        ).first()
        if session:
            attendance_map = {
                rec.student_id: rec.status
                for rec in session.records.all()
            }

    students_with_status = [
        {
            "student": s,
            "is_present": attendance_map.get(s.id, Attendance.PRESENT) == Attendance.PRESENT,
        }
        for s in students
    ]

    return render(request, "panel/mark_attendance.html", {
        "branches": branches,
        "subjects": subjects,
        "branch_id": branch_id,
        "subject_id": subject_id,
        "session_date": session_date,
        "students_with_status": students_with_status,
        "branch": branch,
        "subject": subject,
    })


@staff_or_teacher_required
def panel_students(request):
    form = StudentForm()

    if request.method == "POST" and request.POST.get("action") == "add_student":
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Student added successfully.")
            return redirect("panel_students")

    return render(request, "panel/students.html", {
        "students": Students.objects.select_related("branch"),
        "form": form,
    })


@staff_or_teacher_required
def panel_student_edit(request, student_id):
    student = get_object_or_404(Students, pk=student_id)

    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student updated successfully.")
            return redirect("panel_students")
    else:
        form = StudentForm(instance=student)

    return render(request, "panel/student_edit.html", {
        "form": form,
        "student": student,
    })


@staff_or_teacher_required
def panel_student_delete(request, student_id):
    student = get_object_or_404(Students, pk=student_id)
    if request.method == "POST":
        name = student.name
        student.delete()
        messages.success(request, f"Deleted student {name}.")
        return redirect("panel_students")
    return redirect("panel_students")


@staff_or_teacher_required
def panel_branches(request):
    form = BranchForm()

    if request.method == "POST" and request.POST.get("action") == "add_branch":
        form = BranchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Branch added successfully.")
            return redirect("panel_branches")

    return render(request, "panel/branches.html", {
        "branches": Branch.objects.all(),
        "form": form,
    })


@staff_or_teacher_required
def panel_branch_delete(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id)
    if request.method == "POST":
        name = str(branch)
        branch.delete()
        messages.success(request, f"Deleted branch {name}.")
        return redirect("panel_branches")
    return redirect("panel_branches")


@staff_or_teacher_required
def panel_subjects(request):
    form = SubjectForm()

    if request.method == "POST" and request.POST.get("action") == "add_subject":
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Subject added successfully.")
            return redirect("panel_subjects")

    return render(request, "panel/subjects.html", {
        "subjects": Subject.objects.select_related("branch"),
        "form": form,
    })


@staff_or_teacher_required
def panel_subject_delete(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    if request.method == "POST":
        name = str(subject)
        subject.delete()
        messages.success(request, f"Deleted subject {name}.")
        return redirect("panel_subjects")
    return redirect("panel_subjects")


@staff_or_teacher_required
def panel_sessions(request):
    sessions = AcademicSession.objects.select_related("branch", "subject", "marked_by")
    return render(request, "panel/sessions.html", {"sessions": sessions})


@staff_or_teacher_required
def panel_session_delete(request, session_id):
    session = get_object_or_404(AcademicSession, pk=session_id)
    if request.method == "POST":
        label = str(session)
        session.delete()
        messages.success(request, f"Deleted session {label}.")
        return redirect("panel_sessions")
    return redirect("panel_sessions")

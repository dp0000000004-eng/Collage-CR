from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

# Create your models here.


class Branch(models.Model):
    semester = models.IntegerField()
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=12)

    def __str__(self):
        return f"{self.name} {self.code}"

class Profile(models.Model):
    CR = 'CR'
    PROF = 'PROF'
    STUDENT = 'STUDENT'
    ROLE_CHOICES = [(CR, 'Class Representative'), (PROF, 'Professor'), (STUDENT, 'Student')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="profiles", null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} — {self.role}"





class Students(models.Model):
    name = models.CharField(max_length=64)
    regd_no = models.CharField(max_length=12)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="st_branch")
    email = models.EmailField()
    phone_no = models.IntegerField(
        validators=[
            MinValueValidator(10),
            MaxValueValidator(9999999999)
            ]
    )
    image = models.ImageField(upload_to='student_img')

    def __str__(self):
        return f"{self.name}{self.regd_no} {self.branch} {self.email} {self.phone_no}"
    

    def monthly_attendance_percentage(self, year, month, subject=None):
        """Attendance % for this student for a given month. Optionally filter by subject."""
        records = self.attendance_records.filter(
            session__date__year=year,
            session__date__month=month,
        )
        if subject:
            records = records.filter(session__subject=subject)

        total = records.count()
        if total == 0:
            return None 

        present = records.filter(status=Attendance.PRESENT).count()
        return round((present / total) * 100, 2)
    
    def present_logs(self, year=None, month=None, subject=None):
        """Return all attendance records where student was Present."""
        records = self.attendance_records.filter(status=Attendance.PRESENT)

        if year:
            records = records.filter(session__date__year=year)
        if month:
            records = records.filter(session__date__month=month)
        if subject:
            records = records.filter(session__subject=subject)

        return records


    class Meta:
        ordering = ['regd_no']
    

class Subject(models.Model):
    code = models.CharField(max_length=10)       
    name = models.CharField(max_length=100)       
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="subjects")
    semester = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('branch', 'semester', 'code')

    def __str__(self):
        return f"{self.code} - {self.name} ({self.branch.code} Sem {self.semester})"


class AcademicSession(models.Model):
    """One row per (branch, subject, date) — a CR takes attendance once per subject per day"""
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="sessions")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="sessions")
    date = models.DateField()
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('branch', 'subject', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.subject.code} — {self.branch.code} — {self.date}"


class Attendance(models.Model):
    PRESENT = 'P'
    ABSENT = 'A'
    STATUS_CHOICES = [(PRESENT, 'Present'), (ABSENT, 'Absent')]

    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name="records")
    student = models.ForeignKey(Students, on_delete=models.CASCADE, related_name="attendance_records")
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=ABSENT)

    class Meta:
        unique_together = ('session', 'student')

    def __str__(self):
        return f"{self.student.regd_no} — {self.session.subject.code} — {self.session.date} — {self.get_status_display()}"
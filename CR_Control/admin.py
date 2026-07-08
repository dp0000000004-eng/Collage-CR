from django.contrib import admin
from .models import Branch, Students, Profile, Subject, AcademicSession, Attendance

# Register your models here.

admin.site.register(Branch)
admin.site.register(Profile)
admin.site.register(Subject)
admin.site.register(AcademicSession)
admin.site.register(Attendance)

@admin.register(Students)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'regd_no', 'branch', 'current_month_attendance')

    def current_month_attendance(self, obj):
        from datetime import date
        today = date.today()
        pct = obj.monthly_attendance_percentage(today.year, today.month)
        return f"{pct}%" if pct is not None else "No data"
    current_month_attendance.short_description = "This Month %"
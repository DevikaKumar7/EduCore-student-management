from django.contrib import admin
from .models import Student, Attendance, Task, LeaveRequest


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display  = ('title', 'student', 'priority', 'status', 'due_date', 'assigned_on')
    list_filter   = ('priority', 'status')
    search_fields = ('title', 'student__user__first_name', 'student__user__last_name')


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display  = ('student', 'leave_type', 'from_date', 'to_date', 'status', 'applied_on')
    list_filter   = ('status', 'leave_type')
    search_fields = ('student__user__first_name', 'student__user__last_name')


admin.site.register(Student)
admin.site.register(Attendance)
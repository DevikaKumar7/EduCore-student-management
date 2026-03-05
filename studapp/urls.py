from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('',                    views.user_login,       name='login'),
    path('register/',           views.student_register, name='student_register'),
    # admin registration is disabled for normal users - admins should be created by the superuser
    # path('admin/register/',     views.admin_register,   name='admin_register'),
    path('logout/',             views.user_logout,      name='logout'),
    path('dashboard/',          views.dashboard,        name='dashboard'),

    # Admin
    path('admin-dashboard/',                    views.admin_dashboard,   name='admin_dashboard'),
    path('students/',                           views.student_list,      name='student_list'),
    path('students/add/',                       views.add_student,       name='add_student'),
    path('students/<int:student_id>/',          views.student_detail,    name='student_detail'),
    path('attendance/mark/',                    views.mark_attendance,   name='mark_attendance'),
    path('attendance/report/',                  views.attendance_report, name='attendance_report'),
    path('tasks/',                              views.task_list,         name='task_list'),
    path('tasks/assign/',                       views.assign_task,       name='assign_task'),
    path('tasks/<int:task_id>/edit/',           views.edit_task,         name='edit_task'),
    path('tasks/<int:task_id>/delete/',         views.delete_task,       name='delete_task'),
    path('tasks/<int:task_id>/submission/',     views.view_submission,   name='view_submission'),
    path('students/<int:student_id>/tasks/',    views.student_tasks,     name='student_tasks'),
    path('leaves/',                             views.leave_list,        name='leave_list'),
    path('leaves/<int:leave_id>/action/',       views.leave_action,      name='leave_action'),
    path('announcements/',                      views.admin_announcements, name='admin_announcements'),

    # Student Portal
    path('student/dashboard/',                  views.student_dashboard,     name='student_dashboard'),
    path('student/tasks/',                      views.student_my_tasks,      name='student_my_tasks'),
    path('student/tasks/<int:task_id>/submit/', views.student_submit_task,   name='student_submit_task'),
    path('student/leaves/apply/',               views.student_apply_leave,   name='student_apply_leave'),
    path('student/leaves/',                     views.student_my_leaves,     name='student_my_leaves'),
    path('student/attendance/',                 views.student_attendance,    name='student_attendance'),
    path('student/announcements/',              views.student_announcements, name='student_announcements'),
]

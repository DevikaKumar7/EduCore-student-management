from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from functools import wraps

from .models import Student, Attendance, Task, TaskSubmission, LeaveRequest, Announcement


# ── Decorators ────────────────────────────────────────────────────────────────

def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if Student.objects.filter(user=request.user).exists() or not request.user.is_staff:
            messages.error(request, "Admin access required.")
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper


def student_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            request.student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            messages.error(request, "Student access required.")
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper


# ── Auth ──────────────────────────────────────────────────────────────────────

def user_login(request):
    print("Login attempt:", request.method)   
    if request.method == 'POST':
        print("Form data:", request.POST)
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_staff or user.is_superuser:
                return redirect('admin_dashboard')
            elif Student.objects.filter(user=user).exists():
                return redirect('student_dashboard')
            else:
                logout(request)
                return render(request, 'login.html', {'error': 'No role assigned.'})
        return render(request, 'login.html', {'error': 'Invalid credentials.'})
    return render(request, 'login.html')


def student_register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name',  '').strip()
        username   = request.POST.get('username',   '').strip()
        email      = request.POST.get('email',      '').strip()
        password   = request.POST.get('password',   '')
        password2  = request.POST.get('password2',  '')
        age        = request.POST.get('age',        '').strip()
        gender     = request.POST.get('gender',     '').strip()
        course     = request.POST.get('course',     '').strip()
        phone      = request.POST.get('phone',      '').strip()
        address    = request.POST.get('address',    '').strip()

        errors = []
        if not first_name:        errors.append('First name is required.')
        if not last_name:         errors.append('Last name is required.')
        if not username:          errors.append('Username is required.')
        if ' ' in username:       errors.append('Username cannot have spaces.')
        if not password:          errors.append('Password is required.')
        if len(password) < 8:     errors.append('Password must be at least 8 characters.')
        if password != password2: errors.append('Passwords do not match.')
        if not age:               errors.append('Age is required.')
        if not gender:            errors.append('Gender is required.')
        if not course:            errors.append('Course is required.')
        if not phone:             errors.append('Phone is required.')
        if username and User.objects.filter(username=username).exists():
            errors.append(f'Username "{username}" is already taken.')

        if errors:
            return render(request, 'student_register.html', {'errors': errors, 'data': request.POST})

        user = User.objects.create_user(
            username=username, password=password,
            first_name=first_name, last_name=last_name,
            email=email, is_staff=False,
        )
        Student.objects.create(user=user, age=int(age), gender=gender,
                               course=course, phone=phone, address=address)
        messages.success(request, 'Registration successful! Please login.')
        return redirect('login')

    return render(request, 'student_register.html')


# Admin registration is no longer publicly available.  Only a superuser/root user
# should create additional admin accounts (via the Django admin site or manage.py).
# If someone does hit this view without being logged in as superuser, redirect to login.

def admin_register(request):
    # this view is intentionally restricted; we keep it around for possible
    # superuser-driven use but prevent normal access.
    if not request.user.is_authenticated or not request.user.is_superuser:
        # silently redirect non-superusers back to login (could 403 if preferred)
        return redirect('login')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name',  '').strip()
        username   = request.POST.get('username',   '').strip()
        email      = request.POST.get('email',      '').strip()
        password   = request.POST.get('password',   '')
        password2  = request.POST.get('password2',  '')
        department = request.POST.get('department', '').strip()

        errors = []
        if not first_name:        errors.append('First name is required.')
        if not last_name:         errors.append('Last name is required.')
        if not username:          errors.append('Username is required.')
        if ' ' in username:       errors.append('Username cannot have spaces.')
        if not password:          errors.append('Password is required.')
        if len(password) < 8:     errors.append('Password must be at least 8 characters.')
        if password != password2: errors.append('Passwords do not match.')
        if not department:        errors.append('Department is required.')
        if username and User.objects.filter(username=username).exists():
            errors.append(f'Username "{username}" is already taken.')

        if errors:
            return render(request, 'admin_register.html', {'errors': errors, 'data': request.POST})

        user = User.objects.create_user(
            username=username, password=password,
            first_name=first_name, last_name=last_name,
            email=email, is_staff=True, is_superuser=False,
        )
        messages.success(request, 'Admin registration successful! Please login.')
        return redirect('login')

    return render(request, 'admin_register.html')


def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    elif Student.objects.filter(user=request.user).exists():
        return redirect('student_dashboard')
    return redirect('login')


# ── STUDENT PORTAL ────────────────────────────────────────────────────────────

@student_required
def student_dashboard(request):
    student = request.student
    tasks   = Task.objects.filter(student=student)
    leaves  = LeaveRequest.objects.filter(student=student)
    submitted_ids = list(TaskSubmission.objects.filter(student=student).values_list('task_id', flat=True))
    announcements = Announcement.objects.filter(is_active=True).filter(
        Q(target='all') | Q(target='specific_course', target_course=student.course))[:5]
    return render(request, 'student_dashboard.html', {
        'student':         student,
        'total_tasks':     tasks.count(),
        'pending_tasks':   tasks.filter(status='Pending').count(),
        'completed_tasks': tasks.filter(status='Completed').count(),
        'total_leaves':    leaves.count(),
        'pending_leaves':  leaves.filter(status='Pending').count(),
        'approved_leaves': leaves.filter(status='Approved').count(),
        'recent_tasks':    tasks[:4],
        'recent_leaves':   leaves[:3],
        'announcements':   announcements,
        'attendance_pct':  student.attendance_percentage(),
        'present_count':   student.present_count(),
        'absent_count':    student.absent_count(),
        'total_classes':   student.total_classes(),
        'submitted_ids':   submitted_ids,
    })


@student_required
def student_my_tasks(request):
    student = request.student
    tasks   = Task.objects.filter(student=student)
    submitted_ids = list(TaskSubmission.objects.filter(student=student).values_list('task_id', flat=True))
    return render(request, 'student_my_tasks.html', {
        'student':       student,
        'tasks':         tasks,
        'submitted_ids': submitted_ids,
        'pending':       tasks.filter(status='Pending').count(),
        'progress':      tasks.filter(status='In Progress').count(),
        'completed':     tasks.filter(status='Completed').count(),
    })


@student_required
def student_submit_task(request, task_id):
    student = request.student
    task    = get_object_or_404(Task, id=task_id, student=student)

    if hasattr(task, 'submission'):
        messages.warning(request, 'You already submitted this task.')
        return redirect('student_my_tasks')

    if request.method == 'POST':
        file = request.FILES.get('file')
        note = request.POST.get('note', '').strip()
        if not file:
            messages.error(request, 'Please choose a file to upload.')
        else:
            TaskSubmission.objects.create(task=task, student=student, file=file, note=note)
            task.status = 'Completed'
            task.save()
            messages.success(request, f'Task "{task.title}" submitted successfully!')
            return redirect('student_my_tasks')

    return render(request, 'student_submit_task.html', {'student': student, 'task': task})


@student_required
def student_apply_leave(request):
    student = request.student
    if request.method == 'POST':
        leave_type = request.POST.get('leave_type', 'Personal')
        from_date  = request.POST.get('from_date')
        to_date    = request.POST.get('to_date')
        reason     = request.POST.get('reason', '').strip()
        errors = []
        if not from_date: errors.append('From date is required.')
        if not to_date:   errors.append('To date is required.')
        if not reason:    errors.append('Reason is required.')
        if from_date and to_date and from_date > to_date:
            errors.append('From date cannot be after To date.')
        if errors:
            messages.error(request, ' '.join(errors))
        else:
            LeaveRequest.objects.create(student=student, leave_type=leave_type,
                                        from_date=from_date, to_date=to_date, reason=reason)
            messages.success(request, 'Leave request submitted! Awaiting admin approval.')
            return redirect('student_my_leaves')
    return render(request, 'student_apply_leave.html', {'student': student})


@student_required
def student_my_leaves(request):
    student = request.student
    leaves  = LeaveRequest.objects.filter(student=student)
    return render(request, 'student_my_leaves.html', {
        'student':  student,
        'leaves':   leaves,
        'pending':  leaves.filter(status='Pending').count(),
        'approved': leaves.filter(status='Approved').count(),
        'rejected': leaves.filter(status='Rejected').count(),
    })


@student_required
def student_attendance(request):
    student    = request.student
    attendance = Attendance.objects.filter(student=student).order_by('-date')
    return render(request, 'student_attendance.html', {
        'student':    student,
        'attendance': attendance,
        'present':    student.present_count(),
        'absent':     student.absent_count(),
        'total':      student.total_classes(),
        'pct':        student.attendance_percentage(),
    })


@student_required
def student_announcements(request):
    student = request.student
    announcements = Announcement.objects.filter(is_active=True).filter(
        Q(target='all') | Q(target='specific_course', target_course=student.course))
    return render(request, 'student_announcements.html', {
        'student': student, 'announcements': announcements})


# ── ADMIN ─────────────────────────────────────────────────────────────────────

@admin_required
def admin_dashboard(request):
    today    = timezone.now().date()
    students = Student.objects.select_related('user').all()
    total_students = students.count()
    courses        = students.values('course').distinct().count()
    today_records  = Attendance.objects.filter(date=today)
    today_present  = today_records.filter(status='Present').count()
    today_absent   = today_records.filter(status='Absent').count()
    today_marked   = today_records.count()
    today_unmarked = total_students - today_marked
    total_records  = Attendance.objects.count()
    total_present  = Attendance.objects.filter(status='Present').count()
    overall_pct    = round((total_present / total_records * 100), 1) if total_records else 0
    stats = {
        'total_students': total_students, 'total_courses': courses,
        'today_present':  today_present,  'today_absent':  today_absent,
        'today_unmarked': today_unmarked, 'today_marked':  today_marked,
        'overall_pct':    overall_pct,
        'pending_leaves': LeaveRequest.objects.filter(status='Pending').count(),
        'total_tasks':    Task.objects.count(),
    }
    recent_students = [{'obj': s, 'attendance': s.attendance_percentage(),
        'present': s.present_count(), 'total': s.total_classes(), 'initials': _initials(str(s))}
        for s in students.order_by('-id')[:6]]
    recent_activity = Attendance.objects.select_related('student__user').order_by('-id')[:8]
    return render(request, 'dashboard.html', {
        'stats': stats, 'recent_students': recent_students, 'recent_activity': recent_activity,
        'today': today, 'admin_name': request.user.get_full_name() or request.user.username,
        'admin_initials': _initials(request.user.get_full_name() or request.user.username),
        'form_error':    request.session.pop('form_error', ''),
        'form_data':     request.session.pop('form_data', {}),
        'student_added': request.session.pop('student_added', False),
    })


@admin_required
def add_student(request):
    if request.method != 'POST':
        return redirect('admin_dashboard')
    first_name = request.POST.get('first_name','').strip()
    last_name  = request.POST.get('last_name','').strip()
    username   = request.POST.get('username','').strip()
    email      = request.POST.get('email','').strip()
    password   = request.POST.get('password','')
    password2  = request.POST.get('password2','')
    age        = request.POST.get('age','').strip()
    gender     = request.POST.get('gender','').strip()
    course     = request.POST.get('course','').strip()
    phone      = request.POST.get('phone','').strip()
    address    = request.POST.get('address','').strip()
    form_data  = {'first_name':first_name,'last_name':last_name,'username':username,
                  'email':email,'age':age,'gender':gender,'course':course,'phone':phone,'address':address}
    errors = []
    if not first_name:        errors.append('First name is required.')
    if not last_name:         errors.append('Last name is required.')
    if not username:          errors.append('Username is required.')
    if ' ' in username:       errors.append('Username cannot contain spaces.')
    if not password:          errors.append('Password is required.')
    if len(password) < 8:     errors.append('Password must be at least 8 characters.')
    if password != password2: errors.append('Passwords do not match.')
    if not age:               errors.append('Age is required.')
    if not gender:            errors.append('Gender is required.')
    if not course:            errors.append('Course is required.')
    if not phone:             errors.append('Phone number is required.')
    if username and User.objects.filter(username=username).exists():
        errors.append(f'Username "{username}" is already taken.')
    if errors:
        request.session['form_error'] = ' '.join(errors)
        request.session['form_data']  = form_data
        return redirect('admin_dashboard')
    try:
        user = User.objects.create_user(username=username, password=password,
            first_name=first_name, last_name=last_name, email=email, is_staff=False)
        Student.objects.create(user=user, age=int(age), gender=gender,
            course=course, phone=phone, address=address)
        messages.success(request, f'Student "{first_name} {last_name}" added successfully!')
        request.session['student_added'] = True
    except Exception as e:
        request.session['form_error'] = f'An error occurred: {str(e)}'
        request.session['form_data']  = form_data
    return redirect('admin_dashboard')


@admin_required
def student_list(request):
    query    = request.GET.get('q','').strip()
    course   = request.GET.get('course','').strip()
    students = Student.objects.select_related('user').all()
    if query:
        students = students.filter(Q(user__first_name__icontains=query)|
            Q(user__last_name__icontains=query)|Q(user__username__icontains=query))
    if course:
        students = students.filter(course__icontains=course)
    student_data = [{'obj':s,'attendance':s.attendance_percentage(),'present':s.present_count(),
        'absent':s.absent_count(),'total':s.total_classes(),'initials':_initials(str(s))}
        for s in students.order_by('user__first_name')]
    courses = Student.objects.values_list('course', flat=True).distinct()
    return render(request, 'student_list.html', {'student_data':student_data,
        'courses':courses,'query':query,'course':course})


@admin_required
def student_detail(request, student_id):
    student    = get_object_or_404(Student, id=student_id)
    attendance = Attendance.objects.filter(student=student).order_by('-date')
    return render(request, 'student_detail.html', {'student':student,'attendance':attendance,
        'present':student.present_count(),'absent':student.absent_count(),
        'total':student.total_classes(),'pct':student.attendance_percentage(),
        'initials':_initials(str(student))})


@admin_required
def mark_attendance(request):
    today    = timezone.now().date()
    students = Student.objects.select_related('user').order_by('user__first_name')
    if request.method == 'POST':
        saved = 0
        for student in students:
            status = request.POST.get(f'status_{student.id}')
            if status in ('Present','Absent'):
                Attendance.objects.update_or_create(student=student, date=today,
                    defaults={'status':status})
                saved += 1
        messages.success(request, f"Attendance saved for {saved} student(s) on {today}.")
        return redirect('attendance_report')
    existing = {a.student_id:a.status for a in Attendance.objects.filter(date=today)}
    student_rows = [{'obj':s,'status':existing.get(s.id,''),'initials':_initials(str(s))} for s in students]
    return render(request, 'mark_attendance.html', {'students':student_rows,'today':today,
        'total':students.count(),'marked':len(existing),'unmarked':students.count()-len(existing)})


@admin_required
def attendance_report(request):
    date_str = request.GET.get('date','')
    course   = request.GET.get('course','').strip()
    try:
        selected_date = timezone.datetime.strptime(date_str,'%Y-%m-%d').date()
    except (ValueError,TypeError):
        selected_date = timezone.now().date()
    records = Attendance.objects.select_related('student__user').filter(date=selected_date)
    if course:
        records = records.filter(student__course__icontains=course)
    courses = Student.objects.values_list('course', flat=True).distinct()
    return render(request, 'attendance_report.html', {'records':records,'selected_date':selected_date,
        'present_count':records.filter(status='Present').count(),
        'absent_count':records.filter(status='Absent').count(),
        'total_marked':records.count(),'courses':courses,'course':course})


@admin_required
def task_list(request):
    tasks      = Task.objects.select_related('student__user').all()
    students   = Student.objects.select_related('user').all()
    student_id = request.GET.get('student','')
    status_f   = request.GET.get('status','')
    priority_f = request.GET.get('priority','')
    if student_id:  tasks = tasks.filter(student_id=student_id)
    if status_f:    tasks = tasks.filter(status=status_f)
    if priority_f:  tasks = tasks.filter(priority=priority_f)
    submitted_ids = list(TaskSubmission.objects.values_list('task_id', flat=True))
    return render(request, 'task_list.html', {'tasks':tasks,'students':students,
        'student_id':student_id,'status_f':status_f,'priority_f':priority_f,
        'total':tasks.count(),'pending':tasks.filter(status='Pending').count(),
        'in_progress':tasks.filter(status='In Progress').count(),
        'completed':tasks.filter(status='Completed').count(),
        'submitted_ids':submitted_ids})


@admin_required
def assign_task(request):
    students = Student.objects.select_related('user').order_by('user__first_name')
    if request.method == 'POST':
        student_id  = request.POST.get('student_id')
        title       = request.POST.get('title','').strip()
        description = request.POST.get('description','').strip()
        due_date    = request.POST.get('due_date','').strip()
        priority    = request.POST.get('priority','Medium')
        errors = []
        if not student_id:
            errors.append('Please select a student.')
        if not title:
            errors.append('Task title is required.')
        if not due_date:
            errors.append('Due date is required.')
        if errors:
            messages.error(request, ' '.join(errors))
        else:
            # determine recipients
            if student_id == 'all':
                recipients = Student.objects.all()
            else:
                recipients = [get_object_or_404(Student, id=student_id)]
            for student in recipients:
                Task.objects.create(student=student, title=title,
                                    description=description,
                                    due_date=due_date, priority=priority)
            if student_id == 'all':
                messages.success(request, f'Task "{title}" assigned to all students successfully!')
            else:
                messages.success(request, f'Task "{title}" assigned to {recipients[0]} successfully!')
            return redirect('task_list')
    return render(request, 'assign_task.html', {'students':students})


@admin_required
def edit_task(request, task_id):
    task     = get_object_or_404(Task, id=task_id)
    students = Student.objects.select_related('user').order_by('user__first_name')
    if request.method == 'POST':
        task.student     = get_object_or_404(Student, id=request.POST.get('student_id'))
        task.title       = request.POST.get('title','').strip()
        task.description = request.POST.get('description','').strip()
        task.due_date    = request.POST.get('due_date')
        task.priority    = request.POST.get('priority','Medium')
        task.status      = request.POST.get('status','Pending')
        task.save()
        messages.success(request, f'Task "{task.title}" updated successfully!')
        return redirect('task_list')
    return render(request, 'edit_task.html', {'task':task,'students':students})


@admin_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted.')
    return redirect('task_list')


@admin_required
def student_tasks(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    tasks   = Task.objects.filter(student=student)
    return render(request, 'student_tasks.html', {'student':student,'tasks':tasks,
        'pending':tasks.filter(status='Pending').count(),
        'progress':tasks.filter(status='In Progress').count(),
        'completed':tasks.filter(status='Completed').count()})


@admin_required
def view_submission(request, task_id):
    task       = get_object_or_404(Task, id=task_id)
    submission = getattr(task, 'submission', None)
    return render(request, 'view_submission.html', {
        'task': task,
        'submission': submission
    })

@admin_required
def leave_list(request):
    leaves   = LeaveRequest.objects.select_related('student__user').all()
    status_f = request.GET.get('status','')
    if status_f:
        leaves = leaves.filter(status=status_f)
    return render(request, 'leave_list.html', {'leaves':leaves,'status_f':status_f,
        'pending':LeaveRequest.objects.filter(status='Pending').count(),
        'approved':LeaveRequest.objects.filter(status='Approved').count(),
        'rejected':LeaveRequest.objects.filter(status='Rejected').count(),
        'total':LeaveRequest.objects.count()})


@admin_required
def leave_action(request, leave_id):
    leave = get_object_or_404(LeaveRequest, id=leave_id)
    if request.method == 'POST':
        action       = request.POST.get('action')
        admin_remark = request.POST.get('admin_remark','').strip()
        if action == 'approve':
            leave.status = 'Approved'; leave.admin_remark = admin_remark; leave.save()
            messages.success(request, f'Leave for {leave.student} APPROVED.')
        elif action == 'reject':
            leave.status = 'Rejected'; leave.admin_remark = admin_remark; leave.save()
            messages.success(request, f'Leave for {leave.student} REJECTED.')
        return redirect('leave_list')
    return render(request, 'leave_action.html', {'leave':leave})


@admin_required
def admin_announcements(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            title         = request.POST.get('title','').strip()
            content       = request.POST.get('content','').strip()
            priority      = request.POST.get('priority','normal')
            target        = request.POST.get('target','all')
            target_course = request.POST.get('target_course','').strip() or None
            if title and content:
                Announcement.objects.create(title=title, content=content, priority=priority,
                    target=target, target_course=target_course, created_by=request.user)
                messages.success(request, 'Announcement posted.')
            else:
                messages.error(request, 'Title and content are required.')
        elif action == 'delete':
            Announcement.objects.filter(id=request.POST.get('ann_id')).delete()
            messages.success(request, 'Announcement deleted.')
        elif action == 'toggle':
            ann = get_object_or_404(Announcement, id=request.POST.get('ann_id'))
            ann.is_active = not ann.is_active; ann.save()
            messages.success(request, 'Status updated.')
        return redirect('admin_announcements')
    announcements = Announcement.objects.all()
    courses = Student.objects.values_list('course', flat=True).distinct()
    return render(request, 'announcements_admin.html', {'announcements':announcements,'courses':courses,
        'total_count':announcements.count(),'active_count':announcements.filter(is_active=True).count(),
        'urgent_count':announcements.filter(priority='urgent').count()})


def _initials(name):
    parts = name.strip().split()
    return ''.join(p[0].upper() for p in parts[:2]) if parts else '?'

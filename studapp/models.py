from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Student(models.Model):
    user    = models.OneToOneField(User, on_delete=models.CASCADE)
    age     = models.IntegerField()
    gender  = models.CharField(max_length=10)
    course  = models.CharField(max_length=50)
    phone   = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    def total_classes(self):
        return self.attendance_set.count()

    def present_count(self):
        return self.attendance_set.filter(status='Present').count()

    def absent_count(self):
        return self.attendance_set.filter(status='Absent').count()

    def attendance_percentage(self):
        total = self.total_classes()
        return 0.0 if total == 0 else round((self.present_count() / total) * 100, 1)


class Attendance(models.Model):
    STATUS_CHOICES = [('Present','Present'),('Absent','Absent')]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date    = models.DateField(default=timezone.now)
    status  = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('student','date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student} — {self.date} — {self.status}"


class Task(models.Model):
    PRIORITY_CHOICES = [('Low','Low'),('Medium','Medium'),('High','High')]
    STATUS_CHOICES   = [('Pending','Pending'),('In Progress','In Progress'),('Completed','Completed')]

    student     = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='tasks')
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date    = models.DateField()
    priority    = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    status      = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending')
    assigned_on = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-assigned_on']

    def __str__(self):
        return f"{self.title} → {self.student}"


class TaskSubmission(models.Model):
    task         = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='submission')
    student      = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions')
    file         = models.FileField(upload_to='task_submissions/')
    note         = models.TextField(blank=True)
    submitted_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Submission: {self.task.title} by {self.student}"


class LeaveRequest(models.Model):
    STATUS_CHOICES = [('Pending','Pending'),('Approved','Approved'),('Rejected','Rejected')]
    LEAVE_TYPES    = [('Sick','Sick Leave'),('Personal','Personal Leave'),
                      ('Emergency','Emergency Leave'),('Other','Other')]

    student      = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type   = models.CharField(max_length=20, choices=LEAVE_TYPES, default='Personal')
    from_date    = models.DateField()
    to_date      = models.DateField()
    reason       = models.TextField()
    status       = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    applied_on   = models.DateTimeField(default=timezone.now)
    admin_remark = models.TextField(blank=True)

    class Meta:
        ordering = ['-applied_on']

    def __str__(self):
        return f"{self.student} | {self.leave_type} | {self.status}"

    def days_count(self):
        return (self.to_date - self.from_date).days + 1


class Announcement(models.Model):
    PRIORITY_CHOICES = [('low','Low'),('normal','Normal'),('high','High'),('urgent','Urgent')]

    title         = models.CharField(max_length=200)
    content       = models.TextField()
    priority      = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    created_by    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)
    is_active     = models.BooleanField(default=True)
    target        = models.CharField(max_length=20,
                        choices=[('all','All Students'),('specific_course','Specific Course')],
                        default='all')
    target_course = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

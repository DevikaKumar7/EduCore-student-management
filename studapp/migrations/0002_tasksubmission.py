from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('studapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='task_submissions/')),
                ('note', models.TextField(blank=True)),
                ('submitted_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                    related_name='submissions', to='studapp.student')),
                ('task', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                    related_name='submission', to='studapp.task')),
            ],
        ),
    ]

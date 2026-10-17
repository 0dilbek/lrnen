import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('quiz', '0005_alter_exercise_type'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='exerciseattempt',
            name='content_snapshot',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='exerciseattempt',
            name='feedback',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.CreateModel(
            name='AdminNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('lesson_completed', 'Lesson completed')], default='lesson_completed', max_length=32)),
                ('lesson_title_snapshot', models.CharField(max_length=200)),
                ('score', models.PositiveSmallIntegerField(default=0)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('lesson', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admin_notifications', to='courses.lesson')),
                ('quiz_attempt', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admin_notification', to='quiz.quizattempt')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='admin_notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['is_read', '-created_at'], name='admin_notif_read_idx'),
                    models.Index(fields=['student', '-created_at'], name='admin_notif_student_idx'),
                ],
                'constraints': [
                    models.UniqueConstraint(fields=('student', 'lesson', 'event_type'), name='unique_student_lesson_admin_event'),
                ],
            },
        ),
    ]

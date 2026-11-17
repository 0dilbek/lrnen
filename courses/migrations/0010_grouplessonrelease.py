import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0004_studentgroup_user_study_group'),
        ('courses', '0009_level_current_lesson'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupLessonRelease',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lesson_releases', to='accounts.studentgroup')),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_releases', to='courses.level')),
                ('current_lesson', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='released_for_groups', to='courses.lesson')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('group', 'level'), name='unique_group_level_release')],
            },
        ),
    ]

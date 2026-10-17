from django.db import migrations, models
import django.db.models.deletion


def set_first_lesson_as_current(apps, schema_editor):
    Level = apps.get_model('courses', 'Level')
    for level in Level.objects.all():
        first_lesson = level.lessons.order_by('order', 'id').first()
        if first_lesson:
            level.current_lesson_id = first_lesson.id
            level.save(update_fields=['current_lesson'])


class Migration(migrations.Migration):
    dependencies = [
        ('courses', '0008_vocabulary_source_vocabulary_source_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='level',
            name='current_lesson',
            field=models.ForeignKey(
                blank=True,
                help_text="O'quvchilar shu darsgacha kira oladi. Bo'sh bo'lsa birinchi dars ochiladi.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='released_for_levels',
                to='courses.lesson',
            ),
        ),
        migrations.RunPython(set_first_lesson_as_current, migrations.RunPython.noop),
    ]

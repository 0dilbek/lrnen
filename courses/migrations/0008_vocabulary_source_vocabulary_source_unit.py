from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('courses', '0007_lesson_description_kaa_lesson_description_uz_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vocabulary',
            name='source',
            field=models.CharField(blank=True, db_index=True, max_length=100),
        ),
        migrations.AddField(
            model_name='vocabulary',
            name='source_unit',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]

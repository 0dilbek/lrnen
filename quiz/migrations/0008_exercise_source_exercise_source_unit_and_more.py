from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('quiz', '0007_exercise_instruction_kaa_exercise_instruction_uz')]

    operations = [
        migrations.AddField(
            model_name='exercise',
            name='source',
            field=models.CharField(blank=True, db_index=True, max_length=100),
        ),
        migrations.AddField(
            model_name='exercise',
            name='source_unit',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='exercise',
            name='type',
            field=models.CharField(
                choices=[
                    ('choose_correct', "To'g'ri so'zni tanlash"),
                    ('fill_blank', "Bo'sh joy to'ldirish"),
                    ('matching', 'Moslashtirish'),
                    ('listening', 'Listening'),
                    ('reading', 'Reading'),
                    ('speaking', 'Speaking'),
                    ('word_order', "So'zlarni tartiblash"),
                    ('written_answer', 'Yozma javob'),
                ],
                max_length=20,
            ),
        ),
    ]

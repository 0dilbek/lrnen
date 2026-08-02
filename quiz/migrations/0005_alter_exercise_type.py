from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('quiz', '0004_exerciseattempt_quizattempt_quizattemptanswer')]

    operations = [
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
                ],
                max_length=20,
            ),
        ),
    ]

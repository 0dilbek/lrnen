from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('quiz', '0008_exercise_source_exercise_source_unit_and_more')]
    operations = [
        migrations.AddField(
            model_name='exercise', name='source_key',
            field=models.CharField(blank=True, db_index=True, max_length=160),
        ),
        migrations.AddConstraint(
            model_name='exercise',
            constraint=models.UniqueConstraint(
                fields=('source', 'source_key'), condition=~models.Q(source_key=''),
                name='unique_exercise_book_source_key',
            ),
        ),
    ]

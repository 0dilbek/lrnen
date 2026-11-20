from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('courses', '0010_grouplessonrelease')]
    operations = [
        migrations.AddField(
            model_name='vocabulary', name='source_key',
            field=models.CharField(blank=True, db_index=True, max_length=160),
        ),
        migrations.AddConstraint(
            model_name='vocabulary',
            constraint=models.UniqueConstraint(
                fields=('source', 'source_key'), condition=~models.Q(source_key=''),
                name='unique_vocabulary_book_source_key',
            ),
        ),
    ]

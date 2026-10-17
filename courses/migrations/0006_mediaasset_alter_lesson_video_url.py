import courses.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('courses', '0005_alter_lesson_video_url'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='video_url',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.CreateModel(
            name='MediaAsset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('image', 'Image'), ('audio', 'Audio'), ('video', 'Video')], max_length=10)),
                ('file', models.FileField(upload_to=courses.models.protected_asset_path)),
                ('original_name', models.CharField(max_length=255)),
                ('content_type', models.CharField(blank=True, max_length=120)),
                ('size', models.PositiveBigIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_media_assets', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]

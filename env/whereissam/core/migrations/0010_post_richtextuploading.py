"""Make Post.content use RichTextUploadingField so CKEditor can upload images."""
from django.db import migrations
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_tides_options_tides_timestamp_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='content',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
    ]

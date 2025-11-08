# Generated manually for adding encrypted_data field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vault', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='encryptedfile',
            name='encrypted_data',
            field=models.BinaryField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='encryptedfile',
            name='encrypted_path',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]

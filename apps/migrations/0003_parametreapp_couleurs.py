from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0002_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='parametreapp',
            name='couleur_accent',
            field=models.CharField(default='#0EA5A4', help_text="Couleur d'accent du thème (logo, éléments clés)", max_length=7),
        ),
        migrations.AddField(
            model_name='parametreapp',
            name='couleur_principale',
            field=models.CharField(default='#14345B', help_text='Couleur principale du thème (barre latérale, titres)', max_length=7),
        ),
    ]

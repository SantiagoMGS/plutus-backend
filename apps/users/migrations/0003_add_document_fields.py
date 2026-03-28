from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_user_auth0_sub"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="document_number",
            field=models.CharField(
                blank=True,
                help_text="Número de documento de identidad.",
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="document_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("CC", "Cédula de Ciudadanía"),
                    ("CE", "Cédula de Extranjería"),
                    ("NIT", "NIT"),
                    ("PP", "Pasaporte"),
                    ("TI", "Tarjeta de Identidad"),
                ],
                help_text="Tipo de documento de identidad.",
                max_length=3,
                null=True,
            ),
        ),
    ]

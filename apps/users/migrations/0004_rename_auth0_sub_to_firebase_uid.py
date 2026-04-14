from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_add_document_fields"),
    ]

    operations = [
        migrations.RenameField(
            model_name="user",
            old_name="auth0_sub",
            new_name="firebase_uid",
        ),
    ]

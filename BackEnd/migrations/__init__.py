from django.db import migrations

operations = [
    migrations.RunSQL("ALTER TABLE BackEnd_gguser RENAME COLUMN password TO Password;")
]

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('patients', '0005_allow_independent_registration'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.AddField(
                    model_name='assessment', name='started_at',
                    field=models.DateTimeField(null=True, editable=False),
                ),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='assessment', name='started_at',
                    field=models.DateTimeField(auto_now_add=True, null=True),
                ),
            ],
        ),
    ]

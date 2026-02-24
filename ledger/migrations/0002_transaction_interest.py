from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ledger", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="interest_type",
            field=models.CharField(
                choices=[
                    ("NONE", "No Interest"),
                    ("SIMPLE", "Simple Interest"),
                    ("COMPOUND", "Compound Interest"),
                ],
                default="NONE",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="transaction",
            name="interest_rate",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="Annual interest rate in % (e.g. 12 for 12% per year)",
                max_digits=6,
                null=True,
            ),
        ),
    ]

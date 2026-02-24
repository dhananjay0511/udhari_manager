from django.db import migrations


class Migration(migrations.Migration):
    """
    Removes interest_type and interest_rate fields from Transaction.
    Run: python manage.py migrate
    """

    dependencies = [
        ("ledger", "0002_transaction_interest"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="transaction",
            name="interest_type",
        ),
        migrations.RemoveField(
            model_name="transaction",
            name="interest_rate",
        ),
    ]

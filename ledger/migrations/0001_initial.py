import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Person",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("phone", models.CharField(blank=True, db_index=True, max_length=20)),
                ("notes", models.TextField(blank=True)),
                ("opening_balance", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="persons",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "type",
                    models.CharField(
                        choices=[("GIVEN", "Given (you lent money)"), ("RECEIVED", "Received (you got money back)")],
                        max_length=10,
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=14)),
                ("date", models.DateField(default=django.utils.timezone.now)),
                ("due_date", models.DateField(blank=True, null=True)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transactions",
                        to="ledger.person",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transactions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-date", "-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="person",
            index=models.Index(fields=["user", "name"], name="ledger_pers_user_id_idx"),
        ),
        migrations.AddIndex(
            model_name="transaction",
            index=models.Index(fields=["user", "person"], name="ledger_tran_user_id_idx"),
        ),
        migrations.AddIndex(
            model_name="transaction",
            index=models.Index(fields=["due_date"], name="ledger_tran_due_dat_idx"),
        ),
        migrations.AddIndex(
            model_name="transaction",
            index=models.Index(fields=["date"], name="ledger_tran_date_idx"),
        ),
    ]

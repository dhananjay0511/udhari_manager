from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Person(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="persons")
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True, db_index=True)
    notes = models.TextField(blank=True)
    opening_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["user", "name"]),
        ]

    def __str__(self):
        return self.name


class Transaction(models.Model):
    GIVEN = "GIVEN"
    RECEIVED = "RECEIVED"
    TYPE_CHOICES = [
        (GIVEN, "Given (you lent money)"),
        (RECEIVED, "Received (you got money back)"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="transactions")
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "person"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["date"]),
        ]

    def __str__(self):
        return f"{self.type} ₹{self.amount} — {self.person.name}"

    def clean(self):
        if self.person_id:
            try:
                person = Person.objects.get(pk=self.person_id)
                if self.user_id and person.user_id != self.user_id:
                    raise ValidationError("Transaction user must match person's user.")
            except Person.DoesNotExist:
                pass
        if self.amount is not None and self.amount <= 0:
            raise ValidationError({"amount": "Amount must be greater than zero."})
        if self.due_date and self.date and self.due_date < self.date:
            raise ValidationError({"due_date": "Due date must be on or after the transaction date."})

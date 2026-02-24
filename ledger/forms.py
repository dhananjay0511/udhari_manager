import re
from django import forms
from django.utils import timezone
from .models import Person, Transaction


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ["name", "phone", "notes", "opening_balance"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3, "placeholder": "Any notes about this person…"}),
            "name": forms.TextInput(attrs={"placeholder": "Full name"}),
            "phone": forms.TextInput(attrs={"placeholder": "+91 98765 43210"}),
            "opening_balance": forms.NumberInput(attrs={"placeholder": "0.00", "step": "0.01"}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if phone:
            phone = re.sub(r"[^\d\+\-\s\(\)]", "", phone)
            phone = re.sub(r"\s+", " ", phone).strip()
        return phone


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["person", "type", "amount", "date", "due_date", "description"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 2, "placeholder": "Optional note…"}),
            "amount": forms.NumberInput(attrs={"placeholder": "0.00", "step": "0.01", "min": "0.01"}),
        }

    def __init__(self, *args, user=None, person=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["person"].queryset = Person.objects.filter(user=user)
        if person:
            self.fields["person"].initial = person
            self.fields["person"].widget = forms.HiddenInput()
        self.fields["date"].initial = timezone.now().date()

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount

    def clean(self):
        cleaned = super().clean()
        date = cleaned.get("date")
        due_date = cleaned.get("due_date")
        if date and due_date and due_date < date:
            self.add_error("due_date", "Due date must be on or after the transaction date.")
        return cleaned

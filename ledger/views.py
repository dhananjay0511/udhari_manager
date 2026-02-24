from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import DecimalField, F, Min, Q, Sum, Value, Case, When
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.core.paginator import Paginator

from .forms import PersonForm, TransactionForm
from .models import Person, Transaction
from .utils import balance_annotation


def person_qs(user):
    return (
        Person.objects.filter(user=user)
        .annotate(
            balance=balance_annotation(),
            nearest_due=Min("transactions__due_date"),
        )
    )


# ── DASHBOARD ──────────────────────────────────────────────────────────────

class DashboardView(LoginRequiredMixin, View):
    template_name = "ledger/dashboard.html"

    def get(self, request):
        qs = person_qs(request.user)
        today = timezone.now().date()

        search = request.GET.get("search", "").strip()
        filter_type = request.GET.get("filter", "")
        sort = request.GET.get("sort", "name")

        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(phone__icontains=search))

        if filter_type == "has_due":
            qs = qs.filter(transactions__due_date__isnull=False).distinct()
        elif filter_type == "overdue":
            qs = qs.filter(transactions__due_date__lt=today).distinct()
            qs = [p for p in qs if p.balance > 0]

        if isinstance(qs, list):
            if sort == "balance":
                qs = sorted(qs, key=lambda p: p.balance, reverse=True)
            elif sort == "due_date":
                qs = sorted(qs, key=lambda p: p.nearest_due or timezone.datetime.max.date())
        else:
            if sort == "balance":
                qs = qs.order_by("-balance")
            elif sort == "due_date":
                qs = qs.order_by("nearest_due")
            else:
                qs = qs.order_by("name")

        total_persons = Person.objects.filter(user=request.user).count()
        total_given = (
            Transaction.objects.filter(user=request.user, type="GIVEN")
            .aggregate(s=Coalesce(Sum("amount"), Value(0), output_field=DecimalField()))["s"]
        )
        total_received = (
            Transaction.objects.filter(user=request.user, type="RECEIVED")
            .aggregate(s=Coalesce(Sum("amount"), Value(0), output_field=DecimalField()))["s"]
        )
        net_outstanding = max(total_given - total_received, Decimal("0"))

        return render(request, self.template_name, {
            "persons": qs,
            "search": search,
            "filter_type": filter_type,
            "sort": sort,
            "today": today,
            "total_persons": total_persons,
            "total_given": total_given,
            "total_received": total_received,
            "net_outstanding": net_outstanding,
        })


# ── PEOPLE ─────────────────────────────────────────────────────────────────

class PersonListView(LoginRequiredMixin, View):
    template_name = "ledger/person_list.html"

    def get(self, request):
        qs = person_qs(request.user).order_by("name")
        return render(request, self.template_name, {"persons": qs})


class PersonAddView(LoginRequiredMixin, View):
    template_name = "ledger/person_form.html"

    def get(self, request):
        return render(request, self.template_name, {"form": PersonForm(), "title": "Add Person"})

    def post(self, request):
        form = PersonForm(request.POST)
        if form.is_valid():
            person = form.save(commit=False)
            person.user = request.user
            person.save()
            messages.success(request, f"✓ '{person.name}' added successfully.")
            return redirect("ledger:person_detail", pk=person.pk)
        return render(request, self.template_name, {"form": form, "title": "Add Person"})


class PersonDetailView(LoginRequiredMixin, View):
    template_name = "ledger/person_detail.html"

    def get(self, request, pk):
        person = get_object_or_404(Person, pk=pk, user=request.user)
        today = timezone.now().date()

        tx_list = Transaction.objects.filter(person=person, user=request.user).order_by("-date", "-created_at")

        given = tx_list.filter(type="GIVEN").aggregate(
            s=Coalesce(Sum("amount"), Value(0), output_field=DecimalField()))["s"]
        received = tx_list.filter(type="RECEIVED").aggregate(
            s=Coalesce(Sum("amount"), Value(0), output_field=DecimalField()))["s"]
        balance = person.opening_balance + given - received

        upcoming_due = tx_list.filter(due_date__isnull=False, due_date__gte=today).order_by("due_date").first()
        overdue_txs = tx_list.filter(due_date__isnull=False, due_date__lt=today)
        is_overdue = overdue_txs.exists() and balance > 0

        paginator = Paginator(tx_list, 20)
        page_obj = paginator.get_page(request.GET.get("page"))

        return render(request, self.template_name, {
            "person": person,
            "page_obj": page_obj,
            "total_given": given,
            "total_received": received,
            "balance": balance,
            "upcoming_due": upcoming_due,
            "overdue_txs": overdue_txs,
            "is_overdue": is_overdue,
            "today": today,
        })


class PersonEditView(LoginRequiredMixin, View):
    template_name = "ledger/person_form.html"

    def get_person(self, request, pk):
        return get_object_or_404(Person, pk=pk, user=request.user)

    def get(self, request, pk):
        person = self.get_person(request, pk)
        return render(request, self.template_name, {
            "form": PersonForm(instance=person),
            "title": f"Edit {person.name}",
            "person": person,
        })

    def post(self, request, pk):
        person = self.get_person(request, pk)
        form = PersonForm(request.POST, instance=person)
        if form.is_valid():
            form.save()
            messages.success(request, f"✓ '{person.name}' updated.")
            return redirect("ledger:person_detail", pk=person.pk)
        return render(request, self.template_name, {
            "form": form,
            "title": f"Edit {person.name}",
            "person": person,
        })


class PersonDeleteView(LoginRequiredMixin, View):
    template_name = "ledger/person_confirm_delete.html"

    def get_person(self, request, pk):
        return get_object_or_404(Person, pk=pk, user=request.user)

    def get(self, request, pk):
        return render(request, self.template_name, {"person": self.get_person(request, pk)})

    def post(self, request, pk):
        person = self.get_person(request, pk)
        name = person.name
        person.delete()
        messages.success(request, f"✓ '{name}' deleted.")
        return redirect("ledger:person_list")


# ── TRANSACTIONS ────────────────────────────────────────────────────────────

class TransactionAddView(LoginRequiredMixin, View):
    template_name = "ledger/transaction_form.html"

    def get_person(self, request):
        pid = request.GET.get("person") or request.POST.get("person")
        if pid:
            return get_object_or_404(Person, pk=pid, user=request.user)
        return None

    def get(self, request):
        person = self.get_person(request)
        form = TransactionForm(user=request.user, person=person)
        return render(request, self.template_name, {"form": form, "person": person, "title": "Add Transaction"})

    def post(self, request):
        person = self.get_person(request)
        form = TransactionForm(request.POST, user=request.user, person=person)
        if form.is_valid():
            tx = form.save(commit=False)
            tx.user = request.user
            if tx.person.user != request.user:
                messages.error(request, "Invalid person.")
                return redirect("ledger:dashboard")
            tx.save()
            messages.success(request, f"✓ Transaction of ₹{tx.amount} added.")
            return redirect("ledger:person_detail", pk=tx.person.pk)
        return render(request, self.template_name, {"form": form, "person": person, "title": "Add Transaction"})


class TransactionEditView(LoginRequiredMixin, View):
    template_name = "ledger/transaction_form.html"

    def get_tx(self, request, pk):
        return get_object_or_404(Transaction, pk=pk, user=request.user)

    def get(self, request, pk):
        tx = self.get_tx(request, pk)
        form = TransactionForm(instance=tx, user=request.user)
        return render(request, self.template_name, {"form": form, "tx": tx, "title": "Edit Transaction"})

    def post(self, request, pk):
        tx = self.get_tx(request, pk)
        form = TransactionForm(request.POST, instance=tx, user=request.user)
        if form.is_valid():
            updated = form.save(commit=False)
            if updated.person.user != request.user:
                messages.error(request, "Invalid person.")
                return redirect("ledger:dashboard")
            updated.save()
            messages.success(request, "✓ Transaction updated.")
            return redirect("ledger:person_detail", pk=updated.person.pk)
        return render(request, self.template_name, {"form": form, "tx": tx, "title": "Edit Transaction"})


class TransactionDeleteView(LoginRequiredMixin, View):
    template_name = "ledger/transaction_confirm_delete.html"

    def get_tx(self, request, pk):
        return get_object_or_404(Transaction, pk=pk, user=request.user)

    def get(self, request, pk):
        return render(request, self.template_name, {"tx": self.get_tx(request, pk)})

    def post(self, request, pk):
        tx = self.get_tx(request, pk)
        person_pk = tx.person.pk
        tx.delete()
        messages.success(request, "✓ Transaction deleted.")
        return redirect("ledger:person_detail", pk=person_pk)

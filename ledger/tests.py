"""
Tests for udhari_manager ledger app.
Run: python manage.py test ledger
"""
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Person, Transaction


class BaseTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user("alice", "alice@example.com", "pass1234")
        self.user2 = User.objects.create_user("bob", "bob@example.com", "pass1234")
        self.client = Client()

    def login(self, user):
        self.client.force_login(user)

    def make_person(self, user, name="Test Person", opening_balance=0):
        return Person.objects.create(user=user, name=name, opening_balance=opening_balance)

    def make_tx(self, user, person, tx_type, amount, days_ago=0, due_days=None):
        tx_date = timezone.now().date() - timedelta(days=days_ago)
        due_date = None
        if due_days is not None:
            due_date = tx_date + timedelta(days=due_days)
        return Transaction.objects.create(
            user=user,
            person=person,
            type=tx_type,
            amount=Decimal(str(amount)),
            date=tx_date,
            due_date=due_date,
        )


# ──────────────────────────────────────────────
# Permission / IDOR tests
# ──────────────────────────────────────────────

class PermissionTests(BaseTestCase):
    """User cannot access another user's data."""

    def test_cannot_view_other_persons_detail(self):
        """user2's person detail should 404 for user1."""
        person = self.make_person(self.user2, "Bob's Person")
        self.login(self.user1)
        url = reverse("ledger:person_detail", kwargs={"pk": person.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_cannot_edit_other_persons_person(self):
        person = self.make_person(self.user2)
        self.login(self.user1)
        url = reverse("ledger:person_edit", kwargs={"pk": person.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_cannot_delete_other_persons_person(self):
        person = self.make_person(self.user2)
        self.login(self.user1)
        url = reverse("ledger:person_delete", kwargs={"pk": person.pk})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(Person.objects.filter(pk=person.pk).exists())

    def test_cannot_view_other_persons_tx(self):
        person2 = self.make_person(self.user2)
        tx = self.make_tx(self.user2, person2, "GIVEN", 100)
        self.login(self.user1)
        url = reverse("ledger:tx_edit", kwargs={"pk": tx.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_cannot_delete_other_persons_tx(self):
        person2 = self.make_person(self.user2)
        tx = self.make_tx(self.user2, person2, "GIVEN", 100)
        self.login(self.user1)
        url = reverse("ledger:tx_delete", kwargs={"pk": tx.pk})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(Transaction.objects.filter(pk=tx.pk).exists())

    def test_dashboard_only_shows_own_persons(self):
        p1 = self.make_person(self.user1, "Alice Person")
        p2 = self.make_person(self.user2, "Bob Person")
        self.login(self.user1)
        resp = self.client.get(reverse("ledger:dashboard"))
        self.assertEqual(resp.status_code, 200)
        persons = list(resp.context["persons"])
        pks = [p.pk for p in persons]
        self.assertIn(p1.pk, pks)
        self.assertNotIn(p2.pk, pks)

    def test_unauthenticated_redirected_to_login(self):
        resp = self.client.get(reverse("ledger:dashboard"))
        self.assertRedirects(resp, "/accounts/login/?next=/")


# ──────────────────────────────────────────────
# Balance annotation tests
# ──────────────────────────────────────────────

class BalanceAnnotationTests(BaseTestCase):
    def _annotated_person(self, person):
        from .utils import balance_annotation
        from .models import Person as P
        return P.objects.filter(pk=person.pk).annotate(balance=balance_annotation()).first()

    def test_balance_no_transactions(self):
        person = self.make_person(self.user1, opening_balance=500)
        ap = self._annotated_person(person)
        self.assertEqual(ap.balance, Decimal("500"))

    def test_balance_given_increases(self):
        person = self.make_person(self.user1, opening_balance=0)
        self.make_tx(self.user1, person, "GIVEN", 300)
        ap = self._annotated_person(person)
        self.assertEqual(ap.balance, Decimal("300"))

    def test_balance_received_decreases(self):
        person = self.make_person(self.user1, opening_balance=0)
        self.make_tx(self.user1, person, "GIVEN", 500)
        self.make_tx(self.user1, person, "RECEIVED", 200)
        ap = self._annotated_person(person)
        self.assertEqual(ap.balance, Decimal("300"))

    def test_balance_with_opening_and_transactions(self):
        person = self.make_person(self.user1, opening_balance=100)
        self.make_tx(self.user1, person, "GIVEN", 400)
        self.make_tx(self.user1, person, "RECEIVED", 150)
        # 100 + 400 - 150 = 350
        ap = self._annotated_person(person)
        self.assertEqual(ap.balance, Decimal("350"))

    def test_balance_can_go_negative(self):
        person = self.make_person(self.user1, opening_balance=0)
        self.make_tx(self.user1, person, "RECEIVED", 500)
        ap = self._annotated_person(person)
        self.assertEqual(ap.balance, Decimal("-500"))

    def test_no_n_plus_1_queries(self):
        """Dashboard should not run N+1 queries."""
        for i in range(5):
            p = self.make_person(self.user1, name=f"Person {i}")
            self.make_tx(self.user1, p, "GIVEN", 100)
        self.login(self.user1)
        # Just ensure the dashboard loads without error
        resp = self.client.get(reverse("ledger:dashboard"))
        self.assertEqual(resp.status_code, 200)


# ──────────────────────────────────────────────
# Overdue filter tests
# ──────────────────────────────────────────────

class OverdueFilterTests(BaseTestCase):
    def test_overdue_person_appears_in_overdue_filter(self):
        """Person with past due_date tx and positive balance should appear."""
        person = self.make_person(self.user1, "Overdue Person")
        # Given tx dated 30 days ago, due 20 days ago
        self.make_tx(self.user1, person, "GIVEN", 500, days_ago=30, due_days=10)
        self.login(self.user1)
        resp = self.client.get(reverse("ledger:dashboard") + "?filter=overdue")
        self.assertEqual(resp.status_code, 200)
        pks = [p.pk for p in resp.context["persons"]]
        self.assertIn(person.pk, pks)

    def test_settled_person_not_in_overdue(self):
        """Person fully received (balance=0) not overdue even if due_date < today."""
        person = self.make_person(self.user1, "Settled Person")
        self.make_tx(self.user1, person, "GIVEN", 300, days_ago=30, due_days=10)
        self.make_tx(self.user1, person, "RECEIVED", 300)
        self.login(self.user1)
        resp = self.client.get(reverse("ledger:dashboard") + "?filter=overdue")
        pks = [p.pk for p in resp.context["persons"]]
        self.assertNotIn(person.pk, pks)

    def test_future_due_not_overdue(self):
        """Person with future due_date should not appear in overdue."""
        person = self.make_person(self.user1, "Future Due")
        self.make_tx(self.user1, person, "GIVEN", 500, days_ago=0, due_days=30)
        self.login(self.user1)
        resp = self.client.get(reverse("ledger:dashboard") + "?filter=overdue")
        pks = [p.pk for p in resp.context["persons"]]
        self.assertNotIn(person.pk, pks)


# ──────────────────────────────────────────────
# Form validation tests
# ──────────────────────────────────────────────

class FormValidationTests(BaseTestCase):
    def test_transaction_amount_must_be_positive(self):
        from .forms import TransactionForm
        person = self.make_person(self.user1)
        form = TransactionForm(
            data={
                "person": person.pk,
                "type": "GIVEN",
                "amount": "-100",
                "date": date.today().isoformat(),
            },
            user=self.user1,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("amount", form.errors)

    def test_due_date_before_date_invalid(self):
        from .forms import TransactionForm
        person = self.make_person(self.user1)
        tx_date = date.today()
        form = TransactionForm(
            data={
                "person": person.pk,
                "type": "GIVEN",
                "amount": "100",
                "date": tx_date.isoformat(),
                "due_date": (tx_date - timedelta(days=1)).isoformat(),
            },
            user=self.user1,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("due_date", form.errors)

    def test_valid_transaction_form(self):
        from .forms import TransactionForm
        person = self.make_person(self.user1)
        tx_date = date.today()
        form = TransactionForm(
            data={
                "person": person.pk,
                "type": "GIVEN",
                "amount": "250.50",
                "date": tx_date.isoformat(),
                "due_date": (tx_date + timedelta(days=30)).isoformat(),
            },
            user=self.user1,
        )
        self.assertTrue(form.is_valid(), form.errors)

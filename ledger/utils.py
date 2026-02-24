from django.db.models import Case, DecimalField, F, Sum, Value, When
from django.db.models.functions import Coalesce


def balance_annotation():
    """
    Returns an annotation expression for net balance.
    Balance = opening_balance + SUM(GIVEN amounts) - SUM(RECEIVED amounts)
    Positive balance => person owes user.
    Negative balance => user owes person.
    """
    given_sum = Coalesce(
        Sum(
            Case(
                When(transactions__type="GIVEN", then=F("transactions__amount")),
                default=Value(0),
                output_field=DecimalField(max_digits=14, decimal_places=2),
            )
        ),
        Value(0),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )
    received_sum = Coalesce(
        Sum(
            Case(
                When(transactions__type="RECEIVED", then=F("transactions__amount")),
                default=Value(0),
                output_field=DecimalField(max_digits=14, decimal_places=2),
            )
        ),
        Value(0),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )
    return F("opening_balance") + given_sum - received_sum

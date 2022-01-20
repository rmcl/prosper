"""Useful functions for Analyzing a prosper account."""
from typing import Dict
from datetime import datetime, date

from .api import ProsperAPI


def total_payments_by_month(prosper_api_client : ProsperAPI) -> Dict[date, float]:
    """Return the sum of all payments received by month for the account."""

    payments = prosper_api_client.payments()

    payment_totals_by_month = {}
    for payment_detail in payments:
        if payment_detail['payment_status'] != 'Success':
            continue

        effective_date = datetime.fromisoformat(payment_detail['investor_disbursement_date'][:-5])
        month = date(effective_date.year, effective_date.month, 1)

        if month not in payment_totals_by_month:
            payment_totals_by_month[month] = 0.0

        payment_totals_by_month[month] += payment_detail['payment_amount']

    return payment_totals_by_month

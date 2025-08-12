# app/xero_client.py
import os
from xero_python.accounting import AccountingApi
from xero_python.api_client import ApiClient
from xero_python.api_client.oauth2 import OAuth2Token


def get_garden_costs():
    # Mock costs until OAuth with Xero is set up
    # Real implementation: use Xero AccountingApi to filter by expense category
    return 120.50  # USD

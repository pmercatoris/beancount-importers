#!/usr/bin/env python3
from beancount.ingest import extract

from importers.ing import beancount_importer as beancount

CONFIG = [
    beancount.Importer(
        currency="EUR",
        folder="checking",
        account_root="Assets:EU:ING",
        account_external="Assets:EU:ING:Checking",
    ),

    beancount.Importer(
        currency="EUR",
        folder="savings",
        account_root="Assets:EU:ING",
        account_external="Assets:EU:ING:Savings",
    ),

    beancount.Importer(
        currency="EUR",
        folder="credit",
        account_root="Liabilities:EU:ING",
        account_external="Liabilities:EU:ING:Credit",
    ),

]

# Override the header on extracted text (if desired).
extract.HEADER = ";; -*- mode: org; mode: beancount; coding: utf-8; -*-\n"

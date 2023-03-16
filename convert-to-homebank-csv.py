#!/usr/bin/env python3.8
# file : convert-to-homebank-csv.py
# reconcile bank account with gnucash
# Raiffeisen export:
#   Fortune > Relevé de compte > Télécharger les données du compte
#   Compte: Privé sociétaire
#   Format: Excel CSV
#   Données du compte: Période prédéfinie du relevé de compte > Relevé annuel
#   Détails de la comptabilisation: sans détails
# gnucash export:
#   File > Export > Export Transactions to CSV
#   Simple layout, semicolon separator
#   Assets > Current assets > Bank Accounts > raif courant
# requires python 3.8
__author__ = "Marcel Gerber"
__date__ = "2023-03-16"

import argparse
import sys                             # for retrieving exception messages
import re                              # for matching bank transaction text
import csv                             # for importing CSV data (bank and gnucash transactions)
# import xml.etree.ElementTree as et     # for handling XML
# from xml.sax.saxutils import quoteattr, unescape # for searching quoted text attributes with findall
# from xml.dom import minidom            # for exporting pretty XML
from datetime import date, datetime, timedelta


class Help(object):

    def __init__(self):
        parser = argparse.ArgumentParser(description='Convert CSV file to HomeBank CSV file.')
        parser.add_argument('csv-in', help='Input CSV file')
        parser.add_argument('csv-out', help='Ouput CSV (for HomeBank)')
        parser.add_argument('def', help='Definition file')
        args = parser.parse_args(sys.argv[1:2])
        if args.len == 0:
            print('Not enough arguments.')
            parser.print_help()
            exit(1)
        self.args = parser.parse_args(sys.argv[2:])


'''
Colors for output
'''
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


'''
Convert from all date and date time sources to date object.
'''
def str2date(str):
    try:
        return date.fromisoformat(str[0:10])
    except:
        pass

    try:
        return datetime.strptime(str.replace(' ', ''), '%d.%m.%y').date()
    except:
        pass

    try:
        return datetime.strptime(str.replace(' ', ''), '%d.%m.%Y').date()
    except:
        pass

'''
Convert date to string in HomeBank format.
'''
def date2str(dt):
    return dt.strftime('%d-%m-%Y')

'''
Print a transaction row.
'''
def print_row(row, prefix="", suffix = f"{bcolors.ENDC}"):
    try:
        bookedat = date2str(row['BookedAt'])
    except:
        bookedat = row['BookedAt']
    print(f"{prefix}{bookedat} {float(row['Amount']):9.2f} - {row['Text']}{suffix}")


if __name__ == "__main__":
    print(f"{bcolors.BOLD}Welcome to the transaction CSV to HomeBank CSV Convert Script{bcolors.ENDC}")

    # parse arguments according to action
    help = Help()
    print(f"Action: {help.action}")

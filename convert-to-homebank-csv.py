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
        parser.add_argument('csvin', help='Input CSV file')
        parser.add_argument('csvout', help='Ouput CSV (for HomeBank)')
        parser.add_argument('csvdef', help='Definition file')
        if len(sys.argv) == 1:
            print('')
            print('Not enough arguments.')
            print('')
            parser.print_help()
            exit(1)
        self.args = parser.parse_args(sys.argv[1:])


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
def str2date(str, format = '%Y-%m-%d'):
    try:
        return date.fromisoformat(str[0:10])
    except:
        pass

    try:
        return datetime.strptime(str.replace(' ', ''), format).date()
    except:
        pass

    try:
        return datetime.strptime(str.replace(' ', ''), format).date()
    except:
        pass

'''
Convert date to string in HomeBank format.
'''
def date2str(dt, format = '%d-%m-%Y'):
    return dt.strftime(format)

'''
Print a transaction row.
'''
def print_row(row, prefix="", suffix = f"{bcolors.ENDC}"):
    try:
        bookedat = date2str(row['BookedAt'])
    except:
        bookedat = row['BookedAt']
    print(f"{prefix}{bookedat} {float(row['Amount']):9.2f} - {row['Text']}{suffix}")

'''
Sort a dictionary.
field: field to use for sorting
'''
def sort_dictlist(csvdict, field):
    size = len(csvdict)
    for i in range(size):
        min_index = i
        for j in range(i + 1, size):
            if csvdict[min_index][field] > csvdict[j][field]:
                min_index = j
        temp = csvdict[i]
        csvdict[i] = csvdict[min_index]
        csvdict[min_index] = temp

'''
Parse definition file.
'''
def parse_def(csvdict):
    newlist = []
    for row in csvdict:
        newlist.append({
            'HbFieldPos': int(row['HbFieldPos']),
            'HbFieldName': row['HbFieldName'].strip(),
            'InFieldPos': int(row['InFieldPos']),
            'InFieldName': row['InFieldName'].strip(),
            'InFieldFormat': row['InFieldFormat'].strip()
        })
    sort_dictlist(newlist, field = 'HbFieldPos')
    return newlist


if __name__ == "__main__":
    print(f"{bcolors.BOLD}Welcome to the transaction CSV to HomeBank CSV Convert Script{bcolors.ENDC}")

    # parse arguments according to action
    help = Help()

    # open and filter transactions
    with open(help.args.csvdef, newline='', encoding='utf8') as csvdef:
        print(f"Definition CSV file: '{csvdef.name}'.")
        defreader = csv.DictReader(csvdef, delimiter=';')
        deflist = parse_def(defreader)

    print(deflist)

    # # open and filter transactions
    # with open(help.args.csvdef, newline='', encoding='latin1') as csvdef:
    #     print(f"Definition CSV file: '{csvdef}'.")
    #     defreader = csv.DictReader(csvdef, delimiter=';')
    #     deflist = parse_def(defreader)

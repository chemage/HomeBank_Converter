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
import colorama                        # for command line coloring
import xml.etree.ElementTree as et     # for handling XML
from xml.sax.saxutils import quoteattr, unescape # for searching quoted text attributes with findall
from xml.dom import minidom            # for exporting pretty XML
from datetime import date, datetime, timedelta


class Help(object):

    def __init__(self):
        parser = argparse.ArgumentParser(description='Convert CSV file to HomeBank CSV file.')
        parser.add_argument('csvin', help='Input CSV file')
        parser.add_argument('csvout', help='Ouput CSV (for HomeBank)')
        parser.add_argument('xmldef', help='Definition file')
        if len(sys.argv) == 1:
            print('')
            print('Not enough arguments.')
            print('')
            parser.print_help()
            exit(1)
        self.args = parser.parse_args(sys.argv[1:])


class Definition(object):

    def __init__(self, xmldef = None):
        if (xmldef):
            self.set_xmldef(xmldef)
        else:
            log(f"No XML provided. Can be added later.")

    def set_xmldef(self, xmldef):
        self.xmldef = xmldef
        self.__load_def()
        self.__parse_def()

    '''
    Load definition file from XML.
    '''
    def __load_def(self):
        try:
            self.__xmltree = et.parse(self.xmldef)
            self.xmlroot = self.__xmltree.getroot()
            log(f"Successfully loaded XML file '{self.xmldef}'.")
        except:
            log(f"Error: could not load XML file '{self.xmldef}'. {sys.exc_info()[0]}")

    '''
    Parse definition file.
    '''
    def __parse_def(self):
        # Get CSV definitions
        csvdefs = self.xmlroot.find('CsvDefinitions')
        self.__delimiter   = csvdefs.get('Delimiter')
        self.__headerlines = csvdefs.get('HeaderLineCount')
        self.__encoding    = csvdefs.get('Encoding')

        xmlfields = self.xmlroot.findall('.//Field')
        print("List of fields")
        for xmlfield in xmlfields:
            print(xmlfield.find('HomeBank').get('Name'))

    def __str__(self):
        str = f"Definition => "
        sep = ''
        for attr in self.xmlroot.attrib:
            str += f"{sep}{attr}: {self.xmlroot.get(attr)}"
            sep = ', '

        return str


'''
Colors for output in linux/python
'''
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

'''

'''
def startswith(source, prefix, casesensitive = True):
    if casesensitive:
        return source[:len(prefix)] == prefix
    else:
        return source.lower()[:len(prefix)] == prefix

'''
Write log to console (and file ?)
'''
def log(msg):
    if startswith(msg, "error", False):
        print(f"{colorama.Fore.RED}{msg}")
    elif startswith(msg, "warn", False):
        print(f"{colorama.Fore.YELLOW}{msg}")
    else:
        print(f"{msg}")
    print(colorama.Style.RESET_ALL)

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
    log(f"{prefix}{bookedat} {float(row['Amount']):9.2f} - {row['Text']}{suffix}")

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


if __name__ == "__main__":
    log(f"Welcome to the transaction CSV to HomeBank CSV Convert Script")

    # fix colorama for windows
    if sys.platform == 'win32':
        colorama.just_fix_windows_console()

    # parse arguments according to action
    help = Help()

    # open definitions from XML
    objdef = Definition(help.args.xmldef)

    print(objdef)

    # # open and filter transactions
    # with open(help.args.csvdef, newline='', encoding='latin1') as csvdef:
    #     log(f"Definition CSV file: '{csvdef}'.")
    #     defreader = csv.DictReader(csvdef, delimiter=';')
    #     deflist = parse_def(defreader)

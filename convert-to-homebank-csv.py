#!/usr/bin/env python3
# file : convert-to-homebank-csv.py
# transfrom a transaction file to a HomeBank CSV file.
# requires python >= 3.10
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
        log(f"Load definitions from file '{self.xmldef}'.")
        try:
            self.__xmltree = et.parse(self.xmldef)
            self.xmlroot = self.__xmltree.getroot()
            # log(f"Successfully loaded XML file '{self.xmldef}'.")
        except:
            log(f"Error: could not load XML file '{self.xmldef}'. {sys.exc_info()[0]}")

    '''
    Parse definition file.
    '''
    def __parse_def(self):
        # Get CSV definitions
        csvdefs = self.xmlroot.find('CsvDefinitions')
        self.delim     = csvdefs.get('Delimiter')
        self.headlines = csvdefs.get('HeaderLineCount')
        self.encoding  = csvdefs.get('Encoding')

        xmlfields = self.xmlroot.findall('.//Field')
        self.mapping = {}
        for xmlfield in xmlfields:
            hbrow     = xmlfield.find('HomeBank')
            hbfield   = hbrow.get('Name').strip()
            srcrow    = xmlfield.find('Source')
            condition = xmlfield.find('Condition')
            srcpos    = int(srcrow.get('Position'))
            self.mapping[hbfield] = {
                'hbpos':   int(hbrow.get('Position')),
                'srcpos':  srcpos,
                'srcname': srcrow.get('Name').strip(),
                'format':  srcrow.get('Format')
            }
            if condition != None:
                self.mapping[hbfield]['condition'] = {}
                for attr in condition.attrib:
                    self.mapping[hbfield]['condition'][attr] = condition.get(attr)

    '''
    Return string representation of object
    '''
    def __str__(self):
        str = f"Definition => "
        sep = ''
        for attr in self.xmlroot.attrib:
            str += f"{sep}{attr}: {self.xmlroot.get(attr)}"
            sep = ', '

        return str


'''
Source CSV object
'''
class Source(object):
    def __init__(self, csvin, objdef):
        self.csvin  = csvin
        self.csvdef = objdef
        self.__map  = objdef.mapping
        self.data   = []
        self.load_csv()

    def load_csv(self):
        log(f"Import from file '{self.csvin}'.")
        with open(self.csvin, newline='', encoding=self.csvdef.encoding) as csvin:
            csvreader = csv.DictReader(csvin, delimiter=self.csvdef.delim)
            self.parse_source(csvreader)

    def parse_source(self, csvreader):
        for row in csvreader:
            hbrow = {}
            for hbfield in self.__map:
                srcfield = self.__map[hbfield]['srcname']

                # mapped fields
                srcpos = self.__map[hbfield]['srcpos']
                if srcpos >= 0:
                    # condition
                    if 'condition' in self.__map[hbfield]:
                        condtype  = self.__map[hbfield]['condition']['Function']
                        condtest  = self.__map[hbfield]['condition']['Test']
                        print(f"'{condtest}', '{row[srcfield]}', '{row[srcfield].find(condtest)}'")
                        if row[srcfield].find(condtest) >= 0:
                            value = self.__map[hbfield]['condition']['ValueIfTrue']
                        else:
                            value = self.__map[hbfield]['condition']['ValueIfFalse']
                    else:
                        value  = row[srcfield]
                    match hbfield:
                        case 'date': value = str2date(value, self.__map[hbfield]['format'])

                # unmapped fields will be empty
                else:
                    match hbfield:
                        case 'payment': value = 0
                        case _:         value = ''

                hbrow[hbfield] = value
            self.data.append(hbrow)
        # print(self.data)

    def export(self, csvout):
        log(f"Export to file '{csvout}'.")
        hbfields = self.__map.keys()
        with open(csvout, 'w', newline='') as csvout:
            csvwriter = csv.DictWriter(csvout, hbfields, delimiter = ';')
            csvwriter.writeheader()
            for row in self.data:
                csvwriter.writerow(row)


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
        print(f"{colorama.Fore.RED}{msg}{colorama.Style.RESET_ALL}")
    elif startswith(msg, "warn", False):
        print(f"{colorama.Fore.YELLOW}{msg}{colorama.Style.RESET_ALL}")
    else:
        print(f"{msg}")

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
    print()
    print(objdef)
    print()
    log("List of fields")
    for map in objdef.mapping:
        log(f"{map}: {objdef.mapping[map]}")

    # load CSV data
    print()
    src = Source(help.args.csvin, objdef)
    log(f"Number of transactions: {len(src.data)}")
    src.export(help.args.csvout)

    # display transformed data
    # print()
    # log("List of HomeBank transactions")
    # for row in src.data:
    #     print(row)

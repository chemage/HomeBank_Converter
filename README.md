# HomeBank CSV Converter
Convert CSV to HomeBank import files

## Prerequisites
- Minimum version: Python 3.10 (use of match)
- module colorama (pip install colorama)

## Usage
usage: convert-to-homebank-csv.py [-h] csvin csvout xmldef

```
usage: convert-to-homebank-csv.py [-h] csvin csvout xmldef

Convert CSV file to HomeBank CSV file.

positional arguments:
  csvin       Input CSV file
  csvout      Ouput CSV (for HomeBank)
  xmldef      Definition file


optional arguments:
  -h, --help  show this help message and exit
```

## Definition File

### A few rules
- File format is XML.
- Definition encoding is the encoding of the source file, use the python name.
- Fields that cannot be matched with source should have a source position of -1 to be ignored by script.
- Format in Source field is a date format for Python.
- Multiple conditions are allowed

### Conditions
Conditions allow to fill different fields based on another value.
The order of the conditions is important. Search finishes when a condition is met.

#### Methods
- find: find text in a string
   - CaseSensitive: add the attribute to search with case sensitive
   - default case: not case sensitive
- search: use a regular expression to lookup for contents (https://docs.python.org/3/library/re.html)
   - to replace the value by the search text, use a set of parenthesis () to group your result.
   - to retrieve the result set the number of your group (usually 1) prefixed by a dollar sign $ in ValueIfTrue.

### Example GnuCash
<details>
<summary>Click to display the code</summary>

```xml
<?xml version="1.0" ?>
<Definition Name="Gnucash CHF">
    <CsvDefinitions Delimiter=";" HeaderLineCount="1" Encoding="utf8" />
    <Fields>
        <Field>
            <HomeBank Position="0" Name="date" />
            <Source Position="0" Name="Date" Format="%d.%m.%Y" />
        </Field>
        <Field>
            <HomeBank Position="1" Name="payment" />
            <Source Position="4" Name="Full Category Path" />
            <Condition Method="find" ValueIfTrue="9" ValueIfFalse="3" Test="Assets:Current Assets:Bank Accounts" />
        </Field>
        <Field>
            <HomeBank Position="2" Name="info" />
            <Source Position="-1" Name="N/A" />
        </Field>
        <Field>
            <HomeBank Position="3" Name="payee" />
            <Source Position="-1" Name="N/A" />
        </Field>
        <Field>
            <HomeBank Position="4" Name="memo" />
            <Source Position="3" Name="Description" />
        </Field>
        <Field>
            <HomeBank Position="5" Name="amount" />
            <Source Position="7" Name="Amount Num." />
        </Field>
        <Field>
            <HomeBank Position="6" Name="category" />
            <Source Position="3" Name="Description" />
            <Condition Method="find" Test="Donation" ValueIfTrue="Charitable Donations" ValueIfFalse="" />
            <Condition Method="find" Test="Marché" ValueIfTrue="Food" ValueIfFalse="" />
            <Condition Method="find" Test="Lessive" ValueIfTrue="Housold:Laundry" ValueIfFalse="" />
        </Field>
        <Field>
            <HomeBank Position="7" Name="tags" />
            <Source Position="3" Name="Description" />
            <Condition Method="find" Test="Marché" ValueIfTrue="Food Market" ValueIfFalse="" />
            <Condition Method="find" Test="Coop" ValueIfTrue="Supermarket" ValueIfFalse="" />
            <Condition Method="find" Test="Migros" ValueIfTrue="Supermarket" ValueIfFalse="" />
            <Condition Method="find" Test="Denner" ValueIfTrue="Supermarket" ValueIfFalse="" />
        </Field>
    </Fields>
</Definition>
```
</details>

### Example Raiffeisen Switzerland
<details>
<summary>Click to display the code</summary>

```xml
<?xml version="1.0" ?>
<Definition Name="Raiffeisen">
    <CsvDefinitions Delimiter=";" HeaderLineCount="1" Encoding="latin1" />
    <Fields>
        <Field>
            <HomeBank Position="0" Name="date" />
            <Source Position="5" Name="Valuta Date" Format="%d-%m-%Y" />
        </Field>
        <Field>
            <HomeBank Position="1" Name="payment" />
            <Source Position="2" Name="Text" />
            <Condition Method="find" ValueIfTrue="4" ValueIfFalse="0" Test="transfert de compte à compte" />
            <Condition Method="find" ValueIfTrue="6" ValueIfFalse="0" Test="Achat" />
            <Condition Method="find" ValueIfTrue="7" ValueIfFalse="0" Test="E-banking Ordre permanent" />
            <Condition Method="find" ValueIfTrue="8" ValueIfFalse="0" Test="E-banking Ordre (eBill)" />
        </Field>
        <Field>
            <HomeBank Position="2" Name="info" />
            <Source Position="-1" Name="N/A" />
        </Field>
        <Field>
            <HomeBank Position="3" Name="payee" />
            <Source Position="-1" Name="N/A" />
        </Field>
        <Field>
            <HomeBank Position="4" Name="memo" />
            <Source Position="2" Name="Text" />
        </Field>
        <Field>
            <HomeBank Position="5" Name="amount" />
            <Source Position="3" Name="Credit/Debit Amount" />
        </Field>
        <Field>
            <HomeBank Position="6" Name="category" />
            <Source Position="-1" Name="N/A" />
        </Field>
        <Field>
            <HomeBank Position="7" Name="tags" />
            <Source Position="-1" Name="N/A" />
        </Field>
    </Fields>
</Definition>
```
</details>

## CSV Exports
Exports have to be one line per transaction.
Python CSV DictReader is used, so quotes are not specifically necessary.

### GnuCash Export

Gnucash exports can be done in various ways.

The most compatible to this script is the below.

<details>
<summary>Click to display the details</summary>

- File > Export > Export Transactions to CSV
- Choose Export Settings:
   - Options: Simple layout - mandatory
   - Separators: Semicolon (;) - optional
- Select the account
- Select the date range

![Export Settings](/doc/gnucash-exportsettings.png)
![Export Settings](/doc/gnucash-daterange.png)
</details>

## Limitations

- Script does not accept multi-line CSV sources.
- No payment method information.
- Transfers cannot be imported (not supported by HomeBank)

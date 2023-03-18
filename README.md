# HomeBank CSV Converter
Convert CSV to HomeBank import files

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

#### Functions
- find: find text in a string

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
            <Condition Function="find" ValueIfTrue="9" ValueIfFalse="3" Test="Assets:Current Assets:Bank Accounts" />
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
            <Condition Function="find" Test="Donation" ValueIfTrue="Charitable Donations" ValueIfFalse="" />
            <Condition Function="find" Test="Marché" ValueIfTrue="Food" ValueIfFalse="" />
            <Condition Function="find" Test="Lessive" ValueIfTrue="Housold:Laundry" ValueIfFalse="" />
        </Field>
        <Field>
            <HomeBank Position="7" Name="tags" />
            <Source Position="3" Name="Description" />
            <Condition Function="find" Test="Marché" ValueIfTrue="Food Market" ValueIfFalse="" />
            <Condition Function="find" Test="Coop" ValueIfTrue="Supermarket" ValueIfFalse="" />
            <Condition Function="find" Test="Migros" ValueIfTrue="Supermarket" ValueIfFalse="" />
            <Condition Function="find" Test="Denner" ValueIfTrue="Supermarket" ValueIfFalse="" />
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
            <Condition Function="find" ValueIfTrue="4" ValueIfFalse="0" Test="transfert de compte à compte" />
            <Condition Function="find" ValueIfTrue="6" ValueIfFalse="0" Test="Achat" />
            <Condition Function="find" ValueIfTrue="7" ValueIfFalse="0" Test="E-banking Ordre permanent" />
            <Condition Function="find" ValueIfTrue="8" ValueIfFalse="0" Test="E-banking Ordre (eBill)" />
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
- File > Export > Export Transactions to CSV
- Choose Export Settings:
   - Options: Simple layout - mandatory
   - Separators: Semicolon (;) - optional
- Select the account
- Select the date range

![Export Settings](/doc/gnucash-exportsettings.png)
![Export Settings](/doc/gnucash-daterange.png)

## TODO

- Change condition source to be independent from source field.
- Add option to merge to existing CSV file.
- Correct transfer transactions (see warning in transaction import).
- Add option to double transactions for account to account transfers.

## Limitations

- Script does not accept multi-line CSV sources.
- No payment method information.

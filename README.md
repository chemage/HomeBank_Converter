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
- Description fields can be multiple, text will be concatenated (description.1 + description.2 + description.3 + etc.).
- Fields that cannot be matched with source should have a source position of -1 to be ignored by script.
- Format in Source field is a date format for Python.

### Example Raiffeisen Switzerland
```
<?xml version="1.0" ?>
<Definition Name="Raiffeisen" Encoding="latin1">
    <CsvDefinitions Delimiter=";" HeaderLineCount="1" />
    <Fields>
        <Field>
            <HomeBank Position="0" Name="date" />
            <Source Position="5" Name="Valuta Date" Format="%d-%m-%Y" />
        </Field>
        <Field>
            <HomeBank Position="1" Name="paymode" />
            <Source Position="-1" Name="N/A" />
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
            <HomeBank Position="4" Name="description.1" />
            <Source Position="2" Name="description" />
        </Field>
        <Field>
            <HomeBank Position="4" Name="description.2" />
            <Source Position="2" Name="description" />
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
            <HomeBank Position="7" Name="account" />
            <Source Position="-1" Name="N/A" />
        </Field>
        <Field>
            <HomeBank Position="8" Name="balance" />
            <Source Position="4" Name="Balance" />
        </Field>
    </Fields>
</Definition>
```

## Limitations

- Script does not accept multi-line CSV sources.
- No payment method information.

# Tanzania Motor Insurance Record Review

A small working template for reviewing comprehensive motor insurance quotation records. It connects the sum insured to the quoted rate and keeps questions about the figures visible.

I work in insurance operations in Tanzania. This project reflects the checks I want to see before policy information is used in a register or a client follow-up. It is a portfolio template. The input file contains column headings only, with no invented customer records or completed client assignment.

## What the review does

- Records the sum insured in Tanzanian shillings and the rate stated in the insurer's quotation.
- Calculates the rate component as `sum insured × rate percent ÷ 100`.
- Applies a minimum base premium only when that minimum has been entered from the applicable quotation or rating schedule.
- Compares the resulting base premium with the recorded base premium.
- Flags missing information, invalid numbers, repeated record IDs and differences requiring confirmation.

There is no universal rate in the code. Vehicle use, the insurer's terms and the applicable rating schedule must be checked against the source quotation. Base premium and the total payable are different fields: this tool does not add assumed VAT, levies, fees or extensions.

## Start with the documents

1. Confirm the vehicle use, cover type and the source quotation.
2. Copy `data/quote_register_template.csv` into a private working folder.
3. Enter the sum insured, quoted rate, applicable minimum and recorded base premium. Keep the quotation reference.
4. Run the review and check every question against the original document.
5. Keep the reviewed file and any client information outside this public repository.

The [review checklist](docs/review_checklist.md) gives the manual steps. The [field guide](docs/field_guide.md) explains the inputs and the exact scope of the calculation.

## Run the review

Requires Python 3.10 or later. It uses the standard library only.

```bash
python review_motor_quotes.py /path/to/private_quotes.csv --output review_output
```

The script writes `reviewed_quotes.csv` and `summary.json`. The original file is left intact. A blank template produces a clear `no_records` summary.

An exact comparison is used by default. If a documented rounding difference is acceptable for the task, set a tolerance in TZS explicitly:

```bash
python review_motor_quotes.py /path/to/private_quotes.csv --output review_output --tolerance 1
```

That tolerance is a review setting, not an insurer tariff or a regulatory allowance.

## Read the result

`Arithmetic matches inputs` means the required inputs are present and the base premium agrees with the entered rate and minimum within the chosen tolerance. It does not establish that the rate is authorised, the sum insured is appropriate, or cover has been issued.

`Needs confirmation` identifies the missing or inconsistent details. A blank minimum remains a question. Enter zero only when the source confirms that no minimum applies to that quotation.

## Check the script

```bash
python -m unittest discover -s tests -v
```

Test amounts are software test inputs. They are not customer cases, market prices or published tariffs.

## Tanzania sources and authorship

See [sources and scope](docs/tanzania_sources.md) for the Tanzania references and their limits. Use the current insurer quotation and applicable TIRA requirements for live work.

Prepared for Elius Mukiza Eradius. The insurance background is from my professional experience. AI assisted with drafting and coding. This project makes no claim about a past paid software assignment.

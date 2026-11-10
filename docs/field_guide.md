# Input fields and calculation scope

This template reviews annual comprehensive motor base-premium arithmetic. The insurer's quotation or approved rating schedule supplies the rate, minimum and other terms. A short-period, fleet, instalment or otherwise adjusted quotation requires its own documented calculation and is outside this version.

| Field | Enter from the source |
| --- | --- |
| `record_id` | A unique internal review reference. Avoid publishing personal identifiers. |
| `insurer` | The insurer named on the quotation. |
| `quote_reference` | The quotation or rating document reference. |
| `vehicle_use` | The actual stated use, such as private use or the specific commercial use. This is recorded for manual checking; the script does not choose a rate from it. |
| `sum_insured_tzs` | The sum insured recorded on the quotation, as a positive number in TZS. |
| `rate_percent` | The quoted percentage. Enter `3.5` for a quoted rate of 3.5%. This is a formatting example, not a prescribed rate. |
| `minimum_base_premium_tzs` | The applicable minimum base premium from the source. Leave unknown values blank. Zero means the source explicitly confirms that no minimum applies. |
| `quoted_base_premium_tzs` | The recorded base premium before taxes, levies, fees or extensions. Do not copy an inclusive total into this field. |

Use plain numbers without thousands separators or currency symbols. Decimal fractions are allowed. The script uses decimal arithmetic, keeps the calculation unrounded and reports the difference against the entered premium. The optional tolerance is a comparison setting in TZS.

## Formula

```text
Rate component = Sum insured × quoted rate percent ÷ 100
Expected base premium = Greater of the rate component and the confirmed minimum
Difference = Recorded base premium − expected base premium
```

The minimum formula applies only when the source quotation uses that rating structure. If it uses a different structure, record the question for a manual review rather than forcing it into this template.

## Information this version does not decide

The script does not select a sum insured, verify a vehicle valuation, prescribe a tariff, calculate a claim, verify payment, issue cover or calculate the final total payable. VAT, levies, fees, extensions, discounts and other adjustments must follow the actual quotation and current requirements.

The result is a record-review aid. Keep the source document, confirm its date and version, and document the reason for any change to a record.

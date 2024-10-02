# Change log

## Unreleased

- Specify in visible strings the word representation to distinguish from commercialization properly
- New implementation to create and identify the user staff for Representation Virtual Office
    - Consider existing partners with the specified nif
    - Consider existing links to address from users
- Hide invoices emitted beyond a given date
- Extract liquidation information from invoice line
- Retrieve production data for a single contract

## 0.2.0 (2024-02-13)

- New som.ov.production.data.measures() entry point to obtain production measures
- New invoice field `payment_status`
- Invoice pdf name simplified to `[invoice_number]_[contract_cil].pdf`


## 0.1.0 (2024-01-23)

- OV staff users
- Invoices
- Installations and installation details
- Rgpd Signature
- Proxy data ("representant legal de l'entitat") added to the profile

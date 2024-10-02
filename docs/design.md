# Design choices

## Roles

We identified 3 roles

- Admin: Can provision users
    - ERP using the super secret key
- Staff: Can hijack users
    - TOVALIDATE: res.user?
- Customer: Plain users
    - Customer valid res_partner with the `customer` category.

## Turning ERP users into Som Representa staff

Definicions:
- provided data: the ones provided by the user on the wizard fields
    - VAT
    - Mail
- A consistent linked address has a partner, with a vat and a first address has a valid email

Base case:

1. Operator selects a User in the ERP
2. Operator actions "Turnt into SomRepre Staff"
3. Wizard verifies that user has not a partner address
4. Wizard prompts for a VAT and a email
5. Wizard verifies that there is not a partner with that VAT
6. Wizard creates the partner with provided data
7. Wizard creates the partner_address with provide data
8. Wizard links user to the partner_address
9. Wizard adds the category to the partner
10. Wizard presents any result, error or warning to the user

Extensions:

5.a. Wizard detects that there is one existing partner with the same vat
5.a.1. Wizard chooses the first address of the existing partner
5.a.2. Wizard adds a warning: "Existing person with provided VAT, using email <w@fasdf>, instead the provided one"
5.a.3. Go to step 8

5.a.1.a. Partner address has no email
TODO

5.b. Wizard detects that there is **more than one** existing partner with the same vat
5.b.1. Wizard adds an error: "There is more than one person matching this VAT. Fix it, before proceeding"
5.a.3. Go to step 10

3.a. Wizard detects that the user is already relatated to an address
3.a.1. Wizard verifies that the linked address is not broken
3.a.2. Wizard verifies that the linked address is the first one
3.a.3. Wizard verifies that there is no more partners with that VAT
3.a.4. Wizard verifies that the partner is missing the category
3.a.5. Wizard takes the VAT from the partner to fill the form
3.a.6. Wizard takes the email from the first partner address (not the linked one) to fill the form
3.a.7. Wizard prompts "This will will turn this user into somrepre staff, proceed?"
3.a.8. User acepts
3.a.9. Go to step 9

3.a.1.a. [x] Wizard detect that the linked address is inconsistent
3.a.1.a.1. Shows message "Partner related is broken: <reason>" and abort

3.a.2.a. [x] The address linked to the user is not the first one of the partner
3.a.2.a.1. Set the form warning to "Using the primary address of the partner instead the one set on the user"
3.a.2.a.2. Goto 3.a.3

3.a.3.a. [x] Wizard detect that the linked partner VAT is dupped in other partners
3.a.3.a.1. Shows message "Other parnters have the same VAT, fix it" and abort

3.a.4.a. [x] Wizard detects that the linked parnter already has category
3.a.4.a.1. Shows message "Already staff" and abort

## Authentication

As we use emails and nifs as login, and nifs can be vats for foreigners,
we decided to split those 3 concepts for params and variable names,
to explicit the semantics of a variable.

- Login: Whatever users uses to identify themselves: They may use a NIF, a VAT or a email (whichever the role)
    - allow email login for customers: to allow user google account until we have the auth server
- Username: What the OV uses to identify a user:
    - VAT for customers (even spanish, removing nif from the equation)
    - email for staff
        - Why: no VAT field in res_user
- Domain data: nif, vat, email...
    - vat: vat code with country prefix
        - TOCHECK: passports?
    - nif: vat but removing ES if starts with ES, used only to communicate with the user (internally a vat, use sandwich)
        - vat -> nif remove leading ES
        - nif -> vat, check if it validates as nif, if so, add ES
        - We reduce it into a presentation issue to present vats as nifs, so we delegate that to the API.

- Login is used just to login, erp turns it into a username.
- Username is used along to refer the user in api-erp communications
- NIFS are detected and turned into VATS
- VATS with ES are turned NIFS for presentation purposes (spanish users do not identify a VAT, but a NIF)

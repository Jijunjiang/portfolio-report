# Playbook: cash-secured puts

**User preference (stated directly, applies to every run): this is the
default option-selling strategy, ahead of covered calls.** The user views
covered calls as riskier on this account specifically, since assignment
forces a sale of an already-owned, often appreciated position (see the tax
section's embedded-gain flags), whereas a put's assignment just acquires
stock at a fresh cost basis. When both a covered call and a CSP are
plausible on a name, lead with the put here and only add a covered call
alongside it if it clears the much-further-OTM bar in `covered-calls.md`.

When to suggest one: there's meaningful idle buying power
(`buying_power.unleveraged_buying_power`) sitting uninvested in a taxable or
margin account, and the user already holds or watches the underlying — don't
invent new names.

Sizing: a suggested put's strike * 100 * contracts must not exceed the
account's `unleveraged_buying_power` (use unleveraged, not margin buying
power, so the "cash-secured" framing stays literally true — using margin
buying power here is really a naked/margined put, call it out separately if
ever mentioned).

Strike selection:
1. Default to strikes below current price at a level the user would
   genuinely be fine owning the stock at (a discount to current price, not
   ATM) — being assigned is the acceptable outcome of a CSP, not a failure
   mode, so frame it that way.
2. 2–6 week expirations by default, same rationale as covered calls.
3. Same annualized-yield math as covered calls, denominated on cash secured
   rather than notional: `premium / (strike * 100) * (365 /
   days_to_expiration)`.
4. Flag earnings-window overlap the same way as covered calls.

If idle cash is sitting in a Roth IRA or other tax-advantaged account, note
that assignment there has no wash-sale/tax-lot complications — worth
mentioning as a plus, not a requirement.

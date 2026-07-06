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

## Every suggestion needs a "why it's a good deal if assigned" reason

A CSP's premium is only half the pitch — the other half is that assignment
itself has to be a price you'd genuinely want. Ground this in real data,
not vibes:
- `effective_cost = strike - premium`, then locate it against
  `get_equity_fundamentals`'s `high_52_weeks`/`low_52_weeks`: `position_pct
  = (effective_cost - low) / (high - low)`. Below 0% (under the 52-week
  low) or near it is the strongest case; mid-range or higher means the
  pitch has to rest on something else (dividend yield, income, "still like
  this name at any reasonable price").
- Pull `dividend_yield` and `pe_ratio` too — a high P/E name near its low
  is a growth/momentum bet, not a value entry, and a loss-making name
  (negative P/E) with no dividend has no fundamental floor under the
  price at all. Say which of these situations applies rather than
  presenting every "near the low" case as equally sound.
- Be honest when a candidate doesn't clear this bar — "still well above
  the 52-week low, you'd be paying up" is a real, useful finding,
  especially when it's also the highest-premium name on the list (premium
  and price attractiveness don't move together).

# Playbook: covered calls

**User preference (stated directly, applies to every run): covered calls
are the secondary strategy, not the default.** The user considers a covered
call riskier than a cash-secured put on this account specifically — a
covered call's assignment forces a *sale* of an already-owned, often
appreciated position (realizing embedded gain, per the tax section), while
a put's assignment merely *acquires* stock at a fresh cost basis without
disturbing an existing lot. That reasoning is sound for this portfolio
given how much embedded gain sits in it, so treat it as the working model,
not just a stated quirk. Concretely: when a name could plausibly support
either a covered call or a cash-secured put, lead with the put (see
`cash-secured-puts.md`) and only mention a covered call alongside it if one
clears the bar below.

When to suggest one anyway: the position has ≥100
`shares_available_for_sells` not already fully covered by existing short
calls (subtract contracts already short on that chain from
`shares_available_for_sells / 100` to get spare capacity) **and** a strike
clears the "almost impossible to settle" bar the user wants —
significantly further OTM than the industry-standard 0.20–0.30 delta
screen, more like the account's own existing TSM $600c (roughly 35–40% OTM,
low-single-digit delta) as the reference point. The user is explicit that
they'd rather collect a smaller premium at a strike assignment essentially
never reaches than optimize for yield at a moderate delta — don't default
back to 0.20–0.30 delta just because it's the common heuristic.

Strike/expiration selection, in priority order:
1. **Respect embedded gain first, then push further OTM than that alone
   would require.** If the position is flagged in the tax section for large
   unrealized gain, that's a floor, not the target — go further out than
   "comfortably above current price" toward the low-delta, rarely-reached
   strikes the user actually wants. Say the approximate delta/probability
   explicitly in the suggestion so "almost impossible" is a stated number,
   not just a vibe.
2. Prefer 2–6 week expirations unless the user's existing positions on that
   name are further out — match the account's existing cadence rather than
   introducing a new one.
3. Surface the strike, expiration, and estimated premium (from the option
   chain's current quote if available, else the last comparable trade), plus
   simple annualized-yield math: `premium / (strike * 100) * (365 /
   days_to_expiration)` per contract, so suggestions are comparable to each
   other. Yield will look unimpressive at these strikes — that's expected,
   not a signal to move the strike closer.
4. Always flag if the expiration is at or after the underlying's next
   earnings date (from `get_earnings_calendar`) — earnings-adjacent
   suggestions need a call-out, not a silent inclusion.

Never suggest writing a call that would bring total short-call contracts on
a symbol above the shares actually available to cover — that's a naked
call, out of scope for this playbook.

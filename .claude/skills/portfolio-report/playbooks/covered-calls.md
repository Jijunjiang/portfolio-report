# Playbook: covered calls

When to suggest one: the position has ≥100 `shares_available_for_sells` not
already fully covered by existing short calls (subtract contracts already
short on that chain from `shares_available_for_sells / 100` to get spare
capacity).

Strike/expiration selection, in priority order:
1. **Respect embedded gain first.** If the position is flagged in the tax
   section for large unrealized gain, only suggest strikes comfortably above
   current price (default: far enough OTM that assignment is a low-probability
   tail case, not the base case) — the goal is collecting premium without
   materially raising the odds of a forced taxable sale. Say this explicitly
   in the suggestion, don't just show a strike.
2. Prefer 2–6 week expirations unless the user's existing positions on that
   name are further out — match the account's existing cadence rather than
   introducing a new one.
3. Surface the strike, expiration, and estimated premium (from the option
   chain's current quote if available, else the last comparable trade), plus
   simple annualized-yield math: `premium / (strike * 100) * (365 /
   days_to_expiration)` per contract, so suggestions are comparable to each
   other.
4. Always flag if the expiration is at or after the underlying's next
   earnings date (from `get_earnings_calendar`) — earnings-adjacent
   suggestions need a call-out, not a silent inclusion.

Never suggest writing a call that would bring total short-call contracts on
a symbol above the shares actually available to cover — that's a naked
call, out of scope for this playbook.

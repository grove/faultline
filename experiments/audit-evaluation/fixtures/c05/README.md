# Same-key retry

Review only sequential retries of the same key and amount in one process. The
first call records one ledger effect and returns a receipt; a same-key retry
returns the same receipt without recording another effect. The supplied Ledger
is the only effect boundary. Other keys, changed amounts, restart durability,
concurrency, and lost acknowledgements are outside this review.

# Cart discount

Review apply_discount test protection for an invalid discount. Cart totals and
percentages are integers. A percentage outside 0 through 100 inclusive must raise
ValueError and leave the cart unchanged. Valid discounts round down to integer
units. No nested cart data, caller validation, or concurrent access is in scope.

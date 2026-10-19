def apply_discount(cart, percent):
    cart["total"] = cart["total"] * (100 - percent) // 100
    if not 0 <= percent <= 100:
        raise ValueError("invalid discount")

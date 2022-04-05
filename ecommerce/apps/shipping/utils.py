def variants(product_type):
    print(f"retieving variants for {product_type}")
    if product_type.name == "icons":
        return ["8x10", "wallet-size"]
    else:
        return []

class TradeService:
    def place_trade(self, trade):
        symbol = trade.get("symbol", "UNKNOWN")
        quantity = trade.get("quantity", 0)
        account = trade.get("account", "cash")
        action = trade.get("action", "buy").capitalize()
        order_type = trade.get("order_type", "market")
        price = trade.get("price")

        if order_type == "market":
            price_str = "market price"
        else:
            price_str = f"${price}"

        return (
            f"✅ Trade placed: {action} {quantity} shares of {symbol} "
            f"at {price_str} in {account.upper()} account "
            f"({order_type.capitalize()} order)."
        )

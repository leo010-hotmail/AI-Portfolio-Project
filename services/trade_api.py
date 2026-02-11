from services.broker_app import list_accounts, place_order

class TradeService:
    def place_trade(self, trade):

        symbol = trade.get("symbol")
        quantity = trade.get("quantity")
        action = trade.get("action", "buy")
        order_type = trade.get("order_type", "market")
        price = trade.get("price")

        # Get first account (sandbox)
        accounts = list_accounts()
        account_id = accounts[0]["id"]

        try:
            order = place_order(
                account_id=account_id,
                symbol=symbol,
                quantity=quantity,
                side=action,
                order_type=order_type,
                price=price
            )

            return (
                f"✅ Order submitted!\n\n"
                f"Symbol: {order['symbol']}\n"
                f"Side: {order['side']}\n"
                f"Quantity: {order['qty']}\n"
                f"Type: {order['type']}\n"
                f"Status: {order['status']}"
            )

        except Exception as e:
            return f"❌ Trade failed: {str(e)}"

from services.broker_app import list_accounts, list_orders, place_order, cancel_order


class TradeService:
    def place_trade(self, trade):

        symbol = trade.get("symbol")
        quantity = trade.get("quantity")
        action = trade.get("action", "buy")
        order_type = trade.get("order_type", "market")
        price = trade.get("price")

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
                f"Order submitted!\n\n"
                f"Symbol: {order['symbol']}\n"
                f"Side: {order['side']}\n"
                f"Quantity: {order['qty']}\n"
                f"Type: {order['type']}\n"
                f"Status: {order['status']}"
            )

        except Exception as e:
            return f"Trade failed: {str(e)}"

    def cancel_trade(self, order_id):
        accounts = list_accounts()
        account_id = accounts[0]["id"]

        try:
            order = cancel_order(account_id=account_id, order_id=order_id)
            return (
                f"Cancel request submitted!\n\n"
                f"Order ID: {order.get('id', order_id)}\n"
                f"Symbol: {order.get('symbol', 'N/A')}\n"
                f"Status: {order.get('status', 'cancelled')}"
            )

        except Exception as e:
            return f"Cancel failed: {str(e)}"

    def list_open_orders(self, status="open", limit=50):
        accounts = list_accounts()
        if not accounts:
            raise RuntimeError("No trading accounts could be loaded.")

        account_id = accounts[0]["id"]
        return list_orders(account_id=account_id, limit=limit, status=status)

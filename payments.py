from db import one, execute

def simulate_payment(order_id, method, should_succeed=True):
    order = one("SELECT total_pkr,status FROM orders WHERE id=%s", (order_id,))
    if not order: raise ValueError("Order not found")
    status = 'verified' if should_succeed else 'failed'
    row = one("INSERT INTO payments(order_id,method,amount_pkr,status,reference) VALUES(%s,%s,%s,%s,%s) RETURNING id",
              (order_id,method,order['total_pkr'],status,'DEMO-'+__import__('secrets').token_hex(5).upper()))
    if should_succeed:
        execute("UPDATE orders SET payment_status='verified',status='paid',updated_at=NOW() WHERE id=%s", (order_id,))
    return row

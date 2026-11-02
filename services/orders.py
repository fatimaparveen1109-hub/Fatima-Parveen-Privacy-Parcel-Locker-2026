from db import get_conn, one, query, execute
from services.payments import simulate_payment

from services.workflow_rules import ALLOWED

def place_order(user_id, cart, hub_id, alt_hub_id=None, alt_opt_in=False):
    if not cart: raise ValueError('Cart is empty')
    with get_conn() as conn:
        with conn.cursor() as cur:
            total=0; lines=[]
            for pid, qty in cart.items():
                cur.execute("SELECT id,name,price_pkr,stock_qty,parcel_size,seller_id FROM products WHERE id=%s AND is_active=TRUE FOR UPDATE",(int(pid),))
                p=cur.fetchone()
                if not p or qty < 1 or p['stock_qty'] < qty: raise ValueError('A product is unavailable or out of stock')
                total += p['price_pkr']*qty; lines.append((p,qty))
            product_total=total; total += 90
            cur.execute("INSERT INTO orders(customer_id,hub_id,alternative_hub_id,alternative_opt_in,product_total_pkr,rider_fee_pkr,locker_fee_pkr,total_pkr,status,payment_status) VALUES(%s,%s,%s,%s,%s,30,60,%s,'placed','pending') RETURNING id",
                        (user_id,hub_id,alt_hub_id,alt_opt_in,product_total,total))
            oid=cur.fetchone()['id']
            for p,qty in lines:
                cur.execute("UPDATE products SET stock_qty=stock_qty-%s WHERE id=%s",(qty,p['id']))
                cur.execute("INSERT INTO order_items(order_id,product_id,seller_id,product_name,quantity,unit_price_pkr,parcel_size) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                            (oid,p['id'],p['seller_id'],p['name'],qty,p['price_pkr'],p['parcel_size']))
            cur.execute("INSERT INTO order_status_history(order_id,status,note) VALUES(%s,'placed','Order created; stock reserved')",(oid,))
    return oid

def transition(order_id, new_status, actor_id=None, note=''):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT status FROM orders WHERE id=%s FOR UPDATE",(order_id,)); row=cur.fetchone()
            if not row: raise ValueError('Order not found')
            if new_status not in ALLOWED.get(row['status'],set()): raise ValueError(f"Invalid transition: {row['status']} → {new_status}")
            cur.execute("UPDATE orders SET status=%s,updated_at=NOW() WHERE id=%s",(new_status,order_id))
            cur.execute("INSERT INTO order_status_history(order_id,status,actor_id,note) VALUES(%s,%s,%s,%s)",(order_id,new_status,actor_id,note))

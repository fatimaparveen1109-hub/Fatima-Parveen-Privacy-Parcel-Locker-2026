from db import get_conn, one, query, execute
from datetime import timedelta

def reserve_locker(order_id, hub_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM lockers WHERE hub_id=%s AND status='available' ORDER BY CASE size WHEN 'Small' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END,id FOR UPDATE SKIP LOCKED LIMIT 1",(hub_id,))
            locker=cur.fetchone()
            if not locker: return None
            cur.execute("UPDATE lockers SET status='reserved' WHERE id=%s",(locker['id'],))
            cur.execute("UPDATE orders SET locker_id=%s,status='waiting_locker',updated_at=NOW() WHERE id=%s",(locker['id'],order_id))
            return locker['id']

def deposit(order_id):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT locker_id FROM orders WHERE id=%s FOR UPDATE",(order_id,)); o=cur.fetchone()
            if not o or not o['locker_id']: raise ValueError('No locker assigned')
            cur.execute("UPDATE lockers SET status='occupied' WHERE id=%s",(o['locker_id'],))
            cur.execute("UPDATE orders SET status='deposited',deposited_at=NOW(),pickup_expires_at=NOW()+INTERVAL '48 hours' WHERE id=%s",(order_id,))
            cur.execute("UPDATE qr_tokens SET is_valid=FALSE WHERE order_id=%s AND token_type='CUSTOMER_PICKUP'",(order_id,))

def hubs(): return query("SELECT * FROM hubs WHERE is_active=TRUE ORDER BY name")

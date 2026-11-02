from db import one, execute

PHOTO_REASONS={'Wrong item','Damaged item','Defective item','Missing item'}
def request_return(order_id, customer_id, reason, details, photo_bytes=None):
    o=one("SELECT status,collected_at FROM orders WHERE id=%s AND customer_id=%s",(order_id,customer_id))
    if not o or o['status']!='collected': raise ValueError('Only collected orders can be returned')
    if reason in PHOTO_REASONS and not photo_bytes: raise ValueError('Photo evidence is required for this reason')
    r=one("INSERT INTO returns(order_id,customer_id,reason,details,evidence) VALUES(%s,%s,%s,%s,%s) RETURNING id",(order_id,customer_id,reason,details,photo_bytes))
    execute("UPDATE orders SET status='return_requested' WHERE id=%s",(order_id,)); return r['id']

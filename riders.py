from db import one

def assign_rider(order_id):
    rider=one("SELECT r.id,r.user_id FROM riders r JOIN users u ON u.id=r.user_id WHERE u.status='active' AND r.is_available=TRUE AND (SELECT COUNT(*) FROM deliveries d WHERE d.rider_id=r.id AND d.status IN ('assigned','accepted','in_transit')) < 3 ORDER BY (SELECT COUNT(*) FROM deliveries d WHERE d.rider_id=r.id AND d.status IN ('assigned','accepted','in_transit')),r.id FOR UPDATE SKIP LOCKED LIMIT 1")
    if not rider: return None
    return one("INSERT INTO deliveries(order_id,rider_id,status) VALUES(%s,%s,'assigned') RETURNING id",(order_id,rider['id']))

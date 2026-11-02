from db import query, execute

def expire_pickups():
    rows=query("UPDATE orders SET status='expired_review',updated_at=NOW() WHERE status='deposited' AND pickup_expires_at<NOW() RETURNING id,customer_id")
    for r in rows:
        execute("INSERT INTO notifications(user_id,title,body,kind) VALUES(%s,'Parcel needs review','Your 48-hour pickup window expired. An administrator will review the parcel; it will not be returned automatically.','warning')",(r['customer_id'],))
    return len(rows)

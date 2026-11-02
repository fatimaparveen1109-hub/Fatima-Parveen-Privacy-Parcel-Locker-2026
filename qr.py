import secrets, hashlib, io, qrcode
from datetime import datetime, timedelta, timezone
from db import one, execute

def issue_token(order_id, holder_id, token_type, expiry_hours=48):
    raw=secrets.token_urlsafe(32); digest=hashlib.sha256(raw.encode()).hexdigest()
    pin=f'{secrets.randbelow(1000000):06d}'
    execute("UPDATE qr_tokens SET is_valid=FALSE WHERE order_id=%s AND token_type=%s",(order_id,token_type))
    one("INSERT INTO qr_tokens(order_id,holder_id,token_type,token_hash,pin_hash,expires_at) VALUES(%s,%s,%s,%s,%s,NOW()+(%s * INTERVAL '1 hour')) RETURNING id",
        (order_id,holder_id,token_type,digest,hashlib.sha256(pin.encode()).hexdigest(),expiry_hours))
    return raw,pin

def validate_token(raw, order_id, holder_id, token_type):
    digest=hashlib.sha256(raw.encode()).hexdigest()
    row=one("SELECT * FROM qr_tokens WHERE token_hash=%s AND order_id=%s AND holder_id=%s AND token_type=%s",(digest,order_id,holder_id,token_type))
    if not row or not row['is_valid'] or row['used_at'] or row['expires_at'] < datetime.now(timezone.utc): return False
    execute("UPDATE qr_tokens SET used_at=NOW(),is_valid=FALSE WHERE id=%s",(row['id'],)); return True

def qr_png(raw):
    image=qrcode.make(raw); out=io.BytesIO(); image.save(out,format='PNG'); return out.getvalue()

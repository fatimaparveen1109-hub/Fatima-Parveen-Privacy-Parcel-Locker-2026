from db import query, execute

def notify(user_id, title, body, kind='info'):
    execute("INSERT INTO notifications(user_id,title,body,kind) VALUES(%s,%s,%s,%s)",(user_id,title,body,kind))
def get_notifications(user_id):
    return query("SELECT * FROM notifications WHERE user_id=%s ORDER BY created_at DESC LIMIT 50",(user_id,))

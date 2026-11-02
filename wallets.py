from db import one, execute

def balance(user_id):
    row=one("SELECT balance_pkr FROM wallets WHERE user_id=%s",(user_id,)); return row['balance_pkr'] if row else 0

def add_demo_credit(user_id, amount, note='Demo credit'):
    if amount <= 0: raise ValueError('Amount must be positive')
    execute("INSERT INTO wallets(user_id,balance_pkr) VALUES(%s,%s) ON CONFLICT(user_id) DO UPDATE SET balance_pkr=wallets.balance_pkr+EXCLUDED.balance_pkr",(user_id,amount))
    execute("INSERT INTO wallet_transactions(user_id,amount_pkr,kind,note) VALUES(%s,%s,'credit',%s)",(user_id,amount,note))

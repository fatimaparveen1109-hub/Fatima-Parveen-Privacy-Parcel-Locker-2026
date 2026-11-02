import streamlit as st
from pathlib import Path
from db import db_ready, query, one, execute
from services.auth import register_user, login
from services.catalog import products
from services.orders import place_order
from services.lockers import hubs
from services.payments import simulate_payment
from services.qr import issue_token, qr_png

st.set_page_config(page_title='Privacy Parcel Locker',page_icon='🔐',layout='wide')
ASSET=Path(__file__).parent/'assets'
NAVY='#0F172A'; BLUE='#2563EB'; TEAL='#0D9488'; PURPLE='#7C3AED'
st.markdown('''<style>@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');html,body,[class*="css"]{font-family:Inter,sans-serif} .block-container{padding-top:1.2rem;max-width:1300px}.hero{background:linear-gradient(115deg,#eff6ff,#fff 58%,#ecfeff);padding:2.4rem;border-radius:24px;border:1px solid #dbeafe}.hero h1{font-family:'Plus Jakarta Sans';font-size:3rem;color:#0f172a;line-height:1.1}.hero p{font-size:1.12rem;color:#475569}.tile{background:white;border:1px solid #e2e8f0;border-radius:18px;padding:18px;box-shadow:0 8px 25px #0f172a0a}.muted{color:#64748b}.stButton>button{border-radius:12px;font-weight:600}.role{padding:16px;border-radius:15px;color:white;font-weight:700;text-align:center}</style>''',unsafe_allow_html=True)

def db_status():
 ok,msg=db_ready()
 if not ok: st.error('Database not connected. Complete Supabase setup in README, then add DATABASE_URL in Streamlit Secrets.'); st.code(msg[:500]); return False
 return True

def landing():
 st.markdown('<div class="hero">',unsafe_allow_html=True)
 a,b=st.columns([1.15,1])
 with a:
  st.markdown('### 🔐 Privacy Parcel Locker')
  st.markdown('<h1>Secure. <span style="color:#2563eb">Smart.</span> <span style="color:#0d9488">Private.</span></h1>',unsafe_allow_html=True)
  st.markdown('<p>Your parcels, our priority. Safe and contactless parcel delivery with Privacy Parcel Locker.</p>',unsafe_allow_html=True)
  if st.button('Get Started →',type='primary'): st.session_state.page='auth'; st.rerun()
 with b:
  st.image(str(ASSET/'hero_locker.jpg'),use_container_width=True)
 st.markdown('</div>',unsafe_allow_html=True)
 st.markdown('## How It Works')
 steps=[('01','Shop Online','Browse products from trusted sellers.'),('02','Choose Your Hub','Select your preferred collection hub.'),('03','Get QR Code','Receive a unique QR code and PIN.'),('04','Collect Securely','Scan and collect from your locker.'),('05','Enjoy!','Your parcel is safe and secure.')]
 cols=st.columns(5)
 for c,(n,t,d) in zip(cols,steps):
  with c: st.markdown(f'<div class="tile"><h2 style="color:#2563eb">{n}</h2><b>{t}</b><p class="muted">{d}</p></div>',unsafe_allow_html=True)
 st.markdown('## Powerful Features')
 feats=['🛡️ Privacy protection','▦ QR authentication','🔒 Secure locker collection','📍 Multiple collection hubs','🔔 Notifications','↩️ Return management']
 cols=st.columns(3)
 for c,f in zip(cols,feats):
  with c: st.markdown(f'<div class="tile">{f}</div>',unsafe_allow_html=True)
 st.markdown('## Choose Your Role')
 cols=st.columns(4)
 for c,(role,color) in zip(cols,[('Customer',BLUE),('Seller',TEAL),('Rider',PURPLE),('Admin',NAVY)]):
  with c:
   st.markdown(f'<div class="role" style="background:{color}">{role}</div>',unsafe_allow_html=True)
   if st.button(f'{role} Login',key='role_'+role): st.session_state.role_hint=role.lower(); st.session_state.page='auth'; st.rerun()
 st.markdown('---')
 st.caption('Privacy Policy  ·  Terms  ·  Contact  ·  Return Policy | Privacy Parcel Locker')

def auth_page():
 st.title('Welcome to Privacy Parcel Locker')
 tab1,tab2=st.tabs(['Login','Create account'])
 with tab1:
  with st.form('login'):
   email=st.text_input('Email'); password=st.text_input('Password',type='password'); submit=st.form_submit_button('Login',type='primary')
  if submit:
   try:
    user=login(email,password)
    if user: st.session_state.user=user; st.session_state.page='portal'; st.rerun()
    else: st.error('Email or password is incorrect.')
   except Exception as e: st.error(str(e))
 with tab2:
  with st.form('register'):
   name=st.text_input('Full name / Store name'); email=st.text_input('Email address',key='reg_email'); role=st.selectbox('Account type',['customer','seller','rider']); password=st.text_input('Password (minimum 10 characters)',type='password',key='reg_pass'); confirm=st.text_input('Confirm password',type='password'); go=st.form_submit_button('Register')
  if go:
   if password!=confirm: st.error('Passwords do not match.')
   else:
    try:
     register_user(name,email,password,role); st.success('Account created. Seller and rider accounts require admin approval; customer accounts can log in.')
    except Exception as e: st.error(str(e))

def portal():
 u=st.session_state.user; role=u['role']
 with st.sidebar:
  st.title('🔐 PPL Portal'); st.write(f"**{u['name']}**"); st.caption(role.title())
  page=st.radio('Navigation', ['Dashboard','Catalogue / Orders','Account & Help'])
  if st.button('Logout'): st.session_state.clear(); st.session_state.page='home'; st.rerun()
 st.title(f'{role.title()} Portal')
 if role=='customer': customer(u,page)
 elif role=='seller': seller(u,page)
 elif role=='rider': rider(u,page)
 elif role=='admin': admin(u,page)

def customer(u,page):
 if page=='Dashboard':
  st.subheader('Your delivery dashboard')
  orders=query('SELECT id,status,total_pkr,created_at FROM orders WHERE customer_id=%s ORDER BY id DESC LIMIT 20',(u['id'],))
  st.metric('Total orders',len(orders)); st.dataframe(orders,use_container_width=True)
 elif page=='Catalogue / Orders':
  st.subheader('Customer catalogue')
  ps=products(); cart={}
  if 'cart' not in st.session_state: st.session_state.cart={}
  cols=st.columns(4)
  for i,p in enumerate(ps):
   with cols[i%4]:
    st.image(str(ASSET/p['image_file']),use_container_width=True)
    st.markdown(f"**{p['name']}**")
    st.caption(f"{p['seller_name']} · {p['parcel_size']} · Stock {p['stock_qty']}")
    st.write(f"Rs. {p['price_pkr']:,}")
    q=st.number_input('Quantity',0,10,0,key=f"qty_{p['id']}")
    if q: st.session_state.cart[str(p['id'])]=q
  st.markdown('---'); st.subheader('Place order')
  hs=hubs()
  if not hs: st.warning('No active hubs found. Ask admin to seed hubs.'); return
  opts={h['name']:h['id'] for h in hs}; hname=st.selectbox('Preferred collection hub',list(opts)); alt=st.selectbox('Alternative hub (optional)', ['None']+list(opts)); opt=st.checkbox('I explicitly allow use of my alternative hub')
  timing=st.selectbox('Payment timing',['NOW','AFTER_DEPOSIT'])
  if st.button('Place order',type='primary'):
   if not st.session_state.cart: st.error('Add at least one product first.')
   else:
    try:
     oid=place_order(u['id'],st.session_state.cart,opts[hname],opts[alt] if alt!='None' else None,opt)
     st.session_state.cart={}
     st.success(f'Order #{oid} created. Payment timing: {timing}. Demo payment can be completed from the order details after setup.')
    except Exception as e: st.error(str(e))
  st.caption('Demo charges: products + Rs. 30 rider delivery + Rs. 60 locker fee. No real card or bank details are requested.')
 else:
  st.subheader('Support & privacy'); st.info('Sellers and riders do not receive your private home address or phone number. Hardware unlocking is simulated until the hardware API is supplied.')

def seller(u,page):
 seller=one('SELECT id,store_name FROM sellers WHERE user_id=%s',(u['id'],))
 if not seller: st.warning('Seller profile missing.'); return
 if page=='Dashboard':
  rows=query('SELECT id,name,price_pkr,stock_qty,is_active FROM products WHERE seller_id=%s ORDER BY id',(seller['id'],)); st.dataframe(rows,use_container_width=True)
  st.metric('Listed products',len(rows))
 elif page=='Catalogue / Orders':
  st.subheader('Manage your products')
  with st.form('newprod'):
   name=st.text_input('Product name'); desc=st.text_area('Description'); price=st.number_input('Price (PKR)',min_value=1,step=100); stock=st.number_input('Stock',min_value=0,step=1); size=st.selectbox('Parcel size',['Small','Medium','Large']); image=st.selectbox('Image asset',['earbuds.jpg','smartwatch.jpg','backpack.jpg','sunglasses.jpg','shoes.jpg','shirt.jpg','hoodie.jpg','cap.jpg']); save=st.form_submit_button('Add product')
  if save:
   try:
    from services.catalog import upsert_product
    upsert_product(seller['id'],None,name,desc,int(price),int(stock),size,image); st.success('Product added.')
   except Exception as e: st.error(str(e))
  st.subheader('Orders for your products')
  rows=query('SELECT DISTINCT o.id,o.status,o.total_pkr,o.created_at FROM orders o JOIN order_items i ON i.order_id=o.id WHERE i.seller_id=%s ORDER BY o.id DESC',(seller['id'],)); st.dataframe(rows,use_container_width=True)
 else: st.info('Seller support and notifications will appear here. Customer private contact details are never displayed.')

def rider(u,page):
 r=one('SELECT id FROM riders WHERE user_id=%s',(u['id'],))
 if not r: st.warning('Rider profile missing.'); return
 rows=query('SELECT id,status,created_at FROM deliveries WHERE rider_id=%s ORDER BY id DESC',(r['id'],))
 st.subheader('Assigned deliveries'); st.dataframe(rows,use_container_width=True)
 st.info('Rider view intentionally excludes customer names, addresses, phone numbers and product details. Hardware scanning is simulated pending the partner API.')

def admin(u,page):
 st.subheader('Administration')
 if page=='Dashboard':
  for table in ['users','products','orders','hubs','lockers']:
   try: st.metric(table.replace('_',' ').title(),one(f'SELECT COUNT(*) n FROM {table}')['n'])
   except Exception: st.metric(table,0)
 elif page=='Catalogue / Orders':
  st.markdown('**Pending approvals**')
  pending=query("SELECT id,name,email,role,status FROM users WHERE status='pending' ORDER BY id")
  for x in pending:
   c1,c2=st.columns([3,1]); c1.write(f"{x['name']} · {x['email']} · {x['role']}")
   if c2.button('Approve',key=f"approve{x['id']}"): execute("UPDATE users SET status='active' WHERE id=%s",(x['id'],)); st.rerun()
  st.markdown('**Orders**'); st.dataframe(query('SELECT id,customer_id,status,total_pkr,payment_status FROM orders ORDER BY id DESC LIMIT 100'),use_container_width=True)
  st.markdown('**Products**'); st.dataframe(query('SELECT id,name,price_pkr,stock_qty,is_active FROM products ORDER BY id'),use_container_width=True)
 else: st.info('Admin-only operational actions are logged where implemented. Add production payment and hardware providers before real-world operation.')

if 'page' not in st.session_state: st.session_state.page='home'
if 'user' in st.session_state: portal()
elif st.session_state.page=='auth': auth_page()
else: landing()

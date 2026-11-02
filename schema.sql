-- Privacy Parcel Locker schema for Supabase PostgreSQL
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE TABLE IF NOT EXISTS users (
 id BIGSERIAL PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
 password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('customer','seller','rider')),
 status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('pending','active','suspended')),
 created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS customer_private_details (
 user_id BIGINT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
 phone_encrypted BYTEA, address_encrypted BYTEA, created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS sellers (id BIGSERIAL PRIMARY KEY,user_id BIGINT UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,store_name TEXT NOT NULL,approved_at TIMESTAMPTZ,created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS riders (id BIGSERIAL PRIMARY KEY,user_id BIGINT UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,is_available BOOLEAN NOT NULL DEFAULT TRUE,approved_at TIMESTAMPTZ,created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS hubs (id BIGSERIAL PRIMARY KEY,name TEXT NOT NULL UNIQUE,address TEXT NOT NULL DEFAULT '',is_active BOOLEAN NOT NULL DEFAULT TRUE,created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS lockers (id BIGSERIAL PRIMARY KEY,hub_id BIGINT NOT NULL REFERENCES hubs(id),locker_code TEXT NOT NULL,size TEXT NOT NULL CHECK(size IN ('Small','Medium','Large')),status TEXT NOT NULL DEFAULT 'available' CHECK(status IN ('available','reserved','occupied','maintenance')),UNIQUE(hub_id,locker_code));
CREATE TABLE IF NOT EXISTS products (id BIGSERIAL PRIMARY KEY,seller_id BIGINT NOT NULL REFERENCES sellers(id),name TEXT NOT NULL,description TEXT NOT NULL DEFAULT '',price_pkr INTEGER NOT NULL CHECK(price_pkr>0),stock_qty INTEGER NOT NULL DEFAULT 0 CHECK(stock_qty>=0),parcel_size TEXT NOT NULL CHECK(parcel_size IN ('Small','Medium','Large')),image_file TEXT NOT NULL DEFAULT 'earbuds.jpg',is_active BOOLEAN NOT NULL DEFAULT TRUE,created_at TIMESTAMPTZ DEFAULT NOW(),updated_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS orders (id BIGSERIAL PRIMARY KEY,customer_id BIGINT NOT NULL REFERENCES users(id),hub_id BIGINT NOT NULL REFERENCES hubs(id),alternative_hub_id BIGINT REFERENCES hubs(id),alternative_opt_in BOOLEAN NOT NULL DEFAULT FALSE,locker_id BIGINT REFERENCES lockers(id),product_total_pkr INTEGER NOT NULL,rider_fee_pkr INTEGER NOT NULL DEFAULT 30,locker_fee_pkr INTEGER NOT NULL DEFAULT 60,total_pkr INTEGER NOT NULL,status TEXT NOT NULL DEFAULT 'placed',payment_status TEXT NOT NULL DEFAULT 'pending',deposited_at TIMESTAMPTZ,pickup_expires_at TIMESTAMPTZ,collected_at TIMESTAMPTZ,created_at TIMESTAMPTZ DEFAULT NOW(),updated_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS order_items (id BIGSERIAL PRIMARY KEY,order_id BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,product_id BIGINT REFERENCES products(id),seller_id BIGINT NOT NULL REFERENCES sellers(id),product_name TEXT NOT NULL,quantity INTEGER NOT NULL CHECK(quantity>0),unit_price_pkr INTEGER NOT NULL,parcel_size TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS payments (id BIGSERIAL PRIMARY KEY,order_id BIGINT NOT NULL REFERENCES orders(id),method TEXT NOT NULL,amount_pkr INTEGER NOT NULL,status TEXT NOT NULL CHECK(status IN ('verified','failed','refunded','pending')),reference TEXT UNIQUE,created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS wallets (user_id BIGINT PRIMARY KEY REFERENCES users(id),balance_pkr BIGINT NOT NULL DEFAULT 0 CHECK(balance_pkr>=0),updated_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS wallet_transactions (id BIGSERIAL PRIMARY KEY,user_id BIGINT NOT NULL REFERENCES users(id),amount_pkr BIGINT NOT NULL,kind TEXT NOT NULL,note TEXT,created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS deliveries (id BIGSERIAL PRIMARY KEY,order_id BIGINT NOT NULL REFERENCES orders(id),rider_id BIGINT NOT NULL REFERENCES riders(id),status TEXT NOT NULL DEFAULT 'assigned',created_at TIMESTAMPTZ DEFAULT NOW(),updated_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS qr_tokens (id BIGSERIAL PRIMARY KEY,order_id BIGINT NOT NULL REFERENCES orders(id),holder_id BIGINT REFERENCES users(id),token_type TEXT NOT NULL,token_hash TEXT NOT NULL UNIQUE,pin_hash TEXT NOT NULL,expires_at TIMESTAMPTZ NOT NULL,is_valid BOOLEAN NOT NULL DEFAULT TRUE,used_at TIMESTAMPTZ,failed_attempts INTEGER NOT NULL DEFAULT 0,created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS qr_scan_logs (id BIGSERIAL PRIMARY KEY,order_id BIGINT REFERENCES orders(id),actor_id BIGINT REFERENCES users(id),token_type TEXT,success BOOLEAN NOT NULL,reason TEXT,created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS returns (id BIGSERIAL PRIMARY KEY,order_id BIGINT NOT NULL REFERENCES orders(id),customer_id BIGINT NOT NULL REFERENCES users(id),reason TEXT NOT NULL,details TEXT,evidence BYTEA,status TEXT NOT NULL DEFAULT 'requested',seller_inspection TEXT,created_at TIMESTAMPTZ DEFAULT NOW(),updated_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS notifications (id BIGSERIAL PRIMARY KEY,user_id BIGINT NOT NULL REFERENCES users(id),title TEXT NOT NULL,body TEXT NOT NULL,kind TEXT NOT NULL DEFAULT 'info',is_read BOOLEAN NOT NULL DEFAULT FALSE,created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS messages (id BIGSERIAL PRIMARY KEY,sender_id BIGINT NOT NULL REFERENCES users(id),recipient_id BIGINT NOT NULL REFERENCES users(id),body TEXT NOT NULL,created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS complaints (id BIGSERIAL PRIMARY KEY,customer_id BIGINT NOT NULL REFERENCES users(id),order_id BIGINT REFERENCES orders(id),subject TEXT NOT NULL,body TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'open',created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS order_status_history (id BIGSERIAL PRIMARY KEY,order_id BIGINT NOT NULL REFERENCES orders(id),status TEXT NOT NULL,actor_id BIGINT REFERENCES users(id),note TEXT,created_at TIMESTAMPTZ DEFAULT NOW());
CREATE TABLE IF NOT EXISTS audit_logs (id BIGSERIAL PRIMARY KEY,actor_id BIGINT REFERENCES users(id),action TEXT NOT NULL,entity_type TEXT,entity_id BIGINT,details JSONB NOT NULL DEFAULT '{}'::jsonb,created_at TIMESTAMPTZ DEFAULT NOW());
CREATE INDEX IF NOT EXISTS idx_products_seller ON products(seller_id);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id,created_at DESC);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_deliveries_rider_status ON deliveries(rider_id,status);
CREATE INDEX IF NOT EXISTS idx_qr_tokens_lookup ON qr_tokens(token_hash,is_valid);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id,created_at DESC);

-- Initial hubs and locker inventory (5 hubs x 8 lockers: 4 small, 3 medium, 1 large)
INSERT INTO hubs(name,address) VALUES
 ('DHA','DHA, Karachi'),('Clifton','Clifton, Karachi'),('Saddar','Saddar, Karachi'),('Gulshan-e-Iqbal','Gulshan-e-Iqbal, Karachi'),('PECHS','PECHS, Karachi') ON CONFLICT(name) DO NOTHING;
INSERT INTO lockers(hub_id,locker_code,size)
SELECT h.id, v.code, v.size FROM hubs h CROSS JOIN (VALUES ('S01','Small'),('S02','Small'),('S03','Small'),('S04','Small'),('M01','Medium'),('M02','Medium'),('M03','Medium'),('L01','Large')) v(code,size)
ON CONFLICT(hub_id,locker_code) DO NOTHING;

-- Catalogue demo sellers have intentionally disabled login accounts; real sellers register separately.
INSERT INTO users(name,email,password_hash,role,status) VALUES
 ('Karim Traders','catalog-karim@privacyparcel.invalid','disabled$no-login','seller','suspended'),
 ('Noor Fashion','catalog-noor@privacyparcel.invalid','disabled$no-login','seller','suspended') ON CONFLICT(email) DO NOTHING;
INSERT INTO sellers(user_id,store_name)
SELECT id,name FROM users WHERE email IN ('catalog-karim@privacyparcel.invalid','catalog-noor@privacyparcel.invalid') ON CONFLICT(user_id) DO NOTHING;
INSERT INTO products(seller_id,name,description,price_pkr,stock_qty,parcel_size,image_file)
SELECT s.id,p.name,p.description,p.price,p.stock,p.size,p.image FROM sellers s JOIN users u ON u.id=s.user_id
JOIN (VALUES
 ('catalog-karim@privacyparcel.invalid','Wireless Earbuds','Compact white wireless earbuds with charging case.',4500,25,'Small','earbuds.jpg'),
 ('catalog-karim@privacyparcel.invalid','Smart Watch','Black smart watch for everyday notifications and activity.',7200,18,'Small','smartwatch.jpg'),
 ('catalog-karim@privacyparcel.invalid','Travel Backpack','Pink travel backpack with roomy compartments.',3800,20,'Large','backpack.jpg'),
 ('catalog-karim@privacyparcel.invalid','Sunglasses','Classic black sunglasses with dark lenses.',1800,30,'Small','sunglasses.jpg'),
 ('catalog-noor@privacyparcel.invalid','Running Shoes','Clean white everyday running sneakers.',5900,15,'Large','shoes.jpg'),
 ('catalog-noor@privacyparcel.invalid','Cotton Shirt','Sky-blue cotton shirt for casual wear.',3200,22,'Medium','shirt.jpg'),
 ('catalog-noor@privacyparcel.invalid','Hoodie','Black casual pullover hoodie.',4200,16,'Large','hoodie.jpg'),
 ('catalog-noor@privacyparcel.invalid','Cap','Black everyday baseball cap.',1200,35,'Small','cap.jpg')
) AS p(email,name,description,price,stock,size,image) ON u.email=p.email
WHERE NOT EXISTS (SELECT 1 FROM products old WHERE old.seller_id=s.id AND old.name=p.name);

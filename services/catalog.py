from db import query, one, execute

def products(active_only=True):
    where = "WHERE p.is_active=TRUE" if active_only else ""
    return query(f"""SELECT p.*, COALESCE(s.store_name,'') seller_name FROM products p
      LEFT JOIN sellers s ON s.id=p.seller_id {where} ORDER BY p.id""")

def product(product_id):
    return one("SELECT * FROM products WHERE id=%s", (product_id,))

def upsert_product(seller_id, product_id, name, description, price, stock, size, image):
    if product_id:
        execute("UPDATE products SET name=%s,description=%s,price_pkr=%s,stock_qty=%s,parcel_size=%s,image_file=%s,updated_at=NOW() WHERE id=%s AND seller_id=%s",
                (name,description,price,stock,size,image,product_id,seller_id))
    else:
        execute("INSERT INTO products(seller_id,name,description,price_pkr,stock_qty,parcel_size,image_file) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                (seller_id,name,description,price,stock,size,image))

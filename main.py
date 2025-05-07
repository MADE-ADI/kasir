import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, session

app = Flask(__name__)
app.secret_key = 'kasirwarungsaya123'  # Kunci rahasia untuk session

# Path untuk file JSON
PRODUCTS_FILE = 'data/products.json'
SALES_FILE = 'data/sales.json'

# Inisialisasi file JSON jika belum ada
def init_json_files():
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Inisialisasi products.json
    if not os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, 'w') as f:
            json.dump([], f)
    
    # Inisialisasi sales.json
    if not os.path.exists(SALES_FILE):
        with open(SALES_FILE, 'w') as f:
            json.dump([], f)

# Fungsi untuk membaca data dari file JSON
def read_json_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Fungsi untuk menulis data ke file JSON
def write_json_file(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

# Rute untuk halaman utama
@app.route('/')
def index():
    return render_template('index.html')

# Rute untuk halaman produk
@app.route('/products')
def products():
    all_products = read_json_file(PRODUCTS_FILE)
    return render_template('products.html', products=all_products)

# Rute untuk menambah produk baru
@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        products = read_json_file(PRODUCTS_FILE)
        
        # Cek ID produk tertinggi dan tambahkan 1
        next_id = 1
        if products:
            next_id = max(product['id'] for product in products) + 1
        
        new_product = {
            'id': next_id,
            'name': request.form['name'],
            'category': request.form['category'],
            'price': float(request.form['price']),
            'stock': int(request.form['stock']),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        products.append(new_product)
        write_json_file(PRODUCTS_FILE, products)
        
        return redirect(url_for('products'))
    
    return render_template('add_product.html')

# Rute untuk mengedit produk
@app.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    products = read_json_file(PRODUCTS_FILE)
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        return redirect(url_for('products'))
    
    if request.method == 'POST':
        for p in products:
            if p['id'] == product_id:
                p['name'] = request.form['name']
                p['category'] = request.form['category']
                p['price'] = float(request.form['price'])
                p['stock'] = int(request.form['stock'])
                p['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                break
        
        write_json_file(PRODUCTS_FILE, products)
        return redirect(url_for('products'))
    
    return render_template('edit_product.html', product=product)

# Rute untuk menghapus produk
@app.route('/products/delete/<int:product_id>')
def delete_product(product_id):
    products = read_json_file(PRODUCTS_FILE)
    products = [p for p in products if p['id'] != product_id]
    write_json_file(PRODUCTS_FILE, products)
    
    return redirect(url_for('products'))

# Rute untuk halaman kasir
@app.route('/cashier')
def cashier():
    products = read_json_file(PRODUCTS_FILE)
    return render_template('cashier.html', products=products)

# Rute API untuk mendapatkan data produk
@app.route('/api/products')
def api_products():
    products = read_json_file(PRODUCTS_FILE)
    return jsonify(products)

# Rute API untuk mendapatkan data produk berdasarkan ID
@app.route('/api/products/<int:product_id>')
def api_product(product_id):
    products = read_json_file(PRODUCTS_FILE)
    product = next((p for p in products if p['id'] == product_id), None)
    
    if product:
        return jsonify(product)
    return jsonify({'error': 'Product not found'}), 404

# Rute untuk memproses transaksi penjualan
@app.route('/sales/process', methods=['POST'])
def process_sale():
    try:
        data = request.json
        items = data.get('items', [])
        total = data.get('total', 0)
        payment = data.get('payment', 0)
        change = data.get('change', 0)
        
        # Update stok produk
        products = read_json_file(PRODUCTS_FILE)
        updated_products = products.copy()
        
        for item in items:
            product_id = item['id']
            quantity = item['quantity']
            
            product_found = False
            for p in updated_products:
                if p['id'] == product_id:
                    product_found = True
                    if p['stock'] < quantity:
                        return jsonify({'success': False, 'error': f'Stok produk {p["name"]} tidak mencukupi'}), 400
                    p['stock'] -= quantity
                    break
            
            if not product_found:
                return jsonify({'success': False, 'error': f'Produk dengan ID {product_id} tidak ditemukan'}), 404
        
        write_json_file(PRODUCTS_FILE, updated_products)
        
        # Simpan data penjualan
        sales = read_json_file(SALES_FILE)
        
        # Cek ID penjualan tertinggi dan tambahkan 1
        next_id = 1
        if sales:
            next_id = max(sale['id'] for sale in sales) + 1
        
        new_sale = {
            'id': next_id,
            'items': items,
            'total': total,
            'payment': payment,
            'change': change,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        sales.append(new_sale)
        write_json_file(SALES_FILE, sales)
        
        return jsonify({'success': True, 'sale_id': next_id})
    
    except Exception as e:
        print(f"Error in process_sale: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Rute untuk melihat riwayat penjualan
@app.route('/sales')
def sales():
    all_sales = read_json_file(SALES_FILE)
    return render_template('sales.html', sales=all_sales)

# Rute untuk melihat detail penjualan
@app.route('/sales/<int:sale_id>')
def sale_detail(sale_id):
    sales = read_json_file(SALES_FILE)
    sale = next((s for s in sales if s['id'] == sale_id), None)
    
    if not sale:
        return redirect(url_for('sales'))
    
    return render_template('sale_detail.html', sale=sale)

# Rute untuk laporan penjualan hari ini
@app.route('/reports/daily')
def daily_report():
    sales = read_json_file(SALES_FILE)
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Filter penjualan hari ini
    daily_sales = [s for s in sales if s['date'].startswith(today)]
    
    # Hitung total penjualan
    total_sales = sum(s['total'] for s in daily_sales)
    
    return render_template('daily_report.html', sales=daily_sales, total=total_sales, date=today)

# Inisialisasi file JSON saat aplikasi dimulai
init_json_files()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
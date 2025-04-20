from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'kamal'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/product_master')
def product_master():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM prod_master')
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('product_master.html', products=products)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        hsn_code = request.form['hsn_code']
        type = request.form['type']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO prod_master (name, hsn_code, type) VALUES (%s, %s, %s)',
                      (name, hsn_code, type))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Product added successfully!', 'success')
        return redirect(url_for('product_master'))
    return render_template('add_product.html')

@app.route('/edit_product/<int:prod_id>', methods=['GET', 'POST'])
def edit_product(prod_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        name = request.form['name']
        hsn_code = request.form['hsn_code']
        type = request.form['type']
        
        cursor.execute('UPDATE prod_master SET name = %s, hsn_code = %s, type = %s WHERE prod_id = %s',
                      (name, hsn_code, type, prod_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('product_master'))
    
    cursor.execute('SELECT * FROM prod_master WHERE prod_id = %s', (prod_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<int:prod_id>')
def delete_product(prod_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM prod_master WHERE prod_id = %s', (prod_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('product_master'))

@app.route('/party_master')
def party_master():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM party_master')
    parties = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('party_master.html', parties=parties)

@app.route('/add_party', methods=['GET', 'POST'])
def add_party():
    if request.method == 'POST':
        party = request.form['party']
        gstin = request.form['gstin']
        address = request.form['address']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO party_master (party, gstin, address) VALUES (%s, %s, %s)',
                      (party, gstin, address))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Party added successfully!', 'success')
        return redirect(url_for('party_master'))
    return render_template('add_party.html')

@app.route('/edit_party/<int:p_id>', methods=['GET', 'POST'])
def edit_party(p_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        party = request.form['party']
        gstin = request.form['gstin']
        address = request.form['address']
        
        cursor.execute('UPDATE party_master SET party = %s, gstin = %s, address = %s WHERE p_id = %s',
                      (party, gstin, address, p_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Party updated successfully!', 'success')
        return redirect(url_for('party_master'))
    
    cursor.execute('SELECT * FROM party_master WHERE p_id = %s', (p_id,))
    party = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_party.html', party=party)

@app.route('/delete_party/<int:p_id>')
def delete_party(p_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM party_master WHERE p_id = %s', (p_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Party deleted successfully!', 'success')
    return redirect(url_for('party_master'))

@app.route('/incoming_bills')
def incoming_bills():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT ib.*, pm.party 
        FROM incoming_bills ib
        JOIN party_master pm ON ib.party_id = pm.p_id
        ORDER BY ib.s_no DESC
    ''')
    bills = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('incoming_bills.html', bills=bills)

@app.route('/add_incoming_bill', methods=['GET', 'POST'])
def add_incoming_bill():
    if request.method == 'POST':
        try:
            inv_id = request.form['inv_id']
            party_id = request.form['party_id']
            bill_date = request.form['bill_date']
            account_id = request.form.get('account_id')  # Optional field
            
            # Handle TDS values - convert empty strings to None
            tds_percent = request.form.get('tds_percentage')
            tds_percent = float(tds_percent) if tds_percent and tds_percent.strip() else None
            
            tds_amount = request.form.get('tds_amount')
            tds_amount = float(tds_amount) if tds_amount and tds_amount.strip() else None
            
            conn = get_db_connection()
            cursor = conn.cursor()

            # Find the first available serial number for incoming_bills
            cursor.execute("""
                SELECT MIN(t1.s_no + 1) as next_id
                FROM incoming_bills t1
                LEFT JOIN incoming_bills t2 ON t1.s_no + 1 = t2.s_no
                WHERE t2.s_no IS NULL
            """)
            result = cursor.fetchone()
            next_serial = result[0] if result[0] is not None else 1
            
            # Insert bill header with the next available serial number
            cursor.execute("""
                INSERT INTO incoming_bills (s_no, inv_id, party_id, bill_date, account_id, tds_percent, tds_amount, final_amount)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (next_serial, inv_id, party_id, bill_date, account_id, tds_percent, tds_amount, 0))
            bill_s_no = next_serial  # Use the assigned serial number
            
            # Insert bill items with sequential item_id
            items = request.form.getlist('items[]')
            final_amount = 0
            for i, product_id in enumerate(items):
                # Find the first available item_id for this bill
                cursor.execute("""
                    SELECT MIN(t1.item_id + 1) as next_id
                    FROM bill_items t1
                    LEFT JOIN bill_items t2 ON t1.item_id + 1 = t2.item_id
                    WHERE t2.item_id IS NULL AND t1.bill_s_no = %s
                """, (bill_s_no,))
                result = cursor.fetchone()
                next_item_id = result[0] if result[0] is not None else 1
                
                qty = float(request.form.getlist(f'item_{i}[]')[0])  # Quantity
                rate = float(request.form.getlist(f'item_{i}[]')[1])  # Rate
                gst = float(request.form.getlist(f'item_{i}[]')[2])   # GST
                
                sub_total = qty * rate
                gst_amount = (sub_total * gst) / 100
                sgst_amount = cgst_amount = gst_amount / 2
                total_amount = sub_total + gst_amount
                
                cursor.execute("""
                    INSERT INTO bill_items (item_id, bill_s_no, product_id, qty, rate, sub_total, 
                                          gst_percent, sgst_amount, cgst_amount, total_amount)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (next_item_id, bill_s_no, product_id, qty, rate, sub_total, gst, 
                      sgst_amount, cgst_amount, total_amount))
                
                final_amount += total_amount
            
            # Update the final amount
            cursor.execute("""
                UPDATE incoming_bills 
                SET final_amount = %s 
                WHERE s_no = %s
            """, (final_amount, bill_s_no))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Bill added successfully!', 'success')
            return redirect(url_for('incoming_bills'))
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
                cursor.close()
                conn.close()
            flash(f'Error adding bill: {str(e)}', 'danger')
            return redirect(url_for('add_incoming_bill'))
    
    # GET request - show form
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT p_id, party FROM party_master ORDER BY party")
    parties = cursor.fetchall()
    
    cursor.execute("SELECT a_id, name, type FROM accounts ORDER BY name")
    accounts = cursor.fetchall()
    
    cursor.execute("SELECT prod_id, name, type FROM prod_master ORDER BY name")
    products = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('add_incoming_bill.html', parties=parties, accounts=accounts, products=products)

@app.route('/view_bill/<int:s_no>')
def view_bill(s_no):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get bill details with party and account names
        cursor.execute("""
            SELECT ib.s_no, ib.inv_id, ib.bill_date, 
                   p.party as party_name, a.name as account_name,
                   ib.final_amount
            FROM incoming_bills ib
            LEFT JOIN party_master p ON ib.party_id = p.p_id
            LEFT JOIN accounts a ON ib.account_id = a.a_id
            WHERE ib.s_no = %s
        """, (s_no,))
        bill = cursor.fetchone()
        
        # Get bill items with product names
        cursor.execute("""
            SELECT bi.item_id, bi.qty, bi.rate, bi.sub_total, 
                   bi.gst_percent, bi.sgst_amount, bi.cgst_amount, bi.total_amount,
                   pm.name as product_name
            FROM bill_items bi
            LEFT JOIN prod_master pm ON bi.product_id = pm.prod_id
            WHERE bi.bill_s_no = %s
        """, (s_no,))
        items = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if not bill:
            flash('Bill not found', 'danger')
            return redirect(url_for('incoming_bills'))
            
        return render_template('view_bill.html', bill=bill, items=items)
        
    except Exception as e:
        flash(f'Error viewing bill: {str(e)}', 'danger')
        return redirect(url_for('incoming_bills'))

@app.route('/delete_incoming_bill/<int:s_no>')
def delete_incoming_bill(s_no):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Start transaction
        cursor.execute("START TRANSACTION")
        
        # Delete bill items first (due to foreign key constraint)
        cursor.execute('DELETE FROM bill_items WHERE bill_s_no = %s', (s_no,))
        
        # Delete the bill
        cursor.execute('DELETE FROM incoming_bills WHERE s_no = %s', (s_no,))
        
        # Update serial numbers for incoming_bills
        cursor.execute("SET @counter = 0")
        cursor.execute("""
            UPDATE incoming_bills 
            SET s_no = (@counter := @counter + 1) 
            ORDER BY s_no
        """)
        
        # Reset auto-increment for incoming_bills
        cursor.execute("""
            SELECT MAX(s_no) + 1 FROM incoming_bills
        """)
        next_auto_increment = cursor.fetchone()[0] or 1
        cursor.execute(f"ALTER TABLE incoming_bills AUTO_INCREMENT = {next_auto_increment}")
        
        # Update serial numbers for bill_items
        cursor.execute("""
            SET @counter = 0;
            UPDATE bill_items 
            SET item_id = (@counter := @counter + 1) 
            ORDER BY bill_s_no, item_id
        """)
        
        # Reset auto-increment for bill_items
        cursor.execute("""
            SELECT MAX(item_id) + 1 FROM bill_items
        """)
        next_auto_increment = cursor.fetchone()[0] or 1
        cursor.execute(f"ALTER TABLE bill_items AUTO_INCREMENT = {next_auto_increment}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Bill deleted successfully!', 'success')
        return redirect(url_for('incoming_bills'))
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            cursor.close()
            conn.close()
        flash(f'Error deleting bill: {str(e)}', 'danger')
        return redirect(url_for('incoming_bills'))

@app.route('/accounts')
def accounts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM accounts')
    accounts = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('accounts.html', accounts=accounts)

@app.route('/add_account', methods=['GET', 'POST'])
def add_account():
    if request.method == 'POST':
        name = request.form['name']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO accounts (name) VALUES (%s)', (name,))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Account added successfully!', 'success')
        return redirect(url_for('accounts'))
    return render_template('add_account.html')

@app.route('/edit_account/<int:a_id>', methods=['GET', 'POST'])
def edit_account(a_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        name = request.form['name']
        
        cursor.execute('UPDATE accounts SET name = %s WHERE a_id = %s',
                      (name, a_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Account updated successfully!', 'success')
        return redirect(url_for('accounts'))
    
    cursor.execute('SELECT * FROM accounts WHERE a_id = %s', (a_id,))
    account = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_account.html', account=account)

@app.route('/delete_account/<int:a_id>')
def delete_account(a_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM accounts WHERE a_id = %s', (a_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Account deleted successfully!', 'success')
    return redirect(url_for('accounts'))

@app.route('/party_ledger')
def party_ledger():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all parties
        cursor.execute("""
            SELECT p.p_id, p.party, 
                   COUNT(ib.s_no) as total_bills,
                   COALESCE(SUM(ib.final_amount), 0) as total_amount
            FROM party_master p
            LEFT JOIN incoming_bills ib ON p.p_id = ib.party_id
            GROUP BY p.p_id, p.party
            ORDER BY p.party
        """)
        parties = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('party_ledger.html', parties=parties)
        
    except Exception as e:
        flash(f'Error loading party ledger: {str(e)}', 'danger')
        return redirect(url_for('party_ledger'))

@app.route('/party_ledger/<int:party_id>')
def view_party_ledger(party_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get party details
        cursor.execute("""
            SELECT p.p_id, p.party
            FROM party_master p
            WHERE p.p_id = %s
        """, (party_id,))
        party = cursor.fetchone()
        
        if not party:
            flash('Party not found', 'danger')
            return redirect(url_for('party_ledger'))
        
        # Get all incoming bills for this party with running balance
        cursor.execute("""
            SELECT 
                ib.s_no,
                ib.inv_id as bill_no,
                ib.bill_date,
                ib.final_amount,
                'Incoming' as bill_type,
                @running_balance := @running_balance + ib.final_amount as running_balance
            FROM incoming_bills ib
            CROSS JOIN (SELECT @running_balance := 0) r
            WHERE ib.party_id = %s
            
            UNION ALL
            
            SELECT 
                ob.s_no,
                ob.bill_no,
                ob.bill_date,
                -ob.final_amount as final_amount,  -- Negative for outgoing bills
                'Outgoing' as bill_type,
                @running_balance := @running_balance - ob.final_amount as running_balance
            FROM outgoing_bills ob
            WHERE ob.party_id = %s
            
            ORDER BY bill_date, s_no
        """, (party_id, party_id))
        transactions = cursor.fetchall()
        
        # Get summary for incoming bills
        cursor.execute("""
            SELECT 
                COUNT(*) as total_incoming_bills,
                COALESCE(SUM(final_amount), 0) as total_incoming_amount,
                MIN(bill_date) as first_incoming_transaction,
                MAX(bill_date) as last_incoming_transaction
            FROM incoming_bills
            WHERE party_id = %s
        """, (party_id,))
        incoming_summary = cursor.fetchone()
        
        # Get summary for outgoing bills
        cursor.execute("""
            SELECT 
                COUNT(*) as total_outgoing_bills,
                COALESCE(SUM(final_amount), 0) as total_outgoing_amount,
                MIN(bill_date) as first_outgoing_transaction,
                MAX(bill_date) as last_outgoing_transaction
            FROM outgoing_bills
            WHERE party_id = %s
        """, (party_id,))
        outgoing_summary = cursor.fetchone()
        
        # Calculate net balance
        net_balance = incoming_summary['total_incoming_amount'] - outgoing_summary['total_outgoing_amount']
        
        cursor.close()
        conn.close()
        
        return render_template('view_party_ledger.html', 
                             party=party, 
                             transactions=transactions,
                             incoming_summary=incoming_summary,
                             outgoing_summary=outgoing_summary,
                             net_balance=net_balance)
        
    except Exception as e:
        flash(f'Error loading party transactions: {str(e)}', 'danger')
        return redirect(url_for('party_ledger'))

@app.route('/outgoing_bills')
def outgoing_bills():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT ob.*, pm.party 
        FROM outgoing_bills ob
        JOIN party_master pm ON ob.party_id = pm.p_id
        ORDER BY ob.s_no DESC
    ''')
    bills = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('outgoing_bills.html', bills=bills)

@app.route('/add_outgoing_bill', methods=['GET', 'POST'])
def add_outgoing_bill():
    if request.method == 'POST':
        try:
            bill_no = request.form['bill_no']
            party_id = request.form['party_id']
            bill_date = request.form['bill_date']
            account_id = request.form.get('account_id')  # Optional field
            
            # Handle TDS values - convert empty strings to None
            tds_percent = request.form.get('tds_percentage')
            tds_percent = float(tds_percent) if tds_percent and tds_percent.strip() else None
            
            tds_amount = request.form.get('tds_amount')
            tds_amount = float(tds_amount) if tds_amount and tds_amount.strip() else None
            
            conn = get_db_connection()
            cursor = conn.cursor()

            # Find the first available serial number for outgoing_bills
            cursor.execute("""
                SELECT MIN(t1.s_no + 1) as next_id
                FROM outgoing_bills t1
                LEFT JOIN outgoing_bills t2 ON t1.s_no + 1 = t2.s_no
                WHERE t2.s_no IS NULL
            """)
            result = cursor.fetchone()
            next_serial = result[0] if result[0] is not None else 1
            
            # Insert bill header with the next available serial number
            cursor.execute("""
                INSERT INTO outgoing_bills (s_no, bill_no, party_id, bill_date, account_id, tds_percent, tds_amount, final_amount)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (next_serial, bill_no, party_id, bill_date, account_id, tds_percent, tds_amount, 0))
            bill_s_no = next_serial  # Use the assigned serial number
            
            # Get all form data for items
            product_ids = request.form.getlist('product_id[]')
            quantities = request.form.getlist('qty[]')
            rates = request.form.getlist('rate[]')
            gst_percents = request.form.getlist('gst_percent[]')
            
            final_amount = 0
            for i in range(len(product_ids)):
                product_id = product_ids[i]
                qty = float(quantities[i])
                rate = float(rates[i])
                gst_percent = float(gst_percents[i])
                
                sub_total = qty * rate
                gst_amount = (sub_total * gst_percent) / 100
                sgst_amount = cgst_amount = gst_amount / 2
                total_amount = sub_total + gst_amount
                
                # Find the first available item_id for this bill
                cursor.execute("""
                    SELECT MIN(t1.item_id + 1) as next_id
                    FROM outgoing_bill_items t1
                    LEFT JOIN outgoing_bill_items t2 ON t1.item_id + 1 = t2.item_id
                    WHERE t2.item_id IS NULL AND t1.bill_s_no = %s
                """, (bill_s_no,))
                result = cursor.fetchone()
                next_item_id = result[0] if result[0] is not None else 1
                
                cursor.execute("""
                    INSERT INTO outgoing_bill_items (item_id, bill_s_no, product_id, qty, rate, sub_total, 
                                          gst_percent, sgst_amount, cgst_amount, total_amount)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (next_item_id, bill_s_no, product_id, qty, rate, sub_total, gst_percent, 
                      sgst_amount, cgst_amount, total_amount))
                
                final_amount += total_amount
            
            # Update the final amount
            cursor.execute("""
                UPDATE outgoing_bills 
                SET final_amount = %s 
                WHERE s_no = %s
            """, (final_amount, bill_s_no))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Bill added successfully!', 'success')
            return redirect(url_for('outgoing_bills'))
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
                cursor.close()
                conn.close()
            flash(f'Error adding bill: {str(e)}', 'danger')
            return redirect(url_for('add_outgoing_bill'))
    
    # GET request - show form
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get the next bill number
    cursor.execute("SELECT MAX(bill_no) as max_bill_no FROM outgoing_bills")
    result = cursor.fetchone()
    next_bill_no = 1 if result['max_bill_no'] is None else int(result['max_bill_no']) + 1
    
    cursor.execute("SELECT p_id, party FROM party_master ORDER BY party")
    parties = cursor.fetchall()
    
    cursor.execute("SELECT a_id, name, type FROM accounts ORDER BY name")
    accounts = cursor.fetchall()
    
    cursor.execute("SELECT prod_id, name, type FROM prod_master ORDER BY name")
    products = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('add_outgoing_bill.html', 
                         parties=parties, 
                         accounts=accounts, 
                         products=products,
                         next_bill_no=next_bill_no)

@app.route('/view_outgoing_bill/<int:s_no>')
def view_outgoing_bill(s_no):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get bill details with party and account names
        cursor.execute("""
            SELECT ob.s_no, ob.bill_no, ob.bill_date, 
                   p.party as party_name, a.name as account_name,
                   ob.final_amount
            FROM outgoing_bills ob
            LEFT JOIN party_master p ON ob.party_id = p.p_id
            LEFT JOIN accounts a ON ob.account_id = a.a_id
            WHERE ob.s_no = %s
        """, (s_no,))
        bill = cursor.fetchone()
        
        # Get bill items with product names
        cursor.execute("""
            SELECT bi.item_id, bi.qty, bi.rate, bi.sub_total, 
                   bi.gst_percent, bi.sgst_amount, bi.cgst_amount, bi.total_amount,
                   pm.name as product_name
            FROM outgoing_bill_items bi
            LEFT JOIN prod_master pm ON bi.product_id = pm.prod_id
            WHERE bi.bill_s_no = %s
        """, (s_no,))
        items = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if not bill:
            flash('Bill not found', 'danger')
            return redirect(url_for('outgoing_bills'))
            
        return render_template('view_outgoing_bill.html', bill=bill, items=items)
        
    except Exception as e:
        flash(f'Error viewing bill: {str(e)}', 'danger')
        return redirect(url_for('outgoing_bills'))

@app.route('/delete_outgoing_bill/<int:s_no>')
def delete_outgoing_bill(s_no):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Start transaction
        cursor.execute("START TRANSACTION")
        
        # Delete bill items first (due to foreign key constraint)
        cursor.execute('DELETE FROM outgoing_bill_items WHERE bill_s_no = %s', (s_no,))
        
        # Delete the bill
        cursor.execute('DELETE FROM outgoing_bills WHERE s_no = %s', (s_no,))
        
        # Update serial numbers for outgoing_bills
        cursor.execute("SET @counter = 0")
        cursor.execute("""
            UPDATE outgoing_bills 
            SET s_no = (@counter := @counter + 1) 
            ORDER BY s_no
        """)
        
        # Reset auto-increment for outgoing_bills
        cursor.execute("""
            SELECT MAX(s_no) + 1 FROM outgoing_bills
        """)
        next_auto_increment = cursor.fetchone()[0] or 1
        cursor.execute(f"ALTER TABLE outgoing_bills AUTO_INCREMENT = {next_auto_increment}")
        
        # Update serial numbers for outgoing_bill_items
        cursor.execute("SET @counter = 0")
        cursor.execute("""
            UPDATE outgoing_bill_items 
            SET item_id = (@counter := @counter + 1) 
            ORDER BY bill_s_no, item_id
        """)
        
        # Reset auto-increment for outgoing_bill_items
        cursor.execute("""
            SELECT MAX(item_id) + 1 FROM outgoing_bill_items
        """)
        next_auto_increment = cursor.fetchone()[0] or 1
        cursor.execute(f"ALTER TABLE outgoing_bill_items AUTO_INCREMENT = {next_auto_increment}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Bill deleted successfully!', 'success')
        return redirect(url_for('outgoing_bills'))
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            cursor.close()
            conn.close()
        flash(f'Error deleting bill: {str(e)}', 'danger')
        return redirect(url_for('outgoing_bills'))

@app.route('/edit_outgoing_bill/<int:s_no>', methods=['GET', 'POST'])
def edit_outgoing_bill(s_no):
    if request.method == 'POST':
        try:
            bill_no = request.form['bill_no']
            party_id = request.form['party_id']
            bill_date = request.form['bill_date']
            account_id = request.form.get('account_id')  # Optional field
            
            # Handle TDS values - convert empty strings to None
            tds_percent = request.form.get('tds_percentage')
            tds_percent = float(tds_percent) if tds_percent and tds_percent.strip() else None
            
            tds_amount = request.form.get('tds_amount')
            tds_amount = float(tds_amount) if tds_amount and tds_amount.strip() else None
            
            conn = get_db_connection()
            cursor = conn.cursor()

            # Update bill header
            cursor.execute("""
                UPDATE outgoing_bills 
                SET bill_no = %s, party_id = %s, bill_date = %s, 
                    account_id = %s, tds_percent = %s, tds_amount = %s
                WHERE s_no = %s
            """, (bill_no, party_id, bill_date, account_id, tds_percent, tds_amount, s_no))
            
            # Delete existing items
            cursor.execute('DELETE FROM outgoing_bill_items WHERE bill_s_no = %s', (s_no,))
            
            # Get all form data for items
            product_ids = request.form.getlist('product_id[]')
            quantities = request.form.getlist('qty[]')
            rates = request.form.getlist('rate[]')
            gst_percents = request.form.getlist('gst_percent[]')
            
            final_amount = 0
            for i in range(len(product_ids)):
                product_id = product_ids[i]
                qty = float(quantities[i])
                rate = float(rates[i])
                gst_percent = float(gst_percents[i])
                
                sub_total = qty * rate
                gst_amount = (sub_total * gst_percent) / 100
                sgst_amount = cgst_amount = gst_amount / 2
                total_amount = sub_total + gst_amount
                
                # Find the first available item_id for this bill
                cursor.execute("""
                    SELECT MIN(t1.item_id + 1) as next_id
                    FROM outgoing_bill_items t1
                    LEFT JOIN outgoing_bill_items t2 ON t1.item_id + 1 = t2.item_id
                    WHERE t2.item_id IS NULL AND t1.bill_s_no = %s
                """, (s_no,))
                result = cursor.fetchone()
                next_item_id = result[0] if result[0] is not None else 1
                
                cursor.execute("""
                    INSERT INTO outgoing_bill_items (item_id, bill_s_no, product_id, qty, rate, sub_total, 
                                          gst_percent, sgst_amount, cgst_amount, total_amount)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (next_item_id, s_no, product_id, qty, rate, sub_total, gst_percent, 
                      sgst_amount, cgst_amount, total_amount))
                
                final_amount += total_amount
            
            # Update the final amount
            cursor.execute("""
                UPDATE outgoing_bills 
                SET final_amount = %s 
                WHERE s_no = %s
            """, (final_amount, s_no))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Bill updated successfully!', 'success')
            return redirect(url_for('outgoing_bills'))
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
                cursor.close()
                conn.close()
            flash(f'Error updating bill: {str(e)}', 'danger')
            return redirect(url_for('edit_outgoing_bill', s_no=s_no))
    
    # GET request - show form with existing data
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get bill details
    cursor.execute("""
        SELECT * FROM outgoing_bills 
        WHERE s_no = %s
    """, (s_no,))
    bill = cursor.fetchone()
    
    if not bill:
        flash('Bill not found', 'danger')
        return redirect(url_for('outgoing_bills'))
    
    # Get bill items
    cursor.execute("""
        SELECT * FROM outgoing_bill_items 
        WHERE bill_s_no = %s
        ORDER BY item_id
    """, (s_no,))
    items = cursor.fetchall()
    
    # Get dropdown data
    cursor.execute("SELECT p_id, party FROM party_master ORDER BY party")
    parties = cursor.fetchall()
    
    cursor.execute("SELECT a_id, name, type FROM accounts ORDER BY name")
    accounts = cursor.fetchall()
    
    cursor.execute("SELECT prod_id, name, type FROM prod_master ORDER BY name")
    products = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('edit_outgoing_bill.html', 
                         bill=bill, 
                         items=items,
                         parties=parties, 
                         accounts=accounts, 
                         products=products)

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/reports/sales')
def sales_report():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get date range from query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        party_id = request.args.get('party_id')
        product_id = request.args.get('product_id')
        
        # Base query
        query = """
            SELECT 
                ob.bill_date,
                ob.bill_no,
                p.party as party_name,
                pm.name as product_name,
                obi.qty,
                obi.rate,
                obi.sub_total,
                obi.gst_percent,
                obi.sgst_amount,
                obi.cgst_amount,
                obi.total_amount
            FROM outgoing_bills ob
            JOIN outgoing_bill_items obi ON ob.s_no = obi.bill_s_no
            JOIN party_master p ON ob.party_id = p.p_id
            JOIN prod_master pm ON obi.product_id = pm.prod_id
            WHERE 1=1
        """
        params = []
        
        # Add filters
        if start_date:
            query += " AND ob.bill_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND ob.bill_date <= %s"
            params.append(end_date)
        if party_id:
            query += " AND ob.party_id = %s"
            params.append(party_id)
        if product_id:
            query += " AND obi.product_id = %s"
            params.append(product_id)
            
        query += " ORDER BY ob.bill_date DESC"
        
        cursor.execute(query, params)
        sales_data = cursor.fetchall()
        
        # Get parties and products for filters
        cursor.execute("SELECT p_id, party FROM party_master ORDER BY party")
        parties = cursor.fetchall()
        
        cursor.execute("SELECT prod_id, name FROM prod_master ORDER BY name")
        products = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('sales_report.html', 
                             sales_data=sales_data,
                             parties=parties,
                             products=products,
                             start_date=start_date,
                             end_date=end_date,
                             party_id=party_id,
                             product_id=product_id)
        
    except Exception as e:
        flash(f'Error generating sales report: {str(e)}', 'danger')
        return redirect(url_for('reports'))

@app.route('/reports/purchases')
def purchase_report():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get date range from query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        party_id = request.args.get('party_id')
        product_id = request.args.get('product_id')
        
        # Base query
        query = """
            SELECT 
                ib.bill_date,
                ib.inv_id as bill_no,
                p.party as party_name,
                pm.name as product_name,
                bi.qty,
                bi.rate,
                bi.sub_total,
                bi.gst_percent,
                bi.sgst_amount,
                bi.cgst_amount,
                bi.total_amount
            FROM incoming_bills ib
            JOIN bill_items bi ON ib.s_no = bi.bill_s_no
            JOIN party_master p ON ib.party_id = p.p_id
            JOIN prod_master pm ON bi.product_id = pm.prod_id
            WHERE 1=1
        """
        params = []
        
        # Add filters
        if start_date:
            query += " AND ib.bill_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND ib.bill_date <= %s"
            params.append(end_date)
        if party_id:
            query += " AND ib.party_id = %s"
            params.append(party_id)
        if product_id:
            query += " AND bi.product_id = %s"
            params.append(product_id)
            
        query += " ORDER BY ib.bill_date DESC"
        
        cursor.execute(query, params)
        purchase_data = cursor.fetchall()
        
        # Get parties and products for filters
        cursor.execute("SELECT p_id, party FROM party_master ORDER BY party")
        parties = cursor.fetchall()
        
        cursor.execute("SELECT prod_id, name FROM prod_master ORDER BY name")
        products = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('purchase_report.html', 
                             purchase_data=purchase_data,
                             parties=parties,
                             products=products,
                             start_date=start_date,
                             end_date=end_date,
                             party_id=party_id,
                             product_id=product_id)
        
    except Exception as e:
        flash(f'Error generating purchase report: {str(e)}', 'danger')
        return redirect(url_for('reports'))

@app.route('/reports/party_wise')
def party_wise_report():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get party ID from query parameters
        party_id = request.args.get('party_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not party_id:
            # Show party selection if no party selected
            cursor.execute("SELECT p_id, party FROM party_master ORDER BY party")
            parties = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template('party_wise_report.html', parties=parties)
        
        # Get party details
        cursor.execute("SELECT party FROM party_master WHERE p_id = %s", (party_id,))
        party = cursor.fetchone()
        
        # Get incoming bills
        query = """
            SELECT 
                'Incoming' as type,
                ib.bill_date,
                ib.inv_id as bill_no,
                bi.qty,
                bi.rate,
                bi.sub_total,
                bi.gst_percent,
                bi.sgst_amount,
                bi.cgst_amount,
                bi.total_amount,
                pm.name as product_name
            FROM incoming_bills ib
            JOIN bill_items bi ON ib.s_no = bi.bill_s_no
            JOIN prod_master pm ON bi.product_id = pm.prod_id
            WHERE ib.party_id = %s
        """
        params = [party_id]
        
        if start_date:
            query += " AND ib.bill_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND ib.bill_date <= %s"
            params.append(end_date)
            
        # Get outgoing bills
        query += """
            UNION ALL
            SELECT 
                'Outgoing' as type,
                ob.bill_date,
                ob.bill_no,
                obi.qty,
                obi.rate,
                obi.sub_total,
                obi.gst_percent,
                obi.sgst_amount,
                obi.cgst_amount,
                obi.total_amount,
                pm.name as product_name
            FROM outgoing_bills ob
            JOIN outgoing_bill_items obi ON ob.s_no = obi.bill_s_no
            JOIN prod_master pm ON obi.product_id = pm.prod_id
            WHERE ob.party_id = %s
        """
        params.append(party_id)
        
        if start_date:
            query += " AND ob.bill_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND ob.bill_date <= %s"
            params.append(end_date)
            
        query += " ORDER BY bill_date DESC"
        
        cursor.execute(query, params)
        transactions = cursor.fetchall()
        
        # Get parties for filter
        cursor.execute("SELECT p_id, party FROM party_master ORDER BY party")
        parties = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('party_wise_report.html',
                             party=party,
                             parties=parties,
                             transactions=transactions,
                             party_id=party_id,
                             start_date=start_date,
                             end_date=end_date)
        
    except Exception as e:
        flash(f'Error generating party-wise report: {str(e)}', 'danger')
        return redirect(url_for('reports'))

@app.route('/reports/product_wise')
def product_wise_report():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get product ID from query parameters
        product_id = request.args.get('product_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not product_id:
            # Show product selection if no product selected
            cursor.execute("SELECT prod_id, name FROM prod_master ORDER BY name")
            products = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template('product_wise_report.html', products=products)
        
        # Get product details
        cursor.execute("SELECT name FROM prod_master WHERE prod_id = %s", (product_id,))
        product = cursor.fetchone()
        
        # Get incoming bills
        query = """
            SELECT 
                'Purchase' as type,
                ib.bill_date,
                ib.inv_id as bill_no,
                p.party as party_name,
                bi.qty,
                bi.rate,
                bi.sub_total,
                bi.gst_percent,
                bi.sgst_amount,
                bi.cgst_amount,
                bi.total_amount
            FROM incoming_bills ib
            JOIN bill_items bi ON ib.s_no = bi.bill_s_no
            JOIN party_master p ON ib.party_id = p.p_id
            WHERE bi.product_id = %s
        """
        params = [product_id]
        
        if start_date:
            query += " AND ib.bill_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND ib.bill_date <= %s"
            params.append(end_date)
            
        # Get outgoing bills
        query += """
            UNION ALL
            SELECT 
                'Sale' as type,
                ob.bill_date,
                ob.bill_no,
                p.party as party_name,
                obi.qty,
                obi.rate,
                obi.sub_total,
                obi.gst_percent,
                obi.sgst_amount,
                obi.cgst_amount,
                obi.total_amount
            FROM outgoing_bills ob
            JOIN outgoing_bill_items obi ON ob.s_no = obi.bill_s_no
            JOIN party_master p ON ob.party_id = p.p_id
            WHERE obi.product_id = %s
        """
        params.append(product_id)
        
        if start_date:
            query += " AND ob.bill_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND ob.bill_date <= %s"
            params.append(end_date)
            
        query += " ORDER BY bill_date DESC"
        
        cursor.execute(query, params)
        transactions = cursor.fetchall()
        
        # Get products for filter
        cursor.execute("SELECT prod_id, name FROM prod_master ORDER BY name")
        products = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('product_wise_report.html',
                             product=product,
                             products=products,
                             transactions=transactions,
                             product_id=product_id,
                             start_date=start_date,
                             end_date=end_date)
        
    except Exception as e:
        flash(f'Error generating product-wise report: {str(e)}', 'danger')
        return redirect(url_for('reports'))

@app.route('/reports/gst')
def gst_report():
    try:
        # Get filter parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        party_id = request.args.get('party_id')
        gst_percent = request.args.get('gst_percent')

        # Build base query conditions
        conditions = []
        params = []

        if start_date:
            conditions.append("b.bill_date >= %s")
            params.append(start_date)
        if end_date:
            conditions.append("b.bill_date <= %s")
            params.append(end_date)
        if party_id:
            conditions.append("b.party_id = %s")
            params.append(party_id)
        if gst_percent:
            conditions.append("i.gst_percent = %s")
            params.append(float(gst_percent))

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Get database connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get parties for dropdown
        cursor.execute("SELECT p_id, party FROM party_master ORDER BY party")
        parties = cursor.fetchall()

        # Get input GST summary (purchases)
        cursor.execute(f"""
            SELECT 
                COUNT(DISTINCT b.inv_id) as total_bills,
                COALESCE(SUM(i.total_amount), 0) as total_amount,
                COALESCE(SUM(i.sgst_amount + i.cgst_amount), 0) as total_gst
            FROM incoming_bills b
            JOIN bill_items i ON b.s_no = i.bill_s_no
            WHERE {where_clause}
        """, params)
        input_summary = cursor.fetchone()

        # Get output GST summary (sales)
        cursor.execute(f"""
            SELECT 
                COUNT(DISTINCT b.bill_no) as total_bills,
                COALESCE(SUM(i.total_amount), 0) as total_amount,
                COALESCE(SUM(i.sgst_amount + i.cgst_amount), 0) as total_gst
            FROM outgoing_bills b
            JOIN outgoing_bill_items i ON b.s_no = i.bill_s_no
            WHERE {where_clause}
        """, params)
        output_summary = cursor.fetchone()

        # Calculate net amounts
        net_amount = (input_summary['total_amount'] or 0) - (output_summary['total_amount'] or 0)
        net_gst = (input_summary['total_gst'] or 0) - (output_summary['total_gst'] or 0)

        # Get GST rate-wise summary
        cursor.execute(f"""
            SELECT 
                i.gst_percent,
                COALESCE(SUM(CASE WHEN b.type = 'Purchase' THEN i.total_amount ELSE 0 END), 0) as input_amount,
                COALESCE(SUM(CASE WHEN b.type = 'Purchase' THEN (i.sgst_amount + i.cgst_amount) ELSE 0 END), 0) as input_gst,
                COALESCE(SUM(CASE WHEN b.type = 'Sale' THEN i.total_amount ELSE 0 END), 0) as output_amount,
                COALESCE(SUM(CASE WHEN b.type = 'Sale' THEN (i.sgst_amount + i.cgst_amount) ELSE 0 END), 0) as output_gst
            FROM (
                SELECT s_no, inv_id as bill_no, bill_date, party_id, 'Purchase' as type FROM incoming_bills
                UNION ALL
                SELECT s_no, bill_no, bill_date, party_id, 'Sale' as type FROM outgoing_bills
            ) b
            JOIN (
                SELECT bill_s_no, gst_percent, total_amount, sgst_amount, cgst_amount FROM bill_items
                UNION ALL
                SELECT bill_s_no, gst_percent, total_amount, sgst_amount, cgst_amount FROM outgoing_bill_items
            ) i ON b.s_no = i.bill_s_no
            WHERE {where_clause}
            GROUP BY i.gst_percent
            ORDER BY i.gst_percent
        """, params)
        gst_rates = cursor.fetchall()

        # Calculate net amounts for each rate
        for rate in gst_rates:
            rate['net_amount'] = (rate['input_amount'] or 0) - (rate['output_amount'] or 0)
            rate['net_gst'] = (rate['input_gst'] or 0) - (rate['output_gst'] or 0)

        # Get transaction details
        cursor.execute(f"""
            SELECT 
                b.bill_date,
                b.bill_no,
                b.type,
                p.party as party_name,
                pm.name as product_name,
                COALESCE(i.qty, 0) as qty,
                COALESCE(i.rate, 0) as rate,
                COALESCE(i.sub_total, 0) as sub_total,
                COALESCE(i.gst_percent, 0) as gst_percent,
                COALESCE(i.sgst_amount, 0) as sgst_amount,
                COALESCE(i.cgst_amount, 0) as cgst_amount,
                COALESCE(i.total_amount, 0) as total_amount
            FROM (
                SELECT s_no, inv_id as bill_no, bill_date, party_id, 'Purchase' as type FROM incoming_bills
                UNION ALL
                SELECT s_no, bill_no, bill_date, party_id, 'Sale' as type FROM outgoing_bills
            ) b
            JOIN (
                SELECT bill_s_no, product_id, qty, rate, sub_total, gst_percent, sgst_amount, cgst_amount, total_amount 
                FROM bill_items
                UNION ALL
                SELECT bill_s_no, product_id, qty, rate, sub_total, gst_percent, sgst_amount, cgst_amount, total_amount 
                FROM outgoing_bill_items
            ) i ON b.s_no = i.bill_s_no
            LEFT JOIN party_master p ON b.party_id = p.p_id
            LEFT JOIN prod_master pm ON i.product_id = pm.prod_id
            WHERE {where_clause}
            ORDER BY b.bill_date DESC, b.bill_no DESC
        """, params)
        transactions = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('gst_report.html',
                             start_date=start_date,
                             end_date=end_date,
                             party_id=party_id,
                             gst_percent=gst_percent,
                             parties=parties,
                             input_summary=input_summary,
                             output_summary=output_summary,
                             net_amount=net_amount,
                             net_gst=net_gst,
                             gst_rates=gst_rates,
                             transactions=transactions)

    except Exception as e:
        flash(f'Error generating GST report: {str(e)}', 'danger')
        return redirect(url_for('reports'))

if __name__ == '__main__':
    app.run(debug=True) 
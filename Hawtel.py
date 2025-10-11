from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# Database connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="hotel"
    )

# ---------------- Home Page ----------------
@app.route('/')
def index():
    return render_template('index.html')

# ---------------- View Rooms ----------------
@app.route('/rooms')
def rooms():
    con = get_connection()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM rooms")
    data = cur.fetchall()
    con.close()
    return render_template('rooms.html', rooms=data)

# ---------------- Add Room ----------------
@app.route('/add_room', methods=['POST'])
def add_room():
    rno = request.form['room_no']
    rtype = request.form['room_type']
    price = request.form['price']
    con = get_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO rooms VALUES (%s,%s,%s,'Available')", (rno, rtype, price))
    con.commit()
    con.close()
    return redirect('/rooms')

# ---------------- View Guests ----------------
@app.route('/guests')
def guests():
    con = get_connection()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM guests")
    data = cur.fetchall()
    con.close()
    return render_template('guests.html', guests=data)

# ---------------- Add Guest ----------------
@app.route('/add_guest', methods=['POST'])
def add_guest():
    name = request.form['name']
    contact = request.form['contact']
    idp = request.form['id_proof']
    con = get_connection()
    cur = con.cursor()
    cur.execute("INSERT INTO guests(name,contact,id_proof) VALUES (%s,%s,%s)", (name, contact, idp))
    con.commit()
    con.close()
    return redirect('/guests')

# ---------------- View Bookings ----------------
@app.route('/bookings')
def bookings():
    con = get_connection()
    cur = con.cursor(dictionary=True)
    cur.execute("""
        SELECT b.booking_id, g.name AS guest, r.room_no, r.room_type, b.check_in, b.check_out, b.total_amount
        FROM bookings b
        JOIN guests g ON b.guest_id=g.guest_id
        JOIN rooms r ON b.room_no=r.room_no
        ORDER BY b.booking_id DESC
    """)
    data = cur.fetchall()
    con.close()
    return render_template('bookings.html', bookings=data)

# ---------------- Add Booking ----------------
@app.route('/add_booking', methods=['POST'])
def add_booking():
    guest_id = request.form['guest_id']
    room_no = request.form['room_no']
    check_in = request.form['check_in']
    check_out = request.form['check_out']
    con = get_connection()
    cur = con.cursor()
    # Get room price
    cur.execute("SELECT price_per_day FROM rooms WHERE room_no=%s", (room_no,))
    price = cur.fetchone()[0]
    cur.execute("SELECT DATEDIFF(%s, %s)", (check_out, check_in))
    days = cur.fetchone()[0]
    if days <= 0: days = 1
    total = price * days
    # Insert booking
    cur.execute("INSERT INTO bookings(guest_id,room_no,check_in,check_out,total_amount) VALUES (%s,%s,%s,%s,%s)",
                (guest_id, room_no, check_in, check_out, total))
    cur.execute("UPDATE rooms SET status='Booked' WHERE room_no=%s", (room_no,))
    con.commit()
    con.close()
    return redirect('/bookings')

# Run the app
if __name__ == "__main__":
    app.run(debug=True)

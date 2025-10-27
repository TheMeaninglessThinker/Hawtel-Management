from flask import Flask, render_template, request, redirect, url_for,flash
import pymysql
from datetime import datetime,date


app = Flask(__name__)
app.secret_key = 'some_random_key_2025'  #Useless. Removing it stops the program
app.config['MESSAGE_FLASHING_OPTIONS'] = {'duration': 5}

#pwd = "abcd"
#if inp == "Password":
#   pwd = ""

db = pymysql.connect(host='localhost', user='root', password='', db='hotel_db')
cursor = db.cursor()

#THE CURSOR!!!!!!! YOOOOOOO
def get_cursor():
    return db.cursor()


@app.route('/')
def index():
    return render_template('index.html')

def reserve_date_check(check_in, check_out):
    f = True;
    indate = datetime.strptime(check_in,"%Y-%m-%d").date()
    outdate = datetime.strptime(check_out,"%Y-%m-%d").date()
    today = date.today()

    try:
        if indate <= today:
            print("Yeah, I will let you in when technoblade dies, that is NEVERRRRRR");
            return False;
        
        if outdate<=indate:
            print("That is possible when techno dies, that is it is impossible.")
            return False;
        
        return True;

    
    except ValueError as e:
        print("DATE NO NOO NOO YOU INPUT.")
        return False
        

def reserve_check_status(room_id):
    cur = get_cursor()
    cur.execute("SELECT status from rooms where id = %s",(room_id))
    status = cur.fetchone()[0]
    if status =="occupied":
        return False
        
    return True



@app.route('/dashboard')
def dashboard():
    cur = get_cursor()
    cur.execute("SELECT COUNT(*) FROM rooms WHERE status = 'occupied'")
    occupied = cur.fetchone()[0]
    cur.execute("SELECT SUM(amount) FROM billings WHERE status = 'paid'")
    revenue = cur.fetchone()[0] or 0.00 #Not working :(
    cur.execute("SELECT * FROM rooms LIMIT 5")
    rooms = cur.fetchall()
    cur.close()
    return render_template('dashboard.html', occupied=occupied, revenue=revenue, rooms=rooms)



#:( So muchhhh timeeeeee wasteeeed in this. DO NOT TOUCH, IT STOPS WORKING IF YOU DO.
@app.route('/reservations', methods=['GET', 'POST'])

def reservations():

    cur = get_cursor()
    if request.method == 'POST':

        if 'room_type' in request.form:  # Add new room
            room_type = request.form['room_type']
            status = request.form['status']
            price = request.form['price']

            cur.execute("INSERT INTO rooms (type, status, price) VALUES (%s, %s, %s)", 
                        (room_type, status, price))
            db.commit()


        elif 'book_room_id' in request.form:  # Book a room
            guest_id = request.form['guest_id']
            room_id = request.form['book_room_id']
            check_in = request .form['check_in']
            check_out = request.form['check_out']
            

            f = reserve_date_check(check_in, check_out)
            t= reserve_check_status(room_id)

            
            if f == True and t == True:

                cur.execute("INSERT INTO reservations (guest_id, room_id, check_in, check_out) VALUES (%s, %s, %s, %s)", 
                        (guest_id, room_id, check_in, check_out))
                cur.execute("UPDATE rooms SET status = 'occupied' WHERE id = %s", (room_id,))

                db.commit()
            
            if f== False:
                flash("Teri mkc galat date bharr diya lmfaooooooooooo")
            if t == False:
                flash("Ky kar raha hai tu, kisi aur ke room mai occupy hona hai kya hehehehehe")

            


        elif 'delete_room_id' in request.form:  # Delete room
            room_id = request.form['delete_room_id']
            try:
                
                cur.execute("DELETE FROM reservations WHERE room_id = %s", (room_id,))
                cur.execute("DELETE FROM rooms WHERE id = %s", (room_id,))
                db.commit()

            except pymysql.err.IntegrityError as e:
                print(f"Error deleting room: {e}")


    cur.execute("SELECT * FROM rooms")
    all_rooms = cur.fetchall()
    cur.execute("SELECT * FROM guests")
    guests = cur.fetchall()
    cur.close()
    return render_template('reservations.html', rooms=all_rooms, guests=guests)



@app.route('/guests', methods=['GET', 'POST'])
def guests():
    cur = get_cursor()
    if request.method == 'POST':
        if 'delete_id' in request.form:  # Delete guest
            guest_id = request.form['delete_id']
            try:
                # Delete related reservations first
                cur.execute("DELETE FROM reservations WHERE guest_id = %s", (guest_id,))
                cur.execute("DELETE FROM guests WHERE id = %s", (guest_id,))
                db.commit()
            except pymysql.err.IntegrityError as e:
                print(f"Error deleting guest: {e}")
        else:  # Add guest
            name = request.form['name']
            contact = request.form['contact'] #Exception handle here bhaiiiiiiii
            id_proof = request.form['id_proof']
            preferences = request.form['preferences']
            cur.execute("INSERT INTO guests (name, contact, id_proof, preferences) VALUES (%s, %s, %s, %s)", 
                        (name, int(contact), id_proof, preferences))
            db.commit()
    cur.execute("SELECT * FROM guests")
    guest_list = cur.fetchall()
    cur.close()
    return render_template('guests.html', guests=guest_list)



@app.route('/staff', methods=['GET', 'POST'])
def staff():
    cur = get_cursor()
    if request.method == 'POST':
        name = request.form['name']
        role = request.form['role']
        schedule = request.form['schedule']
        cur.execute("INSERT INTO staff (name, role, schedule) VALUES (%s, %s, %s)", 
                    (name, role, schedule))
        db.commit()

    cur.execute("SELECT * FROM staff")
    staff_list = cur.fetchall()
    cur.close()

    return render_template('staff.html', staff=staff_list)


#Billing work, calculation and all. 
@app.route('/billing/<int:res_id>', methods=['GET', 'POST'])
def billing(res_id):
    cur = get_cursor()

    if request.method == 'POST':
        amount = request.form['amount']
        details = request.form['details']
        status = request.form['status']
        cur.execute("INSERT INTO billings (reservation_id, amount, status, details) VALUES (%s, %s, %s, %s)", 
                    (res_id, amount, status, details))
        db.commit()

    cur.execute("SELECT * FROM reservations WHERE id = %s", (res_id,))
    reservation = cur.fetchone()
    cur.execute("SELECT SUM(amount) FROM billings WHERE reservation_id = %s AND status = 'paid'", (res_id,))
    total_bill = cur.fetchone()[0] or 0.00
    cur.close()

    return render_template('billing.html', reservation=reservation, total_bill=total_bill)

if __name__ == '__main__':
    app.run(debug=True)


#Things to fix: Revenue being shown is not working well.
#The code is a mess, it is hard to navigate. 
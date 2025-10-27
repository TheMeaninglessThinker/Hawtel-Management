from flask import Flask, render_template, request, redirect, url_for,flash
import pymysql
from datetime import datetime,date


app = Flask(__name__)
app.secret_key = 'some_random_key_2025'  #Useless. Removing it stops the program
app.config['MESSAGE_FLASHING_OPTIONS'] = {'duration': 5}



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
            
            return False;
        
        if outdate<=indate:
            
            return False;
        
        return True;

    
    except ValueError as e:
        return False
    
    cur.close()
        

def reserve_check_status(room_id):
    cur = get_cursor()
    cur.execute("SELECT status from rooms where id = %s",(room_id))
    status = cur.fetchone()[0]
    if status =="occupied":
        return False

    cur.close()    
    return True


def number_validity(number):
    
    if number.isdigit() == True:
        if len(number) != 10:
            return False;
        else:
            return True;
    return False;

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

        if 'book_room_id' in request.form:  # Book a room
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
                flash("Please input valid check-in and check-out dates")
            if t == False:
                flash("Please choose an available room, the one you have chosen is occupied.")

            


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
            p = number_validity(contact)
            if p == True:

                id_proof = request.form['id_proof']
                preferences = request.form['preferences']
                cur.execute("INSERT INTO guests (name, contact, id_proof, preferences) VALUES (%s, %s, %s, %s)", 
                            (name, int(contact), id_proof, preferences))
                db.commit()
            else:
                flash("Please input a valid contact number")
    cur.execute("SELECT * FROM guests")
    guest_list = cur.fetchall()
    cur.close()
    return render_template('guests.html', guests=guest_list)



@app.route('/staff', methods=['GET', 'POST'])
def staff():
    cur = get_cursor()
    if request.method == 'POST':
        if 'delete_staff_id' in request.form:
            staff_id = request.form['delete_staff_id']
            cur.execute("DELETE FROM staff WHERE id = %s", (staff_id,))
            db.commit()
            flash("Staff deleted.")
        else:
            name = request.form['name']
            role = request.form['role']
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            cur.execute("INSERT INTO staff (name, role, start_time,end_time) VALUES (%s, %s, %s,%s)", 
                        (name, role, start_time,end_time))
            db.commit()

    cur.execute("SELECT * FROM staff")
    staff_list = cur.fetchall()
    cur.close()

    return render_template('staff.html', staff=staff_list)

#Room Room Room Room Room ROom ROOOOM 
@app.route('/rooms', methods=['GET', 'POST'])
def room():
    
    cur = get_cursor()
    if request.method == 'POST':

        if 'room_type' in request.form:  # Add new room
            room_type = request.form['room_type']
            status = request.form['status']
            price = request.form['price']

            cur.execute("INSERT INTO rooms (type, status, price) VALUES (%s, %s, %s)", 
                        (room_type, status, price))
            db.commit()

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
    cur.close()
    return render_template('rooms.html',rooms=all_rooms)


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


#Things to fix: The contact number of the user can be less than 10.
#The code is a mess, it is hard to navigate. 
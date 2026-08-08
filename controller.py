from app import *
from flask import Flask, render_template,request, redirect, url_for
from models import *
from datetime import datetime, timedelta
#defining app routes

@app.route("/")
def home():
    return redirect(url_for('signin'))

@app.route("/login", methods=["POST","GET"])
def signin():
    if request.method == "POST":
        id = request.form.get("emailid")
        password = request.form.get("pwd")

        user = db.session.query(Users).filter(
            Users.email == id,
            Users.password == password
        ).first()

        if user and user.role == 0:
            return render_template("admin_dashboard.html")

        if user and user.role == 1:
            trekker = db.session.query(Trekker_Profiles).filter(
                Trekker_Profiles.trekker_id == user.id
            ).first()
            if trekker and trekker.status == 1:
                return "Your account has been blacklisted."
            return render_template("user_dashboard.html")

        if user and user.role == 2:
            staff = db.session.query(Staff_Profiles).filter(Staff_Profiles.staff_id == user.id).first()

            if staff and staff.status == 2:
                return redirect(url_for("staff_dashboard", staff_id=staff.staff_id))

            elif staff and staff.status == 1:
                return "Your staff account has been blacklisted."

            else:
                return "Your staff account is waiting for admin approval."

        else:
            return redirect(url_for("signup"))

    else:
        return render_template("login.html")

@app.route("/register",methods=["GET","POST"])
def signup():
    if request.method=="POST":
        #need to store into user credentials
        id=request.form.get("emailid")
        password=request.form.get("pwd")
        role=request.form.get("utype")

        user=Users(email=id,password=password,role=int(role))
        db.session.add(user)
        db.session.commit()

        #after users, then separate trekker & staff role credentials

        address=request.form.get("address")
        name=request.form.get("fname")
        phone=request.form.get("phno")
        em_contact=request.form.get("emr_phno")
        if int(role)==1:
            trekker=Trekker_Profiles(trekker_id = user.id,name=name, address=address, phone=phone, emergency_contact=em_contact)
            db.session.add(trekker)

        elif int(role)==2:
            exp=request.form.get("exp")
            staff=Staff_Profiles(staff_id = user.id,name=name, address=address, phone=phone, emergency_contact=em_contact,experience=exp)
            db.session.add(staff)
        db.session.commit()
        return redirect(url_for("signin"))
    else:
        return render_template("signup.html")





################################################################################################

# ADMIN - Dashboard Management

@app.route("/admin")
def admin_dashboard():

    total_treks = db.session.query(Treks).count()
    total_users = db.session.query(Users).filter(Users.role == 1).count()
    total_staff = db.session.query(Staff_Profiles).count()
    total_bookings = db.session.query(Bookings).count()

    # 5 most recent bookings
    recent_bookings = db.session.query(Bookings).order_by(
        Bookings.booking_date.desc()
    ).limit(5).all()

    return render_template(
        "admin_dashboard.html",total_treks=total_treks,
        total_users=total_users,total_staff=total_staff,
        total_bookings=total_bookings,recent_bookings=recent_bookings)


########################################################################################


# ADMIN - User Management

@app.route("/admin/user")
def admin_user():
    active_users = db.session.query(Trekker_Profiles).filter(Trekker_Profiles.status == 0).all()

    blacklisted_users = db.session.query(Trekker_Profiles).filter(Trekker_Profiles.status == 1).all()

    return render_template("admin_user.html",active_users=active_users,blacklisted_users=blacklisted_users)

# block the user
@app.route("/admin/user/block/<int:user_id>")
def block_user(user_id):

    user = db.session.query(Trekker_Profiles).filter(Trekker_Profiles.trekker_id == user_id).first()

    if user:
        user.status = 1
        db.session.commit()

    return redirect(url_for("admin_user"))

#unblock the user
@app.route("/admin/user/unblock/<int:user_id>")
def unblock_user(user_id):
    user = db.session.query(Trekker_Profiles).filter(Trekker_Profiles.trekker_id == user_id).first()

    if user:
        user.status = 0
        db.session.commit()

    return redirect(url_for("admin_user"))





###########################################################################################

# ADMIN - Treks Management

@app.route("/admin/treks")
def admin_treks():
    # 5 recent treks will be visible
    recent_treks = db.session.query(Treks).order_by(Treks.start_date.desc()).limit(5).all()

    return render_template("admin_treks.html",treks=recent_treks)

#add new trek

@app.route("/admin/treks/add", methods=["GET", "POST"])
def add_trek():

    approved_staff = db.session.query(Staff_Profiles).filter(
        Staff_Profiles.status == 2
    ).all()

    if request.method == "POST":

        trek_name = request.form.get("T_name")
        location = request.form.get("T_loc")
        difficulty = int(request.form.get("T_diff"))
        duration = int(request.form.get("T_days"))
        total_slots = int(request.form.get("T_slots"))
        start_date = datetime.strptime(
            request.form.get("T_sdate"),
            "%Y-%m-%d"
        ).date()

        description = request.form.get("T_discr")

        staff_id = request.form.get("T_staff")

        if staff_id:
            staff_id = int(staff_id)
        else:
            staff_id = None

        # Calculate end date automatically
        end_date = start_date + timedelta(days=duration - 1)

        trek = Treks(
            trek_name=trek_name,
            location=location,
            duration_days=duration,
            total_slots=total_slots,

            # Initially all slots are available
            avail_slots=total_slots,

            staff_id=staff_id,
            difficulty=difficulty,

            # New trek as Pending, need approval
            trek_status=0,

            start_date=start_date,
            end_date=end_date,
            description=description
        )

        db.session.add(trek)
        db.session.commit()

        return redirect(url_for("admin_treks"))

    return render_template("Add_trek.html",approved_staff=approved_staff,trek=None)

# Edit Trek
@app.route("/admin/treks/edit/<int:trek_id>", methods=["GET", "POST"])
def edit_trek(trek_id):

    trek = db.session.query(Treks).filter(Treks.trek_id == trek_id).first()

    if not trek:
        return "Trek not found"

    approved_staff = db.session.query(Staff_Profiles).filter(Staff_Profiles.status == 2).all()

    if request.method == "POST":

        trek.trek_name = request.form.get("T_name")
        trek.location = request.form.get("T_loc")
        trek.difficulty = int(request.form.get("T_diff"))
        trek.duration_days = int(request.form.get("T_days"))

        new_total_slots = int(request.form.get("T_slots"))

        # Number of already booked slots
        booked_slots = trek.total_slots - trek.avail_slots


        trek.total_slots = new_total_slots

        # Recalculate available slots
        trek.avail_slots = new_total_slots - booked_slots

        trek.start_date = datetime.strptime(
            request.form.get("T_sdate"),
            "%Y-%m-%d"
        ).date()

        trek.end_date = trek.start_date + timedelta(
            days=trek.duration_days - 1
        )

        trek.description = request.form.get("T_discr")

        staff_id = request.form.get("T_staff")

        if staff_id:
            trek.staff_id = int(staff_id)
        else:
            trek.staff_id = None

        db.session.commit()

        return redirect(url_for("admin_treks"))

    return render_template("Add_trek.html",approved_staff=approved_staff,trek=trek)


# approve trek

@app.route("/admin/treks/approve/<int:trek_id>")
def approve_trek(trek_id):

    trek = db.session.query(Treks).filter(
        Treks.trek_id == trek_id
    ).first()

    if trek:
        trek.trek_status = 1
        db.session.commit()

    return redirect(url_for("admin_treks"))

#admin - bookings to show all treks till date

@app.route("/admin/bookings")
def admin_bookings():

    all_bookings = db.session.query(Bookings).order_by(
        Bookings.booking_date.desc()
    ).all()

    return render_template("admin_bookings.html",bookings=all_bookings)


#################################################################################################


# ADMIN - Staff Management

@app.route("/admin/staff")
def admin_staff():

    pending_staff = db.session.query(Staff_Profiles).filter(
        Staff_Profiles.status == 0
    ).all()

    approved_staff = db.session.query(Staff_Profiles).filter(
        Staff_Profiles.status == 2
    ).all()

    blacklisted_staff = db.session.query(Staff_Profiles).filter(
        Staff_Profiles.status == 1
    ).all()

    return render_template(
        "admin_staff.html",
        pending_staff=pending_staff,
        approved_staff=approved_staff,
        blacklisted_staff=blacklisted_staff
    )


# Approve staff

@app.route("/admin/staff/approve/<int:staff_id>")
def approve_staff(staff_id):

    staff = db.session.query(Staff_Profiles).filter(
        Staff_Profiles.staff_id == staff_id
    ).first()

    if staff:
        staff.status = 2
        db.session.commit()

    return redirect(url_for("admin_staff"))


# Reject staff

@app.route("/admin/staff/reject/<int:staff_id>")
def reject_staff(staff_id):

    staff = db.session.query(Staff_Profiles).filter(
        Staff_Profiles.staff_id == staff_id
    ).first()

    if staff:
        # Delete staff profile
        user = db.session.query(Users).filter(
            Users.id == staff.staff_id
        ).first()

        db.session.delete(staff)

        if user:
            db.session.delete(user)

        db.session.commit()

    return redirect(url_for("admin_staff"))


# Blacklist approved staff

@app.route("/admin/staff/blacklist/<int:staff_id>")
def blacklist_staff(staff_id):

    staff = db.session.query(Staff_Profiles).filter(
        Staff_Profiles.staff_id == staff_id
    ).first()

    if staff:
        staff.status = 1
        db.session.commit()

    return redirect(url_for("admin_staff"))


##############################################################################

#STAFF - Dashboard

@app.route("/staff/<int:staff_id>")
def staff_dashboard(staff_id):

    staff = db.session.query(Staff_Profiles).filter(Staff_Profiles.staff_id == staff_id).first()

    if not staff:
        return "Staff not found."

    # Approved treks by admin to the staff with all the status of treks
    assigned_treks = db.session.query(Treks).filter(Treks.staff_id == staff_id,Treks.trek_status.in_([1,2,3,4])).all()

    # Count assigned approved treks
    assigned_count = len(assigned_treks)

    # Currently open treks assigned to this staff
    open_count = db.session.query(Treks).filter(Treks.staff_id == staff_id,Treks.trek_status == 2).count()

    # Total participants  are of the no. of booked slots
    total_participants = 0

    for trek in assigned_treks:
        total_participants += (trek.total_slots - trek.avail_slots)

    return render_template(
        "staff_dashboard.html",staff=staff,
        assigned_treks=assigned_treks,assigned_count=assigned_count,
        open_count=open_count,total_participants=total_participants)


#staff - open trek
@app.route("/staff/<int:staff_id>/trek/<int:trek_id>/open")
def open_trek(staff_id, trek_id):
    trek = db.session.query(Treks).filter(Treks.trek_id == trek_id).first()
    if not trek:
        return "Trek not found."
    trek.trek_status = 2
    db.session.commit()
    return redirect(url_for("staff_dashboard",staff_id=staff_id))


#staff - manage trek
@app.route("/staff/<int:staff_id>/trek/<int:trek_id>")
def staff_trek(staff_id, trek_id):
    trek = db.session.query(Treks).filter(Treks.trek_id == trek_id).first()

    if not trek:
        return "Trek not found."

    # Get all bookings for this trek
    bookings = db.session.query(Bookings).filter(Bookings.trek_id == trek_id).all()

    return render_template("staff_treks.html",trek=trek,bookings=bookings,staff_id=staff_id)


#staff - close trek
@app.route("/staff/<int:staff_id>/trek/<int:trek_id>/close")
def close_trek(staff_id, trek_id):
    trek = db.session.query(Treks).filter(Treks.trek_id == trek_id).first()
    if not trek:
        return "Trek not found."

    if trek.trek_status != 2:
        return "This trek cannot be closed."

    trek.trek_status = 3
    db.session.commit()
    return redirect(url_for("staff_trek",staff_id=staff_id,trek_id=trek_id))



# staff- completed the trek

@app.route("/staff/<int:staff_id>/trek/<int:trek_id>/complete")
def complete_trek(staff_id, trek_id):
    trek = db.session.query(Treks).filter(Treks.trek_id == trek_id).first()

    if not trek:
        return "Trek not found."

    if trek.trek_status != 3:
        return "This trek must be closed before marking it completed."
    trek.trek_status = 4
    db.session.commit()
    return redirect(url_for("staff_trek",staff_id=staff_id,trek_id=trek_id))

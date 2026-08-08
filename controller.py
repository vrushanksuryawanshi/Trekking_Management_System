from app import *
from flask import Flask, render_template,request, redirect, url_for
from models import *

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
            staff = db.session.query(Staff_Profiles).filter(
                Staff_Profiles.staff_id == user.id
            ).first()
            if staff and staff.status == 2:
                return render_template("staff_dashboard.html")
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







# ADMIN - Dashboard Management

@app.route("/admin")
def admin_dashboard():
    return render_template("admin_dashboard.html")




# ADMIN - User Management

@app.route("/admin/user")
def admin_user():
    return render_template("admin_user.html")


# ADMIN - Treks Management

@app.route("/admin/treks")
def admin_treks():
    return render_template("admin_treks.html")








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



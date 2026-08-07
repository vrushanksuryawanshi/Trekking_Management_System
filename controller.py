from app import *
from flask import Flask, render_template,request, redirect, url_for
from models import *

#defining app routes
@app.route("/")
def home():
    return "welcome to TMS"

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
            return render_template("user_dashboard.html")

        if user and user.role == 2:
            staff = db.session.query(Staff_Profiles).filter(
                Staff_Profiles.staff_id == user.id
            ).first()

            if staff and staff.status == 2:
                return render_template("staff_dashboard.html")
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

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



# USERS
class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.Integer, nullable=False, default=1) # 0 = Admin, 1 = Trekker, 2 = Staff

    # One user can have one trekker profile
    trekker_profile = db.relationship(
        "Trekker_Profiles",
        cascade="all, delete",
        backref="users",
        uselist=False
    )

    # One user can have one staff profile
    staff_profile = db.relationship(
        "Staff_Profiles",
        cascade="all, delete",
        backref="users",
        uselist=False
    )




# TREKKER PROFILE
class Trekker_Profiles(db.Model):
    __tablename__ = "trekker_profiles"

    trekker_id = db.Column(db.Integer,db.ForeignKey("users.id"),primary_key=True)

    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    emergency_contact = db.Column(db.String, nullable=False)
    status = db.Column(db.Integer,nullable=False,default=0) # 0 = Registered, # 1 = Blacklisted

    # One trekker can have many bookings
    bookings = db.relationship(
        "Bookings",
        cascade="all, delete",
        backref="trekker_profiles"
    )




# STAFF PROFILE
class Staff_Profiles(db.Model):
    __tablename__ = "staff_profiles"

    staff_id = db.Column(db.Integer,db.ForeignKey("users.id"), primary_key=True)

    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String, nullable=False)
    emergency_contact = db.Column(db.String, nullable=False)
    status = db.Column(db.Integer,nullable=False,default=0)     # 0 = Registered, 1 = Blacklisted, 2 = Approved

    # One staff member can be assigned to many treks
    treks = db.relationship("Treks",cascade="all, delete", backref="staff_profiles")




# TREK
class Treks(db.Model):
    __tablename__ = "treks"

    trek_id = db.Column(db.Integer,primary_key=True)

    trek_name = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    duration_days = db.Column(db.Integer,nullable=False)
    total_slots = db.Column(db.Integer,nullable=False)
    avail_slots = db.Column(db.Integer,nullable=False)
    staff_id = db.Column(db.Integer,db.ForeignKey("staff_profiles.staff_id"),nullable=True)
    difficulty = db.Column(db.Integer,nullable=False, default=0)    # 0 = Easy, 1 = Moderate, 2 = Hard
    trek_status = db.Column(db.Integer,nullable=False,default=0)    # 0 = Pending, 1 = Approved, 2 = Open, 3 = Closed, 4 = Completed
    start_date = db.Column(db.Date,nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String,nullable=False)

    # One trek can have many bookings
    bookings = db.relationship(
        "Bookings",
        cascade="all, delete",
        backref="treks"
    )





# BOOKING
class Bookings(db.Model):
    __tablename__ = "bookings"

    booking_id = db.Column(db.Integer,primary_key=True)

    trekker_id = db.Column(db.Integer,db.ForeignKey("trekker_profiles.trekker_id"),nullable=False)
    trek_id = db.Column(db.Integer,db.ForeignKey("treks.trek_id"),nullable=False)
    booking_status = db.Column(db.Integer,nullable=False,default=0)     # 0 = Booked, 1 = Cancelled  2 = Completed
    booking_date = db.Column(db.Date,nullable=False)

    # Prevent the same trekker from booking
    # the same trek more than once
    __table_args__ = (
        db.UniqueConstraint(
            "trekker_id",
            "trek_id",
            name="unique_trekker_trek"
        ),
    )
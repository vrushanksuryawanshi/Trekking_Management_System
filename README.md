# Trekking Management System

## Project Overview

The **Trekking Management System (TMS)** is a web-based application developed to manage trekking activities, trekkers, staff members, trek bookings, and trek operations through a centralized system.

The system provides separate functionalities for three types of users:

- **Admin**
- **Trekker/User**
- **Trek Staff**

The application replaces manual trek management with a structured digital system that allows administrators to manage treks and users, staff members to manage assigned treks, and trekkers to view and book available treks.

The application is developed using the **Flask web framework** with **Python**, **HTML/CSS**, **Jinja2 templates**, and **SQLAlchemy** for database operations.

---

# Main Features

## Authentication and Registration

- User login and authentication
- Role-based login
- Registration for trekkers and staff
- Separate profiles for trekkers and staff
- Staff approval system
- User and staff blacklist management

## Admin Features

- Admin dashboard
- View total treks
- View total trekkers
- View total staff
- View total bookings
- View recent bookings
- Manage trekkers
- Block/unblock trekkers
- Add new treks
- Edit existing treks
- Approve treks
- Manage bookings
- Approve staff
- Reject staff
- Blacklist staff

## Staff Features

- Staff dashboard
- View assigned treks
- View number of assigned treks
- View currently open treks
- View total participants
- Open assigned trek
- View trek bookings
- Close trek
- Complete trek
- Automatically mark active bookings as completed when a trek is completed

## Trekker/User Features

- User dashboard
- View available treks
- Filter treks by difficulty
- Filter treks by location
- View trek details
- Book a trek
- Prevent duplicate active bookings
- Prevent overbooking
- Cancel a booking
- View complete booking history

---

# MVC

The application follows an **MVC (Model-View-Controller)** architectural approach.

MVC divides the application into three major components:

| Component | Implementation | Responsibility |
|---|---|---|
| Model | SQLAlchemy models | Represents and manages database data |
| View | HTML, CSS, Jinja2 | Displays information and user interfaces |
| Controller | Flask/Python routes | Handles requests, application logic and communication between Model and View |

### MVC Flow

```text
                User / Browser
                      |
                      v
                  Controller
               (Flask Routes)
                      |
          +-----------+-----------+
          |                       |
          v                       v
       Model                    View
    (Database)            (HTML + CSS + Jinja2)
          |                       |
          +-----------+-----------+
                      |
                      v
                User / Browser
from flask import Flask,render_template
from models import *


#creating configuration between app, controller and db model
def setup_app():
    app=Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///tms.sqlite3"
    db.init_app(app) #linking between app and db
    app.app_context().push() #Giving access of app to all other modules
    print("TMS app is ready!")
    return app

app=setup_app()


from controller import *

#executing Flask
if __name__=="__main__":
    app.run(debug=True)
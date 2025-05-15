from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_mail import Mail

mail = Mail()
db = SQLAlchemy()
ma = Marshmallow()
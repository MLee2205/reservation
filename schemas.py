# schemas.py
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from model import Reservation, Ticket

class  ReservationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Reservation
        load_instance = True


class  TicketSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Ticket
        load_instance = True









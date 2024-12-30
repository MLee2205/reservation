# models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text


db = SQLAlchemy()

class Reservation(db.Model):
    __tablename__ = 'reservation'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(50), nullable=False)
    user_surname = db.Column(db.String(50), nullable=False)
    nbre_place= db.Column(db.Integer,  nullable=False)
    num_cni= db.Column(db.String(100), nullable=False)
    classe_voyage= db.Column(db.String(100),  nullable=False)
    heure_depart= db.Column(db.String(100),  nullable=False)  
    ville_depart=  db.Column(db.String(100),  nullable=False) 
    ville_arrivee=  db.Column(db.String(100),  nullable=False) 
    email = db.Column(db.String(100),  nullable=False)
    date_voyage= db.Column(db.Date, nullable=False)
    tickets = db.relationship('Ticket', backref='Reservation', lazy=True)    

    def __repr__(self):
        return f'<Reservation {self.user_name}>'
    
    def serialize(self):
        return {
            
            'id': self.id,
            'user_name': self.user_name,
            'user_surname': self.user_surname,
            'nbre_place' : self.nbre_place,
            'num_cni': self.num_cni,
            'classe_voyage': self.classe_voyage,
            'heure_depart':self.heure_depart,
            'date_voyage' : self.date_voyage,
            'email': self.email

        }


################################## classe ticket ##########################################################

class Ticket(db.Model):

    __table_name__ = 'ticket'

    id= db.Column(db.Integer,primary_key=True,autoincrement=True)
    numero_siege = db.Column(db.Integer,nullable=False)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservation.id'), nullable=False)

    def __repr__(self):
        return f'<ticket {self.numero_siege}>'
     
    def serialize(self):
        return {
            
            'id': self.id,
            'numero_siege': self.numero_siege,
            'reservation_id': self.reservation_id,

            }
            
    




from sqlalchemy import text
"""from your_application import db  # Assurez-vous d'importer votre instance de base de données
"""
def reset_sequence(table_name, id_column):
    # Exécute la commande pour réinitialiser la séquence
    sql = f"""
    SELECT setval(pg_get_serial_sequence(:table_name, :id_column), coalesce(max({id_column}), 1) )
    FROM {table_name};
    """
    db.session.execute(text(sql), {'table_name': table_name, 'id_column': id_column})
    db.session.commit()

from flask import Flask, render_template,request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from schemas import ReservationSchema
from model import Reservation, db
import jwt
import datetime
from model import *
from fpdf import FPDF
from datetime import datetime
import qrcode
from io import BytesIO
from sqlalchemy import func, and_
from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Mail, Message
import os




#################################### CONFIGURATION DE L APPLICATION FLASK #################################
#mail = Mail()
#scheduler = BackgroundScheduler()

#l'objet flask pour instancier une application
app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI']='postgresql://yvanna3:1234@localhost/ticket'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False




########################CONFIGURATION DU SERVEUR DE MESSAGERIE###################################################

app.config['MAIL_SERVER']  = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'yvannadjaha@gmail.com'  
app.config['MAIL_PASSWORD'] = 'tgsl apjl qyli nqka'  
app.config['MAIL_DEFAULT_SENDER'] =  'yvannadjaha@gmail.com'

mail = Mail(app)




# Initialiser SQLAlchemy avec l'application
db.init_app(app) 
mail.init_app(app)




################# CREATION D UNE INSTANCE DE reservation##########################################################


SECRET_KEY = 'votre_clé_secrète'  # Assurez-vous que cela est sécurisé

@app.route('/reservation/templates/reserve', methods=['GET'], endpoint='reservation')
def reservation():
        

############################## token sur le client######################################################        
    token1 = request.args.get('token1')
        
    if token1 is None:
        return jsonify({"error": "Token1 manquant."}), 400
        
    try:
        payload = jwt.decode(token1, SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        user_name = payload['user_name']
        user_surname = payload['user_surname']
        num_cni = payload['num_cni']
        email = payload['email']

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Le token a expiré."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token1 invalide."}), 401



########################### token sur le choix du voyage####################################################
 
    token2 = request.args.get('token2')
        
    if token2 is None:
        return jsonify({"error": "Token2 manquant."}), 400
        
    try:
        payload = jwt.decode(token2, SECRET_KEY, algorithms=['HS256'])
        classe_voyage = payload['classe_voyage']
        ville_depart= payload['ville_depart']
        ville_arrivee = payload['ville_arrivee']
        heure_depart = payload['heure_depart']    
        date_voyage = payload['date_voyage']

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Le token a expiré."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token2 invalide."}), 401



    # Afficher le formulaire de choix de reservation
    return render_template('reservation.html',token1=token1,token2=token2) #







#################### endpoint de reservation appele avec la methode post#################################### 


@app.route('/reservation/templates/reserve_post', methods=['POST'], endpoint='reserve_post')
def reserve_post():

    token = request.form.get('token1')

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        user_name = payload['user_name']
        user_surname = payload['user_surname']
        num_cni = payload['num_cni']
        email = payload['email']

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Le token1 a expiré."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token1 invalide."}), 401




########################### token sur le choix du voyage####################################################
 
    token2 = request.form.get('token2')
        
    if token2 is None:
        return jsonify({"error": "Token2 manquant."}), 400
        
    try:
        payload1 = jwt.decode(token2, SECRET_KEY, algorithms=['HS256'])
        classe_voyage = payload1['classe_voyage']
        ville_depart= payload1['ville_depart']
        ville_arrivee = payload1['ville_arrivee']
        heure_depart = payload1['heure_depart']    
        date_voyage = payload1['date_voyage']

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Le token2 a expiré."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token2 invalide."}), 401





        # Récupérer les données du choix de reservation depuis le formulaire
    nbre_place = request.form.get('nombre_place')
    
        #Réinitialiser la séquence avant d'insérer
    reset_sequence('reservation', 'id')

     




 # Récupérer la capacité totale du voyage (exemple : depuis une autre table ou une constante)
    voyage_total_places = 70
    # Calculer les places déjà réservées
    places_reservees = (
        db.session.query(func.sum(Reservation.nbre_place))
        .filter(
            Reservation.ville_depart == ville_depart,
            Reservation.date_voyage == date_voyage,
            Reservation.heure_depart == heure_depart,
            Reservation.classe_voyage == classe_voyage
        )
        .scalar()
        or 0
    )


    # Vérifier la disponibilité
    if places_reservees + int(nbre_place) > voyage_total_places:
        return jsonify({
            "error": "Le nombre de places demandées dépasse la disponibilité.",
            "places_disponibles": voyage_total_places - places_reservees
        }), 400




        # Créer une nouvelle instance de reservation
    new_reservation = Reservation (
            user_name = user_name,
            user_surname=user_surname,
            nbre_place=nbre_place,
            num_cni = num_cni,
            classe_voyage=classe_voyage,
            ville_depart=ville_depart,
            ville_arrivee=ville_arrivee,
            heure_depart=heure_depart,
            date_voyage=date_voyage,
            email = email,
    )

        

       # Ajouter et valider l'instance de reservation dans la base de données
    try:
        db.session.add(new_reservation)
        db.session.commit()
    except Exception as e:
        return jsonify({"error": "Erreur lors de l'enregistrement du reservation.", "details": str(e)}), 500

#recuperation de l'id du reservation en cours
    id_reservation = new_reservation.id

    # Construire le chemin du logo 
    logo_path = os.path.join(os.path.dirname(__file__), 'static', 'logo.png') 
   
 # Création du PDF
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0,0,0)
    # Définir la couleur des bordures (bleu très foncé) 
    pdf.set_draw_color(0, 0, 139) # RGB pour dark blue 
    # Ajouter des bordures 
    pdf.rect(5, 5, 200, 287, 'D') 
    # Position (x=5, y=5), largeur=200, hauteur=287, 'D' pour dessiner uniquement la bordure 

    pdf.image(logo_path, x=10, y=8, w=30)  # Ajuster les paramètres x, y et w selon les besoins

 # Générer les données pour le QR Code
    qr_data = f"TicketID: {new_reservation.id}, UserNAME: {new_reservation.user_name}, Voyage: {new_reservation.ville_depart} -> {new_reservation.ville_arrivee}, Date: {new_reservation.date_voyage}, NombrePlaces: {new_reservation.nbre_place}"
    
    # Générer le QR Code
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)

    # Convertir le QR Code en image PIL
    qr_img = qr.make_image(fill="black", back_color="white")

    # Sauvegarder l'image QR dans un buffer mémoire
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    buffer.seek(0)



    # Ajout des informations au PDF
    pdf.cell(200, 10, txt="Ticket de Voyage", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Numero du Ticket : {new_reservation.id}", ln=True)
    pdf.cell(200, 10, txt=f"Nom du client: {new_reservation.user_name}", ln=True)
    pdf.cell(200, 10, txt=f"Prenom du client: {new_reservation.user_surname}", ln=True)
    pdf.cell(200, 10, txt=f"Classe de Voyage: {new_reservation.classe_voyage}", ln=True)
    pdf.cell(200, 10, txt=f"NombrePlaces : {new_reservation.nbre_place}", ln=True)
    pdf.cell(200, 10, txt=f"Ville de Départ: {new_reservation.ville_depart}", ln=True)
    pdf.cell(200, 10, txt=f"Ville d'Arrivée: {new_reservation.ville_arrivee}", ln=True)
    pdf.cell(200, 10, txt=f"Heure de Départ: {new_reservation.heure_depart}", ln=True)
    pdf.cell(200, 10, txt=f"Date de Voyage: {new_reservation.date_voyage.strftime('%d/%m/%Y')}", ln=True)



# Sauvegarder le QR Code temporairement
    qr_image_path = "/tmp/qrcode.png"
    with open(qr_image_path, "wb") as qr_file:
        qr_file.write(buffer.getvalue())

    # Ajouter le QR Code au PDF
    pdf.ln(10)
    pdf.cell(200, 10, txt="  Code QR pour valider votre ticket :", ln=True)
    pdf.image(qr_image_path, x=80, y=140, w=50)  # Positionnement et taille







    # Exporter le PDF comme réponse pour téléchargement
    response = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=ticket_{new_reservation.id}.pdf'  # "attachment" force le téléchargement
    
    return response





#############################################################################################################

#fonction pour transferer le bordereau de voyage automatiquement

def bordereau_automatique():

    with app.app_context():
    # Sous-requête pour regrouper les réservations similaires
        subquery = (
            db.session.query(
                Reservation.date_voyage,
                Reservation.classe_voyage,
                Reservation.heure_depart,
                Reservation.ville_depart,
                func.string_agg(Reservation.user_name, ',').label('user_names'),
                func.string_agg(Reservation.user_surname, ',').label('user_surnames'),
                func.string_agg(Reservation.num_cni, ',').label('num_cnis')
            )
            .group_by(
                Reservation.date_voyage,
                Reservation.classe_voyage,
                Reservation.heure_depart,
                Reservation.ville_depart
            )
            .subquery()
        )
        
        # Requête principale pour récupérer les données groupées
        query = db.session.query(
            subquery.c.date_voyage,
            subquery.c.classe_voyage,
            subquery.c.heure_depart,
            subquery.c.ville_depart,
            subquery.c.user_names,
            subquery.c.user_surnames,
            subquery.c.num_cnis
        )

        # Exécutez la requête
        results = query.all()

        # Formater les données pour les grouper par voyage
        data = []
        for result in results:
            user_names = result.user_names.split(',')
            user_surnames = result.user_surnames.split(',')
            num_cnis = result.num_cnis.split(',')

            # Construire un groupe par voyage
            voyage_info = {
                "date_voyage": result.date_voyage,
                "classe_voyage": result.classe_voyage,
                "heure_depart": result.heure_depart,
                "ville_depart": result.ville_depart,
                "passengers": [
                    {"user_name": name, "user_surname": surname, "num_cni": cni}
                    for name, surname, cni in zip(user_names, user_surnames, num_cnis)
                ]
            }
            data.append(voyage_info)

        # Générez le PDF pour chaque voyage
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for voyage in data:
            pdf.cell(100, 10, f"Voyage - {voyage['date_voyage']} {voyage['heure_depart']} - Classe: {voyage['classe_voyage']}", ln=True)
            pdf.cell(100, 10, f"Ville de départ: {voyage['ville_depart']}", ln=True)
            pdf.ln(5)

            for passenger in voyage['passengers']:
                pdf.cell(100, 10, f"Nom: {passenger['user_name']} {passenger['user_surname']} - CNI: {passenger['num_cni']}", ln=True)
            pdf.ln(10)  # Espacement entre groupes de voyages




    ##########################################################################################################
    # Sauvegarder le PDF en mémoire
        pdf_output = pdf.output(dest='S').encode('latin1')

        # Envoyer le PDF par e-mail
        msg = Message(
            subject="Bordereau de voyage",
            recipients=["meffolea2205@gmail.com"]  # Adresse e-mail du destinataire
        )
        msg.body = "Veuillez trouver ci-joint le bordereau de voyage."
        msg.attach("bordereau.pdf", "application/pdf", pdf_output)

        mail.send(msg)

        # Retourner la réponse pour téléchargement
        response = make_response(pdf_output)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=bordereau.pdf'
        
    return response





# Configuration du planificateur APScheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    bordereau_automatique, 
    'cron', 
    hour=11,  # Heure à laquelle le bordereau sera envoyé
    minute=00, # Minute précise
    id='envoi_bordereau'  # ID unique pour la tâche
)
scheduler.start()








##############PROGRAMME PRINCIPAL###########################################################################


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
    app.run(debug=True,host="127.0.0.1", port=5002) 


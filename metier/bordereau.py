from fpdf import FPDF
from io import BytesIO
from flask import make_response

from apscheduler.schedulers.background import BackgroundScheduler
from model import Reservation,db

from flask_mail import Message
from metier.sendMail import *



#############################################################################################################
#generation du pdf du bordereau
def generate_bordereau(reservation):
   
    # Créer un document PDF
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Ajouter un titre
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Bordereau de Voyage", ln=True, align="C")
    pdf.ln(10)  # Ligne vide

    # Ajouter les informations des réservations
    pdf.set_font("Arial", size=12)
    for res in reservations:
        pdf.cell(100, 10, f"Nom: {res['user_name']} {res['user_surname']}", ln=True)
        pdf.cell(100, 10, f"CNI: {res['num_cni']}", ln=True)
        pdf.ln(5)  # Ligne vide

    # Sauvegarder le fichier dans un buffer en mémoire
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)

    # Sauvegarder le PDF dans un fichier
    with open(file_name, "wb") as f:
        f.write(buffer.read())
    
    buffer.close()
    """



    # Création du PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

# Ajout des informations au PDF

    for res in reservation:
        pdf.cell(100, 10, f"Nom: {res['user_name']} {res['user_surname']}", ln=True)
        pdf.cell(100, 10, f"CNI: {res['num_cni']}", ln=True)
        pdf.ln(5)  # Ligne vide

    
 # Exporter le PDF comme réponse pour téléchargement
    response = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=bordereau.pdf'  # "attachment" force le téléchargement
    return response

















################################################################################################################

def send_bordereau_task(data):
    # Récupérer les réservations pour une certaine date ou critère
    #reservations = db.session.query(
     #   Reservation.user_name,
      #  Reservation.user_surname,
       # Reservation.num_cni
    #).all()

    # Formater les réservations
    """
    formatted_reservations = [
        {
            "user_name": res.user_name,
            "user_surname": res.user_surname,
            "num_cni": res.num_cni
        }
        for res in data
        ]
    """
    # Générer le PDF
    pdf_file = generate_bordereau(data)
    
    # Envoyer le PDF par e-mail
    send_bordereau("meffolea2205@gmail.com", pdf_file)
"""
# Planifier la tâche pour qu'elle s'exécute tous les jours à 8h
scheduler.add_job(send_bordereau_task, 'cron', hour=17, minute=20)
scheduler.start()
"""































################

def bordereau():
    # Sous-requête pour trouver les combinaisons de date_voyage, heure_depart, ville_arrivee avec plusieurs enregistrements
    subquery = (
        db.session.query(
            Reservation.date_voyage,
            Reservation.classe_voyage,
            Reservation.heure_depart,
            Reservation.ville_depart
        )
        .group_by(
            Reservation.date_voyage,
            Reservation.classe_voyage,
            Reservation.heure_depart,
            Reservation.ville_depart
        )
        .having(func.count(Reservation.id) >= 1)
        .subquery()
    )
    
    # Requête principale pour récupérer les données correspondantes
    query = (
        db.session.query(
            Reservation.user_name,
            Reservation.user_surname,
            Reservation.num_cni
            
        )
        .filter(
            and_(
                Reservation.date_voyage == subquery.c.date_voyage,
                Reservation.classe_voyage ==subquery.c.classe_voyage,
                Reservation.heure_depart == subquery.c.heure_depart,
                Reservation.ville_depart == subquery.c.ville_depart
            )
        )
    )
    
    # Exécutez la requête
    results = query.all()

    # Formatez les résultats en JSON
    data = [
        {
            "user_name": result.user_name,
            "user_surname": result.user_surname,
            "num_cni": result.num_cni
        }
        for result in results
    ]
    
    
    #generate_bordereau(data)
    
    # Création du PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, "Bordereau de voyage", ln=True)


# Ajout des informations au PDF

    for res in data:
        pdf.cell(100, 10, f"Nom: {res['user_name']} {res['user_surname']}", ln=True)
        pdf.cell(100, 10, f"CNI: {res['num_cni']}", ln=True)
        pdf.ln(5)  # Ligne vide

    
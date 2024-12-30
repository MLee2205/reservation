from flask_mail import Message
#################################################################################################################
#fonction pour l envoi du mail a l agence

def send_bordereau(email, pdf_file):
    from config import  mail

    msg = Message(
        subject="Bordereau de Voyage",
        recipients=[email]
    )
    msg.body = "Veuillez trouver ci-joint le bordereau de voyage."
    
    # Joindre le fichier PDF
    with open(pdf_file, "rb") as f:
        msg.attach("bordereau.pdf", "application/pdf", f.read())
    
    # Envoyer l'e-mail
    mail.send(msg)




def prix_ticket(classe_voyage, nbre_place):
    if classe_voyage=='VIP':
        return 7000*nbre_place
    return 4000*nbre_place

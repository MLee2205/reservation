 function loadReservationPage() {
        fetch('reservation.html')
            .then(response => response.text())
            .then(data => {
                document.getElementById('reservationContent').innerHTML = data;
            });
    }

    document.querySelector('.menu-toggle').addEventListener('click', () => {
        document.querySelector('.nav-links').classList.toggle('show');
    });

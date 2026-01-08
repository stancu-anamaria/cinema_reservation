# cinema_reservation
Sistem complet de rezervări pentru cinema, realizat în Python, folosind arhitectură modulară pe clase, bază de date SQLite și interfață grafică prin Streamlit.
Acest proiect permite să gestioneze rezervările pentru un cinematograf. Utilizatorii pot vedea locurile disponibile, pot face rezervări, iar administratorii pot adăuga noi filme sau sălile disponibile.
Caracteristici principale:

1.Autentificare si roluri:
Administrator – are acces complet la gestionarea filmelor, sălilor și rezervărilor.
Client / Vizitator – poate vizualiza filme și crea rezervări.
Este un sistem simplu și intuitiv de login.

2.Gestionarea filmelor:
Vizualizarea filmelor disponibile (poster, descriere, rating, gen, distribuție etc.).
Adăugarea manuală a filmelor:titlu, durată, sală, descriere în limba română, distribuție, genuri
Import automat filme din OMDb API cu: poster automat, rating, genuri, sugestii generate pentru administrator.
Protecție împotriva duplicatelor (nu se pot adăuga filme identice în aceeași sală).

3.Gestionarea salilor:
Vizualizare săli cu informații despre capacitate.
Adăugare săli noi (nume, rânduri, locuri pe rând).
Ștergere săli (cu eliminarea automată a filmelor și rezervărilor asociate).

4.Gestionarea rezervarilor:
Vizualizare rezervări într-o listă ordonată.
Crearea unei rezervări (film + sală + poziție loc).
Ștergerea rezervărilor (doar de administrator).
Sistem extensibil pentru rezervare de grup (în curs de dezvoltare).

5.Arhitectură Modulară (OOP):
Proiectul este organizat în module clare, pe clase:
-models/ – Modele OOP
Clase simple, reprezentând entitățile din sistem:
Film
Sala
Rezervare
Loc
Fiecare clasă conține doar date, fără logică inutilă — logica este în servicii.

-services/ – Logică aplicației
Separat pentru claritate și scalabilitate:
db.py – gestionarea conexiunii SQLite
film_service.py – CRUD filme + validări
sala_service.py – CRUD săli
rezervare_service.py – creare, listare, ștergere rezervări
api_filme_service.py – conectare la OMDb + prelucrarea datelor
Serviciile lucrează cu obiecte, nu cu dicționare – arhitectură complet OOP.

-interface/ – Componente Streamlit
UI împărțit pe sub-modul:
gestionare filme
gestionare săli
rezervări
autentificare
dashboard pentru administrator

-app.py
Punctul de intrare în aplicație.
Conține logica meniului, navigării și conectarea cu serviciile.

6.Bază de date:
Proiectul folosește SQLite, cu următoarele tabele:filme, sali, rezervari
Baza de date se află în data/cinema.db.

Instalare si rulare:
1️.Clonează repository-ul:
git clone <link-repo-github>
cd cinema-reservation 
2.Instalează dependențele: pip install -r requirements.txt
3️.Rulează aplicația: python -m streamlit run interface/app.py
Aplicația se deschide automat în browser.

Conturi implicite:
Administrator: 
-username: admin
-parola: admin123
# cinema_reservation
Sistem complet de rezervări pentru cinema, realizat în Python, folosind arhitectură modulară pe clase, bază de date SQLite și interfață grafică prin Streamlit. Acest proiect permite să gestioneze rezervările pentru un cinematograf. Utilizatorii pot vedea locurile disponibile, pot face rezervări, iar administratorii pot adăuga noi filme sau sălile disponibile. Caracteristici principale:

1.Autentificare si roluri: Administrator – are acces complet la gestionarea filmelor, sălilor și rezervărilor. Client / Vizitator – poate vizualiza filme și crea rezervări. Este un sistem simplu și intuitiv de login.

2.Gestionarea filmelor: Vizualizarea filmelor disponibile (poster, descriere, rating, gen, distribuție etc.). Adăugarea manuală a filmelor:titlu, durată, sală, descriere în limba română, distribuție, genuri Import automat filme din OMDb API cu: poster automat, rating, genuri, sugestii generate pentru administrator. Protecție împotriva duplicatelor (nu se pot adăuga filme identice în aceeași sală).

3.Gestionarea salilor: Vizualizare săli cu informații despre capacitate. Adăugare săli noi (nume, rânduri, locuri pe rând). Ștergere săli (cu eliminarea automată a filmelor și rezervărilor asociate).

4.Gestionarea rezervarilor: Vizualizare rezervări într-o listă ordonată. Crearea unei rezervări (film + sală + poziție loc). Ștergerea rezervărilor (doar de administrator). Sistem extensibil pentru rezervare de grup (în curs de dezvoltare).

5.Arhitectură Modulară (OOP): Proiectul este organizat în module clare, pe clase: -models/ – Modele OOP Clase simple, reprezentând entitățile din sistem: Film Sala Rezervare Loc Fiecare clasă conține doar date, fără logică inutilă — logica este în servicii.

Directorul models conține clasele care definesc entitățile principale ale sistemului de rezervări pentru cinema. Acestea modelează datele reale din aplicație, precum filmele, sălile, locurile și rezervările. Fiecare clasă reflectă structura informațiilor stocate în baza de date și utilizate în interfață.

Directorul services reprezintă partea logică a aplicației de rezervări pentru cinema. Aici sunt implementate regulile de funcționare ale sistemului și operațiile de gestionare a filmelor, sălilor și rezervărilor. Acest director se ocupă de validarea datelor, prevenirea erorilor și coordonarea operațiilor asupra bazei de date. Tot aici este realizată integrarea cu OMDb API pentru importul automat al filmelor. services transformă acțiunile utilizatorilor în operații reale asupra datelor.

Directorul interface conține componentele care definesc interfața grafică a aplicației realizată cu Streamlit. Acesta este responsabil pentru afișarea filmelor, sălilor, locurilor disponibile și pentru interacțiunea utilizatorilor cu sistemul. Fiecare modul corespunde unei funcționalități concrete, precum autentificarea, rezervările sau administrarea filmelor. Interfața controlează accesul în funcție de rolul utilizatorului.

Directorul data conține baza de date SQLite utilizată de aplicație pentru stocarea informațiilor. Aici sunt salvate datele despre filme, săli și rezervări, astfel încât acestea să fie disponibile la fiecare rulare a aplicației. Accesul la date se face exclusiv prin serviciile aplicației. Acest director este esențial pentru păstrarea și consistența datelor.

Directorul repositories este responsabil de accesul direct la baza de date SQLite. Acesta conține module care execută interogările SQL pentru salvarea, citirea și ștergerea datelor despre filme, săli și rezervări. Fiecare repository este asociat unei entități din sistem. Serviciile folosesc acest director pentru a lucra cu datele fără a cunoaște detalii despre baza de date.

Fișierul principal app.py
Fișierul app.py este punctul de pornire al aplicației de rezervări pentru cinema. Acesta inițializează aplicația Streamlit și gestionează fluxul general al aplicației. În acest fișier este realizată autentificarea utilizatorilor și navigarea între diferitele secțiuni. app.py face legătura dintre interfața grafică și logica aplicației. El asigură funcționarea unitară a tuturor componentelor sistemului.

6.Bază de date: Proiectul folosește SQLite, cu următoarele tabele:filme, sali, rezervari Baza de date se află în data/cinema.db.

Cerinte: Python 3.11+

Instalare si rulare: 1️.Clonează repository-ul: git clone <link-repo-github> cd cinema-reservation 2.Instalează dependențele: pip install -r requirements.txt 3️.Rulează aplicația: python -m streamlit run interface/app.py Aplicația se deschide automat în browser.
Conturi implicite: Administrator: -username: admin -parola: admin123


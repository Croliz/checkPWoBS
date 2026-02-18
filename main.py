import requests
from bs4 import BeautifulSoup
import smtplib
import os
from email.message import EmailMessage


def analizza_e_stampa_risultato(url, categoria):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    print(f"\n--- ANALISI IN CORSO PER: {categoria} ({url}) ---")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- 1. CONTROLLO TABELLE STATICHE ---
        tabella_standard = soup.find('table', class_='items')
        righe_tabella = tabella_standard.find_all('tr') if tabella_standard else []

        # --- 2. CONTROLLO COMPONENTI DINAMICI ---
        tag_dinamici = soup.find_all(lambda tag: tag.name and tag.name.startswith('tm-'))
        classi_svelte = soup.find_all(class_=lambda x: x and 'svelte-' in x)

        # --- 3. DETERMINAZIONE VERDETTO ---
        if tabella_standard and len(righe_tabella) > 1:
            verdetto = "✅ USA BEAUTIFUL SOUP"
        elif len(tag_dinamici) > 0 and not tabella_standard:
            verdetto = "❌ USA PLAYWRIGHT (Componenti tm-)"
        elif len(classi_svelte) > 0 and len(soup.text.strip()) < 500:
            verdetto = "❌ USA PLAYWRIGHT (Svelte/Poco testo)"
        else:
            verdetto = "🤔 VERDETTO INCERTO"

        print(f"RISULTATO: {verdetto}")
        # Restituiamo il testo formattato come richiesto
        return f"Per {categoria}: {verdetto}\n(Link: {url})\n{'-' * 30}\n"

    except Exception as e:
        errore = f"Per le {categoria}: ❌ ERRORE ({e})\n{'-' * 30}\n"
        print(errore)
        return errore


def invia_mail(testo_report):
    user = os.getenv('MAIL_USERNAME')
    password = os.getenv('MAIL_PASSWORD')

    if not user or not password:
        print("Errore: Credenziali mail non trovate.")
        return

    msg = EmailMessage()
    msg.set_content(testo_report)
    msg['Subject'] = 'Report Analisi Scraping Transfermarkt'
    msg['From'] = user
    msg['To'] = user

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
        server.quit()
        print("\nMail riepilogativa inviata con successo!")
    except Exception as e:
        print(f"Errore invio mail: {e}")


if __name__ == "__main__":
    # Definiamo i link associati alle loro etichette
    lista_analisi = [
        {"url": "https://www.transfermarkt.it/serie-a/startseite/wettbewerb/IT1", "label": "Competizioni"},
        {"url": "https://www.transfermarkt.it/potenza-calcio/startseite/verein/7197", "label": "Squadre"},
        {"url": "https://www.transfermarkt.it/federico-pace/leistungsdatendetails/spieler/469899", "label": "Giocatori"}
    ]

    report_finale = "REPORT ANALISI TM\n\n"

    # Ciclo sulla lista di dizionari
    for voce in lista_analisi:
        risultato_singolo = analizza_e_stampa_risultato(voce["url"], voce["label"])
        report_finale += risultato_singolo

    # Stampa di controllo nei log di GitHub
    print("\n--- REPORT FINALE ---")
    print(report_finale)

    # Invio mail singola
    invia_mail(report_finale)
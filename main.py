import requests
from bs4 import BeautifulSoup
import smtplib
import os
from email.message import EmailMessage

def analizza_e_stampa_risultato(url):
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

    print(f"\n--- ANALISI IN CORSO PER: {url} ---")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- 1. CONTROLLO TABELLE STATICHE (Come nella tua foto 2) ---
        # Cerchiamo la classica <table class="items">
        tabella_standard = soup.find('table', class_='items')
        righe_tabella = tabella_standard.find_all('tr') if tabella_standard else []

        print(f"[DEBUG] Tabelle standard trovate: {1 if tabella_standard else 0}")
        print(f"[DEBUG] Righe trovate nella tabella: {len(righe_tabella)}")

        # --- 2. CONTROLLO COMPONENTI DINAMICI (Come nella tua foto 1) ---
        # Cerchiamo tag che iniziano con 'tm-' o classi 'svelte-'
        tag_dinamici = soup.find_all(lambda tag: tag.name and tag.name.startswith('tm-'))
        classi_svelte = soup.find_all(class_=lambda x: x and 'svelte-' in x)

        print(f"[DEBUG] Tag 'tm-' (dinamici) trovati: {len(tag_dinamici)}")
        print(f"[DEBUG] Elementi Svelte trovati: {len(classi_svelte)}")

        # --- 3. VERDETTO FINALE STAMPATO A VIDEO ---
        print("\n" + "=" * 40)
        print("RISULTATO DELL'ANALISI:")
        print("=" * 40)

        if tabella_standard and len(righe_tabella) > 1:
            print("✅ USA BEAUTIFUL SOUP")
            print("MOTIVO: Ho trovato una tabella HTML standard con dati dentro.")
            return "✅ USA BEAUTIFUL SOUP"

        elif len(tag_dinamici) > 0 and not tabella_standard:
            print("❌ USA PLAYWRIGHT")
            print("MOTIVO: Ci sono componenti 'tm-' ma nessuna tabella reale.")
            print("I dati sono probabilmente caricati via JavaScript.")
            return "❌ USA PLAYWRIGHT"

        elif len(classi_svelte) > 0 and len(soup.text.strip()) < 500:
            print("❌ USA PLAYWRIGHT")
            print("MOTIVO: Il sito usa Svelte e c'è pochissimo testo nell'HTML.")
            return "❌ USA PLAYWRIGHT"

        else:
            print("🤔 VERDETTO INCERTO")
            print("MOTIVO: La struttura è ambigua. Prova prima con BS4, se fallisce passa a PW.")
            return "🤔 VERDETTO INCERTO"

    except Exception as e:
        print(f"❌ ERRORE DURANTE LA RICHIESTA: {e}")


def invia_mail(testo_report):
    user = os.getenv('MAIL_USERNAME')
    password = os.getenv('MAIL_PASSWORD')

    msg = EmailMessage()
    msg.set_content(testo_report)
    msg['Subject'] = 'Report Analisi Scraping TM'
    msg['From'] = user
    msg['To'] = user

    try:
        # Passiamo alla porta 587 che è più stabile per gli script
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Cripta la connessione
        server.login(user, password)
        server.send_message(msg)
        server.quit()
        print("Mail inviata con successo!")
    except Exception as e:
        print(f"Errore invio mail: {e}")


if __name__ == "__main__":
    url_test = "https://www.transfermarkt.it/federico-pace/leistungsdatendetails/spieler/469899"
    url_bs = "https://www.transfermarkt.it/potenza-calcio/startseite/verein/7197"
    report = analizza_e_stampa_risultato(url_test)

    print(report)
    invia_mail(report)

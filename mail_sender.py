# coding=utf-8
from datetime import datetime
import smtplib
import time
import os

def notify_service(intervallo, ip, labels, kind):

    folder = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Documents') + "\\smersh_mail_setting.txt"
    done = False
    while not done:
        try:
            with open(folder, mode="r") as file:
                content = file.read().split("|")
            done = True
        except:
            # Il file potrebbe essere usato contemporaneamente da smersh-on poller e blacklist poller se runnati
            # contemporaneamente. Pertanto ho previsto questa eccezione.
            time.sleep(3)

    now = datetime.now()
    timestamp = now.strftime("%d/%m/%Y %H:%M:%S")

    if not labels:
        folder = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Documents') + "\\smersh_blacklist.txt"
        fatto = False
        while not fatto:
            try:
                with open(folder, mode='r') as file:
                    listato = file.read().splitlines()
                fatto = True
            except:
                # Il file potrebbe essere usato contemporaneamente da smersh-on poller e blacklist poller se runnati
                # contemporaneamente. Pertanto ho previsto questa eccezione.
                time.sleep(3)

        for add in ip:
            for idx, x in enumerate(listato):
                if add in x:
                    labels.append(listato[idx-1])
                    break
                elif idx+1 == len(listato):
                    labels.append("NUOVO IP")

                    # Quindi aggiungiamoli alla blacklist se dopo averla scorsa tutta non trovo corrispondenze
                    label = "# NUOVO - DA VERIFICARE"
                    blck = os.path.join(os.path.join(os.environ['USERPROFILE']),'Documents') + "\\smersh_blacklist.txt"
                    try:
                        with open(blck, mode="a") as blacklist:
                            blacklist.write("\n#" + label)
                            blacklist.write("\n" + add)
                            print "\n[*] Blacklist file aggiornata con successo!"
                    except:
                        print "\n[!] Qualcosa è andato storto nell'aggiornamento della blacklist!"

    for add in ip:
        # Infine estraiamo i dati generati dagli IP Segnalati...
        try:
            from smersh_off_forensics import estrattore_dati
            estrattore_dati(choose="5", ips=add, intervallo=(86400), verbose=False)
            print "\n[*] Estrazioni report avvenuta con successo!"
        except:
            print"\n[!] Qualcosa è andato storto con il dump delle attività degli IP segnalati."
            return None

    sender = content[0]
    receivers = content[1].split(',')
    message_payload = content[2].format(kind, str(intervallo),", ".join(ip), ", ".join(labels), timestamp)
    address = content[3]

    try:
        smtpObj = smtplib.SMTP(address)
        smtpObj.sendmail(sender, receivers, message_payload)
        print "\n   [***] Notificate figure interessate!"
    except smtplib.SMTPException:
        print "\n[!] Error: unable to send email"

    return None

'''if __name__ == "__main__":
    notify_service(5, ["1","2"])'''
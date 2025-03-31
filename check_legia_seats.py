import requests
import datetime
import time

EVENT_ID = 6755
API_URL = f"https://bilety.legia.com/Stadium/GetWGLSectorsInfo?eventId={EVENT_ID}"
WEBHOOK_URL = "https://webhook.site/54a5075f-f49d-4d6f-bbef-3ccf27cb8736"
ZYLETA_IDS = {603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615}

previous_total = None
previous_zyleta = None

def fetch_and_send():
    global previous_total, previous_zyleta

    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Błąd przy pobieraniu danych: {e}")
        return

    total = 0
    zyleta = 0

    for sector in data.get("sectors", []):
        for area in sector.get("freeSeatsByPriceArea", []):
            free = area["freeSeatsNo"]
            total += free
            if sector["id"] in ZYLETA_IDS:
                zyleta += free

    change_total = None if previous_total is None else total - previous_total
    change_zyleta = None if previous_zyleta is None else zyleta - previous_zyleta

    previous_total = total
    previous_zyleta = zyleta

    message = (
        f"Dostępnych miejsc ogółem: {total}"
        + (f" (zmiana: {change_total})" if change_total is not None else "") + " "
        f"Żyleta: {zyleta} miejsc"
        + (f" (zmiana: {change_zyleta})" if change_zyleta is not None else "")
    )

    payload = {
        "timestamp": datetime.datetime.now().isoformat(),
        "available_seats_total": total,
        "available_seats_zyleta": zyleta,
        "change_total": change_total,
        "change_zyleta": change_zyleta,
        "message": message
    }

    try:
        webhook_response = requests.post(WEBHOOK_URL, json=payload)
        print(f"[{datetime.datetime.now()}] Webhook wysłany: {webhook_response.status_code}")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Błąd przy wysyłaniu webhooka: {e}")

if __name__ == "__main__":
    while True:
        fetch_and_send()
        time.sleep(600)  # 10 minut

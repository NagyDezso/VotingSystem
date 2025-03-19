import socket
import requests
import os
from backend.models import Vote

DISPLAY_URL = os.getenv("DISPLAY_URL", "http://localhost:8080")
BROADCAST_IP = os.getenv("BROADCAST_IP", "255.255.255.255")
UDP_PORT = int(os.getenv("UDP_PORT", "5005"))

def notify_display(vote_data: Vote):
    """
    Kijelző értesítése REST GET kérés segítségével.
    """
    params = {"nev": vote_data.name, "szavazat": vote_data.vote}
    try:
        response = requests.get(DISPLAY_URL, params=params, timeout=5)
        print("Display notified, status code:", response.status_code)
    except Exception as e:
        print("Error notifying display:", e)

def send_udp_message(
    message: str, broadcast_ip: str = BROADCAST_IP, port: int = UDP_PORT
):
    """
    UDP broadcast üzenet küldése a kliensek felé.
    Használható a szavazás indításának vagy lezárásának jelzésére.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        sock.sendto(message.encode("utf-8"), (broadcast_ip, port))
        print("UDP message sent:", message)
    except Exception as e:
        print("Error sending UDP message:", e)
    finally:
        sock.close()

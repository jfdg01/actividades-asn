"""Mide cuándo cierra traefik una conexión entrante.

Uso: python3 prueba-conexiones.py inactiva|keepalive|lenta

- inactiva: una petición y después silencio; mide cuándo cierra traefik la conexión.
- keepalive: una petición por segundo en la misma conexión, hasta que traefik
  responde con "Connection: close".
- lenta: envía una cabecera sin fin, un byte por segundo, como un ataque
  slowloris; mide cuándo cierra traefik la conexión, o para a los 90 s.
"""
import http.client
import socket
import sys
import time

modo = sys.argv[1]
c = http.client.HTTPConnection("localhost", 80, timeout=300)
inicio = time.monotonic()


def pedir():
    """Una petición GET / en la conexión abierta; devuelve la respuesta leída."""
    c.request("GET", "/")
    r = c.getresponse()
    r.read()
    return r


if modo == "inactiva":
    print(pedir().status)
    inicio = time.monotonic()
    c.sock.recv(1)  # devuelve b"" cuando traefik cierra la conexión
    print(f"conexión inactiva cerrada por traefik a los {time.monotonic() - inicio:.1f} s")

elif modo == "keepalive":
    for n in range(1, 300):
        r = pedir()
        t = time.monotonic() - inicio
        if r.getheader("Connection", "").lower() == "close":
            print(f"petición {n} a los {t:.1f} s: traefik responde 'Connection: close'")
            break
        print(f"petición {n} a los {t:.1f} s: {r.status}")
        time.sleep(1)

elif modo == "lenta":
    s = socket.create_connection(("localhost", 80))
    s.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\nX-Lenta: ")
    try:
        for _ in range(90):
            s.sendall(b"a")
            s.settimeout(1)
            try:
                if s.recv(4096) == b"":
                    break
            except socket.timeout:
                pass
    except (BrokenPipeError, ConnectionResetError):
        pass
    print(f"petición lenta cortada por traefik a los {time.monotonic() - inicio:.1f} s")

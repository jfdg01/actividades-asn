# phpwebappv2: frontales PHP balanceados con Traefik (actividad 3.3)

Despliegue con tres servicios: `traefik` (balanceador), `wwwserver` (2 réplicas de la app PHP+Apache) y `mariadb`.

## Requisitos

Docker con `docker compose`. Los puertos 80 y 8080 del equipo deben estar libres.

## Uso

```bash
cp .env.example .env          # credenciales de la BD (no se versiona .env)
make                          # docker compose up -d --build: construye y lanza todo
```

- Aplicación (a través del balanceador): <http://localhost/>
- Panel de Traefik (nodos descubiertos): <http://localhost:8080/> → HTTP Services → `wwwserver@docker`
- Acceso directo a una réplica: `docker compose ps` muestra su puerto aleatorio del host.
- La BD tarda unos segundos en inicializarse la primera vez.

## Descubrimiento dinámico

Traefik usa el proveedor `docker` (`traefik/traefik.yml`) y solo balancea los contenedores con la etiqueta `traefik.enable=true`.

```bash
docker compose up -d --scale wwwserver=5 --no-recreate   # 5 réplicas
docker compose up -d --scale wwwserver=2 --no-recreate   # de vuelta a 2
```

## Ajuste de recursos

Cada frontal tiene `cpus: .25` y `mem_limit: 48m`. El `Dockerfile` limita Apache a `MaxRequestWorkers 30` (por defecto 150, que agota los 48 MiB). Para reproducir la caída, comentar la línea `RUN sed ... MaxRequestWorkers` y reconstruir:

```bash
docker compose down && docker compose up -d --build
```

## Pruebas de carga

`ab` (Apache Benchmark, paquete `apache2-utils`). Si no está instalado se puede usar su imagen oficial:

```bash
AB="docker run --rm --network host httpd:2.4 ab"
$AB -c 40 -t 20 http://localhost:<puerto-frontal>/   # un solo frontal
$AB -c 10 -t 20 http://localhost/                    # balanceador
$AB -c 20 -t 20 http://localhost/
```

Monitorizar en otra terminal con `docker stats` (o `make mon`).

## Tolerancia a fallos

Traefik comprueba cada frontal con un health check L7 (etiquetas `healthcheck.*` en `compose.yml`): pide `/` cada 5 s y saca del servicio el frontal que no responde en 5 s.

```bash
for i in 1 2 3 4; do curl -s -m 10 localhost/ | grep -o 'Container: [a-f0-9]*' || echo 'sin respuesta en 10 s'; done
docker stop phpwebappv2-wwwserver-2      # traefik lo quita al instante
docker start phpwebappv2-wwwserver-2
docker pause phpwebappv2-wwwserver-2     # en unos 5-10 s aparece DOWN en el panel
docker unpause phpwebappv2-wwwserver-2
```

Pausar un frontal solo cuando el panel muestra los dos servidores `UP`: un frontal pausado justo después de `docker start` queda fuera del servicio hasta reiniciar traefik.

## Protección frente a la demanda

- **Middlewares** (etiquetas en `compose.yml`, se aplican con `docker compose up -d wwwserver`): `wwwserver-ratelimit` admite 100 peticiones/s por IP con ráfagas de 50, y `wwwserver-inflight` admite 20 peticiones en curso. El router los aplica en ese orden. Una petición rechazada recibe `429`.
- **Tiempos del entrypoint `web`** (`traefik/traefik.yml`, se aplican con `docker restart phpwebappv2-traefik-1`): una conexión dura 10 s como máximo (`keepAliveMaxTime`), una petición se lee en 10 s como máximo (`readTimeout`) y una conexión inactiva se cierra a los 5 s (`idleTimeout`).

```bash
$AB -c 50 -t 20 http://localhost/                                        # casi todo 429
docker run --rm --network phpwebappv2_default httpd:2.4 ab -c 50 -t 20 http://traefik/   # atacante con otra IP
for i in $(seq 20); do curl -s -o /dev/null -w '%{http_code} %{time_total}\n' localhost/; done   # usuario: 200

python3 prueba-conexiones.py inactiva    # cierre a los 5 s
python3 prueba-conexiones.py keepalive   # "Connection: close" a los 10 s
python3 prueba-conexiones.py lenta       # petición lenta cortada a los 10 s
```

## Parar

```bash
make clean   # docker compose down
```

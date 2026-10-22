# phpwebappv2: frontales PHP balanceados con Traefik (actividad 3.2)

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

## Parar

```bash
make clean   # docker compose down
```

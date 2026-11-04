# phpwebappv2 en Kubernetes (Actividad 4.1)

Aplicación PHP de notas con dos frontales balanceados por un Ingress y una base de datos MariaDB, desplegada en un clúster Kubernetes local.

## Contenido

```text
phpwebappv2/
├── Dockerfile             imagen asn/phpwebapp:v1 (php:8-apache, MaxRequestWorkers 30)
├── .dockerignore
├── html/                  código de la aplicación
├── k8s/
│   ├── wwwserver.yaml     Deployment (2 réplicas) y Service NodePort de los frontales
│   ├── mariadb.yaml       Deployment y Service ClusterIP de MariaDB
│   ├── loadbalancer.yaml  Ingress lb-ingress hacia wwwserver:80
│   ├── configmap.yaml     ConfigMap phpwebapp-config (DB_DSN, DB_NAME, MYSQL_USER)
│   └── db.env             contraseñas con las que se crea el Secret db-credentials
└── kics-report/           último análisis de KICS v2.2.0 (final.html y final.json)
```

## Requisitos

- Clúster Kubernetes local con `kubectl` configurado. Probado con Docker Desktop en modo *kind*.
- Controlador Ingress Traefik instalado con Helm, por ejemplo con el script `k8s/ingress-controller/traefik/helm_install.sh` del repositorio [asnwebapps](https://github.com/jrbalsas/asnwebapps).
- Opcional: metrics-server (`k8s/metrics-server/helm_install.sh` del mismo repositorio) para consultar el consumo con `kubectl top pod`.

## 1. Construir la imagen

```bash
docker build -t asn/phpwebapp:v1 .
```

El despliegue usa `imagePullPolicy: IfNotPresent`, así que el clúster de Docker Desktop toma la imagen local. En un clúster *kind* creado a mano hay que cargarla antes: `kind load docker-image asn/phpwebapp:v1`.

## 2. Crear el Secret y desplegar

```bash
kubectl create secret generic db-credentials --from-env-file=k8s/db.env
kubectl apply -f k8s/
kubectl get pods -w
```

El Secret debe existir antes que los pods que lo usan. `kubectl apply -f k8s/` solo procesa los ficheros `.yaml`; `db.env` no se aplica.

## 3. Acceder

- Aplicación: <http://localhost/>. La primera vez, MariaDB tarda unos segundos en inicializar la base de datos.
- Panel de Traefik: <http://localhost/dashboard/> (la barra final es obligatoria).

## Configuración

| Variable en el contenedor | Origen | Pods |
| --- | --- | --- |
| `DB_DSN` | ConfigMap `phpwebapp-config` | wwwserver |
| `MYSQL_USER` | ConfigMap `phpwebapp-config` | wwwserver, mariadb |
| `MYSQL_DATABASE` (clave `DB_NAME`) | ConfigMap `phpwebapp-config` | mariadb |
| `MYSQL_PASSWORD` | Secret `db-credentials` | wwwserver, mariadb |
| `MYSQL_ROOT_PASSWORD` | Secret `db-credentials` | mariadb |

| Contenedor | Requests (CPU / memoria) | Limits (CPU / memoria) |
| --- | --- | --- |
| phpwebapp (cada réplica) | 100m / 64Mi | 1000m / 256Mi |
| mariadb | 250m / 128Mi | 1000m / 256Mi |

Los dos contenedores declaran `securityContext.allowPrivilegeEscalation: false`.

`db.env` contiene credenciales de laboratorio. En un repositorio real no se versionaría.

Si se cambia `db.env`, hay que recrear el Secret y los pods:

```bash
kubectl delete secret db-credentials
kubectl create secret generic db-credentials --from-env-file=k8s/db.env
kubectl rollout restart deployment wwwserver mariadb
```

La base de datos no tiene volumen persistente: si se recrea el pod de MariaDB, se pierden las notas añadidas.

## Análisis estático con KICS

El informe incluido se generó con KICS v2.2.0 sobre el directorio `k8s/`. Para repetirlo con la imagen Docker de KICS:

```bash
docker run -t -v "$PWD":/path checkmarx/kics:latest scan -p /path/k8s \
  -o /path/kics-report --report-formats "html,json" --output-name final
```

## Eliminar el despliegue

```bash
kubectl delete -f k8s/
kubectl delete secret db-credentials
```

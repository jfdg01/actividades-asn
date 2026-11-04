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


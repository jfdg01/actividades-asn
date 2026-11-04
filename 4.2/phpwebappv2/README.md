# phpwebappv2 en Kubernetes (Actividad 4.2)

Aplicación PHP de notas con dos frontales balanceados por un Ingress y una base de datos MariaDB. Unas NetworkPolicies segmentan la red interna. La aplicación se despliega en un clúster local *kind* y en GKE.

## Contenido

```text
phpwebappv2/
├── Dockerfile             imagen jfdg0002/phpwebapp:v1 (php:8-apache, MaxRequestWorkers 30)
├── .dockerignore
├── html/                  código de la aplicación
└── k8s/
    ├── wwwserver.yaml     Deployment (2 réplicas) y Service NodePort de los frontales
    ├── mariadb.yaml       Deployment y Service ClusterIP de MariaDB
    ├── loadbalancer.yaml  Ingress lb-ingress hacia wwwserver:80
    ├── configmap.yaml     ConfigMap phpwebapp-config (DB_DSN, DB_NAME, MYSQL_USER)
    ├── db.env             contraseñas con las que se crea el Secret db-credentials
    └── network-policy/    reglas de red, en el orden de su nombre
```

## Requisitos

- Clúster Kubernetes local con `kubectl` configurado. Probado con *kind* y `k8s/kind/kind-cluster-wsl.yml` del repositorio [asnwebapps](https://github.com/jrbalsas/asnwebapps). La red *kindnet* de *kind* aplica las NetworkPolicies.
- Controlador Ingress Traefik instalado con Helm, por ejemplo con el script `k8s/ingress-controller/traefik/helm_install.sh` del mismo repositorio.
- Opcional: metrics-server (`k8s/metrics-server/helm_install.sh` del mismo repositorio) para consultar el consumo con `kubectl top pod`.

## 1. Construir y publicar la imagen

```bash
docker build -t jfdg0002/phpwebapp:v1 .
docker push jfdg0002/phpwebapp:v1
```

La imagen es pública en Docker Hub. Los dos clústeres la descargan de allí, porque GKE no ve las imágenes del equipo local.

## 2. Crear el Secret y desplegar

```bash
kubectl create secret generic db-credentials --from-env-file=k8s/db.env
kubectl apply -f k8s/ -f k8s/network-policy/
kubectl get pods -w
```

El Secret debe existir antes que los pods que lo usan. `kubectl apply -f k8s/` solo procesa los ficheros `.yaml`; `db.env` no se aplica.

## 3. Acceder

- Aplicación: <http://localhost/>. La primera vez, MariaDB tarda unos segundos en inicializar la base de datos.
- Panel de Traefik: <http://localhost/dashboard/> (la barra final es obligatoria).

## Segmentación de red

Cada pod lleva la etiqueta `app: asn-app` y una etiqueta `role`: `role: wwwserver` en los frontales y `role: database` en MariaDB. Las reglas que seleccionan un pod se suman: el pod acepta una conexión si alguna regla la permite.

| Regla | Pods | Entrada | Salida |
| --- | --- | --- | --- |
| `1_deny-all-network-policy.yml` | `app: asn-app` | nada | nada |
| `2_allow-dns-policy.yml` | `app: asn-app` | — | DNS del clúster, 53 UDP y TCP |
| `3_wwwserver-network-policy.yml` | `role: wwwserver` | 80/TCP desde cualquier origen | pods `role: database` |
| `4_database-network-policy.yml` | `role: database` | 3306/TCP solo desde `role: wwwserver` | — |

Las reglas 1 y 2 son las del repositorio asnwebapps. La entrada de los frontales admite cualquier origen, porque Traefik y el balanceador de GKE están fuera de la aplicación.

Comprobación desde un pod de prueba sin la etiqueta `app: asn-app`:

```bash
kubectl run --rm -it test-pod --image busybox -- sh
nc -zvw 2 wwwserver 80
nc -zvw 2 mariadb 3306
```

El puerto 80 responde, y el 3306 no. Un frontal no sale a Internet: `curl -vm 2 https://www.ujaen.es` falla dentro de su pod.

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
| phpwebapp (cada réplica) | 50m / 64Mi | 100m / 256Mi |
| mariadb | 50m / 128Mi | 150m / 256Mi |

Los límites de CPU caben en el único nodo de GKE junto a los pods del sistema.

Los dos contenedores declaran `securityContext.allowPrivilegeEscalation: false`.

`db.env` contiene credenciales de laboratorio. En un repositorio real no se versionaría.

Si se cambia `db.env`, hay que recrear el Secret y los pods:

```bash
kubectl delete secret db-credentials
kubectl create secret generic db-credentials --from-env-file=k8s/db.env
kubectl rollout restart deployment wwwserver mariadb
```

La base de datos no tiene volumen persistente: si se recrea el pod de MariaDB, se pierden las notas añadidas.

## Eliminar el despliegue

```bash
kubectl delete -f k8s/network-policy/ -f k8s/
kubectl delete secret db-credentials
```

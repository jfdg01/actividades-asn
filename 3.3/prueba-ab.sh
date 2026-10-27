#!/bin/bash
# Lanza ab contra el balanceador y guarda en notas/ la salida de ab, de docker stats
# y el log de acceso de traefik comprimido, y muestra el recuento de códigos de estado.
# Uso: ./prueba-ab.sh <nombre> [opciones de ab, por defecto -c 50 -t 20]
set -e
cd "$(dirname "$0")"
nombre=$1; shift
opciones=${*:--c 50 -t 20}
desde=$(date -u +%Y-%m-%dT%H:%M:%SZ)

docker stats --format '{{.Name}} {{.CPUPerc}} {{.MemUsage}} {{.PIDs}}' \
  phpwebappv2-traefik-1 phpwebappv2-wwwserver-1 phpwebappv2-wwwserver-2 > "notas/$nombre-stats.txt" &
stats=$!
docker run --rm --network host httpd:2.4 ab $opciones -n 100000 http://localhost/ > "notas/$nombre-ab.txt" 2>&1
kill $stats

docker logs --since "$desde" phpwebappv2-traefik-1 2>&1 > "notas/$nombre-log.txt"

grep -E 'Complete requests|Failed|Non-2xx|Requests per second|Time per request.*mean\)$' "notas/$nombre-ab.txt"
echo '# códigos en el log de acceso'
grep -o '"GET / HTTP/1.0" [0-9]*' "notas/$nombre-log.txt" | awk '{print $NF}' | sort | uniq -c
echo '# máximos de docker stats'
sed 's/\x1b\[[0-9;]*[A-Za-z]//g' "notas/$nombre-stats.txt" | awk 'NF==6 {n=$1; c=$2+0; m=$3+0; p=$6+0
  if(c>cpu[n])cpu[n]=c; if(m>mem[n])mem[n]=m; if(p>pid[n])pid[n]=p}
  END {for(n in cpu) printf "%s cpu %.1f%% mem %.1fMiB pids %d\n", n, cpu[n], mem[n], pid[n]}' | sort
gzip -f "notas/$nombre-log.txt"

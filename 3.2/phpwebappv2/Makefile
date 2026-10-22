LOCALPATH=html

dev:
	docker compose up -d --build
	docker compose ps
build: clean 
	docker compose build 
	@echo  Imagenes creadas
clean: cleandependencies
	-docker compose down 
	@echo Contenedores borrados 
cleandependencies:
	-
mon: monitor
monitor:
	docker stats

# Medidas de seguridad en Spring Boot (Actividad 2.4)

Autores: Javier Francisco Dibo Gómez y Miguel Bolívar García.

La aplicación prueba las medidas de seguridad de Spring Boot que estudia el informe de la actividad 2.3. Cada ejemplo tiene una ruta insegura y una ruta protegida, con la misma entrada.

## La pila

- OpenJDK 21, con la imagen `eclipse-temurin:21-jre`.
- Spring Boot 3.5: Spring MVC, Spring Security, Spring Data JPA y Thymeleaf.
- Jakarta Bean Validation.
- H2, una base de datos en memoria. La aplicación la llena con tres alumnos al arrancar.

## La página de inicio

La ruta `/` muestra los autores, la pila y la lista de ejemplos. Cada ejemplo tiene una línea de descripción y un enlace a cada ruta.

El botón "Empezar desde cero" envía un POST a `/empezar_de_cero`. Los datos de las pruebas vuelven al estado del arranque: los tres alumnos, ningún comentario y el email `contacto@ujaen.es` en cada ruta del ejemplo 4.

## Los ejemplos

| Ejemplo | Ruta insegura | Ruta protegida |
| --- | --- | --- |
| 1. Validación de datos | `/ejemplo1_inseguro` | `/ejemplo1_protegido` |
| 2. Inyección SQL | `/ejemplo2_inseguro` | `/ejemplo2_protegido` |
| 3. XSS | `/ejemplo3_inseguro` | `/ejemplo3_protegido` |
| 4. CSRF | `/ejemplo4_inseguro` | `/ejemplo4_protegido` |

**1. Validación de datos.** Un formulario da de alta un alumno con un nombre, un email y una nota. La ruta insegura guarda cualquier valor, como una nota de 99 o un email vacío. La ruta protegida usa `@Valid` con `@NotBlank`, `@Email`, `@Min` y `@Max`. Un valor fuera de las reglas no entra, y el error aparece junto a su campo.

**2. Inyección SQL.** Un formulario busca un alumno por su nombre. La ruta insegura concatena el texto en una consulta de `JdbcTemplate`, y el texto `' OR '1'='1` devuelve todos los alumnos. La ruta protegida usa un método de un repositorio de Spring Data JPA, con un parámetro enlazado. El mismo texto no devuelve ningún alumno.

**3. XSS.** Un libro de comentarios guarda el texto de cada visitante. Las dos rutas leen la misma lista. La ruta insegura muestra cada comentario con `th:utext`, y el comentario `<img src=x onerror=alert(1)>` ejecuta su código. La ruta protegida usa `th:text`, que escapa el HTML, y el mismo comentario aparece como texto.

**4. CSRF.** Un formulario cambia el email de contacto de la cuenta. La ruta insegura queda fuera de la protección CSRF de Spring Security, con `ignoringRequestMatchers`. La ruta protegida lleva el token oculto que Thymeleaf añade a cada formulario. Cada ruta guarda su propio email.

Cada ruta enlaza su propia página de ataque, `/ataque_csrf?ruta=inseguro` o `/ataque_csrf?ruta=protegido`. La página simula una web externa, y un solo botón envía el formulario de esa ruta sin el token. El ataque a la ruta insegura vuelve a la cuenta, con el email cambiado. El ataque a la ruta protegida recibe un 403. La página del 403 explica en español que la petición no lleva el token CSRF, y enlaza la cuenta, con el email intacto.

## Lanzar en local

El `Dockerfile` compila el proyecto con Maven en una primera etapa. El equipo solo necesita Docker.

```bash
cd 2.4
docker compose up --build
```

La aplicación responde en <http://localhost:8080/>.

## La imagen y el despliegue

- Docker Hub: <https://hub.docker.com/r/jfdg0002/asn-2-4>.
- Google Cloud: el servicio `asn-2-4` de Cloud Run, en la región `europe-west1`.

## Referencias

- Balsas, J.R. *Creación y ejecución de contenedores*. Universidad de Jaén, 2023.
- Spring Security Reference, *Cross Site Request Forgery (CSRF)*. <https://docs.spring.io/spring-security/reference/servlet/exploits/csrf.html>
- Thymeleaf, *Tutorial: Using Thymeleaf*, apartado *Unescaped Text*. <https://www.thymeleaf.org/doc/tutorials/3.1/usingthymeleaf.html>
- Jakarta Bean Validation 3.0. <https://jakarta.ee/specifications/bean-validation/3.0/>
- OWASP Cheat Sheet Series: *SQL Injection Prevention*, *Cross Site Scripting Prevention* y *Cross-Site Request Forgery Prevention*. <https://cheatsheetseries.owasp.org/>

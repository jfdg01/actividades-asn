package es.ujaen.asn;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class TomcatTest {

    @LocalServerPort
    int puerto;

    @Test
    void elRedirectTrasUnPostEsRelativoYConservaElHttpsDelProxy() throws Exception {
        var peticion = HttpRequest.newBuilder(URI.create("http://localhost:" + puerto + "/ejemplo4_inseguro"))
                .header("Content-Type", "application/x-www-form-urlencoded")
                .POST(HttpRequest.BodyPublishers.ofString("email=a@b.c"))
                .build();
        var respuesta = HttpClient.newHttpClient().send(peticion, HttpResponse.BodyHandlers.discarding());
        assertThat(respuesta.statusCode()).isEqualTo(302);
        assertThat(respuesta.headers().firstValue("Location")).hasValue("/ejemplo4_inseguro");
    }

    @Test
    void elAtaqueALaRutaProtegidaRecibeUn403EnEspanolQueEnlazaLaCuenta() throws Exception {
        var peticion = HttpRequest.newBuilder(URI.create("http://localhost:" + puerto + "/ejemplo4_protegido"))
                .header("Content-Type", "application/x-www-form-urlencoded")
                .POST(HttpRequest.BodyPublishers.ofString("email=atacante@malo.example"))
                .build();
        var respuesta = HttpClient.newHttpClient().send(peticion, HttpResponse.BodyHandlers.ofString());
        assertThat(respuesta.statusCode()).isEqualTo(403);
        assertThat(respuesta.body())
                .contains("no lleva el token CSRF")
                .contains("href=\"/ejemplo4_protegido\"");
    }
}

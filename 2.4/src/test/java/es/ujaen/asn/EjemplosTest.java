package es.ujaen.asn;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.not;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
class EjemplosTest {

    @Autowired
    MockMvc mvc;

    @Test
    void laPaginaDeInicioMuestraLosAutoresYEnlazaCadaRuta() throws Exception {
        var pagina = mvc.perform(get("/"))
                .andExpect(status().isOk())
                .andExpect(content().string(containsString("Javier Francisco Dibo Gómez")))
                .andExpect(content().string(containsString("Miguel Bolívar García")))
                .andExpect(content().string(containsString("Spring Boot 3.5")));
        for (int i = 1; i <= 4; i++) {
            pagina.andExpect(content().string(containsString("href=\"/ejemplo" + i + "_inseguro\"")))
                  .andExpect(content().string(containsString("href=\"/ejemplo" + i + "_protegido\"")));
        }
    }

    @Test
    void laRutaInseguraDelEjemplo1GuardaUnaNotaDe99YUnEmailVacio() throws Exception {
        mvc.perform(post("/ejemplo1_inseguro").with(csrf())
                        .param("nombre", "Intruso").param("email", "").param("nota", "99"))
                .andExpect(status().is3xxRedirection());
        mvc.perform(get("/ejemplo1_inseguro"))
                .andExpect(content().string(containsString("<td>Intruso</td>")))
                .andExpect(content().string(containsString("<td>99</td>")));
    }

    @Test
    void laRutaInseguraDelEjemplo1GuardaUnaNotaQueNoEsUnNumero() throws Exception {
        mvc.perform(post("/ejemplo1_inseguro").with(csrf())
                        .param("nombre", "SinNota").param("email", "x").param("nota", "abc"))
                .andExpect(status().is3xxRedirection());
        mvc.perform(get("/ejemplo1_inseguro"))
                .andExpect(content().string(containsString("<td>SinNota</td>")));
    }

    @Test
    void laRutaProtegidaDelEjemplo1RechazaLaNotaYElEmailJuntoASuCampo() throws Exception {
        mvc.perform(post("/ejemplo1_protegido").with(csrf())
                        .param("nombre", "Rechazado").param("email", "").param("nota", "99"))
                .andExpect(status().isOk())
                .andExpect(content().string(containsString("La nota va de 0 a 10")))
                .andExpect(content().string(containsString("El email es obligatorio")));
        mvc.perform(get("/ejemplo1_protegido"))
                .andExpect(content().string(not(containsString("<td>Rechazado</td>"))));
    }

    static final String INYECCION = "' OR '1'='1";

    @Test
    void laRutaInseguraDelEjemplo2DevuelveTodosLosAlumnosConLaInyeccion() throws Exception {
        mvc.perform(get("/ejemplo2_inseguro").param("nombre", INYECCION))
                .andExpect(status().isOk())
                .andExpect(content().string(containsString("<td>Ana</td>")))
                .andExpect(content().string(containsString("<td>Luis</td>")))
                .andExpect(content().string(containsString("<td>Marta</td>")));
    }

    @Test
    void laRutaProtegidaDelEjemplo2NoDevuelveNingunAlumnoConLaInyeccion() throws Exception {
        mvc.perform(get("/ejemplo2_protegido").param("nombre", INYECCION))
                .andExpect(status().isOk())
                .andExpect(content().string(not(containsString("<td>Ana</td>"))))
                .andExpect(content().string(not(containsString("<td>Luis</td>"))));
    }

    @Test
    void laRutaProtegidaDelEjemplo2EncuentraUnNombreReal() throws Exception {
        mvc.perform(get("/ejemplo2_protegido").param("nombre", "Ana"))
                .andExpect(content().string(containsString("<td>Ana</td>")))
                .andExpect(content().string(not(containsString("<td>Luis</td>"))));
    }

    static final String SCRIPT = "<img src=x onerror=alert(1)>";

    @Test
    void elEjemplo3MuestraElComentarioComoHtmlEnLaRutaInseguraYComoTextoEnLaProtegida() throws Exception {
        mvc.perform(post("/ejemplo3_inseguro").with(csrf()).param("texto", SCRIPT))
                .andExpect(status().is3xxRedirection());
        mvc.perform(get("/ejemplo3_inseguro"))
                .andExpect(content().string(containsString(SCRIPT)));
        mvc.perform(get("/ejemplo3_protegido"))
                .andExpect(content().string(containsString("&lt;img src=x onerror=alert(1)&gt;")))
                .andExpect(content().string(not(containsString(SCRIPT))));
    }

    @Test
    void laRutaInseguraDelEjemplo4AceptaElCambioSinToken() throws Exception {
        mvc.perform(post("/ejemplo4_inseguro").param("email", "atacante@malo.example"))
                .andExpect(status().is3xxRedirection());
        mvc.perform(get("/ejemplo4_inseguro"))
                .andExpect(content().string(containsString("atacante@malo.example")));
    }

    @Test
    void laRutaProtegidaDelEjemplo4RespondeCon403SinTokenYAceptaElCambioConToken() throws Exception {
        mvc.perform(post("/ejemplo4_protegido").param("email", "atacante@malo.example"))
                .andExpect(status().isForbidden());
        mvc.perform(post("/ejemplo4_protegido").with(csrf()).param("email", "nuevo@ujaen.es"))
                .andExpect(status().is3xxRedirection());
        mvc.perform(get("/ejemplo4_protegido"))
                .andExpect(content().string(containsString("nuevo@ujaen.es")))
                .andExpect(content().string(containsString("name=\"_csrf\"")));
    }

    @Test
    void cadaRutaDelEjemplo4EnlazaSuPropiaPaginaDeAtaque() throws Exception {
        mvc.perform(get("/ejemplo4_inseguro"))
                .andExpect(content().string(containsString("href=\"/ataque_csrf?ruta=inseguro\"")));
        mvc.perform(get("/ejemplo4_protegido"))
                .andExpect(content().string(containsString("href=\"/ataque_csrf?ruta=protegido\"")));
    }

    @Test
    void laPaginaDeAtaqueEnviaElFormularioDeSuRutaSinElToken() throws Exception {
        mvc.perform(get("/ataque_csrf").param("ruta", "inseguro"))
                .andExpect(status().isOk())
                .andExpect(content().string(containsString("action=\"/ejemplo4_inseguro\"")))
                .andExpect(content().string(not(containsString("/ejemplo4_protegido"))))
                .andExpect(content().string(not(containsString("_csrf\""))));
        mvc.perform(get("/ataque_csrf").param("ruta", "protegido"))
                .andExpect(content().string(containsString("action=\"/ejemplo4_protegido\"")))
                .andExpect(content().string(not(containsString("/ejemplo4_inseguro"))))
                .andExpect(content().string(not(containsString("_csrf\""))));
    }

    @Test
    void elBotonDeEmpezarDesdeCeroDevuelveLosCuatroEjemplosAlArranque() throws Exception {
        mvc.perform(get("/"))
                .andExpect(content().string(containsString("action=\"/empezar_de_cero\"")))
                .andExpect(content().string(containsString("name=\"_csrf\"")));
        mvc.perform(post("/ejemplo1_inseguro").with(csrf())
                .param("nombre", "Borrado").param("email", "").param("nota", "99"));
        mvc.perform(post("/ejemplo3_inseguro").with(csrf()).param("texto", "comentario borrado"));
        mvc.perform(post("/ejemplo4_inseguro").param("email", "atacante@malo.example"));

        mvc.perform(post("/empezar_de_cero").with(csrf()))
                .andExpect(status().is3xxRedirection());

        mvc.perform(get("/ejemplo1_inseguro"))
                .andExpect(content().string(not(containsString("<td>Borrado</td>"))))
                .andExpect(content().string(containsString("<td>Ana</td>")))
                .andExpect(content().string(containsString("<td>Marta</td>")));
        mvc.perform(get("/ejemplo3_inseguro"))
                .andExpect(content().string(not(containsString("comentario borrado"))));
        mvc.perform(get("/ejemplo4_inseguro"))
                .andExpect(content().string(containsString("contacto@ujaen.es")));
    }
}

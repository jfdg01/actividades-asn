package es.ujaen.asn;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.jdbc.core.BeanPropertyRowMapper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

@Controller
public class EjemplosController {

    private final AlumnoRepository alumnos;
    private final JdbcTemplate jdbc;
    private final List<String> comentarios = new CopyOnWriteArrayList<>();
    private final Map<String, String> emailDeContacto = new ConcurrentHashMap<>();

    EjemplosController(AlumnoRepository alumnos, JdbcTemplate jdbc) {
        this.alumnos = alumnos;
        this.jdbc = jdbc;
    }

    @GetMapping("/")
    String inicio() {
        return "index";
    }

    @EventListener(ApplicationReadyEvent.class)
    void datosIniciales() {
        alumnos.deleteAll();
        alumnos.saveAll(List.of(
                new Alumno("Ana", "ana@ujaen.es", 8),
                new Alumno("Luis", "luis@ujaen.es", 6),
                new Alumno("Marta", "marta@ujaen.es", 9)));
        comentarios.clear();
        emailDeContacto.put("/ejemplo4_inseguro", "contacto@ujaen.es");
        emailDeContacto.put("/ejemplo4_protegido", "contacto@ujaen.es");
    }

    @PostMapping("/empezar_de_cero")
    String empezarDeCero() {
        datosIniciales();
        return "redirect:/";
    }


    @GetMapping("/ejemplo1_inseguro")
    String ejemplo1Inseguro(Model model) {
        return ejemplo1(model, new Alumno(), false);
    }

    @PostMapping("/ejemplo1_inseguro")
    String altaInsegura(@ModelAttribute Alumno alumno, BindingResult ignorados) {
        alumnos.save(alumno);
        return "redirect:/ejemplo1_inseguro";
    }

    @GetMapping("/ejemplo1_protegido")
    String ejemplo1Protegido(Model model) {
        return ejemplo1(model, new Alumno(), true);
    }

    @PostMapping("/ejemplo1_protegido")
    String altaProtegida(@Valid @ModelAttribute Alumno alumno, BindingResult errores, Model model) {
        if (errores.hasErrors()) {
            return ejemplo1(model, alumno, true);
        }
        alumnos.save(alumno);
        return "redirect:/ejemplo1_protegido";
    }

    private String ejemplo1(Model model, Alumno alumno, boolean protegido) {
        model.addAttribute("alumno", alumno);
        model.addAttribute("alumnos", alumnos.findAll());
        model.addAttribute("protegido", protegido);
        return "ejemplo1";
    }


    @GetMapping("/ejemplo2_inseguro")
    String busquedaInsegura(@RequestParam(required = false) String nombre, Model model) {
        List<Alumno> encontrados = nombre == null ? List.of() : jdbc.query(
                "SELECT * FROM alumno WHERE nombre = '" + nombre + "'",
                new BeanPropertyRowMapper<>(Alumno.class));
        return ejemplo2(model, nombre, encontrados, false);
    }

    @GetMapping("/ejemplo2_protegido")
    String busquedaProtegida(@RequestParam(required = false) String nombre, Model model) {
        List<Alumno> encontrados = nombre == null ? List.of() : alumnos.findByNombre(nombre);
        return ejemplo2(model, nombre, encontrados, true);
    }

    private String ejemplo2(Model model, String nombre, List<Alumno> encontrados, boolean protegido) {
        model.addAttribute("nombre", nombre);
        model.addAttribute("encontrados", encontrados);
        model.addAttribute("protegido", protegido);
        return "ejemplo2";
    }


    @GetMapping("/ejemplo3_inseguro")
    String comentariosInseguros(Model model) {
        return ejemplo3(model, false);
    }

    @GetMapping("/ejemplo3_protegido")
    String comentariosProtegidos(Model model) {
        return ejemplo3(model, true);
    }

    @PostMapping({"/ejemplo3_inseguro", "/ejemplo3_protegido"})
    String comentar(@RequestParam String texto, HttpServletRequest peticion) {
        comentarios.add(texto);
        return "redirect:" + peticion.getRequestURI();
    }

    private String ejemplo3(Model model, boolean protegido) {
        model.addAttribute("comentarios", comentarios);
        model.addAttribute("protegido", protegido);
        return "ejemplo3";
    }


    @GetMapping({"/ejemplo4_inseguro", "/ejemplo4_protegido"})
    String cuenta(HttpServletRequest peticion, Model model) {
        String ruta = peticion.getRequestURI();
        model.addAttribute("ruta", ruta);
        model.addAttribute("email", emailDeContacto.get(ruta));
        model.addAttribute("protegido", ruta.equals("/ejemplo4_protegido"));
        return "ejemplo4";
    }

    @PostMapping({"/ejemplo4_inseguro", "/ejemplo4_protegido"})
    String cambiarEmail(@RequestParam String email, HttpServletRequest peticion) {
        emailDeContacto.put(peticion.getRequestURI(), email);
        return "redirect:" + peticion.getRequestURI();
    }

    @GetMapping("/ataque_csrf")
    String ataque(@RequestParam(defaultValue = "inseguro") String ruta, Model model) {
        model.addAttribute("destino", ruta.equals("protegido") ? "/ejemplo4_protegido" : "/ejemplo4_inseguro");
        return "ataque_csrf";
    }

    @RequestMapping("/csrf_rechazado")
    String csrfRechazado() {
        return "csrf_rechazado";
    }
}

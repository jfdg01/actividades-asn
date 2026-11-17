package es.ujaen.asn;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

@Entity
public class Alumno {

    @Id
    @GeneratedValue
    private Long id;

    @NotBlank(message = "El nombre es obligatorio")
    private String nombre;

    @NotBlank(message = "El email es obligatorio")
    @Email(message = "El email no tiene un formato válido")
    private String email;

    @NotNull(message = "La nota es obligatoria")
    @Min(value = 0, message = "La nota va de 0 a 10")
    @Max(value = 10, message = "La nota va de 0 a 10")
    private Integer nota;

    public Alumno() {
    }

    public Alumno(String nombre, String email, Integer nota) {
        this.nombre = nombre;
        this.email = email;
        this.nota = nota;
    }

    public Long getId() { return id; }
    public String getNombre() { return nombre; }
    public void setNombre(String nombre) { this.nombre = nombre; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public Integer getNota() { return nota; }
    public void setNota(Integer nota) { this.nota = nota; }
}

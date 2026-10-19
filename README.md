# TimeControl-XP

Sistema web multiusuario para la gestión de temporizadores, desarrollado a partir de un reloj ASCII y evolucionado hacia una aplicación frontend interactiva con HTML, CSS y JavaScript.

El proyecto busca transformar una idea inicial simple en una solución web funcional con autenticación simulada, roles, temporizadores concurrentes, historial de eventos y una interfaz para probar la experiencia de usuario en navegador.

## Objetivo

Desarrollar una aplicación web que permita a distintos usuarios crear y gestionar temporizadores de manera independiente.

Cada usuario podrá iniciar sesión, crear temporizadores, pausarlos, reanudarlos, detenerlos y consultar su historial de actividad. El sistema deberá soportar varios temporizadores simultáneos sin bloquear la experiencia del usuario.

## Estado actual del proyecto

Este repositorio se encuentra en una etapa de prototipo frontend funcional, con una interfaz web completa para:

- Login y registro simulados.
- Roles ADMIN y USER.
- Creación de temporizadores.
- Inicio, pausa, reanudación y finalización de temporizadores.
- Visualización de un reloj ASCII en tiempo real.
- Historial de eventos y acciones.
- Simulación de concurrencia con múltiples temporizadores activos.

## Tecnologías utilizadas

- HTML5
- CSS3
- JavaScript
- Tailwind CSS (para la interfaz)
- Reloj ASCII renderizado en navegador

## Requerimientos principales del proyecto

- Registro de usuarios.
- Inicio y cierre de sesión.
- Roles USER y ADMIN.
- Gestión de temporizadores.
- Historial de eventos.
- Persistencia de datos.
- API REST.
- Autorización por usuario y rol.
- Gestión de sesión.
- Procesamiento concurrente.
- Frontend funcional en navegador.
- Ejecución mediante Docker.
- Desarrollo aplicando Programación Extrema.

## Roles

### USER

Puede crear, iniciar, pausar, reanudar y finalizar sus propios temporizadores.

### ADMIN

Puede realizar todas las acciones de un usuario y además consultar usuarios y temporizadores del sistema.

## Concurrencia

El sistema contempla la ejecución simultánea de múltiples temporizadores sin que uno bloquee al resto.

En la versión actual, esta concurrencia se simula en el frontend mediante un ticker y lógica basada en tiempo real para varios temporizadores activos.

## Historias de usuario iniciales

### HU1
Como usuario quiero registrarme e iniciar sesión para acceder al sistema.

### HU2
Como usuario quiero crear un temporizador para controlar una actividad.

### HU3
Como usuario quiero iniciar, pausar y reanudar un temporizador.

### HU4
Como usuario quiero ejecutar varios temporizadores simultáneamente.

### HU5
Como usuario quiero consultar el historial de un temporizador.

### HU6
Como administrador quiero consultar los usuarios y temporizadores del sistema.

## Programación Extrema

Cada funcionalidad debería atravesar el ciclo:

RED -> GREEN -> REFACTOR

Se aplicarán historias de usuario, pruebas automatizadas, integración frecuente, revisión entre pares y refactorización continua.

## Próximos pasos

- Backend real en Python.
- API REST para persistencia y lógica del negocio.
- Base de datos.
- Autenticación y autorización reales.
- Gestión de sesiones.
- Concurrencia del lado servidor.
- Dockerización final.
- Integración frontend-backend.

## Integrantes

- Federico Montoro
- Uziel Gamarra

## Proyecto académico

Proyecto desarrollado aplicando conceptos de backend, concurrencia, arquitectura web, contenedores y Programación Extrema, con una primera versión en frontend para validar la experiencia de uso y la lógica de temporizadores.

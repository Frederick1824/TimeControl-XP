# TimeControl-XP

Sistema web multiusuario para la gestión de temporizadores, desarrollado a partir de un reloj ASCII en Python.

El proyecto busca evolucionar una idea inicial simple hacia una aplicación completa con autenticación, autorización, persistencia de datos, concurrencia, API REST, frontend, Docker y prácticas de Programación Extrema (XP).

## Objetivo

Desarrollar una aplicación que permita a distintos usuarios crear y gestionar temporizadores de forma independiente.

Cada usuario podrá iniciar sesión, crear temporizadores, pausarlos, reanudarlos, detenerlos y consultar su historial.

El sistema deberá permitir que varios temporizadores funcionen simultáneamente sin bloquearse entre sí.

## Requerimientos principales

- Registro de usuarios.
- Inicio y cierre de sesión.
- Roles USER y ADMIN.
- Gestión de temporizadores.
- Historial de eventos.
- Persistencia en base de datos.
- API REST.
- Autorización por usuario y rol.
- Gestión de sesión.
- Procesamiento concurrente o multihilo.
- Frontend para probar las funcionalidades.
- Ejecución mediante Docker.
- Desarrollo aplicando Programación Extrema.

## Roles

### USER

Puede crear, iniciar, pausar, reanudar y finalizar sus propios temporizadores.

### ADMIN

Puede realizar todas las acciones de un usuario y además consultar usuarios y temporizadores del sistema.

## Concurrencia

El sistema deberá permitir la ejecución simultánea de múltiples temporizadores sin que uno bloquee a los demás.

La implementación podrá utilizar herramientas de Python como:

- threading
- asyncio
- concurrent.futures

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

Cada funcionalidad deberá atravesar el ciclo:

RED -> GREEN -> REFACTOR

Se aplicarán historias de usuario, pruebas automatizadas, integración frecuente, revisión entre pares y refactorización continua.

## Estado actual

Actualmente existe un prototipo frontend funcional con:

- Login y registro simulado.
- Roles ADMIN y USER.
- Creación y control de temporizadores.
- Historial de eventos.
- Reloj ASCII.
- Simulación de múltiples temporizadores activos.

### Pendiente

- Backend real en Python.
- API REST.
- Persistencia en base de datos.
- Autenticación real.
- Gestión de sesión real.
- Autorización en backend.
- Concurrencia del lado servidor.
- Docker.
- Integración frontend-backend.

## Integrantes

- Federico Montoro
- Uziel

## Proyecto académico

Proyecto desarrollado aplicando conceptos de backend, concurrencia, arquitectura web, contenedores y Programación Extrema.

- Uziel Gamarra# TimeControl-XP

Sistema web multiusuario para la gesti�n de temporizadores, desarrollado a partir de un reloj ASCII en Python.

El proyecto busca evolucionar una idea inicial simple hacia una aplicaci�n completa con autenticaci�n, autorizaci�n, persistencia de datos, concurrencia, API REST, frontend, Docker y pr�cticas de Programaci�n Extrema (XP).

## Objetivo

Desarrollar una aplicaci�n que permita a distintos usuarios crear y gestionar temporizadores de forma independiente.

Cada usuario podr� iniciar sesi�n, crear temporizadores, pausarlos, reanudarlos, detenerlos y consultar su historial.

El sistema deber� permitir que varios temporizadores funcionen simult�neamente sin bloquearse entre s�.

## Requerimientos principales

- Registro de usuarios.
- Inicio y cierre de sesi�n.
- Roles USER y ADMIN.
- Gesti�n de temporizadores.
- Historial de eventos.
- Persistencia en base de datos.
- API REST.
- Autorizaci�n por usuario y rol.
- Gesti�n de sesi�n.
- Procesamiento concurrente o multihilo.
- Frontend para probar las funcionalidades.
- Ejecuci�n mediante Docker.
- Desarrollo aplicando Programaci�n Extrema.

## Roles

### USER

Puede crear, iniciar, pausar, reanudar y finalizar sus propios temporizadores.

### ADMIN

Puede realizar todas las acciones de un usuario y adem�s consultar usuarios y temporizadores del sistema.

## Concurrencia

El sistema deber� permitir la ejecuci�n simult�nea de m�ltiples temporizadores sin que uno bloquee a los dem�s.

La implementaci�n podr� utilizar herramientas de Python como:

- threading
- asyncio
- concurrent.futures

## Historias de usuario iniciales

### HU1
Como usuario quiero registrarme e iniciar sesi�n para acceder al sistema.

### HU2
Como usuario quiero crear un temporizador para controlar una actividad.

### HU3
Como usuario quiero iniciar, pausar y reanudar un temporizador.

### HU4
Como usuario quiero ejecutar varios temporizadores simult�neamente.

### HU5
Como usuario quiero consultar el historial de un temporizador.

### HU6
Como administrador quiero consultar los usuarios y temporizadores del sistema.

## Programaci�n Extrema

Cada funcionalidad deber� atravesar el ciclo:

RED -> GREEN -> REFACTOR

Se aplicar�n historias de usuario, pruebas automatizadas, integraci�n frecuente, revisi�n entre pares y refactorizaci�n continua.

## Estado actual

Actualmente existe un prototipo frontend funcional con:

- Login y registro simulado.
- Roles ADMIN y USER.
- Creaci�n y control de temporizadores.
- Historial de eventos.
- Reloj ASCII.
- Simulaci�n de m�ltiples temporizadores activos.

### Pendiente

- Backend real en Python.
- API REST.
- Persistencia en base de datos.
- Autenticaci�n real.
- Gesti�n de sesi�n real.
- Autorizaci�n en backend.
- Concurrencia del lado servidor.
- Docker.
- Integraci�n frontend-backend.

## Integrantes

- Federico Montoro
- Uziel Gamarra

## Proyecto acad�mico

Proyecto desarrollado aplicando conceptos de backend, concurrencia, arquitectura web, contenedores y Programaci�n Extrema.

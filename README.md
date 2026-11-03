# TimeControl-XP

Sistema web multiusuario para gestión de temporizadores, desarrollado a partir de un reloj ASCII en Python y evolucionado hacia una aplicación distribuida con frontend, API REST, autenticación, autorización, persistencia, concurrencia y Docker.

El proyecto se desarrolla aplicando Programación Extrema (XP) y parte del requerimiento de transformar el reloj ASCII original en una solución web multiusuario.

## Integrantes

- Federico Montoro
- Uziel Gamarra

## Objetivo

Permitir que distintos usuarios puedan registrarse, iniciar sesión y gestionar sus propios temporizadores.

Cada usuario puede crear relojes, pausarlos, reanudarlos, detenerlos, consultar su historial y visualizar el tiempo transcurrido mediante el reloj ASCII.

El rol ADMIN puede visualizar y gestionar todos los relojes del sistema.

## Arquitectura

El proyecto se divide en tres componentes:

```text
timecontrol/
├── auth-svc/       # autenticación, usuarios y JWT
├── clock-svc/      # temporizadores, autorización, persistencia e historial
├── web/            # frontend HTML/CSS/JavaScript
└── docker-compose.yml
```

### auth-svc

Backend FastAPI encargado de:

- registro de usuarios;
- login;
- persistencia de usuarios con SQLite;
- roles USER y ADMIN;
- generación de JWT con expiración;
- validación de credenciales.

### clock-svc

Backend FastAPI encargado de:

- crear temporizadores;
- listar relojes visibles para el usuario;
- pausar y reanudar;
- detener;
- eliminar;
- consultar historial;
- persistir relojes e historial en SQLite;
- validar JWT;
- verificar propiedad del recurso;
- permitir acceso global al rol ADMIN.

### web

Frontend servido mediante Nginx.

Incluye:

- login y registro;
- sesión mediante JWT almacenado en el navegador;
- reloj ASCII;
- creación de temporizadores;
- estados RUNNING, PAUSED y STOPPED;
- historial de eventos;
- controles según estado;
- visualización multiusuario.

## Requerimientos cubiertos

### Persistencia

Se utiliza SQLite:

- `auth-svc` persiste usuarios en `/data/users.db`;
- `clock-svc` persiste relojes e historial en `/data/clocks.db`.

Los volúmenes Docker conservan los datos aunque los contenedores sean recreados.

### Autenticación

El usuario se registra y luego inicia sesión en:

```http
POST /register
POST /login
```

El login devuelve un JWT firmado con expiración.

### Autorización

El `clock-svc` valida el JWT en cada endpoint protegido.

- USER puede acceder solamente a sus propios relojes.
- ADMIN puede acceder a todos los relojes.

La propiedad del recurso se verifica en el backend, evitando que un usuario modifique relojes ajenos cambiando un ID desde el navegador.

### Gestión de sesión

La sesión es stateless mediante JWT.

El frontend conserva el token mientras sea válido y elimina la sesión al cerrar sesión o detectar expiración.

### Concurrencia y procesamiento multihilo

Los temporizadores no dependen de un contador bloqueante.

Cada reloj almacena timestamps y calcula su tiempo transcurrido a partir del reloj del servidor.

El servicio utiliza FastAPI/Uvicorn para atender solicitudes concurrentes y un `ThreadPoolExecutor` para procesar múltiples relojes simultáneamente al listar resultados.

SQLite se configura con WAL y `busy_timeout` para mejorar el comportamiento ante accesos concurrentes.

## API REST

### Autenticación

```http
POST http://localhost:8001/register
POST http://localhost:8001/login
```

### Temporizadores

Todos los endpoints de relojes requieren:

```http
Authorization: Bearer <JWT>
```

Endpoints:

```http
POST   /clocks
GET    /clocks
GET    /clocks/{id}
POST   /clocks/{id}/pause
POST   /clocks/{id}/resume
POST   /clocks/{id}/stop
GET    /clocks/{id}/history
DELETE /clocks/{id}
```

## Estados del temporizador

```text
RUNNING
PAUSED
STOPPED
```

Un reloj nuevo comienza en RUNNING.

RUNNING puede pasar a PAUSED o STOPPED.

PAUSED puede pasar nuevamente a RUNNING mediante resume o finalizar en STOPPED.

## Historial

Cada reloj registra eventos como:

```text
CREATED
STARTED
PAUSED
RESUMED
STOPPED
DELETED
```

El historial registra también el usuario y la fecha/hora de la acción.

## Reloj ASCII

Las matrices originales del reloj en Python fueron adaptadas al frontend JavaScript.

El visor genera dinámicamente:

```text
HH:MM:SS
```

manteniendo la estética ASCII del proyecto original.

## Docker

Desde la carpeta `timecontrol`:

```bash
docker compose up --build
```

Servicios:

| Servicio | Puerto |
| --- | ---: |
| Frontend | 8000 |
| auth-svc | 8001 |
| clock-svc | 8002 |

Abrir:

```text
http://localhost:8000
```

## Usuario ADMIN de demostración

```text
usuario: admin
contraseña: admin123
```

Este usuario existe únicamente con fines académicos y de demostración.

## Programación Extrema

El desarrollo se organiza mediante historias de usuario y ciclos incrementales.

Ciclo utilizado:

```text
RED -> GREEN -> REFACTOR
```

Historias principales:

### HU1
Como usuario quiero registrarme e iniciar sesión para acceder al sistema.

### HU2
Como usuario quiero crear un temporizador para controlar una actividad.

### HU3
Como usuario quiero pausar, reanudar y detener un temporizador.

### HU4
Como usuario quiero ejecutar varios temporizadores sin que uno bloquee a los demás.

### HU5
Como usuario quiero consultar el historial de un temporizador.

### HU6
Como administrador quiero consultar y gestionar los relojes del sistema.

## Relación con el avance original de Uziel

El desarrollo conserva las ideas presentadas inicialmente por Uziel:

- integración de las matrices del reloj ASCII en JavaScript;
- funcionamiento de varios temporizadores a partir de timestamps;
- roles ADMIN y USER;
- historial de actividad;
- contenedores Docker;
- diseño incremental orientado a XP.

La implementación actual completa esos puntos llevando la autorización, persistencia, estados e historial también al backend.

## Prototipo inicial

El archivo `timecontrol_web_application.html` en la raíz se conserva como evidencia del prototipo frontend previo.

La aplicación integrada y dockerizada se encuentra en:

```text
timecontrol/web/index.html
```

## Proyecto académico

Proyecto desarrollado para aplicar persistencia, autenticación, autorización, gestión de sesión, concurrencia, API REST, contenedores y Programación Extrema.

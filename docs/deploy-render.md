# Deploy en Render

TimeControl XP se despliega con un Render Blueprint definido en `render.yaml`.

## Arquitectura

- `timecontrol-xp`: servicio web público con Nginx.
- `timecontrol-auth`: servicio privado FastAPI con SQLite persistente.
- `timecontrol-clock`: servicio privado FastAPI con SQLite persistente y WebSocket.

El frontend usa rutas relativas:

- `/auth` -> auth-svc
- `/clock` -> clock-svc
- `/ws` -> WebSocket de clock-svc

Nginx actúa como gateway y proxy reverso.

## Crear el deploy

1. Entrar a Render.
2. Elegir **New > Blueprint**.
3. Conectar el repositorio `Frederick1824/TimeControl-XP`.
4. Seleccionar la rama `integracion-requerimientos` mientras se valida el PR.
5. Confirmar que Render detecta `render.yaml`.
6. Crear el Blueprint.

Render crea automáticamente los tres servicios.

## Persistencia

Los servicios `timecontrol-auth` y `timecontrol-clock` usan discos persistentes montados en `/data`.

Esto conserva:

- `/data/users.db`
- `/data/clocks.db`

## WebSocket

El navegador se conecta a:

```text
wss://<dominio>/ws?token=<JWT>
```

Nginx actualiza la conexión HTTP a WebSocket y la reenvía a `clock-svc`.

## Verificación

Después del deploy:

1. Abrir la URL pública de `timecontrol-xp`.
2. Entrar como ADMIN.
3. Abrir una segunda ventana e iniciar sesión como USER.
4. Crear un reloj desde USER.
5. Verificar que ADMIN lo recibe sin presionar Sincronizar.
6. Pausar o detener desde USER.
7. Confirmar actualización en tiempo real en ADMIN.

## Nota sobre costos

El frontend puede utilizar el plan gratuito.

La configuración actual usa servicios privados con discos persistentes para cumplir el requisito de persistencia. Los discos persistentes requieren un plan compatible de Render.

# Correspondencia con el avance de Uziel

Este documento compara lo comunicado por Uziel con la implementación integrada en el repositorio.

| Avance comunicado | Estado en integración |
| --- | --- |
| Matrices ASCII de reloj.py integradas en JavaScript | Implementado |
| Renderizado del tiempo en tiempo real | Implementado |
| Múltiples temporizadores mediante timestamps | Implementado |
| Roles ADMIN y USER | Implementado |
| Autorización por rol | Implementado en backend |
| Historial de auditoría | Implementado y persistente |
| Docker / docker-compose | Implementado |
| Backend Python | Implementado con FastAPI |
| Persistencia | Usuarios, relojes e historial en SQLite |
| Pausar y reanudar | Implementado |
| Gestión de sesión | JWT con expiración |
| Concurrencia | FastAPI/Uvicorn + timestamps + ThreadPoolExecutor |
| XP | Historias de usuario y desarrollo incremental documentados |

## Diferencias encontradas antes de integrar

En el estado previo del repositorio:

- `clock-svc` mantenía los relojes solamente en memoria;
- los endpoints de relojes no validaban JWT;
- el owner llegaba desde el frontend y podía falsificarse;
- no existían pausa, reanudación ni stop;
- el historial no estaba implementado en el backend;
- Docker esperaba `requirements.txt`, pero el archivo se llamaba `requirements`;
- el README todavía describía el sistema como un prototipo frontend.

La rama `integracion-requerimientos` corrige estas diferencias sin cambiar la arquitectura general planteada por Uziel.

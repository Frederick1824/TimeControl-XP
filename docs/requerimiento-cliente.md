# Requerimiento del cliente

## Cliente

Federico Montoro

## Desarrollador

Uziel Gamarra

## Producto solicitado

Evolucionar el reloj ASCII original escrito en Python hacia una aplicación web multiusuario denominada **TimeControl**.

## Requerimientos funcionales

El sistema debe permitir:

1. Registrar usuarios.
2. Iniciar y cerrar sesión.
3. Diferenciar roles USER y ADMIN.
4. Crear temporizadores.
5. Iniciar temporizadores.
6. Pausar temporizadores.
7. Reanudar temporizadores.
8. Detener temporizadores.
9. Consultar relojes activos.
10. Consultar el historial de eventos.
11. Permitir que cada USER gestione solamente sus propios relojes.
12. Permitir que ADMIN consulte todos los relojes.
13. Mantener el reloj ASCII como parte visual de la aplicación.

## Requerimientos técnicos

El producto debe incluir:

- backend;
- persistencia;
- autenticación;
- autorización;
- gestión de sesión;
- API REST;
- procesamiento concurrente o multihilo;
- capacidad de manejar varios temporizadores simultáneamente;
- frontend para probar la API;
- ejecución mediante Docker;
- aplicación de Programación Extrema.

## Criterio de concurrencia

Un temporizador no debe bloquear la ejecución de otro.

El cálculo del tiempo debe realizarse mediante timestamps y no mediante bucles bloqueantes independientes.

El backend debe poder atender múltiples solicitudes y procesar múltiples relojes concurrentemente.

## Criterio de autorización

Un usuario USER no puede acceder, modificar ni eliminar relojes pertenecientes a otro usuario.

El rol ADMIN tiene acceso global.

La autorización debe realizarse en el backend y no depender únicamente de controles del frontend.

## Criterio de persistencia

Los usuarios, relojes e historial deben sobrevivir al reinicio de la aplicación.

## Criterio de aceptación

El proyecto se considera funcional cuando puede levantarse mediante Docker Compose y, desde el navegador:

1. registrar un usuario;
2. iniciar sesión;
3. crear varios relojes;
4. pausar y reanudar;
5. detener;
6. consultar historial;
7. comprobar aislamiento entre usuarios;
8. comprobar acceso global de ADMIN.

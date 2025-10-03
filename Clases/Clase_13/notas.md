Modelo OSI para evitar torre de babel digital

Capa 7 aplicación -> interfaz usuario

capa 6 presentación -> traduce los datos (cifrado, compresión, etc.)

capa 5 sesión -> gestiona sesiones entre dispositivos (simplex, half, full duplex)

capa 4 transporte -> garantiza comunicación de un extremo a otro, entrega confiable y ordenada de datos

capa 3 red -> enrutamiento, determina mejor ruta para los paquetes

capa 2 enlace -> ordena el flujo de bits y los organiza en unidades manejables (frames)

capa 1 física

Capa de transporte con modelo TCP/IP ofrece 2 protocolos muy distintos TCP (transmission control protocol) y UDP (user datagram protocol) 

tcp -> servicio de comunicación confiable y ordenado, maneja retransmisión de paqueter perdidos, reordenación de paquetes que llegan fuera de secuencia, descarta frames duplicados

UDP -> servicio minimo, agrega multiplexación de puertos a servicios básicos de IP, no es limitación, sino característica, aplicaciones que toleran pérdida ocasional de datos que requieren baja latencia (juegos, streaming o consultas DNS)

telnet -> diseñado para que user se conecte a computadora de forma remota y la opere como si estuviese en frente

netcat (nc) -> simple, "descendiente" de telnet, crea conexión tcp a cualqueir host y puerto, puede funcionar como servidor TCP o UDP simple, con opción -l (listen) puede escuchar puerto y aceptar conexiones entrantes
nc -z -v hostname 20-80 -> verifica puertos abiertos de host especificado

RFC -> request for comments

cada rfc tiene encabezado que incluye el número de rfc, título, autor, fecha de publicación e info de estado de doc dentro de proceso de estándares

RFC 791 -> internet protocol, define protocolo IP (fundamental en comunicación en internet)

RFC 793 -> Transmission control protocol (TCP) 

RFC 2821 -> simple mail transfer protocol (SMTP)

RFC 2616 -> http/1.1 y web
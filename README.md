# SMBCTL

SMBCTL es una herramienta simple para administrar conexiones SMB y levantar servidores SMB utilizando Impacket.

## Características

### Cliente SMB

- Conectar a recursos SMB
- Desconectar recursos SMB
- Listar conexiones activas
- Ver estado del cliente
- Copiar archivos entre local y SMB
- Soporte Windows y Linux

### Servidor SMB

- Iniciar servidor SMB
- Detener servidor SMB
- Consultar estado
- Mostrar información de acceso
- Soporte para autenticación opcional
- Ejecución en background (Linux)

---

# Instalación

## Desarrollo

```bash
git clone https://github.com/kevinzl13/smbctl.git
```

```bash
uv sync
```

Ejecutar:

```bash
uv run smbctl --help
```

## Instalación global

```bash
uv tool install smbctl
```

Después podrás usar:

```bash
smbctl
```

desde cualquier terminal.

---

# Comandos Cliente

## Conectar a un share SMB

Sin autenticación:

```bash
smbctl connect -i 192.168.1.10
```

Con autenticación:

```bash
smbctl connect \
    -i 192.168.1.10 \
    -u usuario \
    -p password
```

Share personalizado:

```bash
smbctl connect \
    -i 192.168.1.10 \
    -s documentos
```

---

## Listar conexiones

```bash
smbctl list
```

Ejemplo:

```text
================ SMB CONNECTIONS ================

SERVER  : 192.168.1.10
SHARE   : smbFolder
CLIENT  : windows
TARGET  : Z:
AUTH    : True
--------------------------------------------------
```

---

## Estado del cliente

```bash
smbctl status
```

---

## Desconectar una conexión

Desconectar servidor específico:

```bash
smbctl disconnect -i 192.168.1.10
```

Desconectar todas:

```bash
smbctl disconnect
```

---

# Copiar Archivos

La sintaxis está inspirada en SCP.

---

## Local → SMB

Copiar archivo local al servidor:

```bash
smbctl copy archivo.txt \
    192.168.1.10:/smbFolder/archivo.txt
```

Copiar a un directorio remoto:

```bash
smbctl copy archivo.txt \
    192.168.1.10:/smbFolder/docs/
```

---

## SMB → Local

Copiar archivo remoto al directorio actual:

```bash
smbctl copy \
    192.168.1.10:/smbFolder/archivo.txt .
```

Copiar a una carpeta específica:

```bash
smbctl copy \
    192.168.1.10:/smbFolder/archivo.txt \
    ./downloads/
```

---

# Comandos Servidor

## Iniciar servidor SMB

Compartir directorio actual:

```bash
smbctl server start
```

Compartir directorio específico:

```bash
smbctl server start \
    -d /home/usuario/files
```

Share personalizado:

```bash
smbctl server start \
    -d /home/usuario/files \
    -s documentos
```

Con autenticación:

```bash
smbctl server start \
    -d /home/usuario/files \
    -u usuario \
    -p password
```

---

## Estado del servidor

```bash
smbctl server status
```

Ejemplo:

```text
=== SMB SERVER STATUS ===

PID      : 21344
Share    : smbFolder
Dir      : /home/usuario/files
Alive    : YES
Uptime   : 230s
```

---

## Información de acceso

```bash
smbctl server info
```

Ejemplo:

```text
smb://192.168.1.10/smbFolder
```

---

## Detener servidor

```bash
smbctl server stop
```

---

# Funcionamiento por Plataforma

## Windows

Las conexiones SMB se montan automáticamente usando:

```cmd
net use Z: \\IP\SHARE
```

Por defecto se utiliza:

```text
Z:
```

Al ejecutar:

```bash
smbctl disconnect
```

la unidad se desmonta automáticamente.

---

## Linux

Las conexiones SMB se montan automáticamente usando:

```bash
mount -t cifs
```

Por defecto:

```text
/mnt/smb
```

Puede personalizarse:

```bash
smbctl connect \
    -i 192.168.1.10 \
    -m /mnt/files
```

---

# Requisitos

## Cliente

Windows:

```text
net use
```

Linux:

```text
mount.cifs
```

---

## Servidor

Impacket:

```bash
pip install impacket
```

Verificar:

```bash
impacket-smbserver -h
```

---

# Ejemplo Completo

Servidor:

```bash
smbctl server start \
    -d /tmp/share \
    -u usuario \
    -p password
```

Cliente:

```bash
smbctl connect \
    -i 192.168.1.10 \
    -u usuario \
    -p password
```

Copiar archivo:

```bash
smbctl copy test.txt \
    192.168.1.10:/smbFolder/test.txt
```

Descargar archivo:

```bash
smbctl copy \
    192.168.1.10:/smbFolder/test.txt .
```

Desconectar:

```bash
smbctl disconnect
```

Detener servidor:

```bash
smbctl server stop
```

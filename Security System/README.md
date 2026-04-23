# Sistema de Seguridad con IA

Aplicación en Python para detectar cumplimiento de EPP usando un modelo YOLO y una cámara USB o stream ESP32-CAM.

## Archivos

- `security_system.py`: aplicación principal.

## Dependencias

- `opencv-python`
- `requests`
- `pandas`
- `ultralytics`
- `customtkinter`
- `pillow`

## Uso

1. Ejecutar `python security_system.py`
2. Detectar cámaras USB o ingresar la URL del stream ESP32-CAM
3. Configurar la IP del ESP32 para enviar comandos `/verde` o `/roja`

## Notas

- El modelo `yolov8n.pt` se descarga automáticamente si no está presente.
- Ajusta la lógica de detección según las clases de tu modelo entrenado.

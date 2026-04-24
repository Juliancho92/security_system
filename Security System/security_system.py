import os
import cv2
import requests
import threading
import pandas as pd
from datetime import datetime
from ultralytics import YOLO
import customtkinter as ctk
from PIL import Image

class SistemaSeguridad(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Control de EPP con IA - Conexión WiFi")
        self.geometry("1100x600")
        
        # Cargar modelo IA
        self.model = YOLO('yolov8n.pt') 
        self.running = False
        
        # --- UI ---
        self.sidebar = ctk.CTkFrame(self, width=250)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.sidebar, text="Fuente de video", font=("Arial", 16, "bold")).pack(pady=10)
        self.cam_optionmenu = ctk.CTkOptionMenu(self.sidebar, values=["Buscando cámaras..."], command=self.on_camera_select)
        self.cam_optionmenu.set("Buscando cámaras...")
        self.cam_optionmenu.pack(pady=5, padx=10)

        self.btn_scan = ctk.CTkButton(self.sidebar, text="Detectar cámaras USB", command=self.scan_cameras)
        self.btn_scan.pack(pady=5, padx=10)

        ctk.CTkLabel(self.sidebar, text="O ingresa IP/URL ESP32-CAM", font=("Arial", 12)).pack(pady=(20, 5))
        self.cam_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Ej: http://192.168.1.50:81/stream")
        self.cam_entry.pack(pady=5, padx=10)

        ctk.CTkLabel(self.sidebar, text="IP Alarma ESP32", font=("Arial", 16, "bold")).pack(pady=10)
        self.ip_esp = ctk.CTkEntry(self.sidebar, placeholder_text="Ej: 192.168.1.50")
        self.ip_esp.pack(pady=5, padx=10)

        self.btn_start = ctk.CTkButton(self.sidebar, text="ENCENDER SISTEMA", fg_color="green", command=self.toggle_system)
        self.btn_start.pack(pady=20, padx=10)

        self.selected_source_label = ctk.CTkLabel(self.sidebar, text="Fuente seleccionada: ninguna", font=("Arial", 12), text_color="gray")
        self.selected_source_label.pack(pady=(0, 10), padx=10)

        self.status_label = ctk.CTkLabel(self, text="SISTEMA APAGADO", font=("Arial", 24), text_color="gray")
        self.status_label.pack(pady=10)

        self.selected_camera = None
        self.current_source = None
        self.source_type = None
        self.scan_cameras()

        self.video_display = ctk.CTkLabel(self, text="")
        self.video_display.pack(expand=True)

    def enviar_comando_esp(self, estado):
        ip = self.ip_esp.get()
        if not ip: return
        try:
            endpoint = "/verde" if estado == "CUMPLE" else "/roja"
            requests.get(f"http://{ip}{endpoint}", timeout=0.5)
        except:
            pass # Evita que el programa se trabe si el ESP32 se desconecta

    def open_video_source(self, source):
        if isinstance(source, int):
            cap = cv2.VideoCapture(source, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(source)
        return cap if (cap is not None and cap.isOpened()) else None

    def toggle_system(self):
        if not self.running:
            source_text = self.cam_entry.get().strip()
            if source_text:
                source = int(source_text) if source_text.isdigit() else source_text
            elif self.selected_camera is not None:
                source = self.selected_camera
            else:
                self.status_label.configure(text="Seleccione una cámara USB o ingrese la URL del stream", text_color="orange")
                return

            cap = self.open_video_source(source)
            if cap is None and isinstance(source, int):
                stream_url = self.cam_entry.get().strip()
                if stream_url and not stream_url.isdigit():
                    self.status_label.configure(text="USB no disponible, intentando stream ESP32...", text_color="orange")
                    cap = self.open_video_source(stream_url)
                    source = stream_url
                else:
                    self.status_label.configure(text="No se pudo abrir la cámara USB", text_color="red")
                    return

            if cap is None:
                self.status_label.configure(text="No se pudo abrir la fuente de video", text_color="red")
                return

            self.cap = cap
            self.current_source = source
            self.source_type = "USB" if isinstance(source, int) else "ESP32"
            if self.source_type == "USB":
                self.selected_source_label.configure(text=f"Fuente seleccionada: USB {source}", text_color="green")
            else:
                self.selected_source_label.configure(text=f"Fuente seleccionada: {source}", text_color="green")

            self.running = True
            self.btn_start.configure(text="APAGAR SISTEMA", fg_color="red")
            threading.Thread(target=self.process_loop, daemon=True).start()
        else:
            self.running = False
            self.btn_start.configure(text="ENCENDER SISTEMA", fg_color="green")
            if hasattr(self, 'cap') and self.cap.isOpened():
                self.cap.release()

    def scan_cameras(self):
        self.btn_scan.configure(state="disabled")
        camera_values = []
        detected = []
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]

        for index in range(6):
            opened = False
            for backend in backends:
                cap = cv2.VideoCapture(index, backend)
                if cap is not None and cap.isOpened():
                    ret, _ = cap.read()
                    cap.release()
                    if ret:
                        detected.append(index)
                        opened = True
                        break
                else:
                    if cap is not None:
                        cap.release()
            if opened:
                continue

        if detected:
            camera_values = [f"Cámara USB {i}" for i in detected]
            self.cam_optionmenu.configure(values=camera_values)
            self.cam_optionmenu.set(camera_values[0])
            self.selected_camera = detected[0]
            self.selected_source_label.configure(text=f"Fuente seleccionada: USB {detected[0]}", text_color="green")
            self.status_label.configure(text=f"Cámara detectada: USB {detected[0]}", text_color="green")
        else:
            self.cam_optionmenu.configure(values=["No se detectaron cámaras"])
            self.cam_optionmenu.set("No se detectaron cámaras")
            self.selected_camera = None
            self.selected_source_label.configure(text="Fuente seleccionada: ninguna", text_color="gray")
            self.status_label.configure(text="No se detectó cámara USB", text_color="gray")

        self.btn_scan.configure(state="normal")

    def on_camera_select(self, value):
        if value.startswith("Cámara USB "):
            try:
                self.selected_camera = int(value.split(" ")[2])
                self.selected_source_label.configure(text=f"Fuente seleccionada: USB {self.selected_camera}", text_color="green")
                self.status_label.configure(text=f"Seleccionada cámara USB {self.selected_camera}", text_color="gray")
            except ValueError:
                self.selected_camera = None
                self.selected_source_label.configure(text="Fuente seleccionada: ninguna", text_color="gray")
        else:
            self.selected_camera = None
            self.selected_source_label.configure(text="Fuente seleccionada: ninguna", text_color="gray")

    def process_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                if self.source_type == "USB":
                    stream_url = self.cam_entry.get().strip()
                    if stream_url and not stream_url.isdigit():
                        self.status_label.configure(text="USB no disponible, cambiando a stream ESP32...", text_color="orange")
                        if hasattr(self, 'cap') and self.cap.isOpened():
                            self.cap.release()
                        cap = self.open_video_source(stream_url)
                        if cap is not None:
                            self.cap = cap
                            self.current_source = stream_url
                            self.source_type = "ESP32"
                            self.selected_source_label.configure(text=f"Fuente seleccionada: {stream_url}", text_color="green")
                            continue
                self.status_label.configure(text="Se perdió la fuente de video", text_color="red")
                break

            results = self.model(frame, verbose=False)
            infraccion = False
            
            # Lógica: Si detecta 'person' pero NO detecta 'helmet' (ejemplo)
            # Nota: Debes ajustar esto según las clases de TU modelo entrenado
            for r in results:
                frame = r.plot() 
                for box in r.boxes:
                    cls_name = self.model.names[int(box.cls[0])]
                    if "no_" in cls_name.lower(): infraccion = True

            if infraccion:
                self.status_label.configure(text="● INFRACCIÓN DETECTADA", text_color="red")
                threading.Thread(target=self.enviar_comando_esp, args=("ROJA",)).start()
                self.log_to_excel("RECHAZADO")
            else:
                self.status_label.configure(text="● PERSONAL SEGURO", text_color="green")
                threading.Thread(target=self.enviar_comando_esp, args=("CUMPLE",)).start()

            # Renderizado en Interfaz
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=(640, 480))
            self.video_display.configure(image=img_ctk)

    def log_to_excel(self, status):
        # Solo guarda registros cuando el estado es RECHAZADO
        if status != "RECHAZADO":
            return

        try:
            excel_path = os.path.join(os.path.dirname(__file__), "registro_infracciones.xlsx")
            fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            nueva_fila = {"FechaHora": fecha_hora, "Estado": status}
            df_nuevo = pd.DataFrame([nueva_fila])

            if os.path.exists(excel_path):
                try:
                    df_existente = pd.read_excel(excel_path)
                    df = pd.concat([df_existente, df_nuevo], ignore_index=True)
                except Exception:
                    df = df_nuevo
            else:
                df = df_nuevo

            df.to_excel(excel_path, index=False)
        except Exception as e:
            print(f"Error guardando Excel: {e}")

if __name__ == "__main__":
    app = SistemaSeguridad()
    app.mainloop()

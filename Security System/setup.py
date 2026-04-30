from cx_Freeze import setup, Executable

setup(
    name="Security System",
    version="1.0",
    description="Sistema de seguridad con IA",
    executables=[Executable("security_system.py")],
    options={
        "build_exe": {
            "packages": ["ultralytics", "torch", "cv2", "customtkinter", "PIL"],
            "include_files": ["yolov8n.pt"]
        }
    }
)
import sys
import psutil

def get_system_telemetry():
    """Возвращает актуальные показатели нагрузки ПК."""
    cpu_percent = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory()
    disk_c = psutil.disk_usage("C:\\")

    return {
        "cpu_percent": cpu_percent,
        "ram_used_gb": round(ram.used / (1024**3), 2),
        "ram_total_gb": round(ram.total / (1024**3), 2),
        "ram_percent": ram.percent,
        "disk_free_gb": round(disk_c.free / (1024**3), 2),
        "disk_total_gb": round(disk_c.total / (1024**3), 2),
        "disk_percent": disk_c.percent
    }

if __name__ == "__main__":
    print("Telemetry test:", get_system_telemetry())

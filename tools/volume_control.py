from pycaw.pycaw import AudioUtilities

class VolumeController:
    """Управление системной громкостью Windows через современный pycaw."""

    def __init__(self):
        self._volume = None

    def _get_endpoint_volume(self):
        try:
            device = AudioUtilities.GetSpeakers()
            return device.EndpointVolume
        except Exception as e:
            print(f"[VolumeController] Ошибка получения аудиоустройства: {e}")
            return None

    def get_volume(self) -> int:
        """Возвращает текущую громкость в процентах (0-100)."""
        vol = self._get_endpoint_volume()
        if not vol:
            return 50
        try:
            current = vol.GetMasterVolumeLevelScalar()
            return int(round(current * 100))
        except Exception:
            return 50

    def set_volume(self, percent: int) -> str:
        """Устанавливает уровень громкости от 0 до 100%."""
        vol = self._get_endpoint_volume()
        if not vol:
            return "Не удалось настроить громкость."
        percent = max(0, min(100, percent))
        try:
            vol.SetMasterVolumeLevelScalar(percent / 100.0, None)
            return f"Громкость установлена на {percent}%."
        except Exception as e:
            return f"Ошибка изменения громкости: {e}"

    def change_volume(self, delta: int) -> str:
        """Изменяет громкость относительно текущей на delta %."""
        current = self.get_volume()
        new_val = max(0, min(100, current + delta))
        return self.set_volume(new_val)

    def set_mute(self, mute: bool) -> str:
        """Включает или выключает режим без звука (Mute)."""
        vol = self._get_endpoint_volume()
        if not vol:
            return "Не удалось изменить статус звука."
        try:
            vol.SetMute(1 if mute else 0, None)
            return "Звук заглушен, сэр." if mute else "Звук включен, сэр."
        except Exception as e:
            return f"Ошибка Mute: {e}"

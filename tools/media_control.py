import ctypes

# Windows Media Key Constants
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP       = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_VOLUME_MUTE      = 0xAD
VK_VOLUME_DOWN      = 0xAE
VK_VOLUME_UP        = 0xAF

def send_key_event(vk_code: int):
    """Посылает системное нажатие мультимедиа-клавиши."""
    KEYEVENTF_EXTENDEDKEY = 0x0001
    KEYEVENTF_KEYUP = 0x0002
    ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY, 0)
    ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)

def toggle_play_pause():
    send_key_event(VK_MEDIA_PLAY_PAUSE)
    return "Воспроизведение переключено."

def next_track():
    send_key_event(VK_MEDIA_NEXT_TRACK)
    return "Следующий трек."

def prev_track():
    send_key_event(VK_MEDIA_PREV_TRACK)
    return "Предыдущий трек."

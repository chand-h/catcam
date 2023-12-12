import threading

class SharedStateManager:
    def __init__(self):
        self._show_boxes = False
        self._show_text = True
        self._lock = threading.Lock()
        self._shutdown_requested = False

    def request_shutdown(self):
        self._shutdown_requested = True

    def should_shutdown(self):
        return self._shutdown_requested

    def toggle_show_boxes(self):
        with self._lock:
            self._show_boxes = not self._show_boxes

    def get_show_boxes(self):
        with self._lock:
            return self._show_boxes
        
    def toggle_show_text(self):
        with self._lock:
            self._show_text = not self._show_text

    def get_show_text(self):
        with self._lock:
            return self._show_text
        
shared_state = SharedStateManager()
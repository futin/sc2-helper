import queue
import subprocess
import threading


class SpeechQueue:
    def __init__(self) -> None:
        self._queue: queue.PriorityQueue = queue.PriorityQueue()
        self._counter = 0
        self._lock = threading.Lock()
        self._proc: subprocess.Popen | None = None
        self._proc_lock = threading.Lock()
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self) -> None:
        while True:
            _, _, message, voice = self._queue.get()
            cmd = ["say", "-v", voice, message] if voice else ["say", message]
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            with self._proc_lock:
                self._proc = proc
            proc.wait()
            with self._proc_lock:
                if self._proc is proc:
                    self._proc = None
            self._queue.task_done()

    def stop(self) -> None:
        with self._proc_lock:
            if self._proc is not None:
                self._proc.kill()
                self._proc = None

    def speak(self, message: str, voice: str = "", priority: int = 99) -> None:
        with self._lock:
            self._counter += 1
            counter = self._counter
        self._queue.put((priority, counter, message, voice))

from machine import Pin, PWM, Timer
import time

class Sound:
    def __init__(self, pin):
        """Inicializa el buzzer y las melodías."""
        self.buzzer = PWM(Pin(pin))
        self.buzzer.duty(0)  # Apagar el buzzer al inicio
        self.playing = False  # Control de reproducción
        self.timer = Timer(0)  # Temporizador para música de fondo

        # Notas musicales con frecuencias ajustadas
        FACTOR = 0.75  # Reducir la frecuencia en un 25% para bajar el tono
        self.NOTES = {
            "B4": int(494 * FACTOR), "B5": int(988 * FACTOR), "FS5": int(740 * FACTOR),
            "DS5": int(622 * FACTOR), "C5": int(523 * FACTOR), "C6": int(1047 * FACTOR),
            "G5": int(784 * FACTOR), "E5": int(659 * FACTOR), "F5": int(698 * FACTOR),
            "GS5": int(831 * FACTOR), "A5": int(880 * FACTOR), "AS5": int(932 * FACTOR),
            "AS4": int(466 * FACTOR), "F6": int(1397 * FACTOR), "REST": 0
        }

        # Melodía de inicio
        self.start_melody = [
            ("AS4", 8), ("AS4", 8), ("AS4", 8), ("F5", 2), ("C6", 2),
            ("AS5", 8), ("A5", 8), ("G5", 8), ("F6", 2), ("C6", 4)
        ]

        # Melodía de juego (Marcha Imperial)
        self.game_melody = [
            ("AS4", 8), ("AS4", 8), ("AS4", 8), ("F5", 2), ("C6", 2),
            ("AS5", 8), ("A5", 8), ("G5", 8), ("F6", 2), ("C6", 4),
            ("AS5", 8), ("A5", 8), ("G5", 8), ("F6", 2), ("C6", 4)
        ]

        # Melodía de muerte
        self.death_melody = [
            ("B4", 16), ("B5", 16), ("FS5", 16), ("DS5", 16),  
            ("B5", 32), ("FS5", -16), ("DS5", 8), ("C5", 16),
            ("C6", 16), ("G5", 16), ("E5", 16), ("C6", 32), ("G5", -16), ("E5", 8),
            ("B4", 16), ("B5", 16), ("FS5", 16), ("DS5", 16), ("B5", 32),  
            ("FS5", -16), ("DS5", 8), ("E5", 32), ("F5", 32), ("G5", 32),
            ("GS5", 32), ("A5", 16), ("B5", 8)
        ]

    def _play_melody(self, melody, tempo=105):
        """Reproduce una melodía sin detener el código principal."""
        wholenote = (60000 * 4) / tempo
        self.playing = True

        for note, duration in melody:
            if not self.playing:
                break  # Si se detiene el sonido, salir del bucle

            note_duration = (wholenote / abs(duration)) * 1.5 if duration < 0 else wholenote / duration
            freq = self.NOTES.get(note, 0)

            if freq > 0:
                self.buzzer.freq(freq)
                self.buzzer.duty(512)  # PWM al 50%
            else:
                self.buzzer.duty(0)

            time.sleep_ms(int(note_duration * 0.9))  # 90% de la duración
            self.buzzer.duty(0)
            time.sleep_ms(int(note_duration * 0.1))  # 10% de pausa entre notas

        self.buzzer.duty(0)  # Apagar el buzzer al finalizar

    def play_intro(self):
        """Reproduce la música del menú de inicio."""
        self.playing = True
        self._play_melody(self.start_melody, 108)

    def play_game_music(self):
        """Ejecuta la música del juego en un temporizador para que se repita automáticamente."""
        self.playing = True
        self.timer.init(period=1, mode=Timer.PERIODIC, callback=lambda t: self._play_melody(self.game_melody, 108))

    def play_death_melody(self):
        """Reproduce la melodía cuando el jugador muere."""
        self.playing = False  # Detener cualquier música en reproducción
        self._play_melody(self.death_melody, 105)  # Reproducir la melodía de muerte

    def stop_music(self):
        """Detiene cualquier música en reproducción."""
        self.playing = False
        self.timer.deinit()  # Detener el temporizador
        self.buzzer.duty(0)

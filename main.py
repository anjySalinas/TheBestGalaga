from machine import Pin, ADC, I2C
import ssd1306
import neopixel
import time
import random
from player import Player
from enemy import Enemy
from sound import Sound

# Configuración del OLED
i2c = I2C(0, scl=Pin(22), sda=Pin(23))  
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Configuración del joystick y botones
joy_x = ADC(Pin(32))
joy_x.atten(ADC.ATTN_11DB)
joy_y = ADC(Pin(35))
joy_y.atten(ADC.ATTN_11DB)
boton = Pin(33, Pin.IN, Pin.PULL_UP)  # Botón de disparo
boton2 = Pin(12, Pin.IN, Pin.PULL_UP)  # Botón para salir

# Configuración de NeoPixels (LEDs de vida)
num_pixels = 3  # Cantidad de LEDs = cantidad de vidas
neopixel_pin = 15  # Pin donde están los NeoPixels
np = neopixel.NeoPixel(Pin(neopixel_pin, Pin.OUT), num_pixels)

# Configuración del sonido
sound = Sound(18)

def update_neopixel_lives(lives):

    np.fill((0, 0, 0))  # 🔴 Apagar TODOS los LEDs antes de actualizar
    for i in range(min(lives, num_pixels)):  # 🔹 No exceder el número de LEDs disponibles
        np[i] = (255, 0, 0)  # 🔴 Enciende los LEDs según las vidas restantes
    
    np.write()  

def draw_menu():
    """Dibuja el menú principal."""
    oled.fill(0)
    oled.text("> Jugar", 30, 10)
    oled.show()

def main_menu():
    """Muestra el menú principal y espera la selección del jugador."""
    draw_menu()
    sound.play_intro()  # Reproduce la música de inicio
    update_neopixel_lives(3)  # ✅ Reiniciar LEDs antes de jugar

    while True:
        if boton2.value() == 0:  # Si se presiona el botón, iniciar el juego
            time.sleep(0.2)
            game_loop()
            break

def game_loop():
    """Bucle principal del juego."""
    player = Player(oled)  
    update_neopixel_lives(player.lives)  # ⚡ Inicializar LEDs con las vidas correctas

    enemies = []
    spawn_delay = 20  
    spawn_timer = 0

    oled.fill(0)
    oled.text("Jugando...", 30, 10)
    oled.show()
    time.sleep(1.5)

    while True:
        oled.fill(0)
        player.render()  # Renderiza el jugador y corazones en la OLED
        player.handle_bullets(enemies)

        # Control del joystick
        joy_x_value = joy_x.read()
        joy_y_value = joy_y.read()

        if joy_x_value > 2048:
            player.move_left()
        elif joy_x_value < 2048:
            player.move_right()

        if joy_y_value > 2048:
            player.move_up()
        elif joy_y_value < 2048:
            player.move_down()

        # Disparo del jugador
        if boton.value() == 0:
            player.shoot()

        # Generación de enemigos
        if spawn_timer >= spawn_delay:
            new_enemy = Enemy(oled, random.randint(10, 117))  
            enemies.append(new_enemy)
            spawn_timer = 0
        else:
            spawn_timer += 1

        # Movimiento y disparo de enemigos
        for enemy in enemies[:]:
            enemy.move()  
            enemy.shoot()
            enemy.handle_bullets()
            enemy.render_enemy()

            # Si el enemigo toca el suelo, se elimina
            if enemy.Y > 64:
                enemies.remove(enemy)

        # 🚨 Si el jugador recibe daño 🚨
        prev_lives = player.lives  # Guardamos el número de vidas antes de la colisión
        if player.check_collision(enemies):
            if player.lives != prev_lives:  # Solo actualizar si hubo cambio
                update_neopixel_lives(player.lives)  # 🔴 Actualizar LEDs de vida

            if player.lives <= 0:
                sound.stop_music()  # Detener la música del juego
                sound.play_death_melody()  # Reproducir la melodía de muerte
                
                oled.fill(0)
                oled.text("Game Over", 30, 30)
                oled.show()
                time.sleep(2)

                update_neopixel_lives(0)  # Apagar LEDs en "Game Over"
                main_menu()  # Regresar al menú principal
                break

        oled.show()

        # Salir del juego con el botón 2
        if boton2.value() == 0:
            oled.fill(0)
            oled.text("Saliendo...", 30, 10)
            oled.show()
            time.sleep(1.5)
            sound.stop_music()  # Detener la música
            update_neopixel_lives(0)  # 🔴 Apagar LEDs al salir
            main_menu()
            break

if __name__ == "__main__":
    main_menu()

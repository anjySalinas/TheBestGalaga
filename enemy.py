import framebuf
import random

class Bullet:
    def __init__(self, x, y):
        self.width = 1
        self.height = 3
        self.img = bytearray(b'\x80\x80\x80\x80\x80\x80')
        self.fb = framebuf.FrameBuffer(self.img, self.width, self.height, framebuf.MONO_HLSB)
        self.X = x
        self.Y = y

class Enemy:
    def __init__(self, oled, x):
        self.width = 11
        self.height = 8
        self.__img = bytearray(
            b' \x80\x1f\x00?\x80n\xc0\xff\xe0\xbf\xa0\xa0\xa0\x1b\x00')
        self.__fb = framebuf.FrameBuffer(self.__img, self.width, self.height, framebuf.MONO_HLSB)
        self.X = x
        self.Y = 10
        self.oled = oled
        self.speed = random.randint(1, 2)  # Velocidad aleatoria entre 1 y 2 píxeles
        self.bullets = []  # Disparos enemigos
        self.shoot_interval = random.randint(30, 60)
        self.shoot_timer = 0
        
        # Nueva lógica de movimiento
        self.moving_sideways = True  # Primero se moverán en X
        self.sideways_distance = random.randint(20, 50)  # Cuánto se moverán en X antes de bajar
        self.direction = random.choice([-1, 1])  # Izquierda o derecha
        self.sideways_moved = 0  # Cuánto se ha movido en X

    def move(self):
        if self.moving_sideways:
            # Mover en X antes de empezar a bajar
            self.X += self.direction * self.speed
            self.sideways_moved += abs(self.speed)
            
            # Evitar que se salga de la pantalla
            if self.X <= 0:  # Si llega al borde izquierdo, cambia de dirección
                self.X = 0
                self.direction = 1
            elif self.X + self.width >= 128:  # Si llega al borde derecho, cambia de dirección
                self.X = 128 - self.width
                self.direction = -1
            
            # Si ya se movió suficiente en X, empieza a bajar
            if self.sideways_moved >= self.sideways_distance:
                self.moving_sideways = False  
        else:
            # Movimiento normal hacia abajo
            self.Y += self.speed  

    def is_enemy_got_hit(self, bullet):
        return bullet.Y <= self.Y + self.height and self.X <= bullet.X <= self.X + self.width

    def shoot(self):
        if self.shoot_timer >= self.shoot_interval:
            self.bullets.append(Bullet(self.X + self.width // 2, self.Y + self.height))
            self.shoot_timer = 0
        else:
            self.shoot_timer += 1

    def handle_bullets(self):
        for bullet in self.bullets[:]:
            bullet.Y += 2
            if bullet.Y > 64:
                self.bullets.remove(bullet)

    def render_enemy(self):
        self.oled.blit(self.__fb, self.X, self.Y)
        for bullet in self.bullets:
            self.oled.blit(bullet.fb, bullet.X, bullet.Y)

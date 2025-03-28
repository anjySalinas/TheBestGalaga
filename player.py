import framebuf
import time

class Bullet:
    def __init__(self, x, y):
        self.width = 1
        self.height = 3
        self.img = bytearray(b'\x80\x80\x80\x80\x80\x80')
        self.fb = framebuf.FrameBuffer(self.img, self.width, self.height, framebuf.MONO_HLSB)
        self.X = x
        self.Y = y

class Player:
    def __init__(self, oled):
        self.width = 9
        self.height = 10
        self.img = bytearray(
            b'\x08\x00\x1c\x00\x14\x00\x14\x00\x1c\x00>\x00\x7f\x00\xff\x80\xdd\x80\x08\x00')
        self.fb = framebuf.FrameBuffer(self.img, self.width, self.height, framebuf.MONO_HLSB)
        self.X = 59
        self.Y = 50
        self.oled = oled
        self.bullets = []
        self.score = 0
        self.lives = 3  
        self.last_shot_time = 0
        self.reload_time = 0.5  
        self.speed = 4  

        # Ícono de corazón (8x8 píxeles)
        self.heart_icon = bytearray([
            0b00110110,  
            0b01111111,  
            0b01111111,  
            0b01111111,  
            0b00111110,  
            0b00011100,  
            0b00001000,  
            0b00000000   
        ])
        self.heart_fb = framebuf.FrameBuffer(self.heart_icon, 8, 8, framebuf.MONO_HLSB)

    def move_left(self):
        if self.X > 0:
            self.X -= self.speed

    def move_right(self):
        if self.X < 128 - self.width:
            self.X += self.speed

    def move_up(self):
        if self.Y > 50:
            self.Y -= self.speed

    def move_down(self):
        if self.Y < 64 - self.height:
            self.Y += self.speed

    def shoot(self):
        current_time = time.time()
        if current_time - self.last_shot_time >= self.reload_time:
            left_cannon_x = self.X
            right_cannon_x = self.X + self.width - 1
            self.bullets.append(Bullet(left_cannon_x, self.Y))
            self.bullets.append(Bullet(right_cannon_x, self.Y))
            self.last_shot_time = current_time

    def handle_bullets(self, enemies):
        for bullet in self.bullets[:]:
            bullet.Y -= 2
            if bullet.Y < 0:
                if bullet in self.bullets:  # ✅ Verificar antes de eliminar
                    self.bullets.remove(bullet)
            
            for enemy in enemies[:]:
                if enemy.is_enemy_got_hit(bullet):
                    if bullet in self.bullets:  # ✅ Verificar antes de eliminar
                        self.bullets.remove(bullet)
                    if enemy in enemies:  # ✅ Verificar antes de eliminar
                        enemies.remove(enemy)
                    self.score += 10

    def check_collision(self, enemies):
        for enemy in enemies:
            # 🔹 Verificar si una bala enemiga golpea al jugador
            for bullet in enemy.bullets:
                if bullet.Y >= self.Y and self.X <= bullet.X <= self.X + self.width:
                    enemy.bullets.remove(bullet)
                    self.lives -= 1  
                    if self.lives <= 0:
                        return True  

            # 🔹 Verificar colisión directa con el enemigo (choque)
            if (
                self.X < enemy.X + enemy.width and
                self.X + self.width > enemy.X and
                self.Y < enemy.Y + enemy.height and
                self.Y + self.height > enemy.Y
            ):
                self.lives -= 1  
                if self.lives <= 0:
                    return True
                enemies.remove(enemy)  # Elimina el enemigo tras la colisión

        return False

    def render(self):
        self.oled.blit(self.fb, self.X, self.Y)
        for bullet in self.bullets:
            self.oled.blit(bullet.fb, bullet.X, bullet.Y)
        
        self.oled.text(f"Score: {self.score}", 0, 0)
        
        # Dibujar corazones en la esquina superior derecha
        for i in range(self.lives):
            self.oled.blit(self.heart_fb, 120 - (i * 10), 2)  


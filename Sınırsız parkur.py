import pygame
import sys
import random

# Pygame başlatma
pygame.init()

# Pencere boyutları
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Sonsuz Parkur Macerası")

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 50, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
SKY_BLUE = (135, 206, 250)
YELLOW = (255, 255, 0)

# FPS (frame per second)
clock = pygame.time.Clock()

# Karakter sınıfı
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))  # Karakterin boyutları
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (400, 500)
        
        self.change_x = 0
        self.change_y = 0
        
        self.on_ground = False
        self.score = 0

    def update(self):
        self.gravity()
        self.rect.x += self.change_x
        self.rect.y += self.change_y
        
        # Yere temas kontrolü ve platforma çıkış
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect) and self.rect.bottom <= platform.rect.top + 10:
                self.on_ground = True
                self.rect.bottom = platform.rect.top
                self.change_y = 0
                self.add_score()  # Platforma çıktıkça puan ekleyelim

        # Eğer karakter yere düşerse puan sıfırlansın
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            self.change_y = 0
            self.reset_score()

    def gravity(self):
        if not self.on_ground:
            self.change_y += 1  # Yer çekimi

    def move_left(self):
        self.change_x = -5  # Yavaş hareket için hızı düşürdük

    def move_right(self):
        self.change_x = 5   # Yavaş hareket için hızı düşürdük

    def stop(self):
        self.change_x = 0

    def jump(self):
        if self.on_ground:
            self.change_y = -15  # Zıplama gücü

    def add_score(self):
        self.score += 5  # Her blokla yukarı çıkarken puan ekleyelim

    def reset_score(self):
        self.score = 0  # Yere düştüğünde puanı sıfırlanacak

# Platform sınıfı
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.y -= 1  # Platformları yukarıya hareket ettiriyoruz
        if self.rect.bottom < 0:  # Platform ekranın üst kısmından çıktıysa, alttan yeniden başlasın
            self.rect.top = screen_height
            self.rect.x = random.randint(100, screen_width - 100)
            self.rect.width = random.randint(100, 200)

# Güneş sınıfı
class Sun(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (50, 50), 50)
        self.rect = self.image.get_rect()
        self.rect.x = screen_width - 150
        self.rect.y = 50

# Oyun döngüsü
def game_loop():
    global platforms, level, player
    player = Player()
    
    # Başlangıçta birkaç platform oluştur
    platform1 = Platform(100, 550, 200, 20)
    platform2 = Platform(300, 450, 200, 20)
    platform3 = Platform(500, 350, 200, 20)
    platform4 = Platform(700, 250, 200, 20)
    
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    
    platforms = pygame.sprite.Group()
    platforms.add(platform1, platform2, platform3, platform4)

    # Hareketli platformlar
    moving_platform1 = Platform(100, 100, 200, 20)
    moving_platform2 = Platform(400, 150, 200, 20)
    platforms.add(moving_platform1, moving_platform2)
    all_sprites.add(moving_platform1, moving_platform2)
    
    # Güneşi ekleyelim
    sun = Sun()
    all_sprites.add(sun)

    level = 1  # Başlangıç seviyemiz
    score = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.move_left()
                elif event.key == pygame.K_RIGHT:
                    player.move_right()
                elif event.key == pygame.K_SPACE:
                    player.jump()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    player.stop()

        # Arka planı (gökyüzü) beyaz renkte doldur
        screen.fill(SKY_BLUE)

        # Platformları yukarı hareket ettir
        for platform in platforms:
            platform.update()

        # Sonsuz bloklar ekleyelim
        if len(platforms) < 10:  # 10'dan fazla platform olmasın
            new_platform = Platform(random.randint(100, screen_width-100), screen_height, random.randint(100, 200), 20)
            platforms.add(new_platform)
            all_sprites.add(new_platform)

        # Eğer oyuncu düşerse, oyunu kaybetme durumu
        if player.rect.bottom > screen_height:
            player.reset_score()  # Puan sıfırlanacak

        # Seviye geçişi: Eğer platformlar yukarıya çıkarsa, oyuncu da aynı şekilde yukarıya çıksın
        if player.rect.top <= 100:  # Yüksekliğe ulaştığında seviye geçişi
            level_up()

        # Tüm sprite'ları güncelle
        all_sprites.update()

        # Tüm sprite'ları ekranda çiz
        all_sprites.draw(screen)

        # Puanı ekranda göster
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Puan: {player.score}", True, BLACK)
        level_text = font.render(f"Seviye: {level}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (screen_width - 200, 10))

        # Ekranı güncelle
        pygame.display.flip()

        # FPS ayarları
        clock.tick(60)

    pygame.quit()
    sys.exit()

def level_up():
    global level, platforms, player
    level += 1  # Seviye atlama
    show_level_complete_screen()  # Seviye tamamlanınca ekranda göster

    pygame.time.wait(1000)  # 1 saniye bekle
    reset_game()  # Yeni seviyeye başla

def show_level_complete_screen():
    font = pygame.font.Font(None, 72)
    text = font.render("Tebrikler!", True, BLACK)
    small_text = pygame.font.Font(None, 36).render(f"Seviyeyi Geçtiniz! Şu an {level}. seviyedesiniz", True, BLACK)
    screen.fill(SKY_BLUE)
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - text.get_height() // 2))
    screen.blit(small_text, (screen_width // 2 - small_text.get_width() // 2, screen_height // 2 + 50))
    pygame.display.flip()

    # 3 saniye bekle
    pygame.time.wait(3000)

    # Yeni bölümün başlangıcı: Yeşil bloklar silinsin
    platforms.empty()  # Mevcut bloklar siliniyor
    generate_new_platforms()  # Yeni seviyede bloklar ekleniyor

def reset_game():
    global platforms, player
    platforms.empty()  # Platformları sıfırla
    generate_new_platforms()  # Yeni platformlar ekle
    player.rect.bottom = screen_height  # Oyuncuyu en alta yerleştir

def generate_new_platforms():
    global platforms
    for i in range(5):  # Her seviyede 5 platform ekleyelim
        platform = Platform(random.randint(100, screen_width-100), screen_height, random.randint(100, 200), 20)
        platforms.add(platform)

# Oyun başlatma
if __name__ == "__main__":
    try:
        game_loop()
    except Exception as e:
        print(f"Bir hata oluştu: {e}")
        pygame.quit()
        sys.exit()

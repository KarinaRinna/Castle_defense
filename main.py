import pygame
import math
import random


pygame.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)


class Castle:
    """класс замок"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 100  #текущее здоровье
        self.max_health = 100  #максимальное здоровье
        self.width = 80
        self.height = 100
        
    def draw(self, screen):
        #Рисуем замок
        pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, self.height))
        #Рисуем башни
        pygame.draw.rect(screen, GRAY, (self.x - 20, self.y + 20, 20, 40))
        pygame.draw.rect(screen, GRAY, (self.x + 80, self.y + 20, 20, 40))
        #Полоска здоровья
        bar_width = 100
        bar_height = 10
        health_percentage = self.health / self.max_health #процент здоровья
        pygame.draw.rect(screen, RED, (self.x - 10, self.y - 20, bar_width, bar_height))   #Рисуем фон полоски здоровья
        pygame.draw.rect(screen, GREEN, (self.x - 10, self.y - 20, bar_width * health_percentage, bar_height))  #Рисуем текущий процент здоровья
        
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0
    
    
class Enemy:
    """"класс враг"""
    def __init__(self, path_points, enemy_type="basic"):
        self.path = path_points
        self.current_point = 0
        self.x, self.y = path_points[0]
        self.target_x, self.target_y = path_points[1]
        self.speed = 2
        self.health = 30
        self.max_health = 30
        self.size = 20
        self.damage = 10
        self.reward = 10
        
    # Типы врагов
        if enemy_type == "fast":
            self.speed = 3
            self.health = 20
            self.color = YELLOW
        elif enemy_type == "tank":
            self.speed = 1
            self.health = 60
            self.color = RED
        else:  # basic
            self.color = BLACK
            
    def move(self):
        # Движение к следующей точке пути
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < self.speed:
            # Достигли точки
            self.current_point += 1
            if self.current_point < len(self.path):
                self.x, self.y = self.target_x, self.target_y
                self.target_x, self.target_y = self.path[self.current_point]
        else:
            # Двигаемся к точке
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
            
    def draw(self, screen):
        # Рисуем врага
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        # Рисуем полоску здоровья
        bar_width = 30
        bar_height = 4
        health_percentage = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x - 15, self.y - 25, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (self.x - 15, self.y - 25, bar_width * health_percentage, bar_height))
        
    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0
    
    
class Tower:
    """Класс башни для защиты"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.range = 150
        self.damage = 15
        self.cooldown = 30  # Кадров между выстрелами
        self.current_cooldown = 0
        self.target = None
        
    def update(self, enemies):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
            
        # Поиск цели
        if self.target is None or self.target not in enemies:
            self.find_target(enemies)
            
        # Атака цели
        if self.target and self.current_cooldown == 0:
            distance = math.sqrt((self.x - self.target.x)**2 + (self.y - self.target.y)**2)
            if distance <= self.range:
                if self.target.take_damage(self.damage):
                    return self.target.reward  # Возвращаем награду за убийство
                self.current_cooldown = self.cooldown
            else:
                self.target = None
        return 0
            
    def find_target(self, enemies):
        closest_distance = float('inf')
        for enemy in enemies:
            distance = math.sqrt((self.x - enemy.x)**2 + (self.y - enemy.y)**2)
            if distance <= self.range and distance < closest_distance:
                closest_distance = distance
                self.target = enemy
                
    def draw(self, screen):
        # Рисуем башню
        pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), 15)
        # Рисуем радиус действия (полупрозрачный)
        surface = pygame.Surface((self.range*2, self.range*2), pygame.SRCALPHA)
        pygame.draw.circle(surface, (0, 0, 255, 50), (self.range, self.range), self.range)
        screen.blit(surface, (self.x - self.range, self.y - self.range))


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Оборона замка")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 36)
        
        # Игровые объекты
        self.castle = Castle(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 200)
        self.enemies = []
        self.towers = []
        self.wave = 1
        self.enemies_in_wave = 5
        self.enemies_spawned = 0
        self.spawn_timer = 0
        self.money = 200
        self.score = 0
        
        # Путь врагов
        self.path = [
            (50, 100),
            (200, 100),
            (200, 300),
            (400, 300),
            (400, 450),
            (600, 450),
            (600, 200),
            (self.castle.x + 40, self.castle.y + 50)
        ]
        
    def spawn_enemy(self):
        if self.enemies_spawned < self.enemies_in_wave:
            # Определяем тип врага
            if self.wave >= 3 and random.random() < 0.3:
                enemy_type = "tank"
            elif self.wave >= 2 and random.random() < 0.4:
                enemy_type = "fast"
            else:
                enemy_type = "basic"
                
            self.enemies.append(Enemy(self.path, enemy_type))
            self.enemies_spawned += 1
            
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    x, y = pygame.mouse.get_pos()
                    if self.money >= 100:  # Стоимость башни
                        self.towers.append(Tower(x, y))
                        self.money -= 100
                        
    def update(self):
        # Спавн врагов
        self.spawn_timer += 1
        if self.spawn_timer >= 60:  # Спавн каждую секунду
            self.spawn_enemy()
            self.spawn_timer = 0
            
        # Обновление врагов
        for enemy in self.enemies[:]:
            enemy.move()
            
            # Проверка достижения замка
            if len(enemy.path) - 1 <= enemy.current_point:
                if self.castle.take_damage(enemy.damage):
                    self.game_over()
                self.enemies.remove(enemy)
                
        # Обновление башен
        for tower in self.towers:
            reward = tower.update(self.enemies)
            if reward:
                self.money += reward
                self.score += reward
                
        # Удаление мертвых врагов
        self.enemies = [e for e in self.enemies if e.health > 0]
        
        # Проверка окончания волны
        if len(self.enemies) == 0 and self.enemies_spawned >= self.enemies_in_wave:
            self.next_wave()
            
    def next_wave(self):
        self.wave += 1
        self.enemies_in_wave = 5 + self.wave * 2
        self.enemies_spawned = 0
        self.money += 50  # Бонус за волну
        
    def game_over(self):
        self.running = False
        self.show_game_over()
        
    def draw(self):
        self.screen.fill(WHITE)
        
        # Рисуем путь
        for i in range(len(self.path) - 1):
            pygame.draw.line(self.screen, GRAY, self.path[i], self.path[i + 1], 5)
            
        # Рисуем объекты
        self.castle.draw(self.screen)
        
        for tower in self.towers:
            tower.draw(self.screen)
            
        for enemy in self.enemies:
            enemy.draw(self.screen)
            
        # Рисуем интерфейс
        self.draw_ui()
        
        pygame.display.flip()
        
    def draw_ui(self):
        # Текст с информацией
        wave_text = self.font.render(f"Волна: {self.wave}", True, BLACK)
        money_text = self.font.render(f"Деньги: {self.money}", True, BLACK)
        score_text = self.font.render(f"Счет: {self.score}", True, BLACK)
        enemies_text = self.font.render(f"Врагов: {len(self.enemies)}", True, BLACK)
        
        self.screen.blit(wave_text, (10, 10))
        self.screen.blit(money_text, (10, 50))
        self.screen.blit(score_text, (10, 90))
        self.screen.blit(enemies_text, (10, 130))
        
        # Инструкция
        instruction_font = pygame.font.Font(None, 24)
        instruction_text = instruction_font.render("Кликните для установки башни (100 монет)", True, BLACK)
        self.screen.blit(instruction_text, (10, SCREEN_HEIGHT - 30))
        
    def show_game_over(self):
        self.screen.fill(WHITE)
        game_over_text = self.font.render("ИГРА ОКОНЧЕНА!", True, RED)
        score_text = self.font.render(f"Ваш счет: {self.score}", True, BLACK)
        wave_text = self.font.render(f"Волна: {self.wave}", True, BLACK)
        
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        wave_rect = wave_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        
        self.screen.blit(game_over_text, text_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(wave_text, wave_rect)
        
        pygame.display.flip()
        pygame.time.wait(3000)
        
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()

# Запуск игры
if __name__ == "__main__":
    game = Game()
    game.run()

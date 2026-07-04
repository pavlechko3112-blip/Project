import math
import random
import sys

import pygame

pygame.init()

# =====================================================
# WINDOW
# =====================================================
WIDTH, HEIGHT = 960, 540
GROUND_Y = HEIGHT - 48
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel JoJo Fighters - Joseph Update")
clock = pygame.time.Clock()

# =====================================================
# COLORS
# =====================================================
BLACK = (18, 18, 24)
WHITE = (245, 245, 245)
GRAY = (70, 70, 78)
LIGHT_GRAY = (140, 140, 155)
RED = (255, 80, 80)
BLUE = (70, 110, 255)
YELLOW = (255, 220, 70)
PURPLE = (150, 90, 255)
SKY = (32, 34, 60)
FLOOR = (52, 46, 62)
GREEN = (90, 235, 150)
MINT = (180, 255, 220)
ORANGE = (255, 165, 70)
HAMON = (255, 225, 120)
BROWN = (120, 72, 40)

FONT = pygame.font.SysFont("Arial", 24)
SMALL_FONT = pygame.font.SysFont("Arial", 18)
BIG_FONT = pygame.font.SysFont("Arial", 52, bold=True)
HUGE_FONT = pygame.font.SysFont("Arial", 70, bold=True)


# =====================================================
# HELPERS
# =====================================================
def draw_text(surf, text, font, color, pos, center=False):
    img = font.render(text, True, color)
    rect = img.get_rect(center=pos) if center else img.get_rect(topleft=pos)
    surf.blit(img, rect)


def draw_bar(surf, x, y, w, h, value, max_value, color, label=""):
    pygame.draw.rect(surf, (28, 28, 35), (x, y, w, h), border_radius=8)
    fill = 0 if max_value <= 0 else max(0, min(w, int((value / max_value) * w)))
    if fill > 0:
        pygame.draw.rect(surf, color, (x, y, fill, h), border_radius=8)
    pygame.draw.rect(surf, WHITE, (x, y, w, h), 2, border_radius=8)
    if label:
        draw_text(surf, label, SMALL_FONT, WHITE, (x, y - 20))


def draw_cooldown_bar(surf, x, y, cooldown, max_cooldown, color, label):
    ready = cooldown <= 0
    draw_bar(surf, x, y, 150, 12, 0 if ready else cooldown, max_cooldown, color, label)
    state = "READY" if ready else f"{cooldown / FPS:.1f}s"
    draw_text(surf, state, SMALL_FONT, WHITE, (x + 160, y - 5))


def draw_background(surf):
    surf.fill(SKY)
    pygame.draw.circle(surf, (240, 240, 180), (760, 100), 42)

    for i in range(6):
        pygame.draw.rect(surf, (40 + i * 7, 36 + i * 5, 58 + i * 6), (0, 240 + i * 18, WIDTH, 18))

    for x in range(0, WIDTH, 64):
        h = 60 + (x // 64 % 4) * 16
        pygame.draw.rect(surf, (28, 24, 42), (x, GROUND_Y - h, 48, h))

    pygame.draw.rect(surf, FLOOR, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    for x in range(0, WIDTH, 40):
        pygame.draw.line(surf, (78, 70, 88), (x, GROUND_Y), (x + 20, HEIGHT), 2)


# =====================================================
# PROJECTILES / ZONES
# =====================================================
class Bullet(pygame.sprite.Sprite):
    def init(self, x, y, direction, owner, color, damage, speed, knockback, size=(18, 6), stun=10):
        super().init()
        self.owner = owner
        self.direction = direction
        self.speed = speed
        self.damage = damage
        self.knockback = knockback
        self.stun = stun
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(self.image, WHITE, (0, 0, size[0], size[1]), border_radius=max(2, size[1] // 2))
        pygame.draw.rect(self.image, color, (size[0] // 2, 0, size[0] // 2, size[1]), border_radius=max(2, size[1] // 2))
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()
class StopSign(pygame.sprite.Sprite):
    def init(self, x, y, direction, owner):
        super().init()
        self.owner = owner
        self.direction = direction
        self.speed = 9
        self.damage = 11
        self.knockback = 18
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.rect(self.image, RED, (2, 2, 22, 22), border_radius=4)
        pygame.draw.rect(self.image, WHITE, (2, 2, 22, 22), 2, border_radius=4)
        pygame.draw.rect(self.image, LIGHT_GRAY, (19, 16, 8, 12), border_radius=3)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()


class RainZone(pygame.sprite.Sprite):
    def init(self, x, y, owner):
        super().init()
        self.owner = owner
        self.width = 96
        self.height = 96
        self.timer = 3 * FPS
        self.damage = 1
        self.knockback = 3
        self.hit_cd = 0
        self.rect = pygame.Rect(x - self.width // 2, y - self.height // 2, self.width, self.height)

    def update(self):
        self.timer -= 1
        if self.hit_cd > 0:
            self.hit_cd -= 1
        if self.timer <= 0:
            self.kill()

    def draw(self, surf):
        alpha = 100 if self.timer > FPS else 55 + (self.timer % 10) * 5
        zone = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.ellipse(zone, (100, 255, 160, alpha), (0, 48, self.width, 42))
        pygame.draw.ellipse(zone, (180, 255, 220, alpha), (18, 0, 84, 44))

        for i in range(8):
            drop_x = 12 + i * 13
            drop_h = 28 + (i % 3) * 10
            pygame.draw.line(zone, (210, 255, 235, alpha + 40), (drop_x, 34), (drop_x - 4, 34 + drop_h), 2)

        surf.blit(zone, self.rect.topleft)


class HamonZone(pygame.sprite.Sprite):
    def init(self, x, owner, direction):
        super().init()
        self.owner = owner
        self.width = 92
        self.height = 54
        offset = 44 if direction > 0 else -44 - self.width
        self.rect = pygame.Rect(x + offset, GROUND_Y - self.height, self.width, self.height)
        self.timer = int(1.6 * FPS)
        self.damage = 2
        self.knockback = 7
        self.hit_cd = 0

    def update(self):
        self.timer -= 1
        if self.hit_cd > 0:
            self.hit_cd -= 1
        if self.timer <= 0:
            self.kill()

    def draw(self, surf):
        alpha = 120 if self.timer > 20 else 50 + self.timer * 3
        glow = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (255, 210, 90, alpha), (0, 10, self.width, self.height - 8))
        for i in range(5):
            px = 12 + i * 16
            pygame.draw.circle(glow, (255, 245, 170, alpha + 30), (px, 18 + (i % 2) * 8), 6)
        surf.blit(glow, self.rect.topleft)


# =====================================================
# FIGHTER
# =====================================================
class Fighter:
    def init(self, fighter_id, name, x, color, accent):
        self.fighter_id = fighter_id
        self.name = name
        self.color = color
        self.accent = accent
        self.rect = pygame.Rect(x, GROUND_Y - 44, 30, 44)
        self.vel_y = 0
        self.on_ground = True
        self.flip = False
        self.hitstun = 0
        self.hit_flash = 0
        self.walk_timer = 0
        self.attack_cd = 0
        self.shoot_cd = 0
        self.sign_cd = 0
        self.ts_cd = 0
        self.skill_cd = 0
        self.burst_shots_remaining = 0
        self.burst_fire_timer = 0
        self.burst_direction = 1
        self.configure_moveset()
        self.hp = self.max_hp
def configure_moveset(self):
        if self.fighter_id == "jotaro":
            self.max_hp = 100
            self.move_speed = 5
            self.attack_damage = 7
            self.attack_range = 34
            self.attack_cooldown_max = 20
            self.shoot_cooldown_max = 24
            self.skill_cooldown_max = 10 * FPS
            self.shoot_label = "Star Finger"
            self.skill_label = "Time Stop"
            self.style_text = "Rushdown / stop time"
        elif self.fighter_id == "jodio":
            self.max_hp = 88
            self.move_speed = 4
            self.attack_damage = 4
            self.attack_range = 28
            self.attack_cooldown_max = 18
            self.shoot_cooldown_max = 24
            self.skill_cooldown_max = 11 * FPS
            self.shoot_label = "Rain Shots"
            self.skill_label = "Rain Zone"
            self.style_text = "Passive zoner"
        elif self.fighter_id == "joseph":
            self.max_hp = 98
            self.move_speed = 5
            self.attack_damage = 6
            self.attack_range = 32
            self.attack_cooldown_max = 18
            self.shoot_cooldown_max = 42
            self.skill_cooldown_max = 10 * FPS
            self.shoot_label = "Your Next Line"
            self.skill_label = "Tommy Gun"
            self.style_text = "Hamon trickster"
        elif self.fighter_id == "dio":
            self.max_hp = 105
            self.move_speed = 4
            self.attack_damage = 7
            self.attack_range = 34
            self.attack_cooldown_max = 22
            self.shoot_cooldown_max = 110
            self.skill_cooldown_max = 10 * FPS
            self.shoot_label = "Stop Sign"
            self.skill_label = "Teleport"
            self.style_text = "Pressure / space control"
        else:
            self.max_hp = 112
            self.move_speed = 5
            self.attack_damage = 8
            self.attack_range = 36
            self.attack_cooldown_max = 18
            self.shoot_cooldown_max = 70
            self.skill_cooldown_max = 8 * FPS
            self.shoot_label = "Blade Feathers"
            self.skill_label = "Pounce"
            self.style_text = "Ultimate lifeform predator"

    def update(self):
        for attr in ("attack_cd", "shoot_cd", "sign_cd", "ts_cd", "skill_cd", "hitstun", "hit_flash", "burst_fire_timer"):
            if getattr(self, attr) > 0:
                setattr(self, attr, getattr(self, attr) - 1)

    def move(self, keys, left, right, jump):
        if self.hitstun > 0:
            return

        moving = False
        if keys[left]:
            self.rect.x -= self.move_speed
            self.flip = True
            moving = True
        if keys[right]:
            self.rect.x += self.move_speed
            self.flip = False
            moving = True
        if keys[jump] and self.on_ground:
            self.vel_y = -15
            self.on_ground = False

        self.walk_timer = self.walk_timer + 1 if moving else 0

    def apply_gravity(self):
        self.vel_y = min(self.vel_y + 1, 15)
        self.rect.y += self.vel_y
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y = 0
            self.on_ground = True
        self.rect.left = max(10, self.rect.left)
        self.rect.right = min(WIDTH - 10, self.rect.right)

    def face_target(self, target):
        self.flip = self.rect.centerx > target.rect.centerx

    def take_damage(self, amount, direction, knockback, stun=10):
        self.hp = max(0, self.hp - amount)
        self.rect.x += knockback * direction
        self.vel_y = -5
        self.hitstun = max(self.hitstun, stun)
        self.hit_flash = 8

    def attack(self, target):
        if self.attack_cd > 0 or self.hitstun > 0:
            return False

        self.attack_cd = self.attack_cooldown_max
        direction = -1 if self.flip else 1
        hitbox_x = self.rect.left - self.attack_range if self.flip else self.rect.right + 4
        hitbox = pygame.Rect(hitbox_x, self.rect.y + 6, self.attack_range, self.rect.height - 6)
if hitbox.colliderect(target.rect):
            knockback = 10 if self.fighter_id == "jodio" else 14
            if self.fighter_id == "joseph":
                knockback = 12
            target.take_damage(self.attack_damage, direction, knockback)
            return True
        return False

    def shoot(self, group):
        if self.shoot_cd > 0 or self.hitstun > 0:
            return

        direction = -1 if self.flip else 1
        x = self.rect.left if self.flip else self.rect.right

        if self.fighter_id == "jotaro":
            self.shoot_cd = self.shoot_cooldown_max
            group.add(Bullet(x, self.rect.centery, direction, self.fighter_id, BLUE, 8, 15, 13, (18, 6)))
        elif self.fighter_id == "jodio":
            self.shoot_cd = self.shoot_cooldown_max
            for y_offset in (-8, 8):
                group.add(Bullet(x, self.rect.centery + y_offset, direction, self.fighter_id, GREEN, 2, 10, 6, (12, 8)))
        elif self.fighter_id == "joseph":
            self.shoot_cd = self.shoot_cooldown_max
            group.add(Bullet(x, self.rect.centery, direction, self.fighter_id, HAMON, 0, 14, 0, (20, 12), stun=40))
        elif self.fighter_id == "kars":
            self.shoot_cd = self.shoot_cooldown_max
            group.add(Bullet(x, self.rect.centery - 6, direction, self.fighter_id, RED, 5, 13, 10, (20, 8), stun=12))
            group.add(Bullet(x, self.rect.centery + 6, direction, self.fighter_id, WHITE, 4, 12, 9, (16, 6), stun=10))

    def use_skill(self, time_state, bullets, zones, target):
        if self.skill_cd > 0 or self.hitstun > 0:
            return

        if self.fighter_id == "jotaro":
            activate_time_stop(time_state, self.fighter_id, self)
            if time_state["user"] == self.fighter_id:
                self.skill_cd = self.skill_cooldown_max
        elif self.fighter_id == "jodio":
            zone_x = max(120, min(WIDTH - 120, target.rect.centerx + random.randint(-10, 10)))
            zones.add(RainZone(zone_x, GROUND_Y - 58, self.fighter_id))
            self.skill_cd = self.skill_cooldown_max
        elif self.fighter_id == "joseph":
            self.burst_direction = -1 if self.flip else 1
            self.burst_shots_remaining = 5
            self.burst_fire_timer = 0
            self.skill_cd = self.skill_cooldown_max
        elif self.fighter_id == "kars":
            direction = -1 if self.flip else 1
            self.rect.x += 55 * direction
            self.rect.left = max(10, self.rect.left)
            self.rect.right = min(WIDTH - 10, self.rect.right)
            self.skill_cd = self.skill_cooldown_max

    def update_special_attacks(self, bullets):
        if self.fighter_id != "joseph":
            return
        if self.burst_shots_remaining <= 0 or self.burst_fire_timer > 0:
            return

        start_x = self.rect.right + 6 if self.burst_direction > 0 else self.rect.left - 6
        y_offset = random.randint(-8, 8)
        speed = random.randint(13, 16)
        bullets.add(Bullet(start_x, self.rect.centery + y_offset, self.burst_direction, self.fighter_id, ORANGE, 3, speed, 7, (18, 8), stun=8))
        self.burst_shots_remaining -= 1
        self.burst_fire_timer = 4

    def throw_sign(self, group):
        if self.sign_cd > 0 or self.hitstun > 0:
            return
        self.sign_cd = 110
        direction = -1 if self.flip else 1
        x = self.rect.left if self.flip else self.rect.right
        group.add(StopSign(x, self.rect.centery - 4, direction, self.fighter_id))

    def teleport_behind(self, target):
        if self.fighter_id != "dio" or self.skill_cd > 0 or self.hitstun > 0:
            return
        offset = -54 if target.flip else 54
        self.rect.centerx = max(40, min(WIDTH - 40, target.rect.centerx + offset))
        self.rect.bottom = GROUND_Y
        self.vel_y = 0
        self.skill_cd = self.skill_cooldown_max
        self.flip = self.rect.centerx > target.rect.centerx
def draw(self, surf):
        x, y = self.rect.x, self.rect.y
        body_color = WHITE if self.hit_flash > 0 and self.hit_flash % 2 == 0 else self.color
        accent_color = WHITE if self.hit_flash > 0 and self.hit_flash % 2 == 0 else self.accent

        pygame.draw.ellipse(surf, (0, 0, 0), (x + 2, GROUND_Y - 6, 28, 10))
        pygame.draw.rect(surf, (10, 10, 10), (x - 2, y - 2, 34, 48), border_radius=5)
        pygame.draw.rect(surf, (255, 220, 180), (x + 8, y, 14, 14), border_radius=4)

        if self.fighter_id == "jotaro":
            pygame.draw.rect(surf, (18, 18, 24), (x + 3, y - 7, 24, 9), border_radius=2)
            pygame.draw.rect(surf, (30, 30, 40), (x + 6, y - 1, 18, 4), border_radius=2)
            pygame.draw.rect(surf, YELLOW, (x + 16, y + 1, 3, 3))
        elif self.fighter_id == "jodio":
            pygame.draw.rect(surf, accent_color, (x + 4, y - 6, 20, 7), border_radius=2)
            pygame.draw.rect(surf, accent_color, (x + 22, y - 3, 5, 5), border_radius=2)
            pygame.draw.rect(surf, (30, 70, 40), (x + 6, y + 1, 15, 4), border_radius=2)
        elif self.fighter_id == "joseph":
            pygame.draw.rect(surf, BROWN, (x + 4, y - 5, 22, 6), border_radius=2)
            pygame.draw.rect(surf, accent_color, (x + 19, y + 1, 6, 4), border_radius=2)
            pygame.draw.rect(surf, HAMON, (x + 3, y + 2, 3, 12), border_radius=2)
        elif self.fighter_id == "kars":
            pygame.draw.rect(surf, (120, 20, 20), (x + 2, y - 6, 24, 8), border_radius=3)
            pygame.draw.rect(surf, WHITE, (x + 18, y - 3, 7, 4), border_radius=2)
            pygame.draw.rect(surf, (180, 40, 40), (x + 4, y + 1, 5, 10), border_radius=2)
        else:
            pygame.draw.rect(surf, accent_color, (x + 4, y - 7, 22, 7), border_radius=2)
            pygame.draw.rect(surf, accent_color, (x + 3, y, 5, 10), border_radius=2)
            pygame.draw.rect(surf, accent_color, (x + 22, y, 5, 10), border_radius=2)

        pygame.draw.rect(surf, body_color, (x + 4, y + 14, 22, 18), border_radius=4)
        pygame.draw.rect(surf, body_color, (x - 1, y + 16, 6, 14), border_radius=3)
        pygame.draw.rect(surf, body_color, (x + 25, y + 16, 6, 14), border_radius=3)

        leg_bob = 2 if (self.walk_timer // 6) % 2 == 0 else -2
        if self.walk_timer == 0:
            leg_bob = 0

        pygame.draw.rect(surf, body_color, (x + 6, y + 32, 7, 12 + leg_bob), border_radius=3)
        pygame.draw.rect(surf, body_color, (x + 17, y + 32, 7, 12 - leg_bob), border_radius=3)


# =====================================================
# MENU / VFX
# =====================================================
def draw_stand(surf, owner, is_jotaro):
    glow = (120, 80, 255, 80) if is_jotaro else (255, 220, 80, 80)
    body = PURPLE if is_jotaro else YELLOW
    float_y = int(math.sin(pygame.time.get_ticks() / 140) * 5)
    side = -52 if owner.flip else 18
    sx = owner.rect.x + side
    sy = owner.rect.y - 86 + float_y

    aura = pygame.Surface((110, 120), pygame.SRCALPHA)
    pygame.draw.ellipse(aura, glow, (10, 10, 90, 95))
    surf.blit(aura, (sx - 20, sy - 10))

    pygame.draw.rect(surf, body, (sx + 18, sy, 30, 30), border_radius=8)
    pygame.draw.rect(surf, WHITE, (sx + 25, sy + 10, 4, 4), border_radius=2)
    pygame.draw.rect(surf, WHITE, (sx + 37, sy + 10, 4, 4), border_radius=2)
    pygame.draw.rect(surf, body, (sx + 10, sy + 30, 46, 44), border_radius=8)
    pygame.draw.rect(surf, body, (sx - 4, sy + 34, 16, 10), border_radius=5)
    pygame.draw.rect(surf, body, (sx + 54, sy + 34, 16, 10), border_radius=5)
    pygame.draw.rect(surf, body, (sx + 18, sy + 72, 11, 26), border_radius=5)
    pygame.draw.rect(surf, body, (sx + 37, sy + 72, 11, 26), border_radius=5)
def draw_character_card(rect, name, color, subtitle, lines, hot, selected=False):
    fill = color if hot or selected else GRAY
    pygame.draw.rect(screen, fill, rect, border_radius=14)
    pygame.draw.rect(screen, WHITE, rect, 3, border_radius=14)
    draw_text(screen, name, BIG_FONT, WHITE, (rect.centerx, rect.y + 42), center=True)
    draw_text(screen, subtitle, SMALL_FONT, WHITE, (rect.centerx, rect.y + 84), center=True)
    for i, line in enumerate(lines):
        draw_text(screen, line, SMALL_FONT, WHITE, (rect.x + 18, rect.y + 118 + i * 24))


def menu():
    while True:
        mouse = pygame.mouse.get_pos()
        draw_background(screen)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 130))
        screen.blit(overlay, (0, 0))

        draw_text(screen, "PIXEL JOJO FIGHTERS", HUGE_FONT, WHITE, (WIDTH // 2, 70), center=True)
        draw_text(screen, "Choose your fighter", FONT, WHITE, (WIDTH // 2, 116), center=True)

        jotaro_rect = pygame.Rect(40, 165, 275, 240)
        jodio_rect = pygame.Rect(342, 165, 275, 240)
        joseph_rect = pygame.Rect(644, 165, 275, 240)

        draw_character_card(
            jotaro_rect,
            "1  JOTARO",
            BLUE,
            "Rushdown / time stop",
            ["Punch hits hard", "Fast straight projectile", "C = stop time for 3 sec"],
            jotaro_rect.collidepoint(mouse),
        )
        draw_character_card(
            jodio_rect,
            "2  JODIO",
            GREEN,
            "Passive zoner",
            ["Weaker melee", "X = rain shots", "C = damaging rain zone"],
            jodio_rect.collidepoint(mouse),
        )
        draw_character_card(
            joseph_rect,
            "3  JOSEPH",
            ORANGE,
            "Hamon trickster",
            ["Balanced melee", "X = your next line stun shot", "C = tommy gun burst"],
            joseph_rect.collidepoint(mouse),
        )

        draw_text(screen, "Move: Arrow Keys   Z: punch   X: ranged   C: special", FONT, WHITE, (150, 434))
        draw_text(screen, "R rematch   ESC menu", FONT, WHITE, (330, 468))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "jotaro"
                if event.key == pygame.K_2:
                    return "jodio"
                if event.key == pygame.K_3:
                    return "joseph"
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if jotaro_rect.collidepoint(mouse):
                    return "jotaro"
                if jodio_rect.collidepoint(mouse):
                    return "jodio"
                if joseph_rect.collidepoint(mouse):
                    return "joseph"

        pygame.display.flip()
        clock.tick(FPS)


# =====================================================
# GAME
# =====================================================
def activate_time_stop(state, user, fighter):
    if state["active"] or fighter.ts_cd > 0:
        return
    state["active"] = True
    state["user"] = user
    state["timer"] = 3 * FPS
    fighter.ts_cd = 10 * FPS


def fighter_frozen(state, fighter_id):
    return state["active"] and state["user"] != fighter_id


def update_projectiles(group, state):
    for projectile in list(group):
        if (not state["active"]) or projectile.owner == state["user"]:
            projectile.update()


def update_zones(zones):
    for zone in list(zones):
        zone.update()
def handle_projectile_hits(projectiles, player, dio):
    for projectile in list(projectiles):
        target = player if projectile.owner == "dio" else dio
        direction = 1 if projectile.direction > 0 else -1
        if projectile.rect.colliderect(target.rect):
            target.take_damage(projectile.damage, direction, projectile.knockback, stun=getattr(projectile, "stun", 10))
            projectile.kill()


def handle_zone_hits(zones, player, dio):
    for zone in list(zones):
        target = player if zone.owner == "dio" else dio
        direction = 1 if target.rect.centerx > zone.rect.centerx else -1
        if zone.hit_cd <= 0 and zone.rect.colliderect(target.rect):
            target.take_damage(zone.damage, direction, zone.knockback, stun=4)
            zone.hit_cd = 22 if zone.owner == "jodio" else 18


def run_dio_ai(dio, player, signs, time_state):
    if fighter_frozen(time_state, "dio"):
        return

    dio.face_target(player)
    dist = player.rect.centerx - dio.rect.centerx
    abs_dist = abs(dist)
    edge_dist = player.rect.left - dio.rect.right if dist > 0 else dio.rect.left - player.rect.right
    move_speed = 4 if dio.hp >= 35 else 5

    if dio.hitstun <= 0:
        if edge_dist > 8:
            dio.rect.x += move_speed if dist > 0 else -move_speed
            if dio.on_ground and abs_dist > 220 and random.randint(0, 80) == 1:
                dio.vel_y = -14
                dio.on_ground = False
        else:
            if dio.attack_cd <= 0:
                dio.attack(player)
            if edge_dist < -10 and random.randint(0, 70) == 1:
                dio.rect.x += -18 if dist > 0 else 18

        if abs_dist > 170 and dio.sign_cd <= 0 and random.randint(0, 80) == 1:
            dio.throw_sign(signs)

        if dio.skill_cd <= 0 and 90 < abs_dist < 230 and random.randint(0, 150) == 1:
            dio.teleport_behind(player)

        if dio.ts_cd <= 0 and dio.hp < 60 and random.randint(0, 420) == 1:
            activate_time_stop(time_state, "dio", dio)


def draw_ui(player, dio, time_state):
    player_color = player.color
    draw_bar(screen, 20, 20, 280, 22, player.hp, player.max_hp, player_color, player.name.upper())
    draw_bar(screen, WIDTH - 300, 20, 280, 22, dio.hp, dio.max_hp, YELLOW, "DIO")

    draw_cooldown_bar(screen, 20, 62, player.attack_cd, player.attack_cooldown_max, RED, "Punch")
    draw_cooldown_bar(screen, 20, 86, player.shoot_cd, player.shoot_cooldown_max, WHITE, player.shoot_label)
    draw_cooldown_bar(screen, 20, 110, player.skill_cd, player.skill_cooldown_max, player_color, player.skill_label)

    draw_text(screen, f"Style: {player.style_text}", SMALL_FONT, WHITE, (20, 138))
    draw_text(screen, "ESC menu   R restart", SMALL_FONT, WHITE, (20, 158))

    if time_state["active"]:
        tint = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        tint.fill((130, 130, 170, 45) if time_state["user"] == "jotaro" else (180, 160, 60, 45))
        screen.blit(tint, (0, 0))

        title = "STAR PLATINUM: THE WORLD!" if time_state["user"] == "jotaro" else "ZA WARUDO!"
        color = BLUE if time_state["user"] == "jotaro" else YELLOW
        draw_text(screen, title, BIG_FONT, color, (WIDTH // 2, 44), center=True)
        draw_bar(screen, WIDTH // 2 - 130, 78, 260, 16, time_state["timer"], 3 * FPS, color)


def create_player(choice):
    if choice == "jodio":
        return Fighter("jodio", "Jodio", 180, GREEN, MINT)
    if choice == "joseph":
        return Fighter("joseph", "Joseph", 180, ORANGE, HAMON)
    return Fighter("jotaro", "Jotaro", 180, BLUE, (190, 215, 255))


def create_match(player_choice):
    player = create_player(player_choice)
    dio = Fighter("dio", "Dio", 750, YELLOW, (255, 245, 120))
    bullets = pygame.sprite.Group()
    signs = pygame.sprite.Group()
    zones = pygame.sprite.Group()
    time_state = {"active": False, "user": None, "timer": 0}
    return player, dio, bullets, signs, zones, time_state
def game(player_choice):
    while True:
        player, dio, bullets, signs, zones, time_state = create_match(player_choice)
        winner = None

        while True:
            clock.tick(FPS)
            restart = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    if event.key == pygame.K_r:
                        restart = True

            if restart:
                break

            keys = pygame.key.get_pressed()

            if winner is None:
                player.update()
                dio.update()
                player.update_special_attacks(bullets)

                if time_state["active"]:
                    time_state["timer"] -= 1
                    if time_state["timer"] <= 0:
                        time_state["active"] = False
                        time_state["user"] = None
                        time_state["timer"] = 0

                if not fighter_frozen(time_state, player.fighter_id):
                    player.move(keys, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP)
                    player.face_target(dio)
                    if keys[pygame.K_z]:
                        player.attack(dio)
                    if keys[pygame.K_x]:
                        player.shoot(bullets)
                    if keys[pygame.K_c]:
                        player.use_skill(time_state, bullets, zones, dio)

                if not fighter_frozen(time_state, player.fighter_id) or player.on_ground is False:
                    player.apply_gravity()

                run_dio_ai(dio, player, signs, time_state)

                if not fighter_frozen(time_state, "dio") or dio.on_ground is False:
                    dio.apply_gravity()

                update_projectiles(bullets, time_state)
                update_projectiles(signs, time_state)
                update_zones(zones)

                handle_projectile_hits(bullets, player, dio)
                handle_projectile_hits(signs, player, dio)
                handle_zone_hits(zones, player, dio)

                if player.hp <= 0 or dio.hp <= 0:
                    winner = "DIO WINS" if player.hp <= 0 else f"{player.name.upper()} WINS"

            draw_background(screen)
            for zone in zones:
                zone.draw(screen)
            player.draw(screen)
            dio.draw(screen)
            bullets.draw(screen)
            signs.draw(screen)

            if time_state["active"]:
                owner = player if time_state["user"] == player.fighter_id else dio
                draw_stand(screen, owner, time_state["user"] == "jotaro")

            draw_ui(player, dio, time_state)

            if winner:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))
                draw_text(screen, winner, HUGE_FONT, WHITE, (WIDTH // 2, HEIGHT // 2 - 30), center=True)
                draw_text(screen, "Press R to rematch or ESC for menu", FONT, WHITE, (WIDTH // 2, HEIGHT // 2 + 34), center=True)

            pygame.display.flip()


# =====================================================
# MAIN
# =====================================================
while True:
    selected_fighter = menu()
    game(selected_fighter)



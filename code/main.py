import pygame
from settings import *
from sprites import *
from groups import AllSprites
from support import *
from timer import Timer
from random import randint


class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Platformer')
        self.clock = pygame.time.Clock()
        self.running = True

        # Groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # Load game
        self.load_assets()
        self.setup()

        # Timers
        self.bee_timer = Timer(100, func=self.create_bee, autostart=True, repeat=True)

    def create_bee(self):
        Bee(
            frames=self.bee_frames,
            pos=((self.level_width + WINDOW_WIDTH), (randint(0, self.level_height))),
            groups=(self.all_sprites, self.enemy_sprites),
            speed=randint(300, 500),
        )

    def create_bullet(self, pos, direction):
        x = pos[0] + direction * 34 if direction == 1 else pos[0] + direction * 34 - self.bullet_surf.get_width()
        Bullet(self.bullet_surf, (x, pos[1]), direction, (self.all_sprites, self.bullet_sprites))
        Fire(self.fire_surf, pos, self.all_sprites, self.player)
        self.audio['shoot'].play()

    def load_assets(self):
        # Absolute paths for graphics
        self.player_frames = import_folder(r'D:\Programming\Platform 4 finish\images\player')  # Updated path
        self.bullet_surf = import_image(r'D:\Programming\Platform 4 finish\images\gun', 'bullet')  # Updated path
        self.fire_surf = import_image(r'D:\Programming\Platform 4 finish\images\gun', 'fire')  # Updated path
        self.bee_frames = import_folder(r'D:\Programming\Platform 4 finish\images\enemies\bee')  # Updated path
        self.worm_frames = import_folder(r'D:\Programming\Platform 4 finish\images\enemies\worm')  # Updated path

        # Absolute path for sounds
        self.audio = audio_importer(r'D:\Programming\Platform 4 finish\audio')  # Updated path

    def setup(self):
        # Absolute path for map file
        tmx_map = load_pygame(r'D:\Programming\Platform 4 finish\data\maps\world.tmx')  # Updated path
        self.level_width = tmx_map.width * TILE_SIZE
        self.level_height = tmx_map.height * TILE_SIZE

        for x, y, image in tmx_map.get_layer_by_name('Main').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, (self.all_sprites, self.collision_sprites))

        for x, y, image in tmx_map.get_layer_by_name('Decoration').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)

        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player(
                    (obj.x, obj.y),
                    self.all_sprites,
                    self.collision_sprites,
                    self.player_frames,
                    self.create_bullet,
                )
            if obj.name == 'Worm':
                Worm(
                    self.worm_frames,
                    pygame.FRect(obj.x, obj.y, obj.width, obj.height),
                    (self.all_sprites, self.enemy_sprites),
                )

        # Uncomment to play background music
        # self.audio['music'].play(loops=-1)

    def collision(self):
        # Bullets -> enemies
        for bullet in self.bullet_sprites:
            sprite_collision = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
            if sprite_collision:
                self.audio['impact'].play()
                bullet.kill()
                for sprite in sprite_collision:
                    sprite.destroy()

        # Enemies -> player
        # if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
        #     self.running = False

    def run(self):
        while self.running:
            dt = self.clock.tick(FRAMERATE) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Update
            self.bee_timer.update()
            self.all_sprites.update(dt)
            self.collision()

            # Draw
            self.display_surface.fill(BG_COLOR)
            self.all_sprites.draw(self.player.rect.center)
            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()

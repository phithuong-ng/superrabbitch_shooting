import pygame
from settings import *
from sprites import *
from groups import AllSprites
from support import *
from timer import Timer
from random import randint
import mediapipe as mp
import cv2


class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Platformer with Mediapipe')
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

        # Mediapipe setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
        self.cap = cv2.VideoCapture(0)

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
        self.player_frames = import_folder(r'D:\Programming\Platform 4 finish\images\player')
        self.bullet_surf = import_image(r'D:\Programming\Platform 4 finish\images\gun', 'bullet')
        self.fire_surf = import_image(r'D:\Programming\Platform 4 finish\images\gun', 'fire')
        self.bee_frames = import_folder(r'D:\Programming\Platform 4 finish\images\enemies\bee')
        self.worm_frames = import_folder(r'D:\Programming\Platform 4 finish\images\enemies\worm')

        # Absolute path for sounds
        self.audio = audio_importer(r'D:\Programming\Platform 4 finish\audio')

    def setup(self):
        # Absolute path for map file
        tmx_map = load_pygame(r'D:\Programming\Platform 4 finish\data\maps\world.tmx')
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

    def collision(self):
        # Bullets -> enemies
        for bullet in self.bullet_sprites:
            sprite_collision = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
            if sprite_collision:
                self.audio['impact'].play()
                bullet.kill()
                for sprite in sprite_collision:
                    sprite.destroy()

    def process_hand_landmarks(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb_frame)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # Get landmark positions
                lm = hand_landmarks.landmark
                if lm[8].y < lm[7].y and lm[12].y < lm[11].y:  # Jump condition
                    self.player.jump()
                elif lm[4].y < lm[3].y:  # Move left
                    self.player.move_left()
                elif lm[20].y < lm[19].y:  # Move right
                    self.player.move_right()

        cv2.imshow('Hand Tracking', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.running = False

    def run(self):
        while self.running:
            dt = self.clock.tick(FRAMERATE) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Process hand landmarks for movement
            self.process_hand_landmarks()

            # Update
            self.bee_timer.update()
            self.all_sprites.update(dt)
            self.collision()

            # Draw
            self.display_surface.fill(BG_COLOR)
            self.all_sprites.draw(self.player.rect.center)
            pygame.display.update()

        pygame.quit()
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    game = Game()
    game.run()

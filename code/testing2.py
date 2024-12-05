
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
        self.paused = False 
        self.score = 0 
        self.start_time = 0 
        self.game_duration = 60  # Default duration 
        self.mode = None  # Game mode

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
        self.player_frames = import_folder(r'C:\Users\Swift3\Desktop\superrabbitch_shooting\images\player')  # Updated path 
        self.bullet_surf = import_image(r'C:\Users\Swift3\Desktop\superrabbitch_shooting\images\gun', 'bullet')  # Updated path 
        self.fire_surf = import_image(r'C:\Users\Swift3\Desktop\superrabbitch_shooting\images\gun', 'fire')  # Updated path 
        self.bee_frames = import_folder(r'C:\Users\Swift3\Desktop\superrabbitch_shooting\images\enemies\bee')  # Updated path 
        self.worm_frames = import_folder(r'C:\Users\Swift3\Desktop\superrabbitch_shooting\images\enemies\worm')  # Updated path 

        # Absolute path for sounds 
        self.audio = audio_importer(r'C:\Users\Swift3\Desktop\superrabbitch_shooting\audio')  # Updated path 

    def setup(self, map_name="world2.tmx"): 
        # Absolute path for map file 
        tmx_map = load_pygame(rf'C:\Users\Swift3\Desktop\superrabbitch_shooting\data\maps\{map_name}')  # Updated path 
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
                    pygame.Rect(obj.x, obj.y, obj.width, obj.height), 
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
                    if isinstance(sprite, Bee): 
                        self.score += 30  # Increase score for killing bee 
                    elif isinstance(sprite, Worm): 
                        self.score += 10  # Increase score for killing worm 

    def run(self): 
        self.show_menu()  # Show the menu before starting the game 
        while self.running: 
            dt = self.clock.tick(FRAMERATE) / 1000 

            for event in pygame.event.get(): 
                if event.type == pygame.QUIT: 
                    self.running = False 
                if event.type == pygame.KEYDOWN: 
                    if event.key == pygame.K_q:  # Quit game 
                        self.running = False 
                    if event.key == pygame.K_p:  # Pause game 
                        self.paused = not self.paused 

            if not self.paused: 
                # Update 
                self.bee_timer.update() 
                self.all_sprites.update(dt) 
                self.collision() 

                # Check for game duration or score
                if self.mode == 'Countdown':
                    elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000 
                    if elapsed_time >= self.game_duration: 
                        self.running = False 
                elif self.mode == 'Adventure' and self.score >= 500:
                    self.switch_to_world_tmx()  # Switch to world.tmx when score reaches 500 

                # Draw 
                self.display_surface.fill(BG_COLOR) 
                self.all_sprites.draw(self.player.rect.center) 

                # Display score and countdown 
                self.display_score() 
                if self.mode == 'Countdown': 
                    self.display_countdown(elapsed_time) 

            pygame.display.update() 

        # Show final score 
        self.show_final_score() 
        pygame.quit() 

    def display_score(self): 
        font = pygame.font.Font(None, 36) 
        score_surface = font.render(f'Score: {self.score}', True, (255, 255, 255)) 
        self.display_surface.blit(score_surface, (10, 10))  # Display score at the top-left corner 

    def display_countdown(self, elapsed_time): 
        remaining_time = max(0, self.game_duration - int(elapsed_time)) 
        font = pygame.font.Font(None, 36) 
        countdown_surface = font.render(f'Time: {remaining_time}', True, (255, 255, 255)) 
        self.display_surface.blit(countdown_surface, (WINDOW_WIDTH - 100, 10))  # Display countdown at the top-right corner 

    def show_final_score(self): 
        font = pygame.font.Font(None, 74) 
        final_score_surface = font.render(f'Final Score: {self.score}', True, (255, 255, 255)) 
        self.display_surface.fill((0, 0, 0))  # Fill the screen with black 
        self.display_surface.blit(final_score_surface, (WINDOW_WIDTH // 2 - final_score_surface.get_width() // 2, WINDOW_HEIGHT // 2)) 
        pygame.display.update() 
        pygame.time.delay(5000)  # Delay 5 seconds to show the final score 
        self.show_menu()  # Return to menu after showing the final score 

    def show_menu(self): 
        menu_active = True 
        selected_option = 0 
        game_options = ["Countdown", "Adventure", "Quit"]  # Game mode options

        while menu_active: 
            self.display_surface.fill((0, 0, 0)) 
            font = pygame.font.Font(None, 74) 

            # Display game mode options 
            for i, option in enumerate(game_options): 
                color = (255, 255, 255) if i == selected_option else (150, 150, 150) 
                text_surface = font.render(option, True, color) 
                self.display_surface.blit(text_surface, (WINDOW_WIDTH // 2 - text_surface.get_width() // 2, WINDOW_HEIGHT // 2 - 50 + i * 100)) 

            pygame.display.update() 

            for event in pygame.event.get(): 
                if event.type == pygame.QUIT: 
                    self.running = False 
                    menu_active = False 
                if event.type == pygame.KEYDOWN: 
                    if event.key == pygame.K_UP: 
                        selected_option = (selected_option - 1) % len(game_options) 
                    if event.key == pygame.K_DOWN: 
                        selected_option = (selected_option + 1) % len(game_options) 
                    if event.key == pygame.K_RETURN: 
                        if selected_option == 0:  # Countdown mode
                            self.mode = 'Countdown'
                            self.select_time()  # Select countdown time
                        if selected_option == 1:  # Adventure mode
                            self.mode = 'Adventure'
                            self.start_time = pygame.time.get_ticks()
                            self.run_game()  # Start the game immediately for Adventure mode
                        elif selected_option == 2:  # Quit game
                            pygame.quit()
                            exit()
                        menu_active = False

    def select_time(self):
        time_options = ["20s", "40s", "60s"]
        time_selected = 0
        time_menu_active = True

        while time_menu_active:
            self.display_surface.fill((0, 0, 0))
            font = pygame.font.Font(None, 74)

            # Display time selection options
            for i, time_option in enumerate(time_options):
                color = (255, 255, 255) if i == time_selected else (150, 150, 150)
                text_surface = font.render(time_option, True, color)
                self.display_surface.blit(text_surface, (WINDOW_WIDTH // 2 - text_surface.get_width() // 2, WINDOW_HEIGHT // 2 - 50 + i * 100))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    time_menu_active = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        time_selected = (time_selected - 1) % len(time_options)
                    if event.key == pygame.K_DOWN:
                        time_selected = (time_selected + 1) % len(time_options)
                    if event.key == pygame.K_RETURN:
                        self.game_duration = (time_selected + 1) * 20  # Set game duration based on selection
                        self.start_time = pygame.time.get_ticks()
                        self.run_game()  # Start the game immediately after selecting time
                        time_menu_active = False

    def run_game(self):
        self.running = True
        self.score = 0
        self.all_sprites.empty()  # Clear previous sprites
        self.setup()  # Setup the game again with default map "world2.tmx"

        while self.running:
            dt = self.clock.tick(FRAMERATE) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:  # Quit game
                        self.running = False
                    if event.key == pygame.K_p:  # Pause game
                        self.paused = not self.paused

            if not self.paused:
                # Update
                self.bee_timer.update()
                self.all_sprites.update(dt)
                self.collision()

                # Check for game duration or score
                if self.mode == 'Countdown':
                    elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
                    if elapsed_time >= self.game_duration:
                        self.running = False
                elif self.mode == 'Adventure' and self.score >= 500:
                    self.switch_to_world_tmx()  # Switch to world.tmx when score reaches 500

                # Draw
                self.display_surface.fill(BG_COLOR)
                self.all_sprites.draw(self.player.rect.center)

                # Display score and countdown
                self.display_score()
                if self.mode == 'Countdown':
                    self.display_countdown(elapsed_time)

            pygame.display.update()

        # Show final score
        self.show_final_score()
        pygame.quit()

    def switch_to_world_tmx(self):
        self.all_sprites.empty()  # Clear previous sprites
        self.collision_sprites.empty()
        self.bullet_sprites.empty()
        self.enemy_sprites.empty()
        self.setup("world.tmx")  # Load new map
        self.score = 0  # Reset score for the new map
        self.start_time = pygame.time.get_ticks()  # Reset start time
        self.bee_timer = Timer(100, func=self.create_bee, autostart=True, repeat=True)  # Reset bee timer

if __name__ == '__main__':
    game = Game()
    game.run()

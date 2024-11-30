"""
Optlympic
Throw the spear as long as possible!
"""

# 에셋 경로 C:\Users\4rest\anaconda3\envs\arcade_env\Lib\site-packages\arcade\resources

import arcade
import math
import random

# Constants
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Optlympic"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
SPEAR_SCALING = 1
TILE_SCALING = 0.5

GRAVITY = 0.3

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Our Scene Object
        self.scene = None

        # Separate variable that holds the player sprite
        self.player_sprite = None
        self.spear_sprite = None
        self.starting_point_sprite = None

        self.player_speed = 5
        self.spear_angle = 45
        self.angle_delta = 1
        self.spear_speed = 30
        self.is_moving = False
        self.is_adjust_angle = False
        self.is_throwing = False
        self.is_thrown = False
        self.is_game_over = False

        self.reset_button = None

        # Our physics engine
        self.physics_engine = None

        # A Camera that can be used for scrolling the screen
        self.camera = None

        # A Camera that can be used to draw GUI elements
        self.gui_camera = None

        # Keep track of the score
        self.distance_travelled = 0

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """
        Set up the game here. Call this function to restart the game.
        """
        # Set up the Camera
        self.camera = arcade.Camera(self.width, self.height)

        # Set up the GUI Camera
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Keep track of the score
        self.distance_travelled = 0

        # Initialize Scene
        self.scene = arcade.Scene()

        # Create the Sprite lists
        self.scene.add_sprite_list("Points", use_spatial_hash=True)
        self.scene.add_sprite_list("BackGround", use_spatial_hash=True)
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Spear")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)

        self.starting_point_sprite = arcade.Sprite(
            ":resources:images/items/flagGreen2.png", TILE_SCALING
        )
        self.starting_point_sprite.center_x = 500
        self.starting_point_sprite.center_y = 96
        self.scene.add_sprite("Points", self.starting_point_sprite)

        coordinate_list = [
            [100, 427],
            [350, 375],
            [600, 364],
            [870, 546],
            [1000, 597],
            [1300, 720],
            [1500, 369],
            [1780, 746],
            [2000, 743],
            [2200, 386],
            [2500, 545],
            [2900, 620],
            [3250, 453],
            [3600, 694],
            [4150, 656],
            [4600, 610],
        ]

        for coordinate in coordinate_list:
            # Add a crate on the ground
            wall = arcade.Sprite("image/cloud.png", 2)
            wall.position = coordinate
            self.scene.add_sprite("BackGround", wall)

        # Set up the player, specifically placing it at these coordinates.
        image_source = ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.scene.add_sprite("Player", self.player_sprite)

        self.spear_sprite = arcade.Sprite("image/spear.png", SPEAR_SCALING)
        self.spear_sprite.center_x = 64
        self.spear_sprite.center_y = 96
        self.scene.add_sprite("Spear", self.spear_sprite)

        # Create the ground
        # This shows using a loop to place multiple sprites horizontally
        for x in range(0, 5000, 64):
            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 32
            self.scene.add_sprite("Walls", wall)

        reset_button_image = "image/reset.png"  # 리셋 버튼에 사용할 이미지 경로
        self.reset_button = arcade.Sprite(reset_button_image, 0.15)
        self.reset_button.center_x = SCREEN_WIDTH / 2
        self.reset_button.center_y = SCREEN_HEIGHT / 2 - 50

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEngineSimple(self.spear_sprite, walls=None)

    def on_draw(self):
        """
        Render the screen.
        """
        # Clear the screen to the background color
        self.clear()

        # Activate our Camera
        self.camera.use()

        # Draw our Scene
        self.scene.draw()

        if self.is_game_over:
            # 리셋 버튼만 그리기
            self.reset_button.draw()

        # Activate the GUI camera before drawing GUI elements
        self.gui_camera.use()

        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Distance: {int(self.distance_travelled/100)} m"
        arcade.draw_text(
            score_text,
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 45,
            arcade.csscolor.BLACK,
            30,
            font_name="Kenney Pixel",
            anchor_x="center",
            bold=True,
        )

        if self.is_game_over:  # 게임 오버 상태일 때
            game_over_text = "GAME OVER"
            arcade.draw_text(
                game_over_text,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2,
                arcade.csscolor.RED,
                50,
                font_name="Kenney Pixel",
                anchor_x="center",
                bold=True,
            )

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
            self.camera.viewport_height / 2
        )

        # Don't let camera travel past 0
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    def center_camera_to_spear(self):
        screen_center_x = self.spear_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.spear_sprite.center_y - (self.camera.viewport_height / 2)

        # Don't let camera travel past 0
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        spear_centered = screen_center_x, screen_center_y

        self.camera.move_to(spear_centered)

    def on_update(self, delta_time):
        """
        업데이트
        """
        if self.is_game_over:  # 게임 오버 상태라면 업데이트를 멈춘다
            self.reset_button.center_x = self.camera.position.x+self.camera.viewport_width / 2  # 전체 화면의 가로 중앙
            self.reset_button.center_y = self.camera.position.y+self.camera.viewport_height / 2 - 50  # 화면 세로 중앙
            return

        # Position the camera
        if self.is_thrown:
            self.center_camera_to_spear()
        else:
            self.center_camera_to_player()

        # 플레이어 이동
        if self.is_moving:
            self.player_sprite.center_x += self.player_speed
            self.spear_sprite.center_x += self.player_speed
            if self.player_sprite.center_x > 500:
                self.is_game_over = True

        if self.is_adjust_angle:
            # 각도를 지속적으로 변경 (0~90도 사이에서 변화)
            self.spear_angle += self.angle_delta

            if self.spear_angle > 90:
                self.spear_angle = 90
                self.angle_delta = -1  # 각도가 90을 넘으면 감소하기 시작
            elif self.spear_angle < 0:
                self.spear_angle = 0
                self.angle_delta = 1

            self.spear_sprite.angle = self.spear_angle - 45

        # 창 던지기
        if self.is_throwing:
            # 창 던지기 구현: 속도와 각도를 반영
            self.spear_sprite.center_x += self.spear_speed * math.cos(
                math.radians(self.spear_angle)
            )
            self.spear_sprite.center_y += self.spear_speed * math.sin(
                math.radians(self.spear_angle)
            )
            self.spear_sprite.change_y -= GRAVITY

            self.spear_angle -= 1
            if self.spear_angle < -90:
                self.spear_angle = -90
            self.spear_sprite.angle = self.spear_angle - 45

            distance = self.spear_sprite.center_x - self.starting_point_sprite.center_x
            if distance < 0:
                distance = 0

            self.distance_travelled = distance

            if arcade.check_for_collision_with_list(
                self.spear_sprite, self.scene["Walls"]
            ):
                # 창이 바닥에 닿으면
                self.spear_sprite.change_y = 0  # Y 속도 0으로 설정
                self.is_throwing = False  # 던지기 멈춤
                self.is_game_over = True

        self.physics_engine.update()

    def on_key_press(self, key, modifiers):
        """키를 눌렀을 때 호출"""
        if key == arcade.key.RIGHT:
            pass
        elif key == arcade.key.SPACE:
            self.is_moving = False  # 플레이어 멈춤
            self.is_adjust_angle = True  # 각도 조정 시작

    def on_key_release(self, key, modifiers):
        """키를 떼었을 때 호출"""
        if key == arcade.key.RIGHT:
            self.is_moving = True  # 오른쪽으로 이동 시작
        elif key == arcade.key.SPACE:
            self.is_adjust_angle = False  # 각도 조정 멈춤
            self.is_throwing = True  # 창 던지기 시작
            self.is_thrown = True

    def on_mouse_press(self, x, y, button, modifiers):
        """마우스 클릭 이벤트 처리"""
        if self.is_game_over:
            # 리셋 버튼 클릭 여부 확인
            world_x, world_y = self.camera.position[0] + x, self.camera.position[1] + y
            print(self.reset_button.left, world_x, self.reset_button.right)
            if (
            self.reset_button.left < world_x < self.reset_button.right
            and self.reset_button.bottom < world_y < self.reset_button.top
            ):
                self.is_game_over = False
                self.reset_game()  # 게임 초기화

    def reset_game(self):
        """게임 상태 초기화"""
        # 상태 변수 초기화
        self.player_speed = 5
        self.spear_angle = 45
        self.angle_delta = 1
        self.spear_speed = 30
        self.is_moving = False
        self.is_adjust_angle = False
        self.is_throwing = False
        self.is_thrown = False
        self.is_game_over = False

        # 플레이어와 창 초기화
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.spear_sprite.center_x = 64
        self.spear_sprite.center_y = 96

        self.setup()  # 씬과 스프라이트 초기화


def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()

"""
Optlympic
Throw the spear as long as possible!
"""

# 에셋 경로 C:\Users\4rest\anaconda3\envs\arcade_env\Lib\site-packages\arcade\resources

import arcade
import math
import random
import os
import sys

def get_resource_path(relative_path):
    """ exe가 아닌 환경에서는 파일 경로를 찾고, exe 환경에서는 sys._MEIPASS 사용 """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

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

        # menu object
        self.menu_scene = None

        # sound
        self.shooting_sound = None
        self.falling_sound = None
        self.drop_sound = None
        self.gameover_sound = None
        self.upgrade_sound = None

        # Our Scene Object
        self.scene = None
        self.is_game_started = False
        self.is_showing_instructions = False
        self.start_button = None
        self.instructions_button = None
        self.back_button = None

        # Separate variable that holds the player sprite
        self.player_sprite = None
        self.spear_sprite = None
        self.starting_point_sprite = None

        self.player_speed = 5
        self.spear_angle = 45
        self.angle_delta = 1
        self.spear_speed = 20
        self.spear_weight = 1.2
        self.wind_speed = 0
        self.points = 5
        self.high_score = 0
        self.is_moving = False
        self.is_adjust_angle = False
        self.is_throwing = False
        self.is_thrown = False
        self.is_adjust_power = False
        self.power_delta = 0.5
        self.is_game_over = False
        self.angle_adjusted = False

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
        # Sound
        self.shooting_sound = arcade.load_sound(":resources:sounds/hurt4.wav")
        self.falling_sound = arcade.load_sound(":resources:sounds/lose4.wav")
        self.drop_sound = arcade.load_sound(":resources:sounds/hit3.wav")
        self.gameover_sound = arcade.load_sound(":resources:sounds/gameover3.wav")
        self.upgrade_sound = arcade.load_sound(":resources:sounds/upgrade1.wav")

        # Set up the Camera
        self.camera = arcade.Camera(self.width, self.height)

        # Set up the GUI Camera
        self.gui_camera = arcade.Camera(self.width, self.height)

        # Keep track of the score
        self.distance_travelled = 0

        # menu setup
        self.menu_scene = arcade.Scene()
        self.start_button = arcade.Sprite(
            ":resources:onscreen_controls/shaded_light/start.png", 1
        )
        self.start_button.center_x = SCREEN_WIDTH / 2
        self.start_button.center_y = SCREEN_HEIGHT / 2 + 50

        self.instructions_button = arcade.Sprite(get_resource_path("image/how.png"), 1)
        self.instructions_button.center_x = SCREEN_WIDTH / 2
        self.instructions_button.center_y = SCREEN_HEIGHT / 2 - 50

        self.menu_scene.add_sprite("Buttons", self.start_button)
        self.menu_scene.add_sprite("Buttons", self.instructions_button)

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
            wall = arcade.Sprite(get_resource_path("image/cloud.png"), 2)
            wall.position = coordinate
            self.scene.add_sprite("BackGround", wall)

        # Set up the player, specifically placing it at these coordinates.
        image_source = ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.scene.add_sprite("Player", self.player_sprite)

        self.spear_sprite = arcade.Sprite(get_resource_path("image/spear.png"), SPEAR_SCALING)
        self.spear_sprite.center_x = 64
        self.spear_sprite.center_y = 96
        self.scene.add_sprite("Spear", self.spear_sprite)

        # Create the ground
        # This shows using a loop to place multiple sprites horizontally
        for x in range(0, 9600, 64):
            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 32
            self.scene.add_sprite("Walls", wall)

        reset_button_image = get_resource_path("image/reset.png")  # 리셋 버튼에 사용할 이미지 경로
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

        if not self.is_game_started:
            # Display the main menu
            if self.is_showing_instructions:
                # Display instructions if necessary
                instructions_text = "게임 방법\n1. 총 5포인트를 플레이어의 스피드와 창의 무게에 분배합니다.\n(스피드는 p키 무게는 w키로 분배)\n2. 오른쪽 방향키를 한번 눌렀다 떼면 캐릭터가 오른쪽으로 달려갑니다.\n2. 스페이스바를 키다운 하여 창의 각도를 조절합니다.\n3. Power가 변하는 동안 스페이스바를 한번 더 누르면 창을 던집니다.\n4. 바람은 조절할 수 없습니다.\n\n S키를 누르면 게임이 시작합니다.\n 최고기록에 도전해보세요! "

                # 텍스트를 \n을 기준으로 분할
                instructions_lines = instructions_text.split("\n")

                # 각 줄을 화면에 출력
                y_position = SCREEN_HEIGHT / 2 + 100
                for line in instructions_lines:
                    arcade.draw_text(
                        line,
                        SCREEN_WIDTH / 2,
                        y_position,
                        arcade.csscolor.BLACK,
                        13,  # 폰트 크기
                        font_name="Malgun Gothic",
                        anchor_x="center",
                        anchor_y="center",
                    )
                    y_position -= 30
            else:
                self.menu_scene.draw()
        else:
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
            score_text = f"Distance: {self.distance_travelled/100:.2f} m"
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
            arcade.draw_text(
                f"World Record: {self.high_score/100:.2f} m",
                50,
                SCREEN_HEIGHT - 45,
                arcade.csscolor.RED,
                25,
                font_name="Kenney Pixel",
                bold=True,
            )

            arcade.draw_text(
                f"Wind: {self.wind_speed:.2f} m/s",
                SCREEN_WIDTH - 250,
                SCREEN_HEIGHT - 50,
                arcade.csscolor.BLACK,
                25,
                font_name="Kenney Pixel",
                bold=True,
            )
            arcade.draw_text(
                f"Player speed: {self.player_speed:} km/h",
                SCREEN_WIDTH - 250,
                SCREEN_HEIGHT - 80,
                arcade.csscolor.BLACK,
                25,
                font_name="Kenney Pixel",
                bold=True,
            )
            arcade.draw_text(
                f"Spear weight: {self.spear_weight:.1f} kg",
                SCREEN_WIDTH - 250,
                SCREEN_HEIGHT - 110,
                arcade.csscolor.BLACK,
                25,
                font_name="Kenney Pixel",
                bold=True,
            )
            arcade.draw_text(
                f"Upgrade Points: {self.points} p",
                SCREEN_WIDTH - 250,
                SCREEN_HEIGHT - 140,
                arcade.csscolor.YELLOW,
                25,
                font_name="Kenney Pixel",
                bold=True,
            )

            if self.is_adjust_power:
                arcade.draw_text(
                    f"Power: {self.spear_speed:.1f}",
                    self.player_sprite.center_x,
                    self.player_sprite.center_y + 100,
                    arcade.csscolor.BLACK,
                    25,
                    font_name="Kenney Pixel",
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
        if not self.is_game_started:
            # Wait for the game to start (button presses)
            pass

        if self.is_game_over:  # 게임 오버 상태라면 업데이트를 멈춘다
            self.reset_button.center_x = (
                self.camera.position.x + self.camera.viewport_width / 2
            )  # 전체 화면의 가로 중앙
            self.reset_button.center_y = (
                self.camera.position.y + self.camera.viewport_height / 2 - 50
            )  # 화면 세로 중앙
            if self.high_score < self.distance_travelled:
                self.high_score = self.distance_travelled
            return

        # wind change
        self.wind_speed += random.uniform(-0.3, 0.3)

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

        if self.is_adjust_power:
            self.spear_speed += self.power_delta

            if self.spear_speed > 30:
                self.spear_speed = 30
                self.power_delta = -0.5
            elif self.spear_speed < 0:
                self.spear_speed = 0
                self.power_delta = 0.5

        # 창 던지기
        if self.is_throwing:
            # 창 던지기 구현: 속도와 각도를 반영
            throwing_power = (self.player_speed + self.spear_speed) * (
                self.spear_weight * 1.5
            ) + self.wind_speed / self.spear_weight
            self.spear_sprite.center_x += throwing_power * math.cos(
                math.radians(self.spear_angle)
            )
            self.spear_sprite.center_y += throwing_power * math.sin(
                math.radians(self.spear_angle)
            )
            self.spear_sprite.change_y -= GRAVITY * self.spear_weight

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
                self.drop_sound.play()
                self.gameover_sound.play()

        self.physics_engine.update()

    def on_key_press(self, key, modifiers):
        """키를 눌렀을 때 호출"""
        if self.is_showing_instructions:
            if key == arcade.key.S:
                self.is_showing_instructions = False
                self.is_game_started = True

        if self.is_game_started:
            if key == arcade.key.RIGHT:
                pass
            elif not self.angle_adjusted and key == arcade.key.SPACE:
                self.is_moving = False  # 플레이어 멈춤
                self.is_adjust_angle = True  # 각도 조정 시작

            if self.points > 0:
                if key == arcade.key.P:
                    self.points -= 1
                    self.player_speed += 1
                    self.upgrade_sound.play()

                if key == arcade.key.W:
                    self.points -= 1
                    self.spear_weight += 0.1
                    self.upgrade_sound.play()

    def on_key_release(self, key, modifiers):
        """키를 떼었을 때 호출"""
        if key == arcade.key.RIGHT:
            self.is_moving = True  # 오른쪽으로 이동 시작
        elif key == arcade.key.SPACE:
            if not self.angle_adjusted and self.is_adjust_angle:
                self.is_adjust_angle = False  # 각도 조정 멈춤
                self.is_adjust_power = True
                self.angle_adjusted = True

            elif self.angle_adjusted and self.is_adjust_power:
                self.is_adjust_power = False
                self.is_throwing = True  # 창 던지기 시작
                self.is_thrown = True
                self.shooting_sound.play()
                self.falling_sound.play()

    def on_mouse_press(self, x, y, button, modifiers):
        """마우스 클릭 이벤트 처리"""
        if not self.is_game_started:
            # Check if the start button is clicked
            if (self.start_button.left < x < self.start_button.right) and (
                self.start_button.bottom < y < self.start_button.top
            ):
                self.is_game_started = True  # Start the game

            # Check if the instructions button is clicked
            if (
                self.instructions_button.left < x < self.instructions_button.right
            ) and (self.instructions_button.bottom < y < self.instructions_button.top):
                self.is_showing_instructions = True  # Show instructions

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
        self.points = 5
        self.spear_weight = 1.2
        self.wind_speed = 0
        self.is_moving = False
        self.is_adjust_angle = False
        self.is_throwing = False
        self.is_thrown = False
        self.is_game_over = False
        self.is_adjust_power = False
        self.angle_adjusted = False

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
import pyxel
import random
import json

# Color settings
COLOR_CODES = [8, 9, 11, 10, 13, 14]  # RED, BLUE, GREEN, YELLOW, PURPLE, ORANGE
COLOR_NAMES = ['RED', 'ORANGE', 'GREEN', 'YELLOW', 'GRAY', 'PINK']
COLOR_MAP = dict(zip(COLOR_CODES, COLOR_NAMES))

BUTTON_SIZE = 16

class App:
    def __init__(self):
        pyxel.init(160, 160, title="Color Guess Game")
        pyxel.load("assets2.pyxres")
        pyxel.mouse(True)

        # 音楽データ読み込み
        with open("music.json", "rt") as f:
            self.music = json.load(f)

        self.playing = False  # ← 追加
        self.play_music_on_startup()  # ← 追加

        self.result_sound_played = False
        self.play_result_music = False
        self.show_help = False
        self.result_music_timer = 0
        self.battle_num = 10
        self.mode = "title"
        self.reset_game()

        pyxel.run(self.update, self.draw)


    def play_music_on_startup(self):
        for ch, sfx in enumerate(self.music):
            pyxel.sound(ch).set(*sfx)
            pyxel.play(ch, ch, loop=True)
        self.playing = True

    def reset_game(self):
        self.answer = [random.choice(COLOR_CODES) for _ in range(4)]
        print("DEBUG Answer:", [COLOR_MAP[c] for c in self.answer])
        self.guess = []
        self.history = []
        self.cleared = False
        self.is_game_over = False
        self.result_sound_played = False  # ← これを追加！


    def update(self):
        if self.show_help:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.show_help = False
            return

        if self.mode == "title":
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.mode = "game"
                self.reset_game()

        elif self.mode == "game":
            self.update_game()

        elif self.mode == "result":

            # 「Back to Title」ボタン
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                mx, my = pyxel.mouse_x, pyxel.mouse_y
                if 59 <= mx <= 99 and 60 <= my <= 72:
                    self.mode = "title"
            # Reset button
            # if 59 <= mx <= 99 and 60 <= my <= 72:
            #     self.guess = []


    def update_game(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx, my = pyxel.mouse_x, pyxel.mouse_y

            # Color buttons
            for i, color in enumerate(COLOR_CODES):
                x, y = 10 + i * (BUTTON_SIZE + 4), 10
                if x <= mx <= x + BUTTON_SIZE and y <= my <= y + BUTTON_SIZE:
                    if len(self.guess) < 4:
                        self.guess.append(color)

            # Submit button
            if 10 <= mx <= 50 and 50 <= my <= 62:
                if len(self.guess) == 4:
                    self.check_answer()
                    self.guess = []

            # Reset button
            if 60 <= mx <= 100 and 50 <= my <= 62:
                self.guess = []

            # Help ボタン
            if 110 <= mx <= 150 and 50 <= my <= 62:
                self.show_help = True
                self.button_enabled = False

            # 音楽ミュートボタン
            if 140 <= mx <= 155 and 5 <= my <= 14:
                self.playing = not self.playing
                if self.playing:
                    for ch, sfx in enumerate(self.music):
                        pyxel.sound(ch).set(*sfx)
                        pyxel.play(ch, ch, loop=True)
                else:
                    pyxel.stop()

    def check_answer(self):
        guess = self.guess[:]
        temp_answer = self.answer[:]
        hit = 0
        blow = 0

        for i in range(4):
            if guess[i] == temp_answer[i]:
                hit += 1
                guess[i] = temp_answer[i] = -1

        for i in range(4):
            if guess[i] != -1 and guess[i] in temp_answer:
                blow += 1
                temp_answer[temp_answer.index(guess[i])] = -1

        self.history.append((self.guess[:], hit, blow))

        if hit == 4:
            self.cleared = True
            self.mode = "result"
        elif len(self.history) >= self.battle_num:
            self.is_game_over = True
            self.mode = "result"

    def draw(self):
        pyxel.cls(7)

        if self.mode == "title":
            # タイトル画面：画像を表示
            pyxel.blt(72, 70, 0, 0, 0, 16, 16, scale=10)
            pyxel.text(52, 140, "CLICK TO START", pyxel.frame_count % 16)

            pyxel.text(48, 40, "Color Guess Game", 0)

        elif self.mode == "game":
            self.draw_game()

        elif self.mode == "result":
            self.draw_game()
            self.draw_result()

    def draw_game(self):
        # Color buttons
        for i, color in enumerate(COLOR_CODES):
            x, y = 10 + i * (BUTTON_SIZE + 4), 10
            pyxel.rect(x, y, BUTTON_SIZE, BUTTON_SIZE, color)
            pyxel.rectb(x, y, BUTTON_SIZE, BUTTON_SIZE, 0)

        # Current selection
        pyxel.text(10, 30, "Selected:", 0)
        for i, color in enumerate(self.guess):
            pyxel.circ(70 + i * 12, 35, 5, color)

        # Submit / Reset buttons
        pyxel.rect(10, 50, 40, 12, 3)
        pyxel.text(26, 53, "OK", 7)
        pyxel.rect(60, 50, 40, 12, 9)
        pyxel.text(70, 53, "Reset", 7)

        # Helpボタン
        pyxel.rect(110, 50, 40, 12, 5)
        pyxel.text(122, 53, "Help", 7)

        # History (2 columns × 5 rows)
        pyxel.text(10, 70, "History:", 0)
        for i, (guess, hit, blow) in enumerate(self.history[-10:]):
            col = i % 2
            row = i // 2
            x_base = 10 + col * 76
            y_base = 80 + row * 14
            for j, color in enumerate(guess):
                pyxel.circ(x_base + j * 10, y_base + 5, 4, color)
            pyxel.text(x_base + 40, y_base + 4, f"H:{hit} B:{blow}", 0)

        # Tries left
        # pyxel.text(107, 70, f"Chances: {10 - len(self.history)}", 3)
        pyxel.text(107, 70, f"Chances: {10 - len(self.history):02}", 3)

        # music on/off
        pyxel.rect(140, 5, 15, 9, 11)
        pyxel.text(142, 7, "BGM", 7 if self.playing else 1)

        # ヘルプ画面
        if self.show_help:
            self.draw_help()

    def draw_result(self):
        pyxel.rect(10, 10, 140, 55, 3)
        if self.cleared:
            pyxel.text(20, 20, "CLEAR!", 7)
        else:
            pyxel.text(20, 20, "GAME OVER", 7)

        pyxel.text(20, 38, "CORRECT ANSWER:", 7)
        for i, color in enumerate(self.answer):
            pyxel.circ(100 + i * 12, 40, 4, color)
        # Tries left
        # pyxel.text(95, 20, f"Tries: {len(self.history)}", 7)
        pyxel.text(67, 20, f"Solved in {len(self.history):02} tries!", 10)

        # RETRY
        pyxel.rect(59, 60, 40, 12, 9)
        pyxel.text(70, 63, "RETRY", 7)

    def draw_help(self):
        pyxel.rect(12, 12, 136, 136, 1)
        pyxel.text(20, 20, "HOW TO PLAY", 7)
        pyxel.text(20, 40, "- Choose 4 colors.", 7)
        pyxel.text(20, 50, "- Press OK to submit your guess.", 7)
        pyxel.text(20, 60, "- Press Reset to choose again.", 7)
        pyxel.text(20, 70, "- You have 10 tries to guess", 7)
        pyxel.text(20, 80, "  correctly.", 7)
        pyxel.text(20, 100, "Clear the game", 10)
        pyxel.text(20, 110, "by guessing right!", 10)
        pyxel.text(20, 125, "Click anywhere to close this", 6)
        pyxel.text(20, 135, "help", 6)
        pyxel.text(138, 20, "x", 7)


App()

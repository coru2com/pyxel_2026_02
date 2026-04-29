import pyxel
import sys
import json

is_web = sys.platform == "emscripten"
if is_web:
    import js

SCENE_MAIN = 0
SCENE_SHOP = 1
SCENE_QR = 2

QR_MATRIX = [
    [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False],
    [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False],
    [False, False, True, True, True, True, True, True, True, False, True, True, True, True, False, False, True, False, True, False, True, True, True, True, True, True, True, False, False],
    [False, False, True, False, False, False, False, False, True, False, True, True, False, True, True, False, True, False, True, False, True, False, False, False, False, False, True, False, False],
    [False, False, True, False, True, True, True, False, True, False, False, True, True, False, False, True, True, False, False, False, True, False, True, True, True, False, True, False, False],
    [False, False, True, False, True, True, True, False, True, False, True, True, True, True, True, False, True, True, True, False, True, False, True, True, True, False, True, False, False],
    [False, False, True, False, True, True, True, False, True, False, False, True, True, False, False, False, False, True, True, False, True, False, True, True, True, False, True, False, False],
    [False, False, True, False, False, False, False, False, True, False, False, False, True, False, False, False, True, False, False, False, True, False, False, False, False, False, True, False, False],
    [False, False, True, True, True, True, True, True, True, False, True, False, True, False, True, False, True, False, True, False, True, True, True, True, True, True, True, False, False],
    [False, False, False, False, False, False, False, False, False, False, True, False, False, True, False, False, False, False, True, False, False, False, False, False, False, False, False, False, False],
    [False, False, True, False, True, True, False, True, True, True, False, True, True, True, False, True, True, False, False, False, True, False, False, True, False, True, True, False, False],
    [False, False, False, True, True, False, False, True, False, False, False, True, True, True, False, False, False, False, False, False, False, True, False, False, False, True, False, False, False],
    [False, False, True, False, True, False, True, True, True, True, False, False, False, True, True, False, False, False, True, True, True, False, True, False, False, False, False, False, False],
    [False, False, False, False, True, False, False, True, False, True, False, False, True, False, True, True, False, True, False, True, False, False, True, True, True, False, False, False, False],
    [False, False, True, True, False, False, True, True, True, False, False, True, True, True, False, True, True, False, False, True, True, False, True, False, True, True, True, False, False],
    [False, False, False, True, False, False, False, True, False, False, True, False, True, True, False, False, False, True, False, True, True, True, True, False, False, False, True, False, False],
    [False, False, False, True, True, True, True, False, True, False, True, True, False, False, True, True, False, False, False, True, True, False, True, False, True, True, False, False, False],
    [False, False, True, False, True, True, False, True, False, False, True, True, True, False, True, False, True, True, True, False, False, True, True, False, False, False, True, False, False],
    [False, False, False, False, False, True, True, False, True, True, False, True, True, True, False, True, False, False, True, True, True, True, True, True, True, True, True, False, False],
    [False, False, False, False, False, False, False, False, False, False, True, True, False, False, True, False, False, False, True, False, False, False, True, False, True, False, True, False, False],
    [False, False, True, True, True, True, True, True, True, False, True, False, True, True, True, False, False, False, True, False, True, False, True, False, True, True, True, False, False],
    [False, False, True, False, False, False, False, False, True, False, True, True, False, False, True, False, False, True, True, False, False, False, True, False, False, True, True, False, False],
    [False, False, True, False, True, True, True, False, True, False, False, True, True, True, True, True, False, False, True, True, True, True, True, True, False, True, False, False, False],
    [False, False, True, False, True, True, True, False, True, False, True, True, False, False, True, True, False, False, False, False, True, False, True, True, True, True, True, False, False],
    [False, False, True, False, True, True, True, False, True, False, True, False, False, True, True, True, False, True, False, True, True, False, True, False, True, True, False, False, False],
    [False, False, True, False, False, False, False, False, True, False, False, False, True, False, False, False, False, False, False, True, True, False, True, False, True, False, False, False, False],
    [False, False, True, True, True, True, True, True, True, False, True, True, True, False, True, False, True, False, False, False, False, True, True, True, True, True, True, False, False],
    [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False],
    [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False],
]

class App:
    def __init__(self):
        pyxel.init(160, 120, title="Clicker Game")
        pyxel.mouse(True)
        
        self.scene = SCENE_MAIN
        
        self.score = 0
        self.qr_unlocked = False
        self.save_msg_timer = 0
        
        # 開発者モードフラグ
        self.dev_mode = False
        
        self.power_items = [
            {"name": "PEN (+1)", "base_cost": 10, "add": 1, "count": 0},
            {"name": "INK (+20)", "base_cost": 100, "add": 20, "count": 0},
            {"name": "PRINTER(+500)", "base_cost": 1000, "add": 500, "count": 0}
        ]
        
        self.auto_items = [
            {"name": "SOLAR (+2/s)", "base_cost": 20, "add": 2, "count": 0},
            {"name": "WIND (+50/s)", "base_cost": 200, "add": 50, "count": 0},
            {"name": "FACTORY(+1k/s)", "base_cost": 2000, "add": 1000, "count": 0}
        ]
        
        self.load_data()
        self.recalc_costs()
        
        self.qr_matrix = QR_MATRIX
        pyxel.run(self.update, self.draw)

    def recalc_costs(self):
        for item in self.power_items:
            item["cost"] = int(item["base_cost"] * (1.15 ** item["count"]))
        for item in self.auto_items:
            item["cost"] = int(item["base_cost"] * (1.15 ** item["count"]))

    def reset_data(self):
        # 開発者モードでの要素初期化処理
        self.score = 0
        self.qr_unlocked = False
        for item in self.power_items:
            item["count"] = 0
        for item in self.auto_items:
            item["count"] = 0
        self.recalc_costs()
        self.save_data()

    @property
    def click_power(self):
        return 1 + sum(i["add"] * i["count"] for i in self.power_items)

    @property
    def auto_pps(self):
        return sum(i["add"] * i["count"] for i in self.auto_items)

    def save_data(self):
        data = {
            "score": self.score,
            "qr_unlocked": self.qr_unlocked,
            "power_items": [{"count": i["count"]} for i in self.power_items],
            "auto_items": [{"count": i["count"]} for i in self.auto_items]
        }
        if is_web:
            js.localStorage.setItem("clicker_save_v2", json.dumps(data))
        else:
            with open("clicker_save_v2.json", "w") as f:
                json.dump(data, f)
        self.save_msg_timer = 30

    def load_data(self):
        try:
            data = None
            if is_web:
                saved = js.localStorage.getItem("clicker_save_v2")
                if saved: data = json.loads(saved)
            else:
                with open("clicker_save_v2.json", "r") as f:
                    data = json.load(f)
            if data:
                self.score = data.get("score", 0)
                self.qr_unlocked = data.get("qr_unlocked", False)
                p_items = data.get("power_items", [])
                for i, saved_item in enumerate(p_items):
                    if i < len(self.power_items):
                        self.power_items[i]["count"] = saved_item.get("count", 0)
                a_items = data.get("auto_items", [])
                for i, saved_item in enumerate(a_items):
                    if i < len(self.auto_items):
                        self.auto_items[i]["count"] = saved_item.get("count", 0)
        except Exception:
            pass

    def is_clicked(self, x, y, w, h):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            if x <= mx <= x + w and y <= my <= y + h:
                return True
        return False

    def is_circle_clicked(self, cx, cy, r):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            dx = pyxel.mouse_x - cx
            dy = pyxel.mouse_y - cy
            if dx*dx + dy*dy <= r*r:
                return True
        return False

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            self.save_data()
            pyxel.quit()

        if self.save_msg_timer > 0:
            self.save_msg_timer -= 1

        if pyxel.frame_count % 60 == 0:
            self.score += self.auto_pps

        if self.scene == SCENE_MAIN:
            self.update_main()
        elif self.scene == SCENE_SHOP:
            self.update_shop()
        elif self.scene == SCENE_QR:
            self.update_qr()

    def update_main(self):
        if self.dev_mode:
            if self.is_clicked(130, 2, 28, 11): # +10M
                self.score += 10000000
            if self.is_clicked(100, 2, 28, 11): # RESET
                self.reset_data()

        if self.is_circle_clicked(80, 60, 25):
            self.score += self.click_power

        if self.is_clicked(110, 80, 45, 15):
            self.scene = SCENE_SHOP

        if self.qr_unlocked:
            if self.is_clicked(5, 80, 65, 15):
                self.scene = SCENE_QR

        if self.is_clicked(110, 100, 45, 12):
            self.save_data()

    def update_shop(self):
        if self.is_clicked(5, 100, 55, 15):
            self.scene = SCENE_MAIN

        for i, item in enumerate(self.power_items):
            y = 28 + i * 16
            if self.is_clicked(2, y, 20, 11):
                if self.score >= item["cost"]:
                    self.score -= item["cost"]
                    item["count"] += 1
                    self.recalc_costs()

        for i, item in enumerate(self.auto_items):
            y = 28 + i * 16
            if self.is_clicked(75, y, 20, 11):
                if self.score >= item["cost"]:
                    self.score -= item["cost"]
                    item["count"] += 1
                    self.recalc_costs()

        if not self.qr_unlocked:
            if self.is_clicked(10, 80, 140, 15):
                if self.score >= 1000000:
                    self.score -= 1000000
                    self.qr_unlocked = True

    def update_qr(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.scene = SCENE_MAIN

    def draw(self):
        pyxel.cls(1)

        if self.scene == SCENE_MAIN:
            self.draw_main()
        elif self.scene == SCENE_SHOP:
            self.draw_shop()
        elif self.scene == SCENE_QR:
            self.draw_qr()

    def draw_main(self):
        pyxel.text(5, 5, f"SCORE: {self.score}", 7)
        pyxel.text(5, 15, f"POWER: {self.click_power}", 6)
        pyxel.text(5, 25, f"AUTO : {self.auto_pps}/s", 6)

        if self.dev_mode:
            pyxel.rect(130, 2, 28, 11, 8)
            pyxel.text(132, 5, "+10M", 7)
            pyxel.rect(100, 2, 28, 11, 8)
            pyxel.text(104, 5, "RESET", 7)

        r = 25 + (pyxel.frame_count // 5) % 3
        pyxel.circ(80, 60, r, 10)
        pyxel.circb(80, 60, r, 9)
        pyxel.text(72, 57, "TAP!", 0)

        pyxel.rect(110, 80, 45, 15, 11)
        pyxel.text(120, 85, "SHOP", 0)

        if self.qr_unlocked:
            pyxel.rect(5, 80, 65, 15, 8)
            pyxel.text(10, 85, "OPEN LINE QR", 7)

        pyxel.rect(110, 100, 45, 12, 13)
        pyxel.text(120, 103, "SAVE", 0)
        if self.save_msg_timer > 0:
            pyxel.text(80, 103, "SAVED!", 10)
            
        pyxel.text(5, 110, "[Q] QUIT&SAVE", 5)

    def draw_shop(self):
        pyxel.text(55, 5, "- ITEM SHOP -", 10)
        pyxel.text(5, 15, f"SCORE: {self.score}", 7)

        for i, item in enumerate(self.power_items):
            y = 28 + i * 16
            c = 10 if self.score >= item["cost"] else 5
            pyxel.rect(2, y, 20, 11, c)
            pyxel.text(5, y+3, "BUY", 0)
            pyxel.text(24, y, item["name"], 7)
            pyxel.text(24, y+6, f"Cost:{item['cost']}", 6)

        for i, item in enumerate(self.auto_items):
            y = 28 + i * 16
            c = 11 if self.score >= item["cost"] else 5
            pyxel.rect(75, y, 20, 11, c)
            pyxel.text(78, y+3, "BUY", 0)
            pyxel.text(97, y, item["name"], 7)
            pyxel.text(97, y+6, f"Cost:{item['cost']}", 6)

        if self.qr_unlocked:
            pyxel.rect(10, 80, 140, 15, 5)
            pyxel.text(55, 85, "SOLD OUT", 7)
        else:
            c3 = 8 if self.score >= 1000000 else 5
            pyxel.rect(10, 80, 140, 15, c3)
            
            ix, iy = 12, 83
            pyxel.rect(ix, iy, 9, 9, 7) 
            pyxel.rectb(ix+1, iy+1, 3, 3, 0)
            pyxel.rectb(ix+5, iy+1, 3, 3, 0) 
            pyxel.rectb(ix+1, iy+5, 3, 3, 0) 
            pyxel.pset(ix+6, iy+6, 0)
            pyxel.pset(ix+5, iy+7, 0)
            pyxel.pset(ix+7, iy+5, 0)
            
            pyxel.text(26, 85, "GET LINE QR (Cost: 1,000,000)", 0)

        pyxel.rect(5, 100, 55, 15, 13)
        pyxel.text(8, 105, "BACK TO MAIN", 0)

    def draw_qr(self):
        pyxel.cls(0)
        pyxel.text(48, 15, "- LINE QR CODE -", 10)
        # 生成されたマトリックスの幅に合わせて完全にセンタリングする
        self.draw_real_qr(35)
        # 13文字(52px)の真ん中
        pyxel.text(54, 100, "TAP TO RETURN", 7)

    def draw_real_qr(self, offset_y):
        if not hasattr(self, 'qr_matrix') or not self.qr_matrix:
            return
        size = len(self.qr_matrix)
        dot_size = 2
        w = size * dot_size
        offset_x = (160 - w) // 2
        
        pyxel.rect(offset_x, offset_y, w, w, 7)
        for r, row in enumerate(self.qr_matrix):
            for c, val in enumerate(row):
                if val:
                    pyxel.rect(offset_x + c * dot_size, offset_y + r * dot_size, dot_size, dot_size, 0)

App()

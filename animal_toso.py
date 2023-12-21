import math
import os
import random
import sys
import time
import pygame as pg

WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]

def check_bound(obj: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内か画面外かを判定し，真理値タプルを返す
    引数 obj：オブジェクト（爆弾，こうかとん，ビーム）SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj.left < 0 or WIDTH < obj.right:  # 横方向のはみ出し判定
        yoko = False
    if obj.top < 0 or HEIGHT < obj.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate

class Siro(pg.sprite.Sprite):
    def __init__(self, num: int, zahyo: int, size: float):
        """
        城を置く
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/siro{num}.png"), 0, size)
        self.img = pg.transform.flip(img0, True, False)  # デフォルトの城

        self.image = self.img
        self.rect = self.image.get_rect()
        self.rect.center = zahyo, 550
        self.hp = 5000

    def update(self, screen: pg.Surface):
        """
        城の描画判定
        """
        screen.blit(self.image, self.rect)

class Shoten(pg.sprite.Sprite):
    """
    友達や敵のHPが0になったときに昇天の画像を作る。
    引数として座標が送られる。
    """
    def __init__(self, zahyo):
        super().__init__()
        img = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/shoten.png"), 0, 2.5)
        self.image = img  #昇天の画像を作成
        self.rect = self.image.get_rect()  #れくとを生成
        self.rect.center = zahyo
        self.speed = 3.5  #上に上がるスピードを定義

    def update(self, screen:pg.Surface):
        """
        昇天画像を上に上昇させる。
        """
        self.rect.move_ip(0, -self.speed)
        screen.blit(self.image, self.rect)
        if check_bound(self.rect) != (True, True):
            self.kill()
    


class Tomo(pg.sprite.Sprite):
    """
    味方に関するクラス
    """
    def __init__(self, name):
        super().__init__()
        self.tmr = random.randint(1, 100)
        self.zahyo = random.randint(1, 15)

        img = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/{name}.png"), 0, 0.5)
        self.image = img  #猫の画像を読み込む
        self.rect = self.image.get_rect()  #れくとを生成
        self.rect.center = 1400, 627-self.zahyo
        self.speed = 2
        self.state = "normal"  #猫の状態を定義
        self.hp = 500
        self.attack = 20

    def motion(self, enemy, tmr):
        """
        攻撃のモーションを定義
        """
        if tmr%100 == self.tmr:
            enemy.hp -= self.attack
            self.rect.move_ip(8, 0)

    def update(self, screen:pg.Surface):
        """
        猫を自陣から左に移動させる。
        """
        if self.state == "normal":
            self.rect.move_ip(-self.speed, 0)
            screen.blit(self.image, self.rect)
            if check_bound(self.rect) != (True, True):
                self.kill()
        elif self.state == "atk":
            screen.blit(self.image, self.rect)
        elif self.state == "death":
            screen.blit(self.image, self.rect)
            self.kill()


class LongTomo(pg.sprite.Sprite):
    def __init__(self, name):
        super().__init__()
        self.tmr = random.randint(1, 300)  #300に一回の攻撃のタイミングを決定する。
        self.range = 300  # 攻撃の射程を定義
        self.zahyo = random.randint(1, 15)

        img = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/{name}.png"), 0, 0.2)
        self.image = img  #キリンの画像を読み込む
        self.rect = self.image.get_rect()  #れくとを生成
        self.rect.center = 1400, 580-self.zahyo
        self.speed = 1.8
        self.attack = 80
        self.hp = 800
        self.state = "normal"
        
        
    def motion(self, enemy, tmr):
        """
        攻撃モーションを起動する処理
        """
        if tmr%180 == self.tmr:
            enemy.hp -= self.attack
            self.rect.move_ip(8, 0)


    def update(self, screen:pg.Surface):
        """
        猫を自陣から左に移動させる。
        """
        if self.state == "normal":
            self.rect.move_ip(-self.speed, 0)
            screen.blit(self.image, self.rect)
            if check_bound(self.rect) != (True, True):
                self.kill()
        elif self.state == "atk":
            screen.blit(self.image, self.rect)
        elif self.state == "death":
            screen.blit(self.image, self.rect)
            self.kill()

def main():
    pg.display.set_caption("アニマル闘争")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"{MAIN_DIR}/fig/haikei.jpg")
    cats = pg.sprite.Group()
    giraffes = pg.sprite.Group()
    shotens = pg.sprite.Group()

    tmr = 0
    clock = pg.time.Clock()

    enemy_siro = Siro(0, 200, 0.4)
    siro = Siro(1, 1400, 0.3)
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_1:
                    cats.add(Tomo("cat"))  #ねこを追加
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_2:
                    giraffes.add(LongTomo("giraffe"))  #キリンを追加

        # 猫に対する捜査の実行
        for cat in cats:
            # 猫が敵の城と当たったときの操作
            if len(pg.sprite.spritecollide(enemy_siro, [cat], False)) != 0:  # ねこと敵城がぶつかったときに止まり攻撃
                cat.hp = 0
                cat.state = "atk"
                cat.motion(enemy_siro, tmr)
            else:
                cat.state = "normal"
            if cat.hp <= 0:
                cat.state = "death"
                shotens.add(Shoten(cat.rect.center))
        
        #射程の長いキリンに対する処理
        for giraffe in giraffes:
            if giraffe.rect.center[0] - enemy_siro.rect.center[0] <= giraffe.range:  # 射程内に敵城がある場合
                giraffe.state = "atk"
                giraffe.motion(enemy_siro, tmr)
            else:
                giraffe.state = "normal"
            if giraffe.hp <= 0:
                giraffe.state = "death"
                shotens.add(Shoten(cat.rect.center))

        if enemy_siro.hp <= 0:
            return

        print(siro.hp)
        screen.blit(bg_img, [0, 0])

        enemy_siro.update(screen)
        siro.update(screen)
        cats.update(screen)
        giraffes.update(screen)
        shotens.update(screen)
        pg.display.update()

        tmr += 1
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
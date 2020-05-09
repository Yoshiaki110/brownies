import sys
import lcd
import image
from fpioa_manager import *
from Maix import I2S, GPIO
from machine import I2C

i2c = I2C(I2C.I2C0, freq=400000, scl=28, sda=29)
def set_backlight(level):
    if level > 8:
        level = 8
    if level < 0:
        level = 0
    val = (level+7) << 4
    i2c.writeto_mem(0x34, 0x91,int(val))

fm.register(board_info.BUTTON_A, fm.fpioa.GPIO1)
but_a=GPIO(GPIO.GPIO1, GPIO.IN, GPIO.PULL_UP) #PULL_UP is required here!

fm.register(board_info.BUTTON_B, fm.fpioa.GPIO2)
but_b = GPIO(GPIO.GPIO2, GPIO.IN, GPIO.PULL_UP) #PULL_UP is required here!

# BUTTON_Cは、なかった
#fm.register(board_info.BUTTON_C, fm.fpioa.GPIO2)
#but_b = GPIO(GPIO.GPIO2, GPIO.IN, GPIO.PULL_UP) #PULL_UP is required here!

def check_but():
    if but_a.value() == 0:
        print('[info]: Button A pushed')
        return 'A'
    if but_b.value() == 0:
        print('[info]: Button B pushed')
        return 'B'
    return None

prog = [("brownie","brownie20.py"),
        ("br_1000","brownie1000.py"),
        ("br_learn","brownielearn.py"),
        ("face","face.py"),             # yoro 顔認識、サーボで顔追跡
        ("face-rv","facetrack.py"),     # yoro 顔認識、RoverCで顔追跡
        ("learn","learn.py"),           # QR使わないbrownielearn
        ("distance","distance.py"),     # 距離計測、RoverCで自動ブレーキ
        ("oshaku","oshaku.py"),         # 遠隔お酌
        ("v-train","vtrain.py"),        # v-train
        ("janken","janken.py"),         # ぐーちょきぱの判定
        ("camera","camera.py"),         # 写真撮影
        ("video_r","video_r.py"),       # 動画撮影
        ("video_p","video_p.py"),       # 動画再生
        ("poweroff","poweroff"),
        ("-","")]

lcd.init()
lcd.rotation(2)
def disp():
    lcd.clear()
    img = image.Image()
    img.draw_string(0, 0, '<< MENU >>', (255,0,0), scale=3)
    lcd.display(img)
    for i in range(4):
        c = " " if i != 2 else ">"
        img.draw_string(0, i * 25 + 25, c + prog[i][0], scale=3)
        lcd.display(img)
        print(prog[i])

disp()
#time.sleep(2)
while(True):
    but = check_but()
    if but == 'A':
        print(prog[2][1])
        if len(prog[2][1]) == 0:
            print('not exec')
        elif prog[2][1] == 'poweroff':
            print('exit')
            lcd.clear()
            set_backlight(0)
            sys.exit()
        else:
            # exec(open("xx.py").read()) でできるかも
            cmd = 'import ' + prog[2][1]
            print('exec ' + cmd)
            exec(cmd)
        time.sleep(0.3)
    if but == 'B':
        tmp = prog.pop(0)
        prog.append(tmp)
        disp()
        time.sleep(0.3)

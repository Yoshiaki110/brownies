# 遠隔お酌
#
# Usage :
# Button A : Shutter / OK
#        B : Menu    / Cancel
# Firmware: maixpy_v0.5.0_9_g8eba07d_m5stickv.bin
#
# GROVE 黄色：34 白:35

import KPU as kpu
import sensor
import lcd
import image
import time
import uos
import gc
import ulab as np
from fpioa_manager import *
from Maix import utils, GPIO
from machine import Timer,PWM,I2C

utils.gc_heap_size(400000)

# LCD初期化
lcd.init()
lcd.rotation(2)

i2c = I2C(I2C.I2C0, freq=400000, scl=28, sda=29)
def set_backlight(level):
    if level > 8:
        level = 8
    if level < 0:
        level = 0
    val = (level+7) << 4
    i2c.writeto_mem(0x34, 0x91,int(val))

try:
    img = image.Image("/sd/enkaku.jpg")
    set_backlight(0)
    lcd.display(img)
    for i in range(9):
        set_backlight(i)
        time.sleep(0.1)
    time.sleep(1)
except Exception as e:
    print(e)

# サーボ関連
# FREQ は 50じゃない
FREQ = 20
PULSE_MIN = 0.6
PULSE_MAX = 2.3

tim = Timer(Timer.TIMER0, Timer.CHANNEL0, mode=Timer.MODE_PWM)
ch = PWM(tim, freq=50, duty=2.5, pin=35)
arg = {-90:2.5, 0:7.25, 90:12}	# arg:duty

def setAngle(ang):
    diff = PULSE_MAX - PULSE_MIN
    pich = diff / 180
    pulse = ang * pich + PULSE_MIN
    duty = pulse / FREQ * 100
    print("-------- ang {} ----- duty {}".format(ang, duty))
    #print("----------------- duty" + str(duty))
    ch.duty(duty)
setAngle(0)

# ボタンの初期化
fm.register(board_info.BUTTON_A, fm.fpioa.GPIO1)
but_a=GPIO(GPIO.GPIO1, GPIO.IN, GPIO.PULL_UP) #PULL_UP is required here!
fm.register(board_info.BUTTON_B, fm.fpioa.GPIO2)
but_b = GPIO(GPIO.GPIO2, GPIO.IN, GPIO.PULL_UP) #PULL_UP is required here!

# カメラ初期化
err_counter = 0
while 1:
    try:
        sensor.reset() #Reset sensor may failed, let's try some times
        break
    except:
        err_counter = err_counter + 1
        if err_counter == 20:
            lcd.draw_string(lcd.width()//2-100,lcd.height()//2-4, "Error: Sensor Init Failed", lcd.WHITE, lcd.RED)
        time.sleep(0.1)
        continue

sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA) #QVGA=320x240
sensor.set_windowing((224, 224))
sensor.run(1)

# AI関連
def get_feature(task):
    img = sensor.snapshot()
    img.draw_rectangle(1,46,222,132,color=(255,0,0),thickness=3)
    lcd.display(img)
    feature = kpu.forward(task,img)
    print('get_feature')
    gc.collect()
    return np.array(feature[:])

def get_nearest(feature_list, feature):
    min_dist = 10000
    name = ''
    vec = []
    for n,v in feature_list:
        dist = np.sum((v-feature)*(v-feature))
        if dist < min_dist:
            min_dist = dist
            name = n
            vec = v
    return name,min_dist,vec

def load(filename):
    feature_list=[]
    try:
        with open(filename, 'rt') as f:
            li = f.readline()
            while li:
                li = li.strip().split(',')
                n = str(li[0])
                vec = np.array([float(v) for v in li[1:]])
                feature_list.append([n,vec])
                li = f.readline()
    except:
        print("no data.")
    return feature_list

def save(filename,feature_list):
    gc.collect()
    output = ""
    try:
        with open(filename, 'wt') as f:
            for n,vec in feature_list:
                f.write(n)
                for v in vec:
                    vec_str=",{0:.5f}".format(v)
                    f.write(vec_str)
                f.write('\n')
    except:
        print("write error.")

feature_file = "/sd/oshaku.csv"
feature_list = load(feature_file)
task = kpu.load("/sd/model/mbnet751_feature.kmodel")
info = kpu.netinfo(task)

# メニュー関連
def disp(title, item):
    print('disp')
    lcd.clear()
    img = image.Image()
    img.draw_string(0, 0, '<<' + title + '>>', (255,0,0), scale=3)
    lcd.display(img)
    for i in range(4):
        c = " " if i != 1 else ">"
        img.draw_string(0, i * 25 + 25, c + item[i], scale=3)
        lcd.display(img)

def menu(title, item):
    gc.collect()
    time.sleep(0.3)
    print("menu 1")
    disp(title, item)
    print("menu 2")
    while(True):
        if but_a.value() == 0:
            print(item[1])
            time.sleep(0.3)
            #return item[2]
            print("menu 3")
            if len(item[1]) > 0:
                break
        if but_b.value() == 0:
            print("menu 4")
            tmp = item.pop(0)
            item.append(tmp)
            print("menu 5")
            disp(title, item)
            print("menu 6")
            time.sleep(0.3)
    return item[1]

# メイン処理
lastTime = time.ticks_ms()
targetAngle = 0
currentAngle = 0
try:
    while(True):
        now = time.ticks_ms()
        if now - lastTime > 2:
            #print("target:" + str(targetAngle) + " current:" + str(currentAngle))
            lastTime = now
            if targetAngle < currentAngle:
                currentAngle -= 5
                setAngle(currentAngle)
            elif targetAngle > currentAngle:
                currentAngle += 5
                setAngle(currentAngle)

        if but_a.value() == 0:
            print('@@@ recording')
            feature = get_feature(task)
            gc.collect()
            time.sleep(0.3)
            ret = menu(" SAVE ", ["Cancel","0","45","90","135",""])
            if ret != "Cancel":
                feature_list.append([ret,feature])
                save(feature_file, feature_list)
            gc.collect()
            # print(gc.mem_free())
            kpu.fmap_free(feature)
            print('@@@ record finished')
            continue
        if but_b.value() == 0:
            print('@@@ reset 0')
            ret = menu("CLEAR", ["OK","Cancel","",""])
            print('@@@ reset 1')
            if ret == "OK":
                feature_list = []
                save(feature_file, feature_list)
            time.sleep(0.3)
            continue

        img = sensor.snapshot()

        # inference
        fmap = kpu.forward(task, img)
        p = np.array(fmap[:])

        # get nearest target
        name,dist,_ = get_nearest(feature_list, p)
        #print("name:" + name + " dist:" + str(dist) + " mem:" + str(gc.mem_free()))
        if dist < 200:
            img.draw_rectangle(1,46,222,132,color=(0,255,0),thickness=3)
            img.draw_string(8, 47 +30, "%s"%(name), scale=3)
            print("[DETECTED]: on:" + name)
            gc.collect()
            targetAngle = int(name)
            #print("targetAngle" + str(targetAngle))
        else:
            targetAngle = 0

        # output
        lcd.display(img)
        kpu.fmap_free(fmap)
except Exception as e:
    print("Exception")
    print(e)
    print("-------")
    kpu.deinit(task)
    sys.exit()

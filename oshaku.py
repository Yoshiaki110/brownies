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
import audio
import gc
import ulab as np
from fpioa_manager import *
from Maix import utils, I2S, GPIO
from machine import Timer,PWM,I2C
import _thread

#utils.gc_heap_size(400000)      # 287
utils.gc_heap_size(450000)      # 287

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
    img = image.Image("/sd/oshaku/enkaku.jpg")
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
    pulse = (ang+45) * pich + PULSE_MIN
    duty = pulse / FREQ * 100
    print("-------- ang %d ----- duty %f"%(ang, duty))
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
        sensor.reset()
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
feature_list = []
def free():
    mem = gc.mem_free()
    b = gc.mem_free()
    gc.collect()
    a = gc.mem_free()
    print("gc %d -> %d %d" % (b, a, len(feature_list)))
free()

def get_feature(task, img):
    print("--- 1")
    #img = sensor.snapshot()
    print("--- 2")
    #img.draw_rectangle(1,46,222,132,color=(255,0,0),thickness=3)
    print("--- 3")
    #lcd.display(img)
    free()
    print("--- 4")
    feature = kpu.forward(task,img)
    print("--- 5")
    free()
    print("--- 6")
    #return np.array(feature[:])
    ar = np.array(feature[:])
    print("--- 7")
    return ar

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
    except Exception as e:
        print('load err:' + str(e))
    return feature_list

def save(filename,feature_list):
    free()
    output = ""
    try:
        with open(filename, 'wt') as f:
            for n,vec in feature_list:
                f.write(n)
                for v in vec:
                    vec_str=",{0:.5f}".format(v)
                    f.write(vec_str)
                f.write('\n')
    except Exception as e:
        print('write err:' + str(e))

feature_file = "/sd/oshaku.csv"
feature_default_file = "/sd/oshaku.default.csv"
feature_list = load(feature_file)
task = kpu.load("/sd/oshaku/mbnet751_feature.kmodel")
info = kpu.netinfo(task)

# 音声関連
fm.register(board_info.SPK_SD, fm.fpioa.GPIO0)
spk_sd=GPIO(GPIO.GPIO0, GPIO.OUT)
spk_sd.value(1) #Enable the SPK output
fm.register(board_info.SPK_DIN,fm.fpioa.I2S0_OUT_D1)
fm.register(board_info.SPK_BCLK,fm.fpioa.I2S0_SCLK)
fm.register(board_info.SPK_LRCLK,fm.fpioa.I2S0_WS)
wav_dev = I2S(I2S.DEVICE_0)
def play_sound(filename):
    try:
        player = audio.Audio(path = filename)
        player.volume(10)
        wav_info = player.play_process(wav_dev)
        wav_dev.channel_config(wav_dev.CHANNEL_1, I2S.TRANSMITTER,resolution = I2S.RESOLUTION_16_BIT, align_mode = I2S.STANDARD_MODE)
        wav_dev.set_sample_rate(wav_info[1])
        while True:
            ret = player.play()
            if ret == None:
                break
            elif ret==0:
                break
        player.finish()
        time.sleep(0.1)
    except Exception as e:
        print('sound err:' + str(e))

# メニュー関連
def disp(title, item):
    lcd.clear()
    print('* 1')
    img = image.Image()
    img.draw_string(0, 0, '<<' + title + '>>', (255,0,0), scale=3)
    for i in range(4):
        c = " " if i != 1 else ">"
        img.draw_string(0, i * 25 + 25, c + item[i], scale=3)
    lcd.display(img)
    print('* 2')

def menu(title, item):
    print('* 21')
    free()
    print('* 22')
    #time.sleep(0.3)
    print('* 23')
    disp(title, item)
    print('* 24')
    while(True):
        if but_a.value() == 0:
            time.sleep(0.3)
            if len(item[1]) > 0:
                break
        if but_b.value() == 0:
            time.sleep(0.3)
            tmp = item.pop(0)
            item.append(tmp)
            disp(title, item)
    return item[1]

def delay(ms):
    st = time.ticks_ms()
    while(True):
        i = sensor.snapshot()
        now = time.ticks_ms()
        if now - st > ms:
            break
        lcd.display(i)

def wizard(task):
    play_sound("/sd/oshaku/start_learn.wav")
    free()
    delay(1500)
    for ang in ["0","45","90","135"]:
        play_sound("/sd/oshaku/" + str(ang) + ".wav")
        play_sound("/sd/oshaku/satuei.wav")
        delay(1000)
        for i in ["3","2","1"]:
            play_sound("/sd/oshaku/" + str(i) + ".wav")
            delay(700)
        play_sound("/sd/oshaku/kacha.wav")
        img = sensor.snapshot()
        lcd.display(img)
        feature = get_feature(task, img)
        free()
        feature_list.append([ang,feature])
        save(feature_file, feature_list)
        free()
    kpu.fmap_free(feature)


'''
print("Thread -1")
def func(name):
    while 1:
        print("Thread")
        time.sleep(1)
_thread.start_new_thread(func,("1",))
print("Thread -2")
'''

# メイン処理
lastTime = time.ticks_ms()
targetAngle = 0
currentAngle = 0
try:
    while(True):
        img = sensor.snapshot()

        now = time.ticks_ms()
        if now - lastTime > 2:
            #print("target:" + str(targetAngle) + " current:" + str(currentAngle))
            lastTime = now
            if targetAngle < currentAngle:
                currentAngle -= 3
                setAngle(currentAngle)
            elif targetAngle > currentAngle:
                currentAngle += 3
                setAngle(currentAngle)

        if but_a.value() == 0:
            time.sleep(0.3)
            print('= 1')
            free()
            print('= 1.1')
            play_sound("/sd/oshaku/kacha.wav")
            print('= 1.2')
            free()
            time.sleep(0.5)
            print('= 1.5')
            feature = get_feature(task, img)
            free()
            #time.sleep(0.3)
            print('= 2')
            ret = menu(" SAVE ", ["Cancel","0","45","90","135",""])
            print('= 3')
            if ret != "Cancel":
                feature_list.append([ret,feature])
                save(feature_file, feature_list)
            free()
            print('= 4')
            kpu.fmap_free(feature)
            print('= 5')
            continue
        if but_b.value() == 0:
            time.sleep(0.3)
            print("*** 1")
            free()
            print("*** 2")
            ret = menu(" MENU ", ["Power Off","Cancel","Auto Set","Clear","Default",""])
            print("*** " + ret)
            free()
            print("*** 3")
            if ret == "Power Off":
                setAngle(0)
                lcd.clear()
                set_backlight(0)
                kpu.deinit(task)
                sys.exit()
            if ret == "Clear":
                feature_list = []
                save(feature_file, feature_list)
            if ret == "Default":
                feature_list = load(feature_default_file)
            if ret == "Auto Set":
                print("*** 5")
                wizard(task)
            print("*** 9")
            continue

        # inference
        fmap = kpu.forward(task, img)
        p = np.array(fmap[:])

        # get nearest target
        name,dist,_ = get_nearest(feature_list, p)
        #print("name:" + name + " dist:" + str(dist) + " mem:" + str(gc.mem_free()))
        if dist < 200:
            img.draw_rectangle(1,46,222,132,color=(0,255,0),thickness=3)
            img.draw_string(9, 78, "%s"%(name), lcd.BLACK, scale=3)
            img.draw_string(8, 77, "%s"%(name), lcd.WHITE, scale=3)
            print("[DETECTED]: on:" + name)
            #gc.collect()
            targetAngle = int(name)
            #print("targetAngle" + str(targetAngle))
        else:
            targetAngle = 0

        # output
        img.draw_string(91, 46, "Learn[A] Menu[B]", lcd.BLACK, mono_space=False, scale=2)
        img.draw_string(90, 45, "Learn[A] Menu[B]", lcd.RED, mono_space=False, scale=2)
        gc.collect()
        mb = "learned[{:>2}] fmem[{:>4}]".format(len(feature_list), gc.mem_free() // 1024)
        print(mb)
        img.draw_string(41, 161, mb, lcd.BLACK, mono_space=False, scale=2)
        img.draw_string(40, 160, mb, lcd.GREEN, mono_space=False, scale=2)
        lcd.display(img)
        #lcd.display(img, roi=(10, 0, 240, 135), oft=(0, 0))
        kpu.fmap_free(fmap)
except Exception as e:
    #print('======')
    print('type:' + str(type(e)))
    print('args:' + str(e.args))
    #print('message:' + e.message)
    print('e:' + str(e))
    kpu.deinit(task)
    sys.exit()
except KeyboardInterrupt:
    a = kpu.deinit(task)
    sys.exit()

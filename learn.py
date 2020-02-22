#
#
# Usage :
# Button A : Shutter / OK
#        B : Menu    / Cancel
# Firmware: maixpy_v0.5.0_9_g8eba07d_m5stickv.bin
#
import KPU as kpu
import sensor
import lcd
import time
import uos
import gc
import ulab as np
from fpioa_manager import *
from Maix import utils, GPIO

fm.register(board_info.BUTTON_A, fm.fpioa.GPIO1)
but_a=GPIO(GPIO.GPIO1, GPIO.IN, GPIO.PULL_UP) #PULL_UP is required here!

fm.register(board_info.BUTTON_B, fm.fpioa.GPIO2)
but_b = GPIO(GPIO.GPIO2, GPIO.IN, GPIO.PULL_UP) #PULL_UP is required here!

utils.gc_heap_size(250000)

def initialize_camera():
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

def get_feature(task):
    img = sensor.snapshot()
    img.draw_rectangle(1,46,222,132,color=(255,0,0),thickness=3)
    lcd.display(img)
    feature = kpu.forward(task,img)
    print('get_feature')
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

#
# main
#

feature_list = []
task = kpu.load("/sd/model/mbnet751_feature.kmodel")

initialize_camera()

print('[info]: Started.')

info=kpu.netinfo(task)
#a=kpu.set_layers(task,29)

old_name=''

clock = time.clock()
try:
    while(True):
        if but_a.value() == 0:
            print('@@@ recording')
            feature = get_feature(task)
            feature_list.append([name,feature])
            gc.collect()
            # print(gc.mem_free())
            kpu.fmap_free(feature)
            print('@@@ record finished')
            continue
        if but_b.value() == 0:
            print('@@@ reset')
            feature_list = []
            continue

        img = sensor.snapshot()

        # inference
        fmap = kpu.forward(task, img)
        p = np.array(fmap[:])

        # get nearest target
        name,dist,_ = get_nearest(feature_list, p)
        print("name:" + name + " dist:" + str(dist))
        if dist < 200:
            img.draw_rectangle(1,46,222,132,color=(0,255,0),thickness=3)
            img.draw_string(2, 47 +30, "%s"%(name), scale=3)
            print("[DETECTED]: on:" + old_name + " n:" + name)
            if old_name != name:
                lcd.display(img)
                old_name = name
        else:
            old_name = ''

        # output
        #img.draw_string(2,47, "%.2f "%(dist),scale=3)
        lcd.display(img)
        kpu.fmap_free(fmap)
except:
    kpu.deinit(task)
    sys.exit()

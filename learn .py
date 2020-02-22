#
#
# Usage :
# Button A : Shutter / OK
#        B : Menu    / Cancel
# Firmware: maixpy_v0.5.0_9_g8eba07d_m5stickv.bin
#
import brownie as br
import KPU as kpu
import sensor
import lcd
import time
import uos
import gc
import ulab as np
from fpioa_manager import *
from Maix import utils
from machine import UART

utils.gc_heap_size(250000)

# for Grove Port
fm.register(35, fm.fpioa.UART2_TX, force=True)
fm.register(34, fm.fpioa.UART2_RX, force=True)

def get_feature(task):
    img = sensor.snapshot()
    img.draw_rectangle(1,46,222,132,color=br.get_color(255,0,0),thickness=3)
    lcd.display(img)
    feature = kpu.forward(task,img)
    print('get_feature')
    return np.array(feature[:])

def get_nearest(feature_list,feature):
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
br.exit_check()

feature_list = []
task = kpu.load("/sd/model/mbnet751_feature.kmodel")

br.initialize_camera()

print('[info]: Started.')

info=kpu.netinfo(task)
#a=kpu.set_layers(task,29)

old_name=''

clock = time.clock()
try:
    while(True):
        but = br.check_but()        # ボタン入力確認
        if but == 'A':
            print('@@@ recording')
            feature = get_feature(task)
            feature_list.append([name,feature])
            gc.collect()
            # print(gc.mem_free())
            kpu.fmap_free(feature)
            print('@@@ record finished')
            continue
        if but == 'B':
            print('@@@ reset')
            feature_list = []
            continue

        img = sensor.snapshot()

        # inference
        fmap = kpu.forward(task, img)
        p = np.array(fmap[:])

        # get nearest target
        name,dist,_ = get_nearest(feature_list,p)
        print("name:" + name + " dist:" + str(dist))
        if dist < 200 and name != "*exclude":
            img.draw_rectangle(1,46,222,132,color=br.get_color(0,255,0),thickness=3)
            img.draw_string(2, 47 +30, "%s"%(name), scale=3)
            print("[DETECTED]: on:" + old_name + " n:" + name)
            if old_name != name:
                lcd.display(img)
                old_name = name
        else:
            old_name = ''

        # output
        #img.draw_string(2,47,  "%.2f "%(dist),scale=3)
        lcd.display(img)
        kpu.fmap_free(fmap)
except:
    kpu.deinit(task)
    sys.exit()

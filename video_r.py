import audio
import re
from fpioa_manager import *
from machine import I2C
from Maix import I2S, GPIO
import sensor, image, time
import lcd
import video

lcd.init()
lcd.rotation(2)

fm.register(board_info.SPK_SD, fm.fpioa.GPIO0)
spk_sd=GPIO(GPIO.GPIO0, GPIO.OUT)
spk_sd.value(1) #Enable the SPK output

fm.register(board_info.SPK_DIN,fm.fpioa.I2S0_OUT_D1)
fm.register(board_info.SPK_BCLK,fm.fpioa.I2S0_SCLK)
fm.register(board_info.SPK_LRCLK,fm.fpioa.I2S0_WS)

wav_dev = I2S(I2S.DEVICE_0)

fm.register(board_info.BUTTON_A, fm.fpioa.GPIO1)
but_a=GPIO(GPIO.GPIO1, GPIO.IN, GPIO.PULL_UP) #PULL_UP is required here!


sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(30)

def play_sound(filename):
    try:
        player = audio.Audio(path = filename)
        player.volume(100)
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
    except:
        pass

rec = False
while(True):
    img = sensor.snapshot()
    if not but_a.value():
        time.sleep(0.1)
        if rec:
            print("finish")
            v.record_finish()
            rec = False
        else:
            print("start")
            v = video.open("/sd/capture.avi", record=1, interval=200000, quality=50)
            rec = True
    if rec:
        img_len = v.record(img)
        img.draw_string(50, 50, "recording", (255,0,0), mono_space=False, scale=2)
    else:
        img.draw_string(50, 50, "Record[A]", mono_space=False, scale=2)
    lcd.display(img)
lcd.clear()

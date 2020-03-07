import audio
import re
from fpioa_manager import *
from machine import I2C
from Maix import I2S, GPIO
import sensor, image, time
import lcd

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

fm.register(board_info.BUTTON_B, fm.fpioa.GPIO2)
but_b = GPIO(GPIO.GPIO2, GPIO.IN, GPIO.PULL_UP) #PULL_UP is required here!

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)

try:
    os.mkdir("/sd/DCIM")
except Exception as e:
    pass

fl = os.listdir('/sd/DCIM')
fl.sort(reverse = True)
cnt = int(re.sub("\\D", "", fl[0])) + 1

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

def shutter():
    global cnt
    img = sensor.snapshot()
    fn = "/sd/DCIM/" + '{:04d}'.format(cnt) + ".jpg"
    img.save(fn, quality=95)
    cnt += 1
    print("shutter")
    play_sound("/sd/kacha.wav")
    img = image.Image(fn, copy_to_fb = True)
    lcd.display(img)
    time.sleep(3)

def selftimer():
    print("selftimer 3")
    play_sound("/sd/voice/3s.wav")
    time.sleep(1)
    print("selftimer 2")
    play_sound("/sd/voice/2s.wav")
    time.sleep(1)
    print("selftimer 1")
    play_sound("/sd/voice/1s.wav")
    time.sleep(1)
    shutter()

while(True):
    img = sensor.snapshot()
    guide = "Shutter[A] SelfTimer[B] {:04}".format(cnt)
    img.draw_string(50, 50, guide, mono_space=False, scale=2)
    lcd.display(img)
#    lcd.draw_string(0, 0, "Shutter[A] SelfTimer[B]")
    if not but_a.value():
        selftimer()
    if not but_b.value():
        shutter()

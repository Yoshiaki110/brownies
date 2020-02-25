# Original: https://iotdiary.blogspot.com/2019/07/maixpy-go-mobilenet-transfer-learning.html
# Slightly modified for M5StickV
import sensor
import image
import lcd
import KPU as kpu
lcd.init()
lcd.rotation(2)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_windowing((224, 224))
sensor.set_vflip(0)
sensor.set_hmirror(0)
sensor.run(1)
lcd.clear()
lcd.draw_string(135, 0, "MobileNetDemo")
f = open('/sd/model/janken.txt', 'r')
labels = f.readlines()
f.close()
print(labels)
task = kpu.load("/sd/model/janken.kmodel")
while(True):
  img = sensor.snapshot()
  fmap = kpu.forward(task, img)
  plist = fmap[:]
  pmax = max(plist)
  max_index = plist.index(pmax)
  a = lcd.display(img, roi=(0, 0, 135, 135), oft=(0, 0))
  lcd.draw_string(135, 100, "%s     " % (labels[max_index].strip()))
  lcd.draw_string(135, 119, "%.2f" % (pmax))
a = kpu.deinit(task)

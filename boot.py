import lcd
import image
from fpioa_manager import *
from Maix import I2S, GPIO

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
        ("face","face.py"),
        ("learn","learn.py"),
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
        else:
            cmd = 'import ' + prog[2][1]
            print('exec ' + cmd)
            exec(cmd)
        time.sleep(0.3)
    if but == 'B':
        tmp = prog.pop(0)
        prog.append(tmp)
        disp()
        time.sleep(0.3)

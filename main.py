from machine import Pin, PWM, I2C
from neopixel import NeoPixel
from random import randint
from time import sleep_ms
from I2C_LCD import I2cLcd

NUM_LEDS = 17
NUM_RING = 35

BLUE = (0, 0, 35)
RED = (35, 0, 0)
YELLOW = (35, 35, 0)
OFF = (0, 0, 0)

SCORE_1 = list(range(0, 18))
SCORE_2 = list(range(18, 29))
SCORE_3 = list(range(29, 35))

takki_blue1 = Pin(10, Pin.IN, Pin.PULL_UP)
takki_blue2 = Pin(16, Pin.IN, Pin.PULL_UP)
takki_red1 = Pin(11, Pin.IN, Pin.PULL_UP)
takki_red2 = Pin(8, Pin.IN, Pin.PULL_UP)
takki_dice = Pin(13, Pin.IN, Pin.PULL_UP)

led_blue1 = Pin(42, Pin.OUT)
led_blue2 = Pin(21, Pin.OUT)
led_red1 = Pin(47, Pin.OUT)
led_red2 = Pin(48, Pin.OUT)
led_dice = Pin(41, Pin.OUT)

buzzer = PWM(Pin(14))
buzzer.duty(0)

strip1 = NeoPixel(Pin(2), NUM_LEDS)
strip2 = NeoPixel(Pin(4), NUM_LEDS)
ring = NeoPixel(Pin(7), NUM_RING)

lcd = None
try:
    i2c = I2C(0, scl=Pin(5), sda=Pin(6))
    devices = i2c.scan()
    if devices:
        lcd = I2cLcd(i2c, devices[0], 2, 16)
except:
    lcd = None

position = 8
game_on = True

startup_song = [
    (659, 120),
    (659, 120),
    (0, 50),
    (659, 120),
    (0, 50),
    (523, 120),
    (659, 120),
    (784, 250),
    (392, 250)
]

victory_song = [
    (523, 100),
    (659, 100),
    (784, 100),
    (1047, 200),
    (784, 100),
    (1047, 300)
]

def play_song(song):

    for freq, length in song:

        if freq > 0:
            buzzer.freq(freq)
            buzzer.duty(300)
        else:
            buzzer.duty(0)

        sleep_ms(length)
        buzzer.duty(0)
        sleep_ms(30)

def clear_all():

    for i in range(NUM_LEDS):
        strip1[i] = OFF
        strip2[i] = OFF

    for i in range(NUM_RING):
        ring[i] = OFF

    strip1.write()
    strip2.write()
    ring.write()

def startup_anim():

    for i in range(NUM_RING):
        ring[i] = BLUE
        ring.write()
        sleep_ms(20)

    for i in range(NUM_RING):
        ring[i] = RED
        ring.write()
        sleep_ms(20)

    for i in range(NUM_RING):
        ring[i] = OFF

    ring.write()

    play_song(startup_song)

def victory_anim(color):

    for j in range(4):

        for i in range(NUM_RING):
            ring[i] = color

        ring.write()

        buzzer.freq(1200)
        buzzer.duty(300)
        sleep_ms(120)

        for i in range(NUM_RING):
            ring[i] = OFF

        ring.write()

        buzzer.duty(0)
        sleep_ms(120)

    play_song(victory_song)

def update_rope():

    for i in range(NUM_LEDS):

        if i == 0:
            strip1[i] = OFF
            strip2[i] = OFF

        elif i <= position:
            strip1[i] = RED
            strip2[i] = RED

        else:
            strip1[i] = BLUE
            strip2[i] = BLUE

    strip1.write()
    strip2.write()

def update_lcd():

    if lcd:
        lcd.clear()
        lcd.putstr("B:" + str(16 - position) + " R:" + str(position))

def wait_dice():

    led_dice.on()

    while takki_dice.value() == 1:
        sleep_ms(10)

    sleep_ms(50)

    while takki_dice.value() == 0:
        sleep_ms(10)

    led_dice.off()

def dice_anim(color, target):

    delay = 12
    current = 0

    total_steps = (NUM_RING * 2) + target

    for step in range(total_steps):

        for i in range(NUM_RING):
            ring[i] = OFF

        ring[current] = color
        ring.write()

        sleep_ms(delay)

        #slow wind down near end
        if step > total_steps - 20:
            delay += 4
        elif step > total_steps - 10:
            delay += 6

        current += 1

        if current >= NUM_RING:
            current = 0

    for i in range(NUM_RING):
        ring[i] = OFF

    ring[target] = YELLOW
    ring.write()

def show_score(score):

    for i in range(NUM_RING):
        ring[i] = OFF

    if score == 1:
        leds = SCORE_1

    elif score == 2:
        leds = SCORE_2

    else:
        leds = SCORE_3

    for i in leds:
        ring[i] = YELLOW

    ring.write()


clear_all()

startup_anim()

update_rope()

for i in range(NUM_RING):
    ring[i] = YELLOW

ring.write()

if lcd:
    lcd.putstr("Press dice!")

wait_dice()

if lcd:
    lcd.clear()
    lcd.putstr("Start")

sleep_ms(1000)


while game_on:

    blue_choice = randint(1, 2)
    red_choice = randint(1, 2)

    led_blue1.off()
    led_blue2.off()
    led_red1.off()
    led_red2.off()

    if blue_choice == 1:
        led_blue1.on()
    else:
        led_blue2.on()

    if red_choice == 1:
        led_red1.on()
    else:
        led_red2.on()

    hit = False
    winner = ""

    while not hit:

        if blue_choice == 1 and not takki_blue1.value():
            winner = "blue"
            hit = True

        if blue_choice == 2 and not takki_blue2.value():
            winner = "blue"
            hit = True

        if red_choice == 1 and not takki_red1.value():
            winner = "red"
            hit = True

        if red_choice == 2 and not takki_red2.value():
            winner = "red"
            hit = True

        sleep_ms(5)

    led_blue1.off()
    led_blue2.off()
    led_red1.off()
    led_red2.off()

    color = BLUE if winner == "blue" else RED

    wait_dice()

    roll = randint(1, 100)

    if roll <= 50:
        score = 1
        target = SCORE_1[randint(0, len(SCORE_1) - 1)]

    elif roll <= 80:
        score = 2
        target = SCORE_2[randint(0, len(SCORE_2) - 1)]

    else:
        score = 3
        target = SCORE_3[randint(0, len(SCORE_3) - 1)]

    dice_anim(color, target)

    show_score(score)

    if winner == "blue":
        position -= score
    else:
        position += score

    if position < 0:
        position = 0

    if position > 16:
        position = 16

    update_rope()
    update_lcd()

    if position == 0 or position == 16:
        game_on = False
    else:
        sleep_ms(300)

        delay_time = randint(4, 6)
        sleep_ms(delay_time * 1000)

winner_color = BLUE if position == 16 else RED

victory_anim(winner_color)

clear_all()

if lcd:
    lcd.clear()
    lcd.putstr("Game over")

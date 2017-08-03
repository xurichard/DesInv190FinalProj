from Tkinter import *
import RPi.GPIO as GPIO
import time
import datetime

# Need the latest version of GPIO
# $ sudo apt-get update
# $ sudo apt-get dist-upgrade

test = True
if test:
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(18, GPIO.OUT)
	pwm = GPIO.PWM(18, 100) #gnd and pin 18
	pwm.start(5)

class VisualApp:

    def __init__(self, master):
        frame = Frame(master)
        frame.pack()
        scale = Scale(frame, from_=0, to=180,
              orient=HORIZONTAL, command=self.update)
        scale.grid(row=0)

    def update(self, angle):
        duty = float(angle) / 10.0 + 2.5
        pwm.ChangeDutyCycle(duty)

class Timer:

	def __init__(self):
		self.times = [] #filled with datetimes

	def add(time):
		if type(time) == datetime:
			self.times.append(time)

	def check():
		current = datetime.datetime.now()
		for time in self.times:
			if (current-time).total_seconds()/60 <= 900: #check if it's within 15 minutes of time
				return True
		return False

class Dispenser:

	def __init__(self, pin=18, angle):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pin, GPIO.OUT)
		self.pwm = GPIO.PWM(18, 100)
		self.angle = angle
		self.pin = pin

	def dispense(slot, time):
		self.pwm.start(slot*angle) #slot/total_slots
		time.sleep(5) #wait for 5 seconds while dispensing
		self.pwm.stop()


class alarm():

	def __init__(self, pin):
		self.pin = pin
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.pin, GPIO.OUT)

	def buzz(self, pitch, duration):
		if(pitch==0):
			time.sleep(duration)
			return
		period = 1.0 / pitch
		delay = period / 2
		cycles = int(duration * pitch)

		for i in range(cycles):
			GPIO.output(self.buzzer_pin, True)
			time.sleep(delay)
			GPIO.output(self.buzzer_pin, False)
			time.sleep(delay)

	def play(self):
		pitches=[262,294,330,349,392,440,494,523,587,659,698,784,880,988,1047]
		duration=0.1
		for p in pitches:
			self.buzz(p, duration)
			time.sleep(duration *0.5)
		for p in reversed(pitches):
			self.buzz(p, duration)
			time.sleep(duration *0.5)


def main():


if __name__ == "__main__":
    if test:
		root = Tk()
		root.wm_title('Servo Control')
		app = VisualApp(root)
		root.geometry("200x50+0+0")
		root.mainloop()
	else:
		main()
























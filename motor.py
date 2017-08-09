from Tkinter import *
from twilio.rest import Client

import RPi.GPIO as GPIO
import time
import datetime
import schedule
import urllib2

# Need the latest version of GPIO
# $ sudo apt-get update
# $ sudo apt-get dist-upgrade
# https://github.com/dbader/schedule
# Find these values at https://twilio.com/user/account
account_sid = "ACee7629d3b852047940e7667b3df719a9"
auth_token = "0b8a98fc45556026f66922e11f5484f0"
client = Client(account_sid, auth_token)

def send_sms():
	client.api.account.messages.create(to="+14256236872", from_="+14142400316", body="Remember to take your medicine!")

GPIO.setwarnings(False)

test = False
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
        duty = float(angle) / 180 * 100 + 5
        pwm.ChangeDutyCycle(duty)

class Timer:

	def __init__(self):
		self.times = [] #filled with datetimes
		print("timer set up")

	def add(self, time):
		if type(time) == datetime:
			self.times.append(time)
		self.times.sort()

	def check(self):
		current = datetime.datetime.now()
		for time in self.times:
			if (current-time).total_seconds()/60 <= 900: #check if it's within 15 minutes of time
				return self.times.index(time)
		return None

	def num_to_time(self, doseNum):
		return self.times[doseNum]

	def time_to_num(self, doseTime):
		return self.times.index(doseTime)

	# def betweenTimes(self):
	# 	current = datetime.current()
	# 	after = None
	# 	for i in range(len(self.times)):
	# 		if current < self.times[i]:
	# 			after = i
	# 			break
	# 	if after == None: #past all time
	# 		return (self.times[len(self.times)-1], self.times[after])
	# 	if after == 0:
	# 		return (None, self.times[after])
	# 	return (self.times[i-1], self.times[i])

	# def beforeTime(self):
	# 	current = datetime.current()
	# 	for i in range(len(self.times)-1):
	# 		if current > self.times[i] and current < self.times[i+1]:
	# 			return self.times[i]
	# 	return None #should never hit

	# def nextTime(self):
	# 	current = datetime.current()
	# 	for i in range(len(self.times)-1):
	# 		if current > self.times[i] and current < self.times[i+1]:
	# 			return self.times[i+1]
	# 	return None

	def betweenTimes(self, time=datetime.datetime.now()):
		after = (None, None)
		before = (None, None)
		for i in range(len(self.times)):
			if time > self.times[i]:
				before = after
				after = (i, self.times[i])
			else:
				return (before, after)
		return (after, (None, None))
				


# Class for interfacing with motor to dispense
class Dispenser:

	def __init__(self, pin=18, angle=55):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pin, GPIO.OUT)
		self.pwm = GPIO.PWM(18, 100)
		self.angle = angle
		self.pin = pin

	def dispense(slot):
		self.pwm.start(slot*angle) #slot/total_slots
		time.sleep(5) #wait for 5 seconds while dispensing
		self.pwm.stop()

# Class for interfacing with the piezoelectric buzzer
class Alarm:

	def __init__(self, pin=17):
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
			GPIO.output(self.pin, True)
			time.sleep(delay)
			GPIO.output(self.pin, False)
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

# Interrupt for button press
# Constant poll for time

class Controller:

	def __init__(self, alarmPin, motorPin, rotationAngle):
		self.alarm = Alarm(alarmPin)
		self.dispeser = Dispenser(motorPin, rotationAngle)
		self.timer = Timer()
		self.doseNum = 1

	# Once the button is pressed, we have to check the time whether or not to dispense the pill or not
	def dispensePill(self):
		print "Tried to dispense"
		if self.timer.check():
			self.dispenser.dispense(self.doseNum)
			self.doseNum += 1

	# If it's within 15 minutes of taking your dosage (the 15 minutes after)
	# buzz the piezo buzzer
	def reminder(self):
		now = datetime.datetime.now()
		before, after = self.timer.betweenTimes(now)
		if (now - after[1]).total_seconds()/60 < 15:
			self.alarm.play()
			# urllib2.urlopen("http://idd190-xurichard.c9users.io:8080/messaging/sms").read()
			send_sms()

	# Timer gets setup in setup only
	def setup(self):
		GPIO.setmode(GPIO.BCM)

		GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #button pin

		GPIO.add_event_detect(27, GPIO.BOTH, callback=self.dispensePill, bouncetime=200)
		schedule.every().minute.do(self.reminder)

def main():
	GPIO.cleanup()

	# buttonPin = 27
	# motorPin = 18
	# alarmPin = 17
	# rotationAngle = 55

	# controller = Controller(alarmPin, motorPin, rotationAngle)

	# controller.timer.add(datetime.datetime.now() + datetime.timedelta(minutes=1)) # test
	# controller.setup()

	# GPIO.setup(buttonPin, GPIO.IN)
	# GPIO.add_event_detect(buttonPin, GPIO.BOTH, callback=controller.dispensePill)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.add_event_detect(27, GPIO.BOTH, callback=temp, bouncetime=200)

	while(True):
		try:
# do any other processing, while waiting for the edge detection
			sleep(1) # sleep 1 sec
		finally:
			gpio.cleanup()
def temp():
	print "hi"

if __name__ == "__main__":
	if test:
		root = Tk()
		root.wm_title('Servo Control')
		app = VisualApp(root)
		root.geometry("200x50+0+0")
		root.mainloop()
	else:
		main()
























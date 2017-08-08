from Tkinter import *
import RPi.GPIO as GPIO
import time
import datetime
import schedule

# Need the latest version of GPIO
# $ sudo apt-get update
# $ sudo apt-get dist-upgrade
# https://github.com/dbader/schedule

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

	def betweenTimes(self, time=datetime.current()):
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
		if self.timer.check():
			self.dispenser.dispense(self.doseNum)
			self.doseNum += 1

	# If it's within 15 minutes of taking your dosage (the 15 minutes after)
	# buzz the piezo buzzer
	def reminder(self):
		now = datetime.current()
		before, after = self.timer.betweenTimes(now)
		if (now - after[1]).total_seconds()/60 < 15:
			self.buzzer.play()

	# Timer gets setup in setup only
	def setup(self):
		GPIO.add_event_detect(buttonPin, GPIO.BOTH, callback=dispensePill)
		schedule.every().minute.do(self.reminder)

def main():
	buttonPin = 1
	motorPin = 18

	timer.add(datetime.current + datetime.timedelta(minutes=1)) # test
	GPIO.add_event_detect(buttonPin, GPIO.BOTH, callback=dispensePill)



if __name__ == "__main__":
	if test:
		root = Tk()
		root.wm_title('Servo Control')
		app = VisualApp(root)
		root.geometry("200x50+0+0")
		root.mainloop()
	else:
		main()
























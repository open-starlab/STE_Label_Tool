

class Event:
# Event(tmp_team, tmp_label, tmp_period, tmp_minute, tmp_second, tmp_x_coord, tmp_y_coord))
	def __init__(self, frame, team, event, minute, second, x_coord, y_coord, position):
		self.team = team
		self.event = event
		self.minute = str(minute)
		self.second = str(second)
		self.x_coord = x_coord
		self.y_coord = y_coord
		self.position = position
		self.time = str(self.minute).zfill(2) + ":" + str(self.second.split(".")[0]).zfill(2) + "." + str(self.second.split(".")[1]).zfill(2)
		self.frame = str(frame)

	def to_text(self):
		return str(self.frame) + " || " + str(self.event) + " - " + str(self.team)  + " - " + str(self.x_coord) + " - " + str(self.y_coord) 

	def __lt__(self, other):
		return self.position < other.position

def ms_to_time(position):
	minutes = int(position//1000)//60
	seconds = (position//1000)%60
	ms = position%1000
	return str(minutes).zfill(2), f"{str(seconds).zfill(2)}.{str(ms).zfill(2)}"
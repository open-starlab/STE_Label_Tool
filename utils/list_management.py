from utils.event_class import Event
import json
import os
import pdb
import pandas as pd

class ListManager:

	def __init__(self):

		self.event_list = list()

	def create_list_from_csv(self, path):

		self.event_list.clear()
		self.event_list = self.read_csv(path)
		if self.event_list != []:
			self.sort_list()

	def create_text_list(self):

		list_text = list()
		for event in self.event_list:
			list_text.append(event.to_text())

		return list_text

	def delete_event(self, index):

		self.event_list.pop(index)
		self.sort_list()

	def add_event(self, event):

		self.event_list.append(event)
		self.sort_list()

	def sort_list(self):

		position_list = list()
		for event in self.event_list:
			position = event.position
			position_list.append(position)

		self.event_list = [x for _,x in sorted(zip(position_list,self.event_list))]

		self.event_list.reverse()

	def read_csv(self, path):
		
		event_list = list()
		data = pd.read_csv(path)
		for i in range(len(data)):
			event_i = data.iloc[i]
			tmp_team = event_i["team"]
			tmp_label = event_i["event"]
			tmp_minute = event_i["minute"]
			tmp_second = event_i["second"]
			tmp_x_coord = event_i["x"]
			tmp_y_coord = event_i["y"]
			tmp_position = event_i["video_ms"]	
			tmp_frame = event_i["frame"]
			# print(tmp_team, tmp_label, tmp_minute, tmp_second, tmp_x_coord, tmp_y_coord, tmp_position)
			event_list.append(Event(tmp_frame, tmp_team, tmp_label, tmp_minute, tmp_second, tmp_x_coord, tmp_y_coord, tmp_position))
		return event_list

	def save_file(self, path, half):
		if self.event_list:
			annotations = []
			for event in self.event_list:
				annotations.append([
					event.frame,
					event.team,
					event.event,
					event.minute,
					event.second,
					event.x_coord,
					event.y_coord,
					event.position,
				])

			df = pd.DataFrame(
				annotations,
				columns=['frame', 'team', 'event', 'minute', 'second', 'x', 'y', 'video_ms']
			)
		else:
			df = pd.DataFrame(
				columns=['frame', 'team', 'event', 'minute', 'second', 'x', 'y', 'video_ms']
			)
		df['frame'] = df['frame'].astype(int)
		df = df.sort_values(by=['frame'])
		df['frame'] = df['frame'].astype(str)
		df.to_csv(path, index=False)

		

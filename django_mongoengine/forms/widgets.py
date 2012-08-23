from django.forms.widgets import TextInput, MultiWidget
from django.utils.safestring import mark_safe

import pdb

class Dictionary(MultiWidget):
	"""
	A widget representing a dictionary field
	"""

	def __init__(self, keys, min_length, attrs=None):
		#pdb.set_trace()
		#have a politic here : if widgets, then check if value pairing name/value
		# if no widget, only one row to begin (or if attribute min_length ?)
		widget_object = []
		if keys:
			for k in keys:
				widget_object.append(Pair(key=k,attrs=attrs))
		else:
			for i in range(min_length):
				widget_object.append(Pair(attrs=attrs))
		self.attrs = attrs
		super(Dictionary, self).__init__(widget_object,attrs)

	#TODO implement the render method : take a dict as value and display a list of inputs ?
	#	  check that WHERE the dict is passed
	#TODO implement the value_from_datadict method if needed : it gets data from POST
	#TODO : get the value from the different widgets with decompress
	def decompress(self, value):
		#pdb.set_trace()
		if value and isinstance(value,dict):
			#we return a list of tuples
			value = value.items()
			value.sort()
			#if there are not enough pairs to render the widget, we need to update it, and add pairs
			delta = len(value) - len(self.widgets)
			if delta > 0:
				self.update_widgets(value[1:delta+1])
			return value
		else:
			return []
	def render(self, name, value, attrs=None):
		#pdb.set_trace()
		if not isinstance(value,list):
			value = self.decompress(value)
		if self.is_localized:
			for widget in self.widgets:
				widget.is_localized = self.is_localized
		output = []
		final_attrs = self.build_attrs(attrs)
		id_ = final_attrs.get('id',None)
		for i, widget in enumerate(self.widgets):
			try:
				widget_value = value[i]
			except IndexError:
				widget_value = None
			if id_:
				final_attrs = dict(final_attrs, id='%s_%s_pair' % (id_, i))
			output.append(widget.render(name + '_%s_pair' % i, widget_value, final_attrs))
		return mark_safe(self.format_output(output))

	def value_from_datadict(self, data, files, name):
		return [widget.value_from_datadict(data, files, name + '_%s_pair' % i) for i, widget in enumerate(self.widgets)]

	#markup to be added (how?)
	def format_output(self, rendered_widgets):
		#pdb.set_trace()
		return '<ul>'+ ''.join(rendered_widgets) +'</ul>'

	def update_widgets(self,keys=1):
		for k in keys:
			self.widgets.append(Pair(key=k, attrs=self.attrs))

class Pair(MultiWidget):
	"""
	A widget representing a key-value pair in a dictionary
	"""

	#default for a pair
	key_type = TextInput
	value_type = TextInput

	def __init__(self, key=None, attrs=None):
		widgets = [self.key_type(),self.value_type()]
		super(Pair, self).__init__(widgets,attrs)

	#this method should be overwritten by subclasses
	def decompress(self, value):
		if value is not None:
			return list(value)
		else:
			return ['','']

	def render(self, name, value, attrs=None):
		if self.is_localized:
			for widget in self.widgets:
				widgets.is_localized = self.is_localized
		if not isinstance(value,list):
			value = self.decompress(value)
		output = []
		final_attrs = self.build_attrs(attrs)
		id_ = final_attrs.get('id',None)
		for i, widget in enumerate(self.widgets):
			try:
				widget_value = value[i]
			except IndexError:
				widget_value = None
			if id_:
				final_attrs = dict(final_attrs, id='%s_%s' % (id_, i))
			output.append(widget.render(name + '_%s' % i, widget_value, final_attrs))
		return mark_safe(self.format_output(output))

	def value_from_datadict(self, data, files, name):
		return [widget.value_from_datadict(data, files, name + '_%s' % i) for i, widget in enumerate(self.widgets)]

	def format_output(self, rendered_widgets):
		#pdb.set_trace()
		return '<li>'+ ' : '.join(rendered_widgets) +'</li>\n'

class SubDictionary(Pair):
	"""
	A widget representing a key-value pair in a dictionary, where value is a dictionary
	"""

	key_type = TextInput
	value_type = Dictionary
	suffix = 'subdict'
	no_schema = False

	def __init__(self, schema={'key':'value'}, no_schema=False, attrs=None):
		self.no_schema = no_schema
		super(SubDictionary, self).__init__(attrs, schema=schema, no_schema=no_schema)

	#TODO
	#def decompress(self,value):
		#pdb.set_trace()
		#pass

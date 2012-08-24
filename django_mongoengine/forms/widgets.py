from django.forms.widgets import TextInput, MultiWidget, Media
from django.utils.safestring import mark_safe

import re
import pdb

#the list of JavaScript files to insert to render any Dictionary widget
MEDIAS = ('jquery-1.8.0.min.js','dict.js')

class Dictionary(MultiWidget):
	"""
	A widget representing a dictionary field
	"""

	#we shouldn't pass only the keys but the whole default dictionary,
	#because in this case, we would be able to rebuild it using SubDictionary
	def __init__(self, schema=None, no_schema=1, attrs=None):
		
		# schema -- A dictionary representing the future schema of
		#			the Dictionary widget. It is responsible for the
		#			creation of subwidgets.
		# no_schema -- An integer that can take 3 values : 0,1,2.
		#			   0 means that no schema was passed.
		#			   1 means that the schema passed was the default
		#			   one. This is the default value.
		#			   2 means that the schema passed was given
		#			   by a parent widget, and that it actually
		#			   represent data for rendering.
		#			   3 means that the schema was rebuilt after
		#			   retrieving form data.

		#pdb.set_trace()

		self.no_schema = no_schema
		widget_object = []
		if isinstance(schema,dict) and self.no_schema > 0:
			for key in schema:
				if isinstance(schema[key],dict):
					widget_object.append(SubDictionary(schema=schema[key],attrs=attrs))
				else:
					widget_object.append(Pair(attrs=attrs))
		else:
			widget_object.append(Pair(attrs=attrs))
			# if subtype == 'Pair':
			# 	direct_children[j] = Pair
			# elif subtype == 'SubDictionary':
			# 	direct_children[j] = SubDictionary

		
		# if keys is not None and keys:
		# 	for k in keys:
		# 		widget_object.append(subtypes(attrs=attrs))
		# else:

		#TODO : give the correct subtypes here : that where we go deeep
		# correct_subtypes = {'key':'value'}
		# for subtype in schema:
		# 	widget_object.append(subtype(schema=correct_subtypes, attrs=attrs))
		super(Dictionary, self).__init__(widget_object,attrs)

	def decompress(self, value):
		#pdb.set_trace()
		if value and isinstance(value,dict):
			#'sort' a dict... recursively

			value = value.items()

			#if there are not enough pairs to render the widget, we need to update it, and add pairs
			delta = len(value) - len(self.widgets)
			#if the schema in place wasn't passed by a parent widget, we need to rebuild it
			if self.no_schema < 2:
				self.update_widgets(value,erase=True)
			else:
				pass
			# 	if delta > 0:
			# 		self.update_widgets(value[1:delta+1])
			return value
		else:
			return []

	def render(self, name, value, attrs=None):
		#pdb.set_trace()
		positions = range(len(value))
		if not isinstance(value,list):
			(value, positions) = self.decompress(value)
		if self.is_localized:
			for widget in self.widgets:
				widget.is_localized = self.is_localized
		output = []
		final_attrs = self.build_attrs(attrs)
		id_ = final_attrs.get('id')
		for i, widget in enumerate(self.widgets):
			try:
				widget_value = value[positions[i]]
			except IndexError:
				widget_value = None
			suffix = widget.suffix
			if id_:
				final_attrs = dict(final_attrs, id='%s_%s_%s' % (id_, i, suffix))
			output.append(widget.render(name + '_%s_%s' % (i, suffix), widget_value, final_attrs))
		#pdb.set_trace()
		return mark_safe(self.format_output(name, output))

	def value_from_datadict(self, data, files, name):
		# I think the best solution here is to start from scratch, i mean :
		# 	- erase every widget ;
		#	- create the new ones from the data dictionary
		# It would take into account every modification on the structure, and
		# make form repopulation automatic

		#pdb.set_trace()
		data_keys = data.keys()
		self.widgets = []
		html_indexes = []

		for data_key in data_keys:
			match = re.match(name+'_(\d+)_pair_0',data_key)
			if match is not None:
				self.widgets.append(Pair(attrs=self.attrs))
				html_indexes.append(match.group(1))
			else:
				match = re.match(name+'_(\d+)_subdict_0',data_key)
				if match is not None:
						self.widgets.append(SubDictionary(no_schema=0, attrs=self.attrs))
						html_indexes.append(match.group(1))
		return [widget.value_from_datadict(data, files, name + '_%s_%s' % (html_indexes[i],widget.suffix)) for i, widget in enumerate(self.widgets)]

	def format_output(self, name, rendered_widgets):
		#pdb.set_trace()
		return '<ul id="id_%s" class="dictionary">\n' % (self.id_for_label(name)) + ''.join(rendered_widgets) +'</ul>\n'+ \
			   '<span id="add_id_%s" class="add_dictionary">Add field</span> - ' % (self.id_for_label(name)) + \
			   '<span id="add_sub_id_%s" class="add_sub_dictionary">Add subdictionary</span>' % (self.id_for_label(name))

	def update_widgets(self,keys,erase=False):
		#pdb.set_trace()
		if erase:
			self.widgets = []
		for k in keys:
			if (isinstance(k[1],dict)):
				self.widgets.append(SubDictionary(schema=k[1], no_schema=2, attrs=self.attrs))
			else:
				self.widgets.append(Pair(attrs=self.attrs))

	def _get_media(self):
		"""
		Mimic the MultiWidget '_get_media' method, adding other media
		"""
		media = Media(js=MEDIAS)
		for w in self.widgets:
			media = media + w.media
		return media
	media = property(_get_media)

class Pair(MultiWidget):
	"""
	A widget representing a key-value pair in a dictionary
	"""

	#default for a pair
	key_type = TextInput
	value_type = TextInput
	suffix = 'pair'

	def __init__(self, attrs=None, **kwargs):
		if self.value_type == TextInput:
			widgets = [self.key_type(),self.value_type()]
		elif self.value_type == Dictionary:
			widgets = [self.key_type(),self.value_type(**kwargs)]
		super(Pair, self).__init__(widgets,attrs)

	#this method should be overwritten by subclasses
	def decompress(self, value):
		#pdb.set_trace()
		if value is not None:
			return list(value)
		else:
			return ['','']

	def render(self, name, value, attrs=None):
		#pdb.set_trace()
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
		#pdb.set_trace()
		## TO CHECK FOR SUBDICT
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

	def __init__(self, schema={'key':'value'}, no_schema=1, attrs=None):
		super(SubDictionary, self).__init__(attrs, schema=schema, no_schema=no_schema)

	def decompress(self,value):
		if value is not None:
			return list(value)
		else:
			return ['',{}]

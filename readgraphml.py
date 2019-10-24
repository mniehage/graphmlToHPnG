import lxml.etree as et
from xml.dom import minidom
import logging
import argparse
import os

# define flags
parser = argparse.ArgumentParser(description='Translation of graphml to xml (for HYPEG and HPnmG)')
parser.add_argument('-i', '--infile', metavar='path', help='Path to *.graphml file',
					required=True)
parser.add_argument('-o', '--outfile', metavar='path',
					help='Path to generated xml file, if not defined same folder as infile')
parser.add_argument('-l', '--logfile', metavar='path',
					help='Path where logfile will get created, if not defined same folder as outfile')

arg = parser.parse_args()
tree = et.parse(arg.infile)
if arg.outfile is None:
	outfile = os.path.splitext(arg.infile)[0] + '.xml'
	print(outfile)
else:
	outfile = arg.outfile

if arg.logfile is None:
	logfile = os.path.splitext(outfile)[0] + '.log'
	print(logfile)
else:
	logfile = arg.logfile

# initialize logfile
logging.basicConfig(filename=logfile, level=logging.DEBUG,
					filemode='w')
logging.info('Logfile contains all information that needs to be dealt with manually')
logging.info('Discrete marking not implemented yet')


def handle_circle_ids():
	num_circles = len(circles)
	# print('number circles', num_circles)
	if num_circles == 2:
		component_ids[svg_resource.get("id")] = 'continuousPlace'
	elif num_circles == 1:
		component_ids[svg_resource.get("id")] = 'discretePlace'


def handle_rect_ids():
	num_rects = len(rects)
	# print('number rects', num_rects)

	if num_rects == 2:
		# inner rectangular filled black is dynamic transition
		if rects[1].attributes['style'].value[0] == 'b':
			component_ids[svg_resource.get("id")] = 'dynamicContinuousTransition'
		else:
			component_ids[svg_resource.get("id")] = 'continuousTransition'
	elif num_rects == 1:
		if rects[0].attributes['style'].value[5] == 'b':
			component_ids[svg_resource.get("id")] = 'immediateTransition'
		elif rects[0].attributes['style'].value[5] == 'g':
			component_ids[svg_resource.get("id")] = 'deterministicTransition'
		else:
			component_ids[svg_resource.get("id")] = 'generalTransition'


def interpret_label_continuous_place():
	# counter to check if just one id got detected
	number_ids = 0
	found_level = False
	found_capacity = False
	found_quantum = False
	for label in svg_node.findall('y:NodeLabel', data.nsmap):
		if label.text is not None:
			text = label.text
			text.replace(" ", "")
			level_pos = text.find('level')
			capacity_pos = text.find('capacity')
			quantum_pos = text.find('quantum')
			if level_pos != -1:
				found_level = True
				place.set('level', text[text.find('=', level_pos) + 1:])
			if capacity_pos != -1:
				found_capacity = True
				if 'inf' in text[text.find('=', capacity_pos) + 1:]:
					place.set('capacity', '0')
					place.set('infiniteCapacity', '1')
				else:
					place.set('capacity', text[text.find('=', capacity_pos) + 1:])
					place.set('infiniteCapacity', '0')
			if quantum_pos != -1:
				found_quantum = True
				place.set('quantum', text[text.find('=', quantum_pos) + 1:])
			if (capacity_pos and level_pos) is -1:
				place.set('id', text)
				number_ids += 1
	if number_ids > 1:
		logging.error('%s entries got interpreted as id of one continuous places, check xml, last id set is %s',
					  number_ids, place.get('id'))
	elif number_ids == 0:
		logging.error('No id for continuous place found')
	if not found_capacity:
		# assume infinite capacity if none is annotated
		place.set('capacity', '0')
		place.set('infiniteCapacity', '1')
		logging.info('No capacity for continuous place %s found, assumed infinite capacity', place.get('id'))
	if not found_level:
		logging.error('No fluid level for continuous place %s found, assumed 0', place.get('id'))
		place.set('level', '0')
	if not found_quantum:
		logging.info('Set quantum for continuous place %s to 1', place.get('id'))
		place.set('quantum', '1')


def interpret_label_discrete_place():
	# counter to check if just one id got detected
	number_ids = 0
	place.set('marking', '0')
	for label in svg_node.findall('y:NodeLabel', data.nsmap):
		if label.text is not None:
			text = label.text
			text.replace(" ", "")
			if text != '':
				print('!' + text + '!')
				place.set('id', text)
				number_ids += 1
	if number_ids > 1:
		logging.error('%s entries got interpreted as id of one discrete place, check xml, last id set is %s',
					  number_ids, place.get('id'))
	elif number_ids == 0:
		logging.error('No id for discrete place found')
	logging.info('Marking of discrete place %s set to 0, please change manually in xml', place.get('id'))


def interpret_label_continuous_transition():
	# counter to check if just one id got detected
	number_ids = 0
	found_rate = False
	for label in svg_node.findall('y:NodeLabel', data.nsmap):
		if label.text is not None:
			text = label.text
			text.replace(" ", "")
			rate_pos = text.find('rate')
			if rate_pos != -1:
				found_rate = True
				transition.set('rate', text[text.find('=', rate_pos) + 1:])
			if rate_pos is -1:
				transition.set('id', text)
				number_ids += 1
	if number_ids > 1:
		logging.error('%s entries got interpreted as id of one continuous place, check xml, last id set is %s',
					  number_ids, transition.get('id'))
	elif number_ids == 0:
		logging.error('No id for continuous transition found')
	if not found_rate:
		logging.error('No rate for continuous transition %s found, set to 1', transition.get('id'))
		transition.set('rate', '1')


# TODO noch nicht fertig, was ist sinnvoll?
def interpret_label_dynamic_continuous_transition():
	# counter to check if just one id got detected
	number_ids = 0
	found_rate = False
	for label in svg_node.findall('y:NodeLabel', data.nsmap):
		if label.text is not None:
			text = label.text
			text.replace(" ", "")
			rate_pos = text.find('rate')
			if rate_pos != -1:
				found_rate = True
				transition.set('rate', text[text.find('=', rate_pos) + 1:])
			if rate_pos is -1:
				transition.set('id', text)
				number_ids += 1
	if number_ids > 1:
		logging.error('%s entries got interpreted as id of one continuous place, check xml, last id set is %s',
					  number_ids, transition.get('id'))
	elif number_ids == 0:
		logging.error('No id for continuous transition found')
	if not found_rate:
		logging.error('No rate for dynamic continuous transition %s found, set to 1', transition.get('id'))
		transition.set('rate', '1')


def interpret_label_deterministic_transition():
	# counter to check if just one id got detected
	number_ids = 0
	found_time = False
	found_priority = False
	found_weight = False
	for label in svg_node.findall('y:NodeLabel', data.nsmap):
		if label.text is not None:
			text = label.text
			text.replace(" ", "")
			time_pos = text.find('t=')
			priority_pos = text.find('prio')
			weight_pos = text.find('weight')
			if time_pos != -1:
				found_time = True
				transition.set('time', text[text.find('=', time_pos) + 1:])
			if priority_pos != -1:
				found_priority = True
				transition.set('priority', text[text.find('=', priority_pos) + 1:])
			if weight_pos != -1:
				found_weight = True
				transition.set('weight', text[text.find('=', weight_pos) + 1:])
			if (time_pos and priority_pos and weight_pos) is -1:
				transition.set('id', text)
				number_ids += 1
	if number_ids > 1:
		logging.error('%s entries got interpreted as id of one deterministic transition, check xml, last id set is %s',
					  number_ids, transition.get('id'))
	elif number_ids == 0:
		logging.error('No id for deterministic transition found')
	if not found_time:
		logging.error('No time for deterministic transition %s found, set to 0', transition.get('id'))
		transition.set('time', '0')
	if not found_priority:
		logging.error('No priority for deterministic transition %s found, set to 0', transition.get('id'))
		transition.set('priority', '0')
	if not found_weight:
		logging.error('No weight for deterministic transition %s found, set to 1', transition.get('id'))
		transition.set('weight', '1')


def interpret_label_general_transition():
	# counter to check if just one id got detected
	number_ids = 0
	found_cdf = False
	found_priority = False
	found_weight = False
	found_policy = False
	for label in svg_node.findall('y:NodeLabel', data.nsmap):
		if label.text is not None:
			text = label.text
			text.replace(" ", "")
			cdf_pos = text.find('cdf')
			priority_pos = text.find('prio')
			weight_pos = text.find('weight')
			policy_pos = text.find('policy')
			if cdf_pos != -1:
				found_cdf = True
				identify_cdf(text, transition)
			if priority_pos != -1:
				found_priority = True
				transition.set('priority', text[text.find('=', priority_pos) + 1:])
			if weight_pos != -1:
				found_weight = True
				transition.set('weight', text[text.find('=', weight_pos) + 1:])
			if policy_pos != -1:
				found_policy = True
				transition.set('policy', text[text.find('=', policy_pos) + 1:])
			if (cdf_pos and priority_pos and weight_pos and policy_pos) is -1:
				transition.set('id', text)
				number_ids += 1
	if number_ids > 1:
		logging.error('%s entries got interpreted as id of one general transition, check xml, last id set is %s',
					  number_ids, transition.get('id'))
	elif number_ids == 0:
		logging.error('No id for general transition found')
	if not found_cdf:
		logging.error('No cdf for general transition %s found, set to exp', transition.get('id'))
		transition.set('cdf', 'exp')
	if not found_priority:
		logging.error('No priority for general transition %s found, set to 0', transition.get('id'))
		transition.set('priority', '0')
	if not found_weight:
		logging.error('No weight for general transition %s found, set to 1', transition.get('id'))
		transition.set('weight', '1')
	if not found_policy:
		logging.error('No policy for general transition %s found, set to resume', transition.get('id'))
		transition.set('policy', 'resume')


def interpret_label_immediate_transition():
	# counter to check if just one id got detected
	number_ids = 0
	found_priority = False
	found_weight = False
	for label in svg_node.findall('y:NodeLabel', data.nsmap):
		if label.text is not None:
			text = label.text
			text.replace(" ", "")
			priority_pos = text.find('prio')
			weight_pos = text.find('weight')
			if priority_pos != -1:
				found_priority = True
				transition.set('priority', text[text.find('=', priority_pos) + 1:])
			if weight_pos != -1:
				found_weight = True
				transition.set('weight', text[text.find('=', weight_pos) + 1:])
			if (priority_pos and weight_pos) is -1:
				transition.set('id', text)
				number_ids += 1
	if number_ids > 1:
		logging.error('%s entries got interpreted as id of one general transition, check xml, last id set is %s',
					  number_ids, transition.get('id'))
	elif number_ids == 0:
		logging.error('No id for general transition found')
	if not found_priority:
		logging.error('No priority for general transition %s found, set to 0', transition.get('id'))
		transition.set('priority', '0')
	if not found_weight:
		logging.error('No weight for general transition %s found, set to 1', transition.get('id'))
		transition.set('weight', '1')


def interpret_label_continuous_arc():
	# counter to check if just one id got detected
	not_interpreted_labels = 0
	found_share = False
	found_priority = False
	found_weight = False
	for label in svg_node.findall('y:GenericEdge/y:EdgeLabel', data.nsmap):
		if label.text is not None:
			text = label.text
			text.replace(" ", "")
			time_pos = text.find('share')
			priority_pos = text.find('prio')
			weight_pos = text.find('weight')
			if time_pos != -1:
				found_share = True
				arc.set('share', text[text.find('=', time_pos) + 1:])
			if priority_pos != -1:
				found_priority = True
				arc.set('priority', text[text.find('=', priority_pos) + 1:])
			if weight_pos != -1:
				found_weight = True
				arc.set('weight', text[text.find('=', weight_pos) + 1:])
			if (time_pos and priority_pos and weight_pos) is -1:
				not_interpreted_labels += 1
	if not_interpreted_labels > 0:
		logging.error('%s labels of arc %s got not interpreted, check xml', not_interpreted_labels,
					  source + 'to' + target)
	if not found_share:
		logging.error('No share for continuous arc  %s found, set to 1', source + 'to' + target)
		arc.set('share', '1')
	if not found_priority:
		logging.error('No priority for continuous arc %s found, set to 0', source + 'to' + target)
		arc.set('priority', '0')
	if not found_weight:
		logging.error('No weight for continuous arc %s found, set to 1', source + 'to' + target)
		arc.set('weight', '1')


def interpret_label_polyline_arc():
	# counter to check if just one id got detected
	not_interpreted_labels = 0
	found_weight = False
	for label in data.findall('y:PolyLineEdge/y:EdgeLabel', data.nsmap):
		if label.text is not None:
			text = label.text
			text.replace(" ", "")
			weight_pos = text.find('weight')
			if weight_pos != -1:
				found_weight = True
				arc.set('weight', text[text.find('=', weight_pos) + 1:])
			if weight_pos is -1:
				not_interpreted_labels += 1
	if not_interpreted_labels > 0:
		logging.error('%s labels of arc %s got not interpreted, check xml', not_interpreted_labels,
					  source + 'to' + target)
	if not found_weight:
		logging.error('No weight for arc %s found, set to 1', source + 'to' + target)
		arc.set('weight', '1')


def identify_cdf(text, gen_transition):
	found_brackets = text.find('{')
	equal_pos = text.find('=')
	if found_brackets != -1:
		distribution = text[equal_pos + 1:found_brackets]
		if distribution == 'normal':
			mu = et.SubElement(gen_transition, 'parameter')
			mu.set('name', 'mu')
			sigma = et.SubElement(gen_transition, 'parameter')
			sigma.set('name', 'sigma')
			sem_pos = text.find(';', found_brackets)
			mu.set('value', text[found_brackets + 1:sem_pos])
			sigma.set('value', text[sem_pos + 1:text.find('}', sem_pos)])
			gen_transition.set('cdf', distribution)
		elif 'exp' in distribution:
			param = et.SubElement(gen_transition, 'parameter')
			param.set('name', 'lambda')
			param.set('value', text[found_brackets + 1:text.find('}', found_brackets)])
			gen_transition.set('cdf', 'exp')
		elif 'uni' in distribution:
			a = et.SubElement(gen_transition, 'parameter')
			a.set('name', 'a')
			b = et.SubElement(gen_transition, 'parameter')
			b.set('name', 'b')
			sem_pos = text.find(';', found_brackets)
			a.set('value', text[found_brackets + 1:sem_pos])
			b.set('value', text[sem_pos + 1:text.find('}', sem_pos)])
			gen_transition.set('cdf', 'uniform')
		elif 'folded' in distribution:
			mu = et.SubElement(gen_transition, 'parameter')
			mu.set('name', 'mu')
			sigma = et.SubElement(gen_transition, 'parameter')
			sigma.set('name', 'sigma')
			sem_pos = text.find(';', found_brackets)
			mu.set('value', text[found_brackets + 1:sem_pos])
			sigma.set('value', text[sem_pos + 1:text.find('}', sem_pos)])
			gen_transition.set('cdf', 'foldednormal')
		else:
			gen_transition.set('cdf', text[equal_pos + 1:])
			logging.error('Distribution of general transition %s did not get detected, please change xml manually',
						  gen_transition.get('id'))
	else:
		gen_transition.set('cdf', text[equal_pos + 1:])
		logging.error('No parameters of distribution of general transition detected, did you use "{"?')


graphml = {
	"graph": "{http://graphml.graphdrawing.org/xmlns}graph",
	"node": "{http://graphml.graphdrawing.org/xmlns}node",
	"edge": "{http://graphml.graphdrawing.org/xmlns}edge",
	"data": "{http://graphml.graphdrawing.org/xmlns}data",
	"label": "{http://graphml.graphdrawing.org/xmlns}data[@key='y:Fill']",
	"x": "{http://graphml.graphdrawing.org/xmlns}data/SVGNode/Geometry",
	"y": "{http://graphml.graphdrawing.org/xmlns}data[@key='y']",
	"size": "{http://graphml.graphdrawing.org/xmlns}data[@key='size']",
	"r": "{http://graphml.graphdrawing.org/xmlns}data[@key='r']",
	"g": "{http://graphml.graphdrawing.org/xmlns}data[@key='g']",
	"b": "{http://graphml.graphdrawing.org/xmlns}data[@key='b']",
	"weight": "{http://graphml.graphdrawing.org/xmlns}data[@key='weight']",
	"edgeid": "{http://graphml.graphdrawing.org/xmlns}data[@key='edgeid']",
	"d6": "{http://graphml.graphdrawing.org/xmlns}data[@key='d6']",
	"d7": "{http://graphml.graphdrawing.org/xmlns}data[@key='d7']",
	"d8": "{http://graphml.graphdrawing.org/xmlns}data[@key='d8']",
	"d10": "{http://graphml.graphdrawing.org/xmlns}data[@key='d10']"
}

graph = tree.find(graphml.get("graph"))
nodes = graph.findall(graphml.get("node"))
edges = graph.findall(graphml.get("edge"))

node_properties = []
component_ids = {}
# determine the ids in the graphml of the components
for component_image in tree.findall(graphml.get('data')):
	for svg_resource in component_image.findall('y:Resources/y:Resource', component_image.nsmap):
		svg_data = svg_resource.text
		svg = minidom.parseString(svg_data)
		items = svg.getElementsByTagName('svg')
		# items only 1 element

		# one circle discrete place, two continuous place
		circles = items[0].getElementsByTagName('circle')
		handle_circle_ids()

		# two rects dynamic and continuous transition, 1 other transitions
		rects = items[0].getElementsByTagName('rect')
		handle_rect_ids()

# print(component_ids)
xml_root = et.Element('HPnG')
xml_nodes = et.SubElement(xml_root, 'places')
xml_transitions = et.SubElement(xml_root, 'transitions')
xml_arcs = et.SubElement(xml_root, 'arcs')
# title = et.SubElement(xml_nodes, 'title')
# print(et.tostring(xmlroot, pretty_print=True))
node_id = {}
for node in nodes:
	attribs = {}
	# print(node.findall(graphml.get('x')))
	for data in node.findall(graphml.get('d6')):
		# key d6 contains relevant data

		if data.get("key") == "d6":
			for svg_node in data.findall('y:SVGNode', data.nsmap):
				# identify nodes
				for refid in svg_node.findall('y:SVGModel/y:SVGContent', data.nsmap):
					comp_id = refid.get('refid')
					comp_type = component_ids[refid.get('refid')]
					if 'Place' in comp_type:
						place = et.SubElement(xml_nodes, comp_type)
						if comp_type[0] is 'c':
							interpret_label_continuous_place()
						else:
							interpret_label_discrete_place()
						if place.get('id') is None:
							node_id[node.get('id')] = node.get('id')
						else:
							node_id[node.get('id')] = place.get('id')
					else:
						transition = et.SubElement(xml_transitions, comp_type)
						if comp_type[0] is 'c':
							interpret_label_continuous_transition()
						elif comp_type[0] is 'd':
							if comp_type[1] is 'y':
								interpret_label_dynamic_continuous_transition()
							else:
								interpret_label_deterministic_transition()
						elif comp_type[0] is 'g':
							interpret_label_general_transition()
						elif comp_type[0] is 'i':
							interpret_label_immediate_transition()
						else:
							logging.error("transition got not detected, type %s", comp_type)
						if transition.get('id') is None:
							node_id[node.get('id')] = node.get('id')
						else:
							node_id[node.get('id')] = transition.get('id')

# edges

for edge in edges:
	source = node_id[edge.get('source')]
	target = node_id[edge.get('target')]
	for data in edge.findall(graphml.get('d10')):
		if len(data.findall('y:GenericEdge', data.nsmap)) is not 0:
			arc = et.SubElement(xml_arcs, 'continuousArc')
			interpret_label_continuous_arc()
		else:
			arrows = data.findall('y:PolyLineEdge/y:Arrows', data.nsmap)
			arrow_source = arrows[0].get('source')
			arrow_target = arrows[0].get('target')
			if arrow_source == 'white_delta' and arrow_target == 'white_delta':
				# guard arc
				arc = et.SubElement(xml_arcs, 'guardArc')
				interpret_label_polyline_arc()
				arc.set('isInhibitor', '0')
			elif arrow_target == 'transparent_circle' and arrow_source == 'none':
				# inhibitor arc
				arc = et.SubElement(xml_arcs, 'guardArc')
				interpret_label_polyline_arc()
				arc.set('isInhibitor', '1')
			elif arrow_target == 'delta' and arrow_source == 'none':
				# discrete arc
				arc = et.SubElement(xml_arcs, 'discreteArc')
				interpret_label_polyline_arc()
			else:
				logging.error("arc got not detected, source %s, target %s, created arc not_detected", source, target)
				arc = et.SubElement(xml_arcs, 'not_detected')
		print(source)
		arc.set('fromNode', source)
		arc.set('toNode', target)
		arc.set('id', source + 'to' + target)

# sort nodes, transitions and edges in xml
for child in xml_root:
	child[:] = sorted(child, key=lambda x: x.tag)

# write xml to file
out = open(outfile, 'wb')
out.write(et.tostring(xml_root, pretty_print=True, xml_declaration=True))

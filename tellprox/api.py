import bottle_helpers as bh
from bottle import request

class API(object):
	def __init__(self, app, config):
		self.app = app
		self.config = config
		app.route('/<out_format:re:(?i)(xml|json)>/<ftype:path>/<func:path>',
			method = ['GET', 'POST'],
			callback = self.route_all)
		self.callbacks = {}
		self.allroutes = {}
		self.add_route('api', {
			'list': {
				'fn': self.output
			}
		})

	def add_route(self, key, funcs):
		for v in funcs.values():
			inputs = v.get('inputs', [])
			if not type(inputs) is list:
				inputs = [inputs]
			v['inputs'] = inputs
		self.allroutes[key] = funcs
		
	def route_all(self, out_format, ftype, func):
		if ftype in self.allroutes:
			funcs = self.allroutes[ftype]
			funcName = func.strip().lower()
			if funcName in funcs:
				if self.check_apikey():
					func = funcs[funcName]
					args = self.get_inputs(func['inputs'])
					resp = func['fn'](funcName, *args)
				else:
					resp = { 'error': 'key not valid' }
				return bh.format_response(resp, out_format, ftype, self.config['pretty_print'])
		bh.raise404()
	
	def get_inputs(self, args = []):
		return [bh.get_type(input['name'], input['type']) for input in args]
		
	def output(self, func):
		return {k : { kk : {'description': vv['fn'].__doc__, 'inputs': vv['inputs'] } for kk,vv in v.iteritems() }
			for k, v in self.allroutes.iteritems()}
		
	def check_apikey(self):
		if not self.config['apikey']:
			return True
		key = bh.get_string('key')
		return key == self.config['apikey']
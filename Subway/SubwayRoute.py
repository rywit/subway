class SubwayRoute:

	def __init__( self, route_id, short_name, long_name ):
		self.route_id = route_id
		self.short_name = short_name
		self.long_name = long_name

	def get_id(self):
		return self.route_id

	def get_short_name( self ):
		return self.short_name

	def get_long_name( self ):
		return self.long_name

	def __str__(self):
		return self.get_short_name()

	def __eq__(self, other):
		return self.get_id() == other.get_id()

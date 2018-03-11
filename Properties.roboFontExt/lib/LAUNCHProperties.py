try:
	from importlib import reload
except:
	pass

import Properties
reload(Properties)

Properties.ShowProperties()
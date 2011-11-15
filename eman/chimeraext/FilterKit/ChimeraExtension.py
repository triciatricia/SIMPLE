import chimera.extension
import threading
import os
import time

# -----------------------------------------------------------------------------
#
class Filter_EMO(chimera.extension.EMO):
	def name(self):
		return "Interactive Filter"

	def categories(self):
		"Return list of category names in which this extension belongs"
		return ["EMAN"]

	def description(self):
		"Return short description (appropriate for balloon help)"
		return 'Allows user to interactively filter volume data'

	def documentation(self):
		"Return full documention URL"
		return None

	def hasUI(self):
		"Return whether extension activation starts a UI"
		return 1

	def activate(self):
		"Activate extension and return an instance (if appropriate)"
		self.module('Filter').gui()

		return None

#print os
chimera.extension.manager.registerExtension(Filter_EMO(__file__))

class Colorizer_EMO(chimera.extension.EMO):
	def name(self):
		return "Isosurface Colorizer"

	def categories(self):
		"Return list of category names in which this extension belongs"
		return ["EMAN"]

	def description(self):
		"Return short description (appropriate for balloon help)"
		return 'Apply surface color variations to isosurfaces'

	def documentation(self):
		"Return full documention URL"
		return None

	def hasUI(self):
		"Return whether extension activation starts a UI"
		return 1

	def activate(self):
		"Activate extension and return an instance (if appropriate)"
		self.module('Colorizer').gui()

		return None

#print os
chimera.extension.manager.registerExtension(Colorizer_EMO(__file__))

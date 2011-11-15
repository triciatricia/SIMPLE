import chimera.extension
import threading
import os
import time

# -----------------------------------------------------------------------------
#
class ModelMemory_EMO(chimera.extension.EMO):
	def name(self):
		return "Model Memory"

	def categories(self):
		"Return list of category names in which this extension belongs"
		return ["EMAN"]

	def description(self):
		"Return short description (appropriate for balloon help)"
		return 'Records positions and orientations of models'

	def documentation(self):
		"Return full documention URL"
		return None

	def hasUI(self):
		"Return whether extension activation starts a UI"
		return 1

	def activate(self):
		"Activate extension and return an instance (if appropriate)"
		self.module('Memory').gui()

		return None

#print os
chimera.extension.manager.registerExtension(ModelMemory_EMO(__file__))

class Animator_EMO(chimera.extension.EMO):
	def name(self):
		return "EMANimator"

	def categories(self):
		"Return list of category names in which this extension belongs"
		return ["EMAN"]

	def description(self):
		"Return short description (appropriate for balloon help)"
		return 'An interface for making molecular animations'

	def documentation(self):
		"Return full documention URL"
		return None

	def hasUI(self):
		"Return whether extension activation starts a UI"
		return 1

	def activate(self):
		"Activate extension and return an instance (if appropriate)"
		self.module('Animator').gui()

		return None

#print os
chimera.extension.manager.registerExtension(Animator_EMO(__file__))

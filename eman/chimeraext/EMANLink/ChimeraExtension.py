import chimera.extension
import threading
import os
import time

# -----------------------------------------------------------------------------
#
class EMANLink_EMO(chimera.extension.EMO):
	def name(self):
		return "EMAN Link"
	
	def categories(self):
		"Return list of category names in which this extension belongs"
		return ["EMAN"]

	def description(self):
		"Return short description (appropriate for balloon help)"
		return 'EMAN interface class. This class allows EMAN to send commands to chimera and vice/versa'

	def documentation(self):
		"Return full documention URL"
		return None

	def hasUI(self):
		"Return whether extension activation starts a UI"
		return 0

	def activate(self):
		"Activate extension and return an instance (if appropriate)"
		self.thr=self.module().EMANThread()
		self.thr.start()
		return None

#print os
chimera.extension.manager.registerExtension(EMANLink_EMO(__file__))


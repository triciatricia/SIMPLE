import chimera.extension
import threading
import os
import time

# -----------------------------------------------------------------------------
#
class helixhunter_EMO(chimera.extension.EMO):
	def name(self):
		return "Helixhunter"

	def categories(self):
		"Return list of category names in which this extension belongs"
		return ["AIRS"]

	def description(self):
		"Return short description (appropriate for balloon help)"
		return 'runs helixhunter2'

	def documentation(self):
		"Return full documention URL"
		return None

	def hasUI(self):
		"Return whether extension activation starts a UI"
		return 1

	def activate(self):
		"Activate extension and return an instance (if appropriate)"
		self.module('hhc').gui()

		return None

chimera.extension.manager.registerExtension(helixhunter_EMO(__file__))

class foldhunter_EMO(chimera.extension.EMO):
	def name(self):
		return "Foldhunter"

	def categories(self):
		"Return list of category names in which this extension belongs"
		return ["AIRS"]

	def description(self):
		"Return short description (appropriate for balloon help)"
		return 'runs AIRS foldhunter'

	def documentation(self):
		"Return full documention URL"
		return None

	def hasUI(self):
		"Return whether extension activation starts a UI"
		return 1

	def activate(self):
		"Activate extension and return an instance (if appropriate)"
		self.module('fhc').gui()

		return None

chimera.extension.manager.registerExtension(foldhunter_EMO(__file__))

class filters_EMO(chimera.extension.EMO):
       def name(self):
	       return "Filters"

       def categories(self):
	       "Return list of category names in which this extension belongs"
	       return ["AIRS"]

       def description(self):
	       "Return short description (appropriate for balloon help)"
	       return '3D map filters'

       def documentation(self):
	       "Return full documention URL"
	       return None

       def hasUI(self):
	       "Return whether extension activation starts a UI"
	       return 1

       def activate(self):
	       "Activate extension and return an instance (if appropriate)"
	       self.module('filters').gui()

	       return None

chimera.extension.manager.registerExtension(filters_EMO(__file__))


class ssehunter_EMO(chimera.extension.EMO):
	def name(self):
		return "SSEHunter"

	def categories(self):
		"Return list of category names in which this extension belongs"
		return ["AIRS"]

	def description(self):
		"Return short description (appropriate for balloon help)"
		return 'ssehunter with skeleton support'

	def documentation(self):
		"Return full documention URL"
		return None

	def hasUI(self):
		"Return whether extension activation starts a UI"
		return 1

	def activate(self):
		"Activate extension and return an instance (if appropriate)"
		self.module('ssehunter').gui()

		return None

chimera.extension.manager.registerExtension(ssehunter_EMO(__file__))


class ssebuilder_EMO(chimera.extension.EMO):
	def name(self):
		return "SSEBuilder"

	def categories(self):
		"Return list of category names in which this extension belongs"
		return ["AIRS"]

	def description(self):
		"Return short description (appropriate for balloon help)"
		return 'runs ssebuilder'

	def documentation(self):
		"Return full documention URL"
		return None

	def hasUI(self):
		"Return whether extension activation starts a UI"
		return 1

	def activate(self):
		"Activate extension and return an instance (if appropriate)"
		self.module('ssebuilder').gui()

		return None

chimera.extension.manager.registerExtension(ssebuilder_EMO(__file__))

class modeviewer_EMO(chimera.extension.EMO):
	def name(self):
		return "ModeViewer"

	def categories(self):
		"Return list of category names in which this extension belongs"
		return ["AIRS"]

	def description(self):
		"Return short description (appropriate for balloon help)"
		return 'runs modeviewer'

	def documentation(self):
		"Return full documention URL"
		return None

	def hasUI(self):
		"Return whether extension activation starts a UI"
		return 1

	def activate(self):
		"Activate extension and return an instance (if appropriate)"
		self.module('modeviewer').gui()

		return None

chimera.extension.manager.registerExtension(modeviewer_EMO(__file__))

class flexible_EMO(chimera.extension.EMO):
	def name(self):
		return "Flexible Foldhunter"

	def categories(self):
		"Return list of category names in which this extension belongs"
		return ["AIRS"]

	def description(self):
		"Return short description (appropriate for balloon help)"
		return 'Flexible Foldhunter'

	def documentation(self):
		"Return full documention URL"
		return None

	def hasUI(self):
		"Return whether extension activation starts a UI"
		return 1

	def activate(self):
		"Activate extension and return an instance (if appropriate)"
		self.module('flexible').gui()

		return None

chimera.extension.manager.registerExtension(flexible_EMO(__file__))

class pdb2cmm_EMO(chimera.extension.EMO):
	def name(self):
		return "PDB to CMM"

	def categories(self):
		"Return list of category names in which this extension belongs"
		return ["AIRS"]

	def description(self):
		"Return short description (appropriate for balloon help)"
		return 'runs pdb2cmm.py'

	def documentation(self):
		"Return full documention URL"
		return None

	def hasUI(self):
		"Return whether extension activation starts a UI"
		return 1

	def activate(self):
		"Activate extension and return an instance (if appropriate)"
		self.module('p2c').gui()

		return None

chimera.extension.manager.registerExtension(pdb2cmm_EMO(__file__))

class cmm2pdb_EMO(chimera.extension.EMO):
	def name(self):
		return "CMM to PDB"

	def categories(self):
		"Return list of category names in which this extension belongs"
		return ["AIRS"]

	def description(self):
		"Return short description (appropriate for balloon help)"
		return 'runs cmm2pdb.py'

	def documentation(self):
		"Return full documention URL"
		return None

	def hasUI(self):
		"Return whether extension activation starts a UI"
		return 1

	def activate(self):
		"Activate extension and return an instance (if appropriate)"
		self.module('c2p').gui()

		return None

chimera.extension.manager.registerExtension(cmm2pdb_EMO(__file__))
"""
class morph_EMO(chimera.extension.EMO):
	def name(self):
		return "morph"

	def categories(self):
		"Return list of category names in which this extension belongs"
		return ["AIRS"]

	def description(self):
		"Return short description (appropriate for balloon help)"
		return 'runs cmm-morph.py'

	def documentation(self):
		"Return full documention URL"
		return None

	def hasUI(self):
		"Return whether extension activation starts a UI"
		return 1

	def activate(self):
		"Activate extension and return an instance (if appropriate)"
		self.module('morph').gui()

		return None

chimera.extension.manager.registerExtension(morph_EMO(__file__))
"""
class rt_EMO(chimera.extension.EMO):
	def name(self):
		return "EMAN Rotate and Translate"

	def categories(self):
		"Return list of category names in which this extension belongs"
		return ["AIRS"]

	def description(self):
		"Return short description (appropriate for balloon help)"
		return 'rotates and translates a map. also runs ccf2.py'

	def documentation(self):
		"Return full documention URL"
		return None

	def hasUI(self):
		"Return whether extension activation starts a UI"
		return 1

	def activate(self):
		"Activate extension and return an instance (if appropriate)"
		self.module('rt').gui()

		return None

chimera.extension.manager.registerExtension(rt_EMO(__file__))

class pdb2mrc_EMO(chimera.extension.EMO):
	def name(self):
		return "PDB to MRC"

	def categories(self):
		"Return list of category names in which this extension belongs"
		return ["AIRS"]

	def description(self):
		"Return short description (appropriate for balloon help)"
		return 'generates a MRC from a PDB'

	def documentation(self):
		"Return full documention URL"
		return None

	def hasUI(self):
		"Return whether extension activation starts a UI"
		return 1

	def activate(self):
		"Activate extension and return an instance (if appropriate)"
		self.module('pdb2mrc').gui()

		return None

chimera.extension.manager.registerExtension(pdb2mrc_EMO(__file__))

class skeleton_EMO(chimera.extension.EMO):
	def name(self):
		return "Skeletonization"

	def categories(self):
		"Return list of category names in which this extension belongs"
		return ["AIRS"]

	def description(self):
		"Return short description (appropriate for balloon help)"
		return 'generates sse and skeletons from a MRC file'

	def documentation(self):
		"Return full documention URL"
		return None

	def hasUI(self):
		"Return whether extension activation starts a UI"
		return 1

	def activate(self):
		"Activate extension and return an instance (if appropriate)"
		self.module('skeleton').gui()

		return None

chimera.extension.manager.registerExtension(skeleton_EMO(__file__))



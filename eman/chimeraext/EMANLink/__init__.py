import chimera
#from chimera.baseDialog import ModelessDialog
import threading
import os
import time

class EMANThread(threading.Thread):
	"""This is a thread class that performs communication with EMAN"""
	def __init__(self):
		threading.Thread.__init__(self)
#		self.os=OS

	def run(self):
		"This is the actual thread. It is never called directly by the user."
		print os
		home=os.getenv("HOME")


		try:
			os.mkfifo(home+"/.eman/tofifo")
			os.mkfifo(home+"/.eman/fromfifo")
		except:
			pass
		infile=open(home+"/.eman/tofifo","r")
		outfile=open(home+"/.eman/fromfifo","w")

		# for convenience
		import VolumeData
		import VolumeViewer
		vd=VolumeData
		vv=VolumeViewer

		from VolumeViewer.volumedialog import show_volume_dialog
		d=show_volume_dialog()

		# example commands
		# g=VolumeData.open_file_type("threed.0a.mrc","mrc")
		# d.add_data_sets([g2])

		while (1):
#			print "hi"
#			time.sleep(1)
			ret="Error"
			try:
				msg=infile.readline()
				msg=msg.strip()
			except:
				break
			if (len(msg)==0) : continue
			print 'eval=%d"%s"'%(len(msg),msg)
			if (msg[:3]=="bye"): break
			try:
				ret=eval(msg)
			except:
				pass
			outfile.write(str(ret)+"!$@#")
			outfile.flush()
			print("Return='%s'"%str(ret))

		outfile.write("bye!$@#")
		try:
			os.unlink(home+"/.eman/tofifo")
			os.unlink(home+"/.eman/fromfifo")
		except:
			pass
#
#from chimera import dialogs
#dialogs.register(Phantom_Dialog.name, Phantom_Dialog, replace = 1)

import sublime, sublime_plugin
import subprocess, threading

class GrowlThread(threading.Thread):
	def __init__(self,msg):
		self.msg = msg
		threading.Thread.__init__(self)
	def run(self):
		msg = self.msg
		cmd = '/usr/local/bin/growlnotify -a "Sublime Text 2" -t "Available Commands" -m "'+msg+'" -d "doublej"'
		subprocess.call(cmd,shell=True)

class DoubleJListener(sublime_plugin.EventListener):
	s = None
	options = ["jjsq: Swap Quotes",
			   "jjsb: Swap Brackets\n",
			   "jjnr: New File (Right)",
			   "jjnd: New File (Down)\n",
			   "jjdr: Drag File (Right)",
			   "jjdu: Drag File (Up)",
			   "jjdd: Drag File (Down)\n",
			   "jjcl: Clone File (Left)",
			   "jjcr: Clone File (Right)",
			   "jjcd: Clone File (Down)\n",
			   "jjmu: Merge File (Up)",
			   "jjmd: Merge File (Down)",
			   "jjml: Merge File (Left)",
			   "jjmr: Merge File (Right)"]

	def on_activated(self,view):
		self.view = view

	def on_deactivated(self,view):
		region = view.get_regions('doublej')
		if region:
			edit = view.begin_edit()
			view.erase(edit, region[0])
			view.erase_regions('doublej')
			view.end_edit(edit)

	def erase(self):
		view = self.view
		sel = view.sel()[0].a
		if view.substr(sublime.Region(sel-4,sel-2)) == 'jj':
			edit = view.begin_edit()
			view.erase(edit,sublime.Region(sel-4,sel))
			view.erase_regions('doublej')
			view.end_edit(edit)

	def on_selection_modified(self,view):
		sel = view.sel()[0].a
		for r in view.get_regions('doublej'):
			if r.empty() or not r.contains(sel):
				view.erase_regions('doublej')
				
	def on_modified(self, view):
		sel = view.sel()[0].a
		msg = ''
		if self.s and view.size() == self.s:
			reg = sublime.Region(sel-2,sel)
			if view.substr(reg) == 'jj':
				view.add_regions('doublej',[sublime.Region(reg.a,reg.b+1)],'smart.tabstops',sublime.DRAW_OUTLINED)
			if view.substr(sublime.Region(sel-4,sel-2)) == 'jj':
				sublime.set_timeout(self.erase,180)
		elif view.size() < self.s:
			view.erase_regions('doublej')
		for r in view.get_regions('doublej'):
			for o in self.options:
				cmd = view.substr(sublime.Region(r.a,r.b-1))
				if o.startswith(cmd):
					msg+=o+'\n'
		self.s = view.size()
		if msg:
			growl = GrowlThread(msg).start()
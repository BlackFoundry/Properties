#coding=utf-8
from __future__ import print_function

from vanilla import *
from defconAppKit.windows.baseWindow import BaseWindowController
from mojo.events import addObserver, removeObserver
from mojo.extensions import getExtensionDefault, setExtensionDefault
try:
	from fontParts.world import *
except:
	from robofab.world import *

from lib.eventTools.eventManager import allObservers

defaultKeyStub = "com.blackfoundry.Properties."
defaultKeyObserverVisibility = defaultKeyStub + "display"

def toggleObserverVisibility():
	state = not getExtensionDefault(defaultKeyObserverVisibility)
	print("show properties: " + str(state))
	setExtensionDefault(defaultKeyObserverVisibility, state)

class ShowPropertiesTextBox(TextBox):
	def __init__(self, viewID, *args, **kwargs):
		super(ShowPropertiesTextBox, self).__init__(*args, **kwargs)
		observers = allObservers()
		for observer in observers:
			if observer[0] == "mouseUp" and isinstance(ShowPropertiesTextBox, type(observer[1])):
				break
		else:
			addObserver(self, "draw", "mouseUp")
		for observer in observers:
			if observer[0] == "keyUp" and isinstance(ShowPropertiesTextBox, type(observer[1])):
				break
		else:
			addObserver(self, "draw", "keyUp")
		addObserver(self, "glyphWindowWillClose", "glyphWindowWillClose")
		self.cachedPoints = {}
		self.viewID = viewID

	def getDist(self, a_list):
		if a_list:
			return max(a_list) - min(a_list)
		else:
			return 0

	def getSelected(self):
		if CurrentGlyph() == None:
			return
		nbContours = 0
		nbON = 0
		nbOFF = 0
		list_x = []
		list_y = []
		offSelection = None
		for contour in CurrentGlyph():
			nbContours += 1
			segIdx = -1
			for segment in contour:
				segIdx += 1
				for point in segment:
					if point.type not in ['offCurve', 'offcurve']:
						nbON += 1
					elif point.type in ['offCurve', 'offcurve']:
						nbOFF += 1
						if point.selected:
							offSelection = (contour, segIdx, point)
					if point.selected:
						list_x.append(point.x)
						list_y.append(point.y)

		return (self.getDist(list_x), self.getDist(list_y), nbContours, nbON, nbOFF, offSelection)

	def bcpDistance(self, offSelection):
		if offSelection == None:
			return (0, 0)
		con, segIdx, pt = offSelection
		seg = con[segIdx]
		onPt = pt

		if pt == seg.offCurve[-1]: # 'Incoming'
			onPt = seg.onCurve
		elif pt == seg.offCurve[0]: # 'Outcoming'
			onPt = con[segIdx-1].onCurve
		dx = pt.x - onPt.x
		dy = pt.y - onPt.y
		return (dx, dy)

	def draw(self, info):
		if id(info['view']) != self.viewID:
			return
		text = ""
		if not getExtensionDefault(defaultKeyObserverVisibility):
			self.set(text)
			return
		if CurrentGlyph() == None:
			self.set(text)
			return
		(dist_x, dist_y, nbContours, nbON, nbOFF, offSelection) = self.getSelected()
		(bcpDist_x, bcpDist_y) = self.bcpDistance(offSelection)

		text = u"⥓ %s ⥔ %s | ↔︎ %s ↕︎ %s | ◦ %s ⋅ %s ⟜ %s" % (bcpDist_x, bcpDist_y, dist_x, dist_y, nbContours, nbON, nbOFF)
		self.set(text)

	def glyphWindowWillClose(self, info):
		if id(info['view']) != self.viewID:
			return
		removeObserver(self, "mouseUp")
		removeObserver(self, "keyUp")
		removeObserver(self, "glyphWindowWillClose")

class ShowProperties():
	def __init__(self):
		addObserver(self, "glyphWindowDidOpen", "glyphWindowDidOpen")

	def glyphWindowDidOpen(self, info):
		window = info["window"]
		vanillaView = ShowPropertiesTextBox(id(info["view"]), (-200, 22, -20, 22), "", alignment="right", sizeStyle="mini")
		superview = window.editGlyphView.enclosingScrollView().superview()
		view = vanillaView.getNSTextField()
		frame = superview.frame()
		vanillaView._setFrame(frame)
		superview.addSubview_(view)

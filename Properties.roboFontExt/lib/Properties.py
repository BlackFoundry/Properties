#coding=utf-8

from vanilla import *
from defconAppKit.windows.baseWindow import BaseWindowController
from mojo.events import addObserver, removeObserver

class ShowPropertiesTextBox(TextBox):
	def __init__(self, *args, **kwargs):
		super(ShowPropertiesTextBox, self).__init__(*args, **kwargs)
		addObserver(self, "draw", "mouseUp")
		
	def getDist(self, a_list):
		if a_list:
			return max(a_list) - min(a_list)
		else:
			return 0
	
	def getSelected(self):
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
					if point.type != 'offCurve':
						nbON += 1
					elif point.type == 'offCurve':
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
		CurrentGlyph().update()
		(dist_x, dist_y, nbContours, nbON, nbOFF, offSelection) = self.getSelected()
		(bcpDist_x, bcpDist_y) = self.bcpDistance(offSelection)
				
		text = u"⥓ %s ⥔ %s | ↔︎ %s ↕︎ %s | ◦ %s ⋅ %s ⟜ %s" % (bcpDist_x, bcpDist_y, dist_x, dist_y, nbContours, nbON, nbOFF)
		self.set(text)
		
		def windowCloseCallback(self, sender):
			super(ShowPropertiesTextBox, self).windowCloseCallback(sender)
			removeObserver(self, "draw")
		
		
class ShowProperties(BaseWindowController):
	def __init__(self):
		addObserver(self, "glyphWindowDidOpen", "glyphWindowDidOpen")
	
	def glyphWindowDidOpen(self, info):
		window = info["window"]
		vanillaView = ShowPropertiesTextBox((20, 22, -20, 22), "", alignment="right", sizeStyle="mini")
		superview = window.editGlyphView.enclosingScrollView().superview()
		view = vanillaView.getNSTextField()
		frame = superview.frame()
		vanillaView._setFrame(frame)
		superview.addSubview_(view)
		
	def windowCloseCallback(self, sender):
		super(ShowPropertiesTextBox, self).windowCloseCallback(sender)
		removeObserver(self, "glyphWindowDidOpen")

ShowProperties()

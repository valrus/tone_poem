# -*- coding: utf-8 -*-
from __future__ import division

import os
from itertools import chain

from kivy.graphics import Line, Scale
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from musicplayer import MusicPlayer
import map


class VertexWidget(Widget):
    pass


class MapOverlay(RelativeLayout):
    def draw_lines(self, pointList, **kw):
        self.canvas.clear()
        with self.canvas:
            for p1, p2 in pointList:
                Line(points=list(chain(p1, p2)), **kw)


class MapFeatures(MapOverlay):
    pass


class MapLayout(RelativeLayout):
    def __init__(self, **kw):
        self.map = map.GraphMap()
        self.vertex_dict = {}
        super(RelativeLayout, self).__init__(**kw)
        for vertex in self.map.nodes_iter():
            widget = VertexWidget(
                pos_hint={"center_x": vertex.x / self.map.dims.w,
                          "center_y": vertex.y / self.map.dims.h},
                size_hint=(0.01, 0.01)
            )
            self.vertex_dict[vertex] = widget
            self.add_widget(widget)
            widget.bind(pos=self.draw_edges)
            self.bind(size=self.draw_walls)

    def draw_edges(self, obj, attr):
        """Draw lines between this map's vertices.

        Currently just naïvely draws all the lines. Could be made smarter
        by referencing obj and only drawing the lines connected to it.
        """
        self.overlay.draw_lines([
            (self.vertex_dict[v1].center, self.vertex_dict[v2].center)
            for v1, v2 in self.map.edges_iter()
        ], dash_offset=2, dash_length=2, width=1)

    def draw_walls(self, obj, attr):
        self.features.draw_lines([
            [(self.width * x1 / self.map.dims.w,
              self.height * y1 / self.map.dims.h),
             (self.width * x2 / self.map.dims.w,
              self.height * y2 / self.map.dims.h)]
            for (x1, y1), (x2, y2) in self.map.walls
        ], width=2)


class AreaScreen(Screen):
    def __init__(self, **kw):
        super(Screen, self).__init__(**kw)
        self.ids.map_root.overlay = self.ids.map_overlay

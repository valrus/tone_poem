# -*- coding: utf-8 -*-
from __future__ import division

import json
import os
from itertools import chain
from math import sqrt
from random import gauss, choice

from kivy.core.image import Image
from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.graphics import Line, Mesh, Rectangle, RenderContext
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.stencilview import StencilView
from kivy.uix.widget import Widget

from musicplayer import MusicPlayer
from tools import Coords, Size, Rect, Quad, distance_squared, WINDOW_SIZE
import map


class VertexWidget(Widget):
    def __init__(self, vertex, **kw):
        super(VertexWidget, self).__init__(**kw)
        self.vertex = vertex


class MapOverlay(RelativeLayout):
    needs_full_redraw = BooleanProperty(True)

    def __init__(self, **kw):
        self.canvas = RenderContext(use_parent_projection=True)
        self.canvas.shader.source = "multiquad.glsl"
        super(MapOverlay, self).__init__(**kw)


class MapFeatures(MapOverlay, StencilView):
    pass


class MapRenderer(EventDispatcher):
    ground_tile = None
    walls_overlay = ObjectProperty(None)
    features_overlay = ObjectProperty(None)
    vertex_format = [
        ('vPosition', 2, 'float'),
        ('vTexCoords0', 2, 'float'),
        ('vRotation', 1, 'float'),
        ('vCenter', 2, 'float')
    ]


class SkeletronMapRenderer(MapRenderer):
    def draw_paths(self, paths, clear=True):
        if not self.features_overlay:
            return
        if self.features_overlay.needs_full_redraw:
            self.features_overlay.canvas.clear()
        with self.features_overlay.canvas:
            for p1, p2 in paths:
                Line(points=list(chain(p1, p2)),
                     dash_offset=2, dash_length=2, width=1)

    def draw_walls(self, walls):
        if not self.walls_overlay:
            return
        self.walls_overlay.canvas.clear()
        with self.walls_overlay.canvas:
            for w1, w2 in walls:
                Line(points=list(chain(w1, w2)), width=2)


class AtlasData(object):
    def __init__(self, filename):
        self.filename = filename
        self.texture_dict = {}
        with open(self.filename, "r") as atlasfile:
            self.atlas_data = json.load(atlasfile)

    def page(self, page):
        base, __ = os.path.splitext(os.path.basename(self.filename))
        return "{}-{}.png".format(base, page)

    def page_path(self, page):
        base, __ = os.path.splitext(self.filename)
        return "{}-{}.png".format(base, page)

    def texture(self, page):
        if page in self.texture_dict:
            return self.texture_dict[page]
        else:
            self.texture_dict[page] = Image(self.page_path(page)).texture
            return self.texture_dict[page]

    def size(self, page):
        return Size(*self.texture_dict.get(page, self.texture(page)).size)

    def atlas_uv_dict(self, page):
        return {
            texture_name: UVData(self.size(page), Rect(*dims))
            for texture_name, dims in self.atlas_data[self.page(page)].iteritems()
        }


class UVData(object):
    def __init__(self, atlas_size, tex_dims):
        atlas_w, atlas_h = atlas_size
        self.corners = Quad(tex_dims.x / atlas_w,
                            1. - tex_dims.y / atlas_h,
                            (tex_dims.x + tex_dims.w) / atlas_w,
                            1. - (tex_dims.y + tex_dims.h) / atlas_h)
        self.size = Size(tex_dims.w, tex_dims.h)


class ForestMapRenderer(SkeletronMapRenderer):
    ground_tile = os.path.join("sprites", "grass_tile.png")
    sprites = AtlasData(os.path.join("sprites", "trees.atlas"))
    wall_page = 0

    def _read_atlas(self):
        return self.__class__.sprites.atlas_uv_dict(
            self.__class__.wall_page
        )

    def __init__(self, **kw):
        super(ForestMapRenderer, self).__init__(**kw)
        self.uvs = self._read_atlas()
        self.wall_meshes = []

    def _choose_tex(self):
        return choice(self.uvs.values())

    def _mesh_box(self, uvs, x, y, scale=1.0):
        return [
            (-uvs.size.w * scale, -uvs.size.h * scale,
             uvs.corners.x1, uvs.corners.y1,
             0, x, y),
            (uvs.size.w * scale, -uvs.size.h * scale,
             uvs.corners.x2, uvs.corners.y1,
             0, x, y),
            (uvs.size.w * scale, uvs.size.h * scale,
             uvs.corners.x2, uvs.corners.y2,
             0, x, y),
            (-uvs.size.w * scale, uvs.size.h * scale,
             uvs.corners.x1, uvs.corners.y2,
             0, x, y)
        ]

    def _triangle_indices(self, start):
        return [start, start + 1, start + 2,
                start + 2, start + 3, start]

    def _get_tree_line(self, wall, verts, indices):
        v1, v2 = wall
        # We want to draw back to front, so larger y value first
        if v1.y < v2.y:
            v1, v2 = v2, v1
        Dx, Dy = v2.x - v1.x, v2.y - v1.y
        sparsity = 20.0
        density = sqrt(distance_squared(v1, v2)) / sparsity
        dy, dx = Dy / density, Dx / density
        x, y = v1
        x_going_right = (dx > 0)
        while y > v2.y and ((x < v2.x) == x_going_right):
            jitter = gauss(0, 0.25)
            indices.extend(self._triangle_indices(len(verts)))
            verts.extend(
                self._mesh_box(
                    self._choose_tex(),
                    x + jitter * dy,
                    y + jitter * dx,
                    scale=0.3
                )
            )
            x, y = x + dx, y + dy

    def draw_walls(self, walls):
        if not self.walls_overlay:
            return
        self.walls_overlay.canvas.clear()
        verts, indices = [], []
        with self.walls_overlay.canvas:
            for wall in walls:
                self._get_tree_line(wall, verts, indices)
            # NB: Max vertices length is 65535. Might need multiple meshes.
            self.wall_meshes.append(Mesh(
                indices=indices,
                vertices=chain(*sorted(verts, key=lambda i: -i[6])),
                fmt=self.__class__.vertex_format,
                mode="triangles",
                texture=self.__class__.sprites.texture(self.__class__.wall_page)
            ))


class MapLayout(RelativeLayout):
    ground_overlay = ObjectProperty(None)
    walls_overlay = ObjectProperty(None)
    features_overlay = ObjectProperty(None)

    def __init__(self, **kw):
        self.map = map.GraphMap()
        self.renderer = kw.get("renderer", ForestMapRenderer)()
        self.vertex_dict = {}
        self.ground_texture = None
        super(RelativeLayout, self).__init__(**kw)
        for vertex in self.map.nodes_iter():
            widget = VertexWidget(
                vertex,
                pos_hint={"center_x": vertex.x / self.map.dims.w,
                          "center_y": vertex.y / self.map.dims.h},
                size_hint=(0.01, 0.01)
            )
            self.add_widget(widget)
            self.vertex_dict[vertex] = widget
            widget.bind(pos=self.draw_edges)
        self.bind(size=self.draw_walls)

    def on_ground_overlay(self, instance, value):
        self.renderer.ground_overlay = value
        self.ground_texture = Image(self.renderer.__class__.ground_tile).texture
        self.ground_texture.wrap = "repeat"
        self.ground_texture.uvsize = (WINDOW_SIZE.w // 512 + 1,
                                      WINDOW_SIZE.h // 512 + 1)  # probably change

    def on_walls_overlay(self, instance, value):
        self.renderer.walls_overlay = value
        self.draw_walls(None, None)

    def on_features_overlay(self, instance, value):
        self.renderer.features_overlay = value
        self.draw_edges(None, None)

    def draw_edges(self, vertex_widget, new_pos):
        """Draw lines between this map's vertices.

        Currently just naïvely draws all the lines. Could be made smarter
        by referencing obj and only drawing the lines connected to it.
        """
        if self.features_overlay.needs_full_redraw:
            vertices = self.vertex_dict.keys()
            self.features_overlay.needs_full_redraw = True
        else:
            vertices = vertex_widget.vertex
            self.features_overlay.needs_full_redraw = False
        self.renderer.draw_paths([
            (self.vertex_dict[v1].center, self.vertex_dict[v2].center)
            for v1, v2 in self.map.edges_iter(vertices)
        ])

    def draw_walls(self, widget, size):
        if not size or size[0] != WINDOW_SIZE.w or size[1] != WINDOW_SIZE.h:
            print(size)
            return
        with self.ground_overlay.canvas:
            Rectangle(pos=(0, 0), size=self.size, texture=self.ground_texture)
        self.renderer.draw_walls([
            [Coords(self.width * x1 / self.map.dims.w,
                    self.height * y1 / self.map.dims.h),
             Coords(self.width * x2 / self.map.dims.w,
                    self.height * y2 / self.map.dims.h)]
            for (x1, y1), (x2, y2) in self.map.walls
        ])


class AreaScreen(Screen):
    def __init__(self, **kw):
        super(Screen, self).__init__(**kw)

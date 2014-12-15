# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function

import json
import os
from itertools import chain
from math import sqrt
from random import gauss, choice

from kivy.core.image import Image
from kivy.event import EventDispatcher
from kivy.graphics import Color, Line, Mesh, Rectangle, RenderContext
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.stencilview import StencilView
from kivy.uix.widget import Widget

from creature import PlayerCharacter
from creature_widget import CreatureWidget
from musicplayer import MusicPlayer
from tools import Size, Quad, Rect, Coords, distance_squared
from tools import ROOT_DIR, WINDOW_SIZE
import map


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


class MapRenderer(EventDispatcher):
    ground_tile = None
    overlay = ObjectProperty(None)
    features = ObjectProperty(None)


class SkeletronMapRenderer(MapRenderer):
    def __init__(self, **kw):
        super(SkeletronMapRenderer, self).__init__(**kw)
        self.ground_texture = Texture.create(size=(512, 512), colorfmt='rgb')
        self.custom_shader = None

    def draw_paths(self, paths):
        if not self.features:
            return
        with self.features.canvas:
            Color(1.0, 1.0, 1.0)
            for p1, p2 in paths:
                Line(points=list(chain(p1, p2)),
                     dash_offset=2, dash_length=2, width=1)

    def draw_walls(self, walls):
        if not self.overlay:
            return
        with self.overlay.canvas:
            Color(1.0, 0, 0)
            for w1, w2 in walls:
                print("Line", w1, w2)
                Line(points=list(chain(w1, w2)), width=2)


class ForestMapRenderer(SkeletronMapRenderer):
    sprites = AtlasData(os.path.join(ROOT_DIR, "sprites", "trees.atlas"))
    wall_page = 0
    vertex_format = [
        ('vPosition', 2, 'float'),
        ('vTexCoords0', 2, 'float'),
        ('vRotation', 1, 'float'),
        ('vCenter', 2, 'float')
    ]

    def _read_atlas(self):
        return self.__class__.sprites.atlas_uv_dict(
            self.__class__.wall_page
        )

    def __init__(self, **kw):
        super(ForestMapRenderer, self).__init__(**kw)
        self.ground_texture = Image(os.path.join("sprites", "grass_tile.png")).texture
        self.ground_texture.wrap = "repeat"
        self.ground_texture.uvsize = (WINDOW_SIZE.w // 512 + 1,
                                      WINDOW_SIZE.h // 512 + 1)  # probably change
        self.custom_shader = os.path.join(ROOT_DIR, "multiquad.glsl")
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
        if not self.overlay:
            return
        verts, indices = [], []
        with self.overlay.canvas:
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


class MapWrapper(AnchorLayout):
    """Thin wrapper widget to make it easier to position a widget by center on the map."""
    def __init__(self, center_coords, wrapped_widget, **kw):
        self.center_coords = center_coords
        super(MapWrapper, self).__init__(**kw)
        self.add_widget(wrapped_widget)


class VertexWidget(Widget):
    pass


class MapOverlay(RelativeLayout):
    needs_full_redraw = BooleanProperty(True)


class MapFeatures(RelativeLayout):
    needs_full_redraw = BooleanProperty(True)

    def __init__(self, vertices_pos, **kw):
        super(MapFeatures, self).__init__(**kw)
        for vertex_pos in vertices_pos:
            # TODO: Does passing in center=vertex_pos work in Kivy 1.9?
            vertex_widget = VertexWidget(size_hint=(0.01, 0.01))
            wrapper = MapWrapper(vertex_pos, vertex_widget)
            self.add_widget(wrapper)
        start_widget_pos = choice(vertices_pos)
        print("Adding pc at", start_widget_pos)
        self.pc = PlayerCharacter('Valrus', 'sprites/walrus')
        self.pcWidget = CreatureWidget(
            self.pc,
            pos=start_widget_pos,
            size=(30, 30),
            size_hint=(None, None),
            label=False
        )
        self.add_widget(MapWrapper(start_widget_pos, self.pcWidget))


class MapLayout(AnchorLayout):
    overlay = ObjectProperty(None)
    features = ObjectProperty(None)
    margin = 60

    def __init__(self, **kw):
        self.map = map.GraphMap(margin=MapLayout.margin)
        self.renderer = kw.get("renderer", ForestMapRenderer)()

        super(MapLayout, self).__init__(**kw)
        self.vertices_pos = list(self.map.nodes_iter())
        self.overlay = MapOverlay(size_hint=(1.0, 1.0),
                                  background_color=(0, 0, 0, 0))
        self.add_widget(self.overlay)
        self.features = MapFeatures(self.vertices_pos,
                                    size_hint=(None, None),
                                    size=tuple(WINDOW_SIZE),
                                    pos=(0, 0),
                                    background_color=(0, 0, 0, 0))
        self.add_widget(self.features)

    def on_overlay(self, instance, value):
        self.renderer.overlay = value
        value.canvas = RenderContext(use_parent_projection=True)
        if self.renderer.custom_shader:
            value.canvas.shader.source = self.renderer.custom_shader
        value.bind(size=self.draw_walls)

    def on_features(self, instance, value):
        self.renderer.features = value
        self.draw_edges(value, value.size)

    def _transform_map_vertex(self, vert):
        return Coords(self.width * vert[0] / self.map.dims.w,
                      self.height * vert[1] / self.map.dims.h)

    def draw_edges(self, widget, size):
        """Draw lines between this map's vertices.
        """
        self.renderer.draw_paths([
            [v1, v2]
            for v1, v2 in self.map.edges_iter(self.vertices_pos)
        ])

    def draw_walls(self, widget, size):
        if not (size and tuple(size) == tuple(WINDOW_SIZE)):
            return
        self.renderer.draw_walls([
            [self._transform_map_vertex(v1),
             self._transform_map_vertex(v2)]
            for v1, v2 in self.map.walls
        ])


class AreaScreen(Screen):
    def __init__(self, **kw):
        super(Screen, self).__init__(**kw)

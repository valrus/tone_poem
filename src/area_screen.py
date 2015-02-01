# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function

import json
import os
from itertools import chain
from math import sqrt
from random import gauss, choice

from kivy.animation import Animation, AnimationTransition
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
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from beastie import NoteCollector
from creature import PlayerCharacter
from creature_widget import CreatureWidget
from keyboard import MidiInputDispatcher
from mingushelpers import is_note_on, is_note_off, notes_match
from musicplayer import MusicPlayer
from tools import Size, Quad, Rect, Coords, distance_squared
from tools import ROOT_DIR, WINDOW_SIZE
import map
import map_label


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
            for texture_name, dims in self.atlas_data[self.page(page)].items()
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

    def draw_paths(self, paths):
        return

    def draw_walls(self, walls):
        return 


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
        (b'vPosition', 2, 'float'),
        (b'vTexCoords0', 2, 'float'),
        (b'vRotation', 1, 'float'),
        (b'vCenter', 2, 'float')
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
        return choice(list(self.uvs.values()))

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
    def __init__(self, **kw):
        renderer = kw.pop("renderer", None)
        super(MapOverlay, self).__init__(**kw)
        if renderer:
            self.canvas = RenderContext(use_parent_projection=True)
            if renderer.custom_shader:
                self.canvas.shader.source = renderer.custom_shader


class MapFeatures(RelativeLayout):
    def __init__(self, **kw):
        super(MapFeatures, self).__init__(**kw)

    def add_vertices(self, vertices_pos):
        for vertex_pos in vertices_pos:
            # TODO: Does passing in center=vertex_pos work in Kivy 1.9?
            vertex_widget = VertexWidget(size_hint=(0.01, 0.01))
            wrapper = MapWrapper(vertex_pos, vertex_widget)
            self.add_widget(wrapper)

    def add_pc(self, pc, start_widget_pos):
        self.pcWidget = CreatureWidget(
            pc,
            pos=start_widget_pos,
            size=(50, 50),
            size_hint=(None, None),
            label=False
        )
        self.add_widget(MapWrapper(start_widget_pos, self.pcWidget))


def getNavigationWidgets(start, graph_map, edges):
    widgets = []
    for p1, p2 in edges:
        if p2 == start:
            p1, p2 = p2, p1
        widgets.append(Label(text=str(graph_map.edge_label(p1, p2)),
                             font_name='fonts/DejaVuSans.ttf',
                             center=p1 + 0.25 * (p2 - p1),
                             size=(50, 50),
                             size_hint=(None, None)))
    widgets.append(Label(text=str(graph_map.node_label(start)),
                         font_name='fonts/DejaVuSans.ttf',
                         center=start,
                         size=(150, 150),
                         font_size=48,
                         bold=True,
                         size_hint=(None, None),
                         color=(1, 1, 1, 0.5)))
    return widgets

class AreaScreen(Screen):
    overlay = ObjectProperty(None)
    features = ObjectProperty(None)
    renderer = ObjectProperty(None)
    midi_in = ObjectProperty(None)
    margin = 60

    def __init__(self, **kw):
        self.map = map.GraphMap(margin=AreaScreen.margin)
        self.map.add_labels(map_label.NodeNote)
        self.renderer = kw.get("renderer", ForestMapRenderer)()
        self.vertices_pos = self.map.nodes()
        self.pc = PlayerCharacter('Valrus', 'sprites/walrus')
        self.pc_loc = choice(self.vertices_pos)
        self.nav_widgets = []
        super(AreaScreen, self).__init__(**kw)
        self.overlay = MapOverlay(renderer=self.renderer)
        self.add_widget(self.overlay)
        self.features = MapFeatures(renderer=self.renderer)
        self.add_widget(self.features)
        self.ear = NoteCollector()

    def on_midi_in(self, instance, value):
        value.watchers.add(self)
        self.register_event_type('on_midi')

    def on_overlay(self, instance, value):
        self.renderer.overlay = value
        self.draw_walls()

    def on_features(self, instance, value):
        self.renderer.features = value
        value.add_vertices(self.vertices_pos)
        value.add_pc(self.pc, self.pc_loc)
        self.draw_edges()
        self.resetNavigationWidgets()

    def resetNavigationWidgets(self, *args):
        """Set up labels describing how to move the PC.

        Takes *args because it's used as a callback for Animation.on_complete
        and I don't know what that passes in."""
        for w in self.nav_widgets:
            self.features.remove_widget(w)
        del self.nav_widgets[:]
        self.nav_widgets = getNavigationWidgets(self.pc_loc, self.map, self.map.edges([self.pc_loc]))
        for w in self.nav_widgets:
            print("adding widget", w, "with center", w.center)
            self.features.add_widget(w)

    def on_midi(self, msg):
        self.ear.hear(msg)
        if not self.ear.heard_count() >= 1:
            return
        heard = self.ear.retrieve()
        print("Heard", heard)
        for neighbor in self.map.neighbors(self.pc_loc):
            print("Comparing to", self.map.node_label(neighbor).value)
            if notes_match(heard, self.map.node_label(neighbor).value):
                self.pc_loc = neighbor
                anim = Animation(
                    center=(self.pc_loc.x, self.pc_loc.y),
                    duration=0.5,
                    transition=AnimationTransition.in_out_quad)
                anim.on_complete = self.resetNavigationWidgets
                anim.start(self.features.pcWidget)

    def draw_edges(self):
        """Draw lines between this map's vertices.
        """
        self.renderer.draw_paths([
            [v1, v2]
            for v1, v2 in self.map.edges_iter(self.vertices_pos)
        ])

    def draw_walls(self):
        self.renderer.draw_walls([[Coords(*v1), Coords(*v2)]
                                  for v1, v2 in self.map.walls])


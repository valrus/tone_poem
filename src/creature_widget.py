from threading import Thread

from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import StringProperty, ObjectProperty, NumericProperty


class CreatureWidget(AnchorLayout):
    image_source = StringProperty(None)
    creature = ObjectProperty(None)
    beat_length = NumericProperty(1.0)
    happy_label = ObjectProperty(None)

    def __init__(self, creature, **kw):
        super(CreatureWidget, self).__init__(**kw)
        self.creature = creature
        self.image_source = self.creature.atlas
        self.thread = None

    def flash(self, *args):
        length = self.beat_length
        self.thread = Thread(
            target=self.creature.anim.build(length).start,
            args=(self.ids.sprite, )
        )
        self.thread.start()

    def on_happiness(self, *args):
        self.happy_label.text = "".join([
            u"\u25CF" * self.creature.current_happiness,
            u"\u25CB" * (self.creature.max_happiness
                         - self.creature.current_happiness)
        ])

    def on_creature(self, *args):
        self.on_happiness()
        self.creature.bind(current_happiness=self.on_happiness)


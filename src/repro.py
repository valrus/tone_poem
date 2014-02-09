from kivy.app import App
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.listview import ListItemButton, ListView
from kivy.uix.stacklayout import StackLayout


def list_args_converter(row_index, s):
    return {
        'text': s,
        'size_hint_y': None,
        'height': 25
    }


class ReproApp(App):
    def build(self):
        root = StackLayout(orientation='lr-tb')
        data = ["1", "2", "3", "4", "5"]
        list_adapter = ListAdapter(data=data,
                                   args_converter=list_args_converter,
                                   cls=ListItemButton,
                                   selection_mode='single',
                                   allow_empty_selection=False)
        root.add_widget(ListView(adapter=list_adapter))
        return root


if __name__ == '__main__':
    ReproApp().run()

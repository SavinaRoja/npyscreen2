#!/usr/bin/env python
# encoding: utf-8

import npyscreen2


#This application class serves as a wrapper for the initialization of curses
#and also manages the actual forms of the application
class MyTestApp(npyscreen2.App):
    def on_start(self):
        self.main = self.add_form(MainForm, 'MAIN', framed=True)


#This form class defines the display that will be presented to the user
class MainForm(npyscreen2.TraditionalForm):
    def create(self):
        self.add(npyscreen2.TitledField,
                 title_value="Text:",
                 field_value="Hello World!")

    def post_edit(self):
        self.parent_app.set_next_form(None)

if __name__ == '__main__':
    test_app = MyTestApp()
    test_app.run()

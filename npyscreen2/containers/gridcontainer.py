# -*- coding: utf-8 -*-

from . import Container

#import curses

import logging
log = logging.getLogger('npyscreen2.containers.gridcontainer')

__all__ = ['GridContainer']


class GridContainer(Container):

    def __init__(self,
                 form,
                 parent,
                 rows=1,
                 cols=2,
                 fill_rows_first=True,
                 *args,
                 **kwargs):

        super(GridContainer, self).__init__(form,
                                            parent,
                                            *args,
                                            **kwargs)

        self.rows = rows
        self.cols = cols
        self.fill_rows_first = fill_rows_first
        self.grid_edit_indices = (0, 0)

        log.debug('''\
{} created with rows={}. cols={}, fill_rows_first={}\
'''.format(self.__class__, rows, cols, fill_rows_first))

        self.initiate_grid()

    def add_widget(self,
                   widget_class,
                   widget_id=None,
                   rely=None,
                   relx=None,
                   max_height=None,
                   max_width=None,
                   *args,
                   **kwargs):
        w = super(GridContainer, self).add_widget(widget_class,
                                                  widget_id=None,
                                                  rely=None,
                                                  relx=None,
                                                  max_height=None,
                                                  max_width=None,
                                                  *args,
                                                  **kwargs)
        self.update_grid()
        return w

    def remove_widget(self, widget=None, widget_id=None):
        super(GridContainer, self).remove_widget(widget=widget,
                                                 widget_id=widget_id)
        self.update_grid()

    def convert_flat_index_to_grid(self, index):
        if self.fill_rows_first:
            row = index // self.cols
            col = index % self.cols
        else:
            row = index % self.rows
            col = index // self.rows
        return col, row

    def convert_grid_indices_to_flat(self, col_index, row_index):
        if self.fill_rows_first:
            return col_index + row_index * self.cols
        else:
            return col_index * self.rows + row_index

    def resize(self):
        #GridContainer expands to fill its entire allocated space
        self.height = self.max_height
        self.width = self.max_width

        self.resize_grid_coords()

        #GridContainer sets rely-relx and sets max height and width
        for index, widget in enumerate(self.autoables):
            col, row = self.convert_flat_index_to_grid(index)
            widget.rely, widget.relx = self.grid_coords[col][row]
            widget.max_height, widget.max_width = self.grid_dim_hw[col][row]

    def initiate_grid(self):
        """
        Initiates the data structures for the grid and grid coordinates
        """

        self.grid = []
        self.grid_coords = []
        self.grid_dim_hw = []

        for i in range(self.cols):
            self.grid.append([None] * self.rows)
            self.grid_coords.append([[0, 0], ] * self.rows)
            self.grid_dim_hw.append([[0, 0], ] * self.rows)

        self.update_grid()

    def update_grid(self):
        for i, widget in enumerate(self.autoables):
            col, row = self.convert_flat_index_to_grid(i)
            self.grid[col][row] = widget

    def resize_grid_coords(self):

        def apportion(start, stop, n):
            locs = []
            cell_size = (stop - start + 1) / n
            for i in range(n):
                locs.append(start + round(i * cell_size))
            return locs

        #Define the start and stop locations
        rely_start = self.rely + self.top_margin
        rely_stop = self.rely + self.height - self.bottom_margin
        relx_start = self.relx + self.left_margin
        relx_stop = self.relx + self.width - self.right_margin

        relys = apportion(rely_start, rely_stop, self.rows)
        relxs = apportion(relx_start, relx_stop, self.cols)

        for col in range(self.cols):
            for row in range(self.rows):
                y, x = relys[row], relxs[col]
                #Set the grid coords matrix
                self.grid_coords[col][row] = [y, x]

        for col in range(self.cols):
            for row in range(self.rows):
                if row == (self.rows - 1):  # Last row
                    height = (self.rely + self.max_height) -\
                             (self.grid_coords[col][row][0] + self.bottom_margin)
                else:
                    height = self.grid_coords[col][row + 1][0] - self.grid_coords[col][row][0]

                if col == (self.cols - 1):  # Final column
                    width = (self.relx + self.max_width) -\
                            (self.grid_coords[col][row][1] + self.right_margin)
                else:
                    width = self.grid_coords[col + 1][row][1] - self.grid_coords[col][row][1]

                self.grid_dim_hw[col][row] = [height, width]

    def set_up_exit_condition_handlers(self):
        """
        Set up handlers for what to do when widgets exit.

        Updates the how_exited_handlers with the new methods for directional
        exit codes in a grid.
        """
        super(GridContainer, self).set_up_exit_condition_handlers()
        self.how_exited_handlers.update({'down': self.find_next_editable_down,
                                         'up': self.find_next_editable_up,
                                         'right': self.find_next_editable_right,
                                         'left': self.find_next_editable_left,
                                         })

    #Thoughts for these methods and the implementation of the Grid:
    #Should probably enable some sort of wrap-around/cycle-widgets behavior in
    #the base; so for instance if one is in the right-most column and a it
    #exits right, then it will go to the left-most column. Then again, this sort
    #of thing is probably a significant target for customization... perhaps it
    #should go to the left-most column *and* down a row, or perhaps wrapping
    #will only be allowed on the left and right, but not the top and bottom.
    #I'll need to put some thought into how this might be made easily customized
    #or documented so that users might be able to avoid re-implementing these
    #methods.
    #
    #On a related note, it seems pretty clear to me that Containers should soon
    #receive support for treating themselves as editable Widgets. Additionally,
    #it seems that there may be circumstances where a Container should inherit
    #the exit condition of a Widget; lots of possibilities out there...
    #
    #Keep in mind that the widgets stored in the grid indices are all autoables
    #TODO: Take precautions in these methods to handle IndexErrormj
    def find_next_editable_down(self):
        cur_col, cur_row = self.grid_edit_indices
        for row in range(cur_row + 1, self.rows):
            flat = self.convert_grid_indices_to_flat(cur_col, row)
            widget = self.autoables[flat]
            if widget.editable:
                self.grid_edit_indices = (cur_col, row)
                self.edit_index = self.contained.index(widget)
                return

    def find_next_editable_up(self):
        cur_col, cur_row = self.grid_edit_indices
        for row in range(cur_row - 1, -1, -1):
            flat = self.convert_grid_indices_to_flat(cur_col, row)
            widget = self.autoables[flat]
            if widget.editable:
                self.grid_edit_indices = (cur_col, row)
                self.edit_index = self.contained.index(widget)
                return

    def find_next_editable_right(self):
        cur_col, cur_row = self.grid_edit_indices
        for col in range(cur_col + 1, self.cols):
            flat = self.convert_grid_indices_to_flat(col, cur_row)
            widget = self.autoables[flat]
            if widget.editable:
                self.grid_edit_indices = (col, cur_row)
                self.edit_index = self.contained.index(widget)
                return

    def find_next_editable_left(self):
        cur_col, cur_row = self.grid_edit_indices
        for col in range(cur_col - 1, -1, -1):
            flat = self.convert_grid_indices_to_flat(col, cur_row)
            widget = self.autoables[flat]
            if widget.editable:
                self.grid_edit_indices = (col, cur_row)
                self.edit_index = self.contained.index(widget)
                return

#!/usr/bin/env python
# -*- coding: utf-8 -*-
### BEGIN LICENSE
# Copyright (C) 2013 Baranovskiy Konstantin (baranovskiykonstantin@gmail.com)
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

from os import path
import codecs


class Schematic:
    """
    Implementation of KiCAD Schematic diagram file.

    """
    ID = 'EESchema Schematic File'

    def __init__(self, sch_name):
        """
        Load all contents from KiCAD's Schematic file.

            Attributes:

            sch_name (str) - full name of KiCAD Schematic file;
            version (int) - version of file format;
            libs (Libs) - list of used libraries;
            eelayer (list of Eelayer) - list of eelayer's information;
            descr (Descr) - title block description;
            items (list of Comp, Sheet, Bitmap, Connection, TextLabel, Wire or
        Entry) - list of all items in schematic.

        """
        self.sch_name = sch_name
        self.load()

    def load(self):
        """
        Open KiCAD Schematic file and read all information from it.

        """
        self.libs = self.Libs()
        self.eelayer = []
        self.items = []

        sch_file = codecs.open(self.sch_name, 'r', 'utf-8')
        first_line = sch_file.readline().encode('utf-8')
        first_line = first_line.replace('\n', '')
        if first_line.startswith(self.ID):
            self.version = int(split_line(first_line)[4])
        else:
            return
        for sch_line in sch_file:
            sch_line = sch_line.encode('utf-8')
            if sch_line.startswith('$'):
                if sch_line == '$EndSCHEMATC':
                    return
                else:
                    item = sch_line
                    item_val = ''
                    while not sch_line.startswith('$End'):
                        item_val += sch_line
                        sch_line = sch_file.readline().encode('utf-8')
                    if item.startswith('$Descr'):
                        self.descr = self.Descr(item_val)
                    elif item.startswith('$Comp'):
                        self.items.append(self.Comp(item_val))
                    elif item.startswith('$Sheet'):
                        self.items.append(self.Sheet(item_val))
                    elif item.startswith('$Bitmap'):
                        self.items.append(self.Bitmap(item_val))
            elif sch_line.startswith('Connection'):
                self.items.append(self.Connection(sch_line))
            elif sch_line.startswith('NoConn'):
                self.items.append(self.Connection(sch_line))
            elif sch_line.startswith('Text'):
                if ' Notes ' in sch_line:
                    sch_line += sch_file.readline().encode('utf-8')
                    self.items.append(self.Text(sch_line))
                elif ' GLabel ' in sch_line:
                    sch_line += sch_file.readline().encode('utf-8')
                    self.items.append(self.Text(sch_line))
                elif ' HLabel ' in sch_line:
                    sch_line += sch_file.readline().encode('utf-8')
                    self.items.append(self.Text(sch_line))
                elif ' Label ' in sch_line:
                    sch_line += sch_file.readline().encode('utf-8')
                    self.items.append(self.Text(sch_line))
            elif sch_line.startswith('Wire'):
                if 'Wire Line' in sch_line:
                    sch_line += sch_file.readline().encode('utf-8')
                    self.items.append(self.Wire(sch_line))
                elif 'Bus Line' in sch_line:
                    sch_line += sch_file.readline().encode('utf-8')
                    self.items.append(self.Wire(sch_line))
                elif 'Notes Line' in sch_line:
                    sch_line += sch_file.readline().encode('utf-8')
                    self.items.append(self.Wire(sch_line))
            elif sch_line.startswith('Entry'):
                if 'Wire Line' in sch_line:
                    sch_line += sch_file.readline().encode('utf-8')
                    self.items.append(self.Entry(sch_line))
                elif 'Bus Bus' in sch_line:
                    sch_line += sch_file.readline().encode('utf-8')
                    self.items.append(self.Entry(sch_line))
            elif sch_line.startswith('LIBS:'):
                self.libs.add(sch_line)
            elif sch_line.startswith('EELAYER') and not \
                 sch_line.startswith('EELAYER END'):
                    self.eelayer.append(self.Eelayer(sch_line))

    def save(self):
        """
        Save all content to KiCAD Schematic file.

        """
        sch_file = codecs.open(self.sch_name, 'w', 'utf-8')

        first_line = self.ID + ' Version ' + str(self.version) + '\n'
        sch_file.write(first_line.decode('utf-8'))

        self.libs.save(sch_file)

        for eelayer in self.eelayer:
            eelayer.save(sch_file)
        sch_file.write(u'EELAYER END\n')

        self.descr.save(sch_file)

        for item in self.items:
            item.save(sch_file)

        sch_file.write(u'$EndSCHEMATC')
        sch_file.close()

    class Libs(list):
        """
        List of libraries used in schematic.

        """

        def add(self, str_lib):
            """
            Extracts library name from string and add it to the list.

                Arguments:

                str_lib (str) - text line read from KiCAD Schematic file.

            """
            str_lib = str_lib.rstrip('\n')
            lib = str_lib.lstrip('LIBS:')
            self.append(lib)

        def save(self, sch_file):
            """
            Save current library name to KiCAD Schematic file.

                Arguments:

                sch_file (file) - file for writing.

            """
            for lib in self:
                line = 'LIBS:' + lib + '\n'
                sch_file.write(line.decode('utf-8'))

    class Eelayer:
        """
        Description of EESchema layer.

            Attributes:

            nn (int) - ???
            mm (int) - ???

        """

        def __init__(self, str_eelayer):
            """
            Extracts EELAYER description from string.

                Arguments:

                str_eelayer (str) - text line read from KiCAD Schematic file.

            """
            str_eelayer = str_eelayer.lstrip('EELAYER ')
            parts = split_line(str_eelayer)
            self.nn = int(parts[0])
            self.mm = int(parts[1])

        def save(self, sch_file):
            """
            Save EELAYER description to KiCAD Schematic file.

                Arguments:

                sch_file (file) - file for writing.

            """
            line = 'EELAYER ' + str(self.nn) + ' ' + str(self.mm) + '\n'
            sch_file.write(line.decode('utf-8'))

    class Descr:
        """
        Title block description.

            Attributes:

            sheet_format (str) - string of sheet format (A4...A0, A...E);
            sheet_size_x (int) - width of sheet in mils (1/1000 inch);
            sheet_size_y (int) - height of sheet in mils;
            portrait (bool) - if True - orientation is portrait;
            encoding (srt) - encoding of text;
            sheet_number (int) - number of current sheet;
            sheet_count (int) - count of all sheets;
            title (str) - title of schematic;
            date (str) - date from title block;
            rev (srt) - revision of schematic;
            comp (str) - company name;
            comment1 (str) - comment #1 (GOST - decimal number);
            comment2 (str) - comment #2 (GOST - developer);
            comment3 (str) - comment #3 (GOST - verfier);
            comment4 (str) - comment #4 (GOST - approver);

        """

        def __init__(self, str_descr):
            """
            Extracts title block description form strings.

                Arguments:

                str_descr (str) - text lines read from KiCAD Schematic file.

            """
            lines = str_descr.splitlines()
            for line in lines:
                parts = split_line(line)
                if parts[0] == '$Descr':
                    if parts[-1] == 'portrait':
                        self.portrait = True
                    else:
                        self.portrait = False
                    self.sheet_format = parts[1]
                    self.sheet_size_x = int(parts[2])
                    self.sheet_size_y = int(parts[3])
                if parts[0] == 'encoding':
                    self.encoding = parts[1]
                if parts[0] == 'Sheet':
                    self.sheet_number = int(parts[1])
                    self.sheet_count = int(parts[2])
                items = ('Title', 'Date', 'Rev', 'Comp', \
                         'Comment1', 'Comment2', 'Comment3', 'Comment4')
                for item in items:
                    if parts[0] == item:
                        setattr(self, item.lower(), parts[1])

        def save(self, sch_file):
            """
            Save title block description to Schematic file.

                Arguments:

                sch_file (file) - file for writing.

            """
            descr = '$Descr ' + self.sheet_format + ' ' + \
                    str(self.sheet_size_x) + ' ' + str(self.sheet_size_y)
            if self.portrait:
                descr += ' portrait'
            descr += '\n'
            descr += 'encoding ' + self.encoding + '\n'
            descr += 'Sheet ' + \
                    str(self.sheet_number) + ' ' + \
                    str(self.sheet_count) + '\n'
            items = ('Title', 'Date', 'Rev', 'Comp', \
                     'Comment1', 'Comment2', 'Comment3', 'Comment4')
            for item in items:
                item_val = getattr(self, item.lower())
                descr += item + ' "' + item_val + '"\n'
            descr += '$EndDescr\n'
            sch_file.write(descr.decode('utf-8'))

    class Comp:
        """
        Description of the component.

            Attributes:

            name (str) - name of the component;
            ref (str) - reference of the component;
            unit (str) - part of the component;
            convert (boot) - True - show as De Morgan convert, False - normal;
            timestamp (str) - timestamp of component;
            pos_x (int) - horizontal position of component;
            pos_y (int) - vertical position of component;
            fields (list of Field) - list of fields of the element;
            orient_matrix (tuple of 4 ints) - rotation matrix.

        """

        def __init__(self, str_comp):
            """
            Create description of component from strings.

                Arguments:

                str_comp (str) - text lines read from KiCAD Schematic file.

            """
            lines = str_comp.splitlines()
            self.fields = []
            for line in lines:
                parts = split_line(line)
                if parts[0] == 'L':
                    self.name = parts[1]
                    self.ref = parts[2]
                elif parts[0] == 'U':
                    self.unit = parts[1]
                    self.convert = (int(parts[2]) == 2)
                    self.timestamp = parts[3]
                elif parts[0] == 'P':
                    self.pos_x = int(parts[1])
                    self.pos_y = int(parts[2])
                elif parts[0] == 'F':
                    self.fields.append(self.Field(line))
                elif parts[0].startswith('\t'):
                    # Skip 1st line that starts with tab - redundant: not used
                    if line == '\t1    ' + str(self.pos_x) + \
                               (4 - len(str(self.pos_x))) *  ' ' + ' ' + \
                               str(self.pos_y) + \
                               (4 - len(str(self.pos_y))) *  ' ':
                        pass
                    else:
                        line = line.lstrip('\t')
                        line = split_line(line)
                        self.orient_matrix = (int(line[0]), int(line[1]), \
                                              int(line[2]), int(line[3]))

        def save(self, sch_file):
            """
            Save description of the component to Schematic file.

                Arguments:

                sch_file (file) - file for writing.

            """
            comp_str = '$Comp\n'
            comp_str += 'L ' + self.name + ' ' + self.ref + '\n'
            comp_str += 'U ' + self.unit
            if self.convert:
                comp_str += ' 2'
            else:
                comp_str += ' 1'
            comp_str += ' ' + self.timestamp + '\n'
            comp_str += 'P ' + str(self.pos_x) + ' ' + str(self.pos_y) + '\n'
            sch_file.write(comp_str.decode('utf-8'))
            for field in self.fields:
                field.save(sch_file)
            comp_str = '\t1    '
            comp_str += str(self.pos_x) + (4 - len(str(self.pos_x))) * ' '
            comp_str += ' ' + str(self.pos_y) + (4 - len(str(self.pos_y))) * ' '
            comp_str += '\n'
            comp_str += '\t'
            for item in self.orient_matrix:
                comp_str += str(item) + (4 - len(str(item))) * ' '
                if self.orient_matrix.index(item) != \
                   len(self.orient_matrix) - 1:
                    comp_str += ' '
            comp_str += '\n$EndComp\n'
            sch_file.write(comp_str.decode('utf-8'))

        class Field:
            """
            Description of the field of the component.

                Attributes:

                number (int) - number of the field:
                    0 - reference;
                    1 - value;
                    2 - pcb footprint;
                    3 - doc link;
                    4, 5, ... - user specified;
                text (str) - text of field;
                orientation (str) - 'H' - horizontal, 'V' - vertical;
                pos_x (int) - horizontal position of the field;
                pos_y (int) - vertical position of the field;
                size (int) - size of the text;
                flags (str) - string of flags;
                hjustify (str) - horizontal justify;
                vjustify (str) - vertical justify;
                    (h, v)justify can be:
                        'L' - left;
                        'C' - center;
                        'R' - right;
                        'B' - bottom;
                        'T' - top;
                italic (bool) - if True - text is italic;
                bold (bool) - if True - text is bold;
                name (str) - name of the field (only if it is not default
            name).

            """

            def __init__(self, str_field):
                """
                Create description of the field from string.

                    Arguments:

                    str_field (str) - text line from KiCAD Schematic file.

                """
                items = split_line(str_field)
                self.number = int(items[1])
                if len(items) == 11:
                    self.name = items[10]
                temp = items[9]
                items = items[2:9]
                self.vjustify = temp[0]
                if temp[1] == 'N':
                    self.italic = False
                else:
                    self.italic = True
                if temp[2] == 'N':
                    self.bold = False
                else:
                    self.bold = True
                item_names = ('text', 'orientation', 'pos_x', 'pos_y', \
                              'size', 'flags', 'hjustify')
                for item in range(len(item_names)):
                    setattr(self, item_names[item], items[item])
                self.pos_x = int(self.pos_x)
                self.pos_y = int(self.pos_y)
                self.size = int(self.size)

            def save(self, sch_file):
                """
                Save description of the field to Schematic file.

                    Arguments:

                    sch_file (file) - file for writing.

                """
                field_str = 'F '
                field_str += str(self.number)
                field_str += ' "' + self.text + '"'
                field_str += ' ' + self.orientation
                field_str += ' ' + str(self.pos_x)
                field_str += ' ' + str(self.pos_y)
                field_str += ' ' + str(self.size)
                field_str += ' ' + self.flags
                field_str += ' ' + self.hjustify
                field_str += ' ' + self.vjustify
                if self.italic:
                    field_str += 'I'
                else:
                    field_str += 'N'
                if self.bold:
                    field_str += 'B'
                else:
                    field_str += 'N'
                if hasattr(self, 'name'):
                    field_str += ' "' + self.name + '"'
                field_str += '\n'
                sch_file.write(field_str.decode('utf-8'))

    class Sheet:
        """
        Description of the hierarchical sheet.

            Attributes:

            name (str) - name of the hierarchical sheet;
            name_size (int) - size of the text 'name';
            file_name (str) - name of the hierarchical sheet file;
            file_name_size (int) - size of the text 'file_name';
            pos_x (int) - horizontal position of the hierarchical sheet;
            pos_y (int) - vertical position of the hierarchical sheet;
            dim_x (int) - horizontal dimension of the hierarchical sheet;
            dim_y (int) - vertical dimension of the hierarchical sheet;
            timestamp (str) - time stamp;
            fields (list of Field) - list of fields of the hierarchical sheet.

        """

        def __init__(self, str_sheet):
            """
            Create description of hierarchical sheet from strings.

                Arguments:

                str_sheet (str) - text lines read from KiCAD Schematic file.

            """
            lines = str_sheet.splitlines()
            self.fields = []
            for line in lines:
                parts = split_line(line)
                if parts[0] == 'S':
                    self.pos_x = parts[1]
                    self.pos_y = parts[2]
                    self.dim_x = parts[3]
                    self.dim_y = parts[4]
                elif parts[0] == 'U':
                    self.timestamp = parts[1]
                elif parts[0].startswith('F'):
                    if int(parts[0][1]) == 0:
                        self.name = parts[1]
                        self.name_size = parts[2]
                    elif int(parts[0][1]) == 1:
                        self.file_name = parts[1]
                        self.file_name_size = parts[2]
                    elif int(parts[0][1]) > 1:
                        self.fields.append(self.Field(line))

        def save(self, sch_file):
            """
            Save description of the hierarchical sheet to Schematic file.

                Arguments:

                sch_file (file) - file for writing.

            """
            sheet_str = '$Sheet\n'
            sheet_str += 'S ' + self.pos_x + ' ' + self.pos_y + ' ' + \
                         self.dim_x + ' ' + self.dim_y + '\n'
            sheet_str += 'U ' + self.timestamp + '\n'
            sheet_str += 'F0 "' + self.name + '" ' + str(self.name_size) + '\n'
            sheet_str += 'F1 "' + self.file_name + '" ' + \
                        str(self.file_name_size) + '\n'
            sch_file.write(sheet_str.decode('utf-8'))
            for field in self.fields:
                field.save(sch_file)
            sheet_str = '$EndSheet\n'
            sch_file.write(sheet_str.decode('utf-8'))

        class Field:
            """
            Description of field of the hierarchical sheet.

                Attributes:

                number (int) - number of the field (starts from 2);
                text (str) - text of field;
                form (str) - field format:
                    'I' - input;
                    'O' - output;
                    'B' - bidirectional;
                    'T' - tri state;
                    'U' - unspecified;
                side (str) - side of the field:
                    'L' - left;
                    'R' - right;
                    'T' - top;
                    'B' - bottom;
                pos_x (int) - horizontal position of the field;
                pos_y (int) - vertical position of the field;
                dimension (int) - dimension of the field;

            """

            def __init__(self, str_field):
                """
                Create description of the field from string.

                    Arguments:

                    str_field (str) - text line from KiCAD Schematic file.

                """
                items = split_line(str_field)
                self.number = items[0][1:]
                self.text = items[1]
                self.form = items[2]
                self.side = items[3]
                self.pos_x = int(items[4])
                self.pos_y = int(items[5])
                self.dimension = int(items[6])

            def save(self, sch_file):
                """
                Save description of the field to Schematic file.

                    Arguments:

                    sch_file (file) - file for writing.

                """
                field_str = 'F'
                field_str += ' ' + str(self.number)
                field_str += ' "' + self.text + '"'
                field_str += ' ' + self.form
                field_str += ' ' + self.side
                field_str += ' ' + str(self.pos_x)
                field_str += ' ' + str(self.pos_y)
                field_str += ' ' + str(self.dimension)
                field_str += '\n'
                sch_file.write(field_str.decode('utf-8'))

    class Bitmap:
        """
        Description of the bitmap.

            Attributes:

            pos_x (int) - horizontal position of the bitmap;
            pos_y (int) - vertical position of the bitmap;
            scale (float) - scale of the bitmap;
            data (list of int) - byte array of the png data.

        """

        def __init__(self, str_bitmap):
            """
            Create description of bitmap from strings.

                Arguments:

                str_bitmap (str) - text lines read from KiCAD Schematic file.

            """
            lines = str_bitmap.splitlines()
            self.data = []
            data_block = False
            for line in lines:
                if data_block:
                    if line.startswith('EndData'):
                        break
                    line = line.rstrip(' ')
                    bytes = split_line(line)
                    for byte in bytes:

                        if byte == '$EndBitmap':
                            continue  # EESchema bug fix

                        self.data.append(int(byte, 16))
                elif line.startswith('Pos'):
                    parts = split_line(line)
                    self.pos_x = parts[1]
                    self.pos_y = parts[2]
                elif line.startswith('Scale'):
                    parts = split_line(line)
                    self.scale = float(parts[1].replace(',', '.'))
                elif line.startswith('Data'):
                    data_block = True

        def save(self, sch_file):
            """
            Save description of the bitmap to Schematic file.

                Arguments:

                sch_file (file) - file for writing.

            """
            bitmap_str = '$Bitmap\n'
            bitmap_str += 'Pos ' + str(self.pos_x) + ' ' + \
                         str(self.pos_y) + '\n'
            bitmap_str += 'Scale ' + \
                         "{:.6f}".format(self.scale).replace('.', ',') + '\n'
            bitmap_str += 'Data\n'
            i = 0
            for byte in self.data:
                i = i + 1
                bitmap_str += '{:02X}'.format(byte) + ' '
                if i % 32 == 0:
                    bitmap_str += '\n'
            bitmap_str += '\nEndData\n'
            bitmap_str += '$EndBitmap\n'
            sch_file.write(bitmap_str.decode('utf-8'))

    class Connection:
        """
        Description of the connection or no connection position.

            Attributes:

            tpye (str) - type of the connection;
            pos_x (int) - horizontal position of the connection;
            pos_y (int) - vertical position of the connection.

        """

        def __init__(self, str_connection):
            """
            Create description of the connection from string.

                Arguments:

                str_connect (str) - text line read from KiCAD Schematic.

            """
            str_connection.replace('\n', '')
            parts = split_line(str_connection)
            self.type = parts[0]
            self.pos_x = int(parts[2])
            self.pos_y = int(parts[3])

        def save(self, sch_file):
            """
            Save description of the connection to Schematic file.

                Arguments:

                sch_file (file) - file for writing;

            """
            connection_str = self.type + ' ~ ' + str(self.pos_x) + ' ' + \
                             str(self.pos_y) + '\n'
            sch_file.write(connection_str.decode('utf-8'))

    class Text:
        """
        Description of the text label.

            Attributes:

            type (str) - type of the text label;
            text (str) - text of the label;
            pos_x (int) - horizontal position of the text label;
            pos_y (int) - vertical position of the text label;
            orientation (int) - orientation of the text label;
            dimension (int) - dimension of the text label;
            shape (str) - shape type of the text label (only for GLabel and
        HLabel);
            italic (bool) - True - if text is italic;
            bold (int) - coefficient of the bold text.

        """

        def __init__(self, str_text):
            """
            Create description of the text label from string.

                Arguments:

                str_connect (str) - text line read from KiCAD Schematic.

            """
            lines = str_text.splitlines()
            parts = split_line(lines[0])
            self.type = parts[1]
            self.pos_x = int(parts[2])
            self.pos_y = int(parts[3])
            self.orientation = int(parts[4])
            self.dimension = int(parts[5])
            if parts[1] == 'GLabel' or parts[1] == 'HLabel':
                self.shape = parts[6]
            self.italic = parts[-2] == 'Italic'
            self.bold = int(parts[-1])
            self.text = lines[1]

        def save(self, sch_file):
            """
            Save description of the text label to Schematic file.

                Arguments:

                sch_file (file) - file for writing;

            """
            text_str = 'Text ' + self.type + ' ' + str(self.pos_x) + ' ' + \
                       str(self.pos_y) + ' ' + str(self.orientation) + ' ' +\
                       str(self.dimension)
            if type == 'GLabel' or type == 'HLabel':
                text_str += ' ' + self.shape
            if self.italic:
                text_str += ' Italic'
            else:
                text_str += ' ~'
            text_str += ' ' + str(self.bold) + '\n'
            text_str += self.text + '\n'
            sch_file.write(text_str.decode('utf-8'))

    class Wire:
        """
        Description of the wire.

            Attributes:

            type (str) - type of the wire;
            start_x (int) - horizontal coordinates of the start position;
            start_y (int) - vertical coordinates of the start position;
            end_x (int) - horizontal coordinates of the end position;
            end_y (int) - vertical coordinates of the end position.

        """

        def __init__(self, str_wire):
            """
            Create description of the wire from string.

                Arguments:

                str_connect (str) - text line read from KiCAD Schematic.

            """
            lines = str_wire.splitlines()
            self.type = lines[0].lstrip('Wire').lstrip(' ')

            parts = split_line(lines[1])
            self.start_x = int(parts[0].lstrip('\t'))
            self.start_y = int(parts[1])
            self.end_x = int(parts[2])
            self.end_y = int(parts[3])

        def save(self, sch_file):
            """
            Save description of the wire to Schematic file.

                Arguments:

                sch_file (file) - file for writing;

            """
            wire_str = 'Wire ' + self.type + '\n'
            wire_str += '\t' + str(self.start_x) + ' ' + str(self.start_y) + \
                        ' ' + str(self.end_x) + ' ' + str(self.end_y) + '\n'
            sch_file.write(wire_str.decode('utf-8'))

    class Entry:
        """
        Description of the entry.

            Attributes:

            start_x (int) - horizontal coordinates of the start position;
            start_y (int) - vertical coordinates of the start position;
            end_x (int) - horizontal coordinates of the end position;
            end_y (int) - vertical coordinates of the end position.

        """

        def __init__(self, str_entry):
            """
            Create description of the entry from string.

                Arguments:

                str_connect (str) - text line read from KiCAD Schematic.

            """
            lines = str_entry.splitlines()
            self.type = lines[0].lstrip('Entry ')
            parts = split_line(lines[1])
            self.start_x = int(parts[0].lstrip('\t'))
            self.start_y = int(parts[1])
            self.end_x = int(parts[2])
            self.end_y = int(parts[3])

        def save(self, sch_file):
            """
            Save description of the entry to Schematic file.

                Arguments:

                sch_file (file) - file for writing;

            """
            wire_str = 'Entry ' + self.type + '\n'
            wire_str += '\t' + str(self.start_x) + ' ' + str(self.start_y) + \
                        ' ' + str(self.end_x) + ' ' + str(self.end_y) + '\n'
            sch_file.write(wire_str.decode('utf-8'))


class Library:
    """
    Implementation of KiCAD Schematic library.

    """
    ID = 'EESchema-LIBRARY'

    def __init__(self, lib_name):
        """
        Load all contents from KiCAD's Schematic library.

            Attributes:

            lib_name (str) - full name of KiCAD Schematic library file;
            version (float) - version of file format;
            date (str) - date of last changes;
            encoding (srt) - encoding of text;
            components (list of Component) - list of components of library.

        """
        self.lib_name = lib_name
        self.load()

    def load(self):
        """
        Open KiCAD Schematic library file and read all information from it.

        """
        self.components = []

        lib_file = codecs.open(self.lib_name, 'r', 'utf-8')
        first_line = lib_file.readline().encode('utf-8')
        first_line = first_line.replace('\n', '')
        if first_line.startswith(self.ID):
            self.version = float(split_line(first_line)[2])
            date_index = first_line.index('Date: ') + len('Date: ')
            self.date = first_line[date_index:]
        else:
            return
        for lib_line in lib_file:
            lib_line = lib_line.encode('utf-8')
            if lib_line.startswith('DEF'):
                component_value = ''
                while not lib_line.startswith('ENDDEF'):
                    component_value += lib_line
                    lib_line = lib_file.readline().encode('utf-8')
                self.components.append(self.Component(component_value))
            elif lib_line.startswith('#encoding'):
                self.encoding = split_line(lib_line)[-1].replace('\n', '')
            elif lib_line.startswith('#End Library'):
                    return

    def save(self):
        """
        Save all content to KiCAD Schematic library file.

        """
        lib_file = codecs.open(self.lib_name, 'w', 'utf-8')

        header = '{} Version {:.1f} Date: {}\n'.format(self.ID, self.version, self.date)
        header += '#encoding {}\n'.format(self.encoding)
        lib_file.write(header.decode('utf-8'))

        for components in self.components:
            components.save(lib_file)

        lib_file.write(u'#\n#End Library\n')
        lib_file.close()

    class Component:
        """
        Description of the component of a library.

            Attributes:

            name (str) - component name in library;
            reference (str) - reference of component;
            text_offset (int) - offset for pin name position;
            draw_pinnumber (bool) - True - display number, False - do not display number;
            draw_pinname (bool) - True - display name, False do not display name;
            unit_count (int) - number of part (or section) in component;
            units_locked (bool) - True - units are not identical and cannot be swapped,
        False - units are identical and therefore can be swapped;
            option_flag (str) - 'N' - normal, 'P' - component type "power";
            fields (list of Field) - list of component fields;
            aliases (list of str) - list of aliases (exists only if the component has alias names);
            fplist (list of str) - list of footprints assigned to component (if specified);
            graphic_elements (list of Polygon, Rectangle, Circle, Arc, Text, Pin) - list of all graphical
        elements of a component.

        """

        def __init__(self, str_component):
            """
            Create description of library component from strings.

                Arguments:

                str_component (str) - text lines read from KiCAD Schematic library file.

            """
            lines = str_component.splitlines()
            self.aliases = []
            self.fields = []
            self.graphic_elements = []
            footprint = False
            for line in lines:
                parts = split_line(line)
                if footprint:
                    if parts[0] == '$ENDFPLIST':
                        footprint = False
                        continue
                    else:
                        self.fplist.append(parts[0])
                        continue
                if parts[0] == 'DEF':
                    self.name = parts[1]
                    self.reference = parts[2]
                    self.text_offset = int(parts[4])
                    if parts[5] == 'Y':
                        self.draw_pinnumber = True
                    elif parts[5] == 'N':
                        self.draw_pinnumber = False
                    if parts[6] == 'Y':
                        self.draw_pinname = True
                    elif parts[6] == 'N':
                        self.draw_pinname = False
                    self.unit_count = int(parts[7])
                    if parts[8] == 'L':
                        self.units_locked = True
                    elif parts[8] == 'F':
                        self.units_locked = False
                    self.option_flag = parts[9]
                elif parts[0] == 'ALIAS':
                    self.aliases = parts[1:]
                elif parts[0].startswith('F'):
                    self.fields.append(self.Field(line))
                elif parts[0] == 'P':
                    self.graphic_elements.append(self.Polygon(line))
                elif parts[0] == 'S':
                    self.graphic_elements.append(self.Rectangle(line))
                elif parts[0] == 'C':
                    self.graphic_elements.append(self.Circle(line))
                elif parts[0] == 'A':
                    self.graphic_elements.append(self.Arc(line))
                elif parts[0] == 'T':
                    self.graphic_elements.append(self.Text(line))
                elif parts[0] == 'X':
                    self.graphic_elements.append(self.Pin(line))
                elif parts[0] == '$FPLIST':
                    footprint = True
                    self.fplist = []

        def save(self, lib_file):
            """
            Save description of the component to Schematic library file.

                Arguments:

                lib_file (file) - file for writing.

            """
            component_str = '#\n# {}\n#\n'.format(self.name)
            component_str += 'DEF {0} {1} {2} {3} {4} {5} {6} {7} {8}\n'.format(
                self.name,
                self.reference,
                '0',
                str(self.text_offset),
                {True:'Y', False:'N'}[self.draw_pinnumber],
                {True:'Y', False:'N'}[self.draw_pinname],
                str(self.unit_count),
                {True:'L', False:'F'}[self.units_locked],
                self.option_flag
                )
            lib_file.write(component_str.decode('utf-8'))
            for field in self.fields:
                field.save(lib_file)
            component_str = 'ALIAS ' + ' '.join(self.aliases) + '\n'
            if hasattr(self, 'fplist'):
                component_str += '$FPLIST\n'
                for fp in self.fplist:
                    component_str += ' {}\n'.format(fp)
                component_str += '$ENDFPLIST\n'
            component_str += 'DRAW\n'
            lib_file.write(component_str.decode('utf-8'))
            for graphic_element in self.graphic_elements:
                graphic_element.save(lib_file)
            component_str = 'ENDDRAW\nENDDEF\n'
            lib_file.write(component_str.decode('utf-8'))


        class Field:
            """
            Description of the field of the library component.

                Attributes:

                number (int) - number of the field:
                    0 - reference;
                    1 - name;
                    2 - pcb footprint;
                    3 - doc link;
                    4, 5, ... - user specified;
                text (str) - text of field;
                pos_x (int) - horizontal position of the field;
                pos_y (int) - vertical position of the field;
                diamension (int) - diamension of the text;
                orientation (str) - 'H' - horizontal, 'V' - vertical;
                visibility (bool) - True - text is visible, False - text is invisible;
                hjustify (str) - horizontal justify;
                vjustify (str) - vertical justify;
                    (h, v)justify can be:
                        'L' - left;
                        'R' - right;
                        'C' - center;
                        'B' - bottom;
                        'T' - top;
                italic (bool) - if True - text is italic;
                bold (bool) - if True - text is bold;
                name (str) - name of the field (only if it is not default
            name).

            """

            def __init__(self, str_field):
                """
                Create description of the field from string.

                    Arguments:

                    str_field (str) - text line from KiCAD Schematic library file.

                """
                items = split_line(str_field)
                self.number = int(items[0][1:])
                if len(items) == 10:
                    self.name = items[9]
                temp = items[8]
                items = items[1:8]
                self.vjustify = temp[0]
                if temp[1] == 'N':
                    self.italic = False
                else:
                    self.italic = True
                if temp[2] == 'N':
                    self.bold = False
                else:
                    self.bold = True
                item_names = ('text', 'pos_x', 'pos_y', 'diamension', \
                              'orientation', 'visibility', 'hjustify')
                for item in range(len(item_names)):
                    setattr(self, item_names[item], items[item])
                self.pos_x = int(self.pos_x)
                self.pos_y = int(self.pos_y)
                self.diamension = int(self.diamension)
                if self.visibility == 'V':
                    self.visibility = True
                elif self.visibility == 'I':
                    self.visibility = False

            def save(self, lib_file):
                """
                Save description of the field to Schematic file.

                    Arguments:

                    lib_file (file) - file for writing.

                """
                field_str = 'F'
                field_str += str(self.number)
                field_str += ' "' + self.text + '"'
                field_str += ' ' + str(self.pos_x)
                field_str += ' ' + str(self.pos_y)
                field_str += ' ' + str(self.diamension)
                field_str += ' ' + self.orientation
                if self.visibility:
                    field_str += ' V'
                else:
                    field_str += ' I'
                field_str += ' ' + self.hjustify
                field_str += ' ' + self.vjustify
                if self.italic:
                    field_str += 'I'
                else:
                    field_str += 'N'
                if self.bold:
                    field_str += 'B'
                else:
                    field_str += 'N'
                if hasattr(self, 'name'):
                    field_str += ' "' + self.name + '"'
                field_str += '\n'
                lib_file.write(field_str.decode('utf-8'))

        class Polygon:
            """
            Description of the polygon.

                Attributes:

                unit (int) - 0 if common to the parts; if not, number of part (1. .n);
                convert (int) - 0 if common to the 2 representations, if not 1 or 2;
                thickness (int) - line thickness;
                points (list of [x(int), y(int)]) - list of x and y coordinates of points;
                fill (str) - F - fill foreground, f - fill background, N - do not fill.

            """

            def __init__(self, str_polygon):
                """
                Create description of the polygon.

                    Arguments:

                    str_polygon (str) - text line from KiCAD Schematic library file.

                """
                items = split_line(str_polygon)
                self.unit = int(items[2])
                self.convert = int(items[3])
                self.thickness = int(items[4])
                point_index = 5
                self.points = []
                for point in range(int(items[1])):
                    x = items[point_index]
                    y = items[point_index + 1]
                    self.points.append([x, y])
                    point_index += 2
                self.fill = items[-1]

            def save(self, lib_file):
                """
                Save description of the polygon to Schematic library file.

                    Arguments:

                    lib_file (file) - file for writing.

                """
                polygon_str = 'P '
                polygon_str += str(len(self.points))
                polygon_str += ' ' + str(self.unit)
                polygon_str += ' ' + str(self.convert)
                polygon_str += ' ' + str(self.thickness)
                for point in self.points:
                    polygon_str += ' {} {}'.format(point[0], point[1])
                polygon_str += ' ' + self.fill
                polygon_str += '\n'
                lib_file.write(polygon_str.decode('utf-8'))

        class Rectangle:
            """
            Description of the rectangle.

                Attributes:

                start_x (int) - x coordinate of rectangle start;
                start_y (int) - y coordinate of rectangle start;
                end_x (int) - x coordinate of rectangle end;
                end_y (int) - y coordinate of rectangle end;
                unit (int) - 0 if common to the parts; if not, number of part (1. .n);
                convert (int) - 0 if common to the 2 representations, if not 1 or 2;
                thickness (int) - line thickness;
                fill (str) - F - fill foreground, f - fill background, N - do not fill.

            """

            def __init__(self, str_rectangle):
                """
                Create description of the rectangle.

                    Arguments:

                    str_rectangle (str) - text line from KiCAD Schematic library file.

                """
                items = split_line(str_rectangle)
                self.start_x = int(items[1])
                self.start_y = int(items[2])
                self.end_x = int(items[3])
                self.end_y = int(items[4])
                self.unit = int(items[5])
                self.convert = int(items[6])
                self.thickness = int(items[7])
                self.fill = items[8]

            def save(self, lib_file):
                """
                Save description of the rectangle to Schematic library file.

                    Arguments:

                    lib_file (file) - file for writing.

                """
                rectangle_str = 'S'
                rectangle_str += ' ' + str(self.start_x)
                rectangle_str += ' ' + str(self.start_y)
                rectangle_str += ' ' + str(self.end_x)
                rectangle_str += ' ' + str(self.end_y)
                rectangle_str += ' ' + str(self.unit)
                rectangle_str += ' ' + str(self.convert)
                rectangle_str += ' ' + str(self.thickness)
                rectangle_str += ' ' + self.fill
                rectangle_str += '\n'
                lib_file.write(rectangle_str.decode('utf-8'))

        class Circle:
            """
            Description of the circle.

                Attributes:

                pos_x (int) - x coordinate of circle center position;
                pos_y (int) - y coordinate of circle center position;
                radius (int) - radius of circle;
                unit (int) - 0 if common to the parts; if not, number of part (1. .n);
                convert (int) - 0 if common to the 2 representations, if not 1 or 2;
                thickness (int) - line thickness;
                fill (str) - F - fill foreground, f - fill background, N - do not fill.

            """

            def __init__(self, str_circle):
                """
                Create description of the circle.

                    Arguments:

                    str_circle (str) - text line from KiCAD Schematic library file.

                """
                items = split_line(str_circle)
                self.pos_x = int(items[1])
                self.pos_y = int(items[2])
                self.radius = int(items[3])
                self.unit = int(items[4])
                self.convert = int(items[5])
                self.thickness = int(items[6])
                self.fill = items[7]

            def save(self, lib_file):
                """
                Save description of the circle to Schematic library file.

                    Arguments:

                    lib_file (file) - file for writing.

                """
                circle_str = 'C'
                circle_str += ' ' + str(self.pos_x)
                circle_str += ' ' + str(self.pos_y)
                circle_str += ' ' + str(self.radius)
                circle_str += ' ' + str(self.unit)
                circle_str += ' ' + str(self.convert)
                circle_str += ' ' + str(self.thickness)
                circle_str += ' ' + self.fill
                circle_str += '\n'
                lib_file.write(circle_str.decode('utf-8'))

        class Arc:
            """
            Description of the arc.

                Attributes:

                pos_x (int) - x coordinate of arc center position;
                pos_y (int) - y coordinate of arc center position;
                radius (int) - radius of arc;
                start (int) - angle of the starting point (in 0,1 degrees);
                end (int) - angle of the end point (in 0,1 degrees);
                unit (int) - 0 if common to the parts; if not, number of part (1. .n);
                convert (int) - 0 if common to the 2 representations, if not 1 or 2;
                thickness (int) - line thickness;
                fill (str) - F - fill foreground, f - fill background, N - do not fill;
                start_x (int) - x coordinate of the starting point (role similar to start);
                start_y (int) - y coordinate of the starting point (role similar to start);
                end_x (int) - x coordinate of the ending point (role similar to end);
                end_y (int) - y coordinate of the ending point (role similar to end).

            """

            def __init__(self, str_arc):
                """
                Create description of the arc.

                    Arguments:

                    str_arc (str) - text line from KiCAD Schematic library file.

                """
                items = split_line(str_arc)
                self.pos_x = int(items[1])
                self.pos_y = int(items[2])
                self.radius = int(items[3])
                self.start = int(items[4])
                self.end = int(items[5])
                self.unit = int(items[6])
                self.convert = int(items[7])
                self.thickness = int(items[8])
                self.fill = items[9]
                self.start_x = int(items[10])
                self.start_y = int(items[11])
                self.end_x = int(items[12])
                self.end_y = int(items[13])

            def save(self, lib_file):
                """
                Save description of the arc to Schematic library file.

                    Arguments:

                    lib_file (file) - file for writing.

                """
                arc_str = 'A'
                arc_str += ' ' + str(self.pos_x)
                arc_str += ' ' + str(self.pos_y)
                arc_str += ' ' + str(self.radius)
                arc_str += ' ' + str(self.start)
                arc_str += ' ' + str(self.end)
                arc_str += ' ' + str(self.unit)
                arc_str += ' ' + str(self.convert)
                arc_str += ' ' + str(self.thickness)
                arc_str += ' ' + self.fill
                arc_str += ' ' + str(self.start_x)
                arc_str += ' ' + str(self.start_y)
                arc_str += ' ' + str(self.end_x)
                arc_str += ' ' + str(self.end_y)
                arc_str += '\n'
                lib_file.write(arc_str.decode('utf-8'))

        class Text:
            """
            Description of the text.

                Attributes:

                angle (int) - angle of the text (in 0,1 degrees);
                pos_x (int) - x coordinate of text position;
                pos_y (int) - y coordinate of text position;
                size (int) - size of text;
                unit (int) - 0 if common to the parts; if not, number of part (1. .n);
                convert (int) - 0 if common to the 2 representations, if not 1 or 2;
                text (str) - text;
                italic (bool) - True - text is italic, False - text is normal;
                bold (bool) - True - text is bold, False - text is normal;
                hjustify (str) - horizontal justify:
                        'L' - left;
                        'C' - center;
                        'R' - right;
                vjustify (str) - vertical justify;
                        'B' - bottom;
                        'C' - center;
                        'T' - top.

            """

            def __init__(self, str_text):
                """
                Create description of the text.

                    Arguments:

                    str_text (str) - text line from KiCAD Schematic library file.

                """
                items = split_line(str_text)
                self.angle = int(items[1])
                self.pos_x = int(items[2])
                self.pos_y = int(items[3])
                self.size = int(items[4])
                self.unit = int(items[6])
                self.convert = int(items[7])
                self.text = items[8]
                if items[9] == 'Italic':
                    self.italic = True
                elif items[9] == 'Normal':
                    self.italic = False
                if items[10] == '1':
                    self.bold = True
                elif items[10] == '0':
                    self.bold = False
                self.hjustify = items[11]
                self.vjustify = items[12]

            def save(self, lib_file):
                """
                Save description of the text to Schematic library file.

                    Arguments:

                    lib_file (file) - file for writing.

                """
                text_str = 'T'
                text_str += ' ' + str(self.angle)
                text_str += ' ' + str(self.pos_x)
                text_str += ' ' + str(self.pos_y)
                text_str += ' ' + str(self.size)
                text_str += ' 0'
                text_str += ' ' + str(self.unit)
                text_str += ' ' + str(self.convert)
                text_str += ' "{}"'.format(self.text)
                if self.italic:
                    text_str += ' Italic'
                else:
                    text_str += ' Normal'
                if self.bold:
                    text_str += ' 1'
                else:
                    text_str += ' 0'
                text_str += ' ' + self.hjustify
                text_str += ' ' + self.vjustify
                text_str += '\n'
                lib_file.write(text_str.decode('utf-8'))

        class Pin:
            """
            Description of the pin.

                Attributes:

                name (str) - name of the pin;
                number (int) - number of the pin;
                pos_x (int) - x coordinate of pin position;
                pos_y (int) - y coordinate of pin position;
                length (int) - length of the pin;
                orientation (str) - orientation of the pin:
                    'U' - up;
                    'D' - down;
                    'L' - left;
                    'R' - right;
                number_size (int) - size of number text label;
                name_size (int) - size of name text label;
                unit (int) - 0 if common to the parts; if not, number of part (1. .n);
                convert (int) - 0 if common to the 2 representations, if not 1 or 2;
                electric_type (str) - electric type:
                    'I' - input;
                    'O' - output;
                    'B' - BiDi;
                    'T' - tristate;
                    'P' - passive;
                    'U' - unspecified;
                    'W' - power input;
                    'w' - power output;
                    'C' - open collector;
                    'E' - open emitter;
                    'N' - not connected;
                shape (str) - if present:
                    'I' - inverted;
                    'C' - clock;
                    'CI' - inverted clock;
                    'L' - input low;
                    'CL' - clock low;
                    'V' - output low;
                    'F' - falling adge low;
                    'X' - non logic;
                    if invisible pin, the shape identifier starts by 'N'

            """

            def __init__(self, str_pin):
                """
                Create description of the pin.

                    Arguments:

                    str_pin (str) - text line from KiCAD Schematic library file.

                """
                items = split_line(str_pin)
                self.name = items[1]
                self.number = int(items[2])
                self.pos_x = int(items[3])
                self.pos_y = int(items[4])
                self.length = int(items[5])
                self.orientation = items[6]
                self.number_size = int(items[7])
                self.name_size = int(items[8])
                self.unit = int(items[9])
                self.convert = int(items[10])
                self.electric_type = items[11]
                if len(items) == 13:
                    self.shape = items[12]

            def save(self, lib_file):
                """
                Save description of the text to Schematic library file.

                    Arguments:

                    lib_file (file) - file for writing.

                """
                pin_str = 'X'
                pin_str += ' ' + self.name
                pin_str += ' ' + str(self.number)
                pin_str += ' ' + str(self.pos_x)
                pin_str += ' ' + str(self.pos_y)
                pin_str += ' ' + str(self.length)
                pin_str += ' ' + self.orientation
                pin_str += ' ' + str(self.number_size)
                pin_str += ' ' + str(self.name_size)
                pin_str += ' ' + str(self.unit)
                pin_str += ' ' + str(self.convert)
                pin_str += ' ' + self.electric_type
                if hasattr(self, 'shape'):
                    pin_str += ' ' + self.shape
                pin_str += '\n'
                lib_file.write(pin_str.decode('utf-8'))


def split_line(str_to_split):
    """
    Split string by whitespace considering text in quotes.

        Arguments:

        str_to_split (str) - string that must be splint.

        Returns:

        output (list of str) - list of strings.

    """
    items = str_to_split.split(' ')
    output = []
    quoted = False
    for item in items:
        if not quoted and item.startswith('"'):
            if item.endswith('"') and not item.endswith('\\"') and \
               len(item) > 1:
                quoted = False
                output.append(item[1:-1])
            else:
                quoted = True
                output.append(item[1:])
            continue
        elif quoted:
            if item.endswith('"') and not item.endswith('\\"'):
                quoted = False
                output[-1] += ' ' + item[:-1]
                continue
            else:
                output[-1] += ' ' + item
        else:
            if item:
                output.append(item)
    return output
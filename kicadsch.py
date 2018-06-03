#!/usr/bin/env python2
# -*-    Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4    -*-
### BEGIN LICENSE
# Copyright (C) 2017 Baranovskiy Konstantin (baranovskiykonstantin@gmail.com)
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

import codecs


class Schematic:
    """
    Implementation of KiCad Schematic diagram file.

    """
    EESCHEMA_FILE_STAMP = u'EESchema'
    SCHEMATIC_HEAD_STRING = u'Schematic File Version'

    def __init__(self, sch_name):
        """
        Load all contents from KiCad's Schematic file.

            Attributes:

            sch_name (unicode) - full name of KiCad Schematic file;
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
        Open KiCad Schematic file and read all information from it.

        """
        self.libs = self.Libs()
        self.eelayer = []
        self.items = []

        sch_file = codecs.open(self.sch_name, 'r', 'utf-8')
        first_line = sch_file.readline()
        first_line = first_line.replace(u'\n', u'')
        if first_line.startswith(self.EESCHEMA_FILE_STAMP):
            self.version = int(split_line(first_line)[-1])
        else:
            return
        for sch_line in sch_file:
            sch_line = sch_line
            if sch_line.startswith(u'$'):
                if sch_line.startswith(u'$EndSCHEMATC'):
                    return
                else:
                    item = sch_line
                    item_val = u''
                    while not sch_line.startswith(u'$End'):
                        item_val += sch_line
                        sch_line = sch_file.readline()
                    if item.startswith(u'$Descr'):
                        self.descr = self.Descr(item_val)
                    elif item.startswith(u'$Comp'):
                        self.items.append(self.Comp(item_val))
                    elif item.startswith(u'$Sheet'):
                        self.items.append(self.Sheet(item_val))
                    elif item.startswith(u'$Bitmap'):
                        self.items.append(self.Bitmap(item_val))
            elif sch_line.startswith(u'Connection'):
                self.items.append(self.Connection(sch_line))
            elif sch_line.startswith(u'NoConn'):
                self.items.append(self.Connection(sch_line))
            elif sch_line.startswith(u'Text'):
                sch_line += sch_file.readline()
                self.items.append(self.Text(sch_line))
            elif sch_line.startswith(u'Wire'):
                sch_line += sch_file.readline()
                self.items.append(self.Wire(sch_line))
            elif sch_line.startswith(u'Entry'):
                sch_line += sch_file.readline()
                self.items.append(self.Entry(sch_line))
            elif sch_line.startswith(u'LIBS:'):
                self.libs.add(sch_line)
            elif sch_line.startswith(u'EELAYER') and not u'END' in sch_line:
                    self.eelayer.append(self.Eelayer(sch_line))

    def save(self, new_name=None):
        """
        Save all content to KiCad Schematic file.

        """
        sch_file_name = self.sch_name
        if new_name:
            sch_file_name = new_name
        sch_file = codecs.open(sch_file_name, 'w', 'utf-8')

        first_line = u'{stamp} {head} {version}\n'.format(
                     stamp = self.EESCHEMA_FILE_STAMP,
                     head = self.SCHEMATIC_HEAD_STRING,
                     version = self.version
                     )
        sch_file.write(first_line)

        self.libs.save(sch_file)

        for eelayer in self.eelayer:
            eelayer.save(sch_file)
        sch_file.write(u'EELAYER END\n')

        self.descr.save(sch_file)

        for item in self.items:
            item.save(sch_file)

        sch_file.write(u'$EndSCHEMATC\n')
        sch_file.close()


    class Libs(list):
        """
        List of libraries used in schematic.

        """

        def add(self, str_lib):
            """
            Extracts library name from string and add it to the list.

                Arguments:

                str_lib (unicode) - text line read from KiCad Schematic file.

            """
            str_lib = str_lib.rstrip(u'\n')
            lib = str_lib.replace(u'LIBS:', u'', 1)
            self.append(lib)

        def save(self, sch_file):
            """
            Save current library name to KiCad Schematic file.

                Arguments:

                sch_file (file) - file for writing.

            """
            for lib in self:
                line = u'LIBS:{lib}\n'.format(
                       lib = lib
                       )
                sch_file.write(line)


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

                str_eelayer (unicode) - text line read from KiCad Schematic file.

            """
            str_eelayer = str_eelayer.lstrip(u'EELAYER ')
            parts = split_line(str_eelayer)
            self.nn = int(parts[0])
            self.mm = int(parts[1])

        def save(self, sch_file):
            """
            Save EELAYER description to KiCad Schematic file.

                Arguments:

                sch_file (file) - file for writing.

            """
            line = u'EELAYER {nn} {mm}\n'.format(
                   nn = self.nn,
                   mm = self.mm
                   )
            sch_file.write(line)


    class Descr:
        """
        Title block description.

            Attributes:

            sheet_format (unicode) - string of sheet format (A4...A0, A...E);
            sheet_size_x (int) - width of sheet in mils (1/1000 inch);
            sheet_size_y (int) - height of sheet in mils;
            portrait (bool) - if True - orientation is portrait;
            encoding (srt) - encoding of text;
            sheet_number (int) - number of current sheet;
            sheet_count (int) - count of all sheets;
            title (unicode) - title of schematic;
            date (unicode) - date from title block;
            rev (srt) - revision of schematic;
            comp (unicode) - company name;
            comment1 (unicode) - comment #1 (GOST - decimal number);
            comment2 (unicode) - comment #2 (GOST - developer);
            comment3 (unicode) - comment #3 (GOST - verfier);
            comment4 (unicode) - comment #4 (GOST - approver);

        """

        def __init__(self, str_descr):
            """
            Extracts title block description form strings.

                Arguments:

                str_descr (unicode) - text lines read from KiCad Schematic file.

            """
            lines = str_descr.splitlines()
            for line in lines:
                parts = split_line(line)
                if parts[0] == u'$Descr':
                    if parts[-1] == u'portrait':
                        self.portrait = True
                    else:
                        self.portrait = False
                    self.sheet_format = parts[1]
                    self.sheet_size_x = int(parts[2])
                    self.sheet_size_y = int(parts[3])
                elif parts[0] == u'encoding':
                    self.encoding = parts[1]
                elif parts[0] == u'Sheet':
                    self.sheet_number = int(parts[1])
                    self.sheet_count = int(parts[2])
                else:
                    items = (u'Title', u'Date', u'Rev', u'Comp', \
                             u'Comment1', u'Comment2', u'Comment3', u'Comment4')
                    for item in items:
                        if parts[0] == item:
                            setattr(self, item.lower(), parts[1])

        def save(self, sch_file):
            """
            Save title block description to Schematic file.

                Arguments:

                sch_file (file) - file for writing.

            """
            descr = u'$Descr {paper} {width} {height}{portrait}\n' \
                    u'encoding {encoding}\n' \
                    u'Sheet {number} {count}\n' \
                    u'Title "{title}"\n' \
                    u'Date "{date}"\n' \
                    u'Rev "{rev}"\n' \
                    u'Comp "{comp}"\n' \
                    u'Comment1 "{comment1}"\n' \
                    u'Comment2 "{comment2}"\n' \
                    u'Comment3 "{comment3}"\n' \
                    u'Comment4 "{comment4}"\n' \
                    u'$EndDescr\n'.format(
                    paper = self.sheet_format,
                    width = self.sheet_size_x,
                    height = self.sheet_size_y,
                    portrait = {True:u' portrait', False:u''}[self.portrait],
                    encoding = self.encoding,
                    number = self.sheet_number,
                    count = self.sheet_count,
                    title = self.title,
                    date = self.date,
                    rev = self.rev,
                    comp = self.comp,
                    comment1 = self.comment1,
                    comment2 = self.comment2,
                    comment3 = self.comment3,
                    comment4 = self.comment4
                    )
            sch_file.write(descr)


    class Comp:
        """
        Description of the component.

            Attributes:

            name (unicode) - name of the component;
            ref (unicode) - reference of the component;
            unit (int) - part of the component;
            path_and_ref (list of ["path", "ref", "part"]) - references of
                the components from complex hierarchy;
            convert (boot) - True - show as De Morgan convert, False - normal;
            timestamp (unicode) - timestamp of component;
            pos_x (int) - horizontal position of component;
            pos_y (int) - vertical position of component;
            fields (list of Field) - list of fields of the element;
            orient_matrix (tuple of 4 ints) - rotation matrix.

        """

        def __init__(self, str_comp):
            """
            Create description of component from strings.

                Arguments:

                str_comp (unicode) - text lines read from KiCad Schematic file.

            """
            lines = str_comp.splitlines()
            self.fields = []
            for line in lines:
                parts = split_line(line)
                if parts[0] == u'L':
                    self.name = parts[1]
                    self.ref = parts[2]
                elif parts[0] == u'U':
                    self.unit = int(parts[1])
                    self.convert = (int(parts[2]) == 2)
                    self.timestamp = parts[3]
                elif parts[0] == u'P':
                    self.pos_x = int(parts[1])
                    self.pos_y = int(parts[2])
                elif parts[0] == u'AR':
                    if not hasattr(self, u'path_and_ref'):
                        self.path_and_ref = []
                    item = []
                    for part in (1, 2, 3):
                        value = parts[part].split(u'"')[1]
                        item.append(value)
                    self.path_and_ref.append(item)
                elif parts[0] == u'F':
                    self.fields.append(self.Field(line))
                elif parts[0].startswith(u'\t'):
                    # Skip 1st line that starts with tab - redundant: not used
                    if line == u'\t{unit:<4} {pos_x:<4} {pos_y:<4}'.format(
                               unit = self.unit,
                               pos_x = self.pos_x,
                               pos_y = self.pos_y
                               ):
                        pass
                    else:
                        line = line.lstrip(u'\t')
                        line = split_line(line)
                        self.orient_matrix = (int(line[0]), int(line[1]), \
                                              int(line[2]), int(line[3]))

        def save(self, sch_file):
            """
            Save description of the component to Schematic file.

                Arguments:

                sch_file (file) - file for writing.

            """
            comp_str = u'$Comp\n' \
                       u'L {name} {ref}\n' \
                       u'U {unit} {convert} {timestamp}\n' \
                       u'P {pos_x} {pos_y}\n'.format(
                       name = self.name,
                       ref = self.ref,
                       unit = self.unit,
                       convert = {True:u'2', False:u'1'}[self.convert],
                       timestamp = self.timestamp,
                       pos_x = self.pos_x,
                       pos_y = self.pos_y
                       )
            sch_file.write(comp_str)
            if hasattr(self, u'path_and_ref'):
                for item in (self.path_and_ref):
                    path_and_ref_str = u'AR Path="{path}" Ref="{ref}"  Part="{part}" \n'.format(
                            path = item[0],
                            ref = item[1],
                            part = item[2]
                            )
                    sch_file.write(path_and_ref_str)
            for field in self.fields:
                field.save(sch_file)
            comp_str = u'\t{unit:<4} {pos_x:<4} {pos_y:<4}\n' \
                       u'\t{or_m[0]:<4} {or_m[1]:<4} {or_m[2]:<4} {or_m[3]:<4}\n' \
                       u'$EndComp\n'.format(
                       unit = self.unit,
                       pos_x = self.pos_x,
                       pos_y = self.pos_y,
                       or_m = self.orient_matrix
                       )
            sch_file.write(comp_str)


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
                text (unicode) - text of field;
                orientation (unicode) - 'H' - horizontal, 'V' - vertical;
                pos_x (int) - horizontal position of the field;
                pos_y (int) - vertical position of the field;
                size (int) - size of the text;
                flags (unicode) - string of flags;
                hjustify (unicode) - horizontal justify:
                        'L' - left;
                        'C' - center;
                        'R' - right;
                vjustify (unicode) - vertical justify:
                        'T' - top;
                        'C' - center;
                        'B' - bottom;
                italic (bool) - if True - text is italic;
                bold (bool) - if True - text is bold;
                name (unicode) - name of the field (only if it is not default
            name).

            """

            def __init__(self, str_field):
                """
                Create description of the field from string.

                    Arguments:

                    str_field (unicode) - text line from KiCad Schematic file.

                """
                items = split_line(str_field)
                self.number = int(items[1])
                if len(items) == 11:
                    self.name = items[10]
                temp = items[9]
                items = items[2:9]
                self.vjustify = temp[0]
                if temp[1] == u'N':
                    self.italic = False
                else:
                    self.italic = True
                if temp[2] == u'N':
                    self.bold = False
                else:
                    self.bold = True
                item_names = (u'text', u'orientation', u'pos_x', u'pos_y', \
                              u'size', u'flags', u'hjustify')
                for item in range(len(item_names)):
                    setattr(self, item_names[item], items[item])
                # make valid empty value field
                if self.number == 1 and self.text == u'~':
                    self.text = u''
                self.pos_x = int(self.pos_x)
                self.pos_y = int(self.pos_y)
                self.size = int(self.size)

            def save(self, sch_file):
                """
                Save description of the field to Schematic file.

                    Arguments:

                    sch_file (file) - file for writing.

                """
                # make valid empty value field
                if self.number == 1 and self.text == u'':
                    vtext = u'~'
                else:
                    vtext = self.text
                name = u''
                if hasattr(self, u'name'):
                    name = u' "{}"'.format(self.name)
                field_str = u'F {number} "{text}" {orient} {pos_x:<3} {pos_y:<3} {size:<3} {flags} {hjustify} {vjustify}{italic}{bold}{name}\n'.format(
                            number = self.number,
                            text = vtext,
                            orient = self.orientation,
                            pos_x = self.pos_x,
                            pos_y = self.pos_y,
                            size = self.size,
                            flags = self.flags,
                            hjustify = self.hjustify,
                            vjustify = self.vjustify,
                            italic = {True:u'I', False:u'N'}[self.italic],
                            bold = {True:u'B', False:u'N'}[self.bold],
                            name = name
                            )
                sch_file.write(field_str)


    class Sheet:
        """
        Description of the hierarchical sheet.

            Attributes:

            name (unicode) - name of the hierarchical sheet;
            name_size (int) - size of the text 'name';
            file_name (unicode) - name of the hierarchical sheet file;
            file_name_size (int) - size of the text 'file_name';
            pos_x (int) - horizontal position of the hierarchical sheet;
            pos_y (int) - vertical position of the hierarchical sheet;
            dim_x (int) - horizontal dimension of the hierarchical sheet;
            dim_y (int) - vertical dimension of the hierarchical sheet;
            timestamp (unicode) - time stamp;
            fields (list of Field) - list of fields of the hierarchical sheet.

        """

        def __init__(self, str_sheet):
            """
            Create description of hierarchical sheet from strings.

                Arguments:

                str_sheet (unicode) - text lines read from KiCad Schematic file.

            """
            lines = str_sheet.splitlines()
            self.fields = []
            for line in lines:
                parts = split_line(line)
                if parts[0] == u'S':
                    self.pos_x = parts[1]
                    self.pos_y = parts[2]
                    self.dim_x = parts[3]
                    self.dim_y = parts[4]
                elif parts[0] == u'U':
                    self.timestamp = parts[1]
                elif parts[0].startswith(u'F'):
                    if int(parts[0][1:]) == 0:
                        self.name = parts[1]
                        self.name_size = parts[2]
                    elif int(parts[0][1:]) == 1:
                        self.file_name = parts[1]
                        self.file_name_size = parts[2]
                    elif int(parts[0][1:]) > 1:
                        self.fields.append(self.Field(line))

        def save(self, sch_file):
            """
            Save description of the hierarchical sheet to Schematic file.

                Arguments:

                sch_file (file) - file for writing.

            """
            sheet_str = u'$Sheet\n' \
                        u'S {pos_x:<4} {pos_y:<4} {dim_x:<4} {dim_y:<4}\n' \
                        u'U {timestamp}\n' \
                        u'F0 "{name}" {name_size}\n' \
                        u'F1 "{file_name}" {file_name_size}\n'.format(
                        pos_x = self.pos_x,
                        pos_y = self.pos_y,
                        dim_x = self.dim_x,
                        dim_y = self.dim_y,
                        timestamp = self.timestamp,
                        name = self.name,
                        name_size = self.name_size,
                        file_name = self.file_name,
                        file_name_size = self.file_name_size
                        )
            sch_file.write(sheet_str)
            for field in self.fields:
                field.save(sch_file)
            sheet_str = u'$EndSheet\n'
            sch_file.write(sheet_str)


        class Field:
            """
            Description of field of the hierarchical sheet.

                Attributes:

                number (int) - number of the field (starts from 2);
                text (unicode) - text of field;
                form (unicode) - field format:
                    'I' - input;
                    'O' - output;
                    'B' - bidirectional;
                    'T' - tri state;
                    'U' - unspecified;
                side (unicode) - side of the field:
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

                    str_field (unicode) - text line from KiCad Schematic file.

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
                field_str = u'F{number} "{text}" {form} {side} {pos_x:<3} {pos_y:<3} {dim:<3}\n'.format(
                            number = self.number,
                            text = self.text,
                            form = self.form,
                            side = self.side,
                            pos_x = self.pos_x,
                            pos_y = self.pos_y,
                            dim = self.dimension
                            )
                sch_file.write(field_str)


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

                str_bitmap (unicode) - text lines read from KiCad Schematic file.

            """
            lines = str_bitmap.splitlines()
            self.data = []
            data_block = False
            for line in lines:
                if data_block:
                    if line.startswith(u'EndData'):
                        break
                    line = line.rstrip(u' ')
                    bytes = split_line(line)
                    for byte in bytes:

                        if byte == u'$EndBitmap':
                            continue  # EESchema bug fix

                        self.data.append(int(byte, 16))
                elif line.startswith(u'Pos'):
                    parts = split_line(line)
                    self.pos_x = parts[1]
                    self.pos_y = parts[2]
                elif line.startswith(u'Scale'):
                    parts = split_line(line)
                    self.scale = float(parts[1].replace(u',', u'.'))
                elif line.startswith(u'Data'):
                    data_block = True

        def save(self, sch_file):
            """
            Save description of the bitmap to Schematic file.

                Arguments:

                sch_file (file) - file for writing.

            """
            data_str = u''
            i = 0
            for byte in self.data:
                i += 1
                data_str += u'{:02X} '.format(byte)
                if i == 32:
                    i = 0
                    data_str += u'\n'
            bitmap_str = u'$Bitmap\n' \
                         u'Pos {pos_x:<4} {pos_y:<4}\n' \
                         u'Scale {scale}\n' \
                         u'Data\n' \
                         u'{data}\n' \
                         u'EndData\n' \
                         u'$EndBitmap\n'.format(
                         pos_x = self.pos_x,
                         pos_y = self.pos_y,
                         scale = u'{:.6f}'.format(self.scale),
                         data = data_str
                         )
            sch_file.write(bitmap_str)


    class Connection:
        """
        Description of the connection (junction) or no connection position.

            Attributes:

            tpye (unicode) - type of the connection (Connection, NoConn);
            pos_x (int) - horizontal position of the connection;
            pos_y (int) - vertical position of the connection.

        """

        def __init__(self, str_connection):
            """
            Create description of the connection from string.

                Arguments:

                str_connect (unicode) - text line read from KiCad Schematic.

            """
            str_connection.replace(u'\n', u'')
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
            connection_str = u'{type} ~ {pos_x:<4} {pos_y:<4}\n'.format(
                             type = self.type,
                             pos_x = self.pos_x,
                             pos_y = self.pos_y
                             )
            sch_file.write(connection_str)


    class Text:
        """
        Description of the text label.

            Attributes:

            type (unicode) - type of the text label (Notes, Label, GLable, HLabel);
            text (unicode) - text of the label;
            pos_x (int) - horizontal position of the text label;
            pos_y (int) - vertical position of the text label;
            orientation (int) - orientation of the text label;
            dimension (int) - dimension of the text label;
            shape (unicode) - shape type of the text label (only for GLabel and
        HLabel);
            italic (bool) - True - if text is italic;
            bold (int) - coefficient of the bold text.

        """

        def __init__(self, str_text):
            """
            Create description of the text label from string.

                Arguments:

                str_connect (unicode) - text line read from KiCad Schematic.

            """
            lines = str_text.splitlines()
            parts = split_line(lines[0])
            self.type = parts[1]
            self.pos_x = int(parts[2])
            self.pos_y = int(parts[3])
            self.orientation = int(parts[4])
            self.dimension = int(parts[5])
            if parts[1] in (u'GLabel', u'HLabel'):
                self.shape = parts[6]
            self.italic = parts[-2] == u'Italic'
            self.bold = int(parts[-1])
            self.text = lines[1]

        def save(self, sch_file):
            """
            Save description of the text label to Schematic file.

                Arguments:

                sch_file (file) - file for writing;

            """
            shape = u''
            if self.type in (u'GLabel', u'HLabel'):
                shape = u'{} '.format(self.shape)
            text_str = u'Text {type} {pos_x:<4} {pos_y:<4} {orient:<4} {dim:<4} {shape}{italic} {bold}\n{text}\n'.format(
                       type = self.type,
                       pos_x = self.pos_x,
                       pos_y = self.pos_y,
                       orient = self.orientation,
                       dim = self.dimension,
                       shape = shape,
                       italic = {True:u'Italic', False:u'~'}[self.italic],
                       bold = self.bold,
                       text = self.text
                       )
            sch_file.write(text_str)


    class Wire:
        """
        Description of the wire.

            Attributes:

            type (unicode) - type of the wire (Note, Wire, Bus);
            start_x (int) - horizontal coordinates of the start position;
            start_y (int) - vertical coordinates of the start position;
            end_x (int) - horizontal coordinates of the end position;
            end_y (int) - vertical coordinates of the end position.

        """

        def __init__(self, str_wire):
            """
            Create description of the wire from string.

                Arguments:

                str_connect (unicode) - text line read from KiCad Schematic.

            """
            lines = str_wire.splitlines()
            parts = split_line(lines[0])
            self.type = parts[1]
            parts = split_line(lines[1])
            self.start_x = int(parts[0].lstrip(u'\t'))
            self.start_y = int(parts[1])
            self.end_x = int(parts[2])
            self.end_y = int(parts[3])

        def save(self, sch_file):
            """
            Save description of the wire to Schematic file.

                Arguments:

                sch_file (file) - file for writing;

            """
            wire_str = u'Wire {type} Line\n' \
                       u'\t{start_x:<4} {start_y:<4} {end_x:<4} {end_y:<4}\n'.format(
                       type = self.type,
                       start_x = self.start_x,
                       start_y = self.start_y,
                       end_x = self.end_x,
                       end_y = self.end_y
                       )
            sch_file.write(wire_str)



    class Entry:
        """
        Description of the entry.

            Attributes:

            type (unicode) - type of the wire (Wire Line, Bus Bus);
            start_x (int) - horizontal coordinates of the start position;
            start_y (int) - vertical coordinates of the start position;
            end_x (int) - horizontal coordinates of the end position;
            end_y (int) - vertical coordinates of the end position.

        """

        def __init__(self, str_entry):
            """
            Create description of the entry from string.

                Arguments:

                str_connect (unicode) - text line read from KiCad Schematic.

            """
            lines = str_entry.splitlines()
            parts = split_line(lines[0])
            self.type = u'{parts[1]} {parts[2]}'.format(parts = parts)
            parts = split_line(lines[1])
            self.start_x = int(parts[0].lstrip(u'\t'))
            self.start_y = int(parts[1])
            self.end_x = int(parts[2])
            self.end_y = int(parts[3])

        def save(self, sch_file):
            """
            Save description of the entry to Schematic file.

                Arguments:

                sch_file (file) - file for writing;

            """
            entry_str = u'Entry {type}\n' \
                       u'\t{start_x:<4} {start_y:<4} {end_x:<4} {end_y:<4}\n'.format(
                       type = self.type,
                       start_x = self.start_x,
                       start_y = self.start_y,
                       end_x = self.end_x,
                       end_y = self.end_y
                       )
            sch_file.write(entry_str)


class Library:
    """
    Implementation of KiCad Schematic library.

    """
    LIBFILE_IDENT = u'EESchema-LIBRARY Version'

    def __init__(self, lib_name):
        """
        Load all contents from KiCad's Schematic library.

            Attributes:

            lib_name (unicode) - full name of KiCad Schematic library file;
            version (float) - version of file format;
            encoding (srt) - encoding of text;
            components (list of Component) - list of components of library.

        """
        self.lib_name = lib_name
        self.load()

    def load(self):
        """
        Open KiCad Schematic library file and read all information from it.

        """
        self.components = []

        lib_file = codecs.open(self.lib_name, 'r', 'utf-8')
        first_line = lib_file.readline()
        first_line = first_line.replace(u'\n', u'')
        if first_line.startswith(self.LIBFILE_IDENT):
            self.version = float(split_line(first_line)[2])
        else:
            return
        for lib_line in lib_file:
            lib_line = lib_line
            if lib_line.startswith(u'DEF'):
                component_value = u''
                while not lib_line.startswith(u'ENDDEF'):
                    component_value += lib_line
                    lib_line = lib_file.readline()
                self.components.append(self.Component(component_value))
            elif lib_line.startswith(u'#encoding'):
                self.encoding = split_line(lib_line)[-1].replace(u'\n', u'')
            elif lib_line.startswith(u'#End Library'):
                    return

    def save(self, new_name=None):
        """
        Save all content to KiCad Schematic library file.

        """
        lib_file_name = self.lib_name
        if new_name:
            lib_file_name = new_name
        lib_file = codecs.open(lib_file_name, 'w', 'utf-8')

        header = u'{id} {version:.1f}\n' \
                 u'#encoding {encoding}\n'.format(
                 id = self.LIBFILE_IDENT,
                 version = self.version,
                 encoding = self.encoding
                 )
        lib_file.write(header)
        for components in self.components:
            components.save(lib_file)
        lib_file.write(u'#\n#End Library\n')
        lib_file.close()


    class Component:
        """
        Description of the component of a library.

            Attributes:

            name (unicode) - component name in library;
            reference (unicode) - reference of component;
            text_offset (int) - offset for pin name position;
            draw_pinnumber (bool) - True - display number, False - do not display number;
            draw_pinname (bool) - True - display name, False do not display name;
            unit_count (int) - number of part (or section) in component;
            units_locked (bool) - True - units are not identical and cannot be swapped,
        False - units are identical and therefore can be swapped;
            option_flag (unicode) - 'N' - normal, 'P' - component type "power";
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

                str_component (unicode) - text lines read from KiCad Schematic library file.

            """
            lines = str_component.splitlines()
            self.aliases = []
            self.fields = []
            self.graphic_elements = []
            footprint = False
            for line in lines:
                parts = split_line(line)
                if footprint:
                    if parts[0] == u'$ENDFPLIST':
                        footprint = False
                        continue
                    else:
                        self.fplist.append(parts[0])
                        continue
                if parts[0] == u'DEF':
                    self.name = parts[1]
                    self.reference = parts[2]
                    self.text_offset = int(parts[4])
                    if parts[5] == u'Y':
                        self.draw_pinnumber = True
                    elif parts[5] == u'N':
                        self.draw_pinnumber = False
                    if parts[6] == u'Y':
                        self.draw_pinname = True
                    elif parts[6] == u'N':
                        self.draw_pinname = False
                    self.unit_count = int(parts[7])
                    if parts[8] == u'L':
                        self.units_locked = True
                    elif parts[8] == u'F':
                        self.units_locked = False
                    self.option_flag = parts[9]
                elif parts[0] == u'ALIAS':
                    self.aliases = parts[1:]
                elif parts[0].startswith(u'F'):
                    self.fields.append(self.Field(line))
                elif parts[0] == u'P':
                    self.graphic_elements.append(self.Polygon(line))
                elif parts[0] == u'S':
                    self.graphic_elements.append(self.Rectangle(line))
                elif parts[0] == u'C':
                    self.graphic_elements.append(self.Circle(line))
                elif parts[0] == u'A':
                    self.graphic_elements.append(self.Arc(line))
                elif parts[0] == u'T':
                    self.graphic_elements.append(self.Text(line))
                elif parts[0] == u'X':
                    self.graphic_elements.append(self.Pin(line))
                elif parts[0] == u'$FPLIST':
                    footprint = True
                    self.fplist = []

        def save(self, lib_file):
            """
            Save description of the component to Schematic library file.

                Arguments:

                lib_file (file) - file for writing.

            """
            nick = self.name
            if nick.startswith(u'~'):
                nick = nick.replace(u'~', u'', 1)
            component_str = u'#\n' \
                            u'# {nick}\n' \
                            u'#\n' \
                            u'DEF {name} {ref} 0 {offset} {pin_num} {pin_name} {unit_count} {units_locked} {options}\n'.format(
                            nick = nick,
                            name = self.name,
                            ref = self.reference,
                            offset = str(self.text_offset),
                            pin_num = {True:u'Y', False:u'N'}[self.draw_pinnumber],
                            pin_name = {True:u'Y', False:u'N'}[self.draw_pinname],
                            unit_count = str(self.unit_count),
                            units_locked = {True:u'L', False:u'F'}[self.units_locked],
                            options = self.option_flag
                            )
            lib_file.write(component_str)
            for field in self.fields:
                field.save(lib_file)
            component_str = u''
            if self.aliases:
                component_str += u'ALIAS {}\n'.format(u' '.join(self.aliases))
            if hasattr(self, u'fplist'):
                component_str += u'$FPLIST\n'
                for fp in self.fplist:
                    component_str += u' {}\n'.format(fp)
                component_str += u'$ENDFPLIST\n'
            component_str += u'DRAW\n'
            lib_file.write(component_str)
            for graphic_element in self.graphic_elements:
                graphic_element.save(lib_file)
            component_str = u'ENDDRAW\n' \
                            u'ENDDEF\n'
            lib_file.write(component_str)


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
                text (unicode) - text of field;
                pos_x (int) - horizontal position of the field;
                pos_y (int) - vertical position of the field;
                diamension (int) - diamension of the text;
                orientation (unicode) - 'H' - horizontal, 'V' - vertical;
                visibility (bool) - True - text is visible, False - text is invisible;
                hjustify (unicode) - horizontal justify:
                        'L' - left;
                        'C' - center;
                        'R' - right;
                vjustify (unicode) - vertical justify:
                        'T' - top;
                        'C' - center;
                        'B' - bottom;
                italic (bool) - if True - text is italic;
                bold (bool) - if True - text is bold;
                name (unicode) - name of the field (only if it is not default
            name).

            """

            def __init__(self, str_field):
                """
                Create description of the field from string.

                    Arguments:

                    str_field (unicode) - text line from KiCad Schematic library file.

                """
                items = split_line(str_field)
                self.number = int(items[0][1:])
                if len(items) == 10:
                    self.name = items[9]
                item_names = (u'text', u'pos_x', u'pos_y', u'diamension', \
                              u'orientation', u'visibility', u'hjustify')
                for item in range(len(item_names)):
                    setattr(self, item_names[item], items[item + 1])
                self.pos_x = int(self.pos_x)
                self.pos_y = int(self.pos_y)
                self.diamension = int(self.diamension)
                if self.visibility == u'V':
                    self.visibility = True
                elif self.visibility == u'I':
                    self.visibility = False
                self.vjustify = items[8][0]
                if items[8][1] == u'N':
                    self.italic = False
                else:
                    self.italic = True
                if items[8][2] == u'N':
                    self.bold = False
                else:
                    self.bold = True

            def save(self, lib_file):
                """
                Save description of the field to Schematic file.

                    Arguments:

                    lib_file (file) - file for writing.

                """
                name = u''
                if hasattr(self, u'name'):
                    name = u' "{}"'.format(self.name)
                field_str = u'F{number} "{text}" {pos_x} {pos_y} {size} {orient} {visibility} {hjustify} {vjustify}{italic}{bold}{name}\n'.format(
                            number = self.number,
                            text = self.text,
                            pos_x = self.pos_x,
                            pos_y = self.pos_y,
                            size = self.diamension,
                            orient = self.orientation,
                            visibility = {True:u'V', False:u'I'}[self.visibility],
                            hjustify = self.hjustify,
                            vjustify = self.vjustify,
                            italic = {True:u'I', False:u'N'}[self.italic],
                            bold = {True:u'B', False:u'N'}[self.bold],
                            name = name
                            )
                lib_file.write(field_str)


        class Polygon:
            """
            Description of the polygon.

                Attributes:

                unit (int) - 0 if common to the parts; if not, number of part (1. .n);
                convert (int) - 0 if common to the 2 representations, if not 1 or 2;
                thickness (int) - line thickness;
                points (list of [x(int), y(int)]) - list of x and y coordinates of points;
                fill (unicode) - F - fill foreground, f - fill background, N - do not fill.

            """

            def __init__(self, str_polygon):
                """
                Create description of the polygon.

                    Arguments:

                    str_polygon (unicode) - text line from KiCad Schematic library file.

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
                polygon_str = u'P {p_count} {unit} {convert} {thickness}'.format(
                              p_count = len(self.points),
                              unit = self.unit,
                              convert = self.convert,
                              thickness = self.thickness
                              )
                for point in self.points:
                    polygon_str += u'  {p[0]} {p[1]}'.format(p = point)
                polygon_str += u' {}\n'.format(self.fill)
                lib_file.write(polygon_str)


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
                fill (unicode) - F - fill foreground, f - fill background, N - do not fill.

            """

            def __init__(self, str_rectangle):
                """
                Create description of the rectangle.

                    Arguments:

                    str_rectangle (unicode) - text line from KiCad Schematic library file.

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
                rectangle_str = u'S {start_x} {start_y} {end_x} {end_y} {unit} {convert} {thickness} {fill}\n'.format(
                                start_x = self.start_x,
                                start_y = self.start_y,
                                end_x = self.end_x,
                                end_y = self.end_y,
                                unit = self.unit,
                                convert = self.convert,
                                thickness = self.thickness,
                                fill = self.fill
                                )
                lib_file.write(rectangle_str)


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
                fill (unicode) - F - fill foreground, f - fill background, N - do not fill.

            """

            def __init__(self, str_circle):
                """
                Create description of the circle.

                    Arguments:

                    str_circle (unicode) - text line from KiCad Schematic library file.

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
                circle_str = u'C {pos_x} {pos_y} {radius} {unit} {convert} {thickness} {fill}\n'.format(
                             pos_x = self.pos_x,
                             pos_y = self.pos_y,
                             radius = self.radius,
                             unit = self.unit,
                             convert = self.convert,
                             thickness = self.thickness,
                             fill = self.fill
                             )
                lib_file.write(circle_str)


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
                fill (unicode) - F - fill foreground, f - fill background, N - do not fill;
                start_x (int) - x coordinate of the starting point (role similar to start);
                start_y (int) - y coordinate of the starting point (role similar to start);
                end_x (int) - x coordinate of the ending point (role similar to end);
                end_y (int) - y coordinate of the ending point (role similar to end).

            """

            def __init__(self, str_arc):
                """
                Create description of the arc.

                    Arguments:

                    str_arc (unicode) - text line from KiCad Schematic library file.

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
                arc_str = u'A {pos_x} {pos_y} {radius} {start} {end} {unit} {convert} {thickness} {fill} {start_x} {start_y} {end_x} {end_y}\n'.format(
                          pos_x = self.pos_x,
                          pos_y = self.pos_y,
                          radius = self.radius,
                          start = self.start,
                          end = self.end,
                          unit = self.unit,
                          convert = self.convert,
                          thickness = self.thickness,
                          fill = self.fill,
                          start_x = self.start_x,
                          start_y = self.start_y,
                          end_x = self.end_x,
                          end_y = self.end_y
                          )
                lib_file.write(arc_str)


        class Text:
            """
            Description of the text.

                Attributes:

                angle (int) - angle of the text (in 0,1 degrees);
                pos_x (int) - x coordinate of text position;
                pos_y (int) - y coordinate of text position;
                size (int) - size of text;
                attr (int) - attributs of the text (visibility etc);
                unit (int) - 0 if common to the parts; if not, number of part (1. .n);
                convert (int) - 0 if common to the 2 representations, if not 1 or 2;
                text (unicode) - text;
                italic (bool) - True - text is italic, False - text is normal;
                bold (bool) - True - text is bold, False - text is normal;
                hjustify (unicode) - horizontal justify:
                        'L' - left;
                        'C' - center;
                        'R' - right;
                vjustify (unicode) - vertical justify:
                        'B' - bottom;
                        'C' - center;
                        'T' - top.

            """

            def __init__(self, str_text):
                """
                Create description of the text.

                    Arguments:

                    str_text (unicode) - text line from KiCad Schematic library file.

                """
                items = split_line(str_text)
                self.angle = int(items[1])
                self.pos_x = int(items[2])
                self.pos_y = int(items[3])
                self.size = int(items[4])
                self.attr = int(items[5])
                self.unit = int(items[6])
                self.convert = int(items[7])
                self.text = items[8]
                if items[9] == u'Italic':
                    self.italic = True
                elif items[9] == u'Normal':
                    self.italic = False
                if items[10] == u'1':
                    self.bold = True
                elif items[10] == u'0':
                    self.bold = False
                self.hjustify = items[11]
                self.vjustify = items[12]

            def save(self, lib_file):
                """
                Save description of the text to Schematic library file.

                    Arguments:

                    lib_file (file) - file for writing.

                """
                text = self.text
                if u'~' in text or u"''" in text:
                    text = u'"{}"'.format(text)
                text_str = u'T {angle} {pos_x} {pos_y} {size} {attr} {unit} {convert} {text}  {italic} {bold} {hjustify} {vjustify}\n'.format(
                           angle = self.angle,
                           pos_x = self.pos_x,
                           pos_y = self.pos_y,
                           size = self.size,
                           attr = self.attr,
                           unit = self.unit,
                           convert = self.convert,
                           text = text,
                           italic = {True:u'Italic', False:u'Normal'}[self.italic],
                           bold = {True:1, False:0}[self.bold],
                           hjustify = self.hjustify,
                           vjustify = self.vjustify
                           )
                lib_file.write(text_str)


        class Pin:
            """
            Description of the pin.

                Attributes:

                name (unicode) - name of the pin ("~" - if empty);
                number (unicode) - number of the pin ("~" - if empty);
                pos_x (int) - x coordinate of pin position;
                pos_y (int) - y coordinate of pin position;
                length (int) - length of the pin;
                orientation (unicode) - orientation of the pin:
                    'U' - up;
                    'D' - down;
                    'L' - left;
                    'R' - right;
                number_size (int) - size of number text label;
                name_size (int) - size of name text label;
                unit (int) - 0 if common to the parts; if not, number of part (1. .n);
                convert (int) - 0 if common to the 2 representations, if not 1 or 2;
                electric_type (unicode) - electric type:
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
                shape (unicode) - if present:
                    'N' - invisible;
                    'I' - inverted;
                    'C' - clock;
                    'L' - input low;
                    'V' - output low;
                    'F' - falling adge low;
                    'X' - non logic;

            """

            def __init__(self, str_pin):
                """
                Create description of the pin.

                    Arguments:

                    str_pin (unicode) - text line from KiCad Schematic library file.

                """
                items = split_line(str_pin)
                self.name = items[1]
                self.number = items[2]
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
                shape = u''
                if hasattr(self, u'shape'):
                    shape = u' {}'.format(self.shape)
                pin_str = u'X {name} {num} {pos_x} {pos_y} {length} {orient} {num_size} {name_size} {unit} {convert} {el_type}{shape}\n'.format(
                          name = self.name,
                          num = self.number,
                          pos_x = self.pos_x,
                          pos_y = self.pos_y,
                          length = self.length,
                          orient = self.orientation,
                          num_size = self.number_size,
                          name_size = self.name_size,
                          unit = self.unit,
                          convert = self.convert,
                          el_type = self.electric_type,
                          shape = shape
                          )
                lib_file.write(pin_str)


def split_line(str_to_split):
    """
    Split string by whitespace considering text in quotes.

        Arguments:

        str_to_split (unicode) - string that must be splint.

        Returns:

        output (list of str) - list of strings.

    """
    items = str_to_split.split(u' ')
    output = []
    quoted = False
    for item in items:
        if not quoted and item.startswith(u'"'):
            if item.endswith(u'"') and not item.endswith(u'\\"') and \
               len(item) > 1:
                quoted = False
                output.append(item[1:-1])
            else:
                quoted = True
                output.append(item[1:])
            continue
        elif quoted:
            if item.endswith(u'"') and not item.endswith(u'\\"'):
                quoted = False
                output[-1] += u' ' + item[:-1]
                continue
            else:
                output[-1] += u' ' + item
        else:
            if item:
                output.append(item)
    return output

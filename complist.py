#!/usr/bin/env python2
# -*-    Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4    -*-
### BEGIN LICENSE
# Copyright (C) 2016 Baranovskiy Konstantin (baranovskiykonstantin@gmail.com)
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

import os
import re
import time
from copy import deepcopy
from operator import itemgetter

import odf.opendocument
from odf.text import P
from odf.table import *
from odf.style import Style, ParagraphProperties, TextProperties
from odf import dc, meta

from kicadsch import *


class CompList():
    """
    Generating list of the components from KiCAD Schematic
    and save it to *.ods file.

    """

    def __init__(self):
        # Load the pattern
        self.pattern = odf.opendocument.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), u'pattern.ods'))
        self.firstPagePattern = None
        self.otherPagesPattern = None
        self.lastPagePattern = None
        for sheet in self.pattern.spreadsheet.getElementsByType(Table):
            # Pattern for first page
            if sheet.getAttribute(u'name') == u'First':
                self.firstPagePattern = sheet
            # Pattern for other pages
            elif sheet.getAttribute(u'name') == u'Other':
                self.otherPagesPattern = sheet
            # Pattern for last pages (the changes sheet)
            elif sheet.getAttribute(u'name') == u'Last':
                self.lastPagePattern = sheet

        # Create list of the components file object
        self.complist = odf.opendocument.OpenDocumentSpreadsheet()

        # Copy all parameters from pattern to list of the components
        for font in self.pattern.fontfacedecls.childNodes[:]:
            self.complist.fontfacedecls.addElement(font)

        for style in self.pattern.styles.childNodes[:]:
            self.complist.styles.addElement(style)

        for masterstyle in self.pattern.masterstyles.childNodes[:]:
            self.complist.masterstyles.addElement(masterstyle)

        for autostyle in self.pattern.automaticstyles.childNodes[:]:
            self.complist.automaticstyles.addElement(autostyle)

        for setting in self.pattern.settings.childNodes[:]:
            self.complist.settings.addElement(setting)

        # Current state of filling list of the components
        self.cur_group = u''
        self.cur_line = 1
        self.cur_page = 1
        self.cur_table = self.firstPagePattern

        # Some variables for filling the list
        self.developer = u''
        self.verifer = u''
        self.approver = u''
        self.decimal_num = u''
        self.title = u''
        self.comp = u''
        self.add_units = False
        self.need_changes_sheet = True

    def replace_text(self, table, label, text, group=False):
        """
        Replace 'label' (like #1:1) to 'text' in 'table'.
        If 'group' is set to 'True' will be used special formatting.

        """
        rows = table.getElementsByType(TableRow)
        for row in rows:
            cells = row.getElementsByType(TableCell)
            for cell in cells:
                for p in cell.getElementsByType(P):
                    for p_data in p.childNodes:
                        if p_data.tagName == u'Text':
                            if p_data.data == label:
                                # Decoding internal escapes
                                text = text.decode('string_escape')
                                # Decoding escapes from KiCAD
                                p_data.data = text.decode('string_escape')
                                if group == True:
                                    # Set center align and underline for ghoup name
                                    curStyleName = cell.getAttribute(u'stylename')
                                    try:
                                        groupStyle = self.complist.getStyleByName(curStyleName + u'g')
                                        # Needed for backwards compatibility
                                        if groupStyle == None:
                                            raise
                                    except:
                                        groupStyle = deepcopy(self.complist.getStyleByName(curStyleName))
                                        groupStyle.setAttribute(u'name', curStyleName + u'g')
                                        groupStyle.addElement(ParagraphProperties(textalignlast=u'center'))
                                        groupStyle.addElement(TextProperties(textunderlinetype=u'single',
                                                                             textunderlinestyle=u'solid',))
                                        self.complist.styles.addElement(groupStyle)
                                    cell.setAttribute(u'stylename', curStyleName + u'g')
                                return

    def clear_table(self, table):
        """
        Clear 'table' of labels.

        """
        rows = table.getElementsByType(TableRow)
        for row in rows:
            cells = row.getElementsByType(TableCell)
            for cell in cells:
                for p in cell.getElementsByType(P):
                    for p_data in p.childNodes:
                        if p_data.tagName == u'Text':
                            if re.search(r'#\d+:\d+', p_data.data) != None:
                                p_data.data = u''

    def append_changes_sheet(self):
        """
        Add to the end of list the changes sheet from template.

        """
        self.cur_table = self.lastPagePattern
        self.cur_page += 1
        self.cur_table.setAttribute(u'name', u'стр. %d' % self.cur_page)
        self.complist.spreadsheet.addElement(self.cur_table)

    def next_line(self):
        """
        Moving to next line.
        If table is full, save it in list object and create a new one.

        """
        # Increment line counter
        self.cur_line += 1

        # First page of the list has 29 lines, other pages has 32 lines
        if (self.cur_page == 1 and self.cur_line > 29) or \
           (self.cur_page > 1 and self.cur_line > 32):
            # Table is full
            self.cur_table.setAttribute(u'name', u'стр. %d' % self.cur_page)
            self.complist.spreadsheet.addElement(self.cur_table)

            self.cur_table = deepcopy(self.otherPagesPattern)
            self.cur_page += 1
            self.cur_line = 1

    def set_line(self, element):
        """
        Fill the line in list of the components using element's fields.

        """
        # Reference
        ref = u''
        if int(element[8]) > 1:
            # Reference number: '5, 6'; '25-28' etc.
            ref = re.search(r'(\d+)(-|,\s?)(\d+)', element[1]).groups()
            # Reference: 'VD1, 2'; 'C8-C11' etc.
            ref = (element[0] + u'%s%s' + element[0] + u'%s') % ref
        else:
            # Reference: 'R5'; 'VT13' etc.
            ref = element[0] + element[1]
        self.replace_text(self.cur_table, u'#1:%d' % self.cur_line, ref)
        # Value
        val = element[2] + element[3]
        if self.add_units:
            if element[0] == u'C' and element[3][-1:] != u'Ф':
                if element[3].isdigit():
                    val += u'п'
                val += u'Ф'
            elif element[0] == u'L' and element[3][-2:] != u'Гн':
                val += u'Гн'
            elif element[0] == u'R' and element[3][-2:] != u'Ом':
                val += u'Ом'
        val += element[4] + element[5] + element[6]
        self.replace_text(self.cur_table, u'#2:%d' % self.cur_line, val)
        # Count
        self.replace_text(self.cur_table, u'#3:%d' % self.cur_line, element[8])
        # Coment
        self.replace_text(self.cur_table, u'#4:%d' % self.cur_line, element[7])

    def compare_ref(self, ref):
        """
        Get integer value of reference (type & number) fo comparison in sort() function.

        """
        ref_val = 0
        matches = re.search(r'^([A-Z]+)\d+', ref[0] + ref[1])
        if matches != None:
            for ch in range(len(matches.group(1))):
                # Ref begins maximum of two letters, the first is multiplied by 10^5, the second by 10^4
                ref_val += ord(matches.group(1)[ch]) * 10 ** 5 / (10 ** ch)
        matches = re.search(r'^[A-Z]+(\d+)', ref[0] + ref[1])
        if matches != None:
            ref_val += int(matches.group(1))
        return ref_val

    def get_descr(self, sch_file_name):
        """
        Open KiCAD Schematic file and get title block description.

        """
        sch = Schematic(sch_file_name)
        self.developer = sch.descr.comment2
        self.verifer = sch.descr.comment3
        self.approver = sch.descr.comment4
        self.decimal_num = self.convert_decimal_num(sch.descr.comment1)
        self.title = self.convert_title(sch.descr.title)
        self.comp = sch.descr.comp

    def get_sheets(self, sch_file_name):
        """
        Return list of all hierarchical sheets used in schematic.

        """
        sheets = []
        exec_path = os.path.dirname(os.path.realpath(__file__))
        cur_path = os.path.dirname(sch_file_name)
        os.chdir(cur_path)
        sch = Schematic(sch_file_name)
        for item in sch.items:
            if item.__class__.__name__ == u'Sheet':
                sheets.append(os.path.abspath(os.path.join(cur_path, item.file_name.decode('utf-8'))))
                sheets.extend(self.get_sheets(os.path.abspath(os.path.join(cur_path, item.file_name.decode('utf-8')))))
        os.chdir(exec_path)
        return sheets

    def get_components(self, sch_file_name, root_only=False):
        """
        Open KiCAD Schematic file and get all components from it.

        """
        components = []
        exec_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(os.path.dirname(sch_file_name))
        sch = Schematic(sch_file_name)
        for item in sch.items:
            if item.__class__.__name__ == u'Comp':
                if not item.ref.startswith(u'#'):
                    components.append(item)
            elif item.__class__.__name__ == u'Sheet' and not root_only:
                components.extend(self.get_components(os.path.abspath(item.file_name)))
        os.chdir(exec_path)
        return components

    def load(self, sch_file_name, comp_fields=None):
        """
        Load all components from KiCAD Schematic file
        or get fields of the components directly
        and then fills the list.

        """

        def get_text_from_field(comp, field_name):
            """
            If field has 'name' then get text from it.

            """
            for field in comp.fields:
                if hasattr(field, u'name'):
                    if field.name == field_name:
                        return field.text
            return u''

        comp_array = []
        if comp_fields:
            comp_array = comp_fields
        else:
            components = self.get_components(sch_file_name)
            # Handle all lines
            for comp in components:
                temp = []
                temp.append(get_text_from_field(comp, u'Группа'))
                ref_type = re.search(r'[A-Z]+', comp.fields[0].text).group()
                ref_num = re.search(r'[0-9]+', comp.fields[0].text).group()
                temp.extend([ref_type, ref_num])
                temp.append(get_text_from_field(comp, u'Марка'))
                temp.append(comp.fields[1].text)
                temp.append(get_text_from_field(comp, u'Класс точности'))
                temp.append(get_text_from_field(comp, u'Тип'))
                temp.append(get_text_from_field(comp, u'Стандарт'))
                temp.append(get_text_from_field(comp, u'Примечание'))
                temp.append(u'1')
                comp_array.append(temp)
        comp_array = sorted(comp_array, key=itemgetter(0))
        self.get_descr(sch_file_name)

        # Split elements into groups
        # output - [['group',[[ref_type, ref_number, mark, value, accuracy, type, GOST, comment, count], ... ]], ... ]
        temp_name = comp_array[0][0]
        temp_array = None
        comp_lines = None
        for array in comp_array:
            if temp_name == array[0]:
                if temp_array == None:
                    temp_array = [array[1:],]
                else:
                    temp_array.append(array[1:])
            else:
                if comp_lines == None:
                    comp_lines = [[temp_name, temp_array],]
                else:
                    comp_lines.append([temp_name, temp_array])
                temp_array = [array[1:],]
                temp_name = array[0]
            if comp_array.index(array) == len(comp_array) - 1:
                if comp_lines == None:
                    comp_lines = [[temp_name, temp_array],]
                else:
                    comp_lines.append([temp_name, temp_array])

        # Sort grops by reference of first element
        comp_lines = sorted(comp_lines, key=lambda x: x[1][0][0])
        # Group with no name must be first
        if comp_lines[-1][0] == u'':
            comp_lines.insert(0, comp_lines.pop(-1))

        temp_array = []
        # Combining the identical elements in one line
        for group in comp_lines:
            first = u''
            last = u''
            prev = []
            first_index = 0
            last_index = 0
            temp_group = [group[0], []]

            group[1].sort(key=self.compare_ref)
            for element in group[1]:
                if group[1].index(element) == 0:
                    # first element
                    first = last = element[1]
                    prev = element[:]
                    if len(group[1]) == 1:
                        temp_group[1].append(element)
                        temp_array.append(temp_group)
                    continue

                if element[0] == prev[0] and int(element[1]) - 1 == int(prev[1]) and element[2:] == prev[2:]:
                    # equal elements
                    last = element[1]
                    last_index = group[1].index(element)
                else:
                    # different elements
                    if int(last) - int(first) > 0:
                        # several identical elements
                        count = int(last) - int(first) + 1
                        separator = u', '
                        if count > 2:
                            separator = u'-'
                        temp_element = group[1][last_index]
                        temp_element[1] = first + separator + last
                        temp_element[8] = str(count)
                        temp_group[1].append(temp_element)
                    else:
                        # next different element
                        temp_group[1].append(prev)
                    first = last = element[1]
                    first_index = last_index = group[1].index(element)

                if group[1].index(element) == len(group[1]) - 1:
                    # last element in the group
                    if int(last) - int(first) > 0:
                        # several identical elements
                        count = int(last) - int(first) + 1
                        separator = u', '
                        if count > 2:
                            separator = u'-'
                        temp_element = group[1][last_index]
                        temp_element[1] = first + separator + last
                        temp_element[8] = str(count)
                        temp_group[1].append(temp_element)
                    else:
                        temp_group[1].append(element)
                    temp_array.append(temp_group)
                prev = element[:]
        comp_lines = temp_array

        # Fill list of the components
        for group in comp_lines:
            if self.cur_group != group[0]:
                # New group title
                self.cur_group = group[0]

                if (self.cur_page == 1 and self.cur_line > 26) or (self.cur_page > 1 and self.cur_line > 29):
                    # If name of group at bottom of table without elements, go to beginning of a new
                    while self.cur_line != 1:
                        self.next_line()
                else:
                    self.next_line() # Skip one line

                self.replace_text(self.cur_table, u'#2:%d' % self.cur_line, group[0], group=True)
                self.next_line() # Skip one line
                self.next_line() # Moving to next line

            # Put all group lines to the table
            if group[0] == u'':
                # Elements without group
                prev = None
                for element in group[1]:
                    if prev == None:
                        prev = element[0]
                        self.set_line(element)
                        self.next_line()
                        continue
                    if element[0] != prev:
                        # Elements with different types separated by one empty line
                        self.next_line()
                        prev = element[0]
                    self.set_line(element)
                    self.next_line()

            else:
                # Elements with group
                for element in group[1]:
                    self.set_line(element)
                    self.next_line()

        if self.cur_line != 1:
            # Current table not empty - save it
            self.cur_table.setAttribute(u'name', u'стр. %d' % self.cur_page)
            self.complist.spreadsheet.addElement(self.cur_table)

    def save(self, complist_file_name):
        """
        Save created list of the components to the file.

        """
        # If the sheet of changes is needed - append it
        if self.need_changes_sheet:
            self.append_changes_sheet()
        # Fill stamp fields on each page
        for index, table in enumerate(self.complist.spreadsheet.getElementsByType(Table)):
            # First page - big stamp
            if index == 0:
                pg_cnt = len(self.complist.spreadsheet.getElementsByType(Table))
                if pg_cnt == 1:
                    pg_cnt = u''
                else:
                    pg_cnt = str(pg_cnt)

                self.replace_text(table, u'#5:1', self.developer)
                self.replace_text(table, u'#5:2', self.verifer)
                self.replace_text(table, u'#5:3', self.approver)
                self.replace_text(table, u'#5:4', self.decimal_num)
                self.replace_text(table, u'#5:5', self.title)
                self.replace_text(table, u'#5:6', str(index + 1))
                self.replace_text(table, u'#5:7', pg_cnt)
                self.replace_text(table, u'#5:8', self.comp)

            # Other pages - smal stamp
            else:
                self.replace_text(table, u'#5:1', self.decimal_num)
                self.replace_text(table, u'#5:2', str(index + 1))

        # Clear tables from labels
        for table in self.complist.spreadsheet.getElementsByType(Table):
            self.clear_table(table)

        # Add meta data
        version_file = open('version', 'r')
        version = version_file.read()
        version = version.replace('\n', '')
        version_file.close()
        creation_time = time.localtime()
        creation_time_str = '{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{min:02d}:{sec:02d}'.format(
                year = creation_time.tm_year,
                month = creation_time.tm_mon,
                day = creation_time.tm_mday,
                hour = creation_time.tm_hour,
                min = creation_time.tm_min,
                sec = creation_time.tm_sec
                )
        self.complist.meta.addElement(meta.CreationDate(text=creation_time_str))
        self.complist.meta.addElement(meta.InitialCreator(text='kicadbom2spec v{}'.format(version)))

        # Save file of list of the components
        self.complist.save(complist_file_name)

    def convert_decimal_num(self, num):
        """
        The correction of the decimal number (adding symbol "П" before the code
        of the schematic type).

        """
        num_parts = num.rsplit(u' Э', 1)
        if len(num_parts) > 1 and num_parts[1] in u'1234567':
            return u' ПЭ'.join(num_parts)
        else:
            return num

    def convert_title(self, title):
        """
        The correction of the title.

        """
        title_parts = title.rsplit(u'Схема электрическая ', 1)
        sch_types = (
            u'структурная',
            u'функциональная',
            u'принципиальная',
            u'соединений',
            u'подключения',
            u'общая',
            u'расположения'
            )
        if len(title_parts) > 1 and title_parts[1] in sch_types:
            return title_parts[0] + u'Перечень элементов'
        else:
            return title + u'\\nПеречень элементов'

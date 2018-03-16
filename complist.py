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

import os
import re
import time
import csv
from copy import deepcopy
from operator import itemgetter

import odf.opendocument
from odf.draw import Frame
from odf.text import P, LineBreak
from odf.table import *
from odf.style import Style, ParagraphProperties, TextProperties
from odf import dc, meta

from kicadsch import *

REF_REGEXP = r'(.*[^0-9])([0-9]+)'
NUM_REGEXP = u'([А-ЯA-Z0-9]+(?:[^А-ЯA-Z0-9][0-9\.\-\s]+)?)(Э[1-7])?'

class CompList():
    """
    Generating list of the components from KiCad Schematic
    and save it to *.ods file.

    """

    def __init__(self):

        # Variables for filling the list
        self.complist = None
        self.components_array = None
        self.complist_pages = []

        # Stamp fields
        self.developer = u''
        self.verifier = u''
        self.inspector = u''
        self.approver = u''
        self.decimal_num = u''
        self.title = u''
        self.company = u''

        # Options
        self.add_first_usage = False
        self.add_customer_fields = False
        self.add_changes_sheet = False
        self.fill_first_usage = False
        self.italic = False
        self.underline_group_name = True
        self.file_format = u'.ods' # u'.odt', u'.csv'
        self.empty_rows_groups = 1
        self.empty_rows_above = 0
        self.empty_rows_below = 0

        # Current state of filling list of the components
        self._cur_line = 1
        self._cur_page_num = 1
        self._cur_page = None
        self._lines_on_page = 0

    def _replace_text(self, page, label, text, group=False):
        """
        Replace 'label' (like #1:1) to 'text' in 'page'.
        If 'group' is set to 'True' will be used special formatting.

        """
        if self.file_format == u'.ods':
            self._replace_text_in_table(page, label, text, group)
        elif self.file_format == u'.odt':
            for table in page.body.getElementsByType(Table):
                self._replace_text_in_table(table, label, text, group)

    def _replace_text_in_table(self, table, label, text, group=False):
        """
        Replace 'label' (like #1:1) to 'text' in 'table'.
        If 'group' is set to 'True' will be used special formatting.

        """
        for row in table.getElementsByType(TableRow):
            for cell in row.getElementsByType(TableCell):
                for p in cell.getElementsByType(P):
                    for p_data in p.childNodes:
                        if p_data.tagName == u'Text':
                            if p_data.data == label:
                                text = text.encode('utf-8')
                                # Decoding internal escapes
                                text = text.decode('string_escape')
                                # Decoding escapes from KiCad
                                text = text.decode('string_escape')
                                text = text.decode('utf-8')
                                text_lines = text.split(u'\n')
                                p_data.data = text_lines[0]
                                # Line breaks
                                if len(text_lines) > 1:
                                    p_style = p.getAttribute(u'stylename')
                                    for line in text_lines[1:]:
                                        new_p = P(text=line)
                                        if self.file_format == u'.odt':
                                            new_p.setAttribute(u'stylename', p_style)
                                        cell.addElement(new_p)
                                if group == True:
                                    # Set center align and underline for group name
                                    if self.file_format == u'.ods':
                                        # If used ODS format the text properties stored
                                        # in cell style.
                                        groupStyleName = cell.getAttribute(u'stylename') + u'g'
                                    elif self.file_format == u'.odt':
                                        # But if used ODT format the text properties stored
                                        # in paragraph style inside cell.
                                        groupStyleName = u'group-name'
                                    try:
                                        groupStyle = self.complist.getStyleByName(groupStyleName)
                                        # Needed for backwards compatibility
                                        if groupStyle == None:
                                            raise
                                    except:
                                        if self.file_format == u'.ods':
                                            groupStyleName = cell.getAttribute(u'stylename')
                                        elif self.file_format == u'.odt':
                                            groupStyleName = p.getAttribute(u'stylename')
                                        groupStyle = deepcopy(self.complist.getStyleByName(groupStyleName))
                                        if self.file_format == u'.ods':
                                            groupStyle.setAttribute(u'name', groupStyleName + u'g')
                                        elif self.file_format == u'.odt':
                                            groupStyle.setAttribute(u'name', u'group-name')
                                        groupStyle.addElement(
                                            ParagraphProperties(textalign=u'center')
                                            )
                                        if self.underline_group_name == True:
                                            groupStyle.addElement(
                                                TextProperties(
                                                    textunderlinetype=u'single',
                                                    textunderlinestyle=u'solid',
                                                    )
                                                )
                                        self.complist.automaticstyles.addElement(groupStyle)
                                    if self.file_format == u'.ods':
                                        cell.setAttribute(u'stylename', groupStyleName + u'g')
                                    elif self.file_format == u'.odt':
                                        p.setAttribute(u'stylename', u'group-name')
                                return

    def _clear_page(self, page):
        """
        Clear 'page' of labels.

        """
        if self.file_format == u'.ods':
            self._clear_table(page)
        elif self.file_format == u'.odt':
            for table in page.body.getElementsByType(Table):
                self._clear_table(table)

    def _clear_table(self, table):
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


    def _next_line(self):
        """
        Moving to next line.
        If table is full, save it in list object and create a new one.

        """
        # Increase line counter
        self._cur_line += 1

        # First page of the list has 29 or 26 lines, other pages has 32 lines
        if self._cur_line > self._lines_on_page:
            # Table is full
            if self.file_format == u'.ods':
                self._cur_page.setAttribute(u'name', u'стр. %d' % self._cur_page_num)
            self.complist_pages.append(self._cur_page)

            self._cur_page = deepcopy(self._otherPagesPattern)
            if self.file_format == u'.odt':
                # Needed for getting styles in _replace_text_in_table
                self.complist = self._cur_page
            self._cur_page_num += 1
            self._cur_line = 1
            self._lines_on_page = 32

    def _get_final_values(self, element):
        """
        Get list with final fields values of component.
        """
        values = []
        # Reference
        ref = u''
        if int(element[9]) > 1:
            # Reference number: '5, 6'; '25-28' etc.
            ref = re.search(r'(\d+)(-|,\s?)(\d+)', element[1]).groups()
            if element[2]:
                # Reference: 'VD1*, VD2*'; 'C8*-C11*' etc.
                ref = (element[0] + u'%s*%s' + element[0] + u'%s*') % ref
            else:
                # Reference: 'VD1, VD2'; 'C8-C11' etc.
                ref = (element[0] + u'%s%s' + element[0] + u'%s') % ref
        else:
            # Reference: 'R5'; 'VT13' etc.
            ref = element[0] + element[1]
            # Add "*" mark if component "needs adjusting"
            if element[2]:
                ref = ref + '*'
        values.append(ref)
        # Value
        values.append(''.join(element[3:8]))
        # Count
        values.append(element[9])
        # Comment
        values.append(element[8])
        return values

    def _set_line(self, element):
        """
        Fill the line in list of the components using element's fields.

        """
        for index, value in enumerate(self._get_final_values(element)):
            self._replace_text(
                self._cur_page,
                u'#{}:{}'.format(index + 1, self._cur_line),
                value
                )

    def load(self, sch_file_name, comp_fields=None):
        """
        Load all components from KiCad Schematic file
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

        def apply_substitution(comp, ref, field_value):
            """
            Replace ${field_name} with value from field with name "field_name".

            """
            match = re.search(r'\$\{([^{}]*)\}', field_value)
            if match == None:
                return field_value
            else:
                substitution_value = u''
                if match.group(1) == u'Обозначение':
                    substitution_value = ref
                elif match.group(1) == u'Значение':
                    substitution_value = comp.fields[1].text
                elif match.group(1) == u'Посад.место':
                    substitution_value = comp.fields[2].text
                elif match.group(1) == u'Документация':
                    substitution_value = comp.fields[3].text
                else:
                    substitution_value = get_text_from_field(comp, match.group(1))

                new_field_value = field_value.replace(
                    u'${%s}' % match.group(1),
                    substitution_value,
                    1
                    )
                new_field_value = apply_substitution(comp, ref, new_field_value)
                return new_field_value

        def get_comp_by_ref(ref):
            """
            Get component object with reference "ref".

            """
            for comp in components:
                if comp.fields[0].text == ref:
                    return comp
                else:
                    if hasattr(comp, 'path_and_ref'):
                        for path_and_ref in comp.path_and_ref:
                            if path_and_ref[1] == ref:
                                return comp
            return None

        # Get title block description
        sch = Schematic(sch_file_name)
        self.developer = sch.descr.comment2.decode('utf-8')
        self.verifier = sch.descr.comment3.decode('utf-8')
        self.approver = sch.descr.comment4.decode('utf-8')
        self.decimal_num = self.convert_decimal_num(sch.descr.comment1)
        self.title = self.convert_title(sch.descr.title)
        self.company = sch.descr.comp.decode('utf-8')

        components = self.get_components(sch_file_name)
        comp_array = []
        if comp_fields:
            # Copy prepared fields
            comp_array = comp_fields[:]
        else:
            # Load all fields
            for comp in components:
                # Skip unannotated components
                if not comp.fields[0].text or comp.fields[0].text.endswith('?'):
                    continue
                # Skip components with not supported ref type
                if not re.match(REF_REGEXP, comp.fields[0].text):
                    continue
                # Skip components excluded manually
                for field in comp.fields:
                    if hasattr(field, u'name'):
                        if field.name == u'Исключён из ПЭ':
                            continue
                # Skip parts of the same component
                for row in comp_array:
                    if comp.fields[0].text == (row[1] + row[2]):
                        break
                else:
                    temp = []
                    temp.append(get_text_from_field(comp, u'Группа'))
                    ref_type = re.search(REF_REGEXP, comp.fields[0].text).group(1)
                    temp.append(ref_type)
                    ref_num = re.search(REF_REGEXP, comp.fields[0].text).group(2)
                    temp.append(ref_num)
                    for field in comp.fields:
                        if hasattr(field, u'name'):
                            if field.name == u'Подбирают при регулировании':
                                temp.append(True)
                                break
                    else:
                        temp.append(False)
                    temp.append(get_text_from_field(comp, u'Марка'))
                    temp.append(comp.fields[1].text)
                    temp.append(get_text_from_field(comp, u'Класс точности'))
                    temp.append(get_text_from_field(comp, u'Тип'))
                    temp.append(get_text_from_field(comp, u'Стандарт'))
                    temp.append(get_text_from_field(comp, u'Примечание'))
                    temp.append(u'1')
                    if hasattr(comp, 'path_and_ref'):
                        for ref in comp.path_and_ref:
                            # Skip unannotated components
                            if not ref[1] or ref[1].endswith('?'):
                                continue
                            # Skip parts of the same comp from different sheets
                            for value in comp_array:
                                tmp_ref = value[1] + value[2]
                                if tmp_ref == ref[1]:
                                    break
                            else:
                                new_temp = list(temp)
                                new_temp[1] = re.search(REF_REGEXP, ref[1]).group(1)
                                new_temp[2] = re.search(REF_REGEXP, ref[1]).group(2)
                                comp_array.append(new_temp)
                    else:
                        comp_array.append(temp)

        # Apply substitution
        for i in range(len(comp_array)):
            comp = get_comp_by_ref(comp_array[i][1] + comp_array[i][2])
            for ii in range(len(comp_array[i])):
                # Skip for ref_type, ref_num, need_adjust_flag and count
                if ii in (1, 2, 3, 9):
                    continue
                field_value = comp_array[i][ii]
                new_field_value = apply_substitution(
                    comp,
                    comp_array[i][1] + comp_array[i][2],
                    field_value
                    )
                comp_array[i][ii] = new_field_value

        comp_array = sorted(comp_array, key=itemgetter(0))

        # Split elements into groups
        # output - [['group',[[ref_type, ref_number, need_adjust_flag, mark, value, accuracy, type, GOST, comment, count], ... ]], ... ]
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

        # Sort components into every group by ref_num
        for group in comp_lines:
            group[1].sort(key=lambda num: int(num[1]))
            group[1].sort(key=lambda ref: ref[0])
        # Split noname group into subgroups by type (ref)
        noname_group = None
        named_groups = []
        for group in comp_lines:
            if group[0] == u'':
                noname_group = group
            else:
                named_groups.append(group)
        comp_lines = named_groups
        if noname_group != None:
            prev_comp_type = None
            temp_noname_group = [u'', []]
            for comp in noname_group[1]:
                if prev_comp_type == None or comp[0] == prev_comp_type:
                    temp_noname_group[1].append(comp)
                else:
                    comp_lines.append(temp_noname_group)
                    temp_noname_group = [u'', []]
                    temp_noname_group[1].append(comp)
                prev_comp_type = comp[0]
            else:
                if len(temp_noname_group[1]) > 0:
                    comp_lines.append(temp_noname_group)
        # Sort grops by reference (ref & num) of first element
        comp_lines = sorted(comp_lines, key=lambda ref: ref[1][0][1])
        comp_lines = sorted(comp_lines, key=lambda ref: ref[1][0][0])
        # Combining the identical elements in one line
        temp_array = []
        for group in comp_lines:
            first = u''
            last = u''
            prev = []
            first_index = 0
            last_index = 0
            temp_group = [group[0], []]
            for element in group[1]:
                if group[1].index(element) == 0:
                    # first element
                    first = last = element[1]
                    prev = element[:]
                    if len(group[1]) == 1:
                        temp_group[1].append(element)
                        temp_array.append(temp_group)
                    continue

                if element[0] == prev[0] and \
                        int(element[1]) - 1 == int(prev[1]) and \
                        element[2:] == prev[2:]:
                    # equal elements
                    last = element[1]
                    last_index = group[1].index(element)
                else:
                    # different elements
                    if int(last) - int(first) > 0:
                        # finish processing of several identical elements
                        count = int(last) - int(first) + 1
                        separator = u', '
                        if count > 2:
                            separator = u'-'
                        temp_element = group[1][last_index]
                        temp_element[1] = first + separator + last
                        temp_element[9] = str(count)
                        temp_group[1].append(temp_element)
                    else:
                        # next different element
                        temp_group[1].append(prev)
                    first = last = element[1]
                    first_index = last_index = group[1].index(element)

                if group[1].index(element) == len(group[1]) - 1:
                    # last element in the group
                    if int(last) - int(first) > 0:
                        # finish processing of several identical elements
                        count = int(last) - int(first) + 1
                        separator = u', '
                        if count > 2:
                            separator = u'-'
                        temp_element = group[1][last_index]
                        temp_element[1] = first + separator + last
                        temp_element[9] = str(count)
                        temp_group[1].append(temp_element)
                    else:
                        temp_group[1].append(element)
                    temp_array.append(temp_group)
                prev = element[:]
        self.components_array = temp_array

    def save(self, complist_file_name):
        """
        Save created list of the components to the file.

        """
        base_path = os.path.dirname(os.path.realpath(__file__))
        if self.file_format == u'.csv':
            # File for writing the list of the components
            file_name = os.path.splitext(complist_file_name)[0] + self.file_format
            headers_row = [u'Поз. обозначение', u'Наименование', u'Кол.', u'Примечание']
            empty_row = ['', '', '', '']
            with open(file_name, 'wb') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(headers_row)
                # Fill list of the components
                for group in self.components_array:
                    # One empty line-separator
                    csv_writer.writerow(empty_row)
                    if group[0] != u'':
                        # New group title
                        csv_writer.writerow(['', group[0], '', ''])
                    # Write all components of the group into list
                    for comp in group[1]:
                        csv_writer.writerow(self._get_final_values(comp))
            return
        elif self.file_format == u'.ods':
            # Load the pattern
            pattern = odf.opendocument.load(os.path.join(
                base_path, u'patterns', u'all_in_one.ods'))
            for sheet in pattern.spreadsheet.getElementsByType(Table):
                # Patterns for first page
                if sheet.getAttribute(u'name') == u'First1':
                    self._firstPagePatternV1 = sheet
                elif sheet.getAttribute(u'name') == u'First2':
                    self._firstPagePatternV2 = sheet
                elif sheet.getAttribute(u'name') == u'First3':
                    self._firstPagePatternV3 = sheet
                elif sheet.getAttribute(u'name') == u'First4':
                    self._firstPagePatternV4 = sheet
                # Pattern for other pages
                elif sheet.getAttribute(u'name') == u'Other':
                    self._otherPagesPattern = sheet
                # Pattern for last pages (the changes sheet)
                elif sheet.getAttribute(u'name') == u'Last':
                    self._lastPagePattern = sheet

            # Create list of the components file object
            self.complist = odf.opendocument.OpenDocumentSpreadsheet()

            # Copy all parameters from pattern to list of the components
            for font in pattern.fontfacedecls.childNodes[:]:
                self.complist.fontfacedecls.addElement(font)
            for style in pattern.styles.childNodes[:]:
                self.complist.styles.addElement(style)
            for masterstyle in pattern.masterstyles.childNodes[:]:
                self.complist.masterstyles.addElement(masterstyle)
            for autostyle in pattern.automaticstyles.childNodes[:]:
                self.complist.automaticstyles.addElement(autostyle)
            for setting in pattern.settings.childNodes[:]:
                self.complist.settings.addElement(setting)
        elif self.file_format == u'.odt':
            # Patterns for first page
            self._firstPagePatternV1 = odf.opendocument.load(os.path.join(
                base_path, u'patterns', u'first1.odt'))
            self._firstPagePatternV2 = odf.opendocument.load(os.path.join(
                base_path, u'patterns', u'first2.odt'))
            self._firstPagePatternV3 = odf.opendocument.load(os.path.join(
                base_path, u'patterns', u'first3.odt'))
            self._firstPagePatternV4 = odf.opendocument.load(os.path.join(
                base_path, u'patterns', u'first4.odt'))
            # Pattern for other pages
            self._otherPagesPattern = odf.opendocument.load(os.path.join(
                base_path, u'patterns', u'other.odt'))
            # Pattern for last pages (the changes sheet)
            self._lastPagePattern = odf.opendocument.load(os.path.join(
                base_path, u'patterns', u'last.odt'))

        # Select pattern for first page
        if not self.add_first_usage and not self.add_customer_fields:
            self._cur_page = self._firstPagePatternV1
            self._lines_on_page = 29
        elif self.add_first_usage and not self.add_customer_fields:
            self._cur_page = self._firstPagePatternV2
            self._lines_on_page = 29
        elif not self.add_first_usage and self.add_customer_fields:
            self._cur_page = self._firstPagePatternV3
            self._lines_on_page = 26
        elif self.add_first_usage and self.add_customer_fields:
            self._cur_page = self._firstPagePatternV4
            self._lines_on_page = 26

        if self.file_format == u'.odt':
            # Needed for getting styles in _replace_text_in_table
            self.complist = self._cur_page

        # Fill list of the components
        for group in self.components_array:
            # One empty line-separator
            if not (self._cur_page_num == 1 and self._cur_line == 1):
                self._next_line() # Skip one line

            if group[0] != u'':
                # New group title
                if self._cur_line == self._lines_on_page:
                    # If name of group at bottom of table without elements, go to beginning of a new table
                    while self._cur_line != 1:
                        self._next_line()
                self._replace_text(self._cur_page, u'#2:%d' % self._cur_line, group[0], group=True)
                self._next_line() # Skip one line
            # Place all components of the group into list
            for comp in group[1]:
                self._set_line(comp)
                self._next_line()

        # Current table not empty - save it
        if self._cur_line != 1:
            # Set last line as current
            self._cur_line = self._lines_on_page
            # Go to next empty page and save current
            self._next_line()

        # If the sheet of changes is needed - append it
        if self.add_changes_sheet == True:
            self._cur_page = self._lastPagePattern
            if self.file_format == u'.ods':
                self._cur_page.setAttribute(u'name', u'стр. %d' % self._cur_page_num)
            self.complist_pages.append(self._cur_page)

        # Fill stamp fields on each page
        pg_cnt = len(self.complist_pages)
        for index, page in enumerate(self.complist_pages):
            # First page - big stamp
            if index == 0:

                self._replace_text(page, u'#5:1', self.developer)
                self._replace_text(page, u'#5:2', self.verifier)
                self._replace_text(page, u'#5:3', self.inspector)
                self._replace_text(page, u'#5:4', self.approver)
                self._replace_text(page, u'#5:5', self.decimal_num)
                self._replace_text(page, u'#5:6', self.title)
                if pg_cnt > 1:
                    self._replace_text(page, u'#5:7', str(index + 1))
                self._replace_text(page, u'#5:8', str(pg_cnt))
                self._replace_text(page, u'#5:9', self.company)
                if self.fill_first_usage:
                    first_usage = re.search(NUM_REGEXP, self.decimal_num)
                    if first_usage != None:
                        self._replace_text(page, u'#6:1', first_usage.group(1).rstrip(' '))

            # Other pages - small stamp
            else:
                self._replace_text(page, u'#5:1', self.decimal_num)
                self._replace_text(page, u'#5:2', str(index + 1))

        # Clear tables from labels
        for page in self.complist_pages:
            self._clear_page(page)

        # Merge all pages in single document
        # ODS
        if self.file_format == u'.ods':
            for table in self.complist_pages:
                self.complist.spreadsheet.addElement(table)
        # ODT
        elif self.file_format == u'.odt':
            self.complist = self.complist_pages[0]
            if len(self.complist_pages) > 1:
                # Every style, frame or table must have unique name
                # on every separate page!
                for num, page in enumerate(self.complist_pages[1:]):
                    for autostyle in page.automaticstyles.childNodes[:]:
                        astyle_name = autostyle.getAttribute(u'name')
                        astyle_name = u'_{}_{}'.format(num + 2, astyle_name)
                        autostyle.setAttribute(u'name', astyle_name)
                        self.complist.automaticstyles.addElement(autostyle)
                    for body in page.body.childNodes[:]:
                        for frame in body.getElementsByType(Frame):
                            name = frame.getAttribute(u'name')
                            stylename = frame.getAttribute(u'stylename')
                            name = str(num + 2) + name
                            stylename = u'_{}_{}'.format(num + 2, stylename)
                            frame.setAttribute(u'name', name)
                            frame.setAttribute(u'stylename', stylename)
                            for table in frame.getElementsByType(Table):
                                name = table.getAttribute(u'name')
                                stylename = table.getAttribute(u'stylename')
                                name = str(num + 2) + name
                                stylename = u'_{}_{}'.format(num + 2, stylename)
                                table.setAttribute(u'name', name)
                                table.setAttribute(u'stylename', stylename)
                                for col in table.getElementsByType(TableColumn):
                                    stylename = col.getAttribute(u'stylename')
                                    stylename = u'_{}_{}'.format(num + 2, stylename)
                                    col.setAttribute(u'stylename', stylename)
                                for row in table.getElementsByType(TableRow):
                                    stylename = row.getAttribute(u'stylename')
                                    stylename = u'_{}_{}'.format(num + 2, stylename)
                                    row.setAttribute(u'stylename', stylename)
                                    for cell in row.getElementsByType(TableCell):
                                        stylename = cell.getAttribute(u'stylename')
                                        stylename = u'_{}_{}'.format(num + 2, stylename)
                                        cell.setAttribute(u'stylename', stylename)
                                        for p in cell.getElementsByType(P):
                                            stylename = p.getAttribute(u'stylename')
                                            stylename = u'_{}_{}'.format(num + 2, stylename)
                                            p.setAttribute(u'stylename', stylename)
                        self.complist.body.addElement(body)

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

        # Set font style
        styles = self.complist.automaticstyles.childNodes + self.complist.styles.childNodes
        for style in styles:
            for node in style.childNodes:
                if node.tagName == u'style:text-properties':
                    for attr_key in node.attributes.keys():
                        if attr_key[-1] == u'font-style':
                            if self.italic == True:
                                node.attributes[attr_key] = u'italic'
                            else:
                                node.attributes[attr_key] = u'regular'
                            break
                    break

        # Save file of list of the components
        file_name = os.path.splitext(complist_file_name)[0] + self.file_format
        self.complist.save(file_name)

    def convert_decimal_num(self, num):
        """
        The correction of the decimal number (adding symbol "П" before the code
        of the schematic type).

        """
        num_parts = re.search(NUM_REGEXP, num)
        if num_parts != None:
            if num_parts.group(1) != None and num_parts.group(2) != None:
                return u'П'.join(num_parts.groups())
            else:
                return num
        else:
            return num

    def convert_title(self, title):
        """
        The correction of the title.

        """
        suffix = u'Перечень элементов'
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
            if not title_parts[0].endswith(u'\\n'):
                suffix = u'\\n' + suffix
            return title_parts[0] + suffix
        else:
            if title != u'':
                suffix = u'\\n' + suffix
            return title + suffix

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
        return list(set(sheets))

    def get_components(self, sch_file_name, root_only=False):
        """
        Open KiCad Schematic file and get all components from it.

        """
        components = []
        if os.path.isabs(sch_file_name):
            exec_path = os.path.dirname(os.path.realpath(__file__))
            os.chdir(os.path.dirname(sch_file_name))
        sch = Schematic(sch_file_name)
        for item in sch.items:
            if item.__class__.__name__ == u'Comp':
                # Skip power symbols
                if not item.fields[0].text.startswith(u'#'):
                    components.append(item)
            elif item.__class__.__name__ == u'Sheet' and not root_only:
                components.extend(self.get_components(item.file_name))
        if os.path.isabs(sch_file_name):
            os.chdir(exec_path)
        return components

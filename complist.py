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

import csv
import os
import re
import time
from copy import deepcopy
from operator import itemgetter

import wx

import odf.opendocument
from odf.draw import Frame
from odf.style import Style, ParagraphProperties, TextProperties
from odf.table import *
from odf.text import P, LineBreak
from odf import dc, meta

from kicadsch import *

REF_REGEXP = re.compile(u'(.*[^0-9])([0-9]+)', re.U)
NUM_REGEXP = re.compile(u'([А-ЯA-Z0-9]+(?:[^А-ЯA-Z0-9][0-9\.\-\s]+)?)(Э[1-7])?', re.U)

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

        # Callback
        # This will be called for getting group name in singular
        self.get_singular_group_name = None

        # Stamp fields
        self.developer = u''
        self.verifier = u''
        self.inspector = u''
        self.approver = u''
        self.decimal_num = u''
        self.title = u''
        self.company = u''

        # Options
        self.file_format = u'.ods' # u'.odt', u'.csv'
        self.all_components = False
        self.add_units = False
        self.space_before_units = False
        self.empty_rows_after_group = 1
        self.empty_rows_everywhere = False
        self.prohibit_empty_rows_on_top = False
        self.gost_in_group_name = False
        self.singular_group_name = True
        self.prohibit_group_name_at_bottom = False
        self.add_first_usage = False
        self.fill_first_usage = False
        self.add_customer_fields = False
        self.add_changes_sheet = False
        self.italic = False
        self.underline_group_name = False
        self.center_group_name = False
        self.center_reference = False

        # Additional data
        self.separators_dict = {
            u'марка':['',''],
            u'значение':['',''],
            u'класс точности':['',''],
            u'тип':['',''],
            u'стандарт':['','']
            }
        self.aliases_dict = {
            u'группа':u'Группа',
            u'марка':u'Марка',
            u'значение':u'',
            u'класс точности':u'Класс точности',
            u'тип':u'Тип',
            u'стандарт':u'Стандарт',
            u'примечание':u'Примечание'
            }
        self.multipliers_dict = {
            u'G': u'Г',
            u'M': u'М',
            u'k': u'к',
            u'm': u'м',
            u'μ': u'мк',
            u'u': u'мк',
            u'U': u'мк',
            u'n': u'н',
            u'p': u'п'
            }

        # Current state of filling the list of components
        self._cur_line = 1
        self._cur_page_num = 1
        self._cur_page = None
        self._lines_on_page = 0

    def _get_width_factor(self, label, text):
        """
        Returns width factor in % if text is not fit in table column.

        """
        if len(text) == 0:
            return 100
        elif label.startswith('#1:'):
            # Size of text that fits in any case
            if len(text) <= 6:
                return 100
            font_size = 14 # pt
            column_width = 17.5 # mm
        elif label.startswith('#2:'):
            # Size of text that fits in any case
            if len(text) <= 37:
                return 100
            font_size = 14 # pt
            column_width = 108 # mm
        elif label.startswith('#3:'):
            # Size of text that fits in any case
            if len(text) <= 3:
                return 100
            font_size = 14 # pt
            column_width = 9 # mm
        elif label.startswith('#4:'):
            # Size of text that fits in any case
            if len(text) <= 14:
                return 100
            font_size = 14 # pt
            column_width = 41.5 # mm
        elif label in ('#5:1', '#5:2', '#5:3', '#5:4'):
            # Size of text that fits in any case
            if len(text) <= 8:
                return 100
            font_size = 12 # pt
            column_width = 20.5 # mm
        else:
            return 100

        dc = wx.ScreenDC()
        pixel_per_mm = dc.GetPPI()[0] / 25.4
        if 'gtk3' in wx.version():
            # FIXME GTK3 has a bug and returns wrong PPI!
            pixel_per_mm = 3.78 # 96 / 25.4

        if self.italic == True:
            font_style = wx.FONTSTYLE_ITALIC
        else:
            font_style = wx.FONTSTYLE_SLANT

        font = wx.Font(
            family=wx.FONTFAMILY_DEFAULT,
            pointSize=font_size,
            style=font_style,
            weight=wx.FONTWEIGHT_NORMAL,
            faceName='OpenGost Type B TT'
            )

        dc.SetFont(font)

        text_width, text_height = dc.GetTextExtent(text)
        # wx draws text differently than libreoffice, correction needed
        text_width -= len(text) * 0.35

        width_factor_float = (100 * column_width * pixel_per_mm) / text_width
        width_factor_int = int(width_factor_float)
        if (width_factor_float % 1) > 0 \
                and width_factor_int > 1:
            width_factor_int -= 1

        return width_factor_int

    def _get_unescaped_text(self, text):
        """
        Remove any escapes in text.

        """
        pure_text = text.encode('utf-8')
        # Decoding internal escapes
        pure_text = pure_text.decode('string_escape')
        # Decoding escapes from KiCad
        pure_text = pure_text.decode('string_escape')
        pure_text = pure_text.decode('utf-8')
        return pure_text

    def _replace_text(self, page, label, text, center=False, underline=False):
        """
        Replace 'label' (like #1:1) to 'text' in every table on 'page'.
        If 'center' is set to 'True' text will be aligned by center of the cell.
        If 'underline' is set to 'True' text will be underlined.

        """
        if self.file_format == u'.ods':
            self._replace_text_in_table(page, label, text, center, underline)
        elif self.file_format == u'.odt':
            for table in page.body.getElementsByType(Table):
                self._replace_text_in_table(table, label, text, center, underline)

    def _replace_text_in_table(self, table, label, text, center=False, underline=False):
        """
        Replace 'label' (like #1:1) to 'text' in 'table'.
        If 'center' is set to 'True' text will be aligned by center of the cell.
        If 'underline' is set to 'True' text will be underlined.

        """
        for row in table.getElementsByType(TableRow):
            for cell in row.getElementsByType(TableCell):
                for p in cell.getElementsByType(P):
                    for p_data in p.childNodes:
                        if p_data.tagName == u'Text':
                            if p_data.data == label:
                                text = self._get_unescaped_text(text)
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
                                if center == True or underline == True:
                                    suffix = u''
                                    if center == True:
                                        suffix += u'_c'
                                    if underline == True:
                                        suffix += u'_u'
                                    # Set center align and/or underline
                                    if self.file_format == u'.ods':
                                        # If used ODS format the text properties stored
                                        # in cell style.
                                        groupStyleName = cell.getAttribute(u'stylename') + suffix
                                    elif self.file_format == u'.odt':
                                        # But if used ODT format the text properties stored
                                        # in paragraph style inside cell.
                                        groupStyleName = suffix
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
                                            groupStyleName += suffix
                                            groupStyle.setAttribute(u'name', groupStyleName)
                                        elif self.file_format == u'.odt':
                                            groupStyle.setAttribute(u'name', suffix)
                                        if center == True:
                                            groupStyle.addElement(
                                                ParagraphProperties(
                                                    textalign=u'center'
                                                    )
                                                )
                                        if underline == True:
                                            groupStyle.addElement(
                                                TextProperties(
                                                    textunderlinetype=u'single',
                                                    textunderlinestyle=u'solid'
                                                    )
                                                )
                                        self.complist.automaticstyles.addElement(groupStyle)
                                    if self.file_format == u'.ods':
                                        cell.setAttribute(u'stylename', groupStyleName)
                                    elif self.file_format == u'.odt':
                                        p.setAttribute(u'stylename', suffix)

                                # Fit text to cell in *.odt (*.ods does it automatically)
                                if self.file_format == u'.odt':
                                    width_factor = self._get_width_factor(label, text)
                                    if width_factor < 100:
                                        suffix = u'_%d' % width_factor
                                        curStyleName = p.getAttribute(u'stylename')
                                        newStyleName = curStyleName + suffix
                                        try:
                                            newStyle = self.complist.getStyleByName(newStyleName)
                                            # Needed for backwards compatibility
                                            if newStyle == None:
                                                raise
                                        except:
                                            newStyle = deepcopy(self.complist.getStyleByName(curStyleName))
                                            newStyle.setAttribute(u'name', newStyleName)
                                            newStyle.addElement(
                                                TextProperties(
                                                    textscale=u'%d%%' % width_factor
                                                    )
                                                )
                                            self.complist.automaticstyles.addElement(newStyle)
                                        p.setAttribute(u'stylename', newStyleName)

                                return

    def _clear_page(self, page):
        """
        Clear every table on 'page' of labels.

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
                            if re.search(u'#\d+:\d+', p_data.data) != None:
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

    def _get_final_values(self, element, with_group=False):
        """
        Get list with final fields values of component.
        """
        values = []

        group, \
        ref_type, \
        ref_num, \
        need_adjust_flag, \
        mark, \
        value, \
        accuracy, \
        type_, \
        gost, \
        comment, \
        count = element

        # Reference
        ref = u''
        if int(count) > 1:
            # Reference number: '5, 6'; '25-28' etc.
            ref = re.search(u'(\d+)(-|,\s?)(\d+)', ref_num).groups()
            if need_adjust_flag == True:
                # Reference: 'VD1*, VD2*'; 'C8*-C11*' etc.
                ref = (ref_type + u'%s*%s' + ref_type + u'%s*') % ref
            else:
                # Reference: 'VD1, VD2'; 'C8-C11' etc.
                ref = (ref_type + u'%s%s' + ref_type + u'%s') % ref
        else:
            # Reference: 'R5'; 'VT13' etc.
            ref = ref_type + ref_num
            # Add "*" mark if component "needs adjusting"
            if need_adjust_flag == True:
                ref = ref + u'*'
        values.append(ref)

        # Name
        name = u''
        # Adding separators
        if mark != u'':
            name += "{prefix}{value}{suffix}".format(
                    prefix = self.separators_dict[u'марка'][0],
                    value = mark,
                    suffix = self.separators_dict[u'марка'][1]
                    )
        if value != u'':
            # Automatically units addition
            if self.add_units == True:
                num_value = u''
                multiplier = u''
                units = u''
                mult_keys, mult_values = zip(*self.multipliers_dict.items())
                multipliers = mult_keys + mult_values
                multipliers = list(set(multipliers))
                # 2u7, 2н7, 4m7, 5k1 etc.
                regexp_1= re.compile(u'^(\d+)({})(\d+)$'.format(u'|'.join(multipliers)), re.U)
                # 2.7 u, 2700p, 4.7 m, 470u, 5.1 k, 510 etc.
                regexp_2= re.compile(u'^(\d+(?:[\.,]\d+)?)\s*({})?$'.format(u'|'.join(multipliers)), re.U)
                if ref_type.startswith(u'C') and not value.endswith(u'Ф'):
                    units = u'Ф'
                    if re.match(u'^\d+$', value):
                        num_value = value
                        multiplier = u'п'
                    elif re.match(u'^\d+[\.,]\d+$', value):
                        num_value = value
                        multiplier = u'мк'
                    else:
                        num_value = value.rstrip(u'F')
                        num_value = num_value.strip()
                        if re.match(regexp_1, num_value):
                            search_res = re.search(regexp_1, num_value).groups()
                            num_value = search_res[0] + ',' + search_res[2]
                            multiplier = search_res[1]
                        elif re.match(regexp_2, num_value):
                            search_res = re.search(regexp_2, num_value).groups()
                            num_value = search_res[0]
                            multiplier = search_res[1]
                        else:
                            num_value = u''
                elif ref_type.startswith(u'L') and not value.endswith(u'Гн'):
                    units = u'Гн'
                    num_value = value.rstrip(u'H')
                    num_value = num_value.strip()
                    if re.match(regexp_1, num_value):
                        search_res = re.search(regexp_1, num_value).groups()
                        num_value = search_res[0] + ',' + search_res[2]
                        multiplier = search_res[1]
                    elif re.match(regexp_2, num_value):
                        search_res = re.search(regexp_2, num_value).groups()
                        num_value = search_res[0]
                        if search_res[1] == None:
                            multiplier = u'мк'
                        else:
                            multiplier = search_res[1]
                    else:
                        num_value = u''
                elif ref_type.startswith(u'R') and not value.endswith(u'Ом'):
                    units = u'Ом'
                    num_value = value.rstrip(u'Ω')
                    if num_value.endswith(u'Ohm') or num_value.endswith(u'ohm'):
                        num_value = num_value[:-3]
                    num_value = num_value.strip()
                    if re.match(u'R\d+', num_value):
                        num_value = num_value.replace(u'R', u'0,')
                    elif re.match(u'\d+R\d+', num_value):
                        num_value = num_value.replace(u'R', u',')
                    elif re.match(regexp_1, num_value):
                        search_res = re.search(regexp_1, num_value).groups()
                        num_value = search_res[0] + ',' + search_res[2]
                        multiplier = search_res[1]
                    elif re.match(regexp_2, num_value):
                        search_res = re.search(regexp_2, num_value).groups()
                        num_value = search_res[0]
                        if search_res[1] != None:
                            multiplier = search_res[1]
                    else:
                        num_value = u''
                if num_value != u'':
                    # Translate multiplier
                    if multiplier in self.multipliers_dict.keys():
                        multiplier = self.multipliers_dict[multiplier]
                    value = num_value.replace(u'.', u',')
                    if self.space_before_units == True:
                        value += u' '
                    value += multiplier
                    value += units
            name += "{prefix}{value}{suffix}".format(
                    prefix = self.separators_dict[u'значение'][0],
                    value = value,
                    suffix = self.separators_dict[u'значение'][1]
                    )
        if accuracy != u'':
            name += "{prefix}{value}{suffix}".format(
                    prefix = self.separators_dict[u'класс точности'][0],
                    value = accuracy,
                    suffix = self.separators_dict[u'класс точности'][1]
                    )
        if type_ != u'':
            name += "{prefix}{value}{suffix}".format(
                    prefix = self.separators_dict[u'тип'][0],
                    value = type_,
                    suffix = self.separators_dict[u'тип'][1]
                    )
        if gost != u'':
            name += "{prefix}{value}{suffix}".format(
                    prefix = self.separators_dict[u'стандарт'][0],
                    value = gost,
                    suffix = self.separators_dict[u'стандарт'][1]
                                )
        if with_group == True:
            try:
                singular_group_name = self.get_singular_group_name(group)
            except:
                singular_group_name = group
            name = singular_group_name + u' ' + name
        values.append(name)

        # Count
        values.append(count)

        # Comment
        values.append(comment)

        return values

    def _get_group_names_with_gost(self, group):
        """
        Get list of group names with GOST for every mark of components
        and prepared components (without GOST).
        """
        group_name = group[0][0]
        gost = group[0][8]
        components = deepcopy(group)

        # Check if GOST is equal in components
        for comp in components:
            if comp[8] != gost:
                break
        else:
            # Clear GOST in every component
            for comp in components:
                comp[8] = u''
            # Group title is Groupname + GOST (without Mark)
            return [' '.join([group_name, gost])], components

        # Create collection of unique set of groupname, mark and gost
        group_names_parts_with_gost = []
        multi_components_in_group = False
        for comp in components:
            mark = comp[4]
            if mark == u'':
                # If Mark field is empty to use Value instead
                mark = comp[5]
            gost = comp[8]
            if mark != u'' and gost != u'':
                group_name_parts = [group_name, mark, gost]
                if not group_name_parts in group_names_parts_with_gost:
                    group_names_parts_with_gost.append(group_name_parts)
                else:
                    multi_components_in_group = True

        if multi_components_in_group:
            for comp in components:
                comp[8] = u''

        # Split mark into parts by non-alphabetical chars
        for group_name_parts in group_names_parts_with_gost:
            mark_string = group_name_parts[1]
            mark_parts = []
            # First part without prefix
            res = re.search(u'[^A-Za-zА-Яа-я0-9]*([A-Za-zА-Яа-я0-9]+)($|[^A-Za-zА-Яа-я0-9].*)', mark_string)
            if res == None:
                group_name_parts[1] = [mark_string]
                continue
            mark_parts.append(res.groups()[0])
            mark_string = res.groups()[1]
            # Other parts with delimiters as prefix
            while True:
                res = re.search(u'([^A-Za-zА-Яа-я0-9]+[A-Za-zА-Яа-я0-9_\.,]+)($|[^A-Za-zА-Яа-я0-9].*)', mark_string)
                if res != None:
                    mark_parts.append(res.groups()[0])
                    mark_string = res.groups()[1]
                else:
                    break
            group_name_parts[1] = mark_parts

        # Create set of groupname, mark and gost with unique GOST
        # and common part of Mark
        group_names_parts_with_unique_gost = []
        for group_name_parts in group_names_parts_with_gost:
            group_name, mark_parts, gost = group_name_parts
            for group_name_unique_parts in group_names_parts_with_unique_gost:
                if group_name_unique_parts[2] == gost \
                        and group_name_unique_parts[1][0] == mark_parts[0]:
                    # Leave only common parts of Mark
                    list_len = len(mark_parts)
                    if list_len > len(group_name_unique_parts[1]):
                        list_len = len(group_name_unique_parts[1])
                    for i in range(list_len):
                        if group_name_unique_parts[1][i] != mark_parts[i]:
                            group_name_unique_parts[1] = mark_parts[:i]
                            break
                    break
            else:
                # Format: [Groupname, [Markparts, ...], GOST]
                group_names_parts_with_unique_gost.append([group_name, mark_parts[:], gost])

        # Concatenate parts of names together
        group_names = []
        if len(group_names_parts_with_unique_gost) == 1:
            name = group_names_parts_with_unique_gost[0][0] + u' ' + \
                   group_names_parts_with_unique_gost[0][2]
            group_names.append(name)
        elif not multi_components_in_group:
            name = group_names_parts_with_unique_gost[0][0]
            group_names.append(name)
        else:
            for group_name_parts in group_names_parts_with_unique_gost:
                group_name_parts[1] = u''.join(group_name_parts[1])
                name = u' '.join(group_name_parts)
                group_names.append(name)

        # If GOST or Mark not present - use default group name
        if group_names == []:
            group_names = [group_name]

        return group_names, components

    def _set_line(self, element, with_group=False):
        """
        Fill the line in list of the components using element's fields.

        """
        for index, value in enumerate(self._get_final_values(element, with_group)):
            center = False
            # Reference column
            if index == 0:
                center = self.center_reference

            self._replace_text(
                self._cur_page,
                u'#{}:{}'.format(index + 1, self._cur_line),
                value,
                center=center
                )

    def load(self, sch_file_name):
        """
        Load values of the fields from all components of
        KiCad Schematic file.

        """

        def get_text_from_field(comp, field_name):
            """
            If field has 'name' then get text from it.

            """
            for field in comp.fields:
                if hasattr(field, u'name'):
                    if field.name == field_name:
                        return field.text.decode('utf-8')
            return u''

        def apply_substitution(comp, ref, field_value):
            """
            Replace ${field_name} with value from field with name "field_name".

            """
            match = re.search(u'\$\{([^{}]*)\}', field_value)
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
                    if hasattr(comp, u'path_and_ref'):
                        for path_and_ref in comp.path_and_ref:
                            if path_and_ref[1] == ref:
                                return comp
            return None

        # Get title block description
        sch = Schematic(sch_file_name)
        self.developer = sch.descr.comment2.decode('utf-8')
        self.verifier = sch.descr.comment3.decode('utf-8')
        self.approver = sch.descr.comment4.decode('utf-8')
        self.decimal_num = self.convert_decimal_num(sch.descr.comment1.decode('utf-8'))
        self.title = self.convert_title(sch.descr.title.decode('utf-8'))
        self.company = sch.descr.comp.decode('utf-8')

        # Load all fields
        components = self.get_components(sch_file_name)
        comp_array = []
        for comp in components:
            # Skip unannotated components
            if not comp.fields[0].text or comp.fields[0].text.endswith(u'?'):
                continue
            # Skip components with not supported ref type
            if not re.match(REF_REGEXP, comp.fields[0].text):
                continue
            # Skip components excluded manually
            if self.all_components == False:
                try:
                    for field in comp.fields:
                        if hasattr(field, u'name'):
                            if field.name.decode('utf-8') == u'Исключён из ПЭ':
                                raise
                except:
                    continue
            # Skip parts of the same component
            for row in comp_array:
                if comp.fields[0].text == (row[1] + row[2]):
                    break
            else:
                temp = []
                temp.append(get_text_from_field(
                    comp,
                    self.aliases_dict[u'группа']
                    ))
                ref_type = re.search(REF_REGEXP, comp.fields[0].text).group(1)
                temp.append(ref_type)
                ref_num = re.search(REF_REGEXP, comp.fields[0].text).group(2)
                temp.append(ref_num)
                for field in comp.fields:
                    if hasattr(field, u'name'):
                        if field.name.decode('utf-8') == u'Подбирают при регулировании':
                            temp.append(True)
                            break
                else:
                    temp.append(False)
                temp.append(get_text_from_field(
                    comp,
                    self.aliases_dict[u'марка']
                    ))
                if self.aliases_dict[u'значение'] == u'':
                    temp.append(comp.fields[1].text.decode('utf-8'))
                else:
                    temp.append(get_text_from_field(
                        comp,
                        self.aliases_dict[u'значение']
                        ))
                temp.append(get_text_from_field(
                    comp,
                    self.aliases_dict[u'класс точности']
                    ))
                temp.append(get_text_from_field(
                    comp,
                    self.aliases_dict[u'тип']
                    ))
                temp.append(get_text_from_field(
                    comp,
                    self.aliases_dict [u'стандарт']
                    ))
                temp.append(get_text_from_field(
                    comp,
                    self.aliases_dict [u'примечание']
                    ))
                temp.append(u'1')
                if hasattr(comp, u'path_and_ref'):
                    for ref in comp.path_and_ref:
                        # Skip unannotated components
                        if not ref[1] or ref[1].endswith(u'?'):
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
                if ii in (1, 2, 3, 10):
                    continue
                field_value = comp_array[i][ii]
                new_field_value = apply_substitution(
                    comp,
                    comp_array[i][1] + comp_array[i][2],
                    field_value
                    )
                comp_array[i][ii] = new_field_value

        # Sort all components by ref_type
        comp_array = sorted(comp_array, key=itemgetter(1))

        # Split elements into groups based on ref_type
        # input: list of components;
        # every component represent as [group, ref_type, ref_number, need_adjust_flag, mark, value, accuracy, type, GOST, comment, count];
        # output: list of groups;
        # every group represent as list of components.
        group_array = []
        grouped_comp_array = []
        cur_ref = None
        for comp in comp_array:
            if cur_ref == None:
                # First component
                group_array.append(comp)
                cur_ref = comp[1]
            elif comp[1] == cur_ref:
                # The same type
                group_array.append(comp)
            else:
                # Next group
                grouped_comp_array.append(group_array)
                group_array = [comp]
                cur_ref = comp[1]
        # Append last group
        grouped_comp_array.append(group_array)

        # Sort components into every group by ref_num
        for group in grouped_comp_array:
            group.sort(key=lambda num: int(num[2]))

        # Split every group by group name
        # (may have different name with same ref_type)
        comp_array = grouped_comp_array[:]
        grouped_comp_array = []
        for group in comp_array:
            cur_name = None
            group_array = []
            for comp in group:
                if cur_name == None:
                    # First component
                    group_array.append(comp)
                    cur_name = comp[0]
                elif comp[0] == cur_name:
                    # The same type
                    group_array.append(comp)
                else:
                    # Next group
                    grouped_comp_array.append(group_array)
                    group_array = [comp]
                    cur_name = comp[0]
            # Append last group
            grouped_comp_array.append(group_array)

        # Combining the identical elements in one line
        temp_array = []
        for group in grouped_comp_array:
            first = u''
            last = u''
            prev = None
            first_index = 0
            last_index = 0
            temp_group = []
            for element in group:
                if group.index(element) == 0:
                    # first element
                    first = last = element[2]
                    prev = element[:]
                    if len(group) == 1:
                        temp_group.append(element)
                        temp_array.append(temp_group)
                    continue

                if element[:2] == prev[:2] and \
                        int(element[2]) - 1 == int(prev[2]) and \
                        element[3:] == prev[3:]:
                    # equal elements
                    last = element[2]
                    last_index = group.index(element)
                else:
                    # different elements
                    if int(last) - int(first) > 0:
                        # finish processing of several identical elements
                        count = int(last) - int(first) + 1
                        separator = u', '
                        if count > 2:
                            separator = u'-'
                        temp_element = group[last_index]
                        temp_element[2] = first + separator + last
                        temp_element[10] = str(count)
                        temp_group.append(temp_element)
                    else:
                        # next different element
                        temp_group.append(prev)
                    first = last = element[2]
                    first_index = last_index = group.index(element)

                if group.index(element) == len(group) - 1:
                    # last element in the group
                    if int(last) - int(first) > 0:
                        # finish processing of several identical elements
                        count = int(last) - int(first) + 1
                        separator = u', '
                        if count > 2:
                            separator = u'-'
                        temp_element = group[last_index]
                        temp_element[2] = first + separator + last
                        temp_element[10] = str(count)
                        temp_group.append(temp_element)
                    else:
                        temp_group.append(element)
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
                prev_ref_type = self.components_array[0][0][1]
                for group in self.components_array:
                    group_name = group[0][0]
                    ref_type = group[0][1]

                    # Empty rows between groups
                    add_empty_rows = True
                    if self.components_array.index(group) == 0:
                        # Before first group not needed
                        add_empty_rows = False
                    if self.empty_rows_everywhere == False \
                            and prev_ref_type == ref_type:
                        # Between elements of the same type not needed
                        add_empty_rows = False
                    if add_empty_rows == True:
                        for _ in range(self.empty_rows_after_group):
                            csv_writer.writerow(empty_row)
                    prev_ref_type = ref_type

                    if group_name != u'':
                        if len(group) == 1 and self.singular_group_name == True:
                            # Place group name with name of component
                            comp_values = self._get_final_values(group[0], True)
                            for value in comp_values:
                                value = self._get_unescaped_text(value)
                            csv_writer.writerow(comp_values)
                            continue
                        else:
                            # New group title
                            if self.gost_in_group_name == True:
                                group_names_with_gost, components = self._get_group_names_with_gost(group)
                                # Write group names with GOST
                                for group_name_with_gost in group_names_with_gost:
                                    group_name_with_gost = self._get_unescaped_text(group_name_with_gost)
                                    csv_writer.writerow([u'', group_name_with_gost, u'', u''])
                                # Write to table prepared components
                                for comp in components:
                                    # Write component into list
                                    comp_values = self._get_final_values(comp)
                                    for value in comp_values:
                                        value = self._get_unescaped_text(value)
                                    csv_writer.writerow(comp_values)
                                continue
                            else:
                                csv_writer.writerow([u'', group_name, u'', u''])

                    for comp in group:
                        # Write component into list
                        comp_values = self._get_final_values(comp)
                        for value in comp_values:
                            value = self._get_unescaped_text(value)
                        csv_writer.writerow(comp_values)
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
        prev_ref_type = self.components_array[0][0][1]
        for group in self.components_array:
            group_name = group[0][0]
            ref_type = group[0][1]

            # Empty rows between groups
            add_empty_rows = True
            if self.components_array.index(group) == 0:
                # Before first group not needed
                add_empty_rows = False
            if self.empty_rows_everywhere == False \
                    and prev_ref_type == ref_type:
                # Between elements of the same type not needed
                add_empty_rows = False
            if add_empty_rows == True:
                for _ in range(self.empty_rows_after_group):
                    if self.prohibit_empty_rows_on_top == True and \
                            self._cur_line == 1:
                        break
                    self._next_line()
            prev_ref_type = ref_type

            if group_name != u'':
                if len(group) == 1 and self.singular_group_name == True:
                    # Place group name with name of component
                    self._set_line(group[0], with_group=True)
                    self._next_line()
                    continue
                else:
                    # New group title
                    if self.gost_in_group_name == True:
                        group_names_with_gost, components = self._get_group_names_with_gost(group)
                        # If name of group at bottom of page - move it to next page
                        if self.prohibit_group_name_at_bottom == True \
                                and (self._cur_line + len(group_names_with_gost)) >= self._lines_on_page:
                            while self._cur_line != 1:
                                self._next_line()
                        # Write group names with GOST
                        for group_name_with_gost in group_names_with_gost:
                            self._replace_text(
                                self._cur_page,
                                u'#2:%d' % self._cur_line,
                                group_name_with_gost,
                                center=self.center_group_name,
                                underline=self.underline_group_name
                                )
                            self._next_line()
                        # Write to table prepared components
                        for comp in components:
                            # Write component into list
                            self._set_line(comp)
                            self._next_line()
                        continue

                    else:
                        # If name of group at bottom of page - move it to next page
                        if self.prohibit_group_name_at_bottom == True \
                                and self._cur_line == self._lines_on_page:
                            self._next_line()
                        self._replace_text(
                            self._cur_page,
                            u'#2:%d' % self._cur_line,
                            group_name,
                            center=self.center_group_name,
                            underline=self.underline_group_name
                            )
                        self._next_line()

            for comp in group:
                # Write component into list
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

                if self.file_format == u'.odt':
                    # Needed for getting styles in _replace_text_in_table
                    self.complist = page

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
                        self._replace_text(page, u'#6:1', first_usage.group(1).strip())

            # Other pages - small stamp
            else:
                self._replace_text(page, u'#5:10', self.decimal_num)
                self._replace_text(page, u'#5:11', str(index + 1))

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
        creation_time_str = u'{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{min:02d}:{sec:02d}'.format(
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

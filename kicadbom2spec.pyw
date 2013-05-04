#!/usr/bin/env python
# -*-    Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4    -*-
### BEGIN LICENSE
# Copyright (C) 2012 Baranovskiy Konstantin (baranovskiykonstantin@gmail.com)
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
import sys
import codecs
import locale
import argparse
import odf.opendocument
from copy import deepcopy
from odf.text import P
from odf.table import *
from odf.style import Style, ParagraphProperties, TextProperties
from Tkinter import *
import tkFileDialog as fileDialog
import tkMessageBox as message

# Set default encoding
reload(sys)
sys.setdefaultencoding('utf-8')

class Specification():
    '''
        Generating specification from BOM, fill stamp using
        KiCAD Schematic and save it to *.ods file.
    '''

    def __init__(self):

        # Load the pattern
        self.pattern = odf.opendocument.load(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pattern.ods'))
        self.firstPagePattern = None
        self.otherPagesPattern = None
        for sheet in self.pattern.spreadsheet.getElementsByType(Table):
            # Pattern for first page
            if sheet.getAttribute('name') == 'First':
                self.firstPagePattern = sheet
            # Pattern for other pages
            elif sheet.getAttribute('name') == 'Other':
                self.otherPagesPattern = sheet

        # Create specification file object
        self.specification = odf.opendocument.OpenDocumentSpreadsheet()

        # Copy all parameters from pattern to the specification
        for meta in self.pattern.meta.childNodes[:]:
            self.specification.meta.addElement(meta)

        for font in self.pattern.fontfacedecls.childNodes[:]:
            self.specification.fontfacedecls.addElement(font)

        for style in self.pattern.styles.childNodes[:]:
            self.specification.styles.addElement(style)

        for masterstyle in self.pattern.masterstyles.childNodes[:]:
            self.specification.masterstyles.addElement(masterstyle)

        for autostyle in self.pattern.automaticstyles.childNodes[:]:
            self.specification.automaticstyles.addElement(autostyle)

        for setting in self.pattern.settings.childNodes[:]:
            self.specification.settings.addElement(setting)

        # Current state of filling the specification
        self.curGroup   = ''
        self.curLine    = 1
        self.curPage    = 1
        self.curTable   = self.firstPagePattern

        # Some variables for stamp filling
        self.devel  = ''
        self.check  = ''
        self.approv = ''
        self.decNum = ''
        self.title  = ''
        self.comp   = ''

    def replaceText(self, table, label, text, group=False):
        '''
            Replace 'label' (like #1:1) to 'text' in 'table'.
            If 'group' is set to 'True' will be used special formatting.
        '''

        rows = table.getElementsByType(TableRow)
        for row in rows:
            cells = row.getElementsByType(TableCell)
            for cell in cells:
                for p in cell.getElementsByType(P):
                    for p_data in p.childNodes:
                        if p_data.tagName == 'Text':
                            if p_data.data == label:
                                p_data.data = text.decode('string_escape')
                                if group == True:
                                    # Set center align and underline for ghoup name
                                    curStyleName = cell.getAttribute('stylename')
                                    groupStyle = self.specification.getStyleByName(curStyleName +'g')
                                    if groupStyle == None:
                                        groupStyle = deepcopy(self.specification.getStyleByName(curStyleName))
                                        groupStyle.setAttribute('name', curStyleName +'g')
                                        groupStyle.addElement(ParagraphProperties(textalign='center'))
                                        groupStyle.addElement(TextProperties(textunderlinetype='single',
                                                                              textunderlinestyle='solid',))
                                        self.specification.styles.addElement(groupStyle)
                                    cell.setAttribute('stylename', curStyleName +'g')
                                return

    def clearTable(self, table):
        '''
            Clear 'table' of labels
        '''

        rows = table.getElementsByType(TableRow)
        for row in rows:
            cells = row.getElementsByType(TableCell)
            for cell in cells:
                for p in cell.getElementsByType(P):
                    for p_data in p.childNodes:
                        if p_data.tagName == 'Text':
                            if re.search(r'#\d+:\d+', p_data.data) != None:
                                p_data.data = ''

    def nextLine(self):
        '''
            Moving to next line.
            If table is full, save it in specification and create a new one
        '''

        # Increment line counter
        self.curLine += 1

        # First page of specification has 29 lines, other pages has 32 lines
        if (self.curPage == 1 and self.curLine > 29) or (self.curPage > 1 and self.curLine > 32):
            # Table is full
            self.curTable.setAttribute('name', u'стр. %d' % self.curPage)
            self.specification.spreadsheet.addElement(self.curTable)

            self.curTable = self.otherPagesPattern
            self.curPage += 1
            self.curLine = 1

    def setLine(self, element):
        '''
            Fill the specification's line using element's fields.
        '''

        # Reference
        ref = ''
        if int(element[8]) > 1:
            # Reference number: '5, 6'; '25...28' etc.
            ref = re.search(r'(\d+)(\.*|,\s?)(\d+)', element[1]).groups()
            # Reference: 'VD1, 2'; 'C8...C11' etc.
            ref = (element[0] + '%s%s' + element[0] + '%s') % ref
        else:
            # Reference: 'R5'; 'VT13' etc.
            ref = element[0] + element[1]
        self.replaceText(self.curTable, '#1:%d' % self.curLine, ref)
        # Value
        val = element[2] + element[3]
        if element[0] == 'C' and element[3][-1:] != u'Ф':
            if element[3].isdigit():
                val += u'п'
            val += u'Ф'
        elif element[0] == 'L' and element[3][-2:] != u'Гн':
            val += u'Гн'
        elif element[0] == 'R' and element[3][-2:] != u'Ом':
            val += u'Ом'
        val += element[4] + element[5] + element[6]
        self.replaceText(self.curTable, '#2:%d' % self.curLine, val)
        # Count
        self.replaceText(self.curTable, '#3:%d' % self.curLine, element[8])
        # Coment
        self.replaceText(self.curTable, '#4:%d' % self.curLine, element[7])

    def compareRef(self, ref):
        '''
            Get integer value of reference (type & number) fo comparison in sort() function
        '''

        refVal = 0
        matches = re.search(r'^([A-Z]+)\d+', ref[0] + ref[1])
        if matches != None:
            for ch in range(len(matches.group(1))):
                # Ref begins maximum of two letters, the first is multiplied by 10, the second by 1
                refVal += ord(matches.group(1)[ch]) * 10 / (10 ** ch)
        matches = re.search(r'^[A-Z]+(\d+)', ref[0] + ref[1])
        if matches != None:
            refVal += int(matches.group(1))
        return refVal

    def loadBOM(self, bomFileName):
        '''
            Open BOM file and load all elements to specification.
        '''

        # Open BOM file
        bomFile = codecs.open(bomFileName, encoding='utf-8')

        # First line not needed
        bomFile.readline()

        # Handle all lines
        bomArray = []
        for bomLine in bomFile:
            line = bomLine[0:-1].split('\t')
            bomArray.append([line[2],                                       # group
                             re.search(r'[A-Z]+', line[0]).group(),         # reference type
                             re.search(r'[0-9]+', line[0]).group(),         # reference number
                             line[3],                                       # mark
                             line[1],                                       # value
                             line[4],                                       # accuracy
                             line[5],                                       # type
                             line[6],                                       # GOST
                             line[7],                                       # comment
                             '1'])                                          # count of elements (default 1)
        bomArray.sort()

        # Split elements into groups
        tempName = bomArray[0][0]
        tempArray = None
        lineArray = None
        for array in bomArray:
            if tempName == array[0]:
                if tempArray == None:
                    tempArray = [array[1:],]
                else:
                    tempArray.append(array[1:])
            else:
                if lineArray == None:
                    lineArray = [[tempName, tempArray],]
                else:
                    lineArray.append([tempName, tempArray])
                tempArray = [array[1:],]
                tempName = array[0]
            if bomArray.index(array) == len(bomArray) - 1:
                if lineArray == None:
                    lineArray = [[tempName, tempArray],]
                else:
                    lineArray.append([tempName, tempArray])

        # Combining the identical elements in one line
        for group in lineArray:
            first = ''
            last = ''
            prev = []
            firstIndex = 0
            lastIndex = 0

            group[1].sort(key=self.compareRef)
            for element in group[1]:
                if group[1].index(element) == 0:
                    # first element
                    first = last = element[1]
                    prev = element[:]
                    continue

                if element[0] == prev[0] and int(element[1]) - 1 == int(prev[1]) and element[2:] == prev[2:]:
                    # equal elements
                    last = element[1]
                    lastIndex = group[1].index(element)
                else:
                    # different elements
                    if int(last) - int(first) > 0:
                        # several identical elements
                        count = int(last) - int(first) + 1
                        separator = ''
                        if count > 2:
                            separator = '...'
                        else:
                            separator = ', '
                        group[1][lastIndex][1] = first + separator + last
                        group[1][lastIndex][8] = str(count)
                        del group[1][firstIndex:lastIndex]
                        first = last = element[1]
                        firstIndex = lastIndex = group[1].index(element)
                    else:
                        # next different element
                        first = last = element[1]
                        firstIndex = lastIndex = group[1].index(element)

                if group[1].index(element) == len(group[1]) - 1:
                    # last element
                    if int(last) - int(first) > 0:
                        # several identical elements
                        count = int(last) - int(first) + 1
                        separator = ''
                        if count > 2:
                            separator = '...'
                        else:
                            separator = ', '
                        group[1][lastIndex][1] = first + separator + last
                        group[1][lastIndex][8] = str(count)
                        del group[1][firstIndex:lastIndex]
                prev = element[:]

        # Fill the specification
        for group in lineArray:
            if self.curGroup != group[0]:
                # New group title
                self.curGroup = group[0]

                if (self.curPage == 1 and self.curLine > 26) or (self.curPage > 1 and self.curLine > 29):
                    # If name of group at bottom of table without elements, go to beginning of a new
                    while self.curLine != 1:
                        self.nextLine()
                else:
                    self.nextLine() # Skip one line

                self.replaceText(self.curTable, '#2:%d' % self.curLine, group[0], group=True)
                self.nextLine() # Skip one line
                self.nextLine() # Moving to next line

            # Put all group lines to the table
            if group[0] == '':
                # Elements without group
                prev = None
                for element in group[1]:
                    if prev == None:
                        prev = element[0]
                        self.setLine(element)
                        self.nextLine()
                        continue
                    if element[0] != prev:
                        # Elements with different types separated by one empty line
                        self.nextLine()
                        prev = element[0]
                    self.setLine(element)
                    self.nextLine()

            else:
                # Elements with group
                for element in group[1]:
                    self.setLine(element)
                    self.nextLine()

        if self.curLine != 1:
            # Current table not empty - save it
            self.curTable.setAttribute('name', u'стр. %d' % self.curPage)
            self.specification.spreadsheet.addElement(self.curTable)

    def loadSchematic(self, schFileName):
        '''
            Open KiCAD Schematic file and load all fields
            for specification's stamp.
        '''

        # Open schematic file
        schFile = codecs.open(schFileName, encoding='utf-8')

        # Get stamp field's data from schematic file
        for line in schFile:
            if line.startswith('$EndDescr'):
                break

            elif line.startswith('Title'):
                self.title = re.search(r'\"(.*)\"', line).group(1)

            elif line.startswith('Comp'):
                self.comp = re.search(r'\"(.*)\"', line).group(1)

            elif line.startswith('Comment1'):
                self.decNum = re.search(r'\"(.*)\"', line).group(1)
                if self.decNum[-2:-1] == u'Э' and self.decNum[-1:].isdigit():
                    self.decNum = self.decNum[:-2] + u'П' + self.decNum[-2:]

            elif line.startswith('Comment2'):
                self.devel = re.search(r'\"(.*)\"', line).group(1)

            elif line.startswith('Comment3'):
                self.check = re.search(r'\"(.*)\"', line).group(1)

            elif line.startswith('Comment4'):
                self.approv = re.search(r'\"(.*)\"', line).group(1)

    def saveSpecification(self, specFileName):
        '''
            Save created specification to the file.
        '''

        # Fill stamp fields on each page
        for table in self.specification.spreadsheet.getElementsByType(Table):
            pgNum = re.search(r'\d+', table.getAttribute('name')).group()

            # First page - big stamp
            if pgNum == '1':
                pgCnt = len(self.specification.spreadsheet.getElementsByType(Table))
                if pgCnt == 1:
                    pgCnt = ''
                else:
                    pgCnt = str(pgCnt)

                self.replaceText(table, '#5:1', self.devel)
                self.replaceText(table, '#5:2', self.check)
                self.replaceText(table, '#5:3', self.approv)
                self.replaceText(table, '#5:4', self.decNum)
                self.replaceText(table, '#5:5', self.title)
                self.replaceText(table, '#5:6', pgNum)
                self.replaceText(table, '#5:7', pgCnt)
                self.replaceText(table, '#5:8', self.comp)

            # Other pages - smal stamp
            else:
                self.replaceText(table, '#5:1', self.decNum)
                self.replaceText(table, '#5:2', pgNum)

        # Clear tables from labels
        for table in self.specification.spreadsheet.getElementsByType(Table):
            self.clearTable(table)

        # Save specification file
        self.specification.save(specFileName)

class Window(Frame):
    '''
        Graphical user interface for kicadbom2spes
    '''

    def __init__(self, parent, args):
        Frame.__init__(self, parent)

        self.mainWindow = parent
        self.args = args

        # title of main window
        self.mainWindow.title('kicadbom2spes')

        # vars for store text fields content
        self.bomFileName = StringVar()
        self.schFileName = StringVar()
        self.specFileName = StringVar()

        # labels
        self.bomLabel = Label(self.mainWindow, text=u'Файл перечня элементов (BOM):')
        self.bomLabel.grid(row=1, column=1, sticky='w')
        self.schLabel = Label(self.mainWindow, text=u'Файл схемы (KiCAD Schematic):')
        self.schLabel.grid(row=3, column=1, sticky='w')
        self.specLabel = Label(self.mainWindow, text=u'Файл спецификации:')
        self.specLabel.grid(row=5, column=1, sticky='w')

        # text fields
        self.bomEntry = Entry(self.mainWindow, textvariable=self.bomFileName, width=50)
        self.bomEntry.grid(row=2, column=1, sticky='ew')
        self.schEntry = Entry(self.mainWindow, textvariable=self.schFileName, width=50)
        self.schEntry.grid(row=4, column=1, sticky='ew')
        self.specEntry = Entry(self.mainWindow, textvariable=self.specFileName, width=50)
        self.specEntry.grid(row=6, column=1, sticky='ew')

        # buttons
        self.bomButton = Button(self.mainWindow, text=u'Открыть...')
        self.bomButton.grid(row=2, column=2, sticky='ew')
        self.bomButton.bind('<ButtonRelease-1>', self.bomOpen)
        self.schButton = Button(self.mainWindow, text=u'Открыть...')
        self.schButton.bind('<ButtonRelease-1>', self.schOpen)
        self.schButton.grid(row=4, column=2, sticky='ew')
        self.specButton = Button(self.mainWindow, text=u'Сохранить как...')
        self.specButton.bind('<ButtonRelease-1>', self.specSave)
        self.specButton.grid(row=6, column=2, sticky='ew')
        self.makeButton = Button(self.mainWindow, text=u'Создать спецификацию')
        self.makeButton.bind('<ButtonRelease-1>', self.specMake)
        self.makeButton.grid(row=7, column=1, columnspan=2, sticky='ew')

        # Get default encoding
        prefEncoding = locale.getpreferredencoding()

        # BOM file name from args
        if self.args.bom != None and os.path.exists(self.args.bom):
            self.bomFileName.set(os.path.abspath(self.args.bom.decode(prefEncoding)))

        # KiCAD Schematic file name from args
        if self.args.schematic != None and os.path.exists(self.args.schematic):
            self.schFileName.set(os.path.abspath(self.args.schematic.decode(prefEncoding)))

        # Specification file name from args
        if self.args.output != None:
            if os.path.dirname(self.args.output) != '':
                if os.path.exists(os.path.dirname(self.args.output)):
                    self.specFileName.set(os.path.abspath(self.args.output.decode(prefEncoding)))
            else:
                self.specFileName.set(os.path.abspath(self.args.output.decode(prefEncoding)))


    def bomOpen(self, event):
        '''
            Get name of BOM file from dialog
        '''

        fileTypes = [(u'BOM файлы', '*.csv'), (u'Все файлы', '*')]
        fileName = fileDialog.askopenfilename(parent=self,
                                              filetypes=fileTypes,
                                              initialdir=os.path.dirname(self.bomFileName.get()),
                                              initialfile=os.path.basename(self.bomFileName.get()))

        if fileName != '' and fileName != ():
            self.bomFileName.set(fileName)
            sch = os.path.splitext(self.bomFileName.get())[0] + '.sch'
            spec = os.path.splitext(self.bomFileName.get())[0] + '.ods'
            if os.path.exists(sch) and self.schFileName.get() == '':
                self.schFileName.set(sch)
            if self.specFileName.get() == '':
                self.specFileName.set(spec)

    def schOpen(self, event):
        '''
            Get name of KiCAD Schematic file from dialog
        '''

        fileTypes = [('KiCAD Schematic', '*.sch'), (u'Все файлы', '*')]
        fileName = fileDialog.askopenfilename(parent=self,
                                              filetypes=fileTypes,
                                              initialdir=os.path.dirname(self.schFileName.get()),
                                              initialfile=os.path.basename(self.schFileName.get()))

        if fileName != '' and fileName != ():
            self.schFileName.set(fileName)

    def specSave(self, event):
        '''
            Get name of specification file from dialog
        '''

        fileTypes = [(u'Файлы таблиц', '*.ods'), (u'Все файлы', '*')]
        fileName = fileDialog.asksaveasfilename(parent=self,
                                                filetypes=fileTypes,
                                                initialdir=os.path.dirname(self.specFileName.get()),
                                                initialfile=os.path.basename(self.specFileName.get()))

        if str(fileName) != '':
            self.specFileName.set(fileName)

    def specMake(self, event):
        '''
            Generate specification and write to file
        '''

        if not os.path.exists(self.bomFileName.get()):
            message.showerror(u'Ошибка!', u'Файл перечня элементов (BOM) не указан или отсутствует.')
            return

        if not os.path.exists(os.path.dirname(self.specFileName.get())):
            message.showerror(u'Ошибка!', u'Неверно указан путь к файлу спецификации.')
            return

        if os.path.splitext(self.specFileName.get())[1] != '.ods':
            message.showerror(u'Ошибка!', u'Неверно указано расширение файла спецификации.\nДолжно быть ".ods"')
            return

        spec = Specification()
        spec.loadBOM(self.bomFileName.get())
        if os.path.exists(self.schFileName.get()):
            spec.loadSchematic(self.schFileName.get())
        elif self.schFileName.get() != '':
            message.showwarning(u'Внимание!', u'Файл схемы указан, но не найден.\nВ штампы спецификации будут занесены только номера страниц.')

        spec.saveSpecification(self.specFileName.get())

        message.showinfo(u'Готово!', u'Файл спецификации успешно создан.')


def main():
    '''
        Main function called at start
    '''

    # Parsing of command-line arguments
    parser = argparse.ArgumentParser(description=(u'Скрипт создает файл спецификации оформленный в соответствии с ЕСКД из перечня элементов (BOM).\n'))
    parser.add_argument('-b', '--bom',      type=str,           help=u'полное или относительное имя BOM файла')
    parser.add_argument('-c', '--console',  action='store_true',help=u'работа в режиме командной строки')
    parser.add_argument('-o', '--output',   type=str,           help=u'полное или относительное имя файла спецификации')
    parser.add_argument('-s', '--schematic',type=str,           help=u'полное или относительное имя файла схемы в формате KiCAD')
    parser.add_argument('-v', '--verbose',  action='store_true',help=u'вывод информации о ходе выполнения')

    args = parser.parse_args()

    # working in console mode
    if args.console == True:

        if args.bom == None:
            print >> sys.stderr, u'Для создания спецификации необходимо указать файл перечня элементов (BOM).'
            return
        else:
            bomFileName = os.path.abspath(args.bom)
            if not os.path.exists(bomFileName):
                print >> sys.stderr, u'Указанный файл перечня элементов не найден.'
                return

            spec = Specification()
            spec.loadBOM(bomFileName)
            if args.verbose == True:
                print u'Файл перечня элементов загружен.'

            if args.schematic == None:
                schFileName = os.path.splitext(bomFileName)[0] + '.sch'
                if os.path.exists(schFileName):
                    spec.loadSchematic(schFileName)
                    if args.verbose == True:
                        print u'Найден файл схемы. Значения полей основной надписи будут скопированы в спецификацию.'
            elif os.path.exists(args.schematic):
                spec.loadSchematic(os.path.abspath(args.schematic))
                if args.verbose == True:
                    print u'Значения полей основной надписи скопированы из схемы в спецификацию.'
            else:
                if args.verbose == True:
                    print u'Файл схемы не найден. В основной надписи спецификации будут указаны только намера страниц.'

            specFileName = ''
            if args.output == None:
                specFileName = os.path.splitext(bomFileName)[0] + '.ods'
            elif os.path.dirname(args.output) != '':
                if os.path.exists(os.path.dirname(args.output)):
                    specFileName = os.path.abspath(args.output)
                else:
                    print >> sys.stderr, u'Неверно указан путь к файлу спецификации.'
                    return
            else:
                specFileName = os.path.abspath(args.output)

            if os.path.splitext(specFileName)[1] != '.ods':
                specFileName += '.ods'
            spec.saveSpecification(specFileName)
            if args.verbose == True:
                print u'Файл спецификации успешно создан.'

    # working in GUI mode
    else:

        # Create and show main window
        root = Tk()
        root.resizable(width=False, height=False)
        window = Window(root, args)
        root.mainloop()

if __name__ == '__main__':
    main()

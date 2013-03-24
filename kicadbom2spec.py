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

# Set coding for console
reload(sys)
sys.setdefaultencoding('utf-8')

# Get default encoding
prefEncoding = locale.getpreferredencoding()

# Parsing of command-line arguments
parser = argparse.ArgumentParser(description=(u"Скрипт создает файл спецификации оформленный в соответствии с ЕСКД из перечня элементов (BOM).\n").encode('utf-8'))
parser.add_argument("bom", type=str, help=u"полное или относительное имя BOM файла".encode('utf-8'))
parser.add_argument("-o", "--output", type=str, help=u"имя файла спецификации".encode('utf-8'))
parser.add_argument("-s", "--schematic", type=str, help=u"имя файла схемы в формате KiCAD".encode('utf-8'))
parser.add_argument("-v", "--verbose", action="store_true", help=u"вывод информации о ходе выполнения".encode('utf-8'))

args = parser.parse_args()

# Create specification file object
specification = odf.opendocument.OpenDocumentSpreadsheet()

if args.verbose == True:
    print u"\nСоздан объект файла спецификации"

# Load the pattern
pattern = odf.opendocument.load("pattern.ods")
firstPg = None
otherPgs = None
for sheet in pattern.spreadsheet.getElementsByType(Table):
    # Pattern for first page
    if sheet.getAttribute("name") == "First":
        firstPg = sheet
    # Pattern for other pages
    elif sheet.getAttribute("name") == "Other":
        otherPgs = sheet

if args.verbose == True:
    print u"Загружены шаблоны спецификации для первой и последующих страниц"

# Copy all parameters from pattern to the specification
for meta in pattern.meta.childNodes[:]:
    specification.meta.addElement(meta)

for font in pattern.fontfacedecls.childNodes[:]:
    specification.fontfacedecls.addElement(font)

for style in pattern.styles.childNodes[:]:
    specification.styles.addElement(style)

for masterstyle in pattern.masterstyles.childNodes[:]:
    specification.masterstyles.addElement(masterstyle)

for autostyle in pattern.automaticstyles.childNodes[:]:
    specification.automaticstyles.addElement(autostyle)

for setting in pattern.settings.childNodes[:]:
    specification.settings.addElement(setting)

if args.verbose == True:
    print u"Скопированы параметры файла спецификации из шаблона"

# Global variables
curGroup = ""
curLine = 1
curPage = 1
curTable = firstPg

# Replace "label" (like #1:1) to "text" in "table".
def replaceText(table, label, text, group=False):
    rows = table.getElementsByType(TableRow)
    for row in rows:
        cells = row.getElementsByType(TableCell)
        for cell in cells:
            for p in cell.getElementsByType(P):
                for p_data in p.childNodes:
                    if p_data.tagName == 'Text':
                        if p_data.data == label:
                            p_data.data = text.decode("string_escape")
                            if group == True:
                                # Set center align and underline for ghoup name
                                curStyleName = cell.getAttribute("stylename")
                                groupStyle = specification.getStyleByName(curStyleName +"g")
                                if groupStyle == None:
                                    groupStyle = deepcopy(specification.getStyleByName(curStyleName))
                                    groupStyle.setAttribute("name", curStyleName +"g")
                                    groupStyle.addElement(ParagraphProperties(textalign="center"))
                                    groupStyle.addElement(TextProperties(textunderlinetype="single",
                                                                          textunderlinestyle="solid",))
                                    specification.styles.addElement(groupStyle)
                                cell.setAttribute("stylename", curStyleName +"g")
                            return

# Clear "table" of labels
def clearTable(table):
    rows = table.getElementsByType(TableRow)
    for row in rows:
        cells = row.getElementsByType(TableCell)
        for cell in cells:
            for p in cell.getElementsByType(P):
                for p_data in p.childNodes:
                    if p_data.tagName == 'Text':
                        if re.search(r"#\d+:\d+", p_data.data) != None:
                            p_data.data = ""

# Moving to next line. If table is full, save it in specification and create a new one
def nextLine():
    global specification, curTable, curPage, curLine

    # Increment line counter
    curLine += 1

    if (curPage == 1 and curLine > 29) or (curPage > 1 and curLine > 32):
        # Table is full
#        clearTable(curTable)
        curTable.setAttribute("name", u"стр. %d" % curPage)
        specification.spreadsheet.addElement(curTable)

        if args.verbose == True:
            print u"cтраница %d заполнена" % curPage

        curTable = otherPgs
        curPage += 1
        curLine = 1

# Fill the line using element's fields
def setLine(element):
    # Reference
    ref = ""
    if int(element[8]) > 1:
        ref = re.search(r"(\d+)(\.*|,\s?)(\d+)", element[1]).groups()
        ref = (element[0] + "%s%s" + element[0] + "%s") % ref
    else:
        ref = element[0] + element[1]
    replaceText(curTable, "#1:%d" % curLine, ref)
    # Value
    val = element[2] + element[3]
    if element[0] == "C" and element[3][-1:] != u"Ф":
        if element[3].isdigit():
            val += u"п"
        val += u"Ф"
    elif element[0] == "L" and element[3][-2:] != u"Гн":
        val += u"Гн"
    elif element[0] == "R" and element[3][-2:] != u"Ом":
        val += u"Ом"
    val += element[4] + element[5] + element[6]
    replaceText(curTable, "#2:%d" % curLine, val)
    # Count
    replaceText(curTable, "#3:%d" % curLine, element[8])
    # Coment
    replaceText(curTable, "#4:%d" % curLine, element[7])

# Get integer value of reference fo comparison in sort() function
def compareRef(ref):
    refVal = 0
    matches = re.search(r"^([A-Z]+)\d+", ref[0] + ref[1])
    if matches != None:
        for ch in range(len(matches.group(1))):
            # Ref begins maximum of two letters, the first is multiplied by 10, the second by 1
            refVal += ord(matches.group(1)[ch]) * 10 / (10 ** ch)
    matches = re.search(r"^[A-Z]+(\d+)", ref[0] + ref[1])
    if matches != None:
        refVal += int(matches.group(1))
    return refVal

# Open bom file
if os.path.exists(args.bom):
    bomAbspath = os.path.abspath(args.bom)
    bomFile = codecs.open(bomAbspath, encoding='utf-8')
else:
    print u"Файл перечня элементов (BOM) \"%s\" не найден!" % args.bom.decode(prefEncoding)
    exit(1)

if args.verbose == True:
    print u"Открыт файл перечня элементов (BOM)"

# First line not needed
bomFile.readline()

# Handle all lines
bomArray = []
for bomLine in bomFile:
    line = bomLine[0:-1].split("\t")
    bomArray.append([line[2],                                       # group
                     re.search(r"[A-Z]+", line[0]).group(),         # reference type
                     re.search(r"[0-9]+", line[0]).group(),         # reference number
                     line[3],                                       # mark
                     line[1],                                       # value
                     line[4],                                       # accuracy
                     line[5],                                       # type
                     line[6],                                       # GOST
                     line[7],                                       # comment
                     "1"])                                          # count of elements (default 1)
bomArray.sort()

if args.verbose == True:
    print u"Из BOM файла получены все элементы и их параметры"

# Split elements into groups
tempName = ""
lineArray = None
tempArray = None
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

if args.verbose == True:
    print u"Все элементы разбиты на группы:"
    for ln in lineArray:
        if ln[0] == "":
            print u"*без группы* %d шт." % len(ln[1])
        else:
            print u"%s %d шт." % (ln[0], len(ln[1]))

# Combining the identical elements in one line
for group in lineArray:
    first = ""
    last = ""
    prev = []
    firstIndex = 0
    lastIndex = 0
    group[1].sort(key=compareRef)
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
                separator = ""
                if count > 2:
                    separator = "..."
                else:
                    separator = ", "
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
                separator = ""
                if count > 2:
                    separator = "..."
                else:
                    separator = ", "
                group[1][lastIndex][1] = first + separator + last
                group[1][lastIndex][8] = str(count)
                del group[1][firstIndex:lastIndex]
                #first = last = element[1]
                #firstIndex = lastIndex = group[1].index(element)
        prev = element[:]

if args.verbose == True:
    print u"Одинаковые элементы, идущие подряд, сгруппированы в одну строку"
    print u"\nЗаполнение спецификации:"

# Fill the specification
for group in lineArray:
    if curGroup != group[0]:
        # New group title
        curGroup = group[0]

        if (curPage == 1 and curLine > 26) or (curPage > 1 and curLine > 29):
            # If name of group at bottom of table without elements, go to beginning of a new
            while curLine != 1:
                nextLine()
        else:
            nextLine() # Skip one line

        replaceText(curTable, "#2:%d" % curLine, group[0], group=True)
        nextLine() # Skip one line
        nextLine() # Moving to next line

    # Put all group lines to the table
    if group[0] == "":
        # Elements without group
        prev = None
        for element in group[1]:
            if prev == None:
                prev = element[0]
                setLine(element)
                nextLine()
                continue
            if element[0] != prev:
                nextLine()
                prev = element[0]
            setLine(element)
            nextLine()

    else:
        # Elements with group
        for element in group[1]:
            setLine(element)
            nextLine()

if curLine != 1:
    # Current table not empty - save it
    curTable.setAttribute("name", u"стр. %d" % curPage)
#    clearTable(curTable)
    specification.spreadsheet.addElement(curTable)

    if args.verbose == True:
        print u"cтраница %d заполнена" % curPage

if args.verbose == True:
    print u"Все элементы занесены в спецификацию"

# Some variables for stamp filling
schAbspath = ""
devel = ""
check = ""
approv = ""
decNum = ""
title = ""
comp = ""

# Get schematic file name
if args.schematic == None:
    # Name of schematic file same as BOM file name
    schAbspath = os.path.splitext(bomAbspath)[0] + ".sch"
else:
    # Name of schematic file are specified
    schAbspath = os.path.join(os.path.dirname(bomAbspath), args.schematic)

# Сheck whether a file exists
if os.path.exists(schAbspath):
    if args.verbose == True:
        print u"\nНайден файл схемы \"%s\"" % os.path.basename(schAbspath).decode(prefEncoding)
    # Open schematic file
    schFile = codecs.open(schAbspath, encoding='utf-8')
    if args.verbose == True:
        print u"Файл схемы открыт для чтения"
    # Get stamp data from schematic file
    for line in schFile:
        if line.startswith("$EndDescr"):
            if args.verbose == True:
                print u"Загружены значения полей основной надписи"
            break
        elif line.startswith("Title"):
            title = re.search(r'\"(.*)\"', line).group(1)
        elif line.startswith("Comp"):
            comp = re.search(r'\"(.*)\"', line).group(1)
        elif line.startswith("Comment1"):
            decNum = re.search(r'\"(.*)\"', line).group(1)
            if decNum[-2:-1] == u"Э" and decNum[-1:].isdigit():
                decNum = decNum[:-2] + u"П" + decNum[-2:]
        elif line.startswith("Comment2"):
            devel = re.search(r'\"(.*)\"', line).group(1)
        elif line.startswith("Comment3"):
            check = re.search(r'\"(.*)\"', line).group(1)
        elif line.startswith("Comment4"):
            approv = re.search(r'\"(.*)\"', line).group(1)
else:
    if args.verbose == True:
        print u"\nФайл схемы \"%s\" не найден" % os.path.basename(schAbspath).decode(prefEncoding)
        print u"В основных надписях будут указаны только номера страниц"

# Fill stamp fields on each page
for table in specification.spreadsheet.getElementsByType(Table):
    pgNum = re.search(r"\d+", table.getAttribute("name")).group()
    # First page - big stamp
    if pgNum == "1":
        pgCnt = len(specification.spreadsheet.getElementsByType(Table))
        if pgCnt == 1:
            pgCnt = ""
        else:
            pgCnt = str(pgCnt)

        replaceText(table, "#5:1", devel)
        replaceText(table, "#5:2", check)
        replaceText(table, "#5:3", approv)
        replaceText(table, "#5:4", decNum)
        replaceText(table, "#5:5", title)
        replaceText(table, "#5:6", pgNum)
        replaceText(table, "#5:7", pgCnt)
        replaceText(table, "#5:8", comp)

    # Other pages - smal stamp
    else:
        replaceText(table, "#5:1", decNum)
        replaceText(table, "#5:2", pgNum)
if args.verbose == True:
    print u"Основные надписи заполнены"


# Clear tables from labels
for table in specification.spreadsheet.getElementsByType(Table):
    clearTable(table)
if args.verbose == True:
    print u"Спецификация очищенна от воспомогательных меток"

# Save specification file
output_name = os.path.splitext(bomAbspath)[0] + ".ods"
if args.output != None:
    output_name = os.path.join(os.path.dirname(bomAbspath), args.output)

specification.save(output_name)

if args.verbose == True:
    print u"\nФайл спецификации \"%s\" сохранен в %s" % (os.path.basename(output_name).decode(prefEncoding), os.path.dirname(output_name).decode(prefEncoding))

EESchema Schematic File Version 2  date Суб 04 Май 2013 17:36:57
LIBS:sample
LIBS:sample-cache
EELAYER 24 0
EELAYER END
$Descr A4 8268 11693 portrait
encoding utf-8
Sheet 1 1
Title "Однокаскадный транзисторный усилитель"
Date "4 may 2013"
Rev ""
Comp "\"kicadbom2spec\""
Comment1 "АБВГ.0000.0001 Э3"
Comment2 "Иванова А.М."
Comment3 "Петров Н.Г."
Comment4 "Смирнов С.Н."
$EndDescr
$Comp
L NPN VT1
U 1 1 51850FE1
P 4700 4850
F 0 "VT1" H 4100 4600 138 0000 C CNN
F 1 "КТ3102А" H 4100 4350 138 0000 C CNN
F 2 "~" H 4700 4850 60  0000 C CNN
F 3 "~" H 4700 4850 60  0000 C CNN
F 4 "Транзисторы" H 4700 4850 60  0001 C CNN "Группа"
	1    4700 4850
	1    0    0    -1  
$EndComp
$Comp
L R R3
U 1 1 51850FF0
P 4800 6650
F 0 "R3" V 4900 6500 138 0000 R CNN
F 1 "68" V 4700 6500 138 0000 R CNN
F 2 "~" H 4800 6650 60  0000 C CNN
F 3 "~" H 4800 6650 60  0000 C CNN
F 4 "Резисторы" H 4800 6650 60  0001 C CNN "Группа"
F 5 "МЛТ-0,125-" H 4800 6650 60  0001 C CNN "Марка"
F 6 " ±5%" H 4800 6650 60  0001 C CNN "Класс точности"
F 7 "-В" H 4800 6650 60  0001 C CNN "Тип"
F 8 " ОЖ0.467.18" H 4800 6650 60  0001 C CNN "Стандарт"
	1    4800 6650
	0    -1   -1   0   
$EndComp
$Comp
L CPOL C3
U 1 1 518511B5
P 5800 6650
F 0 "C3" H 5550 6750 138 0000 R CNN
F 1 "10мк" H 5550 6500 138 0000 R CNN
F 2 "~" H 5800 6650 60  0000 C CNN
F 3 "~" H 5800 6650 60  0000 C CNN
F 4 "Конденсаторы" H 5800 6650 60  0001 C CNN "Группа"
F 5 "К50-35-63В-" H 5800 6650 60  0001 C CNN "Марка"
F 6 " ±10%" H 5800 6650 60  0001 C CNN "Класс точности"
F 7 " ОЖО.464.214 ТУ" H 5800 6650 60  0001 C CNN "Стандарт"
	1    5800 6650
	-1   0    0    -1  
$EndComp
$Comp
L R R2
U 1 1 518516D6
P 4800 3000
F 0 "R2" V 4900 2850 138 0000 R CNN
F 1 "1.5к" V 4700 2850 138 0000 R CNN
F 2 "~" H 4800 3000 60  0000 C CNN
F 3 "~" H 4800 3000 60  0000 C CNN
F 4 "Резисторы" H 4800 3000 60  0001 C CNN "Группа"
F 5 "МЛТ-0,125-" H 4800 3000 60  0001 C CNN "Марка"
F 6 " ±5%" H 4800 3000 60  0001 C CNN "Класс точности"
F 7 "-В" H 4800 3000 60  0001 C CNN "Тип"
F 8 " ОЖ0.467.18" H 4800 3000 60  0001 C CNN "Стандарт"
	1    4800 3000
	0    -1   -1   0   
$EndComp
$Comp
L R R1
U 1 1 518516FF
P 3950 4000
F 0 "R1" H 3950 4200 138 0000 C CNN
F 1 "330к" H 3950 3750 138 0000 C CNN
F 2 "~" H 3950 4000 60  0000 C CNN
F 3 "~" H 3950 4000 60  0000 C CNN
F 4 "Резисторы" H 3950 4000 60  0001 C CNN "Группа"
F 5 "МЛТ-0,125-" H 3950 4000 60  0001 C CNN "Марка"
F 6 " ±5%" H 3950 4000 60  0001 C CNN "Класс точности"
F 7 "-В" H 3950 4000 60  0001 C CNN "Тип"
F 8 " ОЖ0.467.18" H 3950 4000 60  0001 C CNN "Стандарт"
F 9 "270...360 кОм" H 3950 4000 60  0001 C CNN "Примечание"
	1    3950 4000
	1    0    0    -1  
$EndComp
$Comp
L CPOL C1
U 1 1 51851778
P 2650 4850
F 0 "C1" V 2350 4800 138 0000 C CNN
F 1 "4.7мк" V 3000 4800 138 0000 C CNN
F 2 "~" H 2650 4850 60  0000 C CNN
F 3 "~" H 2650 4850 60  0000 C CNN
F 4 "Конденсаторы" H 2650 4850 60  0001 C CNN "Группа"
F 5 "К50-35-63В-" H 2650 4850 60  0001 C CNN "Марка"
F 6 " ±10%" H 2650 4850 60  0001 C CNN "Класс точности"
F 7 " ОЖО.464.214 ТУ" H 2650 4850 60  0001 C CNN "Стандарт"
	1    2650 4850
	0    -1   1    0   
$EndComp
$Comp
L C C2
U 1 1 518517EC
P 5700 4000
F 0 "C2" V 6000 4000 138 0000 C CNN
F 1 "1мк" V 5350 3950 138 0000 C CNN
F 2 "~" H 5700 4000 60  0000 C CNN
F 3 "~" H 5700 4000 60  0000 C CNN
F 4 "Конденсаторы" H 5700 4000 60  0001 C CNN "Группа"
F 5 "К73-17-1б-Н90-" H 5700 4000 60  0001 C CNN "Марка"
F 6 " ±10%" H 5700 4000 60  0001 C CNN "Класс точности"
F 7 " ОЖ0.461.104ТУ" H 5700 4000 60  0001 C CNN "Стандарт"
	1    5700 4000
	0    -1   -1   0   
$EndComp
Text GLabel 2000 7650 0    138  Input ~ 0
Общ.
Text GLabel 7000 7650 2    138  Input ~ 0
Общ.
Text GLabel 2000 4850 0    138  Input ~ 0
Вход
Text GLabel 2000 1950 0    138  Input ~ 0
+9 В
Text GLabel 6800 4000 2    138  Output ~ 0
Общ.
Wire Wire Line
	6800 4000 5950 4000
Wire Wire Line
	5500 4000 4800 4000
Wire Wire Line
	4800 4000 4350 4000
Wire Wire Line
	4800 3400 4800 4000
Wire Wire Line
	4800 4000 4800 4550
Connection ~ 4800 4000
Wire Wire Line
	4800 2600 4800 1950
Wire Wire Line
	4800 1950 2000 1950
Wire Wire Line
	4350 4850 3350 4850
Wire Wire Line
	3350 4850 2900 4850
Wire Wire Line
	3550 4000 3350 4000
Wire Wire Line
	3350 4000 3350 4850
Connection ~ 3350 4850
Wire Wire Line
	2450 4850 2000 4850
Wire Wire Line
	4800 5150 4800 5750
Wire Wire Line
	4800 5750 4800 6250
Wire Wire Line
	2000 7650 4800 7650
Wire Wire Line
	4800 7650 5800 7650
Wire Wire Line
	5800 7650 7000 7650
Wire Wire Line
	5800 6900 5800 7650
Connection ~ 5800 7650
Wire Wire Line
	4800 7050 4800 7650
Connection ~ 4800 7650
Wire Wire Line
	5800 6450 5800 5750
Wire Wire Line
	5800 5750 4800 5750
Connection ~ 4800 5750
$EndSCHEMATC

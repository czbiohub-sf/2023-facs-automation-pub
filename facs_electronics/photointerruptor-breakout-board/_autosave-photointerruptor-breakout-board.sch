EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title "5-0007 FACS Photointerruptor Breakout Board"
Date "2021-10-19"
Rev "1"
Comp "Chan Zuckerberg Biohub"
Comment1 "Bioengineering Platform"
Comment2 "Emily Huynh"
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L photointerruptor_lib:AEDR-8300 U1
U 1 1 6187EB9F
P 1810 3035
F 0 "U1" H 1815 2685 50  0000 C CNN
F 1 "AEDR-8300" H 1810 2620 50  0000 C CNN
F 2 "photointerruptor_lib:Broadcom_DFN-6_2x2mm_P0.65mm" H 1810 2835 50  0001 C CNN
F 3 "http://www.everlight.com/file/ProductFile/ITR8307.pdf" H 1810 3135 50  0001 C CNN
	1    1810 3035
	1    0    0    -1  
$EndComp
NoConn ~ 1760 2785
$Comp
L power:GND #PWR01
U 1 1 61880642
P 1445 3135
F 0 "#PWR01" H 1445 2885 50  0001 C CNN
F 1 "GND" H 1450 2962 50  0000 C CNN
F 2 "" H 1445 3135 50  0001 C CNN
F 3 "" H 1445 3135 50  0001 C CNN
	1    1445 3135
	1    0    0    -1  
$EndComp
Wire Wire Line
	1510 3135 1445 3135
$Comp
L power:GND #PWR05
U 1 1 618810DE
P 2160 3135
F 0 "#PWR05" H 2160 2885 50  0001 C CNN
F 1 "GND" H 2165 2962 50  0000 C CNN
F 2 "" H 2160 3135 50  0001 C CNN
F 3 "" H 2160 3135 50  0001 C CNN
	1    2160 3135
	1    0    0    -1  
$EndComp
Wire Wire Line
	2160 3135 2110 3135
$Comp
L power:+5V #PWR04
U 1 1 61881891
P 1860 2560
F 0 "#PWR04" H 1860 2410 50  0001 C CNN
F 1 "+5V" H 1875 2733 50  0000 C CNN
F 2 "" H 1860 2560 50  0001 C CNN
F 3 "" H 1860 2560 50  0001 C CNN
	1    1860 2560
	1    0    0    -1  
$EndComp
$Comp
L Device:C_Small C1
U 1 1 6188303E
P 1480 1240
F 0 "C1" H 1572 1286 50  0000 L CNN
F 1 "0.1 uF" H 1572 1195 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 1480 1240 50  0001 C CNN
F 3 "https://www.digikey.com/en/products/detail/kemet/C0603C104K3RAC7081/12701191" H 1480 1240 50  0001 C CNN
	1    1480 1240
	1    0    0    -1  
$EndComp
$Comp
L power:+5V #PWR02
U 1 1 618844D2
P 1480 1140
F 0 "#PWR02" H 1480 990 50  0001 C CNN
F 1 "+5V" H 1495 1313 50  0000 C CNN
F 2 "" H 1480 1140 50  0001 C CNN
F 3 "" H 1480 1140 50  0001 C CNN
	1    1480 1140
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR03
U 1 1 61885847
P 1480 1340
F 0 "#PWR03" H 1480 1090 50  0001 C CNN
F 1 "GND" H 1485 1167 50  0000 C CNN
F 2 "" H 1480 1340 50  0001 C CNN
F 3 "" H 1480 1340 50  0001 C CNN
	1    1480 1340
	1    0    0    -1  
$EndComp
Wire Wire Line
	1495 2935 1510 2935
Text Notes 4820 2055 0    50   ~ 0
Current through each photointerruptor: 15mA\n270mA total
$Comp
L photointerruptor_lib:AEDR-8300 U2
U 1 1 6191F60F
P 2805 3035
F 0 "U2" H 2810 2685 50  0000 C CNN
F 1 "AEDR-8300" H 2805 2620 50  0000 C CNN
F 2 "photointerruptor_lib:Broadcom_DFN-6_2x2mm_P0.65mm" H 2805 2835 50  0001 C CNN
F 3 "http://www.everlight.com/file/ProductFile/ITR8307.pdf" H 2805 3135 50  0001 C CNN
	1    2805 3035
	1    0    0    -1  
$EndComp
NoConn ~ 2755 2785
$Comp
L power:GND #PWR06
U 1 1 6191F616
P 2440 3135
F 0 "#PWR06" H 2440 2885 50  0001 C CNN
F 1 "GND" H 2445 2962 50  0000 C CNN
F 2 "" H 2440 3135 50  0001 C CNN
F 3 "" H 2440 3135 50  0001 C CNN
	1    2440 3135
	1    0    0    -1  
$EndComp
Wire Wire Line
	2505 3135 2440 3135
$Comp
L power:GND #PWR08
U 1 1 6191F61D
P 3155 3135
F 0 "#PWR08" H 3155 2885 50  0001 C CNN
F 1 "GND" H 3160 2962 50  0000 C CNN
F 2 "" H 3155 3135 50  0001 C CNN
F 3 "" H 3155 3135 50  0001 C CNN
	1    3155 3135
	1    0    0    -1  
$EndComp
Wire Wire Line
	3155 3135 3105 3135
$Comp
L power:+5V #PWR07
U 1 1 6191F624
P 2855 2560
F 0 "#PWR07" H 2855 2410 50  0001 C CNN
F 1 "+5V" H 2870 2733 50  0000 C CNN
F 2 "" H 2855 2560 50  0001 C CNN
F 3 "" H 2855 2560 50  0001 C CNN
	1    2855 2560
	1    0    0    -1  
$EndComp
Wire Wire Line
	2490 2935 2505 2935
$Comp
L photointerruptor_lib:AEDR-8300 U3
U 1 1 6192D89D
P 3815 3035
F 0 "U3" H 3820 2685 50  0000 C CNN
F 1 "AEDR-8300" H 3815 2620 50  0000 C CNN
F 2 "photointerruptor_lib:Broadcom_DFN-6_2x2mm_P0.65mm" H 3815 2835 50  0001 C CNN
F 3 "http://www.everlight.com/file/ProductFile/ITR8307.pdf" H 3815 3135 50  0001 C CNN
	1    3815 3035
	1    0    0    -1  
$EndComp
NoConn ~ 3765 2785
$Comp
L power:GND #PWR09
U 1 1 6192D8A4
P 3450 3135
F 0 "#PWR09" H 3450 2885 50  0001 C CNN
F 1 "GND" H 3455 2962 50  0000 C CNN
F 2 "" H 3450 3135 50  0001 C CNN
F 3 "" H 3450 3135 50  0001 C CNN
	1    3450 3135
	1    0    0    -1  
$EndComp
Wire Wire Line
	3515 3135 3450 3135
$Comp
L power:GND #PWR011
U 1 1 6192D8AB
P 4165 3135
F 0 "#PWR011" H 4165 2885 50  0001 C CNN
F 1 "GND" H 4170 2962 50  0000 C CNN
F 2 "" H 4165 3135 50  0001 C CNN
F 3 "" H 4165 3135 50  0001 C CNN
	1    4165 3135
	1    0    0    -1  
$EndComp
Wire Wire Line
	4165 3135 4115 3135
$Comp
L power:+5V #PWR010
U 1 1 6192D8B2
P 3865 2560
F 0 "#PWR010" H 3865 2410 50  0001 C CNN
F 1 "+5V" H 3880 2733 50  0000 C CNN
F 2 "" H 3865 2560 50  0001 C CNN
F 3 "" H 3865 2560 50  0001 C CNN
	1    3865 2560
	1    0    0    -1  
$EndComp
Wire Wire Line
	3500 2935 3515 2935
$Comp
L photointerruptor_lib:AEDR-8300 U4
U 1 1 61936DBC
P 4800 3040
F 0 "U4" H 4805 2690 50  0000 C CNN
F 1 "AEDR-8300" H 4800 2625 50  0000 C CNN
F 2 "photointerruptor_lib:Broadcom_DFN-6_2x2mm_P0.65mm" H 4800 2840 50  0001 C CNN
F 3 "http://www.everlight.com/file/ProductFile/ITR8307.pdf" H 4800 3140 50  0001 C CNN
	1    4800 3040
	1    0    0    -1  
$EndComp
NoConn ~ 4750 2790
$Comp
L power:GND #PWR012
U 1 1 61936DC3
P 4435 3140
F 0 "#PWR012" H 4435 2890 50  0001 C CNN
F 1 "GND" H 4440 2967 50  0000 C CNN
F 2 "" H 4435 3140 50  0001 C CNN
F 3 "" H 4435 3140 50  0001 C CNN
	1    4435 3140
	1    0    0    -1  
$EndComp
Wire Wire Line
	4500 3140 4435 3140
$Comp
L power:GND #PWR014
U 1 1 61936DCA
P 5150 3140
F 0 "#PWR014" H 5150 2890 50  0001 C CNN
F 1 "GND" H 5155 2967 50  0000 C CNN
F 2 "" H 5150 3140 50  0001 C CNN
F 3 "" H 5150 3140 50  0001 C CNN
	1    5150 3140
	1    0    0    -1  
$EndComp
Wire Wire Line
	5150 3140 5100 3140
$Comp
L power:+5V #PWR013
U 1 1 61936DD1
P 4850 2565
F 0 "#PWR013" H 4850 2415 50  0001 C CNN
F 1 "+5V" H 4865 2738 50  0000 C CNN
F 2 "" H 4850 2565 50  0001 C CNN
F 3 "" H 4850 2565 50  0001 C CNN
	1    4850 2565
	1    0    0    -1  
$EndComp
Wire Wire Line
	4485 2940 4500 2940
$Comp
L photointerruptor_lib:AEDR-8300 U5
U 1 1 61936DE0
P 5795 3040
F 0 "U5" H 5800 2690 50  0000 C CNN
F 1 "AEDR-8300" H 5795 2625 50  0000 C CNN
F 2 "photointerruptor_lib:Broadcom_DFN-6_2x2mm_P0.65mm" H 5795 2840 50  0001 C CNN
F 3 "http://www.everlight.com/file/ProductFile/ITR8307.pdf" H 5795 3140 50  0001 C CNN
	1    5795 3040
	1    0    0    -1  
$EndComp
NoConn ~ 5745 2790
$Comp
L power:GND #PWR015
U 1 1 61936DE7
P 5430 3140
F 0 "#PWR015" H 5430 2890 50  0001 C CNN
F 1 "GND" H 5435 2967 50  0000 C CNN
F 2 "" H 5430 3140 50  0001 C CNN
F 3 "" H 5430 3140 50  0001 C CNN
	1    5430 3140
	1    0    0    -1  
$EndComp
Wire Wire Line
	5495 3140 5430 3140
$Comp
L power:GND #PWR017
U 1 1 61936DEE
P 6145 3140
F 0 "#PWR017" H 6145 2890 50  0001 C CNN
F 1 "GND" H 6150 2967 50  0000 C CNN
F 2 "" H 6145 3140 50  0001 C CNN
F 3 "" H 6145 3140 50  0001 C CNN
	1    6145 3140
	1    0    0    -1  
$EndComp
Wire Wire Line
	6145 3140 6095 3140
$Comp
L power:+5V #PWR016
U 1 1 61936DF5
P 5845 2565
F 0 "#PWR016" H 5845 2415 50  0001 C CNN
F 1 "+5V" H 5860 2738 50  0000 C CNN
F 2 "" H 5845 2565 50  0001 C CNN
F 3 "" H 5845 2565 50  0001 C CNN
	1    5845 2565
	1    0    0    -1  
$EndComp
Wire Wire Line
	5480 2940 5495 2940
$Comp
L photointerruptor_lib:AEDR-8300 U6
U 1 1 61936E04
P 6805 3040
F 0 "U6" H 6810 2690 50  0000 C CNN
F 1 "AEDR-8300" H 6805 2625 50  0000 C CNN
F 2 "photointerruptor_lib:Broadcom_DFN-6_2x2mm_P0.65mm" H 6805 2840 50  0001 C CNN
F 3 "http://www.everlight.com/file/ProductFile/ITR8307.pdf" H 6805 3140 50  0001 C CNN
	1    6805 3040
	1    0    0    -1  
$EndComp
NoConn ~ 6755 2790
$Comp
L power:GND #PWR018
U 1 1 61936E0B
P 6440 3140
F 0 "#PWR018" H 6440 2890 50  0001 C CNN
F 1 "GND" H 6445 2967 50  0000 C CNN
F 2 "" H 6440 3140 50  0001 C CNN
F 3 "" H 6440 3140 50  0001 C CNN
	1    6440 3140
	1    0    0    -1  
$EndComp
Wire Wire Line
	6505 3140 6440 3140
$Comp
L power:GND #PWR020
U 1 1 61936E12
P 7155 3140
F 0 "#PWR020" H 7155 2890 50  0001 C CNN
F 1 "GND" H 7160 2967 50  0000 C CNN
F 2 "" H 7155 3140 50  0001 C CNN
F 3 "" H 7155 3140 50  0001 C CNN
	1    7155 3140
	1    0    0    -1  
$EndComp
Wire Wire Line
	7155 3140 7105 3140
$Comp
L power:+5V #PWR019
U 1 1 61936E19
P 6855 2565
F 0 "#PWR019" H 6855 2415 50  0001 C CNN
F 1 "+5V" H 6870 2738 50  0000 C CNN
F 2 "" H 6855 2565 50  0001 C CNN
F 3 "" H 6855 2565 50  0001 C CNN
	1    6855 2565
	1    0    0    -1  
$EndComp
Wire Wire Line
	6490 2940 6505 2940
$Comp
L photointerruptor_lib:AEDR-8300 U7
U 1 1 61950C20
P 7800 3040
F 0 "U7" H 7805 2690 50  0000 C CNN
F 1 "AEDR-8300" H 7800 2625 50  0000 C CNN
F 2 "photointerruptor_lib:Broadcom_DFN-6_2x2mm_P0.65mm" H 7800 2840 50  0001 C CNN
F 3 "http://www.everlight.com/file/ProductFile/ITR8307.pdf" H 7800 3140 50  0001 C CNN
	1    7800 3040
	1    0    0    -1  
$EndComp
NoConn ~ 7750 2790
$Comp
L power:GND #PWR021
U 1 1 61950C27
P 7435 3140
F 0 "#PWR021" H 7435 2890 50  0001 C CNN
F 1 "GND" H 7440 2967 50  0000 C CNN
F 2 "" H 7435 3140 50  0001 C CNN
F 3 "" H 7435 3140 50  0001 C CNN
	1    7435 3140
	1    0    0    -1  
$EndComp
Wire Wire Line
	7500 3140 7435 3140
$Comp
L power:GND #PWR023
U 1 1 61950C2E
P 8150 3140
F 0 "#PWR023" H 8150 2890 50  0001 C CNN
F 1 "GND" H 8155 2967 50  0000 C CNN
F 2 "" H 8150 3140 50  0001 C CNN
F 3 "" H 8150 3140 50  0001 C CNN
	1    8150 3140
	1    0    0    -1  
$EndComp
Wire Wire Line
	8150 3140 8100 3140
$Comp
L power:+5V #PWR022
U 1 1 61950C35
P 7850 2565
F 0 "#PWR022" H 7850 2415 50  0001 C CNN
F 1 "+5V" H 7865 2738 50  0000 C CNN
F 2 "" H 7850 2565 50  0001 C CNN
F 3 "" H 7850 2565 50  0001 C CNN
	1    7850 2565
	1    0    0    -1  
$EndComp
Wire Wire Line
	7485 2940 7500 2940
$Comp
L photointerruptor_lib:AEDR-8300 U8
U 1 1 61950C44
P 8795 3040
F 0 "U8" H 8800 2690 50  0000 C CNN
F 1 "AEDR-8300" H 8795 2625 50  0000 C CNN
F 2 "photointerruptor_lib:Broadcom_DFN-6_2x2mm_P0.65mm" H 8795 2840 50  0001 C CNN
F 3 "http://www.everlight.com/file/ProductFile/ITR8307.pdf" H 8795 3140 50  0001 C CNN
	1    8795 3040
	1    0    0    -1  
$EndComp
NoConn ~ 8745 2790
$Comp
L power:GND #PWR024
U 1 1 61950C4B
P 8430 3140
F 0 "#PWR024" H 8430 2890 50  0001 C CNN
F 1 "GND" H 8435 2967 50  0000 C CNN
F 2 "" H 8430 3140 50  0001 C CNN
F 3 "" H 8430 3140 50  0001 C CNN
	1    8430 3140
	1    0    0    -1  
$EndComp
Wire Wire Line
	8495 3140 8430 3140
$Comp
L power:GND #PWR026
U 1 1 61950C52
P 9145 3140
F 0 "#PWR026" H 9145 2890 50  0001 C CNN
F 1 "GND" H 9150 2967 50  0000 C CNN
F 2 "" H 9145 3140 50  0001 C CNN
F 3 "" H 9145 3140 50  0001 C CNN
	1    9145 3140
	1    0    0    -1  
$EndComp
Wire Wire Line
	9145 3140 9095 3140
$Comp
L power:+5V #PWR025
U 1 1 61950C59
P 8845 2565
F 0 "#PWR025" H 8845 2415 50  0001 C CNN
F 1 "+5V" H 8860 2738 50  0000 C CNN
F 2 "" H 8845 2565 50  0001 C CNN
F 3 "" H 8845 2565 50  0001 C CNN
	1    8845 2565
	1    0    0    -1  
$EndComp
Wire Wire Line
	8480 2940 8495 2940
$Comp
L photointerruptor_lib:AEDR-8300 U9
U 1 1 61950C68
P 9805 3040
F 0 "U9" H 9810 2690 50  0000 C CNN
F 1 "AEDR-8300" H 9805 2625 50  0000 C CNN
F 2 "photointerruptor_lib:Broadcom_DFN-6_2x2mm_P0.65mm" H 9805 2840 50  0001 C CNN
F 3 "http://www.everlight.com/file/ProductFile/ITR8307.pdf" H 9805 3140 50  0001 C CNN
	1    9805 3040
	1    0    0    -1  
$EndComp
NoConn ~ 9755 2790
$Comp
L power:GND #PWR027
U 1 1 61950C6F
P 9440 3140
F 0 "#PWR027" H 9440 2890 50  0001 C CNN
F 1 "GND" H 9445 2967 50  0000 C CNN
F 2 "" H 9440 3140 50  0001 C CNN
F 3 "" H 9440 3140 50  0001 C CNN
	1    9440 3140
	1    0    0    -1  
$EndComp
Wire Wire Line
	9505 3140 9440 3140
$Comp
L power:GND #PWR029
U 1 1 61950C76
P 10155 3140
F 0 "#PWR029" H 10155 2890 50  0001 C CNN
F 1 "GND" H 10160 2967 50  0000 C CNN
F 2 "" H 10155 3140 50  0001 C CNN
F 3 "" H 10155 3140 50  0001 C CNN
	1    10155 3140
	1    0    0    -1  
$EndComp
Wire Wire Line
	10155 3140 10105 3140
$Comp
L power:+5V #PWR028
U 1 1 61950C7D
P 9855 2565
F 0 "#PWR028" H 9855 2415 50  0001 C CNN
F 1 "+5V" H 9870 2738 50  0000 C CNN
F 2 "" H 9855 2565 50  0001 C CNN
F 3 "" H 9855 2565 50  0001 C CNN
	1    9855 2565
	1    0    0    -1  
$EndComp
Wire Wire Line
	9490 2940 9505 2940
$Comp
L Mechanical:MountingHole H2
U 1 1 619CC0E3
P 1570 5780
F 0 "H2" H 1670 5826 50  0000 L CNN
F 1 "MountingHole" H 1670 5735 50  0000 L CNN
F 2 "photointerruptor_lib:MountingHole_2.3mm_#2" H 1570 5780 50  0001 C CNN
F 3 "~" H 1570 5780 50  0001 C CNN
	1    1570 5780
	1    0    0    -1  
$EndComp
$Comp
L Mechanical:MountingHole H4
U 1 1 619D10C2
P 2315 5785
F 0 "H4" H 2415 5831 50  0000 L CNN
F 1 "MountingHole" H 2415 5740 50  0000 L CNN
F 2 "photointerruptor_lib:MountingHole_2.3mm_#2" H 2315 5785 50  0001 C CNN
F 3 "~" H 2315 5785 50  0001 C CNN
	1    2315 5785
	1    0    0    -1  
$EndComp
$Comp
L Mechanical:MountingHole H1
U 1 1 619D3417
P 1565 6010
F 0 "H1" H 1665 6056 50  0000 L CNN
F 1 "MountingHole" H 1665 5965 50  0000 L CNN
F 2 "photointerruptor_lib:MountingHole_2.3mm_#2" H 1565 6010 50  0001 C CNN
F 3 "~" H 1565 6010 50  0001 C CNN
	1    1565 6010
	1    0    0    -1  
$EndComp
$Comp
L Mechanical:MountingHole H3
U 1 1 619D341D
P 2310 6015
F 0 "H3" H 2410 6061 50  0000 L CNN
F 1 "MountingHole" H 2410 5970 50  0000 L CNN
F 2 "photointerruptor_lib:MountingHole_2.3mm_#2" H 2310 6015 50  0001 C CNN
F 3 "~" H 2310 6015 50  0001 C CNN
	1    2310 6015
	1    0    0    -1  
$EndComp
$Comp
L Mechanical:MountingHole_Pad H5
U 1 1 619D7C02
P 3145 5805
F 0 "H5" V 3090 5980 50  0000 L CNN
F 1 "MountingHole_Pad" V 3170 5980 50  0000 L CNN
F 2 "photointerruptor_lib:power-pads_copy" H 3145 5805 50  0001 C CNN
F 3 "~" H 3145 5805 50  0001 C CNN
	1    3145 5805
	0    1    1    0   
$EndComp
$Comp
L Mechanical:MountingHole_Pad H6
U 1 1 619DF6A9
P 3145 6015
F 0 "H6" V 3099 6165 50  0000 L CNN
F 1 "MountingHole_Pad" V 3190 6165 50  0000 L CNN
F 2 "photointerruptor_lib:power-pads_copy" H 3145 6015 50  0001 C CNN
F 3 "~" H 3145 6015 50  0001 C CNN
	1    3145 6015
	0    1    1    0   
$EndComp
$Comp
L power:+5V #PWR0101
U 1 1 619E202B
P 3045 5805
F 0 "#PWR0101" H 3045 5655 50  0001 C CNN
F 1 "+5V" H 3060 5978 50  0000 C CNN
F 2 "" H 3045 5805 50  0001 C CNN
F 3 "" H 3045 5805 50  0001 C CNN
	1    3045 5805
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0102
U 1 1 619E2EDB
P 3045 6015
F 0 "#PWR0102" H 3045 5765 50  0001 C CNN
F 1 "GND" H 3050 5842 50  0000 C CNN
F 2 "" H 3045 6015 50  0001 C CNN
F 3 "" H 3045 6015 50  0001 C CNN
	1    3045 6015
	1    0    0    -1  
$EndComp
Text Label 2345 2935 2    50   ~ 0
ENC_1
Wire Wire Line
	2110 2935 2345 2935
Text Label 3360 2935 2    50   ~ 0
ENC_2
Wire Wire Line
	3105 2935 3360 2935
Text Label 4370 2935 2    50   ~ 0
ENC_3
Wire Wire Line
	4115 2935 4370 2935
Text Label 5355 2940 2    50   ~ 0
ENC_4
Wire Wire Line
	5100 2940 5355 2940
Text Label 6350 2940 2    50   ~ 0
ENC_5
Wire Wire Line
	6095 2940 6350 2940
Text Label 7360 2940 2    50   ~ 0
ENC_6
Wire Wire Line
	7105 2940 7360 2940
Text Label 8355 2940 2    50   ~ 0
ENC_7
Wire Wire Line
	8100 2940 8355 2940
Text Label 9350 2940 2    50   ~ 0
ENC_8
Wire Wire Line
	9095 2940 9350 2940
Text Label 10360 2940 2    50   ~ 0
ENC_9
Wire Wire Line
	10105 2940 10360 2940
$Comp
L Mechanical:MountingHole_Pad H7
U 1 1 61A7124F
P 8895 4355
F 0 "H7" V 8845 4515 50  0000 L CNN
F 1 "MountingHole_Pad" V 8920 4510 50  0000 L CNN
F 2 "photointerruptor_lib:power-pads_copy" H 8895 4355 50  0001 C CNN
F 3 "~" H 8895 4355 50  0001 C CNN
	1    8895 4355
	0    1    1    0   
$EndComp
$Comp
L Mechanical:MountingHole_Pad H8
U 1 1 61A71255
P 8895 4565
F 0 "H8" V 8849 4715 50  0000 L CNN
F 1 "MountingHole_Pad" V 8940 4715 50  0000 L CNN
F 2 "photointerruptor_lib:power-pads_copy" H 8895 4565 50  0001 C CNN
F 3 "~" H 8895 4565 50  0001 C CNN
	1    8895 4565
	0    1    1    0   
$EndComp
$Comp
L Mechanical:MountingHole_Pad H12
U 1 1 61A72E10
P 8900 4785
F 0 "H12" V 8845 4940 50  0000 L CNN
F 1 "MountingHole_Pad" V 8925 4935 50  0000 L CNN
F 2 "photointerruptor_lib:power-pads_copy" H 8900 4785 50  0001 C CNN
F 3 "~" H 8900 4785 50  0001 C CNN
	1    8900 4785
	0    1    1    0   
$EndComp
$Comp
L Mechanical:MountingHole_Pad H13
U 1 1 61A72E16
P 8900 4995
F 0 "H13" V 8854 5145 50  0000 L CNN
F 1 "MountingHole_Pad" V 8945 5145 50  0000 L CNN
F 2 "photointerruptor_lib:power-pads_copy" H 8900 4995 50  0001 C CNN
F 3 "~" H 8900 4995 50  0001 C CNN
	1    8900 4995
	0    1    1    0   
$EndComp
$Comp
L Mechanical:MountingHole_Pad H9
U 1 1 61A7812E
P 8895 5205
F 0 "H9" V 8845 5365 50  0000 L CNN
F 1 "MountingHole_Pad" V 8920 5360 50  0000 L CNN
F 2 "photointerruptor_lib:power-pads_copy" H 8895 5205 50  0001 C CNN
F 3 "~" H 8895 5205 50  0001 C CNN
	1    8895 5205
	0    1    1    0   
$EndComp
$Comp
L Mechanical:MountingHole_Pad H10
U 1 1 61A78134
P 8895 5415
F 0 "H10" V 8849 5565 50  0000 L CNN
F 1 "MountingHole_Pad" V 8940 5565 50  0000 L CNN
F 2 "photointerruptor_lib:power-pads_copy" H 8895 5415 50  0001 C CNN
F 3 "~" H 8895 5415 50  0001 C CNN
	1    8895 5415
	0    1    1    0   
$EndComp
$Comp
L Mechanical:MountingHole_Pad H14
U 1 1 61A7813A
P 8900 5635
F 0 "H14" V 8845 5790 50  0000 L CNN
F 1 "MountingHole_Pad" V 8925 5785 50  0000 L CNN
F 2 "photointerruptor_lib:power-pads_copy" H 8900 5635 50  0001 C CNN
F 3 "~" H 8900 5635 50  0001 C CNN
	1    8900 5635
	0    1    1    0   
$EndComp
$Comp
L Mechanical:MountingHole_Pad H15
U 1 1 61A78140
P 8900 5845
F 0 "H15" V 8854 5995 50  0000 L CNN
F 1 "MountingHole_Pad" V 8945 5995 50  0000 L CNN
F 2 "photointerruptor_lib:power-pads_copy" H 8900 5845 50  0001 C CNN
F 3 "~" H 8900 5845 50  0001 C CNN
	1    8900 5845
	0    1    1    0   
$EndComp
$Comp
L Mechanical:MountingHole_Pad H11
U 1 1 61A799B0
P 8895 6055
F 0 "H11" V 8849 6205 50  0000 L CNN
F 1 "MountingHole_Pad" V 8940 6205 50  0000 L CNN
F 2 "photointerruptor_lib:power-pads_copy" H 8895 6055 50  0001 C CNN
F 3 "~" H 8895 6055 50  0001 C CNN
	1    8895 6055
	0    1    1    0   
$EndComp
Text Label 8560 4355 0    50   ~ 0
ENC_1
Wire Wire Line
	8795 4355 8560 4355
Text Label 8560 4565 0    50   ~ 0
ENC_2
Wire Wire Line
	8795 4565 8560 4565
Text Label 8565 4785 0    50   ~ 0
ENC_3
Wire Wire Line
	8800 4785 8565 4785
Text Label 8565 4995 0    50   ~ 0
ENC_4
Wire Wire Line
	8800 4995 8565 4995
Text Label 8560 5205 0    50   ~ 0
ENC_5
Wire Wire Line
	8795 5205 8560 5205
Text Label 8560 5415 0    50   ~ 0
ENC_6
Wire Wire Line
	8795 5415 8560 5415
Text Label 8565 5635 0    50   ~ 0
ENC_7
Wire Wire Line
	8800 5635 8565 5635
Text Label 8565 5845 0    50   ~ 0
ENC_8
Wire Wire Line
	8800 5845 8565 5845
Text Label 8560 6055 0    50   ~ 0
ENC_9
Wire Wire Line
	8795 6055 8560 6055
Wire Wire Line
	1860 2560 1860 2710
Wire Wire Line
	2855 2560 2855 2710
Wire Wire Line
	3865 2560 3865 2710
Wire Wire Line
	4850 2565 4850 2715
Wire Wire Line
	6855 2565 6855 2715
Wire Wire Line
	8845 2565 8845 2715
$Comp
L Device:R_Small R1
U 1 1 61714F81
P 1595 2710
F 0 "R1" V 1525 2715 50  0000 C CNN
F 1 "220" V 1595 2710 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" H 1595 2710 50  0001 C CNN
F 3 "https://www.digikey.com/en/products/detail/stackpole-electronics-inc/RMCF0805JT220R/1757893" H 1595 2710 50  0001 C CNN
	1    1595 2710
	0    1    1    0   
$EndComp
Wire Wire Line
	1495 2710 1495 2935
Wire Wire Line
	1695 2710 1860 2710
Connection ~ 1860 2710
Wire Wire Line
	1860 2710 1860 2785
Wire Wire Line
	2490 2710 2490 2935
Wire Wire Line
	2690 2710 2855 2710
Connection ~ 2855 2710
Wire Wire Line
	2855 2710 2855 2785
Wire Wire Line
	3500 2710 3500 2935
Wire Wire Line
	3700 2710 3865 2710
Connection ~ 3865 2710
Wire Wire Line
	3865 2710 3865 2785
Wire Wire Line
	4485 2715 4485 2940
Wire Wire Line
	4685 2715 4850 2715
Connection ~ 4850 2715
Wire Wire Line
	4850 2715 4850 2790
Wire Wire Line
	5480 2715 5480 2940
Wire Wire Line
	5845 2565 5845 2715
Wire Wire Line
	5680 2715 5845 2715
Connection ~ 5845 2715
Wire Wire Line
	5845 2715 5845 2790
Wire Wire Line
	6490 2715 6490 2940
Wire Wire Line
	6690 2715 6855 2715
Connection ~ 6855 2715
Wire Wire Line
	6855 2715 6855 2790
Wire Wire Line
	7850 2565 7850 2715
Wire Wire Line
	7485 2715 7485 2940
Wire Wire Line
	7685 2715 7850 2715
Connection ~ 7850 2715
Wire Wire Line
	7850 2715 7850 2790
Wire Wire Line
	8480 2715 8480 2940
Wire Wire Line
	8680 2715 8845 2715
Connection ~ 8845 2715
Wire Wire Line
	8845 2715 8845 2790
Wire Wire Line
	9490 2715 9490 2940
Wire Wire Line
	9690 2715 9855 2715
Wire Wire Line
	9855 2565 9855 2715
Connection ~ 9855 2715
Wire Wire Line
	9855 2715 9855 2790
$Comp
L Device:R_Small R2
U 1 1 6175A43C
P 2590 2710
F 0 "R2" V 2520 2715 50  0000 C CNN
F 1 "220" V 2590 2710 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" H 2590 2710 50  0001 C CNN
F 3 "https://www.digikey.com/en/products/detail/stackpole-electronics-inc/RMCF0805JT220R/1757893" H 2590 2710 50  0001 C CNN
	1    2590 2710
	0    1    1    0   
$EndComp
$Comp
L Device:R_Small R3
U 1 1 6175EA98
P 3600 2710
F 0 "R3" V 3530 2715 50  0000 C CNN
F 1 "220" V 3600 2710 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" H 3600 2710 50  0001 C CNN
F 3 "https://www.digikey.com/en/products/detail/stackpole-electronics-inc/RMCF0805JT220R/1757893" H 3600 2710 50  0001 C CNN
	1    3600 2710
	0    1    1    0   
$EndComp
$Comp
L Device:R_Small R4
U 1 1 61762B7C
P 4585 2715
F 0 "R4" V 4515 2720 50  0000 C CNN
F 1 "220" V 4585 2715 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" H 4585 2715 50  0001 C CNN
F 3 "https://www.digikey.com/en/products/detail/stackpole-electronics-inc/RMCF0805JT220R/1757893" H 4585 2715 50  0001 C CNN
	1    4585 2715
	0    1    1    0   
$EndComp
$Comp
L Device:R_Small R5
U 1 1 61766AB6
P 5580 2715
F 0 "R5" V 5510 2720 50  0000 C CNN
F 1 "220" V 5580 2715 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" H 5580 2715 50  0001 C CNN
F 3 "https://www.digikey.com/en/products/detail/stackpole-electronics-inc/RMCF0805JT220R/1757893" H 5580 2715 50  0001 C CNN
	1    5580 2715
	0    1    1    0   
$EndComp
$Comp
L Device:R_Small R6
U 1 1 6176AAF4
P 6590 2715
F 0 "R6" V 6520 2720 50  0000 C CNN
F 1 "220" V 6590 2715 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" H 6590 2715 50  0001 C CNN
F 3 "https://www.digikey.com/en/products/detail/stackpole-electronics-inc/RMCF0805JT220R/1757893" H 6590 2715 50  0001 C CNN
	1    6590 2715
	0    1    1    0   
$EndComp
$Comp
L Device:R_Small R7
U 1 1 6176F2E2
P 7585 2715
F 0 "R7" V 7515 2720 50  0000 C CNN
F 1 "220" V 7585 2715 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" H 7585 2715 50  0001 C CNN
F 3 "https://www.digikey.com/en/products/detail/stackpole-electronics-inc/RMCF0805JT220R/1757893" H 7585 2715 50  0001 C CNN
	1    7585 2715
	0    1    1    0   
$EndComp
$Comp
L Device:R_Small R8
U 1 1 61774FF6
P 8580 2715
F 0 "R8" V 8510 2720 50  0000 C CNN
F 1 "220" V 8580 2715 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" H 8580 2715 50  0001 C CNN
F 3 "https://www.digikey.com/en/products/detail/stackpole-electronics-inc/RMCF0805JT220R/1757893" H 8580 2715 50  0001 C CNN
	1    8580 2715
	0    1    1    0   
$EndComp
$Comp
L Device:R_Small R9
U 1 1 61778F35
P 9590 2715
F 0 "R9" V 9520 2720 50  0000 C CNN
F 1 "220" V 9590 2715 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" H 9590 2715 50  0001 C CNN
F 3 "https://www.digikey.com/en/products/detail/stackpole-electronics-inc/RMCF0805JT220R/1757893" H 9590 2715 50  0001 C CNN
	1    9590 2715
	0    1    1    0   
$EndComp
$EndSCHEMATC

ICONS_CATEGORY_ID = 1
INCENSE_CATEGORY_ID = 3
BOOKS_CATEGORY_ID = 2
LINES_PER_PAGE = 29
PHANURIUS_BOOK_SLUG = "martyrdom-and-miracles-of-saint-phanurius"
NEW_RE = "^(A-(?!0)\d{1,3})(?:\.(\d{1,2}x\d{1,2}))?((?(2)[MP]|P?))\Z|^([BHJR]-(?!0)\d{1,3})\Z|^([DG]-(?!0)\d{1,3})(P)?\Z|^(L-(?!0)\d{1,3})([ABC])\Z|^(M-(?!0)\d{1,3})([AEJ])?\Z|^(S-[1-9])\Z"
INCENSE_RE = "^(L-(?!0)\d{1,3})([ABC])\Z"
BHJR_RE = "^([BHJR]-(?!0)\d{1,3})\Z|^([DG]-(?!0)\d{1,3})(P)?\Z"
DGM_RE = "^([DGM]-(?!0)\d{1,3})([JPEA])?\Z"
DAYS_LATE = 30

LURE = "<a href=\"product_info\.php/products_id/(\d+)\">([\w\s]+)</a>"

ROOMS = [
    ("nowhere", "nowhere"),
    ("sanding", "Sanding room"),
    ("wrapping", "Wrapping room"),
    ("painting", "Painting room"),
    ("print_supply", "Print Supply"),
]
ORDER_STATUS = [
    ("PENDING", "pending"),
    ("PROCESSING", "processing"),
    ("SHIPPED", "shipped"),
    ("CANCELED", "canceled"),
    ("RETURNED", "returned"),
]

ORDER_KINDS = [
    ("INCENSE", "incense"),
    ("ENL_OR_RED", "enlargement or reduction"),
    ("GENERIC", "generic"),
]

US_STATES = [
    ("AL", "Alabama"),
    ("AK", "Alaska"),
    ("AS", "American Samoa"),
    ("AZ", "Arizona"),
    ("AR", "Arkansas"),
    ("CA", "California"),
    ("CO", "Colorado"),
    ("CT", "Connecticut"),
    ("DE", "Delaware"),
    ("DC", "District of Columbia"),
    ("FL", "Florida"),
    ("GA", "Georgia"),
    ("GU", "Guam"),
    ("HI", "Hawaii"),
    ("ID", "Idaho"),
    ("IL", "Illinois"),
    ("IN", "Indiana"),
    ("IA", "Iowa"),
    ("KS", "Kansas"),
    ("KY", "Kentucky"),
    ("LA", "Louisiana"),
    ("ME", "Maine"),
    ("MD", "Maryland"),
    ("MA", "Massachusetts"),
    ("MI", "Michigan"),
    ("MN", "Minnesota"),
    ("MS", "Mississippi"),
    ("MO", "Missouri"),
    ("MT", "Montana"),
    ("NE", "Nebraska"),
    ("NV", "Nevada"),
    ("NH", "New Hampshire"),
    ("NJ", "New Jersey"),
    ("NM", "New Mexico"),
    ("NY", "New York"),
    ("NC", "North Carolina"),
    ("ND", "North Dakota"),
    ("MP", "Northern Mariana Islands"),
    ("OH", "Ohio"),
    ("OK", "Oklahoma"),
    ("OR", "Oregon"),
    ("PA", "Pennsylvania"),
    ("PR", "Puerto Rico"),
    ("RI", "Rhode Island"),
    ("SC", "South Carolina"),
    ("SD", "South Dakota"),
    ("TN", "Tennessee"),
    ("TX", "Texas"),
    ("UT", "Utah"),
    ("VT", "Vermont"),
    ("VI", "Virgin Islands"),
    ("VA", "Virginia"),
    ("WA", "Washington"),
    ("WV", "West Virginia"),
    ("WI", "Wisconsin"),
    ("WY", "Wyoming"),
]

SS_DT_FORMAT = "%m/%d/%Y %H:%M"

ANGEL_EMAILS = ["archangelsgiftshop@gmail.com"]

BOOKSTORE_DISCOUNT_A = 30
BOOKSTORE_DISCOUNT_I = 15
BOOKSTORE_DISCOUNT_ARCHANGELS = 33

idlookup = {
    110: "A-301",
    61: "A-149",
    60: "A-339",
    69: "J-52",
    53: "A-159",
    54: "A-202",
    55: "A-393",
    56: "A-345",
    57: "A-9",
    58: "A-206",
    59: "A-207",
    49: "A-216",
    47: "A-141",
    48: "A-392",
    33: "A-1",
    34: "A-2",
    35: "A-3",
    36: "A-380",
    37: "A-399",
    124: "D-22",
    123: "A-383",
    51: "A-21",
    41: "M-23",
    42: "B-22",
    70: "A-334",
    63: "A-292",
    64: "A-312",
    65: "A-371",
    67: "A-287",
    68: "A-322",
    71: "A-4",
    72: "A-252",
    73: "A-221",
    74: "A-273",
    75: "A-366",
    76: "A-406",
    77: "A-198",
    78: "A-294",
    79: "A-311",
    80: "A-315",
    81: "A-369",
    82: "A-64",
    83: "A-329",
    84: "A-148",
    85: "A-5",
    88: "A-228",
    87: "A-147",
    89: "A-391",
    90: "A-142",
    91: "A-338",
    92: "A-183",
    93: "A-337",
    94: "A-6",
    95: "A-205",
    96: "A-302",
    97: "A-7",
    98: "A-220",
    99: "A-415",
    100: "A-346",
    101: "A-300",
    102: "A-235",
    103: "A-328",
    104: "A-261",
    105: "A-210",
    106: "A-381",
    107: "A-262",
    108: "A-414",
    109: "A-343",
    111: "A-143",
    112: "A-195",
    113: "A-10",
    114: "A-199",
    115: "A-11",
    116: "A-215",
    117: "A-309",
    118: "A-13",
    119: "A-14",
    120: "A-400",
    121: "A-15",
    122: "D-76",
    133: "A-167",
    126: "A-8",
    127: "A-161",
    128: "A-162",
    129: "A-163",
    130: "A-164",
    131: "A-165",
    132: "A-166",
    134: "A-168",
    135: "A-169",
    136: "A-170",
    137: "A-171",
    138: "A-172",
    139: "A-173",
    140: "A-174",
    141: "A-175",
    142: "A-176",
    143: "A-177",
    144: "A-178",
    145: "G-33",
    146: "A-16",
    147: "A-17",
    148: "A-238",
    149: "A-187",
    150: "A-229",
    151: "A-18",
    152: "A-226",
    153: "A-324",
    154: "A-333",
    155: "A-19",
    156: "A-20",
    158: "A-323",
    159: "A-214",
    160: "A-340",
    161: "A-185",
    162: "A-310",
    163: "A-368",
    164: "A-23",
    165: "A-358",
    166: "A-326",
    167: "A-247",
    168: "A-134",
    169: "A-360",
    170: "A-179",
    171: "A-241",
    172: "A-283",
    173: "A-24",
    174: "A-296",
    175: "A-25",
    176: "A-363",
    177: "A-144",
    178: "A-26",
    179: "A-27",
    180: "A-28",
    182: "A-29",
    183: "A-30",
    184: "A-31",
    185: "A-350",
    186: "A-280",
    187: "A-269",
    188: "A-32",
    189: "A-33",
    190: "A-372",
    191: "A-373",
    192: "A-34",
    193: "A-208",
    194: "A-36",
    195: "A-35",
    196: "A-153",
    197: "A-250",
    198: "A-265",
    199: "A-295",
    200: "A-404",
    201: "A-403",
    202: "A-37",
    203: "A-38",
    204: "A-267",
    205: "A-291",
    206: "A-39",
    207: "A-281",
    208: "A-263",
    209: "A-313",
    210: "A-40",
    211: "A-41",
    212: "A-43",
    213: "A-42",
    214: "A-209",
    215: "A-385",
    216: "A-154",
    217: "A-286",
    218: "A-231",
    219: "A-44",
    220: "A-150",
    221: "A-284",
    222: "A-45",
    223: "A-395",
    224: "A-46",
    225: "A-246",
    226: "A-182",
    227: "A-377",
    228: "A-297",
    229: "A-48",
    230: "A-47",
    231: "A-347",
    232: "A-49",
    233: "A-200",
    234: "A-388",
    235: "A-50",
    236: "A-362",
    237: "A-197",
    238: "A-51",
    239: "A-53",
    240: "A-52",
    241: "A-54",
    242: "A-55",
    243: "A-157",
    244: "A-375",
    245: "A-402",
    246: "A-211",
    247: "A-253",
    248: "A-57",
    249: "A-160",
    250: "A-155",
    251: "A-58",
    252: "A-387",
    253: "A-379",
    254: "A-344",
    255: "A-271",
    256: "A-60",
    257: "A-135",
    258: "A-59",
    259: "A-277",
    260: "A-376",
    261: "A-61",
    262: "A-62",
    263: "A-248",
    264: "A-308",
    265: "A-390",
    266: "A-63",
    267: "A-409",
    268: "A-201",
    269: "A-272",
    270: "A-192",
    271: "A-22",
    272: "A-359",
    273: "A-282",
    274: "A-65",
    275: "A-66",
    276: "A-67",
    277: "A-189",
    278: "A-68",
    279: "A-407",
    280: "A-341",
    281: "A-234",
    282: "A-330",
    283: "A-382",
    284: "A-69",
    285: "A-314",
    286: "A-70",
    287: "A-71",
    288: "A-74",
    289: "A-180",
    290: "A-288",
    291: "A-318",
    292: "A-72",
    293: "A-73",
    294: "A-151",
    295: "A-259",
    296: "A-213",
    297: "A-389",
    298: "A-270",
    299: "A-76",
    300: "A-156",
    301: "A-257",
    302: "A-239",
    303: "A-77",
    304: "A-78",
    305: "A-355",
    306: "A-307",
    307: "A-251",
    308: "A-79",
    309: "A-80",
    310: "A-227",
    311: "A-327",
    312: "A-374",
    313: "A-254",
    314: "A-316",
    315: "A-274",
    316: "A-364",
    317: "A-298",
    318: "A-249",
    319: "A-81",
    320: "A-82",
    321: "A-222",
    322: "A-413",
    323: "A-349",
    324: "A-233",
    325: "A-236",
    326: "A-83",
    327: "A-320",
    328: "A-84",
    329: "A-85",
    330: "A-86",
    331: "A-193",
    332: "A-240",
    333: "A-87",
    334: "A-260",
    335: "A-194",
    336: "A-88",
    337: "A-196",
    338: "A-89",
    339: "A-90",
    340: "A-303",
    341: "A-378",
    342: "A-429",
    343: "A-430",
    344: "A-431",
    345: "A-432",
    346: "A-421",
    347: "A-422",
    348: "A-423",
    349: "A-424",
    350: "A-425",
    351: "A-426",
    352: "A-427",
    353: "A-428",
    354: "A-420",
    355: "A-92",
    356: "A-91",
    357: "A-93",
    358: "A-94",
    359: "A-184",
    360: "A-361",
    361: "A-335",
    362: "A-401",
    363: "A-305",
    364: "A-258",
    365: "A-203",
    366: "A-95",
    367: "A-336",
    368: "A-356",
    369: "A-218",
    370: "A-97",
    371: "A-370",
    372: "A-190",
    373: "A-96",
    374: "A-365",
    375: "A-98",
    376: "A-99",
    377: "A-100",
    378: "A-416",
    379: "A-290",
    380: "A-107",
    381: "A-299",
    382: "A-411",
    383: "A-357",
    384: "A-136",
    385: "A-101",
    386: "A-275",
    387: "A-102",
    388: "A-137",
    389: "A-103",
    390: "A-276",
    391: "A-352",
    392: "A-104",
    393: "A-106",
    394: "A-351",
    395: "A-105",
    396: "A-145",
    397: "A-108",
    398: "A-408",
    399: "A-325",
    400: "A-396",
    401: "A-397",
    402: "A-109",
    403: "A-110",
    404: "A-158",
    405: "A-146",
    406: "A-138",
    407: "A-367",
    408: "A-394",
    409: "A-386",
    410: "A-111",
    411: "A-112",
    412: "A-212",
    413: "A-412",
    414: "A-285",
    415: "A-113",
    416: "A-114",
    417: "A-293",
    418: "A-319",
    419: "A-152",
    420: "A-181",
    421: "A-348",
    422: "A-116",
    423: "A-256",
    424: "A-255",
    425: "A-117",
    426: "A-118",
    427: "A-279",
    428: "A-219",
    429: "A-188",
    430: "A-331",
    431: "A-243",
    432: "A-232",
    433: "A-289",
    434: "A-119",
    435: "A-115",
    436: "A-120",
    437: "A-139",
    438: "A-237",
    439: "A-121",
    440: "A-384",
    441: "A-122",
    442: "A-123",
    443: "A-124",
    444: "A-125",
    445: "A-126",
    446: "A-127",
    447: "A-405",
    448: "A-332",
    449: "A-204",
    450: "A-306",
    451: "A-225",
    452: "A-242",
    453: "A-223",
    454: "A-224",
    455: "A-128",
    456: "A-398",
    457: "A-417",
    458: "A-191",
    459: "A-268",
    460: "A-230",
    461: "A-129",
    462: "A-130",
    463: "A-131",
    464: "A-278",
    465: "A-266",
    466: "A-264",
    467: "A-317",
    468: "A-140",
    469: "A-321",
    470: "A-342",
    471: "A-418",
    472: "A-186",
    473: "A-132",
    474: "A-217",
    475: "A-304",
    476: "A-133",
    477: "A-245",
    478: "A-312",
    479: "D-2",
    480: "D-40",
    481: "D-4",
    482: "D-63",
    483: "D-81",
    484: "D-5",
    485: "D-80",
    486: "D-66",
    487: "D-41",
    488: "D-74",
    489: "D-10",
    490: "D-11",
    491: "D-78",
    492: "D-77",
    493: "D-14",
    494: "D-64",
    495: "D-15",
    496: "D-92",
    497: "D-17",
    498: "D-18",
    499: "D-20",
    500: "D-23",
    501: "D-27",
    502: "D-67",
    503: "D-82",
    504: "D-68",
    505: "D-72",
    506: "D-29",
    507: "D-87",
    508: "D-62",
    509: "D-90",
    510: "D-31",
    511: "D-30",
    512: "D-83",
    513: "D-85",
    514: "D-32",
    515: "D-61",
    516: "D-84",
    517: "D-28",
    518: "D-70",
    519: "D-34",
    520: "D-36",
    522: "D-37",
    523: "D-35",
    524: "D-91",
    525: "D-86",
    526: "D-57",
    527: "D-93",
    528: "D-38",
    529: "D-39",
    530: "D-42",
    531: "D-43",
    532: "D-45",
    533: "D-60",
    534: "D-75",
    535: "D-89",
    536: "A-353",
    537: "D-58",
    538: "D-47",
    539: "D-48",
    540: "D-49",
    541: "D-88",
    542: "D-50",
    543: "D-51",
    544: "D-71",
    545: "D-79",
    546: "D-52",
    547: "D-56",
    548: "D-53",
    549: "D-73",
    550: "D-65",
    551: "D-54",
    552: "D-69",
    553: "R-26",
    554: "R-28",
    561: "R-22",
    556: "R-29",
    557: "R-24",
    558: "R-19",
    560: "R-20",
    562: "R-27",
    563: "B-30",
    564: "B-31",
    565: "B-28",
    566: "B-36",
    567: "B-6",
    569: "B-9",
    570: "B-18",
    572: "B-20",
    573: "B-45",
    574: "B-3",
    575: "B-26",
    576: "B-25",
    577: "B-10",
    578: "B-17",
    579: "B-16",
    580: "B-27",
    581: "B-35",
    583: "L-1",
    584: "L-2",
    585: "L-4",
    586: "L-3",
    587: "L-5",
    588: "L-6",
    589: "L-7",
    590: "L-8",
    591: "L-9",
    592: "L-10",
    593: "L-11",
    594: "L-13",
    595: "L-14",
    596: "L-15",
    597: "L-16",
    598: "L-17",
    599: "L-18",
    600: "L-19",
    601: "L-31",
    602: "L-27",
    603: "L-20",
    604: "L-21",
    605: "L-22",
    606: "L-23",
    607: "L-24",
    608: "L-28",
    609: "L-32",
    610: "L-25",
    611: "L-26",
    612: "L-29",
    613: "L-39",
    614: "L-33",
    615: "L-36",
    616: "L-38",
    617: "L-30",
    618: "L-34",
    619: "L-35",
    620: "L-37",
    621: "L-43",
    622: "L-42",
    623: "L-40",
    624: "L-41",
    625: "J-17",
    626: "B-4",
    627: "B-1",
    628: "B-29",
    629: "B-14",
    630: "B-34",
    631: "B-39",
    632: "B-15",
    633: "B-32",
    634: "B-33",
    635: "B-23",
    636: "B-24",
    659: "B-38",
    686: "B-46",
    687: "C-48",
    688: "M-207",
    689: "M-223",
    690: "M-209",
    691: "M-225",
    692: "M-236",
    693: "M-243",
    694: "M-208",
    695: "M-227",
    696: "M-244",
    697: "M-226",
    698: "M-228",
    699: "M-222",
    700: "M-245",
    701: "M-211",
    702: "M-250",
    703: "M-252",
    704: "M-636",
    705: "M-246",
    706: "M-249",
    707: "M-237",
    708: "M-232",
    709: "M-204",
    710: "M-644",
    711: "M-643",
    712: "M-642",
    713: "M-645",
    714: "M-203",
    715: "M-640",
    716: "M-641",
    717: "M-648",
    718: "M-649",
    719: "M-650",
    720: "M-654",
    721: "M-655",
    722: "M-657",
    723: "M-653",
    724: "M-652",
    725: "M-659",
    726: "M-519",
    727: "M-501",
    728: "M-661",
    729: "M-530",
    730: "M-505",
    731: "M-526",
    732: "M-509",
    733: "M-544",
    734: "M-502",
    735: "M-512",
    736: "M-513",
    737: "H-260",
    738: "H-117",
    739: "H-82",
    743: "J-19",
    744: "J-49",
    745: "J-37",
    746: "J-36",
    747: "C-6",
    748: "C-7",
    749: "C-8",
    750: "C-9",
    751: "C-10",
    752: "C-11",
    753: "C-12",
    754: "C-13",
    755: "C-14",
    756: "C-15",
    757: "C-16",
    758: "C-17",
    759: "C-18",
    760: "C-34",
    761: "C-35",
    762: "C-36",
    763: "C-37",
    764: "C-38",
    765: "C-39",
    766: "C-40",
    767: "C-41",
    768: "C-42",
    769: "C-43",
    770: "C-44",
    771: "C-45",
    772: "C-46",
    773: "C-49",
    774: "C-50",
    775: "C-51",
    776: "C-52",
    777: "C-53",
    778: "C-54",
    779: "C-55",
    780: "C-56",
    781: "C-57",
    782: "C-58",
    783: "C-59",
    784: "C-60",
    785: "C-61",
    786: "C-62",
    787: "C-63",
    788: "C-64",
    789: "C-65",
    790: "C-66",
    791: "C-67",
    792: "C-68",
    793: "C-69",
    794: "C-71",
    795: "C-72",
    796: "C-73",
    797: "C-74",
    798: "C-75",
    799: "C-76",
    800: "C-77",
    801: "C-78",
    802: "C-79",
    891: "B-48",
    803: "J-50",
    804: "J-51",
    805: "H-246",
    806: "H-218",
    807: "H-182",
    808: "H-120",
    809: "H-214",
    810: "H-215",
    811: "H-216",
    812: "H-187",
    813: "H-217",
    814: "H-220",
    815: "H-219",
    816: "H-259",
    817: "H-188",
    818: "H-189",
    819: "H-190",
    820: "H-221",
    821: "H-191",
    822: "H-192",
    823: "H-258",
    824: "H-222",
    825: "H-185",
    826: "H-186",
    827: "H-193",
    828: "H-223",
    829: "H-113",
    830: "M-401",
    831: "J-13",
    832: "J-54",
    833: "J-14",
    834: "J-15",
    835: "J-55",
    836: "J-16",
    838: "M-452",
    839: "M-472",
    840: "M-451",
    841: "M-471",
    842: "M-450",
    843: "M-470",
    844: "M-495",
    845: "M-496",
    846: "M-475",
    847: "M-477",
    848: "M-476",
    849: "M-478",
    850: "M-493",
    890: "J-1",
    851: "M-494",
    852: "J-23",
    853: "J-25",
    854: "J-22",
    855: "J-21",
    856: "J-48",
    857: "J-66",
    858: "J-4",
    859: "J-3",
    860: "J-47",
    861: "J-65",
    862: "J-58",
    863: "J-44",
    864: "J-53",
    865: "J-8",
    866: "J-9",
    867: "J-30",
    868: "J-26",
    869: "J-31",
    870: "J-32",
    871: "J-33",
    872: "J-63",
    873: "J-34",
    874: "J-10",
    875: "J-64",
    876: "M-58",
    877: "M-660",
    878: "M-51",
    879: "M-50",
    880: "M-218",
    881: "M-52",
    882: "M-537",
    883: "M-536",
    884: "M-57",
    885: "M-40",
    886: "M-217",
    887: "M-497",
    888: "B-47",
    889: "J-18",
    894: "C-80",
    896: "C-70",
    897: "B-40",
    898: "G-27",
    899: "M-41",
    900: "L-44",
    901: "Z-1",
    902: "A-433",
    903: "A-434",
    904: "A-435",
    905: "A-419",
    906: "R-30",
    907: "A-436",
    908: "G-28",
    909: "G-32",
    910: "M-662",
    912: "A-437",
    913: "A-438",
    914: "A-439",
    915: "M-663",
    916: "A-56",
    917: "B-42",
    918: "B-901",
    919: "A-440",
    920: "A-441",
    921: "H-123",
    922: "H-124",
    923: "H-179",
    924: "H-250",
    925: "H-249",
    926: "H-181",
    927: "H-180",
    928: "H-125",
    929: "H-238",
    930: "H-255",
    931: "H-257",
    932: "H-251",
    933: "H-235",
    934: "H-236",
    935: "H-237",
    936: "H-253",
    937: "H-194",
    938: "H-195",
    939: "H-252",
    940: "H-227",
    941: "H-127",
    942: "H-133",
    943: "H-226",
    944: "H-131",
    945: "H-130",
    946: "H-151",
    947: "H-256",
    948: "H-225",
    949: "H-224",
    950: "H-196",
    951: "H-126",
    953: "H-261",
    952: "H-262",
    954: "B-44",
    955: "H-198",
    956: "A-410",
    957: "M-248",
    958: "M-647",
    959: "G-22",
    960: "B-49",
    961: "B-50",
    962: "A-442",
    963: "A-443",
    964: "A-444",
    965: "A-445",
    966: "A-446",
    967: "J-70",
    968: "H-263",
    969: "D-93",
    970: "A-447",
    971: "A-448",
    972: "A-450",
    973: "A-449",
    974: "A-451",
    975: "A-452",
    976: "B-51",
    977: "A-453",
    978: "A-454",
    979: "A-455",
    980: "B-53",
    981: "A-456",
    982: "A-457",
    983: "A-459",
    984: "A-458",
    985: "B-54",
    986: "B-56",
    987: "B-55",
    988: "J-73",
    989: "B-57",
    991: "J-39",
    992: "B-58",
    993: "B-59",
    998: "B-61",
    999: "B-62",
    994: "B-503",
    995: "B-504",
    996: "B-505",
    997: "B-60",
    1000: "S-1",
}

PACKING_WEIGHT_MULTIPLIER = 1.22

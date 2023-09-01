ICONS_CATEGORY_ID = 1
INCENSE_CATEGORY_ID = 3
BOOKS_CATEGORY_ID = 2
ICON_PRINT_TYPE_ID = 4
MOUNTED_ICON_TYPE_ID = 3
INCENSE_TYPE_ID = 2
BOOK_TYPE_ID = 1
LINES_PER_PAGE = 29
NEW_RE = "^(A-(?!0)\d{1,3})(?:\.(\d{1,2}x\d{1,2}))?((?(2)[MP]|P?))\Z|^([BHJR]-(?!0)\d{1,3})\Z|^([DG]-(?!0)\d{1,3})(P)?\Z|^(L-(?!0)\d{1,3})([ABC])\Z|^(M-(?!0)\d{1,3})([AEJ])?\Z|^(S-[1-9])\Z"
INCENSE_RE = "^(L-(?!0)\d{1,3})([ABC])\Z"
BHJR_RE = "^([BHJR]-(?!0)\d{1,3})\Z|^([DG]-(?!0)\d{1,3})(P)?\Z"
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

SS_DT_FORMAT = "%m%d%Y %H:%M"

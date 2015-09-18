#
raw_columns = [ (1,2,3,4,5),
                (6,7,8,9,10),
                (11,12,13,14,15),
                (16,None,17,18),
                (19,20,21,22),
                (23,None,24,25),
                (26,27,28,29,30),
                (31,32,33,34,35),
                (None, None, None, 36, 37),
]

# raw_columns = [ ((37,36,None,None,None),
#                 (35,34,33,32,31),
#                 (30,29,28,27,26),
#                 (25,24,None,23),
#                 (22,21,20,19),
#                 (18,17,None,16),
#                 (15,1413,12,11),
#                 (10,9,8,7,6),
#                 (5,4,3,2,1),
# ]

def x (column): return 8-column
def y(row): return row

# mapping node to coordinates
id_to_coord = { node : (x(column), y(row))
                for column, vec in enumerate(raw_columns)
                for row, node in enumerate(vec)
                if node }

print("node_specs=[")
for n,(i,j) in id_to_coord.items():
    print("{{ id: {}, i:{}, j:{} }},".format(n,i,j))
print("];")


    

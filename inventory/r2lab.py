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

def x (column): return 8-column
def y(row): return row

# mapping node to coordinates
id_to_coord = { node : (x(column), y(row))
                for column, vec in enumerate(raw_columns)
                for row, node in enumerate(vec)
                if node }

print("node_specs=[")
for n,(x,y) in id_to_coord.items():
    print("{{ id: {}, x:{}, y:{} }},".format(n,x,y))
print("];")

#coord_to_id = { c:n for n,c in id_to_coord.items() }
#print("coord_to_id=", coord_to_id,";")


    

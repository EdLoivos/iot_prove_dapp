import json

_PATH = "./"


def loadConect(graph_file):
    graph_file = _PATH + "/" + graph_file

    f = open(graph_file)
    data = json.load(f)

    f.close()
    return data

'''
def get_neighbors(gph):
    seen_by = {}
    for node in gph:
        for item in gph[node]:
            if item["id"] in seen_by:
                seen_by[item["id"]].append((node, item["pos"]))
            else:
                seen_by[item["id"]] = [(node, item["pos"])]
    return seen_by
'''

def saveConect(gph, file_name):
    json_object = json.dumps(gph, indent=2)

    with open(file_name, "w") as outfile:
        outfile.write(json_object)


if __name__ == '__main__':
    graph = loadConect("ex.txt")

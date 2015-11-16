#/usr/bin/env python3

class Selector:

    # typically regularname='fit' and rebootname='reboot'
    # so that fit01 and reboot01 are names that resolve
    def __init__(self, regularname, rebootname):
        self.regularname = regularname
        self.rebootname = rebootname
        self.set = set()

    def add_or_delete(self, index, add_if_true):
        if add_if_true:
            self.set.add(index)
        # set.remove triggers KeyError
        elif index in self.set:
            self.set.remove(index)

    # range is a shell arg, like fit01, fit1, 1, 1-12, ~25
    def add_range(self, range_spec):
        range_spec = range_spec.replace(self.regularname, "").replace(self.rebootname, "")
        commas = range_spec.split(',')
        for comma in commas:
            adding = True
            if comma.startswith('~'):
                adding = False
                comma = comma[1:]
            try:
                items = [ int(x) for x in comma.split('-')]
            except:
                #import traceback
                #traceback.print_exc()
                print("Ignored arg {comma}".format(**locals()))
                continue
            if len(items) >= 4:
                print("Ignored arg {comma}".format(**locals()))
                continue
            elif len(items) == 3:
                a, b, c = items
                for i in range(a, b+1, c):
                    self.add_or_delete(i, adding)
            elif len(items) == 2:
                a, b = items
                for i in range(a, b+1):
                    self.add_or_delete(i, adding)
            else:
                i = items[0]
                self.add_or_delete(i, adding)

    # generators
    def node_names(self):
        return ("{}{:02}".format(self.regularname, i) for i in self.set)
    def cmc_names(self):
        return ("{}{:02}".format(self.rebootname, i) for i in self.set)

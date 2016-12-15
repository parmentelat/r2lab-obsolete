import re

def urn_to_type_hrn(urn):
    """
    returns a tuple (type, hrn)
    or None, None
    """
    patt1 = "urn:publicid:IDN\+(?P<auth>[\w_:]+)\+(?P<utype>\w+)\+(?P<name>\w+)"
    try:
        auth, utype, name = re.match(patt1, urn).groups()
        hrn = auth.replace(':', '.') + '.' + name
        return utype, hrn
    except:
        import traceback
        traceback.print_exc()
        return None, None

def type_hrn_to_urn(type, hrn):
    pieces = hrn.split('.')
    return "urn:publicid:IDN+" + \
        ':'.join(pieces[:-1]) + \
        '+{}+'.format(type) + \
        pieces[-1]

############################## tests
if __name__ == '__main__':

    test_urns = [
        "urn:publicid:IDN+onelab:inria+user+walid_dabbous",
        "urn:publicid:IDN+onelab:upmc:apitest+user+aaaa",
    ]

    test_hrns = [
        "onelab.inria.walid_dabbous",
        "onelab.upmc.apitest.aaaa",
    ]

    itype = 'user'
    for iurn, ihrn in zip(test_urns, test_hrns):
        type, hrn = urn_to_type_hrn(iurn)
        assert type == itype
        assert hrn == ihrn
        urn = type_hrn_to_urn(itype, ihrn)
        assert urn == iurn
        print("{iurn} -> {itype} x {ihrn} OK".format(**locals()))
        

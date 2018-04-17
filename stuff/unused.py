# arbitrary length paths.  what a pain.
def get_paths(index, Ntok, maxlen=3, getlen=[3]):
    def justpaths(i):
        i=str(i)
        # paths starting at i
        tokpaths_by_len = {length:[] for length in xrange(2, maxlen+1)}
        tokpaths_by_len[2] = set(extend_paths(index, [(i,)] ))  # length 2
        for length in xrange(3, maxlen+1):
            newpaths = set()
            for newpath in extend_paths(index, tokpaths_by_len[length-1]):
                newpaths.add(newpath)
            tokpaths_by_len[length] = newpaths
        for length in getlen:
            tokpaths = tokpaths_by_len[length]
            for tokpath in tokpaths:
                yield tokpath
    def allpaths():
        for i in xrange(1,Ntok+1):
            for path in justpaths(i):
                yield path
    return set(path_to_edgeset(path) for path in allpaths())


f = open("hashtags", 'w')
with open("urls", 'r+') as d:
    for g in d.readlines():
        if "#" in g:
            f.write(g)
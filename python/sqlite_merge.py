import sqlite3

def merge_db(target, source):
	t = sqlite3.connect(target)
	c = t.cursor()

    c.execute("pragma synchronous = off;")
    c.execute("pragma journal_mode=off;")

    print("Attempting to merge " + source + ".")
    query = "attach '" + source + "' as toMerge;"
    c.execute(query)
    c.execute("insert into results * from toMerge.results")
    c.execute("insert into parameters * from toMerge.parameters")
    c.execute("detach toMerge")
    t.commit()
    c.close()
    t.close()

def merge_dbs(sources, target=None):
	if target is None:
		target = sources[0]
		sources = sources[1:]
	for source in sources:
		merge_db(target, source)
import sqlite3
import fnmatch
import os
import argparse
import csv
import multiprocessing

def dump_db(where, output, sources):
    source = sources.pop()
    try:
        t = sqlite3.connect(source)
    except:
        print source
        raise
    c = t.cursor()

    if output is None:
        output = "%s.csv" % source

    c.execute("pragma synchronous = off;")
    c.execute("pragma journal_mode=off;")
    print("Dumping from " + source + ".")
    if where is None:
        c.execute("select * from results join parameters;")
    else:    
        c.execute("select * from results join parameters where %s;" %where)
    csv_writer = csv.writer(open(output, "w"))
    csv_writer.writerow([i[0] for i in c.description]) # write headers
    print("Wrote headers.")
    print("Writing rows.")
    csv_writer.writerows(c)
    del csv_writer
    c.close()
    t.close()
    for source in sources:
        print("Dumping from " + source + ".")
        t = sqlite3.connect(source)
        c = t.cursor()

        c.execute("pragma synchronous = off;")
        c.execute("pragma journal_mode=off;")
        if where is None:
            c.execute("select * from results join parameters;")
        else:    
           c.execute("select * from results join parameters where %s;" %where)
        print("Writing rows.")
        csv_writer = csv.writer(open(output, "a"))
        csv_writer.writerows(c)
        del csv_writer
        c.close()
        t.close()

def list_matching(directory, name):
    matching = []
    for file in os.listdir(directory):
        if fnmatch.fnmatch(file, name):
            matching.append("%s/%s" % (directory, file))
    return matching

 
def arguments():
    parser = argparse.ArgumentParser(
        description='A simple SQLite db merger.')
    parser.add_argument('-d', type=str, nargs='?',
                   help='Directory to look for DBs to dump.', default=".",
                   dest="directory")
    parser.add_argument('-f', type=str, nargs='*',
                   help='List of source filenames which may include wildcards.', default=["*.db"],
                   dest="files")

    parser.add_argument('-t', type=str, nargs='*',
                   help='Target CSV.', default=None,
                   dest="target")
    parser.add_argument('-where', type=str, nargs='?',
        help='Optional argument to where.', dest="where",
        default=None)
    args = parser.parse_args()
    files = []
    for f in args.files:
        files.append(list_matching(args.directory, f))
    return args.target, files, args.where


if __name__ =="__main__":
    target, files, where = arguments()
    print "Dumping", files
    pool = multiprocessing.Pool()
    pool.map(lambda x: dump_db(where, target, x), files)
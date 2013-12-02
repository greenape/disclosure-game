import gzip
import sqlite3
try:
    import scoop
    single_db = False
except:
    single_db = True
    pass

class Result(object):
    def __init__(self, fields, parameters, results):
        fields.append("parameters")
        self.fields = fields
        self.param_fields = parameters.keys()
        self.param_fields.append("hash")
        param_hash = hash(tuple(parameters.values()))
        self.parameters = {param_hash:parameters.values() + [param_hash]}
        for result in results:
            result.append(param_hash)
        self.results = results

    def add_results(self, results):
        self.parameters.update(results.parameters)
        self.results += results.results
        return self

    def write(self, file_name, sep=","):
        """
        Write a results to a (csv) file.
        """
        if not single_db:
            file_name = "%s_%s" % (scoop.worker[0], file_name)
        result = [sep.join(self.fields)]
        result += map(lambda l: sep.join(map(str, l)), self.results)
        file = gzip.open(file_name, "w")
        file.write("\n".join(result))
        file.close()
    
    def write_params(self, file_name, sep=","):
        if not single_db:
            file_name = "%s_%s" % (scoop.worker[0], file_name)
        result = [sep.join(self.param_fields)]
        result += map(lambda l: sep.join(map(str, l)), self.parameters.values())
        file = gzip.open(file_name, "w")
        file.write("\n".join(result))
        file.close()

    def write_db(self, db_name):
        """
        Write this result set to an sqlite db.
        """
        if not single_db:
            db_name = "%s_%s" % (scoop.worker[0], db_name)

        conn = sqlite3.connect("%s.db" % db_name)
        
        fields = ",".join(self.fields)
        print fields
        try:
            conn.execute("CREATE TABLE IF NOT EXISTS results (%s)" % fields)
        except sqlite3.OperationalError:
            pass #Already exists I guess
        fields = ",".join(self.param_fields)
        try:
            conn.execute("CREATE TABLE IF NOT EXISTS parameters (%s)" % fields)
        except sqlite3.OperationalError:
            pass #Already exists I guess

        params = map(tuple, self.parameters.values())
        placeholders = ",".join(['?']*len(self.param_fields))
        insert = "INSERT INTO parameters VALUES(%s)" % placeholders
        #print insert
        conn.executemany(insert, params)

        results = map(tuple, self.results)
        placeholders = ",".join(['?']*len(self.fields))
        insert = "INSERT INTO results VALUES(%s)" % placeholders
        #print insert
        conn.executemany(insert, results)
        conn.commit()
        conn.close()


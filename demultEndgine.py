import editdistance

class demultiplexer():
    def __init__(self, base_index_dict, maxdist = 2,
                 undetermined_name = "Und"):
        # basedict should look like:
        # {"AAAAA+AAAAA" : sample_name}

        self.base_index_dict = base_index_dict
        self.undetermined_name = undetermined_name
        self.base_index_dict[self.undetermined_name] = self.undetermined_name
        self.index_dict = base_index_dict
        self.maxdist = maxdist

    def demultiplex(self, index):
        try: # if we've already seen this index
            return self.index_dict[index]
        except KeyError:
            relevant_base_index = self.find_index(index)
            self.index_dict[index] = self.index_dict[relevant_base_index] # save index for next search
            return self.index_dict[relevant_base_index]

    def find_index(self,index):
        # search for most suitable sample for index
        # return sample name or 'undetermined'

        results = []
        # go over samples indexes
        for i in self.base_index_dict:
            # compute edit distance for each
            d = editdistance.eval(i,index)
            if d == 0: # exact match
                return i # return and exit
            if d > self.maxdist: # too bad match, do not save
                continue
            results.append((d,i)) # save match; find the best one later

        if len(results)==1:
            return results[0][1]
        elif len(results)>1:
            results.sort(key=lambda x:x[0])

            # index matches 2 samples with same edit distance
            # i.e. there is no unambigious best match
            if results[0][0]==results[1][0]:
                return self.undetermined_name
            else: # there is the best match
                return results[0][1]
        elif len(results)==0: # no match found
            return self.undetermined_name

    def get_output_names(self):
        return self.base_index_dict.values()
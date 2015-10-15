__author__ = 'u88591'

import Features
import inspect

def computeFeatures(candidate, reference, candidate_parsed, reference_parsed, alignments):

    for name, my_class in inspect.getmembers(Features):

        if name == 'Abstract' or not inspect.isclass(my_class):
            continue

        instance = my_class()
        instance.run(candidate, reference, candidate_parsed, reference_parsed, alignments)

        print(instance.getIndex() + ' ' + instance.getDescription() + ' ' + str(instance.getValue()))
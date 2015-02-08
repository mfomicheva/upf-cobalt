from ConfigParser import ConfigParser
from json import *


class AlignerConfig(object):
    config = ConfigParser()

    def __init__(self, language):
        self.config.readfp(open('Config/' + language + '.cfg'))

    def similar_group(self, pos_source, pos_target, is_opposite, relation):
        group_name = pos_source + '_' + ('opposite_' if is_opposite else '') + pos_target + '_' + relation
        similar_group = []
        for line in self.config.get('Similar Groups', group_name).splitlines():
            similar_group.append(loads(line.strip()))
        return similar_group
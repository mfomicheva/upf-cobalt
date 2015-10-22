__author__ = 'MarinaFomicheva'

from human_data import *
from feature_extractor import *

class TrainingSet(object):

    def __init__(self):
        self.training_instances = []

    def cross_human_metric(self, human_data, features_data, directions):

        for direction in directions:

            for case in human_data[direction]:
                if case.sign == '=':
                    continue

                good_system = features_data[direction][(self.find_winner(case), case.phrase)]
                bad_system = features_data[direction][(self.find_loser(case), case.phrase)]
                self.training_instances.append(self.get_positive_instance(good_system, bad_system))
                self.training_instances.append(self.get_negative_instance(good_system, bad_system))

    def build_from_scratch(self, paths, dataset, directions, output_directory, judgments, max_segments):

        human_data = HumanData()
        human_data.add_human_data(judgments, directions, max_segments)
        features_data = FeatureExtractor()
        features_data.extract_features(paths, dataset, directions, max_segments)
        features_data.print_features(output_directory, dataset)
        self.cross_human_metric(human_data, features_data, directions)
        self.make_arff(features_data.get_feature_names(), dataset, directions, output_directory)

    def build_from_files(self, files, dataset, directions, output_directory, judgments, max_segments):

        human_data = HumanData()
        human_data.add_human_data(judgments, directions, max_segments)
        features_data = FeatureExtractor()

        for file in files:
            features_data.get_from_file(file)

        self.cross_human_metric(human_data, features_data, directions)
        self.make_arff(features_data.get_feature_names(), dataset, directions, output_directory)

    def find_winner(self, case):

        if case.sign == '<':
            return case.sys1
        else:
            return case.sys2

    def find_loser(self, case):

        if case.sign == '<':
            return case.sys2
        else:
            return case.sys1

    def get_positive_instance(self, good, bad):

        new_feature_vector = []

        for i, feature in enumerate(good):
            positive_value = float(feature[1])
            negative_value = float(bad[i][1])
            new_feature_vector.append(positive_value - negative_value)

        new_feature_vector.append('positive')
        return new_feature_vector

    def get_negative_instance(self, good, bad):

        new_feature_vector = []

        for i, feature in enumerate(good):
            positive_value = float(feature[1])
            negative_value = float(bad[i][1])
            new_feature_vector.append(negative_value - positive_value)

        new_feature_vector.append('negative')
        return new_feature_vector

    def make_arff(self, feature_names, dataset, directions, output_directory):

        for direction in directions:

            file = open(output_directory + '/' + 'training_set.' + dataset + '.' + direction + '.arff', 'w')

            print >>file, '@relation ' + dataset

            for name in feature_names:
                print >>file, '@attribute ' + name + ' real'

            print >>file, '@attribute ' + 'class' + ' {positive, negative}'
            print >>file, '@data'

            for instance in self.training_instances:
                print >>file, ','.join([str(x) for x in instance])

            file.close()
__author__ = 'MarinaFomicheva'

import argparse
from training.training_set import *
from training.human_data import *
from training.feature_extractor import *
from training.evaluate import Evaluator
import weka.core.jvm as jvm
from training.logistic_wrapper import Logistic
from weka.core.converters import Loader
from training.extend_cobalt_features import *

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
            description="Use this script to build the training set"
            )

    parser.add_argument("--options",
            help="File with paths to reference and test files",
            type=str
            )

    parser.add_argument("--features_file",
            metavar="FILE",
            type=argparse.FileType('r'),
            default=None
            )

    parser.add_argument("--model_file",
            help="File with the trained model coefficients",
            type=str
            )

    parser.add_argument("--test_file",
            help="File with cobalt features for evaluation",
            type=str
            )

    parser.add_argument("--training_set",
            help="File with cobalt features for training",
            type=str
            )

    parser.add_argument("--paths",
            help="File with paths to reference and test files",
            metavar="FILE",
            type=str
            )

    parser.add_argument("--work_directory",
            help="Work directory",
            type=str
            )

    parser.add_argument("--output_directory",
            help="Output directory",
            metavar="FILE",
            type=str
            )

    parser.add_argument("--directions",
            help="Translation directions",
            metavar="DIRECTION",
            default=["es-en"],
            nargs='*'
            )

    parser.add_argument("--dataset",
            help="Name of the dataset",
            metavar="DATASET",
            type=str
            )

    parser.add_argument("--max_segments",
            help="Maximum number of phrases",
            default=0,
            type=int,
            )

    parser.add_argument("--judgments",
            help="File with original human judgments",
            metavar="FILE",
            type=argparse.FileType('r')
            )

    parser.add_argument("--cobalt_feature_set",
            help="Name of the feature set for cobalt",
            type=str
    )

    parser.add_argument("--quest_feature_set",
            help="Name of the feature set for quest",
            type=str
            )

    parser.add_argument("--feature_set",
            help="Name of the feature set for creating training arff",
            type=str
            )

    return parser.parse_args()

args = parse_args()

def main():

    if args.options == 'extract_features':
        features_data = FeatureExtractor()

        if args.features_file is not None:
            selected_features = features_data.read_features_from_file(args.features_file)
            feature_set = args.features_file.name.split('.')[1]
        else:
            selected_features = features_data.get_feature_names_cobalt()
            feature_set = 'cobalt_all'

        for direction in args.directions:
            output_file = open(args.output_directory + '/' + args.dataset + '/' + feature_set + '.' + args.dataset + '.' + direction, 'w')
            features_data.extract_features(args.paths, args.dataset, direction, args.max_segments, selected_features)
            features_data.print_features(output_file, direction)
            output_file.close()
            print 'Features extracted for language pair ' + direction

    elif args.options == 'combine_features_raw':

        for direction in args.directions:

            features_data_cobalt = FeatureExtractor()
            features_data_quest = FeatureExtractor()

            features_data_cobalt.get_from_file(args.work_directory + '/' + 'cobalt_features_raw' + '/' + args.dataset + '/' + args.cobalt_feature_set + '/' + args.cobalt_feature_set + '.' + args.dataset + '.' + direction)
            features_data_quest.get_from_file(args.work_directory + '/' + 'quest_features_raw' + '/' + args.dataset + '/' + args.quest_feature_set + '/' + args.quest_feature_set + '.' + args.dataset + '.' + direction)

            features_combined = FeatureExtractor()
            features_combined.combine([features_data_quest, features_data_cobalt])

            feature_set_combined = args.cobalt_feature_set + '_' + args.quest_feature_set
            output_file = args.output_directory + '/' + args.dataset + '/' + feature_set_combined + '.' + args.dataset + '.' + direction
            features_combined.print_features(output_file, direction)

    elif args.options == 'build_training_set_separate':
            human_data = HumanDataRank()
            human_data.add_human_data(args.judgments, args.directions, args.max_segments)

            for file in args.training_source_files:
                features_data = FeatureExtractor()
                features_data.get_from_file(file)
                training_data = TrainingSet()
                training_data.build_from_file(features_data, human_data, args.dataset, file.split('.')[2], args.output_directory, args.max_segments)

    elif args.options == 'build_training_set_all':

        training_data = TrainingSet()
        human_data = HumanDataRank()
        human_data.add_human_data(args.judgments, args.directions, args.max_segments)
        features_data = FeatureExtractor()

        for direction in args.directions:
            features_data.get_from_file(args.work_directory + '/' + args.dataset + '/' + args.feature_set + '/' + args.feature_set + '.' + args.dataset + '.' + direction)

        dir = args.output_directory + '/' + args.dataset + '/' + args.feature_set
        training_data.merge_from_files(features_data, human_data, args.dataset, args.directions, dir, args.feature_set)

    elif args.options == 'build_training_set_absolute':
        training_data = TrainingSet()
        human_data = HumanDataScores()
        human_data.add_human_data_sample(args.judgments)
        human_dict = human_data.list_to_dict()

        selected_features = []

        for direction in args.directions:

            features_data_quest = FeatureExtractor()

            if args.features_file is not None:
                 selected_features = features_data_quest.read_features_from_file(args.features_file)
                 out_feature_set = args.features_file.name.split('.')[1]
            else:
                 out_feature_set = args.cobalt_feature_set


            my_file = open(args.work_directory + '/' + 'quest_features_raw' + '/' + args.dataset + '/' + args.quest_feature_set + '.' + args.dataset + '.' + direction, 'r')
            features_data_quest.get_from_file(my_file, selected_features)

            output_file = open(args.output_directory + '/' + args.dataset + '/' + out_feature_set + '.' + args.dataset + '.' + direction, 'w')
            training_data.build_absolute(features_data_quest, human_dict, args.directions, output_file)

    elif args.options == 'train_model':
        jvm.start(max_heap_size='1500m')
        model = Logistic()
        loader = Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(args.training_set)
        data.class_is_last()
        model.build_classifier(data)
        model.save_model(args.output_directory, args.training_set.split('.')[1], args.training_set.split('.')[2], args.training_set.split('.')[0].split('/')[-1])
        jvm.stop()

    elif args.options == 'evaluate':
        evaluator = Evaluator()
        evaluator.evaluate(args.test_file, args.model_file, args.output_directory, args.feature_set)

    elif args.options == 'extend_cobalt_features':

        selected_features = []
        out_feature_set = args.cobalt_feature_set

        if args.features_file is not None:
            selected_features = FeatureExtractor.read_features_from_file(args.features_file)
            out_feature_set = args.features_file.name.split('.')[1]

        for direction in args.directions:

            features_data_cobalt = FeatureExtractor()
            feature_data_new = FeatureExtractor()
            my_file = open(args.work_directory + '/' + 'cobalt_features_raw' + '/' + args.dataset + '/' + args.cobalt_feature_set + '.' + args.dataset + '.' + direction, 'r')
            features_data_cobalt.get_from_file(my_file, selected_features)

            new_data = extend_cobalt_features(features_data_cobalt, feature_data_new)

            output_file = open(args.output_directory + '/' + args.dataset + '/' + out_feature_set + '_' + 'extended.' + args.dataset + '.' + direction, 'w')
            new_data.print_features(output_file, direction)

    elif args.options == 'show_feature_names':
        features_data = FeatureExtractor()
        for name in features_data.get_feature_names_cobalt():
            print name
    else:
        pass

if __name__ == "__main__":
    main()

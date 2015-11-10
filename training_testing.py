__author__ = 'MarinaFomicheva'

import argparse
from training.training_set import *
from training.human_data import *
from training.feature_extractor import *
from training.evaluate import Evaluator
import weka.core.jvm as jvm
from training.logistic_wrapper import Logistic
from weka.core.converters import Loader

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
            description="Use this script to build the training set"
            )

    parser.add_argument("--options",
            help="File with paths to reference and test files",
            type=str
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

    parser.add_argument("--training_source_files",
            help="Files with raw feature data",
            nargs='*'
            )

    return parser.parse_args()

args = parse_args()

def main():

    if args.options == 'extract_features':
        features_data = FeatureExtractor()
        for direction in args.directions:
            features_data.extract_features(args.paths, args.dataset, direction, args.max_segments)
            features_data.print_features(args.output_directory, args.dataset, direction)
            print 'Features extracted for language pair ' + direction

    elif args.options == 'build_training_set_separate':
            human_data = HumanData()
            human_data.add_human_data(args.judgments, args.directions, args.max_segments)

            for file in args.training_source_files:
                features_data = FeatureExtractor()
                features_data.get_from_file(file)
                training_data = TrainingSet()
                training_data.build_from_file(features_data, human_data, args.dataset, file.split('.')[2], args.output_directory, args.max_segments)

    elif args.options == 'build_training_set_all':
        training_data = TrainingSet()
        human_data = HumanData()
        human_data.add_human_data(args.judgments, args.directions, args.max_segments)
        features_data = FeatureExtractor()

        for file in args.training_source_files:
            features_data.get_from_file(file)

        training_data.merge_from_files(features_data, human_data, args.dataset, args.directions, args.output_directory)

    elif args.options == 'train_model':
        jvm.start(max_heap_size='1500m')
        model = Logistic()
        loader = Loader(classname="weka.core.converters.ArffLoader")
        data = loader.load_file(args.training_set)
        data.class_is_last()
        model.build_classifier(data)
        model.save_model(args.output_directory, args.training_set.split('.')[1], args.training_set.split('.')[2])
        jvm.stop()
    elif args.options == 'evaluate':
        evaluator = Evaluator()
        evaluator.evaluate(args.test_file, args.model_file, args.output_directory)
    else:
        pass

if __name__ == "__main__":
    main()

__author__ = 'MarinaFomicheva'

import argparse
from training_set import *
from evaluate import Evaluator
import weka.core.jvm as jvm
from logistic_wrapper import Logistic
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

    return parser.parse_args()

args = parse_args()

def main():

    if args.options == 'extract_features':
        features_data = FeatureExtractor()
        features_data.extract_features(args.paths, args.dataset, args.directions, args.max_segments)
        features_data.print_features(args.paths, args.dataset)
    elif args.options == 'build_training_set':
        training_data = TrainingSet()
        training_data.build_from_files(args.training_source_files, args.dataset, args.directions, args.output_directory, args.judgments, args.max_segments)
    elif args.options == 'train_model':
        jvm.start()
        model = Logistic()
        loader = Loader(classname = "weka.core.converters.ArffLoader")
        data = loader.load_file(args.training_set)
        data.class_is_last()
        model.build_classifier(data)
        model.save_model(args.output_directory, args.training_set.split('.')[1])
        jvm.stop()
    elif args.options == 'evaluate':
        evaluator = Evaluator()
        evaluator.evaluate(args.test_file, args.model_file)
    else:
        pass




if __name__ == "__main__":
    main()

## UPF-Cobalt Metric for Machine Translation Evaluation
UPF-Cobalt is a MT evaluation metric that exploits alignment and syntactic context to assess MT quality.

### Installation
1. Install Stanford Parser (http://nlp.stanford.edu/software/corenlp.shtml)
2. Download dependency-based word vectors from https://levyomer.wordpress.com/2014/04/25/dependency-based-word-embeddings/ (optional)
3. Download upf-cobalt

`git clone https://github.com/mfomicheva/upf-cobalt.git`

### Usage
To use the metric, run evaluate.py with the following parameters:

|**Parameter**|**Description**|
|:-------------|:-------------|
|-r|parsed reference file|
|-t|parsed system output file|
|-v|file containing word vectors - optional|
|-a|output alignments - optional|
|-o|specify output directory - optional (default is "./Data")|

If no parameters are specified the metric will process the example files stored in Data folder.

### Citation

```bibtex
@inproceedings{fomicheva2016cobaltf,
  title={CobaltF: a fluent metric for MT evaluation},
  author={Fomicheva, Marina and Bel Rafecas, N{\'u}ria and Specia, Lucia and da Cunha Fanego, Iria and Malinovsiy, Anton},
  booktitle={The 54th Annual Meeting of the Association for Computational Linguistics. Proceedings of the First Conference on Machine Translation (WMT); 2016 Aug 7-12; Berlin, Germany},
  year={2016},
  pages={483--490},
  organization={ACL (Association for Computational Linguistics)}
}
```

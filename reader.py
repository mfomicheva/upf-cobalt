class Reader(object):

    @staticmethod
    def read_alignment_line(line):
        values = line.split(' : ')
        return [
            int(values[0].split(',')[0].replace('[', '')),
            int(values[0].split(',')[1].replace(']', '')),
            float(values[2])
        ]

    def read(self, alignment_file):
        phrase = 0

        alignments = {}

        for line in open(alignment_file):
            if line.startswith('Sentence #'):
                phrase = int(line.replace('Sentence #', ''))
                if phrase > 1:
                    alignments[phrase - 1] = [alignment, [], similarities]
                alignment = []
                similarities = []
            else:
                values = Reader.read_alignment_line(line)
                alignment.append([values[0], values[1]])
                similarities.append(values[2])

        alignments[phrase] = [alignment, [], similarities]

        return alignments
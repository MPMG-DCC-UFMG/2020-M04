'''
    Calculate the polarity of sentiment for English sentences.

    Dependencies:
        pip3 install --upgrade vaderSentiment
    Args:
        --text -t 'text'
        --file -f file.txt

    >>> python3 vader.py -t "i love you! :)"
    >>> python3 vader.py -f example.txt
        
'''

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from optparse import OptionParser

def checkText(text):
    analyzer = SentimentIntensityAnalyzer()
    analyse = analyzer.polarity_scores(text)
    compound = analyse["compound"]
    if compound < -0.05:
        return compound
    elif compound > 0.05:
        return compound
    else:
        return 0

def main():
    parser = OptionParser()
    parser.add_option('-f', '--filename', dest='filename')
    parser.add_option('-t', '--text', dest='text')
    options, args = parser.parse_args()

    if options.text:
        print(checkText(options.text))

    elif options.filename:
        F_out = open("results_" + options.filename, "w")
        with open(options.filename) as F:
            for text in F:
                F_out.write(text.strip() + "\t" + str(checkText(text)) + "\n")
        print("File results_" + options.filename + " successfully generated.")
        F_out.close()

if __name__ == '__main__':
    main()

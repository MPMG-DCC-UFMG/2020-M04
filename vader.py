'''
    Calculate the polarity of sentiment for English sentences.

    Dependencies:
        pip3 install --upgrade vaderSentiment
        pip3 install nltk
        pip3 install pandas
    Args:
        --text -t 'text'
        --file -f file.txt

    >>> python3 vader.py -t "i love you! :)"
    >>> python3 vader.py -f example.txt
        
'''

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from optparse import OptionParser
import json
import pandas as pd
import nltk
import logging
from nltk.tokenize.punkt import PunktSentenceTokenizer

# Calculates VADER score for given sentence
def vaderScore(text):
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
    # Define data option
    parser = OptionParser()
    parser.add_option('-f', '--filename', dest='filename')
    parser.add_option('-t', '--text', dest='text')

    try:
        (options, args) = parser.parse_args()
    except SystemExit:
        logging.error("BadOptionError")
        return

    # Handle --text option and calculate sentiment score for the given text
    if options.text:
        logging.info('Perform VADER sentiment analysis for --text "%s"', options.text)
        data = dict()
        data['polarity'] = {'score':vaderScore(options.text), 'ranking':pd.cut([vaderScore(options.text)], bins=[-1,-0.5,-0.05,0.05,0.5,1],labels=['Extremely Negative','Negative', 'Neutro', 'Positive', 'Extremely Positive'])[0]}
        logging.info(str(data))

    # Handle --filename option
    elif options.filename:
        logging.info('Perform VADER sentiment analysis for --filename %s', options.filename)

        try:
            input_file = open(options.filename)
        except Exception as e:
            logging.error("Exception occurred", exc_info=True)
            return

        # Read text from the input file
        input_text = input_file.read()
        # Open output file
        output_file = open("results_" + options.filename.replace(".txt",".json"), "w")
        output_file.write('[')
        # Define dictionary to keep data output
        data = dict()

        # Iterate thorough the sentences and calculate sentiment scores for each one
        for start, end in PunktSentenceTokenizer().span_tokenize(input_text):
            length = end - start
            text = input_text[start:end]
            data['sentence'] = text
            data['position'] = {'start': start, 'end': end, 'length': length}
            data['polarity'] = {'score':vaderScore(text), 'ranking':pd.cut([vaderScore(text)], bins=[-1,-0.5,-0.05,0.05,0.5,1],labels=['Extremely Negative','Negative', 'Neutro', 'Positive', 'Extremely Positive'])[0]}
            json.dump(data, output_file, indent=2)
            if end != (len(input_text) - 1):
                output_file.write(',\n')
            else:
                output_file.write('\n')

        output_file.write(']')
        output_file.close()
        logging.info("File results_" + options.filename.replace(".txt",".json") + " successfully generated")

if __name__ == '__main__':  
    logging.basicConfig(level=logging.DEBUG, filename='M04.log', filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

    main()

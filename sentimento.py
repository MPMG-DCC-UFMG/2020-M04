from optparse import OptionParser
from enelvo import normaliser
import subprocess
import shlex
import os.path
import sys
import pandas as pd
import re
import nltk
import json

# NLTK's data collection includes a trained model for Portuguese sentence segmentation
stok = nltk.data.load('tokenizers/punkt/portuguese.pickle')

# https://pypi.org/project/sentistrength/
class PySentiStr:
    def __init__(self):
        pass
        
    def setSentiStrengthPath(self, ss_Path):
        self.SentiStrengthLocation = ss_Path

    def setSentiStrengthLanguageFolderPath(self, sslf_Path):
        # Ensure it has a forward slash at the end
        if sslf_Path[-1] != '/':
            sslf_Path += '/'
        self.SentiStrengthLanguageFolder = sslf_Path

    def getSentiment(self, df_text, score='scale'):
        if not hasattr(self, 'SentiStrengthLocation'):
            assert False, "Set path using setSentiStrengthPath(path) function."

        if not hasattr(self, 'SentiStrengthLanguageFolder'):
            assert False, "Set path using setSentiStrengthLanguageFolderPath(path) function."
        if type(df_text) != pd.Series:
            df_text = pd.Series(df_text)
        df_text = df_text.str.replace('\n','')
        df_text = df_text.str.replace('\r','')
        conc_text = '\n'.join(df_text)
        p = subprocess.Popen(shlex.split("java -jar '" + self.SentiStrengthLocation + "' stdin sentidata '" + self.SentiStrengthLanguageFolder + "' trinary"),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        b = bytes(conc_text, 'utf-8')
        stdout_byte, stderr_text = p.communicate(b)
        stdout_text = stdout_byte.decode("utf-8")
        stdout_text = stdout_text.rstrip().replace("\t"," ")
        stdout_text = stdout_text.replace('\r\n','')
        senti_score = stdout_text.split(' ')
     
        senti_score = list(map(float, senti_score))        

        senti_score = [int(i) for i in senti_score]
        if score == 'scale': # Returns from -4 to 4
            senti_score = [sum(senti_score[i:i+2]) for i in range(0, len(senti_score), 3)]
        elif score == 'binary': # Return 1 if positive and -1 if negative
            senti_score = [1 if senti_score[i] >= abs(senti_score[i+1]) else -1 for i in range(0, len(senti_score), 3)]
        elif score == 'trinary': # Return Positive and Negative Score and Neutral Score
            senti_score = [tuple(senti_score[i:i+3]) for i in range(0, len(senti_score), 3)]
        elif score == 'dual': # Return Positive and Negative Score
            senti_score = [tuple(senti_score[i:i+2]) for i in range(0, len(senti_score), 3)]
        else:
            return "Argument 'score' takes in either 'scale' (between -1 to 1) or 'binary' (two scores, positive and negative rating)"
        return senti_score

def sentistrengthClassifier():
    senti = PySentiStr()
    senti.setSentiStrengthPath('sentistrength/SentiStrength.jar')
    senti.setSentiStrengthLanguageFolderPath('sentistrength/portugueseLexicon_modified')
    return senti

def getSplitSentences(text):
    text = text.replace("\\n", ". ")
    text = text.replace('u.u', 'XXHAPPYXX')

    #adding a white space after the punctuation (. ? and !) followed by any word + word except [.]
    text = re.sub(r'(?<=[\w\s][?.!])(?=[\w][^.])', r' ', text)
    text = text.replace('XXHAPPYXX', 'u.u')
    return stok.tokenize(text)

def getArrayJsonSentences(complete_text):
    labeled_sentence = []
    classifier = sentistrengthClassifier()
    # complete_text = complete_text.lower()

    for sentence_text in getSplitSentences(complete_text):
        sentence_value = dict()
        length = len(sentence_text)
        sentence_value['text'] = sentence_text

        #get position of sentence
        i_start = complete_text.index(sentence_text)
        i_end = i_start + len(sentence_text)
        sentence_value['position'] = {'start': i_start, 'end': i_end, 'length': length}
        
        #execute lexicon methods
        try:
            ranking = classifier.getSentiment(sentence_text, score='scale')[0]
            
            if ranking > 2:
                polarity = "Muito Positivo"
            elif ranking > 0:
                polarity = "Positivo"
            elif ranking < -2:
                polarity = "Muito Negativo"
            elif ranking < 0:
                polarity = "Negativo"
            else:
                polarity = "Neutro"
        except Exception as e:
            ranking = ""
            polarity = ""
            pass        

        sentence_value['ranking'] = ranking
        sentence_value['polarity'] = polarity
        labeled_sentence.append(sentence_value)

    return labeled_sentence

def main():
    # Define data option
    parser = OptionParser()
    parser.add_option('-f', '--filename', dest='filename')
    parser.add_option('-t', '--text', dest='text')

    # Check user option
    try:
        (options, args) = parser.parse_args()
    except SystemExit:
        return

    # Define classifier
    classifier = sentistrengthClassifier()

    
    # Creates a normaliser object with default attributes.
    norm = normaliser.Normaliser()
    norm.capitalize_inis = True
    norm.capitalize_acrs = True
    norm.capitalize_pns = True
    
    # Handle user option
    if options.text:
        try:
            # Get an array for each sentence in the original text
            labeled_sentence = getArrayJsonSentences(options.text)
            data_output = dict()
            data_output['sentences'] = labeled_sentence

            # Print output
            print(json.dumps(data_output))

        except Exception as e:
            print(e)
            return
    elif options.filename:
        try:    
            # Read text from the input file
            text = open("data/input/" + options.filename).read()

            # Open Output file
            output_file = open("data/output/results_" + options.filename.split(".")[0] + ".json", "w")

            # Get an array for each sentence in the original text
            labeled_sentence = getArrayJsonSentences(text)
            data_output = dict()
            data_output['sentences'] = labeled_sentence

            # Print output
            output_file.write(json.dumps(data_output, indent = 2, ensure_ascii = False))

        except Exception as e:
            print(e)
            return


if __name__ == '__main__':
    main()

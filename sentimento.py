from optparse import OptionParser
from enelvo import normaliser
import subprocess
import shlex
import os.path
import sys
import pandas as pd
import re
import nltk
import os
import json

# NLTK's data collection includes a trained model for Portuguese sentence segmentation
stok = nltk.data.load('tokenizers/punkt/portuguese.pickle')

# Creates a normaliser object with default attributes.
norm = normaliser.Normaliser()
norm.capitalize_inis = True
norm.capitalize_acrs = True
norm.capitalize_pns = True

# SentiStrength main class (https://pypi.org/project/sentistrength/)
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

def getSentimentResults(text):
    # Define classifier
    classifier = PySentiStr()
    classifier.setSentiStrengthPath('sentistrength/SentiStrength.jar')
    classifier.setSentiStrengthLanguageFolderPath('sentistrength/portugueseLexicon_modified')

    # Get ranking and polarity for normalized text
    try:
        ranking = classifier.getSentiment(norm.normalise(text), score='scale')[0]
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
    return ranking, polarity

def getArrayJsonSentences(complete_text):
    labeled_sentence = []

    for sentence_text in getSplitSentences(complete_text):
        sentence_value = dict()
        length = len(sentence_text)
        sentence_value['text'] = sentence_text

        #get position of sentence
        i_start = complete_text.index(sentence_text)
        i_end = i_start + len(sentence_text)
        sentence_value['position'] = {'start': i_start, 'end': i_end, 'length': length}
        
        #execute lexicon methods
        ranking, polarity = getSentimentResults(sentence_text)

        sentence_value['ranking'] = ranking
        sentence_value['polarity'] = polarity
        labeled_sentence.append(sentence_value)

    return labeled_sentence

def getSplitSentences(text):
    text = text.replace("\\n", ". ")
    text = text.replace('u.u', 'XXHAPPYXX')

    # Add white space after the punctuation (. ? and !) followed by any word + word except [.]
    text = re.sub(r'(?<=[\w\s][?.!])(?=[\w][^.])', r' ', text)
    text = text.replace('XXHAPPYXX', 'u.u')
    return stok.tokenize(text)

def main():
    # Define data option
    parser = OptionParser()
    parser.add_option('-f', '--filename', dest='filename')
    parser.add_option('-t', '--text', dest='text')
    parser.add_option('-i', '--instagram', dest='instagram')
    parser.add_option('-w', '--whatsapp', dest='whatsapp')

    # Check user option
    try:
        (options, args) = parser.parse_args()
    except SystemExit:
        return
    
    # Handle user option
    if options.text:
        try:
            # Get an array for each sentence in the original text
            ranking, polarity = getSentimentResults(options.text)
            print(ranking, polarity)

        except Exception as e:
            print(e)
            return

    elif options.filename:
        try:
            # Set directory and filename
            _file = options.filename.split("/")[-1]
            directory = "/".join(options.filename.split("/")[0:-1]) + "/"
            directory = "/datalake/ufmg/m04/files" + directory

            # Create directory if it does not exist
            os.makedirs(os.path.dirname(directory), exist_ok=True)

            # Read text from the input file
            text = open(options.filename).read()

            # Open Output file
            output_file = open(directory + _file, "w")

            # Get an array for each sentence in the original text
            labeled_sentence = getArrayJsonSentences(text)
            data_output = dict()
            data_output['sentences'] = labeled_sentence

            # Write output
            output_file.write(json.dumps(data_output, indent = 2, ensure_ascii = False))

            # Close Output file
            output_file.close()

        except Exception as e:
            print(e)
            return

    elif options.instagram:
        try:
            # Set directory and filename
            directory = options.instagram.replace("/datalake/ufmg/crawler/instagram/", "")
            directory = "/datalake/ufmg/m04/instagram/" + directory
            _file = directory.split("/")[-1]
            directory = "/".join(directory.split("/")[0:-1]) + "/"

            # Create directory if it does not exist
            os.makedirs(os.path.dirname(directory), exist_ok=True)

            # Open Output file
            output_file = open(directory + _file, "w")

            # Read file from the directory
            txt_file = open(options.instagram).read().split("\n")
            qntd = 0
            for entry in txt_file:
                if len(entry) == 0:
                    continue
                qntd = qntd + 1
                entry = json.loads(entry)
                if 'text' in entry:
                    ranking, polarity = getSentimentResults(entry['text'])
                    entry["sentiment"] = {"ranking": ranking, "polarity": polarity}
                if qntd < (len(txt_file) - 1):
                    output_file.write(json.dumps(entry) + "\n")
                else:
                    output_file.write(json.dumps(entry))
                print("Processed", qntd, "out of", len(txt_file) - 1)

            # Close Output file
            output_file.close()

        except Exception as e:
            print(e)
            return

    elif options.whatsapp:
        try:
            # Set directory and filename
            directory = options.whatsapp.replace("/datalake/ufmg/crawler/whatsapp/", "")
            directory = "/datalake/ufmg/m04/whatsapp/" + directory
            _file = directory.split("/")[-1]
            directory = "/".join(directory.split("/")[0:-1]) + "/"

            # Create directory if it does not exist
            os.makedirs(os.path.dirname(directory), exist_ok=True)

            # Open Output file
            output_file = open(directory + _file, "w")

            # Read file from the directory
            txt_file = open(options.whatsapp).read().split("\n")
            qntd = 0
            for entry in txt_file:
                if len(entry) == 0:
                    continue
                qntd = qntd + 1
                entry = json.loads(entry)
                if 'content' in entry:
                    ranking, polarity = getSentimentResults(entry['content'])
                    entry["sentiment"] = {"ranking": ranking, "polarity": polarity}
                if qntd < (len(txt_file) - 1):
                    output_file.write(json.dumps(entry) + "\n")
                else:
                    output_file.write(json.dumps(entry))
                print("Processed", qntd, "out of", len(txt_file) - 1)

            # Close Output file
            output_file.close()

        except Exception as e:
            print(e)
            return


if __name__ == '__main__':
    main()

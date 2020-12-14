from kafka import KafkaConsumer, KafkaProducer
from optparse import OptionParser
import subprocess
import shlex
import os.path
import sys
import pandas as pd
import re
import nltk
import os
import json
import operator
from json import dump
import time
from random import randint

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

        df_text = df_text.str.replace('!','.')
        df_text = df_text.str.replace('?','.')

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
    # Verify whether it is an ad post
    neutralWords = ["promocao", "promoção", "promocão", "promoçao", "concorr", "venda", "promo", "frete", "premi", "prêmi"]
    for i in neutralWords:
        if i in neutralWords:
            if i in text.lower():
                return 0, "Neutro"

    # Verify whether it contains neg/pos emojis
    for i in negEmojis:
        text = text.replace(i, ":(")
    for i in posEmojis:
        text = text.replace(i, ":)")


    # Get ranking and polarity for normalized text
    try:
        ranking = classifier.getSentiment(text, score='scale')[0]
        
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
    # Add white space after the punctuation (. ? and !) followed by any word + word except [.]
    text = re.sub(r'(?<=[\w\s][?.!])(?=[\w][^.])', r' ', text)
    text = text.replace("\\n", ". ")
    return stok.tokenize(text)

# Define classifier
classifier = PySentiStr()
classifier.setSentiStrengthPath('sentistrength/SentiStrength.jar')
classifier.setSentiStrengthLanguageFolderPath('sentistrength/portugueseLexicon_modified_final')

# NLTK's data collection includes a trained model for Portuguese sentence segmentation
stok = nltk.data.load('tokenizers/punkt/portuguese.pickle')

# Read neg/pos emojis
negEmojis = list()
posEmojis = list()
with open("sentistrength/portugueseLexicon_modified_final/negEmoji.txt") as f:
    for line in f:
        negEmojis.append(line.strip())
with open("sentistrength/portugueseLexicon_modified_final/posEmoji.txt") as f:
    for line in f:
        posEmojis.append(line.strip())

def main():
    # Define data option
    parser = OptionParser()
    parser.add_option('-t', '--text', dest='text')
    parser.add_option('-f', '--filename', dest='filename')
    parser.add_option('-c', '--crawler', dest='crawler')

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

    # Handle filename option
    elif options.filename:
        listFiles = args
        args.insert(0, options.filename)
        for filename in listFiles:
            try:
                # Set directory and filename
                _file = filename.split("/")[-1]
                directory = "/".join(filename.split("/")[0:-1]) + "/"
                directory = "/datalake/ufmg/m04/files" + directory

                # Create directory if it does not exist
                os.makedirs(os.path.dirname(directory), exist_ok=True)

                # Read text from the input file
                text = open(filename).read()

                # Open Output file
                output_file = open(directory + _file, "w")
                
                # Get an array for each sentence in the original text
                labeled_sentence = getArrayJsonSentences(text)
                
                # Get overall score for sentences
                ranking_scores = dict({-4:0, -3:0, -2:0, -1:0, 0:0, 1:0, 2:0, 3:0, 4:0})
                for sentence in labeled_sentence:
                    ranking_scores[sentence['ranking']] += 1

                ranking_scores_translated = dict()
                ranking_scores_translated['Muito Negativo'] = ranking_scores[-4] + ranking_scores[-3]
                ranking_scores_translated['Negativo'] = ranking_scores[-2] + ranking_scores[-1]
                ranking_scores_translated['Neutro'] = ranking_scores[0]
                ranking_scores_translated['Positivo'] = ranking_scores[1] + ranking_scores[2]
                ranking_scores_translated['Muito Positivo'] = ranking_scores[3] + ranking_scores[4]

                # Output json
                data_output = dict()
                data_output['sentences'] = labeled_sentence
                data_output['text'] = {'ranking': ranking_scores, 'polarity': ranking_scores_translated, 'overall_polarity': max(ranking_scores_translated.items(), key=operator.itemgetter(1))[0]}

                # Write output
                output_file.write(json.dumps(data_output, indent = 2, ensure_ascii = False))

                # Close Output file
                output_file.close()

            except Exception as e:
                print(e)
                continue

    # Handle files from crawler
    elif options.crawler:

        try:
            consumerTopic = options.crawler # Get consumer topic
            producerTopic = args[0] # Get producer topic
            brokers = args[1].split(',') # Get brokers
            if len(args) > 2:
                groupId = args[2] # Get group id
            else:
                groupId = "group" + str(randint(0,100)) # Create random group id in case it is not given

            print('Group ID:', groupId)
            print('Consumer:', consumerTopic)
            print('Producer:', producerTopic)
            print('Brokers:', brokers)
        except Exception as e:
            print("Passagem de parâmetros incorreta. Consulte documentação para detalhes")
            return

        # brokers = ["hadoopdn-gsi-prod04.mpmg.mp.br:6667", "hadoopdn-gsi-prod05.mpmg.mp.br:6667", "hadoopdn-gsi-prod06.mpmg.mp.br:6667", "hadoopdn-gsi-prod07.mpmg.mp.br:6667", "hadoopdn-gsi-prod08.mpmg.mp.br:6667", "hadoopdn-gsi-prod09.mpmg.mp.br:6667", "hadoopdn-gsi-prod10.mpmg.mp.br:6667"]
        
        try:
            consumer = KafkaConsumer(consumerTopic, auto_offset_reset='latest', group_id=groupId, bootstrap_servers=brokers) # Initialize consumer
            producer = KafkaProducer(bootstrap_servers=brokers) # Initialize producer
        except Exception as e:
            print(e)
            return

        # Keep consumer alive
        while True:
            try:
                # Consume data from the topic
                message = consumer.poll()
                if not message:
                    time.sleep(5) # Sleep for 5 seconds
                    print("Sleeping for 5 seconds...")
                else:
                    for i in message:
                        try:
                            for j in message[i]:
                                content = json.loads(j.value)
                                print(content)
                                if "texto" in content:
                                    postId = content["identificador"]
                                    text = content["texto"]
                                    ranking, polarity = getSentimentResults(text)
                                    output = {"identificador":postId, "sentiment":{"ranking":ranking, "polarity":polarity}}
                                    producer.send(producerTopic, str.encode(json.dumps(output)))
                        except Exception as e:
                            print(e)
                            continue
            except Exception as e:
                print(e)
                return
    else:
        return

if __name__ == '__main__':
    main()

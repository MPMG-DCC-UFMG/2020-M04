# M04: Análise de Sentimentos

## Descrição
Ferramenta para determinar se textos livres, a partir de um contexto, possuem conotação positiva, neutra ou negativa.

## How To
1 - Download _vader.py_. O código foi desenvolvido utilizando Python3 e é uma versão inicial do módulo, com a implementação do VADER (Valence Aware Dictionary and sEntiment Reasoner) para sentenças em Inglês. 

2 - Download bibliotecas necessárias.

    pip3 install --upgrade vaderSentiment
    pip3 install nltk
    pip3 install pandas
    
3 - Existem duas formas de executar o programa. A primeira recebe o argumento __-t__ (--text) e a segunda __-f__ (--file). Para o segundo caso, o programa recebe um texto corrido, sem a separação de sentenças por quebra de linha.

    python3 vader.py -t "this is an example."
    
    python3 vader.py -f example.txt
    
## Output
O módulo implementado gera um arquivo __results_fileName.json__ para um determinado __fileName.txt__ de entrada. O JSON possui a seguinte estrutura:

    [{
      "sentence": "I hate you!",
      "position": {
        "start": 0,
        "end": 11,
        "length": 11
      },
      "polarity": {
        "score": -0.6114,
        "ranking": "Extremely Negative"
      }
    }]

O arquivo JSON contém cada frase do texto separada, a posição dos caracteres de início (_start_) e término (_end_) no arquivo de entrada, o tamanho da sentença (_length_), a conotação encontrada (_score_) e um _ranking_ baseado na conotação (_Extremely Negative, Negative, Neutro, Positive, Extremely Positive_).

O programa gera ainda um arquivo __M04.log__ contendo as informações de logging referentes as execuções do mesmo. Caso o usuário opte pela entrada de texto (--text), o arquivo de log armazena os dados da sentença e os resultados correspondentes.

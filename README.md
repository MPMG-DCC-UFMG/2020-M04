# M04: Análise de Sentimentos

## Descrição
Ferramenta para determinar se textos livres em Português, a partir de um contexto, possuem conotação positiva, neutra ou negativa.

## How To
1 - O código foi desenvolvido utilizando Python3 e é uma versão inicial do módulo de sentimentos para sentenças em Português. Para utilizá-lo, basta clonar o repositório para uma pasta local.
    
    git clone https://github.com/MPMG-DCC-UFMG/M04

2 - Instalação de bibliotecas necessárias.

    pip3 install -r enelvo/requirements.txt
    pip3 install nltk
    pip3 install pandas
    
3 - Existem duas formas de executar o programa. A primeira recebe o argumento __-t__ (--text) e a segunda __-f__ (--file). Para o segundo caso, o programa recebe um texto corrido, sem a separação de sentenças por quebra de linha.

    python3 sentimento.py -t "this is an example."
    
    python3 sentimento.py -f examplo.txt
    
## Output
O módulo implementado gera um arquivo __results_fileName.json__ para um determinado __fileName.txt__ de entrada. O JSON possui a seguinte estrutura:

    {
      "sentences": [
        {
          "text": "Café da manhã incrível, com opções  quentes saborosas, frutas diversas e bolos gostosos!",
          "position": {
            "start": 2901,
            "end": 2988,
            "length": 87
          },
          "ranking": 4,
          "polarity": "Muito Positivo"
        }
      ]
    }

O arquivo JSON contém cada frase do texto separada, a posição dos caracteres de início (_start_) e término (_end_) no arquivo de entrada, o tamanho da sentença (_length_), a conotação encontrada (_ranking_) e a _polarity_ baseada na conotação (_Muito Negativo, Negativo, Neutro, Positivo, Muito Positivo_).

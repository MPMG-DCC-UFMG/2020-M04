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
    
É importante verificar se o Punkt Tokenizer Model já está presente. Caso contrário, inicie o python3 e instale-o da seguinte forma:

    import nltk
    nltk.download("punkt")
    
3 - Existem quatro formas de executar o programa. A primeira recebe o argumento __-t__ (--text) e a segunda __-f__ (--file). Para o segundo caso, o programa recebe um texto corrido, sem a separação de sentenças por quebra de linha. Os argumentos __-i__ (--instagram) e __-w__ (--whatsapp) são utilizados para o processamento de arquivos gerados pelos coletores de instagram e whatsapp, respectivamente. O _script_ sentimento.py e os outros arquivos necessrios para a execução do programa estão localizados no diretório _/dados01/workspace/ufmg.m04dcc/M04_ .

    python3 sentimento.py -t "Estou muito feliz :)"
    
    python3 sentimento.py -f examplo.txt
    
    python3 sentimento.py -i [fonte]
    
    python3 sentimento.py -w [fonte]
    
## Output
O módulo executado com o argumento __-t__ retorna diretamente no _console_ a conotação encontrada (_ranking_) e a polaridade (_polarity_) baseada na conotação (_Muito Negativo, Negativo, Neutro, Positivo, Muito Positivo_) para a sentença requerida. O resultado do processametno dos outros argumentos são armazenados dentro no diretório _/datalake/ufmg/m04/_ .

A execuço do módulo com o argumento __-f__ para um determinado __[fonte]/fileName.txt__ de entrada gera um arquivo JSON de mesmo nome no diretório _/datalake/ufmg/m04/[fonte]/_. O JSON possui a seguinte estrutura:

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

O arquivo JSON contém cada frase do texto separada, a posição dos caracteres de início (_start_) e término (_end_) no arquivo de entrada, o tamanho da sentença (_length_), a conotação encontrada (_ranking_) e a _polarity_ baseada na conotação.

No caso dos argumentos referentes ao whatsapp e instagram, os arquivos JSONs com o resultado do processamento são salvos em /datalake/ufmg/m04/[fonte], onde [fonte] é a estrutura do diretório de entrada utilizado (ex de entrada: /datalake/ufmg/crawler/instagram/1592484906/..., ex de saida: /datalake/ufmg/m04/instagram/1592484906/...). No caso, os JSONs de entrada são replicados e o parâmetro "sentimento" é adicionado. 

Exemplo de retorno para comentário extraído do Instagram. A polaridade foi calculada baseada no parâmetro "text" do JSON.

    {"text": "Bora @ariel_triatleta", "created_time": 1592400295, "created_time_str": "2020-06-17 10:24:55", "media_code": "CBgy_mRJnyH", "id": "17849543501112303", "owner_username": "jpbrag", "owner_id": "47973234", "tags": [], "mentioned_usernames": ["ariel_triatleta"], "sentiment": {"ranking": 0, "polarity": "Neutro"}}

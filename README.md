# M04: Análise de Sentimentos

## Descrição
Ferramenta para determinar se textos livres em Português possuem conotação positiva, neutra ou negativa. Módulo adaptado para receber texto livre e textos/comentários de redes sociais.

## Instalação e Execução

### Padrão (Python3)
1 - O código foi desenvolvido utilizando Python3 e sua execução pode ser realizada a partir da sequência de passos descrita a seguir. Primeiramente, para utilizá-lo, basta clonar o repositório para uma pasta local.
    
    git clone https://github.com/MPMG-DCC-UFMG/M04

2 - Em seguida, realize a instalação das bibliotecas necessárias. Para acessar lista completa de requisitos a instalar, ver _requirements.txt_.

    pip3 install -r enelvo/requirements.txt
    pip3 install nltk
    pip3 install pandas
    pip3 install kafka-python
    
É importante verificar se o Punkt Tokenizer Model já está presente. Caso contrário, inicie o python3 e instale-o da seguinte forma:

    import nltk
    nltk.download("punkt")
    
3 - Existem três formas de executar o programa, descritas a seguir. O _script_ sentimento.py e os outros arquivos necessrios para a execução do programa estão localizados no diretório _/dados01/workspace/ufmg.m04dcc/M04_ .

A primeira maneira recebe o argumento __-t__ (--text) para verificar a polaridade de sentenças passadas por parâmetro. O texto deve estar entre aspas. É um exemplo de execução.

    python3 sentimento.py -t "Estou muito feliz :)"

A segunda maneira recebe o argumento __-f__ (--file). Neste segundo caso, o programa recebe um texto corrido, sem a separação de sentenças por quebra de linha. Pode receber ainda múltiplos arquivos por parâmetro. São exemplos de execução.
    
    python3 sentimento.py -f [fonte]/examplo.txt
    
    python3 sentimento.py -f [fonte]/examplo.txt [fonte]/examplo_2.txt [fonte]/examplo_3.txt [...]
    
Finalmente, a terceira maneira recebe o argumento __-c__ (--crawler). Este argumento foi criado especificamente para atender às necessidades de integração do módulo de sentimentos com os coletores de redes sociais. Esta chamada recebe ainda como parâmetro o tópico consumidor, produtor, um (ou uma lista) _broker_ e o identificador do grupo (opcional). O padrão genérico de execução é apresentado a seguir.

    python3 sentimento.py -c consumerTopic producerTopic host1:port1,host2:port2,....,hostN:portN groupId
    
Os três primeiros parâmetros são mandatórios. Se o identificador do grupo (quarto parâmetro) não for informado, um identificador de grupo aleatório será utilizado. Um exemplo de execução é mostrado a seguir. A partir desta execução, M04 irá consumir do tópico _crawler_telegram_mensagem_ e produzir no tópico _model_analise_sentimento_telegram_mensagem_, utilizando como _brokers_ os endereços _hadoopdn-gsi-prod04.mpmg.mp.br:6667_ e _hadoopdn-gsi-prod05.mpmg.mp.br:6667_. Um identificador de grupo aleatório é utilizado neste exemplo.

    python3 sentimento.py -c crawler_telegram_mensagem model_analise_sentimento_telegram_mensagem hadoopdn-gsi-prod04.mpmg.mp.br:6667,hadoopdn-gsi-prod05.mpmg.mp.br:6667
    
### Docker
É possível encapsular todo o processo de execução em containers do Docker. A instalação e ativação ocorreu a partir da execução dos seguintes comandos.

    sudo yum-config-manager --setopt="docker-ce-stable.baseurl=https://download.docker.com/linux/centos/7/x86_64/stable" --save
    sudo yum install docker-ce docker-ce-cli containerd.io
    sudo yum install -y http://mirror.centos.org/centos/7/extras/x86_64/Packages/container-selinux-2.107-3.el7.noarch.rpm
    sudo yum install -y https://download.docker.com/linux/centos/7/x86_64/stable/Packages/containerd.io-1.2.6-3.3.el7.x86_64.rpm
    sudo yum install -y docker-ce docker-ce-cli
    sudo systemctl enable docker.service
    sudo systemctl start docker.service

Com o Docker ativo e o usuário dentro da pasta M04/, onde estão localizados os arquivos Dockerfile e docker-compose.yml, para instalar os recursos necessários para a execução do módulo e as suas dependências, execute o seguinte comando (caso já não o tenha feito). Com isso, o módulo de sentimentos estará pronto para utilização.

    sudo docker-compose build
    
Com a instalação finalizada, os scripts do módulo de sentimentos estarão localizados em um container que se chama "m04_sentimento_python". A utilização do coletor com o Docker se diferencia um pouco da utilização normal de scripts Python supracitados. Dessa forma, o módulo pode ser executado das seguintes formas, por exemplo, a partir do uso dos três parâmetros distintos supracitados. O parâmetro -u após python3 em um dos exemplos é apenas para não armazenar saídas do teclado em _buffer_ e sim imprimir os resultados direto na tela.   

    sudo docker run --rm m04_sentimento_python python3 sentimento.py -t "Estou feliz :)"
    
    sudo docker run -v /datalake/ufmg/:/datalake/ufmg/ --rm m04_sentimento_python python3 sentimento.py -f /datalake/ufmg/m04/input/exemplo_input.txt
    
    sudo docker run --rm m04_sentimento_python python3 -u sentimento.py -c crawler_telegram_mensagem model_analise_sentimento_telegram_mensagem hadoopdn-gsi-prod04.mpmg.mp.br:6667,hadoopdn-gsi-prod05.mpmg.mp.br:6667
    
## Saídas
O módulo executado com o argumento __-t__ retorna diretamente no _console_ a conotação encontrada (_ranking_) e a polaridade (_polarity_) baseada na conotação (_Muito Negativo, Negativo, Neutro, Positivo, Muito Positivo_) para a sentença requerida. O resultado do processametno dos outros argumentos são armazenados dentro no diretório _/datalake/ufmg/m04/_ .

A execuço do módulo com o argumento __-f__ para um determinado __[fonte]/fileName.txt__ de entrada gera um arquivo JSON de mesmo nome no diretório _/datalake/ufmg/m04/files/[fonte]/_. O JSON possui a seguinte estrutura:

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
      ],
      "text": {
        "ranking": {
          "-4": 0,
          "-3": 0,
          "-2": 0,
          "-1": 0,
          "0": 0,
          "1": 0,
          "2": 0,
          "3": 0,
          "4": 1
        },
        "polarity": {
          "Muito Negativo": 0,
          "Negativo": 0,
          "Neutro": 0,
          "Positivo": 0,
          "Muito Positivo": 1
        },
        "overall_polarity": "Neutro"
      }
    }

O arquivo JSON contém cada frase do texto separada dentro do subgrupo _sentences_, a posição dos caracteres de início (_start_) e término (_end_) no arquivo de entrada, o tamanho da sentença (_length_), a conotação encontrada (_ranking_) e a _polarity_ baseada na conotação. Dentro do subgrupo _text_, os resultados considerando o texto de todo arquivo (não apenas as sentenças) são levados em conta, onde _ranking_ e _polarity_ apresentam o número de sentenças com os referidos  scores, e _overall_polarity_ determina a polaridade geral do texto.

No caso dos argumentos da execução utilizando o argumento __-c__, é escrito no tópico do Kafka o _id_ da mensagem recebida do consumidor, e ranking e a polaridade referente a mensagem. O JSON possui a seguinte estrutura:

    {
      "identificador": 123890,
      "sentiment": {
        "ranking": 2,
        "polarity": "Positivo"
      }
    }

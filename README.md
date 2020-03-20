# M04: Análise de Sentimentos

## Descrição
Ferramenta para determinar se textos livres, a partir de um contexto, possuem conotação positiva, neutra ou negativa.

## How To
1 - Download _vader.py_. O código foi desenvolvido utilizando Python3 e é uma versão inicial do módulo, com a implementação do VADER (Valence Aware Dictionary and sEntiment Reasoner) para sentenças em Inglês. 

2 - Download bibliotecas necessárias.

    pip3 install --upgrade vaderSentiment
    
3 - Existem duas formas de executar o programa. A primeira recebe o argumento __-t__ (--text) e a segunda __-f__ (--file). Para o segundo caso, o arquivo de entrada deve conter uma sentença por linha.

    python3 vader.py -t "this is an example."
    
    python3 vader.py -f example.txt
    
## Output
O módulo implementado retorna [<-0.05), 0, (> 0.05].

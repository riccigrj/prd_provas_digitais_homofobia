# prd_provas_digitais_homofobia
Trabalho de Conclusão de Curso Ciência da Computação

Monitoramento do Twitter, a fim de coletar suas postagens, os tweets, que tenham menção a comunidade LGBTQIA+, de maneira que cada uma dessas postagens seja analisada e quando identificadas como um possível caso de homofobia é feita a sua evidenciação, para uma possível ação judicial. Para isso, é apresentado uma proposta de arquitetura que visa a identificação do possível infrator e a geração de evidências que possam comprovar a autoria da postagem. 

![Topologia](/topologia2.png)

- **create_lgbtqia_helper.py**

Script Python para a criação/deploy de toda a arquitetura.

- **conf.json**

Arquivo de configuração para a execução do script "create_lgbtqia_helper.py"

- **stack.json**

Cloud Formation para a criação da arquitetura na AWS.

- **lgbtqia-helper.py**

Script Python responsável pela inteligência de toda a arquitetura.

- **lgbtqia-streamer.conf**

Arquivo de configuração do Logstash para a coleta dos Tweets.

- **filter_logstash.rb**

Script Ruby utilizado para a adição do campo "word".

- **keywords.txt**

Palavras utilizadas na coleta dos Tweets.

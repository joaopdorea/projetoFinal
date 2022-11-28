# webScrapingFinance
Projeto desenvolvido para a matéria de Desenvolvimento Web 3, da universidade Unilasalle-RJ.

Objetivo do trabalho: fazer o cadastro de clientes, obtendo nome e email do cliente/usuário. Com essas informações, o cliente preenche o nome da empresa que ele quer fazer a cotação em tempo real do valor da ação, e também, receber alertas via email caso a ação esteja com um preço favorável, seja de compra ou venda da ação.

Funcionamento: foi utilizado o framework Django para fazer esse projeto. Nesse projeto foi abordado conceitos de WebScraping (Python), banco de dados(MySql) e interface web (Html/CSS).

O código do WebScraping foi programado no arquivo "views.py". Já o código da página Web foi feito no arquivo "home.html".

Obs.: Existe uma função (alerta()) no arquivo "views.py" que foi inserida como comentário. Caso seja retirada do comentário, o programa irá monitorar os preços das ações de meia em meia hora, e caso os preços estejam favoráveis de acordo com os limites que o cliente inseriu, o programa irá emitir alertas via email, para o email que a pessoa cadastrou na plataforma

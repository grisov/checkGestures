# NVDA Verificar Comandos de Entrada

* Autor: Oleksandr Gryshchenko
* Versão: 1.0
* Compatibilidade com NVDA: 2019.3 e seguintes
* Baixar [versão estável] [1]
* Baixar [versão de desenvolvimento] [2]

Encontre e corrija conflitos de comandos de entrada no NVDA e nos extras . O termo geral "comandos de entrada" inclui comandos de teclado, comandos inseridos em teclados Braille e comandos de ecrã sensíveis ao toque.
Cada um dos extras instalados pode fazer alterações na configuração do NVDA, adicionando ou reatribuindo comandos de entrada já existentes. Se os mesmos comandos de entrada estiverem vinculados a várias funções, será impossível chamar algumas delas.

## Procurar por comandos duplicados
Para detectar os comandos duplicados, chame o menu do NVDA, vá ao submenu "Ferramentas", a seguir - "Procurar Comandos de Entrada" e active o item de menu "Procurar comandos duplicados ...".
Depois disso, todos os comandos de entrada usados no NVDA serão verificados na seguinte ordem:

1. globalCommands;
2. globalPlugins.

Se comandos de entrada duplicados forem detectados,  atribuídos a funções diferentes, a sua lista será mostrada numa caixa de diálogo separada.
Depois de pressionar a tecla Enter no item da lista selecionado, a função do NVDA correspondente será seleccionada e aberta na caixa de diálogo "Gestor de comandos", onde  pode excluir ou reatribuir o comando associado.

Observação: como sabe, os recursos que não tenham uma descrição de texto não aparecem na caixa de diálogo "Gestor de Comandos". Portanto, após a activação de tal elemento, o aviso correspondente será mostrado.

## Comandos sem descrição
Para ver a lista de comandos vinculados a funções sem texto descritivo, caso se encontrem na configuração do NVDA, é necessário chamar o menu do NVDA, ir ao submenu "Ferramentas", depois - "Comandos sem descrição ...".
Tais recursos não aparecem na caixa de diálogo "Gestor de Comandos" padrão do NVDA, portanto ainda não é possível excluir ou reatribuir comandos a eles associados.

## Ajuda
Uma forma de ver esta página de ajuda é aceder ao menu do NVDA, ir ao submenu "Ferramentas", "Procurar Comandos de Entrada" e activar a "Ajuda".

Nota: Todos os recursos deste extra são apresentados na caixa de diálogo "Gestor de Comandos" do NVDA e  pode atribuir-lhe os seus próprios atalhos de teclado.

## Registo de alterações

### Versão 1.0
* pesquisa implementada para comandos de entrada duplicados;
* pesquisa implementada para comandos de entrada vinculados a funções sem uma descrição de texto.

## Alteração do código-fonte do complemento
Ppode clonar este repo para alterar os comandos de entrada de  do NVDA.

[1]: https://github.com/grisov/checkGestures/releases/download/latest/checkGestures-1.0.nvda-addon
[2]: https://github.com/grisov/checkGestures/releases/download/latest/checkGestures-1.0.1-dev.nvda-addon
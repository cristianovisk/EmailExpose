# EmailExpose

EmailExpose é uma ferramenta de linha de comando que verifica rapidamente se uma lista de e-mails foi exposta em vazamentos online. Proteja sua privacidade e segurança digital com essa solução eficiente e fácil de usar.

Os dados utilizados pela EmailExpose são retirados do site [Hotsheet](https://www.hotsheet.com/inoitsu/), uma fonte confiável de informações sobre vazamentos de dados na web.

Para utilizar a EmailExpose, basta fornecer uma lista de e-mails e deixar que a ferramenta faça o resto. Mantenha-se informado sobre possíveis exposições de dados e tome medidas proativas para proteger suas informações pessoais.

Instalação:

```shell
$ pip install email-expose
```

Exemplo de uso:

Sem output:

```shell
$ email_expose --file /home/user/EmailExpose/list_emails.txt
```

Com output:

```shell
$ email_expose --file /home/user/EmailExpose/list_emails.txt --output
Output file: output.xlsx
```
# Bot-admin
Bot-admin for telegram chat

Данный телеграм-бот написан на языке Python с использованием Aiogram. Бот выполняет функции модератора в чате или группе Telegram. Для запуска необходимо добавить бота администратором в группу. Управление ботом происходит через меню по команде "/admin". В текстовых файлах хранятся шаблоны сообщений бота, а также нецензурные слова для фильтрации (файл пустой, его нужно заполнить самим).

Функции:
  - Удаление системных сообщения (пользователь вступил/покинул группу, сообщение закреплено)
  - Удаление сообщений с нецензурными словами, рекламой, ссылками
  - Удаление повторяющихся одинаковых сообщений от пользователей
  - Удалив нежелательное сообщение, отправляет свое сообщение с предупреждением
  - Включение и отключение чата в определенное время суток и отправка соответствующего сообщения (в ночное время писать в группу нельзя)
  - Ограничение на отправку пользователями номеров телефонов
  - Лимит на добавление участников в час
  - Админка с возможностью управлять ботом, редактировать сообщения, отправляемые ботом, а также добавление списка пользователей, которым будет разрешена отправка рекламы.




This telegram bot is written in Python using Aiogram. The bot acts as a moderator in a Telegram chat or group. To start, you need to add the bot to the group as an administrator. The bot is controlled through the menu by the command "/admin". The text files contain templates of the bot's messages, as well as obscene words for filtering (the file is empty, you need to fill it in yourself).

Functions:
  - Deleting system messages (the user joined/left the group, the message is pinned)
  - Deleting messages with obscene words, advertising, links
  - Deleting duplicate identical messages from users
  - Having deleted an unwanted message, sends its own message with a warning
  - Enabling and disabling the chat at a certain time of day and sending a corresponding message (you cannot write to the group at night)
  - Restricting users from sending phone numbers
  - Limit on adding participants per hour
  - Admin panel with the ability to manage the bot, edit messages sent by the bot, and add a list of users who will be allowed to send advertising.

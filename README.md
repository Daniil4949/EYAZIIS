* Лаба ЕЯЗИС №1 бэк

* Команда для запуска

> python -m spacy download ru_core_news_sm
>
> python -m spacy download de_core_news_sm

> uvicorn --factory app:create_web_app 
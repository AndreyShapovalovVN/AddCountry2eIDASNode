# AddCountry2eIDASNode

Скрипт для добавления новых стран в конфигурацию eIDAS Node (Service и Connector), загрузки метаданных и обновления сертификатов/шифрования.

## Требования

- Python 3.9+
- Конфигурация eIDAS Node в каталоге `./eIDAS-conf/tomcat/`
- Установленные зависимости:

```bash
pip install -r requirements.txt
```

## Подготовка

1. Откройте `Node.py`.
2. В словаре `Node` добавьте страны в формате:

```python
Node = {
    "AT": "https://vidp.gv.at",
    "EE": "https://eidastest.eesti.ee",
}
```

Где ключ — код страны, значение — базовый URL удалённого eIDAS узла.

## Запуск

```bash
python eIDAS_add_country.py
```

## Что делает скрипт

Для каждой страны из `Node.py` скрипт:

- обновляет `MetadataFetcher` для Service и Connector;
- добавляет сертификаты (metadata/signature/encryption) в keystore;
- обновляет `encryptionConf.xml`;
- обновляет `eidas.xml` (для Service-конфигурации).

## Важно

- Перед запуском сделайте резервную копию файлов в `./eIDAS-conf/tomcat/`.
- Скрипт изменяет рабочие XML/properties-конфиги и keystore.

## Веб-сервис FastAPI для простой модели 

Веб-сервис FastAPI для [простой модели](https://github.com/DariaMishina/ML_HT) в рамках курса по прикладному питону в магистратуре НИУ ВШЭ по программе «Машинное обучение и высоконагруженные системы».

Сервис развернут на публичном хостинге render и доступен по [ссылке](https://fastapi-service-1n6d.onrender.com)
Доступные операции описаны в [сервисной документации](https://fastapi-service-1n6d.onrender.com/docs)

### образец для эндпоинта /predict_item выглядит так: 
```
{
  "name": "Toyota Corolla",
  "year": 2018,
  "selling_price": 12000,
  "km_driven": 50000,
  "fuel": "Petrol",
  "seller_type": "Individual",
  "transmission": "Manual",
  "owner": "First Owner",
  "mileage": "18.0 kmpl",
  "engine": "1496 CC",
  "max_power": "108 bhp @ 6000 rpm",
  "torque": "137 Nm @ 4400 rpm",
  "seats": 5
}
```

### образец для эндпоинта /predict_items 
хранится в файле test.csv


### для запуска в docker
 - создаем docker образ
```angular2html
docker build -t simple_model:latest .
```
- запускаем docker контейнер (порт 7290 для мэппинга выбран произвольно)
```angular2html
docker run -p 7290:80 simple_model:latest
```
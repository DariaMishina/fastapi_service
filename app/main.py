from fastapi import FastAPI, File, UploadFile
import pandas as pd
import numpy as np
from io import BytesIO
import time
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis
from config import REDIS_HOST, REDIS_PORT



from schemas import Item, Items, PingResponse
from utils import load_model, preprocess_data, save_csv_to_s3


app = FastAPI()

poly, scaler, model = load_model('poly_scaler_model.pkl')


@app.get("/ping/", response_model=PingResponse)
async def ping():
    return {"status": "Привет! Я микросервис и я живой."}

@app.get("/simple_test_cache")
@cache(expire=30)
def get_long_op():
    time.sleep(5)
    return "Представим, что это select * в огромной таблице без партиций"

# Здесь возвращаем список признаков, которые принимает модель для предсказания, они изменятся
@app.get("/features/")
@cache(expire=300)
def get_features():
    features = ["name", "year", "selling_price", "km_driven", "fuel", "seller_type", "transmission", "owner", "mileage", "engine", "max_power", "torque", "seats"]
    return {"features": features}


@app.post("/predict_item")
def predict_item(item: Item) -> float:
    new_data_df = preprocess_data(item)
    prediction = model.predict(new_data_df)
    return round(float(np.expm1(prediction)))


@app.post("/predict_items")
def predict_items(file: UploadFile):
    content = file.file.read()
    buffer = BytesIO(content)
    df = pd.read_csv(buffer, index_col=0)
    buffer.close()
    file.close()

    predictions = []
    for _, row in df.iterrows():
        # cоздаем объект Item из строки датафрейма
        item = Item(
            name=row.get('name', ''),
            year=row.get('year', 0),
            selling_price=row.get('selling_price', 0),
            km_driven=row.get('km_driven', 0),
            fuel=row.get('fuel', ''),
            seller_type=row.get('seller_type', ''),
            transmission=row.get('transmission', ''),
            owner=row.get('owner', ''),
            mileage=row.get('mileage', ''),
            engine=row.get('engine', ''),
            max_power=row.get('max_power', ''),
            torque=row.get('torque', ''),
            seats=row.get('seats', 0.0)
        )

        new_data_df = preprocess_data(item)
        prediction = model.predict(new_data_df)
        predictions.append(round(float(np.expm1(prediction))))

    df['predictions'] = predictions
    save_csv_to_s3(df, "predictions_output.csv")

@app.delete("/clear_cache")
async def clear_cache():
    redis_backend = FastAPICache._backend
    if isinstance(redis_backend, RedisBackend):
        await redis_backend.redis.flushdb()
        return {"message": "Кэш очищен, проверь в консоли: redis-cli и KEYS*."}
    else:
        return {"message": "что-то пошло не так, проверь запущен ли redis-server"}


@app.on_event("startup")
async def startup_event():
    redis = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")



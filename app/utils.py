import pandas as pd
import re
import boto3
import pickle
from io import StringIO
from config import S3_KEY_ID, S3_SECRET_KEY, S3_BUCKET


def save_csv_to_s3(csv_data, file_name):
    """
    Сохранение CSV файла в S3.
    """
    s3_resource = boto3.resource(
        service_name="s3",
        endpoint_url="https://storage.yandexcloud.net",
        aws_access_key_id=S3_KEY_ID,
        aws_secret_access_key=S3_SECRET_KEY,
    )

    try:
        csv_buffer = StringIO()
        csv_data.to_csv(path_or_buf=csv_buffer, index=False)
        s3_resource.Object(bucket_name=S3_BUCKET,
                           key=file_name).put(Body=csv_buffer.getvalue())
    except Exception as e:
        print(f"Ошибка при сохранении файла в Amazon S3: {e}")

def load_model(model_name):
    """
    Загрузка модели из S3.
    """
    s3_resource = boto3.resource(
        service_name="s3",
        endpoint_url="https://storage.yandexcloud.net",
        aws_access_key_id=S3_KEY_ID,
        aws_secret_access_key=S3_SECRET_KEY,
    )
    obj = s3_resource.Object(bucket_name=S3_BUCKET, key=model_name)

    pickle_byte_obj = obj.get()['Body'].read()
    poly, scaler, model = pickle.loads(pickle_byte_obj)
    return poly, scaler, model

poly, scaler, model = load_model('poly_scaler_model.pkl')

def extract_numeric(value):
    numeric_part = re.search(r'\d+\.\d+|\d+', str(value))
    return float(numeric_part.group()) if numeric_part else None


def preprocess_data(data):
    new_data = pd.DataFrame(data.dict(), index=[0])
    new_data['mileage'] = new_data['mileage'].apply(extract_numeric)
    new_data['engine'] = new_data['engine'].apply(extract_numeric)
    new_data['max_power'] = new_data['max_power'].apply(extract_numeric)
    new_data.drop(['torque'], axis=1, inplace=True)
    new_data[['mileage', 'engine', 'max_power', 'seats']] = new_data[
        ['mileage', 'engine', 'max_power', 'seats']].fillna(0)
    new_data['engine'] = new_data['engine'].astype('int')
    new_data['seats'] = new_data['seats'].astype('int')

    new_data = new_data.select_dtypes(exclude=['object'])
    new_data = new_data.drop('selling_price', axis=1)

    new_data_pl = poly.transform(new_data)
    new_data = pd.DataFrame(new_data_pl, index=new_data.index, columns=poly.get_feature_names_out(new_data.columns))

    new_data_scaled = scaler.transform(new_data)
    new_data_df = pd.DataFrame(new_data_scaled, index=new_data.index, columns=new_data.columns)
    return new_data_df
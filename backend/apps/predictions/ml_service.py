"""
Service xử lý dự đoán giá nhà — dùng model XGBoost đã huấn luyện
trong ml/models/best_model.pkl.
"""

import os
import joblib
import numpy as np
import pandas as pd
from django.conf import settings

MODEL_PATH = os.path.join(settings.BASE_DIR.parent, 'ml', 'models', 'best_model.pkl')

_saved = None
_model = None
_feature_names = None
_cat_cols = None
_num_cols = None
_log_transformed = False
_model_name = "unknown"

if os.path.exists(MODEL_PATH):
    _saved = joblib.load(MODEL_PATH)
    _model = _saved['model']
    _feature_names = _saved['feature_names']
    _cat_cols = _saved['cat_cols']
    _num_cols = _saved['num_cols']
    _log_transformed = _saved.get('log_transformed', False)
    _model_name = _saved.get('model_name', 'unknown')


def _extract_district_from_text(city, district):
    if district:
        return district.strip()
    return city.strip() if city else 'Khác'


def predict_price(area, frontage=None, access_road=None, floors=None,
                   bedrooms=0, bathrooms=0, legal_status=None,
                   furniture_state=None, city=None, district=None, **kwargs):
    """
    Input: các đặc trưng BĐS.
    Output: (predicted_price: float [đơn vị VNĐ], model_version: str)
    """
    if _model is None:
        raise RuntimeError(
            "Model AI chưa được train hoặc không tìm thấy file. "
            "Chạy notebook train_model.ipynb trong ml/notebooks/ trước."
        )

    area = float(area)
    frontage = float(frontage) if frontage else 0.0
    access_road = float(access_road) if access_road else 0.0
    floors = int(floors) if floors else 1
    bedrooms = int(bedrooms)
    bathrooms = int(bathrooms)
    legal_status = legal_status or 'Have certificate'
    furniture_state = furniture_state or 'Full'
    district_value = _extract_district_from_text(city, district)

    total_bed_bath = bedrooms + bathrooms

    row = {
        'District': district_value,
        'Legal status': legal_status,
        'Furniture state': furniture_state,
        'Area': area,
        'Frontage': frontage,
        'Access Road': access_road,
        'Floors': floors,
        'Bedrooms': bedrooms,
        'Bathrooms': bathrooms,
        'Frontage_Area_Ratio': frontage / (area + 1),
        'Total_Bed_Bath': total_bed_bath,
        'Rooms_per_Floor': total_bed_bath / (floors + 1),
    }

    input_df = pd.DataFrame([row])[_feature_names]

    pred = _model.predict(input_df)[0]

    if _log_transformed:
        pred = np.expm1(pred)

    # Dataset train có Price đơn vị TỶ VNĐ -> quy đổi ra VNĐ nguyên
    predicted_price_vnd = float(pred) * 1_000_000_000

    return round(predicted_price_vnd, -6), f"{_model_name}"
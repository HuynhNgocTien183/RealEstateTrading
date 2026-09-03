import os
import joblib
import numpy as np
import pandas as pd
from django.conf import settings

MODEL_PATH = os.path.join(settings.BASE_DIR.parent, 'ml', 'models', 'best_model.pkl')

_saved = None
_model = None
_feature_names = None
_model_name = "unknown"
_r2_score = None
_district_median_areas = {}

# dự phòng
DEFAULT_DISTRICT_MEDIAN_AREAS = {
    'Quận 1': 35.9, 'Quận 2': 77.0, 'Quận 3': 38.0, 'Quận 4': 40.0, 'Quận 5': 36.2,
    'Quận 6': 57.0, 'Quận 7': 64.0, 'Quận 8': 55.0, 'Quận 9': 79.0, 'Quận 10': 41.0,
    'Quận 11': 44.0, 'Quận 12': 66.0, 'Bình Thạnh': 50.0, 'Phú Nhuận': 42.0,
    'Tân Bình': 55.0, 'Tân Phú': 62.2, 'Gò Vấp': 60.0, 'Bình Tân': 60.5,
    'Thủ Đức': 70.0, 'Nhà Bè': 74.1, 'Hóc Môn': 92.0, 'Củ Chi': 141.6, 'Bình Chánh': 85.0,
    'Khác': 70.5
}

if os.path.exists(MODEL_PATH):
    try:
        _saved = joblib.load(MODEL_PATH)
        _model = _saved.get('model')
        _feature_names = _saved.get('features')
        _model_name = _saved.get('model_name', 'Voting Ensemble (LightGBM + CatBoost + XGBoost)')
        _r2_score = _saved.get('r2_score')
        # Tải từ điển trung vị diện tích thực tế được tính từ tập dữ liệu
        _district_median_areas = _saved.get('district_median_areas', DEFAULT_DISTRICT_MEDIAN_AREAS)
    except Exception as e:
        print(f"Lỗi khi tải mô hình ML: {e}")
        _district_median_areas = DEFAULT_DISTRICT_MEDIAN_AREAS


def _clean_text(val, default='Unknown'):
    if val and str(val).strip():
        return str(val).strip()
    return default


def predict_price(area, frontage=None, access_road=None, floors=None,
                  bedrooms=0, bathrooms=0, legal_status=None,
                  furniture_state=None, city=None, district=None, ward=None, **kwargs):
    if _model is None:
        raise RuntimeError(
            "Mô hình AI chưa được tải hoặc file models/best_model.pkl không tồn tại. "
            "Chạy notebook train.ipynb trước."
        )

    area = float(area)
    frontage = float(frontage) if frontage not in (None, '') else 4.0
    access_road = float(access_road) if access_road not in (None, '') else 5.0
    floors = int(floors) if floors not in (None, '', 0) else 1
    bedrooms = int(bedrooms) if bedrooms not in (None, '') else 2
    bathrooms = int(bathrooms) if bathrooms not in (None, '') else 2
    
    legal_status = _clean_text(legal_status, default='Have certificate')
    furniture_state = _clean_text(furniture_state, default='Full')
    district_clean = _clean_text(district, default='Gò Vấp')
    ward_clean = _clean_text(ward, default='Unknown')

    total_bed_bath = bedrooms + bathrooms
    floors_safe = max(1, floors)
    rooms_per_floor = total_bed_bath / floors_safe
    area_per_room = area / (total_bed_bath + 1)
    total_usable_area = area * floors_safe
    frontage_area_ratio = frontage / area if area > 0 else 0.0
    access_road_area_ratio = access_road / area if area > 0 else 0.0

    dist_median = _district_median_areas.get(district_clean, DEFAULT_DISTRICT_MEDIAN_AREAS.get(district_clean, 60.0))
    area_to_dist_med = area / dist_median if dist_median > 0 else 1.0
    
    location_group = f"{district_clean}_{ward_clean}"
    area_log = np.log1p(area)
    usable_area_log = np.log1p(total_usable_area)
    area_sq = area ** 2

    row = {
        'Area': area,
        'Frontage': frontage,
        'Access Road': access_road,
        'Floors': floors,
        'Bedrooms': bedrooms,
        'Bathrooms': bathrooms,
        'Total_Bed_Bath': total_bed_bath,
        'Rooms_per_Floor': rooms_per_floor,
        'Area_per_Room': area_per_room,
        'Total_Usable_Area': total_usable_area,
        'Frontage_Area_Ratio': frontage_area_ratio,
        'Access_Road_Area_Ratio': access_road_area_ratio,
        'Area_to_Dist_Med': area_to_dist_med,
        'Area_log': area_log,
        'Usable_Area_log': usable_area_log,
        'Area_sq': area_sq,
        'Legal status': legal_status,
        'Furniture state': furniture_state,
        'District': district_clean,
        'Ward': ward_clean,
        'Location_Group': location_group,
    }

    input_df = pd.DataFrame([row])
    if _feature_names:
        input_df = input_df[_feature_names]

    pred_log = _model.predict(input_df)[0]
    pred_billion_vnd = np.expm1(pred_log)  # Kết quả theo đơn vị tỷ VNĐ
    predicted_price_vnd = float(pred_billion_vnd) * 1_000_000_000

    return round(predicted_price_vnd, -6), _model_name
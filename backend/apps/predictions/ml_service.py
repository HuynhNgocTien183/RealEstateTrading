import os
import re
import joblib
import numpy as np
import pandas as pd
from django.conf import settings

ML_DIR = settings.BASE_DIR.parent / 'ml' / 'models'
MODEL_PATH_V3 = os.path.join(ML_DIR, 'best_model_v3.pkl')
MODEL_PATH_V2 = os.path.join(ML_DIR, 'best_model_v2.pkl')
MODEL_PATH_V1 = os.path.join(ML_DIR, 'best_model.pkl')

_saved = None
_model = None
_feature_names = None
_model_name = "unknown"
_r2_score = None
_district_median_areas = {}
_model_version = 1

DEFAULT_DISTRICT_MEDIAN_AREAS = {
    'Quận 1': 35.9, 'Quận 2': 77.0, 'Quận 3': 38.0, 'Quận 4': 40.0, 'Quận 5': 36.2,
    'Quận 6': 57.0, 'Quận 7': 64.0, 'Quận 8': 55.0, 'Quận 9': 79.0, 'Quận 10': 41.0,
    'Quận 11': 44.0, 'Quận 12': 66.0, 'Bình Thạnh': 50.0, 'Phú Nhuận': 42.0,
    'Tân Bình': 55.0, 'Tân Phú': 62.2, 'Gò Vấp': 60.0, 'Bình Tân': 60.5,
    'Thủ Đức': 70.0, 'Nhà Bè': 74.1, 'Hóc Môn': 92.0, 'Củ Chi': 141.6, 'Bình Chánh': 85.0,
    'Cần Giờ': 80.0, 'Khác': 70.5,
}

NAMED_DISTRICTS = {
    'thủ đức': 'Thủ Đức', 'thu duc': 'Thủ Đức',
    'gò vấp': 'Gò Vấp', 'go vap': 'Gò Vấp',
    'bình thạnh': 'Bình Thạnh', 'binh thanh': 'Bình Thạnh',
    'tân bình': 'Tân Bình', 'tan binh': 'Tân Bình',
    'tân phú': 'Tân Phú', 'tan phu': 'Tân Phú',
    'bình tân': 'Bình Tân', 'binh tan': 'Bình Tân',
    'phú nhuận': 'Phú Nhuận', 'phu nhuan': 'Phú Nhuận',
    'nhà bè': 'Nhà Bè', 'nha be': 'Nhà Bè',
    'bình chánh': 'Bình Chánh', 'binh chanh': 'Bình Chánh',
    'hóc môn': 'Hóc Môn', 'hoc mon': 'Hóc Môn',
    'củ chi': 'Củ Chi', 'cu chi': 'Củ Chi',
    'cần giờ': 'Cần Giờ', 'can gio': 'Cần Giờ',
}

PROJECT_RE = re.compile(r'Dự án|Vinhomes|Masteri|Opal|Celadon|Grand Park|The Beverly', re.I)
ALLEY_RE = re.compile(r'Hẻm|hẻm|hem\s', re.I)

def _try_load_model(path):
    if not os.path.exists(path):
        return None
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=DeprecationWarning)
            warnings.filterwarnings('ignore', category=UserWarning)
            saved = joblib.load(path)
        if not saved or not saved.get('model'):
            print(f"File mô hình không hợp lệ: {path}")
            return None
        print(f"Đã tải mô hình: {path} (version={saved.get('version')}, name={saved.get('model_name')})")
        return saved
    except Exception as e:
        print(f"Lỗi khi tải mô hình {path}: {e}")
        return None


def _apply_saved(saved):
    global _saved, _model, _feature_names, _model_name, _r2_score
    global _district_median_areas, _model_version
    _saved = saved
    if not saved:
        _model = None
        _district_median_areas = DEFAULT_DISTRICT_MEDIAN_AREAS
        return
    _model = saved.get('model')
    _feature_names = saved.get('features')
    _model_name = saved.get('model_name', 'unknown')
    _r2_score = saved.get('r2_score')
    _district_median_areas = saved.get('district_median_areas', DEFAULT_DISTRICT_MEDIAN_AREAS)
    _model_version = int(saved.get('version', 1))


def _ensure_model():
    global _saved, _model
    if _model is not None:
        return
    saved = _try_load_model(MODEL_PATH_V2)
    if saved and int(saved.get('version', 0)) != 2:
        print(f"Canh bao: {MODEL_PATH_V2} khong phai version 2 (got {saved.get('version')})")
    if saved is None:
        saved = _try_load_model(MODEL_PATH_V1)
    _apply_saved(saved)


_ensure_model()


def _clean_text(val, default='Unknown'):
    if val and str(val).strip():
        return str(val).strip()
    return default


def _to_optional_float(val):
    if val in (None, ''):
        return None
    return float(val)


def _to_optional_int(val, *, zero_as_missing=False):
    if val in (None, ''):
        return None
    number = int(val)
    if zero_as_missing and number == 0:
        return None
    return number


def _known_districts():
    saved = (_saved or {}).get('district_median_areas') or DEFAULT_DISTRICT_MEDIAN_AREAS
    return set(saved.keys())


def _normalize_district(name, default='Khác'):
    if name is None or str(name).strip() == '':
        return default
    s = str(name).strip()
    key = s.lower()
    if key in NAMED_DISTRICTS:
        s = NAMED_DISTRICTS[key]
    else:
        m = re.search(r'(?:quận|quan|q\.)\s*(\d{1,2})', s, flags=re.IGNORECASE)
        if m:
            n = int(m.group(1))
            if 1 <= n <= 12:
                s = f'Quận {n}'
        elif re.fullmatch(r'\d{1,2}', s):
            n = int(s)
            if 1 <= n <= 12:
                s = f'Quận {n}'
        elif len(s) > 20 or re.search(r'tỷ|gia|chỉ|phút|hđmb|hcm|tphcm', s, flags=re.IGNORECASE):
            s = 'Khác'
    if s not in _known_districts():
        return 'Khác'
    return s


def _normalize_ward(name):
    if name is None or str(name).strip() == '':
        return 'Unknown'
    s = str(name).strip()
    if re.fullmatch(r'\d{1,2}', s):
        return f'Phường {int(s)}'
    s = re.sub(r'\s*Quận\s+\d+.*$', '', s, flags=re.IGNORECASE).strip()
    return s if s else 'Unknown'


def _clean_street(street):
    s = str(street or '').strip()
    if not s or s.lower() in ('nan', 'none'):
        return 'Unknown'
    if re.search(r'nhựa|nhua|^\d+\s*m$', s, flags=re.IGNORECASE):
        return 'Unknown'
    s = re.sub(r'Dự án[^,]*(,|$)', '', s, flags=re.IGNORECASE)
    s = re.sub(r'^Hẻm\s*[\d./\-]+,?\s*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'^(Đường|Duong)\s+', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+', ' ', s).strip(' ,')
    return s if s else 'Unknown'


def _extract_street(address):
    parts = [p.strip() for p in str(address).strip().split(',') if p.strip()]
    return parts[0] if parts else 'Unknown'


def _extract_ward(address):
    parts = [p.strip() for p in str(address).strip().split(',') if p.strip()]
    if len(parts) >= 3:
        return _normalize_ward(parts[-3])
    return 'Unknown'


def _impute(col, raw, district):
    if raw is not None:
        return raw
    by_dist = (_saved or {}).get('impute_district', {}).get(col, {})
    if district in by_dist and pd.notna(by_dist[district]):
        return float(by_dist[district])
    global_map = (_saved or {}).get('impute_global', {})
    if col in global_map and pd.notna(global_map[col]):
        return float(global_map[col])
    fallback = {'Frontage': 4.0, 'Access Road': 5.0, 'Floors': 3.0, 'Bedrooms': 3.0, 'Bathrooms': 3.0}
    return fallback.get(col, 0.0)


def _predict_v3(area, frontage, floors, bedrooms, bathrooms,
                district, ward, address, street, house_position, property_type):
    frontage_raw = _to_optional_float(frontage)
    if frontage_raw is not None and frontage_raw <= 0:
        frontage_raw = None
    floors_raw = _to_optional_int(floors, zero_as_missing=True)
    bedrooms_raw = _to_optional_int(bedrooms, zero_as_missing=True)
    bathrooms_raw = _to_optional_int(bathrooms, zero_as_missing=True)

    frontage_missing = int(frontage_raw is None)
    floors_missing = int(floors_raw is None)
    bedrooms_missing = int(bedrooms_raw is None)
    bathrooms_missing = int(bathrooms_raw is None)

    address = str(address or '')
    district_clean = _normalize_district(district, default='Khác')
    ward_raw = _clean_text(ward, default='')
    if not ward_raw or ward_raw.lower() in ('unknown', 'nan', 'none'):
        ward_clean = _extract_ward(address)
    else:
        ward_clean = _normalize_ward(ward_raw)
    known_wards = set((_saved or {}).get('ward_price_m2') or {})
    if ward_clean not in known_wards:
        ward_clean = 'Khác' if 'Khác' in known_wards else 'Unknown'

    street_src = street or _extract_street(address)
    street_clean = _clean_street(street_src)
    rare_streets = set((_saved or {}).get('rare_streets') or [])
    known_streets = set((_saved or {}).get('street_price_m2') or {})
    if street_clean in rare_streets or (
        street_clean not in known_streets and street_clean != 'Unknown'
    ):
        street_clean = 'Khác'

    pos = _clean_text(house_position, default='').lower()
    if pos in ('alley', 'hẻm', 'hem'):
        house_pos = 'Alley'
    elif pos in ('frontage', 'mặt tiền', 'mat tien'):
        house_pos = 'Frontage'
    elif ALLEY_RE.search(address):
        house_pos = 'Alley'
    else:
        house_pos = 'Unknown'
    is_alley = 1 if house_pos == 'Alley' else 0

    # train_v3 loc het Is_Project==1; chi giu cung cong thuc regex, khong suy tu property_type
    loc_text = f"{address} {district_clean} {street_clean}"
    is_project = 1 if PROJECT_RE.search(loc_text) else 0

    area = float(area)
    frontage_v = _impute('Frontage', frontage_raw, district_clean)
    floors_v = _impute('Floors', None if floors_missing else floors_raw, district_clean)
    bedrooms_v = _impute('Bedrooms', bedrooms_raw, district_clean)
    bathrooms_v = _impute('Bathrooms', bathrooms_raw, district_clean)

    total_bed_bath = bedrooms_v + bathrooms_v
    floors_safe = max(1.0, float(floors_v))
    rooms_per_floor = total_bed_bath / floors_safe
    area_per_room = area / (total_bed_bath + 1)
    total_usable_area = area * floors_safe
    frontage_area_ratio = frontage_v / area if area > 0 else 0.0

    dist_areas = (_saved or {}).get('district_median_areas') or _district_median_areas
    dist_median = dist_areas.get(district_clean, DEFAULT_DISTRICT_MEDIAN_AREAS.get(district_clean, 60.0))
    area_to_dist_med = area / dist_median if dist_median else 1.0

    global_pm2 = float((_saved or {}).get('global_price_m2') or 90.0)
    dist_pm2 = ((_saved or {}).get('dist_price_m2') or {}).get(district_clean, global_pm2)
    ward_pm2 = ((_saved or {}).get('ward_price_m2') or {}).get(ward_clean, global_pm2)
    street_pm2 = ((_saved or {}).get('street_price_m2') or {}).get(street_clean, ward_pm2)

    row = {
        'Area': area,
        'Frontage': frontage_v,
        'Floors': floors_v,
        'Bedrooms': bedrooms_v,
        'Bathrooms': bathrooms_v,
        'Total_Bed_Bath': total_bed_bath,
        'Rooms_per_Floor': rooms_per_floor,
        'Area_per_Room': area_per_room,
        'Total_Usable_Area': total_usable_area,
        'Frontage_Area_Ratio': frontage_area_ratio,
        'Area_to_Dist_Med': area_to_dist_med,
        'Area_log': np.log1p(area),
        'Usable_Area_log': np.log1p(total_usable_area),
        'Area_sq': area ** 2,
        'Frontage_missing': frontage_missing,
        'Floors_missing': floors_missing,
        'Bedrooms_missing': bedrooms_missing,
        'Bathrooms_missing': bathrooms_missing,
        'Is_Alley': is_alley,
        'Is_Project': is_project,
        'Dist_Med_Price_m2': dist_pm2,
        'Ward_Med_Price_m2': ward_pm2,
        'Street_Med_Price_m2': street_pm2,
        'Naive_Price': area * dist_pm2 / 1000.0,
        'Naive_Price_Ward': area * ward_pm2 / 1000.0,
        'Naive_Price_Street': area * street_pm2 / 1000.0,
        'District': district_clean,
        'Ward': ward_clean,
        'Street_Clean': street_clean,
        'House_Position': house_pos,
    }

    input_df = pd.DataFrame([row])
    if _feature_names:
        input_df = input_df[_feature_names]

    pred_log = _model.predict(input_df)[0]
    pred_billion = float(np.expm1(pred_log))
    version_label = _model_name if 'v3' in str(_model_name).lower() else f'{_model_name} v3'
    return round(pred_billion * 1_000_000_000, -6), version_label


def _predict_v2(area, frontage, access_road, floors, bedrooms, bathrooms,
                legal_status, furniture_state, district, ward, address, street, property_type):
    frontage_raw = _to_optional_float(frontage)
    if frontage_raw is not None and frontage_raw <= 0:
        frontage_raw = None
    access_raw = _to_optional_float(access_road)
    if access_raw is not None and access_raw <= 0:
        access_raw = None
    floors_raw = _to_optional_int(floors, zero_as_missing=True)
    bedrooms_raw = _to_optional_int(bedrooms, zero_as_missing=True)
    bathrooms_raw = _to_optional_int(bathrooms, zero_as_missing=True)

    frontage_missing = int(frontage_raw is None)
    access_missing = int(access_raw is None)
    floors_missing = int(floors_raw is None)

    address = str(address or '')
    district_clean = _normalize_district(district, default='Khác')
    ward_raw = _clean_text(ward, default='')
    if not ward_raw or ward_raw.lower() in ('unknown', 'nan', 'none'):
        ward_clean = _extract_ward(address)
    else:
        ward_clean = _normalize_ward(ward_raw)
    legal_status = _clean_text(legal_status, default='Unknown')
    furniture_state = _clean_text(furniture_state, default='Unknown')

    is_project = 1 if PROJECT_RE.search(address) else 0
    is_alley = 1 if ALLEY_RE.search(address) else 0
    pt = _clean_text(property_type, default='').lower()
    if pt in ('apartment', 'chung cư', 'chung cu'):
        is_project = 1
        property_label = 'apartment'
    elif is_project:
        property_label = 'apartment'
    else:
        property_label = 'house'

    street_src = street or _extract_street(address)
    street_clean = _clean_street(street_src)
    rare_streets = set((_saved or {}).get('rare_streets') or [])
    if street_clean in rare_streets:
        street_clean = 'Khác'

    area = float(area)
    frontage_v = _impute('Frontage', frontage_raw, district_clean)
    access_v = _impute('Access Road', access_raw, district_clean)
    floors_v = _impute('Floors', None if floors_missing else floors_raw, district_clean)
    bedrooms_v = _impute('Bedrooms', bedrooms_raw, district_clean)
    bathrooms_v = _impute('Bathrooms', bathrooms_raw, district_clean)

    total_bed_bath = bedrooms_v + bathrooms_v
    floors_safe = max(1.0, float(floors_v))
    rooms_per_floor = total_bed_bath / floors_safe
    area_per_room = area / (total_bed_bath + 1)
    total_usable_area = area * floors_safe
    frontage_area_ratio = frontage_v / area if area > 0 else 0.0
    access_road_area_ratio = access_v / area if area > 0 else 0.0

    dist_areas = (_saved or {}).get('district_median_areas') or _district_median_areas
    dist_median = dist_areas.get(district_clean, DEFAULT_DISTRICT_MEDIAN_AREAS.get(district_clean, 60.0))
    area_to_dist_med = area / dist_median if dist_median else 1.0

    global_pm2 = float((_saved or {}).get('global_price_m2') or 90.0)
    dist_pm2 = ((_saved or {}).get('dist_price_m2') or {}).get(district_clean, global_pm2)
    ward_pm2 = ((_saved or {}).get('ward_price_m2') or {}).get(ward_clean, global_pm2)
    street_pm2 = ((_saved or {}).get('street_price_m2') or {}).get(street_clean, ward_pm2)

    row = {
        'Area': area,
        'Frontage': frontage_v,
        'Access Road': access_v,
        'Floors': floors_v,
        'Bedrooms': bedrooms_v,
        'Bathrooms': bathrooms_v,
        'Total_Bed_Bath': total_bed_bath,
        'Rooms_per_Floor': rooms_per_floor,
        'Area_per_Room': area_per_room,
        'Total_Usable_Area': total_usable_area,
        'Frontage_Area_Ratio': frontage_area_ratio,
        'Access_Road_Area_Ratio': access_road_area_ratio,
        'Area_to_Dist_Med': area_to_dist_med,
        'Area_log': np.log1p(area),
        'Usable_Area_log': np.log1p(total_usable_area),
        'Area_sq': area ** 2,
        'Frontage_missing': frontage_missing,
        'AccessRoad_missing': access_missing,
        'Floors_missing': floors_missing,
        'Is_Alley': is_alley,
        'Is_Project': is_project,
        'Dist_Med_Price_m2': dist_pm2,
        'Ward_Med_Price_m2': ward_pm2,
        'Street_Med_Price_m2': street_pm2,
        'Naive_Price': area * dist_pm2 / 1000.0,
        'Naive_Price_Ward': area * ward_pm2 / 1000.0,
        'Naive_Price_Street': area * street_pm2 / 1000.0,
        'Legal status': legal_status,
        'Furniture state': furniture_state,
        'District': district_clean,
        'Ward': ward_clean,
        'Street_Clean': street_clean,
        'Property_Type': property_label,
    }

    input_df = pd.DataFrame([row])
    if _feature_names:
        input_df = input_df[_feature_names]

    pred_log = _model.predict(input_df)[0]
    pred_billion = float(np.expm1(pred_log))
    version_label = _model_name if 'v2' in str(_model_name).lower() else f'{_model_name} v2'
    return round(pred_billion * 1_000_000_000, -6), version_label


def _predict_v1(area, frontage, access_road, floors, bedrooms, bathrooms,
                legal_status, furniture_state, district, ward):
    area = float(area)
    frontage = float(frontage) if frontage not in (None, '') else 4.0
    access_road = float(access_road) if access_road not in (None, '') else 5.0
    floors = int(floors) if floors not in (None, '', 0) else 1
    bedrooms = int(bedrooms) if bedrooms not in (None, '') else 2
    bathrooms = int(bathrooms) if bathrooms not in (None, '') else 2

    legal_status = _clean_text(legal_status, default='Have certificate')
    furniture_state = _clean_text(furniture_state, default='Full')
    district_clean = _normalize_district(district, default='Gò Vấp')
    ward_clean = _normalize_ward(ward)

    total_bed_bath = bedrooms + bathrooms
    floors_safe = max(1, floors)
    rooms_per_floor = total_bed_bath / floors_safe
    area_per_room = area / (total_bed_bath + 1)
    total_usable_area = area * floors_safe
    frontage_area_ratio = frontage / area if area > 0 else 0.0
    access_road_area_ratio = access_road / area if area > 0 else 0.0

    dist_median = _district_median_areas.get(district_clean, DEFAULT_DISTRICT_MEDIAN_AREAS.get(district_clean, 60.0))
    area_to_dist_med = area / dist_median if dist_median > 0 else 1.0

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
        'Area_log': np.log1p(area),
        'Usable_Area_log': np.log1p(total_usable_area),
        'Area_sq': area ** 2,
        'Legal status': legal_status,
        'Furniture state': furniture_state,
        'District': district_clean,
        'Ward': ward_clean,
        'Location_Group': f"{district_clean}_{ward_clean}",
    }

    input_df = pd.DataFrame([row])
    if _feature_names:
        input_df = input_df[_feature_names]

    pred_log = _model.predict(input_df)[0]
    predicted_price_vnd = float(np.expm1(pred_log)) * 1_000_000_000
    return round(predicted_price_vnd, -6), _model_name


def predict_price(area, frontage=None, access_road=None, floors=None,
                  bedrooms=0, bathrooms=0, legal_status=None,
                  furniture_state=None, city=None, district=None, ward=None, **kwargs):
    _ensure_model()
    if _model is None:
        raise RuntimeError(
            "Mô hình AI chưa được tải. Chạy notebooks/train_v2.ipynb "
            f"để tạo {MODEL_PATH_V2}, rồi khởi động lại Django."
        )

    if _model_version >= 2:
        return _predict_v2(
            area, frontage, access_road, floors, bedrooms, bathrooms,
            legal_status, furniture_state, district, ward,
            address=kwargs.get('address'),
            street=kwargs.get('street'),
            property_type=kwargs.get('property_type'),
        )

    return _predict_v1(
        area, frontage, access_road, floors, bedrooms, bathrooms,
        legal_status, furniture_state, district, ward,
    )

# EPA+DHA 주간 급여량 계산기

반려견영양연구소의 공개 교육용 Streamlit 계산기입니다. 건강한 성견의 NRC 유지 목적 EPA+DHA 계산과 주간 급여 계획 확인을 지원합니다.

## 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

Railway 시작 명령:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
```

## 식품 데이터

`food_data.json`에 식품명, 상태, EPA, DHA 및 출처 URL을 별도로 관리합니다. 현재는 USDA FoodData Central SR Legacy FDC 175139의 **대서양 정어리·기름 통조림·기름 뺀 고형분·뼈 포함**만 넣었습니다(EPA 473mg, DHA 509mg/100g). 목록에 없는 식품은 추정하지 않고 직접 입력합니다.

## 계산 기준

- 유지 권장량: `30 × 체중(kg)^0.75 mg/day`
- 대사체중 기준 안전 상한: `370 × 체중(kg)^0.75 mg/day`
- 열량 기준 안전 상한: `2.8 × 일일 kcal mg/day`

두 상한은 각각 표시하며, 둘 중 낮은 값을 단일 공식 상한으로 정의하지 않습니다.

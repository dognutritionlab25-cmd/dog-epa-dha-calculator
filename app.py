import json
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="EPA+DHA 주간 급여량 계산기", page_icon="🐾", layout="centered")

DATA_PATH = Path(__file__).with_name("food_data.json")
FOODS = json.loads(DATA_PATH.read_text(encoding="utf-8"))
DAYS = ["월", "화", "수", "목", "금", "토", "일"]


def num(value):
    return 0.0 if value is None else float(value)


def safe_number(label, value=0.0, step=1.0, min_value=0.0, key=None, help=None):
    return st.number_input(label, min_value=min_value, value=value, step=step, key=key, help=help)


def mg_from_food(epa_100, dha_100, grams):
    return (num(epa_100) + num(dha_100)) * num(grams) / 100


def main():
    st.title("🐾 EPA+DHA 주간 급여량 계산기")
    st.caption("반려견영양연구소 교육용 계산기 · 건강한 성견의 유지 목적")
    st.info("NRC 성견 유지 기준을 계산합니다. 질환, 임신·수유, 약물 복용 또는 치료 목적의 급여는 개별 판단이 필요합니다.")

    with st.expander("기준과 해석", expanded=False):
        st.markdown("""
        - 하루 유지 권장량: **30 × 체중(kg)^0.75 mg**
        - 주간 유지 목표: 하루 권장량 × 7
        - 대사체중 기준 안전 상한: **370 × 체중(kg)^0.75 mg/일**
        - 열량 기준 안전 상한: **2.8 × 하루 섭취 kcal mg/일**

        두 상한은 각각 참고값입니다. 낮은 값을 임의로 NRC의 단일 공식 상한으로 합치지 않습니다. 상한 초과는 곧바로 독성 발생을 뜻하지 않습니다.
        """)

    st.subheader("1. 아이 정보")
    c1, c2 = st.columns(2)
    weight = c1.number_input("체중 (kg)", min_value=0.0, value=4.0, step=0.1)
    kcal = c2.number_input("하루 섭취 열량 (kcal, 선택)", min_value=0.0, value=0.0, step=1.0,
                           help="입력하면 열량 기준 안전 상한을 함께 계산합니다.")
    if weight <= 0:
        st.error("체중은 0보다 커야 합니다.")
        return
    metabolic_weight = weight ** 0.75
    daily_target = 30 * metabolic_weight
    weekly_target = daily_target * 7
    metabolic_cap = 370 * metabolic_weight
    kcal_cap = 2.8 * kcal if kcal > 0 else None

    st.subheader("2. 식품 섭취")
    food_mode = st.radio("식품 데이터 입력 방식", ["등록 식품 선택", "EPA·DHA 직접 입력"], horizontal=True)
    selected_food = None
    food_epa = food_dha = 0.0
    if food_mode == "등록 식품 선택":
        labels = [f'{f["name"]} — EPA+DHA {f["epa_mg_per_100g"] + f["dha_mg_per_100g"]:.0f}mg/100g' for f in FOODS]
        choice = st.selectbox("생선·어패류 종류와 상태", labels)
        selected_food = FOODS[labels.index(choice)]
        food_epa, food_dha = selected_food["epa_mg_per_100g"], selected_food["dha_mg_per_100g"]
        st.caption(f'출처: [{selected_food["source"]}]({selected_food["source_url"]})')
    else:
        st.caption("제품 라벨 또는 확인 가능한 식품성분 자료의 100g당 값으로 직접 입력하세요.")
        a, b = st.columns(2)
        food_epa = a.number_input("100g당 EPA (mg)", min_value=0.0, value=0.0, step=1.0)
        food_dha = b.number_input("100g당 DHA (mg)", min_value=0.0, value=0.0, step=1.0)
    food_grams = st.number_input("1회 급여 중량 (g)", min_value=0.0, value=0.0, step=1.0)
    food_days = st.multiselect("식품 급여 요일", DAYS, default=[])
    food_once = mg_from_food(food_epa, food_dha, food_grams)

    st.subheader("3. 피시오일·기존 보충제")
    st.caption("피시오일 전체 무게가 아니라, 라벨의 EPA와 DHA 함량만 입력합니다.")
    p1, p2 = st.columns(2)
    product_epa = p1.number_input("표시 1단위당 EPA (mg)", min_value=0.0, value=0.0, step=1.0)
    product_dha = p2.number_input("표시 1단위당 DHA (mg)", min_value=0.0, value=0.0, step=1.0)
    unit_type = st.selectbox("제품 표시 기준", ["1mL", "5mL", "1캡슐", "기타 단위"])
    if unit_type == "기타 단위":
        unit_label = st.text_input("표시 단위 이름", value="1회 제공량")
    else:
        unit_label = unit_type
    supplement_amount = st.number_input(f"급여량 ({unit_label} 기준 단위 수)", min_value=0.0, value=0.0, step=0.1)
    supplement_days = st.multiselect("보충제 급여 요일", DAYS, default=[])
    supplement_once = (product_epa + product_dha) * supplement_amount
    if product_epa + product_dha == 0 and supplement_amount > 0:
        st.warning("보충제 급여량이 입력되었지만 EPA+DHA 함량이 0입니다. 라벨 수치를 확인해 주세요.")

    st.subheader("4. 주간 결과")
    food_weekly = food_once * len(food_days)
    supplement_weekly = supplement_once * len(supplement_days)
    planned_weekly = food_weekly + supplement_weekly
    extra_needed = max(0.0, weekly_target - food_weekly - supplement_weekly)
    planned_daily_average = planned_weekly / 7
    difference = planned_weekly - weekly_target
    product_per_unit = product_epa + product_dha

    r1, r2 = st.columns(2)
    r1.metric("하루 NRC 유지 권장량", f"{daily_target:.2f} mg")
    r2.metric("주간 NRC 유지 목표", f"{weekly_target:.2f} mg")
    r1.metric("주간 식품 섭취", f"{food_weekly:.2f} mg")
    r2.metric("주간 기존 보충제 섭취", f"{supplement_weekly:.2f} mg")
    r1.metric("추가 보충 필요량", f"{extra_needed:.2f} mg")
    if product_per_unit > 0:
        additional_units = extra_needed / product_per_unit
        suffix = "mL" if unit_type in ["1mL", "5mL"] else "캡슐" if unit_type == "1캡슐" else unit_label
        r2.metric(f"제품 기준 추가 필요 {suffix}", f"{additional_units:.3f} {suffix}")
    else:
        r2.metric("제품 기준 추가 필요량", "제품 함량 입력 필요")
    r1.metric("실제 계획 주간 총섭취량", f"{planned_weekly:.2f} mg")
    r2.metric("하루 평균 섭취량", f"{planned_daily_average:.2f} mg")
    st.metric("주간 목표 대비 차이", f"{difference:+.2f} mg")

    st.subheader("5. 요일별 확인")
    rows = []
    for day in DAYS:
        f = food_once if day in food_days else 0.0
        s = supplement_once if day in supplement_days else 0.0
        total = f + s
        meta_note = "초과" if total > metabolic_cap else "이내"
        kcal_note = "입력 없음" if kcal_cap is None else ("초과" if total > kcal_cap else "이내")
        rows.append({"요일": day, "식품 (mg)": round(f, 2), "보충제 (mg)": round(s, 2), "합계 (mg)": round(total, 2),
                     f"대사체중 상한 {metabolic_cap:.2f}mg": meta_note,
                     f"열량 상한 {kcal_cap:.2f}mg" if kcal_cap is not None else "열량 기준": kcal_note})
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.caption("주간 총량이 같더라도 급여 간격에 따른 효과가 동일하다고 단정할 수 없습니다. 이 계산기는 특정 급여 횟수를 의학적 권장사항으로 제시하지 않습니다.")

    st.subheader("안전 상한 참고")
    cap1, cap2 = st.columns(2)
    cap1.metric("대사체중 기준 안전 상한", f"{metabolic_cap:.2f} mg/일")
    cap2.metric("열량 기준 안전 상한", "하루 열량을 입력해 주세요" if kcal_cap is None else f"{kcal_cap:.2f} mg/일")

    with st.expander("등록 식품 데이터와 한계"):
        st.markdown("""
        현재 등록 식품은 출처와 상태를 특정할 수 있는 항목만 포함합니다. 같은 생선이라도 종, 원산지, 생것·익힌 것·통조림 상태, 기름과 고형분의 처리에 따라 값이 달라질 수 있습니다.
        
        목록에 없는 식품은 추정값을 만들지 않고 **직접 입력**을 사용하도록 했습니다. 식품 데이터는 `food_data.json`에서 코드와 분리되어 있어, 검증한 항목을 추가할 수 있습니다.
        """)


if __name__ == "__main__":
    main()

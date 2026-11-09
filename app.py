import json
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="EPA+DHA 주간 급여량 계산기", page_icon="🐾", layout="centered")
BASE_DIR = Path(__file__).parent
FOODS = json.loads((BASE_DIR / "food_data.json").read_text(encoding="utf-8"))
DAYS = ["월", "화", "수", "목", "금", "토", "일"]


def food_mg(epa, dha, grams):
    return (float(epa) + float(dha)) * float(grams) / 100


def main():
    st.markdown("""<style>
    .stApp {background:#fbf5e9;}
    .block-container {max-width:760px;padding-top:1.25rem;padding-bottom:4rem;}
    h2 {padding-top:1.2rem;border-top:4px solid #6b9442;margin-top:1.6rem;}
    div[data-testid="stMetric"] {background:#f7f2e9;border-radius:12px;padding:12px;}
    .small-note {color:#6c6257;font-size:.9rem;}
    .result-callout {background:#f4ead7;border:3px solid #6b9442;border-radius:16px;padding:20px 22px;margin:14px 0 22px;}
    .result-callout .eyebrow {font-size:.95rem;font-weight:700;color:#496b2d;margin-bottom:5px;}
    .result-callout .amount {font-size:2rem;font-weight:800;color:#24451f;line-height:1.15;margin:3px 0 9px;}
    .result-callout .explanation {font-size:1.05rem;font-weight:650;color:#30352a;line-height:1.6;}
    </style>""", unsafe_allow_html=True)
    st.image(str(BASE_DIR / "assets" / "dog-nutrition-lab-logo.png"), width=500)
    st.title("EPA+DHA 주간 급여량 계산기")
    st.caption("반려견영양연구소 · 건강한 성견의 유지 목적 교육용 계산기")
    st.info("체중, 일주일 동안 먹이는 생선, 피시오일을 차례로 입력하면 주간 총량을 계산합니다.")
    with st.expander("이 계산기의 기준"):
        st.markdown("""- 하루 유지 목표: **30 × 체중(kg)^0.75 mg**
        - 주간 유지 목표: 하루 유지 목표 × 7
        - 대사체중 기준 안전 상한: **370 × 체중(kg)^0.75 mg/일**
        - 열량 기준 안전 상한: **2.8 × 하루 섭취 kcal mg/일**

        두 안전 상한은 서로 다른 참고 기준이므로 따로 보여 드립니다. 상한을 넘었다고 바로 독성이 생긴다는 뜻은 아닙니다.""")

    st.header("1. 아이 정보")
    left, right = st.columns(2)
    weight = left.number_input("체중 (kg)", min_value=0.0, value=4.0, step=0.1)
    kcal = right.number_input("하루 먹는 열량 (kcal, 선택)", min_value=0.0, value=0.0, step=1.0)
    if weight <= 0:
        st.error("체중은 0보다 커야 계산할 수 있습니다.")
        return
    mw = weight ** .75
    daily_target, weekly_target, metabolic_cap = 30 * mw, 30 * mw * 7, 370 * mw
    kcal_cap = 2.8 * kcal if kcal > 0 else None

    st.header("2. 일주일 동안 먹이는 생선")
    st.caption("기름 통조림은 목록에서 제외했습니다. 정어리는 **물에 든 무염 제품**을 고르세요.")
    labels = [f'{f["name"]} · EPA+DHA {f["epa_mg_per_100g"] + f["dha_mg_per_100g"]:.0f}mg/100g' for f in FOODS]
    selected = st.selectbox("생선 종류", labels)
    food = FOODS[labels.index(selected)]
    c1, c2, c3 = st.columns(3)
    c1.metric("EPA", f'{food["epa_mg_per_100g"]:.0f} mg')
    c2.metric("DHA", f'{food["dha_mg_per_100g"]:.0f} mg')
    c3.metric("합계 · 100g당", f'{food["epa_mg_per_100g"] + food["dha_mg_per_100g"]:.0f} mg')
    st.markdown(f'<div class="small-note">상태: {food["state"]} · 출처: <a href="{food["source_url"]}" target="_blank">{food["source"]}</a></div>', unsafe_allow_html=True)
    grams = st.number_input("한 번에 먹이는 양 (g)", min_value=0.0, value=0.0, step=1.0)
    food_days = st.multiselect("먹이는 요일", DAYS, placeholder="예: 화요일, 토요일")
    fish_once = food_mg(food["epa_mg_per_100g"], food["dha_mg_per_100g"], grams)
    st.caption(f"이 생선을 한 번 {grams:.0f}g 먹이면 EPA+DHA는 {fish_once:.2f}mg입니다.")

    with st.expander("목록에 없는 생선·어패류라면 직접 입력"):
        st.caption("라벨 또는 확인한 식품성분표의 100g당 수치를 입력하세요. 추정값은 넣지 마세요.")
        a, b = st.columns(2)
        manual_epa = a.number_input("100g당 EPA (mg)", min_value=0.0, value=0.0, step=1.0)
        manual_dha = b.number_input("100g당 DHA (mg)", min_value=0.0, value=0.0, step=1.0)
        manual_grams = st.number_input("한 번에 먹이는 양 (g)", min_value=0.0, value=0.0, step=1.0, key="manual_grams")
        manual_days = st.multiselect("먹이는 요일", DAYS, key="manual_days", placeholder="직접 입력한 식품의 요일")
        manual_once = food_mg(manual_epa, manual_dha, manual_grams)

    st.header("3. 피시오일 또는 기존 보충제")
    st.caption("병 전체의 기름 무게가 아니라, 제품 라벨에 적힌 EPA와 DHA만 입력하세요.")
    p1, p2 = st.columns(2)
    product_epa = p1.number_input("라벨의 EPA (mg)", min_value=0.0, value=0.0, step=1.0)
    product_dha = p2.number_input("라벨의 DHA (mg)", min_value=0.0, value=0.0, step=1.0)
    label_unit = st.selectbox("위 EPA·DHA가 표시된 기준", ["1mL", "5mL", "1캡슐", "기타 단위"])
    label_total = product_epa + product_dha
    if label_unit == "1mL":
        dose_unit, mg_per_dose = "mL", label_total
    elif label_unit == "5mL":
        dose_unit, mg_per_dose = "mL", label_total / 5
    elif label_unit == "1캡슐":
        dose_unit, mg_per_dose = "캡슐", label_total
    else:
        dose_unit, mg_per_dose = st.text_input("단위 이름", value="1회 제공량"), label_total
    if label_total > 0:
        st.success(f"실제 {dose_unit} 1단위당 EPA+DHA는 {mg_per_dose:.2f}mg입니다.")
    dose_amount = st.number_input(f"한 번에 주는 양 ({dose_unit})", min_value=0.0, value=0.0, step=0.1)
    supplement_days = st.multiselect("보충제를 주는 요일", DAYS, placeholder="예: 월요일, 목요일")
    supplement_once = mg_per_dose * dose_amount

    food_weekly = fish_once * len(food_days) + manual_once * len(manual_days)
    supplement_weekly = supplement_once * len(supplement_days)
    planned_weekly = food_weekly + supplement_weekly
    extra_needed = max(0.0, weekly_target - planned_weekly)

    st.header("4. 계산 결과")
    if extra_needed > 0:
        if mg_per_dose > 0:
            callout_amount = f"추가로 {extra_needed:.2f}mg · {extra_needed / mg_per_dose:.3f}{dose_unit}"
            callout_text = f"이번 주 계획만으로는 유지 목표보다 {extra_needed:.2f}mg 부족합니다. 현재 입력한 제품이라면 위 양을 더해야 주간 유지 목표에 닿습니다."
        else:
            callout_amount = f"추가로 {extra_needed:.2f}mg 필요"
            callout_text = "이번 주 계획만으로는 유지 목표에 부족합니다. 피시오일 제품의 EPA와 DHA 함량을 입력하면 필요한 실제 급여량도 확인할 수 있습니다."
        callout_title = "이번 주, 추가 보충이 필요합니다"
    else:
        callout_amount = "추가 보충 0mg"
        callout_title = "이번 주 계획으로 유지 목표를 채웠습니다"
        callout_text = "입력한 생선과 기존 보충제의 주간 합계가 유지 목표 이상입니다. 그래서 계산상 추가 보충은 필요하지 않습니다."
    st.markdown(f'''<div class="result-callout"><div class="eyebrow">{callout_title}</div><div class="amount">{callout_amount}</div><div class="explanation">{callout_text}</div></div>''', unsafe_allow_html=True)
    r1, r2 = st.columns(2)
    r1.metric("하루 유지 목표", f"{daily_target:.2f} mg")
    r2.metric("일주일 유지 목표", f"{weekly_target:.2f} mg")
    r1.metric("일주일 생선 섭취량", f"{food_weekly:.2f} mg")
    r2.metric("일주일 보충제 섭취량", f"{supplement_weekly:.2f} mg")
    r1.metric("실제 일주일 총섭취량", f"{planned_weekly:.2f} mg")
    r2.metric("목표까지 추가로 필요한 양", f"{extra_needed:.2f} mg")
    if mg_per_dose > 0:
        r1.metric(f"현재 제품으로 추가 필요 {dose_unit}", f"{extra_needed / mg_per_dose:.3f} {dose_unit}")
    r2.metric("하루 평균 섭취량", f"{planned_weekly / 7:.2f} mg")
    st.metric("주간 목표와의 차이", f"{planned_weekly - weekly_target:+.2f} mg")

    st.subheader("요일별 확인")
    rows = []
    for day in DAYS:
        fish_today = (fish_once if day in food_days else 0) + (manual_once if day in manual_days else 0)
        supplement_today = supplement_once if day in supplement_days else 0
        total = fish_today + supplement_today
        rows.append({"요일":day, "생선 (mg)":round(fish_today,2), "보충제 (mg)":round(supplement_today,2), "하루 합계 (mg)":round(total,2), "대사체중 기준":"초과" if total > metabolic_cap else "이내", "열량 기준":"입력 없음" if kcal_cap is None else ("초과" if total > kcal_cap else "이내")})
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.caption("주간 총량이 같더라도 급여 간격의 효과가 같다고 단정할 수 없습니다. 이 계산기는 특정 횟수를 의학적 권장사항처럼 제시하지 않습니다.")
    a, b = st.columns(2)
    a.metric("대사체중 기준 안전 상한", f"{metabolic_cap:.2f} mg/일")
    b.metric("열량 기준 안전 상한", "하루 열량을 입력해 주세요" if kcal_cap is None else f"{kcal_cap:.2f} mg/일")


if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="동네별 지표 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 한글 폰트 설정
import plotly.io as pio
pio.templates.default = "plotly_white"

@st.cache_data
def load_data():
    """데이터 로드 및 전처리"""
    df = pd.read_csv('radar_지표.csv')
    # 동(dong) 데이터만 필터링
    dong_data = df[df['GUBUN'] == 'dong'].copy()
    return dong_data

def create_radar_chart(data, year, dong_name):
    """Plotly를 사용한 레이더 차트 생성"""
    categories = ['프랜차이즈비율', '임대료', '폐업률', '업력평균']
    
    # 데이터 추출 및 정규화
    values = []
    actual_values = []
    
    # 프랜차이즈비율
    franchise_ratio = data[f'{year}_프랜차이즈비율']
    values.append(franchise_ratio / 25.0)
    actual_values.append(franchise_ratio)
    
    # 임대료
    rent = data[f'{year}_1층_임대료']
    values.append(rent / 300000.0)
    actual_values.append(rent)
    
    # 폐업률
    closure_rate = data[f'{year}_폐업률']
    values.append(closure_rate / 10.0)
    actual_values.append(closure_rate)
    
    # 업력평균
    if year <= 2024:
        avg_business_years = data[f'{year}외식업력평균']
    else:  # 2025년은 2024년 값 사용
        avg_business_years = data['2024외식업력평균']
    values.append(avg_business_years / 15.0)
    actual_values.append(avg_business_years)
    
    # 레이더 차트 생성
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=dong_name,
        line_color='rgb(32, 201, 151)',
        fillcolor='rgba(32, 201, 151, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title=f"{dong_name} - {year}년 지표",
        title_x=0.5,
        title_font_size=16
    )
    
    return fig, actual_values

def create_comparison_chart(data, year, selected_dongs):
    """여러 동의 비교 레이더 차트"""
    categories = ['프랜차이즈비율', '임대료', '폐업률', '업력평균']
    
    fig = go.Figure()
    
    colors = ['rgb(32, 201, 151)', 'rgb(255, 99, 132)', 'rgb(54, 162, 235)', 
              'rgb(255, 205, 86)', 'rgb(153, 102, 255)', 'rgb(255, 159, 64)']
    
    for i, dong_name in enumerate(selected_dongs):
        dong_data = data[data['동네명'] == dong_name].iloc[0]
        
        # 데이터 추출 및 정규화
        values = []
        
        # 프랜차이즈비율
        franchise_ratio = dong_data[f'{year}_프랜차이즈비율']
        values.append(franchise_ratio / 25.0)
        
        # 임대료
        rent = dong_data[f'{year}_1층_임대료']
        values.append(rent / 300000.0)
        
        # 폐업률
        closure_rate = dong_data[f'{year}_폐업률']
        values.append(closure_rate / 10.0)
        
        # 업력평균
        if year <= 2024:
            avg_business_years = dong_data[f'{year}외식업력평균']
        else:
            avg_business_years = dong_data['2024외식업력평균']
        values.append(avg_business_years / 15.0)
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=dong_name,
            line_color=colors[i % len(colors)],
            fillcolor=colors[i % len(colors)].replace('rgb', 'rgba').replace(')', ', 0.3)')
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title=f"{year}년 동네별 지표 비교",
        title_x=0.5,
        title_font_size=16
    )
    
    return fig

def create_trend_chart(data, selected_dong, years):
    """시계열 트렌드 차트"""
    categories = ['프랜차이즈비율', '임대료', '폐업률', '업력평균']
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=categories,
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    dong_data = data[data['동네명'] == selected_dong].iloc[0]
    
    # 프랜차이즈비율 트렌드
    franchise_values = [dong_data[f'{year}_프랜차이즈비율'] for year in years]
    fig.add_trace(
        go.Scatter(x=years, y=franchise_values, mode='lines+markers', name='프랜차이즈비율'),
        row=1, col=1
    )
    
    # 임대료 트렌드
    rent_values = [dong_data[f'{year}_1층_임대료'] for year in years]
    fig.add_trace(
        go.Scatter(x=years, y=rent_values, mode='lines+markers', name='임대료'),
        row=1, col=2
    )
    
    # 폐업률 트렌드
    closure_values = [dong_data[f'{year}_폐업률'] for year in years]
    fig.add_trace(
        go.Scatter(x=years, y=closure_values, mode='lines+markers', name='폐업률'),
        row=2, col=1
    )
    
    # 업력평균 트렌드
    business_years_values = []
    for year in years:
        if year <= 2024:
            business_years_values.append(dong_data[f'{year}외식업력평균'])
        else:
            business_years_values.append(dong_data['2024외식업력평균'])
    
    fig.add_trace(
        go.Scatter(x=years, y=business_years_values, mode='lines+markers', name='업력평균'),
        row=2, col=2
    )
    
    fig.update_layout(
        title=f"{selected_dong} 지표 변화 추이 (2015-2025)",
        title_x=0.5,
        height=600,
        showlegend=False
    )
    
    # Y축 레이블 설정
    fig.update_yaxes(title_text="%", row=1, col=1)
    fig.update_yaxes(title_text="원/㎡", row=1, col=2)
    fig.update_yaxes(title_text="%", row=2, col=1)
    fig.update_yaxes(title_text="년", row=2, col=2)
    
    return fig

def main():
    st.title("🏘️ 서울시 동네별 지표 대시보드")
    st.markdown("2015년부터 2025년까지의 동네별 주요 지표를 시각화합니다.")
    
    # 데이터 로드
    data = load_data()
    
    # 사이드바 설정
    st.sidebar.header("📊 설정")
    
    # 년도 선택
    years = list(range(2015, 2026))
    selected_year = st.sidebar.selectbox(
        "연도 선택",
        years,
        index=len(years)-1  # 기본값: 2025년
    )
    
    # 동네 선택
    available_dongs = data['동네명'].unique().tolist()
    selected_dong = st.sidebar.selectbox(
        "동네 선택",
        available_dongs,
        index=0
    )
    
    # 비교할 동네들 선택
    st.sidebar.subheader("동네 비교")
    comparison_dongs = st.sidebar.multiselect(
        "비교할 동네들 선택 (최대 6개)",
        available_dongs,
        default=available_dongs[:3]
    )
    
    if len(comparison_dongs) > 6:
        st.sidebar.warning("최대 6개 동네까지만 선택 가능합니다.")
        comparison_dongs = comparison_dongs[:6]
    
    # 메인 컨텐츠
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📈 개별 동네 레이더 차트")
        
        # 선택된 동네의 데이터 확인
        dong_data = data[data['동네명'] == selected_dong]
        
        if not dong_data.empty:
            # 필수 컬럼 확인
            required_cols = [f'{selected_year}_프랜차이즈비율', f'{selected_year}_1층_임대료', f'{selected_year}_폐업률']
            if selected_year <= 2024:
                required_cols.append(f'{selected_year}외식업력평균')
            else:
                required_cols.append('2024외식업력평균')
            
            if dong_data[required_cols].notna().all().all():
                radar_fig, actual_values = create_radar_chart(dong_data.iloc[0], selected_year, selected_dong)
                st.plotly_chart(radar_fig, use_container_width=True)
                
                # 실제 값 표시
                st.markdown("**실제 지표 값:**")
                metrics_col1, metrics_col2 = st.columns(2)
                with metrics_col1:
                    st.metric("프랜차이즈비율", f"{actual_values[0]:.1f}%")
                    st.metric("임대료", f"{actual_values[1]:,.0f}원/㎡")
                with metrics_col2:
                    st.metric("폐업률", f"{actual_values[2]:.1f}%")
                    st.metric("업력평균", f"{actual_values[3]:.1f}년")
            else:
                st.error(f"{selected_year}년 데이터가 부족합니다.")
        else:
            st.error("선택된 동네의 데이터를 찾을 수 없습니다.")
    
    with col2:
        st.subheader("🔄 동네 비교 레이더 차트")
        
        if comparison_dongs:
            # 비교할 동네들의 데이터 확인
            valid_dongs = []
            for dong in comparison_dongs:
                dong_data = data[data['동네명'] == dong]
                if not dong_data.empty:
                    required_cols = [f'{selected_year}_프랜차이즈비율', f'{selected_year}_1층_임대료', f'{selected_year}_폐업률']
                    if selected_year <= 2024:
                        required_cols.append(f'{selected_year}외식업력평균')
                    else:
                        required_cols.append('2024외식업력평균')
                    
                    if dong_data[required_cols].notna().all().all():
                        valid_dongs.append(dong)
            
            if valid_dongs:
                comparison_fig = create_comparison_chart(data, selected_year, valid_dongs)
                st.plotly_chart(comparison_fig, use_container_width=True)
            else:
                st.error(f"{selected_year}년 비교 데이터가 부족합니다.")
        else:
            st.info("비교할 동네를 선택해주세요.")
    
    # 시계열 트렌드 차트
    st.subheader("📊 시계열 변화 추이")
    
    if selected_dong:
        dong_data = data[data['동네명'] == selected_dong]
        if not dong_data.empty:
            # 데이터가 있는 연도만 필터링
            available_years = []
            for year in years:
                required_cols = [f'{year}_프랜차이즈비율', f'{year}_1층_임대료', f'{year}_폐업률']
                if year <= 2024:
                    required_cols.append(f'{year}외식업력평균')
                else:
                    required_cols.append('2024외식업력평균')
                
                if dong_data[required_cols].notna().all().all():
                    available_years.append(year)
            
            if available_years:
                trend_fig = create_trend_chart(data, selected_dong, available_years)
                st.plotly_chart(trend_fig, use_container_width=True)
            else:
                st.error("시계열 데이터가 부족합니다.")
        else:
            st.error("선택된 동네의 데이터를 찾을 수 없습니다.")
    
    # 데이터 테이블
    st.subheader("📋 상세 데이터")
    
    if selected_dong:
        dong_data = data[data['동네명'] == selected_dong]
        if not dong_data.empty:
            # 선택된 동네의 모든 연도 데이터 표시
            display_data = []
            for year in years:
                row_data = {'연도': year}
                
                # 각 지표 추가
                if f'{year}_프랜차이즈비율' in dong_data.columns:
                    row_data['프랜차이즈비율(%)'] = dong_data[f'{year}_프랜차이즈비율'].iloc[0]
                if f'{year}_1층_임대료' in dong_data.columns:
                    row_data['임대료(만원)'] = dong_data[f'{year}_1층_임대료'].iloc[0]
                if f'{year}_폐업률' in dong_data.columns:
                    row_data['폐업률(%)'] = dong_data[f'{year}_폐업률'].iloc[0]
                if f'{year}외식업력평균' in dong_data.columns:
                    row_data['업력평균(년)'] = dong_data[f'{year}외식업력평균'].iloc[0]
                elif year == 2025 and '2024외식업력평균' in dong_data.columns:
                    row_data['업력평균(년)'] = dong_data['2024외식업력평균'].iloc[0]
                
                display_data.append(row_data)
            
            df_display = pd.DataFrame(display_data)
            st.dataframe(df_display, use_container_width=True)
        else:
            st.error("선택된 동네의 데이터를 찾을 수 없습니다.")

if __name__ == "__main__":
    main() 
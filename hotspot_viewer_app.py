import streamlit as st
import pandas as pd

def load_data(uploaded_file):
    """加载上传的CSV文件"""
    try:
        df = pd.read_csv(uploaded_file)
        return df, None
    except Exception as e:
        return None, str(e)

def format_percentage(value):
    """格式化百分比显示"""
    if pd.isna(value):
        return "N/A"
    return f"{value*100:.2f}%"

def display_all_hotspots_data(df):
    """显示所有热点的搜索词数据"""
    # 按relevance_score排序
    df_sorted = df.sort_values(['focus_unique_id', 'relevance_score'], ascending=[True, False])
    
    # 创建数据表格
    display_df = df_sorted.copy()
    
    # 格式化百分比字段
    display_df['search_popularity_comparison_formatted'] = display_df['search_popularity_comparison'].apply(format_percentage)
    display_df['search_result_gtv_order_uv_growth_rate_formatted'] = display_df['search_result_gtv_order_uv_growth_rate'].apply(format_percentage)
    display_df['search_result_uv_cxr_formatted'] = display_df['search_result_uv_cxr'].apply(format_percentage)
    
    # 添加过滤器
    col1, col2 = st.columns(2)
    with col1:
        relevance_filter = st.selectbox(
            "按相关性评分筛选",
            options=["全部", "2分(强相关)", "1分(弱相关)", "0分(无相关)"],
            index=0
        )
    
    with col2:
        min_uv = st.number_input(
            "最小搜索浏览UV", 
            min_value=0, 
            value=0,
            step=100
        )
    
    # 应用过滤器
    filtered_df = display_df.copy()
    if relevance_filter != "全部":
        relevance_value = int(relevance_filter[0])
        filtered_df = filtered_df[filtered_df['relevance_score'] == relevance_value]
    
    if min_uv > 0:
        filtered_df = filtered_df[filtered_df['search_result_view_uv'] >= min_uv]
    
    # 按热点分组显示数据
    unique_hotspots = filtered_df['focus_unique_id'].unique()
    
    for hotspot_id in unique_hotspots:
        hotspot_data = filtered_df[filtered_df['focus_unique_id'] == hotspot_id]
        hotspot_name = hotspot_data.iloc[0]['focus_name']
        hotspot_detail = hotspot_data.iloc[0]['focus_detail'] if 'focus_detail' in hotspot_data.columns else ""
        
        # 显示热点名称作为标题
        st.markdown(f"### 🔥 {hotspot_name}")
        # 在热点名称下方展示热点详情（小号灰色字体）
        if hotspot_detail:
            st.markdown(f"<div style='color:gray;font-size:13px;margin-bottom:8px'>{hotspot_detail}</div>", unsafe_allow_html=True)
        
        # 准备显示的数据
        display_data = hotspot_data[[
            'format_query',
            'relevance_score', 
            'search_result_view_uv',
            'search_popularity_comparison_formatted',
            'search_result_gtv_order_uv',
            'search_result_gtv_order_uv_growth_rate_formatted',
            'search_result_uv_cxr_formatted'
        ]].copy()
        
        # 重命名列
        display_data.columns = [
            '搜索词',
            '相关性评分',
            '搜索人气',
            '搜索人气涨幅',
            '交易人气',
            '交易人气涨幅',
            '支付转化率'
        ]
        
        # 使用颜色编码相关性评分
        def highlight_relevance(row):
            relevance_score = row['相关性评分']
            if relevance_score == 2:
                return ['background-color: #d4edda'] * len(row)  # 绿色
            elif relevance_score == 1:
                return ['background-color: #fff3cd'] * len(row)  # 黄色
            else:
                return ['background-color: #f8d7da'] * len(row)  # 红色
        
        # 显示该热点的搜索词表格
        st.dataframe(
            display_data.style.apply(highlight_relevance, axis=1),
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")  # 分隔线

def main():
    st.set_page_config(
        page_title="热点搜索词分析器",
        page_icon="🔥",
        layout="wide"
    )
    
    st.title("🔥 热点搜索词分析器")
    st.markdown("---")
    
    # 文件上传
    uploaded_file = st.file_uploader(
        "请上传CSV文件",
        type=['csv'],
        help="请上传hotspot_query_ranked_top10格式的CSV文件"
    )
    
    if uploaded_file is not None:
        # 加载数据
        with st.spinner("正在加载数据..."):
            df, error = load_data(uploaded_file)
        
        if error:
            st.error(f"加载文件失败: {error}")
            return
        
        if df is None or df.empty:
            st.error("文件为空或格式不正确")
            return
        
        # 验证必要的列是否存在
        required_columns = [
            'focus_unique_id', 'focus_name', 'format_query', 'relevance_score',
            'search_result_view_uv', 'search_popularity_comparison', 
            'search_result_gtv_order_uv', 'search_result_gtv_order_uv_growth_rate',
            'search_result_uv_cxr'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"缺少必要的列: {', '.join(missing_columns)}")
            return
        
        # 数据总览
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总搜索词数", len(df))
        with col2:
            st.metric("热点数量", df['focus_unique_id'].nunique())
        with col3:
            avg_relevance = df['relevance_score'].mean()
            st.metric("平均相关性评分", f"{avg_relevance:.2f}")
        with col4:
            total_uv = df['search_result_view_uv'].sum()
            st.metric("总搜索UV", f"{total_uv:,}")
        
        # 显示所有热点数据
        st.subheader("📊 热点搜索词数据")
        display_all_hotspots_data(df)
    
    else:
        st.info("👆 请上传CSV文件开始分析")
        
        # 显示示例数据格式
        st.subheader("📄 文件格式说明")
        st.markdown("""
        请上传包含以下列的CSV文件:
        - `focus_unique_id`: 热点唯一ID
        - `focus_name`: 热点名称
        - `focus_detail`: 热点详情
        - `format_query`: 搜索词
        - `relevance_score`: 相关性评分 (0/1/2)
        - `search_result_view_uv`: 搜索浏览UV
        - `search_popularity_comparison`: 搜索热度对比
        - `search_result_gtv_order_uv`: 搜索下单UV
        - `search_result_gtv_order_uv_growth_rate`: 下单UV增长率
        - `search_result_uv_cxr`: 搜索转化率
        """)

if __name__ == "__main__":
    main()
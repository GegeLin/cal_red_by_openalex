import streamlit as st
import pandas as pd
from pyalex import Works
import requests
import time

# --------------------------------------------------------------------------------
# 核心工具函数（不变）
# --------------------------------------------------------------------------------
def get_refs_by_id(openalex_id_url, show_detail_error=False, log_placeholder=None):
    try:
        pure_id = openalex_id_url.split('/')[-1]
        api_url = f"https://api.openalex.org/works/{pure_id}"
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        refs = response.json().get("referenced_works", [])
        return refs
    except Exception as e:
        if show_detail_error and log_placeholder:
            st.session_state.sidebar_logs.append(f"ID文献获取失败：{str(e)}")
            log_placeholder.markdown("<br>".join(st.session_state.sidebar_logs), unsafe_allow_html=True)
        return []

def get_refs_by_doi(doi, show_detail_error=False, log_placeholder=None):
    try:
        w = Works()
        focus_doi = f"https://doi.org/{doi}"
        w = w[focus_doi]
        
        refs = w.get("referenced_works", [])
        n_refs = len(refs)
        # 追加“参考文献数量”日志
        st.session_state.sidebar_logs.append(f"参考文献数量：{n_refs}")
        if log_placeholder:
            log_placeholder.markdown("<br>".join(st.session_state.sidebar_logs), unsafe_allow_html=True)
        
        df_temp = pd.DataFrame({"refs": refs})
        df_temp = df_temp.explode('refs').reset_index(drop=True)
        all_refs = df_temp['refs'].tolist()
        df_temp['ref_else'] = df_temp['refs'].apply(lambda x: [r for r in all_refs if r != x])
        df_temp['ref_refs'] = df_temp['refs'].apply(lambda x: get_refs_by_id(x, show_detail_error, log_placeholder))
        df_temp['ref_links'] = df_temp.apply(lambda row: len(set(row['ref_else']) & set(row['ref_refs'])), axis=1)
        total_links = df_temp['ref_links'].sum()
        
        if n_refs < 2:
            density = 0.0
            red = 1.0
        else:
            density = 2 * total_links / (n_refs * (n_refs - 1))
            red = round(1 - density **(1/3), 4)
        
        return {
            "doi": doi,
            "refs": n_refs,
            "links": total_links,
            "density": round(density, 6),
            "RED": red
        }
    except Exception as e:
        if show_detail_error and log_placeholder:
            st.session_state.sidebar_logs.append(f"DOI {doi} 处理失败：{str(e)}")
            log_placeholder.markdown("<br>".join(st.session_state.sidebar_logs), unsafe_allow_html=True)
        return {
            "doi": doi,
            "refs": "获取失败",
            "links": "获取失败",
            "density": "获取失败",
            "RED": "获取失败"
        }

# --------------------------------------------------------------------------------
# Streamlit网页主逻辑（修改日志渲染方式）
# --------------------------------------------------------------------------------
def main():
    st.title("学术论文参考文献疏离度计算工具")
    st.write("📋 使用说明：上传含'doi'列的CSV文件 → 点击计算 → 下载结果（含doi、refs、links、density、RED）")
    st.write("ℹ️ 计算过程中侧边栏会实时显示执行进程")
    
    # 初始化会话状态
    if "calculated_results" not in st.session_state:
        st.session_state.calculated_results = None
    if "sidebar_logs" not in st.session_state:
        st.session_state.sidebar_logs = []
    if "valid_dois_count" not in st.session_state:
        st.session_state.valid_dois_count = 0
    
    # 侧边栏配置
    st.sidebar.title("调试配置")
    st.sidebar.write("依赖版本验证：")
    st.sidebar.write(f"pyalex: {__import__('pyalex').__version__}")
    st.sidebar.write(f"requests: {requests.__version__}")
    show_detail_error = st.sidebar.checkbox("显示详细错误（仅调试用）", value=False)
    
    # 侧边栏执行进程：用Markdown强制换行（核心修改）
    st.sidebar.title("执行进程")
    sidebar_log_placeholder = st.sidebar.empty()
    # 初始显示
    if st.session_state.sidebar_logs:
        sidebar_log_placeholder.markdown("<br>".join(st.session_state.sidebar_logs), unsafe_allow_html=True)
    else:
        sidebar_log_placeholder.write("等待计算开始...")
    
    # 文件上传
    uploaded_file = st.file_uploader("选择CSV文件", type="csv", help="文件必须包含名为'doi'的列，每行一个DOI号")
    
    if uploaded_file:
        try:
            df_upload = pd.read_csv(uploaded_file)
            if "doi" not in df_upload.columns:
                st.error("❌ 错误：上传的CSV文件必须包含名为'doi'的列！")
                return
            
            st.subheader("上传数据预览")
            st.write(df_upload[['doi']].head(), f"（共 {len(df_upload)} 行数据）")
            
            valid_dois = df_upload['doi'].dropna().astype(str).str.strip()
            st.session_state.valid_dois_count = len(valid_dois)
            st.write(f"✅ 筛选出 {st.session_state.valid_dois_count} 个有效DOI（已去除空值和无效格式）")
            
            # 开始计算按钮
            if st.button("开始计算", type="primary"):
                if st.session_state.valid_dois_count == 0:
                    st.warning("⚠️ 没有找到有效DOI，请检查文件内容！")
                    return
                
                # 重置日志和结果
                st.session_state.sidebar_logs = []
                st.session_state.calculated_results = []
                progress_bar = st.progress(0)
                sidebar_log_placeholder.write("计算开始...")
                
                # 批量处理（实时更新侧边栏，强制换行）
                for i, doi in enumerate(valid_dois, 1):
                    # 追加“正在处理”日志
                    process_log = f"【{i}/{st.session_state.valid_dois_count}】正在处理：{doi}"
                    st.session_state.sidebar_logs.append(process_log)
                    # 用Markdown的<br>强制换行显示
                    sidebar_log_placeholder.markdown("<br>".join(st.session_state.sidebar_logs), unsafe_allow_html=True)
                    
                    # 调用计算函数
                    result = get_refs_by_doi(doi, show_detail_error, sidebar_log_placeholder)
                    st.session_state.calculated_results.append(result)
                    
                    progress_bar.progress(i / st.session_state.valid_dois_count)
                    time.sleep(1)
            
            # 显示计算结果
            if st.session_state.calculated_results is not None and len(st.session_state.calculated_results) > 0:
                result_df = pd.DataFrame(st.session_state.calculated_results)
                st.subheader("计算结果")
                st.dataframe(result_df, use_container_width=True)
                
                # 下载功能
                csv_data = result_df.to_csv(index=False, encoding="utf_8_sig")
                st.download_button(
                    label="📥 下载结果",
                    data=csv_data,
                    file_name="参考文献疏离度计算结果.csv",
                    mime="text/csv"
                )
        
        except Exception as e:
            st.error(f"文件处理失败：{str(e)}")

if __name__ == "__main__":
    main()
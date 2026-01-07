import streamlit as st
import pandas as pd
import io
import datetime

# 設定頁面配置
st.set_page_config(page_title="Sustainability Assessment Tool", layout="wide")

# CSS 用於強制按鈕樣式 (置中、橘色)
st.markdown("""
    <style>
    /* 強制按鈕為橘色並調整文字顏色 */
    div.stButton > button {
        background-color: #FF8C00 !important; /* Dark Orange */
        color: white !important;
        border: none;
        padding: 10px 24px;
        font-size: 16px;
        border-radius: 8px;
        display: block;
        margin: 0 auto; /* 嘗試透過 CSS 置中 */
    }
    div.stButton > button:hover {
        background-color: #FF7000 !important; /* Darker Orange on hover */
        color: white !important;
    }
    /* 調整 Expander 標題字體 */
    .streamlit-expanderHeader {
        font-weight: bold;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

class SustainabilityAssessment:
    def __init__(self):
        self.init_session_state()
        self.setup_data()
        
    def init_session_state(self):
        # 0:Language, 1:Info, 2:Stakeholder, 3:Materiality, 4:TCFD, 5:HRDD, 6:Finish
        if 'step' not in st.session_state:
            st.session_state.step = 0 
        if 'language' not in st.session_state:
            st.session_state.language = 'zh' # 預設，稍後選擇
        if 'user_info' not in st.session_state:
            st.session_state.user_info = {}
        if 'data_stakeholder' not in st.session_state:
            st.session_state.data_stakeholder = None
        if 'data_materiality' not in st.session_state:
            st.session_state.data_materiality = None
        if 'selected_materiality_topics' not in st.session_state:
            st.session_state.selected_materiality_topics = []
        if 'data_tcfd' not in st.session_state:
            st.session_state.data_tcfd = {}
        if 'data_hrdd' not in st.session_state:
            st.session_state.data_hrdd = {}

    def setup_data(self):
        # 這裡定義所有的翻譯和固定選項資料
        self.texts = {
            "zh": {
                "step0_title": "語言選擇 / Language Selection",
                "step1_title": "基本資料 / Basic Information",
                "step2_title": "1. 利害關係人評估 (Stakeholder Assessment)",
                "step3_title": "2. 重大性議題評估 (Materiality Assessment)",
                "step4_title": "3. 氣候變遷風險評估 (TCFD)",
                "step5_title": "4. 人權盡職調查 (HRDD)",
                "name": "姓名",
                "dept": "部門",
                "next": "下一步 (Next Step)",
                "submit": "提交並下載結果",
                "error_fill_all": "請填寫所有欄位",
                "error_select_10": "請正好選擇 10 個議題",
                "download_btn": "下載 Excel 結果報告",
                "risk_section": "風險評估 (Risk Assessment)",
                "opp_section": "機會評估 (Opportunity Assessment)",
                "hrdd_sev_label": "嚴重度 (Severity)",
                "hrdd_prob_label": "可能性 (Probability)",
                "hrdd_vc_label": "價值鏈關聯 (Value Chain)"
            },
            "en": {
                "step0_title": "Language Selection",
                "step1_title": "Basic Information",
                "step2_title": "1. Stakeholder Assessment",
                "step3_title": "2. Materiality Assessment",
                "step4_title": "3. TCFD Assessment",
                "step5_title": "4. HRDD Assessment",
                "name": "Name",
                "dept": "Department",
                "next": "Next Step",
                "submit": "Submit & Download",
                "error_fill_all": "Please fill in all fields",
                "error_select_10": "Please select exactly 10 topics",
                "download_btn": "Download Result Excel",
                "risk_section": "Risk Assessment",
                "opp_section": "Opportunity Assessment",
                "hrdd_sev_label": "Severity",
                "hrdd_prob_label": "Probability",
                "hrdd_vc_label": "Value Chain Relevance"
            }
        }

        # Stakeholder Data
        self.sh_cols = ["Responsibility (責任)", "Influence (影響力)", "Tension (張力)", "Diverse Perspectives (多元觀點)", "Dependency (依賴性)"]
        self.sh_rows = ["Supplier (供應商)", "Customer (客戶)", "Employee (員工)", "Shareholder/Investor (股東/投資人)", "Government (政府機關)", "Community/School/NPO (社區/學校/非營利組織)"]
        
        # Materiality Topics
        self.mat_topics = [
            "Sustainability Strategy (永續策略)", "Ethical Management (誠信經營)", "Corporate Governance (公司治理)", 
            "Risk Management (風險控管)", "Compliance (法規遵循)", "Business Continuity (營運持續)", 
            "Information Security (資訊安全)", "Supplier Management (供應商管理)", "Customer Relationship (客戶關係)", 
            "Tax Policies (稅務政策)", "Operational Performance (營運績效)", "Innovation (創新與數位責任)", 
            "AI & Tech Transformation (AI與科技變革)", "Climate Adaptation (氣候變遷因應)", "Resource Management (環境與能資源)", 
            "Biodiversity (生物多樣性)", "Occupational Safety (職場健康與安全)", "Employee Development (員工培育)", 
            "Talent Retention (人才吸引留任)", "Social Care (社會關懷)", "Human Rights (人權平等)"
        ]

        # TCFD Topics
        self.tcfd_risks = [
            "溫室氣體排放定價上升 (Rising GHG pricing)",
            "對現有商品與服務的法規強制 (Mandates on existing products/services)",
            "現有商品與服務被低碳商品替代 (Substitution of existing products)",
            "新技術投資成效不佳 (Unsuccessful investment in new tech)",
            "低碳轉型的轉型成本 (Costs to transition to lower emissions)",
            "消費者行為改變 (Changing consumer behavior)",
            "氣候極端事件 (Extreme weather events)",
            "平均氣溫上升 (Rising mean temperatures)"
        ]
        self.tcfd_opps = [
            "使用低排放能源 (Use of lower-emission sources of energy)",
            "開發新低碳產品與服務 (Development of new products/services)",
            "低碳產品與服務-研發與創新 (R&D and Innovation)",
            "資源替代/多元化 (Resource substitutes/diversification)",
            "公共部門的激勵措施 (Public sector incentives)",
            "參與再生能源及高效能源計畫 (Participation in renewable energy markets)"
        ]

        # HRDD Topics
        self.hrdd_topics = [
            "強迫勞動/規模 (Forced Labor)",
            "人口販運/範圍 (Human Trafficking)",
            "童工/規模 (Child Labor)",
            "性騷擾/範圍 (Sexual Harassment)",
            "職場歧視(種族、性別等)/範圍 (Discrimination)",
            "同工不同酬勞/範圍 (Equal Pay)",
            "超時工作/規模 (Overtime)",
            "未落實職業安全衛生/規模 (Occupational Safety)",
            "剝奪自由結社權/範圍 (Freedom of Association)",
            "無定期勞資會議/範圍 (No Regular Meetings)",
            "無建立員工溝通管道/範圍 (No Communication Channels)",
            "未遵守現行個資法之規範/範圍 (Privacy Compliance)",
            "未落實個資保護之內部控制 (Internal Control for Privacy)",
            "不遵守與同意國際人權原則 (Intl Human Rights Principles)",
            "未對利害關係人宣達人權觀念 (Human Rights Communication)"
        ]
        
        # 定義純文字字串，用於 Tooltip
        self.hrdd_severity_def_text = """
        Severity Definitions (嚴重度定義):
        
        1: 基礎傷害/沒有對利害關係人造成負面影響/1年內可以補救
        2: 輕度傷害(需微修復)/對少部分(40%)利害關係人造成負面影響/1-3年內可以補救
        3: 中度傷害(需長時間修復)/對大部分(60%)利害關係人造成負面影響/3-5年內可以補救
        4: 嚴重傷害(需長時間修復)/對大部分(80%)利害關係人造成負面影響/5-7年內可以補救
        5: 造成物理殘疾或死亡/對所有利害關係人造成負面影響/10年以上才以補救
        """

    def get_text(self, key):
        return self.texts[st.session_state.language][key]

    # --- 輔助函式：置中橘色按鈕 ---
    def render_next_button(self, label, callback_func=None, args=None):
        st.write("") # Spacer
        st.write("") 
        # 使用 Columns 進行佈局置中：[1, 1, 1]
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            if st.button(label, use_container_width=True):
                if callback_func:
                    callback_func(args) if args else callback_func()
                else:
                    return True
        return False

    # --- UI Pages ---

    # PAGE 1: 語言選擇
    def render_language_selection(self):
        st.title("Language Selection / 語言選擇")
        
        # 置中顯示選項
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            with st.container(border=True):
                lang = st.radio(
                    "Please select your language / 請選擇語言",
                    options=["zh", "en"],
                    format_func=lambda x: "繁體中文 (Traditional Chinese)" if x == "zh" else "English",
                )
        
        def go_next():
            st.session_state.language = lang
            st.session_state.step = 1
            st.rerun()

        self.render_next_button("Next / 下一步", go_next)

    # PAGE 2: 基本資料
    def render_entry_portal(self):
        st.title(self.get_text("step1_title"))
        
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input(self.get_text("name"))
            with col2:
                dept = st.text_input(self.get_text("dept"))
        
        def go_next():
            if name and dept:
                st.session_state.user_info = {"Name": name, "Department": dept}
                st.session_state.step = 2
                st.rerun()
            else:
                st.error(self.get_text("error_fill_all"))

        self.render_next_button(self.get_text("next"), go_next)

    # PAGE 3: Stakeholder (修正：移除 Form 以避免 Enter 跳頁)
    def render_stakeholder(self):
        st.title(self.get_text("step2_title"))
        st.info("Score Definition: 0 (No relevant) - 5 (Very relevant)")
        st.caption("Pressing 'Enter' will only update the score. Please click the button at the bottom to proceed.")

        # 使用 Session State 暫存數據，如果還沒有就初始化
        if 'temp_stakeholder_data' not in st.session_state:
            st.session_state.temp_stakeholder_data = {}

        data = {}
        for row in self.sh_rows:
            st.subheader(row)
            cols = st.columns(len(self.sh_cols))
            row_data = {}
            for idx, col_name in enumerate(self.sh_cols):
                key = f"sh_{row}_{idx}"
                with cols[idx]:
                    # 不使用 form，直接 input
                    # 預設值邏輯：如果有存過就用存過的，沒有就預設 3
                    default_val = st.session_state.temp_stakeholder_data.get(key, 3)
                    val = st.number_input(
                        f"{col_name}", 
                        min_value=0, max_value=5, value=default_val, 
                        key=key
                    )
                    row_data[col_name] = val
                    st.session_state.temp_stakeholder_data[key] = val # 即時更新暫存
            data[row] = row_data
            st.divider()
        
        def go_next():
            st.session_state.data_stakeholder = pd.DataFrame.from_dict(data, orient='index')
            st.session_state.step = 3
            st.rerun()

        self.render_next_button(self.get_text("next"), go_next)

    # PAGE 4: Materiality
    def render_materiality(self):
        st.title(self.get_text("step3_title"))
        
        # Part A: Topic Selection
        if not st.session_state.selected_materiality_topics:
            st.subheader("Step 2.1: Select 10 Topics (選擇10個議題)")
            selected = []
            cols = st.columns(2)
            for i, topic in enumerate(self.mat_topics):
                with cols[i % 2]:
                    # 使用暫存 key 保持勾選狀態
                    is_checked = st.checkbox(topic, key=f"mat_topic_{i}")
                    if is_checked:
                        selected.append(topic)
            
            st.write(f"Selected: **{len(selected)}** / 10")
            
            def confirm_selection():
                if len(selected) == 10:
                    st.session_state.selected_materiality_topics = selected
                    st.rerun()
                else:
                    st.error(self.get_text("error_select_10"))
            
            self.render_next_button("Confirm Selection", confirm_selection)
        
        # Part B: Evaluation (移除 Reselect 按鈕)
        else:
            st.subheader("Step 2.2: Evaluate Selected Topics")
            
            # 不使用 Form，避免 UI 卡頓或過於擁擠，改為直接渲染
            results = []
            for topic in st.session_state.selected_materiality_topics:
                with st.expander(topic, expanded=True):
                    c1, c2, c3 = st.columns([1, 2, 2])
                    with c1:
                        status = st.radio("Status", ["Actual (Happened)", "Potential (Not happened)"], key=f"status_{topic}")
                    with c2:
                        value = st.slider("Value Creation (Opportunities) [1-5]", 1, 5, 3, key=f"val_{topic}")
                    with c3:
                        prob = st.slider("Probability (Likelihood) [1-5]", 1, 5, 3, key=f"prob_{topic}")
                    
                    results.append({
                        "Topic": topic,
                        "Status": status,
                        "Value Creation": value,
                        "Probability": prob
                    })
            
            def go_next():
                st.session_state.data_materiality = pd.DataFrame(results)
                st.session_state.step = 4
                st.rerun()

            self.render_next_button(self.get_text("next"), go_next)

    # PAGE 5: TCFD
    def render_tcfd(self):
        st.title(self.get_text("step4_title"))
        
        results = []
        
        # Section 1: Risks (明顯區隔)
        st.markdown(f"### 🛑 {self.get_text('risk_section')}")
        st.markdown("---") # 分隔線
        
        for item in self.tcfd_risks:
            st.markdown(f"**{item}**")
            c1, c2 = st.columns(2)
            with c1:
                # 修正：Label 只保留 Severity，不重複題目
                sev = st.slider("Severity", 1, 5, 3, key=f"tcfd_risk_sev_{item}")
            with c2:
                like = st.slider("Likelihood", 1, 5, 3, key=f"tcfd_risk_like_{item}")
            results.append({"Type": "Risk", "Topic": item, "Severity": sev, "Likelihood": like})
            st.write("") # Spacer

        st.write("")
        st.write("")
        
        # Section 2: Opportunities (明顯區隔)
        st.markdown(f"### 🌟 {self.get_text('opp_section')}")
        st.markdown("---") # 分隔線
        
        for item in self.tcfd_opps:
            st.markdown(f"**{item}**")
            c1, c2 = st.columns(2)
            with c1:
                sev = st.slider("Value/Severity", 1, 5, 3, key=f"tcfd_opp_sev_{item}")
            with c2:
                like = st.slider("Likelihood", 1, 5, 3, key=f"tcfd_opp_like_{item}")
            results.append({"Type": "Opportunity", "Topic": item, "Severity": sev, "Likelihood": like})
            st.write("")

        def go_next():
            st.session_state.data_tcfd = pd.DataFrame(results)
            st.session_state.step = 5
            st.rerun()

        self.render_next_button(self.get_text("next"), go_next)

    # PAGE 6: HRDD
    def render_hrdd(self):
        st.title(self.get_text("step5_title"))
        
        # 修正：定義不在上方顯示，而是嵌入在 Severity 的 Tooltip 中
        
        results = []
        st.subheader("Human Rights Topics Assessment")
        
        for item in self.hrdd_topics:
            with st.container(border=True):
                st.markdown(f"##### {item}")
                
                # 修正：欄位順序 Value Chain (左) -> Severity (中) -> Probability (右)
                c1, c2, c3 = st.columns([1.5, 2, 2])
                
                with c1:
                    st.write(f"**{self.get_text('hrdd_vc_label')}**")
                    is_supp = st.checkbox("Supplier", key=f"hrdd_sup_{item}")
                    is_cust = st.checkbox("Customer", key=f"hrdd_cust_{item}")

                with c2:
                    # 修正：Severity 標籤旁加入小問號 (help)，點擊/懸停顯示定義
                    sev = st.select_slider(
                        label=self.get_text('hrdd_sev_label'),
                        options=[1, 2, 3, 4, 5], 
                        value=3,
                        key=f"hrdd_sev_{item}",
                        help=self.hrdd_severity_def_text # 這裡嵌入定義
                    )
                
                with c3:
                    prob = st.select_slider(
                        label=self.get_text('hrdd_prob_label'),
                        options=[1, 2, 3, 4, 5], 
                        value=3,
                        key=f"hrdd_prob_{item}"
                    )
                
                results.append({
                    "Topic": item,
                    "Severity": sev,
                    "Probability": prob,
                    "Supplier (Value Chain)": 1 if is_supp else 0,
                    "Customer (Value Chain)": 1 if is_cust else 0
                })
        
        def go_next():
            st.session_state.data_hrdd = pd.DataFrame(results)
            st.session_state.step = 6
            st.rerun()

        self.render_next_button("Finish Assessment", go_next)

    # PAGE 7: FINISH
    def generate_excel(self):
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        
        # Sheet 1: Stakeholder
        sh_df = st.session_state.data_stakeholder.copy()
        sh_df.insert(0, "Department", st.session_state.user_info["Department"])
        sh_df.insert(0, "Name", st.session_state.user_info["Name"])
        sh_df.to_excel(writer, sheet_name='Stakeholder')
        
        # Sheet 2: Materiality
        mat_df = st.session_state.data_materiality.copy()
        mat_df.insert(0, "Department", st.session_state.user_info["Department"])
        mat_df.insert(0, "Name", st.session_state.user_info["Name"])
        mat_df.to_excel(writer, sheet_name='Materiality', index=False)
        
        # Sheet 3: TCFD
        tcfd_df = st.session_state.data_tcfd.copy()
        tcfd_df.insert(0, "Department", st.session_state.user_info["Department"])
        tcfd_df.insert(0, "Name", st.session_state.user_info["Name"])
        tcfd_df.to_excel(writer, sheet_name='TCFD', index=False)
        
        # Sheet 4: HRDD
        hrdd_df = st.session_state.data_hrdd.copy()
        hrdd_df.insert(0, "Department", st.session_state.user_info["Department"])
        hrdd_df.insert(0, "Name", st.session_state.user_info["Name"])
        hrdd_df.to_excel(writer, sheet_name='HRDD', index=False)
        
        writer.close()
        processed_data = output.getvalue()
        return processed_data

    def render_finish(self):
        st.balloons()
        st.title("Assessment Completed! / 評估完成")
        st.success("All steps finished. Please download your report below.")
        
        excel_data = self.generate_excel()
        file_name = f"{st.session_state.user_info['Name']}_{st.session_state.user_info['Department']}_Result.xlsx"
        
        # 這裡的按鈕也需要置中與橘色
        st.write("")
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            st.download_button(
                label=self.get_text("download_btn"),
                data=excel_data,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
            st.write("")
            if st.button("Start Over / 重新開始", use_container_width=True):
                st.session_state.clear()
                st.rerun()

    def run(self):
        if st.session_state.step == 0:
            self.render_language_selection()
        elif st.session_state.step == 1:
            self.render_entry_portal()
        elif st.session_state.step == 2:
            self.render_stakeholder()
        elif st.session_state.step == 3:
            self.render_materiality()
        elif st.session_state.step == 4:
            self.render_tcfd()
        elif st.session_state.step == 5:
            self.render_hrdd()
        elif st.session_state.step == 6:
            self.render_finish()

if __name__ == "__main__":
    app = SustainabilityAssessment()
    app.run()

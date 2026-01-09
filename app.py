import streamlit as st
import pandas as pd
import io

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
        margin: 0 auto;
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
    /* 調整 Radio Button 的字體大小 */
    .stRadio label {
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
            st.session_state.language = 'zh' # 預設
        if 'user_info' not in st.session_state:
            st.session_state.user_info = {}
        # 暫存區
        if 'temp_stakeholder_data' not in st.session_state:
            st.session_state.temp_stakeholder_data = {}
        if 'selected_materiality_indices' not in st.session_state:
            st.session_state.selected_materiality_indices = [] # 改存索引 (Index) 以便中英互轉
            
        # 結果區
        if 'data_stakeholder' not in st.session_state:
            st.session_state.data_stakeholder = None
        if 'data_materiality' not in st.session_state:
            st.session_state.data_materiality = None
        if 'data_tcfd' not in st.session_state:
            st.session_state.data_tcfd = {}
        if 'data_hrdd' not in st.session_state:
            st.session_state.data_hrdd = {}

    def setup_data(self):
        # ---------------------------------------------------------
        # 1. 介面文字 (UI Labels)
        # ---------------------------------------------------------
        self.ui_texts = {
            "zh": {
                "step0_title": "語言選擇 / Language Selection",
                "step1_title": "基本資料",
                "step2_title": "1. 利害關係人評估 (Stakeholder Assessment)",
                "step3_title": "2. 重大性議題評估 (Materiality Assessment)",
                "step4_title": "3. 氣候變遷風險評估 (TCFD)",
                "step5_title": "4. 人權盡職調查 (HRDD)",
                "name_label": "姓名",
                "dept_label": "部門",
                "next_btn": "下一步",
                "finish_btn": "完成評估並下載",
                "error_fill": "請填寫所有欄位",
                "error_select_10": "請正好選擇 10 個議題",
                "download_btn": "下載 Excel 結果報告",
                "start_over": "重新開始",
                "score_def": "評分定義：0 (無關) - 5 (高度相關)",
                "enter_note": "按下 'Enter' 僅會更新數值，請點擊下方按鈕繼續。",
                "mat_select_instr": "步驟 2.1: 請勾選 10 個議題",
                "mat_eval_instr": "步驟 2.2: 評估已選議題",
                "confirm_sel": "確認選擇",
                "status_label": "狀態",
                "val_label": "價值創造 (機會) [1-5]",
                "prob_label": "可能性 (機率) [1-5]",
                "status_opts": ["已發生 (Actual)", "潛在 (Potential)"],
                "risk_header": "🛑 風險評估 (Risk)",
                "opp_header": "🌟 機會評估 (Opportunity)",
                "sev_label": "嚴重度",
                "like_label": "可能性",
                "hrdd_vc": "價值鏈關聯",
                "hrdd_sup": "供應商",
                "hrdd_cust": "客戶",
                "hrdd_sev": "嚴重度",
                "hrdd_prob": "可能性"
            },
            "en": {
                "step0_title": "Language Selection",
                "step1_title": "Basic Information",
                "step2_title": "1. Stakeholder Assessment",
                "step3_title": "2. Materiality Assessment",
                "step4_title": "3. TCFD Assessment",
                "step5_title": "4. Human Rights Due Diligence (HRDD)",
                "name_label": "Name",
                "dept_label": "Department",
                "next_btn": "Next Step",
                "finish_btn": "Finish & Download",
                "error_fill": "Please fill in all fields",
                "error_select_10": "Please select exactly 10 topics",
                "download_btn": "Download Result Excel",
                "start_over": "Start Over",
                "score_def": "Score Definition: 0 (No relevant) - 5 (Very relevant)",
                "enter_note": "Pressing 'Enter' only updates the score. Click the button below to proceed.",
                "mat_select_instr": "Step 2.1: Select 10 Topics",
                "mat_eval_instr": "Step 2.2: Evaluate Selected Topics",
                "confirm_sel": "Confirm Selection",
                "status_label": "Status",
                "val_label": "Value Creation (Opp) [1-5]",
                "prob_label": "Probability (Likelihood) [1-5]",
                "status_opts": ["Actual (Happened)", "Potential (Not happened)"],
                "risk_header": "🛑 Risk Assessment",
                "opp_header": "🌟 Opportunity Assessment",
                "sev_label": "Severity",
                "like_label": "Likelihood",
                "hrdd_vc": "Value Chain Relevance",
                "hrdd_sup": "Supplier",
                "hrdd_cust": "Customer",
                "hrdd_sev": "Severity",
                "hrdd_prob": "Probability"
            }
        }

        # ---------------------------------------------------------
        # 2. 評估內容資料 (Content Data) - 中英分流
        # ---------------------------------------------------------
        self.content = {
            "zh": {
                "sh_rows": ["供應商", "客戶", "員工", "股東/投資人", "政府機關", "社區/學校/非營利組織"],
                "sh_cols": ["責任", "影響力", "張力", "多元觀點", "依賴性"],
                
                "mat_topics": [
                    "永續策略", "誠信經營", "公司治理", "風險控管", "法規遵循", "營運持續管理", 
                    "資訊安全", "供應商管理", "客戶關係管理", "稅務政策", "營運績效", 
                    "創新與數位責任", "人工智慧與科技變革", "氣候變遷因應", "環境與能資源管理", 
                    "生物多樣性", "職場健康與安全", "員工培育與職涯發展", "人才吸引與留任", 
                    "社會關懷與鄰里促進", "人權平等"
                ],

                "tcfd_risks": [
                    "溫室氣體排放定價上升", "對現有商品與服務的法規強制", "現有商品與服務被低碳商品替代",
                    "新技術投資成效不佳", "低碳轉型的轉型成本", "消費者行為改變",
                    "氣候極端事件", "平均氣溫上升"
                ],
                "tcfd_opps": [
                    "使用低排放能源", "開發新低碳產品與服務", "低碳產品與服務-研發與創新",
                    "資源替代/多元化", "公共部門的激勵措施", "參與再生能源及高效能源計畫"
                ],

                "hrdd_topics": [
                    "強迫勞動/規模", "人口販運/範圍", "童工/規模", "性騷擾/範圍",
                    "職場歧視(種族、性別等)/範圍", "同工不同酬勞/範圍", "超時工作/規模",
                    "未落實職業安全衛生/規模", "剝奪自由結社權/範圍", "無定期勞資會議/範圍",
                    "無建立員工溝通管道/範圍", "未遵守現行個資法之規範/範圍", "未落實個資保護之內部控制",
                    "不遵守與同意國際人權原則", "未對利害關係人宣達人權觀念"
                ],
                "hrdd_def": """
                **嚴重度定義 (Severity):**
                
                * **1**: 基礎傷害/沒有對利害關係人造成負面影響/1年內可以補救
                * **2**: 輕度傷害(需微修復)/對少部分(40%)利害關係人造成負面影響/1-3年內可以補救
                * **3**: 中度傷害(需長時間修復)/對大部分(60%)利害關係人造成負面影響/3-5年內可以補救
                * **4**: 嚴重傷害(需長時間修復)/對大部分(80%)利害關係人造成負面影響/5-7年內可以補救
                * **5**: 造成物理殘疾或死亡/對所有利害關係人造成負面影響/10年以上才以補救
                """
            },
            "en": {
                "sh_rows": ["Supplier", "Customer", "Employee", "Shareholder/Investor", "Government", "Community/School/NPO"],
                "sh_cols": ["Responsibility", "Influence", "Tension", "Diverse Perspectives", "Dependency"],
                
                "mat_topics": [
                    "Sustainability Strategy", "Ethical Management", "Corporate Governance", "Risk Management",
                    "Compliance", "Business Continuity Management", "Information Security", "Supplier Management",
                    "Customer Relationship Management", "Tax Policies", "Operational Performance", 
                    "Innovation and Digital Responsibility", "AI and Technological Transformation", 
                    "Climate Change Adaptation", "Environment and Resource Management", "Biodiversity", 
                    "Workplace Health and Safety", "Employee Cultivation and Career Development", 
                    "Talent Attraction and Retention", "Social Care and Community Promotion", "Equal Human Rights"
                ],

                "tcfd_risks": [
                    "Rising GHG pricing", "Mandates on and regulation of existing products and services",
                    "Substitution of existing products and services with lower emissions options",
                    "Unsuccessful investment in new technologies", "Costs to transition to lower emissions technology",
                    "Changing consumer behavior", "Extreme weather events", "Rising mean temperatures"
                ],
                "tcfd_opps": [
                    "Use of lower-emission sources of energy", "Development and/or expansion of low emission goods and services",
                    "R&D and Innovation", "Use of more efficient production and distribution processes",
                    "Public sector incentives", "Participation in renewable energy markets"
                ],

                "hrdd_topics": [
                    "Forced Labor (Scale)", "Human Trafficking (Scope)", "Child Labor (Scale)", "Sexual Harassment (Scope)",
                    "Discrimination (Race, Gender, etc.) (Scope)", "Unequal Pay (Scope)", "Excessive Overtime (Scale)",
                    "Occupational Health & Safety Violations (Scale)", "Freedom of Association Violations (Scope)",
                    "Lack of Regular Labor-Management Meetings (Scope)", "Lack of Employee Communication Channels (Scope)",
                    "Non-compliance with Privacy Laws (Scope)", "Lack of Internal Controls for Data Privacy",
                    "Non-compliance with Int'l Human Rights Principles", "Failure to Communicate Human Rights Concepts"
                ],
                "hrdd_def": """
                **Severity Definitions:**
                
                * **1**: Basic injury / No negative impact on stakeholders / Remediable within 1 year
                * **2**: Minor injury (minor repair needed) / Negative impact on minority (40%) / Remediable within 1-3 years
                * **3**: Moderate injury (long repair needed) / Negative impact on majority (60%) / Remediable within 3-5 years
                * **4**: Severe injury (long repair needed) / Negative impact on vast majority (80%) / Remediable within 5-7 years
                * **5**: Physical disability or death / Negative impact on all stakeholders / Remediable only after 10+ years
                """
            }
        }

    def get_ui(self, key):
        return self.ui_texts[st.session_state.language][key]

    def get_content(self, key):
        return self.content[st.session_state.language][key]
    
    # 取得英文內容 (強制用於資料儲存)
    def get_en_content(self, key):
        return self.content['en'][key]

    # --- 輔助函式：置中橘色按鈕 ---
    def render_next_button(self, label, callback_func=None, args=None):
        st.write("") 
        st.write("") 
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            if st.button(label, use_container_width=True):
                if callback_func:
                    callback_func(args) if args else callback_func()
                else:
                    return True
        return False

    # --- UI Pages ---

    # PAGE 0: 語言選擇
    def render_language_selection(self):
        st.title(self.ui_texts['en']['step0_title']) 
        
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

    # PAGE 1: 基本資料
    def render_entry_portal(self):
        st.title(self.get_ui("step1_title"))
        
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input(self.get_ui("name_label"))
            with col2:
                dept = st.text_input(self.get_ui("dept_label"))
        
        def go_next():
            if name and dept:
                # User info 保留原始輸入
                st.session_state.user_info = {"Name": name, "Department": dept}
                st.session_state.step = 2
                st.rerun()
            else:
                st.error(self.get_ui("error_fill"))

        self.render_next_button(self.get_ui("next_btn"), go_next)

    # PAGE 2: Stakeholder
    def render_stakeholder(self):
        st.title(self.get_ui("step2_title"))
        st.info(self.get_ui("score_def"))
        st.caption(self.get_ui("enter_note"))

        # UI 顯示用的清單
        rows_ui = self.get_content("sh_rows")
        cols_names_ui = self.get_content("sh_cols")
        
        # 資料儲存用的清單 (強制英文)
        rows_en = self.get_en_content("sh_rows")
        cols_names_en = self.get_en_content("sh_cols")

        data = {}
        
        # 使用 enumerate 同時取得索引 (idx) 和 UI 顯示名稱
        for r_idx, row_name_ui in enumerate(rows_ui):
            st.subheader(row_name_ui) # 顯示：中文或英文
            cols = st.columns(len(cols_names_ui))
            
            # 對應的英文名稱 (用於 Key)
            row_name_en = rows_en[r_idx]
            row_data = {}
            
            for c_idx, col_name_ui in enumerate(cols_names_ui):
                # 對應的英文欄位 (用於 Data)
                col_name_en = cols_names_en[c_idx]
                
                key = f"sh_{r_idx}_{c_idx}"
                with cols[c_idx]:
                    val = st.number_input(
                        f"{col_name_ui}", # 顯示：中文或英文
                        min_value=0, max_value=5, value=3, 
                        key=key
                    )
                    # 儲存：使用英文欄位名
                    row_data[col_name_en] = val
            
            # 儲存：使用英文列名
            data[row_name_en] = row_data
            st.divider()
        
        def go_next():
            st.session_state.data_stakeholder = pd.DataFrame.from_dict(data, orient='index')
            st.session_state.step = 3
            st.rerun()

        self.render_next_button(self.get_ui("next_btn"), go_next)

    # PAGE 3: Materiality
    def render_materiality(self):
        st.title(self.get_ui("step3_title"))
        
        topics_ui = self.get_content("mat_topics")
        topics_en = self.get_en_content("mat_topics") # 用於後續儲存
        
        # Part A: Topic Selection
        if not st.session_state.selected_materiality_indices:
            st.subheader(self.get_ui("mat_select_instr"))
            selected_indices = []
            cols = st.columns(2)
            
            for i, topic in enumerate(topics_ui):
                with cols[i % 2]:
                    # 顯示 UI 語言
                    if st.checkbox(topic, key=f"mat_topic_{i}"):
                        selected_indices.append(i) # 只存索引，方便之後轉換
            
            st.write(f"Selected: **{len(selected_indices)}** / 10")
            
            def confirm_selection():
                if len(selected_indices) == 10:
                    st.session_state.selected_materiality_indices = selected_indices
                    st.rerun()
                else:
                    st.error(self.get_ui("error_select_10"))
            
            self.render_next_button(self.get_ui("confirm_sel"), confirm_selection)
        
        # Part B: Evaluation
        else:
            st.subheader(self.get_ui("mat_eval_instr"))
            results = []
            status_options_ui = self.get_ui("status_opts")
            
            # 定義 Status 映射到英文
            # status_options_ui[0] 是 "已發生 (Actual)" -> 存為 "Actual"
            # status_options_ui[1] 是 "潛在 (Potential)" -> 存為 "Potential"
            status_map = {
                status_options_ui[0]: "Actual",
                status_options_ui[1]: "Potential"
            }
            
            for i in st.session_state.selected_materiality_indices:
                # 取得對應語言的 Topic 用於顯示，英文 Topic 用於儲存
                topic_display = topics_ui[i]
                topic_save = topics_en[i]
                
                with st.expander(topic_display, expanded=True):
                    c1, c2, c3 = st.columns([1, 2, 2])
                    with c1:
                        status_ui = st.radio(self.get_ui("status_label"), status_options_ui, key=f"mat_stat_{i}")
                    with c2:
                        value = st.slider(self.get_ui("val_label"), 1, 5, 3, key=f"mat_val_{i}")
                    with c3:
                        prob = st.slider(self.get_ui("prob_label"), 1, 5, 3, key=f"mat_prob_{i}")
                    
                    results.append({
                        "Topic": topic_save, # 存英文
                        "Status": status_map[status_ui], # 存英文
                        "Value Creation": value,
                        "Probability": prob
                    })
            
            def go_next():
                st.session_state.data_materiality = pd.DataFrame(results)
                st.session_state.step = 4
                st.rerun()

            self.render_next_button(self.get_ui("next_btn"), go_next)

    # PAGE 4: TCFD
    def render_tcfd(self):
        st.title(self.get_ui("step4_title"))
        results = []
        
        # UI 清單
        risks_ui = self.get_content("tcfd_risks")
        opps_ui = self.get_content("tcfd_opps")
        # 英文清單 (儲存用)
        risks_en = self.get_en_content("tcfd_risks")
        opps_en = self.get_en_content("tcfd_opps")
        
        sev_txt = self.get_ui("sev_label")
        like_txt = self.get_ui("like_label")
        
        # Risks
        st.markdown(f"### {self.get_ui('risk_header')}")
        st.markdown("---")
        for i, item_ui in enumerate(risks_ui):
            st.markdown(f"**{item_ui}**")
            c1, c2 = st.columns(2)
            with c1:
                sev = st.slider(sev_txt, 1, 5, 3, key=f"risk_s_{i}")
            with c2:
                like = st.slider(like_txt, 1, 5, 3, key=f"risk_l_{i}")
            
            # 儲存英文 Topic
            results.append({"Type": "Risk", "Topic": risks_en[i], "Severity": sev, "Likelihood": like})
            st.write("") 

        st.write("")
        st.write("")
        
        # Opportunities
        st.markdown(f"### {self.get_ui('opp_header')}")
        st.markdown("---")
        for i, item_ui in enumerate(opps_ui):
            st.markdown(f"**{item_ui}**")
            c1, c2 = st.columns(2)
            with c1:
                sev = st.slider(sev_txt, 1, 5, 3, key=f"opp_s_{i}")
            with c2:
                like = st.slider(like_txt, 1, 5, 3, key=f"opp_l_{i}")
            
            # 儲存英文 Topic
            results.append({"Type": "Opportunity", "Topic": opps_en[i], "Severity": sev, "Likelihood": like})
            st.write("")

        def go_next():
            st.session_state.data_tcfd = pd.DataFrame(results)
            st.session_state.step = 5
            st.rerun()

        self.render_next_button(self.get_ui("next_btn"), go_next)

    # PAGE 5: HRDD
    def render_hrdd(self):
        st.title(self.get_ui("step5_title"))
        
        topics_ui = self.get_content("hrdd_topics")
        topics_en = self.get_en_content("hrdd_topics") # 儲存用
        
        def_text = self.get_content("hrdd_def")
        
        results = []
        
        for i, item_ui in enumerate(topics_ui):
            with st.container(border=True):
                st.markdown(f"##### {item_ui}")
                c1, c2, c3 = st.columns([1.5, 2, 2])
                
                with c1:
                    st.write(f"**{self.get_ui('hrdd_vc')}**")
                    is_supp = st.checkbox(self.get_ui('hrdd_sup'), key=f"hr_sup_{i}")
                    is_cust = st.checkbox(self.get_ui('hrdd_cust'), key=f"hr_cust_{i}")

                with c2:
                    sev = st.select_slider(
                        label=self.get_ui('hrdd_sev'),
                        options=[1, 2, 3, 4, 5], 
                        value=3,
                        key=f"hr_sev_{i}",
                        help=def_text
                    )
                
                with c3:
                    prob = st.select_slider(
                        label=self.get_ui('hrdd_prob'),
                        options=[1, 2, 3, 4, 5], 
                        value=3,
                        key=f"hr_prob_{i}"
                    )
                
                # 儲存英文資訊
                results.append({
                    "Topic": topics_en[i],
                    "Severity": sev,
                    "Probability": prob,
                    "Supplier (Value Chain)": 1 if is_supp else 0,
                    "Customer (Value Chain)": 1 if is_cust else 0
                })
        
        def go_next():
            st.session_state.data_hrdd = pd.DataFrame(results)
            st.session_state.step = 6
            st.rerun()

        self.render_next_button(self.get_ui("finish_btn"), go_next)

    # PAGE 6: FINISH
    def generate_excel(self):
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        
        # 強制使用英文欄位頭 (Headers)
        name_col = "Name"
        dept_col = "Department"
        
        # Sheet 1: Stakeholder
        sh_df = st.session_state.data_stakeholder.copy()
        sh_df.insert(0, dept_col, st.session_state.user_info["Department"])
        sh_df.insert(0, name_col, st.session_state.user_info["Name"])
        sh_df.to_excel(writer, sheet_name='Stakeholder')
        
        # Sheet 2: Materiality
        mat_df = st.session_state.data_materiality.copy()
        mat_df.insert(0, dept_col, st.session_state.user_info["Department"])
        mat_df.insert(0, name_col, st.session_state.user_info["Name"])
        mat_df.to_excel(writer, sheet_name='Materiality', index=False)
        
        # Sheet 3: TCFD
        tcfd_df = st.session_state.data_tcfd.copy()
        tcfd_df.insert(0, dept_col, st.session_state.user_info["Department"])
        tcfd_df.insert(0, name_col, st.session_state.user_info["Name"])
        tcfd_df.to_excel(writer, sheet_name='TCFD', index=False)
        
        # Sheet 4: HRDD
        hrdd_df = st.session_state.data_hrdd.copy()
        hrdd_df.insert(0, dept_col, st.session_state.user_info["Department"])
        hrdd_df.insert(0, name_col, st.session_state.user_info["Name"])
        hrdd_df.to_excel(writer, sheet_name='HRDD', index=False)
        
        writer.close()
        return output.getvalue()

    def render_finish(self):
        st.balloons()
        st.title("Assessment Completed!")
        
        excel_data = self.generate_excel()
        file_name = f"{st.session_state.user_info['Name']}_{st.session_state.user_info['Department']}_Result.xlsx"
        
        st.write("")
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            st.download_button(
                label=self.get_ui("download_btn"),
                data=excel_data,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
            st.write("")
            if st.button(self.get_ui("start_over"), use_container_width=True):
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

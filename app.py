import streamlit as st
import pandas as pd
import io
import datetime

# 設定頁面配置
st.set_page_config(page_title="Sustainability Assessment Tool", layout="wide")

class SustainabilityAssessment:
    def __init__(self):
        self.init_session_state()
        self.setup_data()
        
    def init_session_state(self):
        # 初始化狀態變數
        if 'step' not in st.session_state:
            st.session_state.step = 0  # 0:Entry, 1:Stakeholder, 2:Materiality, 3:TCFD, 4:HRDD, 5:Finish
        if 'language' not in st.session_state:
            st.session_state.language = 'zh'
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
                "title": "永續發展綜合評估問卷",
                "step0_title": "基本資料 Entry Portal",
                "step1_title": "1. 利害關係人評估 (Stakeholder Assessment)",
                "step2_title": "2. 重大性議題評估 (Materiality Assessment)",
                "step3_title": "3. 氣候變遷風險評估 (TCFD)",
                "step4_title": "4. 人權盡職調查 (HRDD)",
                "name": "姓名",
                "dept": "部門",
                "lang_select": "選擇語言 (選定後不可更改)",
                "next": "下一步",
                "submit": "提交並下載結果",
                "error_fill_all": "請填寫所有欄位",
                "error_select_10": "請正好選擇 10 個議題",
                "download_btn": "下載 Excel 結果報告"
            },
            "en": {
                "title": "Sustainability Integrated Assessment",
                "step0_title": "Entry Portal",
                "step1_title": "1. Stakeholder Assessment",
                "step2_title": "2. Materiality Assessment",
                "step3_title": "3. TCFD Assessment",
                "step4_title": "4. HRDD Assessment",
                "name": "Name",
                "dept": "Department",
                "lang_select": "Select Language (Not adjustable afterwards)",
                "next": "Next Step",
                "submit": "Submit & Download",
                "error_fill_all": "Please fill in all fields",
                "error_select_10": "Please select exactly 10 topics",
                "download_btn": "Download Result Excel"
            }
        }

        # Stakeholder Data
        self.sh_cols = ["Responsibility (責任)", "Influence (影響力)", "Tension (張力)", "Diverse Perspectives (多元觀點)", "Dependency (依賴性)"]
        self.sh_rows = ["Supplier (供應商)", "Customer (客戶)", "Employee (員工)", "Shareholder/Investor (股東/投資人)", "Government (政府機關)", "Community/School/NPO (社區/學校/非營利組織)"]
        
        # Materiality Topics (Mixed from your old code source)
        self.mat_topics = [
            "Sustainability Strategy (永續策略)", "Ethical Management (誠信經營)", "Corporate Governance (公司治理)", 
            "Risk Management (風險控管)", "Compliance (法規遵循)", "Business Continuity (營運持續)", 
            "Information Security (資訊安全)", "Supplier Management (供應商管理)", "Customer Relationship (客戶關係)", 
            "Tax Policies (稅務政策)", "Operational Performance (營運績效)", "Innovation (創新與數位責任)", 
            "AI & Tech Transformation (AI與科技變革)", "Climate Adaptation (氣候變遷因應)", "Resource Management (環境與能資源)", 
            "Biodiversity (生物多樣性)", "Occupational Safety (職場健康與安全)", "Employee Development (員工培育)", 
            "Talent Retention (人才吸引留任)", "Social Care (社會關懷)", "Human Rights (人權平等)"
        ]

        # TCFD Topics (Parsed from Image)
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

        # HRDD Topics (Parsed from Image)
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
        
        self.hrdd_severity_def = """
        **Severity Definitions (嚴重度定義):**
        * **1**: 基礎傷害/沒有對利害關係人造成負面影響/1年內可以補救
        * **2**: 輕度傷害(需微修復)/對少部分(40%)利害關係人造成負面影響/1-3年內可以補救
        * **3**: 中度傷害(需長時間修復)/對大部分(60%)利害關係人造成負面影響/3-5年內可以補救
        * **4**: 嚴重傷害(需長時間修復)/對大部分(80%)利害關係人造成負面影響/5-7年內可以補救
        * **5**: 造成物理殘疾或死亡/對所有利害關係人造成負面影響/10年以上才以補救
        """

    def get_text(self, key):
        return self.texts[st.session_state.language][key]

    # --- UI Pages ---

    def render_entry_portal(self):
        st.title(self.get_text("step0_title"))
        
        with st.container(border=True):
            # Language Selection
            lang = st.radio(
                "Language / 語言",
                options=["zh", "en"],
                format_func=lambda x: "繁體中文" if x == "zh" else "English",
                horizontal=True,
                index=0 if st.session_state.language == 'zh' else 1
            )
            st.session_state.language = lang
            st.caption(self.get_text("lang_select"))
            
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input(self.get_text("name"))
            with col2:
                dept = st.text_input(self.get_text("dept"))
                
            if st.button(self.get_text("next"), type="primary"):
                if name and dept:
                    st.session_state.user_info = {"Name": name, "Department": dept}
                    st.session_state.step = 1
                    st.rerun()
                else:
                    st.error(self.get_text("error_fill_all"))

    def render_stakeholder(self):
        st.title(self.get_text("step1_title"))
        st.info("Score Definition: 0 (No relevant) - 5 (Very relevant)")
        
        # 使用 Form 來收集矩陣數據
        with st.form("stakeholder_form"):
            data = {}
            for row in self.sh_rows:
                st.subheader(row)
                cols = st.columns(len(self.sh_cols))
                row_data = {}
                for idx, col_name in enumerate(self.sh_cols):
                    with cols[idx]:
                        # 預設值為 3 (Normal)
                        val = st.number_input(
                            f"{col_name}", 
                            min_value=0, max_value=5, value=3, 
                            key=f"sh_{row}_{idx}"
                        )
                        row_data[col_name] = val
                data[row] = row_data
            
            submitted = st.form_submit_button(self.get_text("next"))
            if submitted:
                st.session_state.data_stakeholder = pd.DataFrame.from_dict(data, orient='index')
                st.session_state.step = 2
                st.rerun()

    def render_materiality(self):
        st.title(self.get_text("step2_title"))
        
        # Part A: Topic Selection
        if not st.session_state.selected_materiality_topics:
            st.subheader("Step 2.1: Select 10 Topics (選擇10個議題)")
            selected = []
            cols = st.columns(2)
            for i, topic in enumerate(self.mat_topics):
                with cols[i % 2]:
                    if st.checkbox(topic, key=f"mat_topic_{i}"):
                        selected.append(topic)
            
            st.write(f"Selected: **{len(selected)}** / 10")
            
            if st.button("Confirm Selection"):
                if len(selected) == 10:
                    st.session_state.selected_materiality_topics = selected
                    st.rerun()
                else:
                    st.error(self.get_text("error_select_10"))
        
        # Part B: Evaluation
        else:
            st.subheader("Step 2.2: Evaluate Selected Topics")
            with st.form("mat_eval_form"):
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
                
                if st.form_submit_button(self.get_text("next")):
                    st.session_state.data_materiality = pd.DataFrame(results)
                    st.session_state.step = 3
                    st.rerun()
            
            if st.button("Reselect Topics"):
                st.session_state.selected_materiality_topics = []
                st.rerun()

    def render_tcfd(self):
        st.title(self.get_text("step3_title"))
        
        with st.form("tcfd_form"):
            results = []
            
            st.subheader("Risk Assessment (風險評估)")
            for item in self.tcfd_risks:
                st.markdown(f"**{item}**")
                c1, c2 = st.columns(2)
                with c1:
                    sev = st.slider(f"Severity ({item})", 1, 5, 3, key=f"tcfd_risk_sev_{item}")
                with c2:
                    like = st.slider(f"Likelihood ({item})", 1, 5, 3, key=f"tcfd_risk_like_{item}")
                results.append({"Type": "Risk", "Topic": item, "Severity": sev, "Likelihood": like})
                st.divider()

            st.subheader("Opportunity Assessment (機會評估)")
            for item in self.tcfd_opps:
                st.markdown(f"**{item}**")
                c1, c2 = st.columns(2)
                with c1:
                    sev = st.slider(f"Value/Severity ({item})", 1, 5, 3, key=f"tcfd_opp_sev_{item}")
                with c2:
                    like = st.slider(f"Likelihood ({item})", 1, 5, 3, key=f"tcfd_opp_like_{item}")
                results.append({"Type": "Opportunity", "Topic": item, "Severity": sev, "Likelihood": like})
                st.divider()
                
            if st.form_submit_button(self.get_text("next")):
                st.session_state.data_tcfd = pd.DataFrame(results)
                st.session_state.step = 4
                st.rerun()

    def render_hrdd(self):
        st.title(self.get_text("step4_title"))
        
        # Display Definition
        st.info(self.hrdd_severity_def)
        
        with st.form("hrdd_form"):
            results = []
            st.subheader("Human Rights Topics Assessment")
            
            for item in self.hrdd_topics:
                with st.container(border=True):
                    st.markdown(f"##### {item}")
                    c1, c2, c3 = st.columns([2, 2, 2])
                    
                    with c1:
                        sev = st.select_slider(
                            "Severity (嚴重度)", 
                            options=[1, 2, 3, 4, 5], 
                            value=3,
                            key=f"hrdd_sev_{item}"
                        )
                    with c2:
                        prob = st.select_slider(
                            "Probability (可能性)", 
                            options=[1, 2, 3, 4, 5], 
                            value=3,
                            key=f"hrdd_prob_{item}"
                        )
                    with c3:
                        st.write("Value Chain Relevance:")
                        is_supp = st.checkbox("Supplier", key=f"hrdd_sup_{item}")
                        is_cust = st.checkbox("Customer", key=f"hrdd_cust_{item}")
                    
                    results.append({
                        "Topic": item,
                        "Severity": sev,
                        "Probability": prob,
                        "Supplier (Value Chain)": 1 if is_supp else 0,
                        "Customer (Value Chain)": 1 if is_cust else 0
                    })
            
            if st.form_submit_button("Finish Assessment"):
                st.session_state.data_hrdd = pd.DataFrame(results)
                st.session_state.step = 5
                st.rerun()

    def generate_excel(self):
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        
        # Sheet 1: Stakeholder
        # Format: Name | Dept | Stakeholder | Scores...
        sh_df = st.session_state.data_stakeholder.copy()
        sh_df.insert(0, "Department", st.session_state.user_info["Department"])
        sh_df.insert(0, "Name", st.session_state.user_info["Name"])
        sh_df.to_excel(writer, sheet_name='Stakeholder')
        
        # Sheet 2: Materiality
        # Format: Name | Dept | Topic | Status | Value | Probability
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
        
        st.download_button(
            label=self.get_text("download_btn"),
            data=excel_data,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        if st.button("Start Over / 重新開始"):
            st.session_state.clear()
            st.rerun()

    def run(self):
        if st.session_state.step == 0:
            self.render_entry_portal()
        elif st.session_state.step == 1:
            self.render_stakeholder()
        elif st.session_state.step == 2:
            self.render_materiality()
        elif st.session_state.step == 3:
            self.render_tcfd()
        elif st.session_state.step == 4:
            self.render_hrdd()
        elif st.session_state.step == 5:
            self.render_finish()

if __name__ == "__main__":
    app = SustainabilityAssessment()
    app.run()
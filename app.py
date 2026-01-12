import streamlit as st
import pandas as pd
import io

# 設定頁面配置
st.set_page_config(page_title="Sustainability Assessment Tool", layout="wide")

# CSS 用於強制按鈕樣式
st.markdown("""
    <style>
    /* Next 按鈕 (橘色) */
    .stButton button[kind="primary"] {
        background-color: #FF8C00 !important;
        color: white !important;
        border: none;
    }
    /* Back 按鈕 (灰色/預設) */
    .stButton button[kind="secondary"] {
        background-color: #f0f2f6;
        color: #31333F;
        border: 1px solid #d6d6d6;
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
    /* 調整 Tooltip 顯示 */
    div[data-baseweb="tooltip"] {
        width: 300px;
        white-space: pre-wrap;
    }
    </style>
    """, unsafe_allow_html=True)

class SustainabilityAssessment:
    def __init__(self):
        self.init_session_state()
        self.setup_data()
        
    def init_session_state(self):
        # 0:Language, 1:Info, 2:Stakeholder, 3:Materiality, 4:TCFD, 5:HRDD, 6:Finish
        if 'step' not in st.session_state: st.session_state.step = 0 
        if 'language' not in st.session_state: st.session_state.language = 'zh'
        if 'user_info' not in st.session_state: st.session_state.user_info = {}
        if 'temp_stakeholder_data' not in st.session_state: st.session_state.temp_stakeholder_data = {}
        if 'selected_materiality_keys' not in st.session_state: st.session_state.selected_materiality_keys = []
            
        # 結果存儲
        if 'data_stakeholder' not in st.session_state: st.session_state.data_stakeholder = None
        if 'data_materiality' not in st.session_state: st.session_state.data_materiality = None
        if 'data_tcfd' not in st.session_state: st.session_state.data_tcfd = {}
        if 'data_hrdd' not in st.session_state: st.session_state.data_hrdd = {}
        
        # 狀態標記
        if 'just_finished' not in st.session_state: st.session_state.just_finished = False

    def setup_data(self):
        # =============================================================================================
        # 1. 介面文字 (UI Labels)
        # =============================================================================================
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
                "back_btn": "返回上一頁",
                "finish_btn": "完成評估並下載",
                "error_fill": "請填寫所有欄位",
                "error_select_10": "請正好選擇 10 個議題",
                "download_btn": "下載 Excel 結果報告",
                "start_over": "重新開始",
                "score_def": "評分定義：1 (無關) - 5 (高度相關)",
                "enter_note": "按下 'Enter' 僅會更新數值，請點擊下方按鈕繼續。",
                "mat_select_instr": "步驟 2.1: 請勾選 10 個議題",
                "mat_eval_instr": "步驟 2.2: 評估已選議題 (機會與風險)",
                "confirm_sel": "確認選擇",
                "status_label": "狀態",
                "status_help": "伊雲谷正在發生的議題 / 尚未在伊雲谷發生過的議題",
                "opp_val_label": "機會：價值創造 [1-5]",
                "opp_prob_label": "機會：可能性 [1-5]",
                "risk_imp_label": "風險：衝擊度 [1-5]",
                "risk_prob_label": "風險：可能性 [1-5]",
                "status_opts": ["已發生 (Actual)", "潛在 (Potential)"],
                "risk_header": "🛑 風險評估 (Risk)",
                "opp_header": "🌟 機會評估 (Opportunity)",
                "sev_label": "嚴重度/衝擊",
                "val_create_label": "價值創造",
                "like_label": "可能性",
                "hrdd_vc": "價值鏈關聯 (必填)",
                "hrdd_sup": "供應商",
                "hrdd_cust": "客戶",
                "hrdd_sev": "嚴重度",
                "hrdd_prob": "可能性",
                "hrdd_error": "錯誤：每個議題都必須至少勾選一項「價值鏈關聯」(供應商或客戶)"
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
                "back_btn": "Back",
                "finish_btn": "Finish & Download",
                "error_fill": "Please fill in all fields",
                "error_select_10": "Please select exactly 10 topics",
                "download_btn": "Download Result Excel",
                "start_over": "Start Over",
                "score_def": "Score Definition: 1 (No relevant) - 5 (Very relevant)",
                "enter_note": "Pressing 'Enter' only updates the score. Click the button below to proceed.",
                "mat_select_instr": "Step 2.1: Select 10 Topics",
                "mat_eval_instr": "Step 2.2: Evaluate Selected Topics (Opportunity & Risk)",
                "confirm_sel": "Confirm Selection",
                "status_label": "Status",
                "status_help": "Issues currently happening at eCloudvalley / Issues not yet happened at eCloudvalley",
                "opp_val_label": "Opportunity: Value Creation [1-5]",
                "opp_prob_label": "Opportunity: Probability [1-5]",
                "risk_imp_label": "Risk: Impact [1-5]",
                "risk_prob_label": "Risk: Probability [1-5]",
                "status_opts": ["Actual (Happened)", "Potential (Not happened)"],
                "risk_header": "🛑 Risk Assessment",
                "opp_header": "🌟 Opportunity Assessment",
                "sev_label": "Severity/Impact",
                "val_create_label": "Value Creation",
                "like_label": "Likelihood",
                "hrdd_vc": "Value Chain Relevance (Required)",
                "hrdd_sup": "Supplier",
                "hrdd_cust": "Customer",
                "hrdd_sev": "Severity",
                "hrdd_prob": "Probability",
                "hrdd_error": "Error: You must select at least one Value Chain (Supplier or Customer) for each topic."
            }
        }

        # =============================================================================================
        # 2. Stakeholder Assessment 內容與定義
        # =============================================================================================
        self.sh_rows = {
            "zh": ["供應商", "客戶", "員工", "股東/投資人", "政府機關", "社區/學校/非營利組織"],
            "en": ["Supplier", "Customer", "Employee", "Shareholder/Investor", "Government", "Community/School/NPO"]
        }
        self.sh_cols_def = {
            "Responsibility": {
                "zh": "責任：是否有法律、財務、營運法規或公約上的責任",
                "en": "Responsibility: Legal, financial, operational regulations, or customary obligations."
            },
            "Influence": {
                "zh": "影響力：是否有能力影響組織的策略決策",
                "en": "Influence: Ability to impact the organization's strategic decision-making."
            },
            "Tension": {
                "zh": "張力：是否在財務、環境或社會議題上有立即的衝突或關注需求",
                "en": "Tension: Immediate conflicts or attention required regarding financial, environmental, or social issues."
            },
            "Diverse Perspectives": {
                "zh": "多元觀點：是否能帶來新的觀點、創新或市場理解",
                "en": "Diverse Perspectives: Potential to bring new views, innovation, or market understanding."
            },
            "Dependency": {
                "zh": "依賴性：對組織的依賴程度，或組織對其的依賴程度",
                "en": "Dependency: Level of reliance on the organization (or vice versa)."
            }
        }
        self.sh_cols = {
            "zh": ["責任", "影響力", "張力", "多元觀點", "依賴性"],
            "en": ["Responsibility", "Influence", "Tension", "Diverse Perspectives", "Dependency"]
        }
        self.sh_col_keys = ["Responsibility", "Influence", "Tension", "Diverse Perspectives", "Dependency"]

        # =============================================================================================
        # 3. Materiality Topics (依據 CSV 更新)
        # =============================================================================================
        # 從 Excel 提取的資料
        self.mat_topic_data = {
            "m1": {
                "zh": "永續策略", "en": "Sustainability Strategies",
                "def_zh": "遵循金管會「永續發展路徑圖」、制定與實施永續發展藍圖、提升永續資訊透明度、參與外部永續評級與獎項、增進企業社會責任形象。",
                "def_en": "Follow the FSC's 'Sustainable Development Action Plans' to formulate and implement sustainable development blueprints, enhance transparency, and participate in external ratings."
            },
            "m2": {
                "zh": "誠信經營", "en": "Ethical Management",
                "def_zh": "制定與落實誠信經營相關政策、積極防範不誠實行為、制定防止利益衝突政策、建立有效之會計制度及內部控制制度。",
                "def_en": "Formulate and implement policies related to integrity management, prevent dishonest behavior, prevent conflicts of interest, and establish effective accounting/control systems."
            },
            "m3": {
                "zh": "公司治理", "en": "Corporate Governance",
                "def_zh": "董事成員組成、董事會及功能性委員會運作、董事提名與多元背景、董事會績效評估、ESG 議案提呈。",
                "def_en": "Composition of the board, operation of committees, director nomination and diversity, board performance assessment, and submission of ESG proposals."
            },
            "m4": {
                "zh": "風險控管", "en": "Risk Management",
                "def_zh": "制定風險管理政策及程序與架構、設立質化與量化標準以評估風險胃納能力、分析與辨識風險來源與類別、落實風險管理措施。",
                "def_en": "Formulate risk management policies/frameworks, establish standards to assess risk tolerance, analyze risk sources, and implement risk management measures."
            },
            "m5": {
                "zh": "法規遵循", "en": "Compliance",
                "def_zh": "定期檢視與追蹤國內外相關法規變動、各單位法規遵循查核、無違反法規及未遭受裁罰。",
                "def_en": "Regularly review and track changes in domestic and foreign regulations, conduct compliance checks, and ensure no violations or penalties."
            },
            "m6": {
                "zh": "營運持續管理", "en": "Business Continuity Management",
                "def_zh": "鑑別潛在的營運衝擊風險、制定營運持續計畫、建立緊急應變機制、定期演練與檢討。",
                "def_en": "Identify potential operational impact risks, formulate business continuity plans, establish emergency response mechanisms, and conduct regular drills."
            },
            "m7": {
                "zh": "資訊安全", "en": "Information Security",
                "def_zh": "建立資安管理制度、落實資安防護措施、定期進行資安檢測、提升員工資安意識、保障客戶與公司資料安全。",
                "def_en": "Establish ISMS, implement security measures, conduct regular tests, enhance employee awareness, and protect customer/company data."
            },
            "m8": {
                "zh": "供應商管理", "en": "Supplier Management",
                "def_zh": "建立供應商篩選與評鑑機制、要求供應商簽署行為準則、定期稽核供應商、輔導供應商提升永續績效。",
                "def_en": "Establish supplier screening/evaluation mechanisms, require Code of Conduct signing, audit suppliers, and assist them in improving sustainability performance."
            },
            "m9": {
                "zh": "客戶關係管理", "en": "Customer Relationship Management",
                "def_zh": "建立客戶滿意度調查機制、即時處理客戶客訴、維護客戶權益、提供高品質服務。",
                "def_en": "Establish customer satisfaction surveys, handle complaints promptly, protect customer rights, and provide high-quality services."
            },
            "m10": {
                "zh": "稅務政策", "en": "Tax Policies",
                "def_zh": "制定透明且合規的稅務政策、誠實申報納稅、揭露稅務資訊、不進行不當避稅。",
                "def_en": "Formulate transparent/compliant tax policies, declare taxes honestly, disclose tax info, and avoid improper tax avoidance."
            },
            # 依據一般清單補充後續 Materiality，若 Excel 有更多請在此新增
            "m11": {"zh": "營運績效", "en": "Operational Performance", "def_zh": "持續創造經濟價值，確保公司獲利能力與財務穩健。", "def_en": "Continuously create economic value to ensure profitability and financial stability."},
            "m12": {"zh": "創新與數位責任", "en": "Innovation and Digital Responsibility", "def_zh": "推動產品與服務創新，並負責任地運用數位科技。", "def_en": "Promote product/service innovation and responsible use of digital technologies."},
            "m13": {"zh": "人工智慧與科技變革", "en": "AI and Technological Transformation", "def_zh": "關注 AI 發展趨勢，評估其對營運之影響與機會。", "def_en": "Monitor AI trends and assess impacts/opportunities on operations."},
            "m14": {"zh": "氣候變遷因應", "en": "Climate Change Adaptation", "def_zh": "鑑別氣候風險與機會，制定減緩與調適策略。", "def_en": "Identify climate risks/opportunities and formulate mitigation/adaptation strategies."},
            "m15": {"zh": "環境與能資源管理", "en": "Environment and Resource Management", "def_zh": "提升能源使用效率，推動節能減碳與資源循環。", "def_en": "Improve energy efficiency and promote carbon reduction/resource circulation."},
            "m16": {"zh": "生物多樣性", "en": "Biodiversity", "def_zh": "評估營運對生態之影響，支持生物多樣性保育。", "def_en": "Assess operational impact on ecology and support biodiversity conservation."},
            "m17": {"zh": "職場健康與安全", "en": "Workplace Health and Safety", "def_zh": "提供安全健康之工作環境，預防職業災害與疾病。", "def_en": "Provide a safe/healthy work environment to prevent occupational injuries/diseases."},
            "m18": {"zh": "員工培育與職涯發展", "en": "Employee Development", "def_zh": "提供完善教育訓練，協助員工規劃職涯發展。", "def_en": "Provide comprehensive training and assist in career planning."},
            "m19": {"zh": "人才吸引與留任", "en": "Talent Attraction and Retention", "def_zh": "提供具競爭力之薪酬福利，營造友善職場以留才。", "def_en": "Provide competitive compensation and a friendly workplace to retain talent."},
            "m20": {"zh": "社會關懷與鄰里促進", "en": "Social Care", "def_zh": "參與社會公益活動，回饋社區並促進鄰里關係。", "def_en": "Participate in social welfare and give back to the community."},
            "m21": {"zh": "人權平等", "en": "Equal Human Rights", "def_zh": "尊重與保護國際公認之人權，杜絕任何形式之歧視。", "def_en": "Respect/protect internationally recognized human rights and eliminate discrimination."}
        }
        self.mat_topic_keys = list(self.mat_topic_data.keys())

        # =============================================================================================
        # 4. TCFD Topics (保留標準架構，請依 Excel 填入)
        # =============================================================================================
        # Risks
        self.tcfd_risk_data = {
            "tr1": {"zh": "溫室氣體排放定價上升", "en": "Rising GHG pricing", "def_zh": "政府為控制排放而提高碳稅或碳費，增加營運成本。", "def_en": "Increased operating costs due to carbon taxes/fees imposed by governments."},
            "tr2": {"zh": "對現有商品與服務的法規強制", "en": "Mandates on existing products/services", "def_zh": "法規要求產品需符合更嚴格的環保標準，導致合規成本增加。", "def_en": "Regulations requiring products to meet stricter environmental standards."},
            "tr3": {"zh": "現有商品與服務被低碳商品替代", "en": "Substitution of existing products", "def_zh": "客戶轉向購買低碳產品，導致現有高碳產品需求下降。", "def_en": "Reduced demand for existing high-carbon products as customers switch to low-carbon options."},
            "tr4": {"zh": "新技術投資成效不佳", "en": "Unsuccessful investment in new tech", "def_zh": "投資低碳技術失敗或回報不如預期，造成財務損失。", "def_en": "Financial losses due to failed or underperforming investments in low-carbon technologies."},
            "tr5": {"zh": "低碳轉型的轉型成本", "en": "Costs to transition to lower emissions", "def_zh": "為達成低碳目標而需投入的設備更新或製程改善成本。", "def_en": "Costs for equipment upgrades or process improvements to achieve low-carbon goals."},
            "tr6": {"zh": "消費者行為改變", "en": "Changing consumer behavior", "def_zh": "消費者偏好改變，更傾向支持永續品牌，影響市佔率。", "def_en": "Shifts in consumer preferences towards sustainable brands, affecting market share."},
            "tr7": {"zh": "氣候極端事件", "en": "Extreme weather events", "def_zh": "颱風、洪水等極端氣候導致資產受損或營運中斷。", "def_en": "Asset damage or operational disruption caused by extreme weather (typhoons, floods)."},
            "tr8": {"zh": "平均氣溫上升", "en": "Rising mean temperatures", "def_zh": "長期氣溫上升導致空調成本增加或工作環境惡化。", "def_en": "Increased cooling costs or worsened working conditions due to rising temperatures."}
        }
        # Opportunities
        self.tcfd_opp_data = {
            "to1": {"zh": "使用低排放能源", "en": "Use of lower-emission sources of energy", "def_zh": "採用再生能源降低碳排放，提升能源韌性。", "def_en": "Adopting renewable energy to reduce emissions and enhance energy resilience."},
            "to2": {"zh": "開發新低碳產品與服務", "en": "Development of new products/services", "def_zh": "開發低碳解決方案，滿足市場對綠色產品的需求。", "def_en": "Developing low-carbon solutions to meet market demand for green products."},
            "to3": {"zh": "低碳產品與服務-研發與創新", "en": "R&D and Innovation", "def_zh": "投入研發創新技術，提升競爭力並創造新營收來源。", "def_en": "Investing in R&D to enhance competitiveness and create new revenue streams."},
            "to4": {"zh": "資源替代/多元化", "en": "Resource substitutes/diversification", "def_zh": "尋求更環保的替代材料或多元供應來源，降低依賴風險。", "def_en": "Seeking eco-friendly substitutes or diverse supply sources to reduce risks."},
            "to5": {"zh": "公共部門的激勵措施", "en": "Public sector incentives", "def_zh": "利用政府提供的補助或稅收優惠，降低轉型成本。", "def_en": "Utilizing government subsidies or tax incentives to reduce transition costs."},
            "to6": {"zh": "參與再生能源及高效能源計畫", "en": "Participation in renewable energy markets", "def_zh": "參與綠電交易市場或能源效率專案，創造額外價值。", "def_en": "Participating in green power markets or energy efficiency projects."}
        }

        # =============================================================================================
        # 5. HRDD Topics (依據 CSV 更新)
        # =============================================================================================
        # 注意：Excel 中的 HRDD 議題與標準列表不同，以下為 Excel 內容
        self.hrdd_topic_data = {
            "hr_csv_1": {
                "zh": "舉報機制失效", "en": "Ineffective Grievance Mechanism",
                "def_zh": "1.管道不通暢：舉報專線或信箱形同虛設，員工反映問題後長期未得到回應或處理。\n2.保密性受損：舉報人的資訊被不當揭露給被檢舉人，導致員工失去對系統的信任。",
                "def_en": "1. Obstructed Channels: Whistleblowing hotlines are mere formalities; reports remain unaddressed.\n2. Compromised Confidentiality: Whistleblower identities disclosed, leading to loss of trust."
            },
            "hr_csv_2": {
                "zh": "報復利害關係人", "en": "Retaliation Against Stakeholders",
                "def_zh": "1.職務打壓：員工在參與人權訪談或表達對公司不滿後，被調動至偏遠單位或邊緣職務。\n2.社會/心理壓力：員工和供應商人員在發聲後，遭受公司主管在公開場合的言語排擠或恐嚇。",
                "def_en": "1. Career Suppression: Employees transferred/marginalized after speaking out.\n2. Social/Psychological Pressure: Personnel facing exclusion or intimidation after speaking out."
            },
            "hr_csv_3": {
                "zh": "勞資關係緊張", "en": "Labor-Management Tensions",
                "def_zh": "1.衝突解決缺失：雙方缺乏互信，勞資會議無法有效解決爭議。\n2.集體行動風險：因溝通不良導致罷工或抗議。",
                "def_en": "1. Conflict Resolution Missing: Lack of trust preventing dispute resolution.\n2. Collective Action Risk: Strikes or protests due to poor communication."
            }
            # 若 Excel 還有更多 HRDD 議題，請繼續在此添加
        }

        # HRDD Severity 定義 (General, Scale, Scope)
        # 如果標題沒有 Scale/Scope，將使用 General
        self.hrdd_sev_defs = {
            "scale": {
                "zh": "**規模 (Scale) 嚴重度定義:**\n* 1: 基礎傷害/無負面影響\n* 2: 輕度傷害\n* 3: 中度傷害\n* 4: 嚴重傷害\n* 5: 造成物理殘疾或死亡",
                "en": "**Scale Severity Definitions:**\n* 1: Basic injury / No impact\n* 2: Minor injury\n* 3: Moderate injury\n* 4: Severe injury\n* 5: Physical disability or death"
            },
            "scope": {
                "zh": "**範圍 (Scope) 嚴重度定義:**\n* 1: 影響範圍極小 (<5%)\n* 2: 影響範圍小 (5-20%)\n* 3: 影響範圍中等 (20-50%)\n* 4: 影響範圍大 (50-80%)\n* 5: 影響範圍極大 (>80%)",
                "en": "**Scope Severity Definitions:**\n* 1: Minimal scope (<5%)\n* 2: Minor scope (5-20%)\n* 3: Moderate scope (20-50%)\n* 4: Major scope (50-80%)\n* 5: Extensive scope (>80%)"
            },
            "general": {
                "zh": "**嚴重度定義 (Severity):**\n* 1: 輕微/無明顯影響\n* 2: 低度影響/短期可恢復\n* 3: 中度影響/需一定時間恢復\n* 4: 高度影響/長期且難以恢復\n* 5: 極度嚴重/不可逆的損害",
                "en": "**Severity Definitions:**\n* 1: Minor / No significant impact\n* 2: Low impact / Short-term recovery\n* 3: Moderate impact / Medium-term recovery\n* 4: High impact / Long-term hard to recover\n* 5: Critical / Irreversible damage"
            }
        }

    # Helper functions
    def get_ui(self, key): return self.ui_texts[st.session_state.language][key]
    
    # 導航按鈕
    def render_nav_buttons(self, next_label, next_callback, next_args=None, back_visible=True):
        st.write("") 
        st.write("") 
        c1, c2, c3, c4, c5 = st.columns([1, 0.5, 1, 0.5, 1])
        with c1:
            if back_visible:
                if st.button(self.get_ui("back_btn"), key="nav_back", type="secondary", use_container_width=True):
                    st.session_state.step -= 1
                    st.rerun()
        with c5:
            if st.button(next_label, key="nav_next", type="primary", use_container_width=True):
                if next_callback:
                    next_callback(next_args) if next_args else next_callback()

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

        self.render_nav_buttons("Next / 下一步", go_next, back_visible=False)

    # PAGE 1: 基本資料
    def render_entry_portal(self):
        st.title(self.get_ui("step1_title"))
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input(self.get_ui("name_label"), value=st.session_state.user_info.get("Name", ""))
            with col2:
                dept = st.text_input(self.get_ui("dept_label"), value=st.session_state.user_info.get("Department", ""))
        
        def go_next():
            if name and dept:
                st.session_state.user_info = {"Name": name, "Department": dept}
                st.session_state.step = 2
                st.rerun()
            else:
                st.error(self.get_ui("error_fill"))

        self.render_nav_buttons(self.get_ui("next_btn"), go_next, back_visible=True)

    # PAGE 2: Stakeholder Assessment
    def render_stakeholder(self):
        st.title(self.get_ui("step2_title"))
        st.info(self.get_ui("score_def"))
        st.caption(self.get_ui("enter_note"))

        lang = st.session_state.language
        rows = self.sh_rows[lang]
        col_names = self.sh_cols[lang]
        col_keys = self.sh_col_keys

        data = {}
        rows_en = self.sh_rows["en"]

        for r_idx, row_name in enumerate(rows):
            st.subheader(row_name)
            cols = st.columns(len(col_names))
            
            row_key_en = rows_en[r_idx]
            row_data = {}
            
            for c_idx, col_name in enumerate(col_names):
                col_key = col_keys[c_idx] 
                input_key = f"sh_{r_idx}_{c_idx}"
                def_text = self.sh_cols_def[col_key][lang]
                
                with cols[c_idx]:
                    val = st.number_input(
                        f"{col_name}",
                        min_value=1, max_value=5, value=st.session_state.temp_stakeholder_data.get(input_key, 3), 
                        key=input_key,
                        help=def_text # 顯示定義
                    )
                    row_data[col_key] = val
                    st.session_state.temp_stakeholder_data[input_key] = val
            
            data[row_key_en] = row_data
            st.divider()
        
        def go_next():
            st.session_state.data_stakeholder = pd.DataFrame.from_dict(data, orient='index')
            st.session_state.step = 3
            st.rerun()

        self.render_nav_buttons(self.get_ui("next_btn"), go_next)

    # PAGE 3: Materiality Assessment
    def render_materiality(self):
        st.title(self.get_ui("step3_title"))
        lang = st.session_state.language
        
        # Part A: Selection (Step 2.1)
        if not st.session_state.selected_materiality_keys:
            st.subheader(self.get_ui("mat_select_instr"))
            selected_keys = []
            
            keys = self.mat_topic_keys
            cols = st.columns(2)
            
            for i, key in enumerate(keys):
                topic_info = self.mat_topic_data[key]
                display_text = topic_info[lang]
                def_text = topic_info[f"def_{lang}"]
                
                with cols[i % 2]:
                    # 選題階段：顯示 Topic 定義
                    if st.checkbox(display_text, key=f"mat_sel_{key}", help=def_text):
                        selected_keys.append(key)

            st.write(f"Selected: **{len(selected_keys)}** / 10")
            
            def confirm_selection():
                if len(selected_keys) == 10:
                    st.session_state.selected_materiality_keys = selected_keys
                    st.rerun()
                else:
                    st.error(self.get_ui("error_select_10"))
            
            c1, c2, c3, c4, c5 = st.columns([1, 0.5, 1, 0.5, 1])
            with c1:
                if st.button(self.get_ui("back_btn"), type="secondary", use_container_width=True):
                    st.session_state.step -= 1
                    st.rerun()
            with c5:
                if st.button(self.get_ui("confirm_sel"), type="primary", use_container_width=True):
                    confirm_selection()
        
        # Part B: Evaluation (Step 2.2)
        else:
            st.subheader(self.get_ui("mat_eval_instr"))
            results = []
            status_options_ui = self.get_ui("status_opts")
            status_map = {status_options_ui[0]: "Actual", status_options_ui[1]: "Potential"}
            status_help_text = self.get_ui("status_help")

            for key in st.session_state.selected_materiality_keys:
                topic_info = self.mat_topic_data[key]
                display_text = topic_info[lang]
                save_text = topic_info["en"]
                
                with st.expander(display_text, expanded=True):
                    # 評分階段：Topic 定義移除，改在 Actual/Potential 顯示狀態定義
                    status_ui = st.radio(
                        f"{self.get_ui('status_label')} - {display_text}", 
                        status_options_ui, 
                        key=f"mat_stat_{key}", 
                        horizontal=True,
                        label_visibility="collapsed",
                        help=status_help_text 
                    )
                    st.write(f"**{self.get_ui('status_label')}:** {status_ui}")

                    st.markdown("---")
                    
                    c_opp, c_risk = st.columns(2)
                    with c_opp:
                        st.markdown(f"#### {self.get_ui('opp_header')}")
                        opp_val = st.slider(self.get_ui("opp_val_label"), 1, 5, 3, key=f"mat_oval_{key}")
                        opp_prob = st.slider(self.get_ui("opp_prob_label"), 1, 5, 3, key=f"mat_oprob_{key}")
                        
                    with c_risk:
                        st.markdown(f"#### {self.get_ui('risk_header')}")
                        risk_imp = st.slider(self.get_ui("risk_imp_label"), 1, 5, 3, key=f"mat_rimp_{key}")
                        risk_prob = st.slider(self.get_ui("risk_prob_label"), 1, 5, 3, key=f"mat_rprob_{key}")
                    
                    results.append({
                        "Topic": save_text,
                        "Status": status_map[status_ui],
                        "Opp Value Creation": opp_val,
                        "Opp Probability": opp_prob,
                        "Risk Impact": risk_imp,
                        "Risk Probability": risk_prob
                    })
            
            def go_next():
                st.session_state.data_materiality = pd.DataFrame(results)
                st.session_state.step = 4
                st.rerun()

            self.render_nav_buttons(self.get_ui("next_btn"), go_next)

    # PAGE 4: TCFD Assessment
    def render_tcfd(self):
        st.title(self.get_ui("step4_title"))
        results = []
        lang = st.session_state.language
        
        # 1. Opportunities (Top)
        st.markdown(f"### {self.get_ui('opp_header')}")
        st.markdown("---")
        
        for key, info in self.tcfd_opp_data.items():
            display_text = info[lang]
            def_text = info[f"def_{lang}"]
            
            # TCFD：每一個議題都有定義 [?]
            st.markdown(f"**{display_text}**", help=def_text)
            
            c1, c2 = st.columns(2)
            with c1:
                sev = st.slider(self.get_ui("val_create_label"), 1, 5, 3, key=f"tcfd_os_{key}")
            with c2:
                like = st.slider(self.get_ui("like_label"), 1, 5, 3, key=f"tcfd_ol_{key}")
            
            results.append({"Type": "Opportunity", "Topic": info["en"], "Severity/Value": sev, "Likelihood": like})
            st.write("")

        st.write("")
        st.write("")

        # 2. Risks (Bottom)
        st.markdown(f"### {self.get_ui('risk_header')}")
        st.markdown("---")
        
        for key, info in self.tcfd_risk_data.items():
            display_text = info[lang]
            def_text = info[f"def_{lang}"]
            
            st.markdown(f"**{display_text}**", help=def_text)
            
            c1, c2 = st.columns(2)
            with c1:
                sev = st.slider(self.get_ui("sev_label"), 1, 5, 3, key=f"tcfd_rs_{key}")
            with c2:
                like = st.slider(self.get_ui("like_label"), 1, 5, 3, key=f"tcfd_rl_{key}")
            
            results.append({"Type": "Risk", "Topic": info["en"], "Severity/Value": sev, "Likelihood": like})
            st.write("")

        def go_next():
            st.session_state.data_tcfd = pd.DataFrame(results)
            st.session_state.step = 5
            st.rerun()

        self.render_nav_buttons(self.get_ui("next_btn"), go_next)

    # PAGE 5: HRDD
    def render_hrdd(self):
        st.title(self.get_ui("step5_title"))
        lang = st.session_state.language
        
        temp_results = []
        
        for key, info in self.hrdd_topic_data.items():
            display_text = info[lang]
            save_text = info["en"]
            topic_def = info[f"def_{lang}"]
            
            # 自動偵測標題中的 Scale/Scope 關鍵字
            # 如果標題像 "Child Labor (Scale)" -> 使用 Scale 定義
            # 如果標題像 "Ineffective Grievance Mechanism" (無關鍵字) -> 使用 General 定義
            
            is_scale = "規模" in display_text or "Scale" in display_text or "scale" in display_text
            is_scope = "範圍" in display_text or "Scope" in display_text or "scope" in display_text
            
            if is_scale:
                sev_def_text = self.hrdd_sev_defs["scale"][lang]
            elif is_scope:
                sev_def_text = self.hrdd_sev_defs["scope"][lang]
            else:
                sev_def_text = self.hrdd_sev_defs["general"][lang]
            
            with st.container(border=True):
                # HRDD：每一個議題都有定義 [?]
                st.markdown(f"##### {display_text}", help=topic_def)
                
                c1, c2, c3 = st.columns([1.5, 2, 2])
                
                with c1:
                    st.write(f"**{self.get_ui('hrdd_vc')}**")
                    is_supp = st.checkbox(self.get_ui('hrdd_sup'), key=f"hr_sup_{key}")
                    is_cust = st.checkbox(self.get_ui('hrdd_cust'), key=f"hr_cust_{key}")

                with c2:
                    # Severity：根據偵測結果顯示 Scale/Scope/General 定義 [?]
                    sev = st.select_slider(
                        label=self.get_ui('hrdd_sev'),
                        options=[1, 2, 3, 4, 5], 
                        value=3,
                        key=f"hr_sev_{key}",
                        help=sev_def_text 
                    )
                
                with c3:
                    prob = st.select_slider(
                        label=self.get_ui('hrdd_prob'),
                        options=[1, 2, 3, 4, 5], 
                        value=3,
                        key=f"hr_prob_{key}"
                    )
                
                temp_results.append({
                    "Topic": save_text,
                    "Severity": sev,
                    "Probability": prob,
                    "Supplier (Value Chain)": 1 if is_supp else 0,
                    "Customer (Value Chain)": 1 if is_cust else 0
                })
        
        def go_next():
            for res in temp_results:
                if res["Supplier (Value Chain)"] == 0 and res["Customer (Value Chain)"] == 0:
                    st.error(f"{self.get_ui('hrdd_error')} (Topic: {res['Topic']})")
                    return

            st.session_state.data_hrdd = pd.DataFrame(temp_results)
            st.session_state.step = 6
            st.session_state.just_finished = True
            st.rerun()

        self.render_nav_buttons(self.get_ui("finish_btn"), go_next)

    # PAGE 6: FINISH
    def generate_excel(self):
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        name_col = "Name"
        dept_col = "Department"
        
        sh_df = st.session_state.data_stakeholder.copy()
        sh_df.insert(0, dept_col, st.session_state.user_info["Department"])
        sh_df.insert(0, name_col, st.session_state.user_info["Name"])
        sh_df.to_excel(writer, sheet_name='Stakeholder')
        
        mat_df = st.session_state.data_materiality.copy()
        mat_df.insert(0, dept_col, st.session_state.user_info["Department"])
        mat_df.insert(0, name_col, st.session_state.user_info["Name"])
        mat_df.to_excel(writer, sheet_name='Materiality', index=False)
        
        tcfd_df = st.session_state.data_tcfd.copy()
        tcfd_df.insert(0, dept_col, st.session_state.user_info["Department"])
        tcfd_df.insert(0, name_col, st.session_state.user_info["Name"])
        tcfd_df.to_excel(writer, sheet_name='TCFD', index=False)
        
        hrdd_df = st.session_state.data_hrdd.copy()
        hrdd_df.insert(0, dept_col, st.session_state.user_info["Department"])
        hrdd_df.insert(0, name_col, st.session_state.user_info["Name"])
        hrdd_df.to_excel(writer, sheet_name='HRDD', index=False)
        
        writer.close()
        return output.getvalue()

    def render_finish(self):
        if st.session_state.just_finished:
            st.balloons()
            st.session_state.just_finished = False

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
            if st.button(self.get_ui("start_over"), type="secondary", use_container_width=True):
                st.session_state.clear()
                st.rerun()

    def run(self):
        if st.session_state.step == 0: self.render_language_selection()
        elif st.session_state.step == 1: self.render_entry_portal()
        elif st.session_state.step == 2: self.render_stakeholder()
        elif st.session_state.step == 3: self.render_materiality()
        elif st.session_state.step == 4: self.render_tcfd()
        elif st.session_state.step == 5: self.render_hrdd()
        elif st.session_state.step == 6: self.render_finish()

if __name__ == "__main__":
    app = SustainabilityAssessment()
    app.run()

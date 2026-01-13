import streamlit as st
import pandas as pd
import io
import streamlit.components.v1 as components

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

    def scroll_to_top(self):
            # The 'key' parameter is CRITICAL here. It changes with every step,
            # forcing Streamlit to re-execute this Javascript every time you click Next/Back.
            components.html(
                f"""
                <script>
                    // Use a small timeout to ensure the page has rendered
                    setTimeout(function() {{
                        // 1. Scroll the main window
                        window.scrollTo(0, 0);
                        
                        // 2. Scroll the parent window (if in iframe)
                        if (window.parent) {{
                            window.parent.scrollTo(0, 0);
                        }}
    
                        // 3. Scroll Streamlit's specific container class
                        var mainContainer = window.parent.document.querySelector('section.main');
                        if (mainContainer) {{
                            mainContainer.scrollTo(0, 0);
                        }}
                        
                        // 4. Fallback: Scroll to our specific anchor
                        var topAnchor = window.parent.document.getElementById('top-marker');
                        if (topAnchor) {{
                            topAnchor.scrollIntoView({{behavior: "instant", block: "start"}});
                        }}
                    }}, 100); // 100ms delay to beat the render race
                </script>
                """,
                height=0,
                key=f"scroll_to_top_{st.session_state.step}"  # <--- THIS FIXES THE ISSUE
            )
    
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
                "zh": "責任：部門是否對於利害關係人有法律、財務、營運法規或公約上的責任",
                "en": "Responsibility: Does The Department has any legal, financial, operational regulations, or customary obligations."
            },
            "Influence": {
                "zh": "影響力：利害關係人是否有能力影響部門的策略決策",
                "en": "Influence: Does stakeholder has ability to impact The Department's strategic decision-making."
            },
            "Tension": {
                "zh": "張力：部門是否對於利害關係人在財務、環境或社會議題上有立即的衝突或關注需求",
                "en": "Tension: Does The Department need to take action immediately conflicts or attention required regarding financial, environmental, or social issues."
            },
            "Diverse Perspectives": {
                "zh": "多元觀點：利害關係人是否為部門能帶來新的觀點、創新或市場理解",
                "en": "Does stakeholder can brings diverse perspectives to The Department, like potential to bring new views, innovation, or market understanding."
            },
            "Dependency": {
                "zh": "依賴性：利害關係人對部門的依賴程度，或部門對其的依賴程度",
                "en": "Dependency: Level of reliance of stakeholder on The Department (or vice versa)."
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
                "zh": "資安韌性與數位信任", "en": "Cyber Resilience and Digital Trust",
                "def_zh": "完善的資訊與雲端資安管理，不僅強化資料、機敏資訊與個資保護，也涵蓋資安事件發生時的快速復原能力。以 ISO 27001、NIST 等國際資安框架，建立完善的偵測與防護機制，並持續提升人員資安意識，以強化整體資安韌性與長期數位信任。",
                "def_en": "Comprehensive information and cloud security management not only strengthens the protection of data, sensitive information, and personal data, but also includes rapid recovery capabilities in the event of a security incident. Leveraging international frameworks such as ISO 27001 and NIST, robust detection and protection mechanisms are implemented, while personnel awareness is continuously enhanced to reinforce overall cybersecurity resilience and long-term digital trust."
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
  "tr1": {
    "zh": "極端降雨事件",
    "en": "Extreme rainfall events",
    "def_zh": "背景：科技部TCCIP研究指出，未來颱風的生成呈現減少，而颱風帶來的降雨強度則呈現增加。\n風險：此型態的極端降雨將使得營運面臨更嚴重的颱風災害，包括市區淹水、道路坍方、淹水封閉等；因伊雲谷因服務性質，對於系統設備穩定性特別重視，當極端災害發生可能導致系統服務中斷，及人員傷亡，造成營運衝擊。",
    "def_en": "Background: Research by the Ministry of Science and Technology's TCCIP indicates that the formation of typhoons is decreasing, while the intensity of rainfall brought by typhoons is increasing. \nRisk: This type of extreme rainfall will expose operations to more severe typhoon disasters, including urban flooding, road collapses, and flood closures. Because of the service nature of E-Cloud Valley, the stability of its system equipment is of paramount importance. Extreme disasters could lead to system service interruptions and personnel casualties, causing operational disruptions."
  },
  "tr2": {
    "zh": "長期氣候模式改變",
    "en": "Long-term climate pattern changes",
    "def_zh": "背景：根據國家氣候變遷科學報告評估顯示，臺灣未來極端高溫日數將顯著增加，並伴隨更明顯的乾旱趨勢，反映出氣候模式長期改變的趨勢。這些變化可能對企業日常運作與環境條件造成影響。\n風險：持續高溫、乾旱及異常低溫情況可能帶來營運風險，如提高辦公場所能源使用需求與成本，並影響員工健康與工作效能。",
    "def_en": "Background: According to the National Climate Change Scientific Report, Taiwan is expected to experience a significant increase in the number of days with extreme high temperatures, accompanied by a more pronounced drought trend, reflecting a long-term shift in climate patterns. These changes may impact daily business operations and environmental conditions. \nRisk: Persistent high temperatures, drought, and abnormally low temperatures may pose operational risks, such as increased energy demands and costs in office spaces, and negatively impact employee health and work efficiency."
  },
  "tr3": {
    "zh": "溫室氣體排放價格上升",
    "en": "Rising greenhouse gas emission prices",
    "def_zh": "背景：台灣已頒佈《氣候法》，溫室氣體排放將開始面臨各種費用與稅收。參考國際趨勢，每噸碳的價格預計逐步上升，海外營運據點也陸續實施碳稅或碳交易機制。若未來擴大海外營運，公司可能面臨營運成本增加的挑戰。\n風險：若減碳成效有限，公司未來可能面臨支付額外費用來覆蓋營運碳排放，增加營運成本。",
    "def_en": "Background: Taiwan has enacted the Climate Change Act, and greenhouse gas emissions will begin to face various fees and taxes. Referring to international trends, the price per ton of carbon is expected to gradually rise, and overseas operating locations are also gradually implementing carbon taxes or carbon trading mechanisms. If the company expands its overseas operations in the future, it may face the challenge of increased operating costs. \nRisk: If carbon reduction efforts are limited, the company may face additional costs to cover operational carbon emissions in the future, increasing operating costs."
  },
  "tr4": {
    "zh": "對既有的產品與服務增加強制性法規",
    "en": "Add mandatory regulations to existing products and services",
    "def_zh": "背景：歐盟已發佈《CBAM》開始針對原物料課稅，全球各國開始針對各項碳排放源制定法規、費用政策等。\n風險：政府開始強制所有供應商(下游往上)都需要提供產品/服務碳足跡，以確保終端消費者以此為消費判斷，產生違規罰款、銷售成本增加等風險。",
    "def_en": "Background: The EU has published the CBAM and begun taxing raw materials. Globally, countries are developing regulations and fee policies for various carbon emission sources. \nRisk: Governments are beginning to mandate that all suppliers provide the carbon footprint of their products and services for consumer decision-making, leading to potential fines for non-compliance and increased sales costs."
  },
  "tr5": {
    "zh": "溫室氣體盤查與揭露要求",
    "en": "Greenhouse gas inventory and disclosure requirements",
    "def_zh": "背景：根據金管會「上市櫃公司永續發展行動方案」，上市櫃公司未來需揭露合併公司範圍內的溫室氣體盤查資訊，以確保碳排放數據的完整性與透明度，作為投資人與利益關係人評估企業永續績效的重要依據。\n風險：未如規定揭露溫室氣體盤查資訊，可能遭主管機關處分，並影響公司信譽與外部信任。",
    "def_en": "Background: According to the Financial Supervisory Commission's Action Plan for the Sustainable Development of Listed Companies, companies will be required to disclose greenhouse gas inventories within their consolidated scope to ensure data integrity and transparency. \nRisk: Failure to disclose as required may result in regulatory penalties and damage to corporate reputation and trust."
  },
  "tr6": {
    "zh": "法律訴訟與合規",
    "en": "Legal proceedings and compliance",
    "def_zh": "背景：法規日益嚴格，及利害關係人高度關注企業碳排放資訊，因此必須揭露正確、完整的溫室氣體盤查資料。\n風險：若資訊不完整或不正確，公司可能違反法規，並影響信譽與外部信任。",
    "def_en": "Background: Increasingly stringent regulations and heightened stakeholder scrutiny require accurate and complete greenhouse gas disclosures. \nRisk: Incomplete or inaccurate information may lead to regulatory violations and reputational damage."
  },
  "tr7": {
    "zh": "利害關係人的關注度上升或負面回饋",
    "en": "Increased stakeholder attention or negative feedback",
    "def_zh": "背景：政府、投資人、供應鏈、客戶及員工等利害關係人高度關注企業永續、道德及環境表現，外部評比機構亦進行評分。\n風險：若永續績效不佳，可能遭受負面回饋，影響品牌形象與聲譽。",
    "def_en": "Background: Governments, investors, supply chains, customers, employees, and rating agencies closely scrutinize corporate sustainability performance. \nRisk: Poor performance may result in negative feedback, damaging brand image and reputation."
  },
  "tr8": {
    "zh": "既有產品與服務的低碳排替代品",
    "en": "Low-carbon alternatives to existing products and services",
    "def_zh": "背景：台灣進入碳有價時代，產品與服務的全生命週期碳足跡將影響成本與市場競爭。\n風險：市場出現更低碳的雲端與MSP服務，可能導致客戶轉換供應商，使公司競爭力下降。",
    "def_en": "Background: With carbon pricing, full life-cycle carbon footprints affect costs and competitiveness. \nRisk: Lower-carbon cloud and MSP services may attract customers, reducing the company's competitiveness."
  },
  "tr9": {
    "zh": "新技術投資成效不佳",
    "en": "Unsuccessful investment in new technologies",
    "def_zh": "背景：氣候相關新技術快速發展，吸引企業投入資源。\n風險：若評估不足，可能因技術淘汰、市場策略不足或法規變動導致投資失敗。",
    "def_en": "Background: Rapid development of climate-related technologies attracts investment. \nRisk: Inadequate assessment may lead to failure due to technological obsolescence, poor market strategy, or regulatory changes."
  },
  "tr10": {
    "zh": "低碳技術轉型的轉型成本",
    "en": "Transition costs of low-carbon technology transformation",
    "def_zh": "背景：因應COP30能源轉型與碳管理要求，需調整營運模式與技術。\n風險：轉型過程將產生初期投資成本、資源限制及成本上升，影響營運穩定性與競爭力。",
    "def_en": "Background: To meet COP30 energy transition and carbon management requirements, operational models and technologies must be adjusted. \nRisk: Initial investment, resource constraints, and rising costs may affect operational stability and competitiveness."
  }
        }

        # Opportunities
        self.tcfd_opp_data = {
  "to1": {
    "zh": "使用低碳排的能源",
    "en": "Use low-carbon energy",
    "def_zh": "1. 背景：台灣推行全面能源轉型，逐步邁向2050淨零目標\n2. 機會：積極推低碳排能源之使用，獲得參與國際倡議之資格(如RE100)，增加公司名譽、降低服務碳足跡、提升產品與服務之市場競爭力",
    "def_en": "1. Background: Taiwan is implementing a comprehensive energy transition, gradually moving towards its 2050 net-zero target.\n\n2. Opportunities: Actively promoting the use of low-carbon energy sources can qualify the company to participate in international initiatives (such as RE100), enhancing its reputation, reducing its service carbon footprint, and improving the market competitiveness of its products and services."
  },
  "to2": {
    "zh": "碳交易市場參與",
    "en": "Participation in the carbon trading market",
    "def_zh": "1. 背景：台灣政府積極推動碳市場發展，制定碳排放相關法規，推動碳交易體系\n2. 機會：企業可以透過參與碳市場，不僅減少碳排放成本，還可以參與碳信用交易，推動企業的永續發展，並在國際市場上贏得競爭優勢",
    "def_en": "1. Background: The Taiwanese government is actively promoting the development of the carbon market, enacting carbon emission-related regulations, and promoting a carbon trading system.\n\n2. Opportunities: By participating in the carbon market, businesses can not only reduce carbon emission costs but also participate in carbon credit trading, promoting sustainable development and gaining a competitive advantage in the international market."
  },
  "to3": {
    "zh": "低碳產品與服務-開發與拓展",
    "en": "Low-carbon products and services - development and expansion",
    "def_zh": "1. 背景：台灣市場對低碳產品與服務的需求逐漸增加，消費者對環保和氣候友善的商品有更高的關注度\n2. 機會：企業透過開發氣候友善的品牌，不僅滿足現代消費者的偏好，還可以建立積極的企業形象，提升品牌忠誠度；建立低碳供應鏈，促進供應商和製造商之間的合作，實現整體價值鏈的碳足跡降低",
    "def_en": "1. Background: The demand for low-carbon products and services in the Taiwanese market is gradually increasing, with consumers paying greater attention to environmentally friendly and climate-friendly goods.\n\n2. Opportunities: By developing climate-friendly brands, companies can not only meet the preferences of modern consumers but also build a positive corporate image and enhance brand loyalty; establishing a low-carbon supply chain can promote cooperation between suppliers and manufacturers, thereby reducing the carbon footprint of the entire value chain."
  },
  "to4": {
    "zh": "低碳產品與服務-研發與創新",
    "en": "Low-carbon products and services - R&D and innovation",
    "def_zh": "1. 背景：政府鼓勵綠色技術研發，提供獎勵與補助。本公司的 AIoT 技術可即時監控能源使用，提升設備與系統效率，降低碳排放，並支持低碳產品研發，幫助企業在節能減碳的同時提升產品與服務價值。\n2. 機會：透過提供客戶創新低碳解決方案，協助企業實現更高效的能源使用和減少碳排放；取得低碳產品專利，與其他企業建立戰略合作",
    "def_en": "1. Background: The government encourages green technology research and development, providing rewards and subsidies. Our company's AIoT technology can monitor energy use in real time, improve equipment and system efficiency, reduce carbon emissions, and support the development of low-carbon products, helping companies enhance the value of their products and services while saving energy and reducing carbon emissions.\n\n2. Opportunities: By providing customers with innovative low-carbon solutions, we assist companies in achieving more efficient energy use and reducing carbon emissions; we acquire low-carbon product patents and establish strategic partnerships with other companies."
  },
  "to5": {
    "zh": "消費者偏好改變",
    "en": "Changes in consumer preferences",
    "def_zh": "1. 背景：消費者對環保、氣候友善產品的偏好增加，推動企業改變產品和服務提供方向\n2. 機會：企業可透過理解消費者需求，調整產品組合，提高市場份額；提供產品的環境友善資訊，強調公司的社會責任，有助於建立與消費者之間的信任",
    "def_en": "1. Background: Increased consumer preference for environmentally friendly and climate-friendly products is driving companies to shift their product and service offerings.\n\n2. Opportunities: Companies can increase market share by understanding consumer needs, adjusting their product mix, and providing information about the environmental friendliness of their products, emphasizing corporate social responsibility, which helps build trust with consumers."
  },
  "to6": {
    "zh": "數位與 AI 技術應用成長",
    "en": "Growth of digital and AI technology applications",
    "def_zh": "1.背景：AI 與數位轉型快速普及，企業對 AI 應用需求持續增加。市場也越來越重視既能提升效率，又兼顧能源使用與低碳表現的數位產品。\n2.機會：本公司推出 AI 產品與服務，協助客戶快速導入 AI 並提升作業效率。隨著市場對低碳、高效能 AI 產品需求增長，相關服務可擴大客戶應用範圍，並創造新的營收成長機會。",
    "def_en": "1. Background: With the rapid adoption of AI and digital transformation, enterprise demand for AI applications continues to increase. The market is also placing increasing emphasis on digital products that improve efficiency while also considering energy use and low-carbon performance.\n\n2. Opportunity: Our company offers AI products and services to help customers quickly implement AI and improve operational efficiency. As market demand for low-carbon, high-efficiency AI products grows, related services can expand the scope of customer applications and create new revenue growth opportunities."
  },
  "to7": {
    "zh": "領先資安技術",
    "en": "Leading cybersecurity technology",
    "def_zh": "1. 背景：本公司具備資安防護、異地備援及完善的營運持續計劃，能維持自身及客戶系統穩定運作，即使面臨意外事件，也能確保服務不中斷。\n2. 機會：透過先進技術與韌性能力，公司可提供穩定可靠的服務，滿足客戶對營運穩定性的需求，並強化市場信任，創造新的合作與營收機會。",
    "def_en": "1. Background: Our company possesses cybersecurity protection, off-site backup, and a comprehensive operational continuity plan, enabling us to maintain the stable operation of our own and our clients' systems. Even in the face of unforeseen events, we can ensure uninterrupted service.\n\n2. Opportunity: Through advanced technology and resilience, the company can provide stable and reliable services, meeting clients' needs for operational stability, strengthening market trust, and creating new cooperation and revenue opportunities."
  },
  "to8": {
    "zh": "氣候情境分析",
    "en": "Climate Context Analysis",
    "def_zh": "1.背景：氣候變遷可能帶來極端天氣與能源波動，對企業的上雲及雲端服務運作造成潛在影響。透過氣候情境分析，公司能提前評估不同情境下的影響，降低營運中斷的可能性，確保服務穩定。\n2.機會：氣候情境分析使公司能提前應對可能的風險，降低營運中斷的可能性，確保服務持續與營運穩定，並提升整體營運韌性。",
    "def_en": "1. Background: Climate change may bring extreme weather and energy fluctuations, potentially impacting businesses' cloud adoption and cloud service operations. Through climate scenario analysis, companies can assess the impact of different scenarios in advance, reducing the likelihood of operational disruptions and ensuring service stability.\n\n2. Opportunities: Climate scenario analysis enables companies to proactively address potential risks, reduce the likelihood of operational disruptions, ensure service continuity and operational stability, and enhance overall operational resilience."
  },
  "to9": {
    "zh": "優化能資源管理",
    "en": "Optimize energy resource management",
    "def_zh": "1.背景：本公司已導入 ISO 14001 環境管理系統，持續監控能源、水資源及原物料的使用，以降低浪費並降低環境風險。結合規劃中的 2030 減碳目標，公司致力於提升資源使用效率，並減少碳排放。\n2.機會：透過優化能源與資源管理，公司可降低成本與碳排放，以減少資源浪費，並達成本公司淨零碳排目標。",
    "def_en": "1. Background: Our company has implemented an ISO 14001 environmental management system to continuously monitor the use of energy, water resources, and raw materials to reduce waste and environmental risks. In line with our planned 2030 carbon reduction targets, the company is committed to improving resource efficiency and reducing carbon emissions.\n\n2. Opportunity: By optimizing energy and resource management, the company can reduce costs and carbon emissions, thereby reducing resource waste and achieving our net-zero carbon emission target."
  },
  "to10": {
    "zh": "低碳建築",
    "en": "Low-carbon buildings",
    "def_zh": "使用低碳鋼材與混凝土建設數據中心，避免了數萬噸的隱含碳排放。>若有列入，再新增背景及機會的說明",
    "def_en": "Using low-carbon steel and concrete to construct data centers avoids tens of thousands of tons of hidden carbon emissions. >If listed, please add background and opportunity explanations."
  }
}

        # =============================================================================================
        # 5. HRDD Topics (依據 CSV 更新)
        # =============================================================================================
        # 注意：Excel 中的 HRDD 議題與標準列表不同，以下為 Excel 內容
        self.hrdd_topic_data = {
            "hrdd01": {
    "zh": "強迫勞動", "en": "Forced Labor",
    "def_zh": "1.非自願性工作： 包含強制加班、限制請假、脅迫、威脅、扣留押金或沒收個人證件。\n2.債務脅迫： 勞工因支付高額仲介費而背負債務，被迫在惡劣條件下持續工作以償還債務。",
    "def_en": "1. Involuntary Work: Includes forced overtime, restricted leave, coercion, threats, withholding of deposits, or confiscation of personal identification documents.\n2. Debt Bondage: Workers incurring high recruitment fees and being forced to work under poor conditions to repay the debt."
},
"hrdd02": {
    "zh": "勞動條件不公", "en": "Unfair Working Conditions",
    "def_zh": "1.超時違規： 專案趕工期間，員工被迫連續加班且未獲得法律規定的休息時間或加班費。\n2.薪資低於生活所需： 支付給基層勞工的薪資僅符合當地法定最低標準，但不足以應付基本食宿與醫療支出。",
    "def_en": "1. Overtime Violations: During peak project periods, employees are forced to work excessive hours without legally mandated rest periods or overtime pay.\n2. Wages Below Living Standards: Paying base-level workers wages that meet the legal minimum but are insufficient to cover basic food, housing, and medical expenses."
},
"hrdd03": {
    "zh": "健康與安全受損", "en": "Health and Safety Risks",
    "def_zh": "1.職業災害防護不足： 無落實教育訓練預防以及符合法規之消防系統因應緊急災難。\n2.心理健康負荷： 因長期高壓工作、人力配置不足，導致員工出現嚴重的身心耗竭或職業倦怠。",
    "def_en": "1. Inadequate Occupational Safety: Failure to implement preventive training and legally compliant fire safety systems for emergency disaster response.\n2. Mental Health Overload: Long-term high-pressure work or insufficient staffing leading to severe burnout or mental exhaustion among employees."
},
"hrdd04": {
    "zh": "職場歧視與偏見", "en": "Workplace Discrimination",
    "def_zh": "1.招募與晉升不公： 在面試或考核時，因應徵者的年齡、宗教或婚姻狀態而給予較低評分。\n2.資源分配偏差： 特定背景的員工在參與核心專案或海外受訓機會上受到隱性排擠。",
    "def_en": "1. Unfair Recruitment and Promotion: Giving lower ratings during interviews or appraisals based on a candidate's age, religion, or marital status.\n2. Resource Allocation Bias: Implicitly excluding employees of certain backgrounds from core projects or overseas training opportunities."
},
"hrdd05": {
    "zh": "結社自由受限", "en": "Restrictions on Freedom of Association",
    "def_zh": "1.干預組職： 管理層採取明示或暗示手段，阻撓員工成立工會或參與外部專業協會。\n2.溝通阻礙： 公司拒絕與員工選出的代表進行對話，或對參與協商的員工給予負面評價。",
    "def_en": "1. Interference with Organizing: Management using explicit or implicit means to obstruct employees from forming unions or joining professional associations.\n2. Communication Barriers: The company refusing to engage in meaningful dialogue with elected employee representatives or penalizing employees involved in negotiations."
},
"hrdd06": {
    "zh": "假訊息與社會對立", "en": "Disinformation and Social Polarization",
    "def_zh": "1.決策資訊不對稱： 公司重大變革資訊傳達不實，導致員工群體間相互猜忌，引發嚴重的勞資對立或罷工風險。\n2.供應鏈溝通誠信缺失： 在合作過程中提供具誤導性的業務資訊，導致經濟損失，或因謠言而遭受不公正的商譽評核。",
    "def_en": "1. Information Asymmetry in Decision-Making:Inaccurate communication of major corporate changes leads to mutual suspicion among employees, triggering severe labor-management antagonism or the risk of strikes.\n2. Lack of Integrity in Supply Chain Communication:Providing misleading business information during collaboration leads to financial losses for partners or subjects them to unfair reputation assessments based on rumors."
},
"hrdd07": {
    "zh": "數據監控與隱私權侵害", "en": "Surveillance and Privacy Infringement",
    "def_zh": "1.過度監控行為： 在未經充分告知下，利用軟體監控員工的桌面螢幕、通訊軟體內容或通訊往來。\n2.不當存取： 內部人員利用管理權限，在非業務必要情況下查看客戶或同事的私人存取紀錄。",
    "def_en": "1. Excessive Monitoring: Using software to monitor employee desktops, messaging content, or communication history without adequate prior notification.\n2. Improper Access: Internal personnel utilizing administrative privileges to view private records of customers or colleagues without business necessity."
},
"hrdd08": {
    "zh": "非人道對待風險", "en": "Inhuman Treatment Risks",
    "def_zh": "1.管理手段殘暴： 營運或供應鏈中存在公開辱罵、威脅恐嚇或剝奪基本生理需求（如飲水、如廁權）的管理方式。",
    "def_en": "1. Brutal Management Methods: Presence of public verbal abuse, intimidation, or deprivation of basic physiological needs (e.g., water, restroom access) in operations or supply chains."
},
"hrdd09": {
    "zh": "供應鏈非法雇用", "en": "Illegal Employment in the Supply Chain",
    "def_zh": "1.使用違法勞動力： 供應商為降低成本，雇用未達法定年齡的童工或未具備工作許可的黑工。\n2.層層轉包缺失： 供應商將業務轉包給無牌照小工廠，導致勞動管理出現法律真空地帶。",
    "def_en": "1. Use of Illegal Labor: Suppliers hiring child labor or workers without valid permits to reduce costs.\n2. Subcontracting Gaps: Suppliers outsourcing work to unlicensed workshops, resulting in a legal vacuum in labor management."
},
"hrdd10": {
    "zh": "數據隱私保護缺失", "en": "Data Privacy Vulnerability",
    "def_zh": "1.資安防護漏洞： 因技術加密不足或系統後門，導致大量用戶或員工個資遭駭客竊取或流失。\n2.第三方外洩： 將數據分享給協力廠商進行分析時，未落實去識別化或管控，導致隱私權受損。",
    "def_en": "1. Cybersecurity Gaps: Insufficient encryption or system backdoors leading to the theft or loss of large-scale customer or employee personal data.\n2. Third-Party Leakage: Failure to implement de-identification or controls when sharing data with third-party vendors for analysis, resulting in privacy harm.lved."
},
"hrdd11": {
    "zh": "演算法偏見與歧視", "en": "Algorithmic Bias",
    "def_zh": "1.招募系統偏差： AI 篩選履歷時，因訓練數據偏誤而自動排除特定族群（如特定性別或畢業學校）。\n2.服務不對等： 演算法自動對特定地區或族群的用戶提供品質較差或價格較高的服務方案。",
    "def_en": "1. Recruitment System Bias: AI screening tools automatically excluding certain groups (e.g., specific genders or schools) due to biased training data.\n2. Service Inequality: Algorithms automatically providing lower quality services or higher price points to users of specific regions or ethnic groups."
},
"hrdd12": {
    "zh": "職場性騷擾風險", "en": "Workplace Sexual Harassment",
    "def_zh": "1.言行騷擾： 職場中存在具性暗示的言語、圖片或肢體接觸，且環境氛圍對此類行為視為理所當然。\n2.權勢壓迫： 主管利用職位權力要求下屬提供私人服務或進行與性相關之交易。",
    "def_en": "1. Verbal and Behavioral Harassment: Presence of sexually suggestive language, images, or physical contact, with an environment that treats such behavior as \"normal.\"\n2. Power Abuse: Superiors using their position to demand personal favors or engage in sex-related transactions with subordinates."
},
"hrdd13": {
    "zh": "薪資不平等", "en": "Wage Inequality",
    "def_zh": "1.同職不同酬： 相同職級與資歷的員工，僅因性別不同而導致基本起薪或獎金分配出現顯著差異。\n2.考核偏誤： 考核標準不透明，導致特定族群在爭取薪資調升時面臨更高的隱形門檻。",
    "def_en": "1. Equal Work, Unequal Pay: Significant differences in base pay or bonuses for employees in the same position/seniority based solely on gender or other non-performance factors.\n2. Appraisal Bias: Opaque appraisal standards creating invisible barriers for specific groups seeking salary increases or promotions."
},
"hrdd14": {
    "zh": "女性領導權受限", "en": "Barriers to Female Leadership",
    "def_zh": "1.晉升透明度不足： 高階管理職位的遴選過程缺乏透明度，導致女性員工在升遷路徑中被排除。\n2.缺乏支持機制： 組織環境未提供如彈性工時等支持，導致優秀女性人才因家庭照顧責任被迫中斷職涯。",
    "def_en": "1. Lack of Promotion Transparency: Opaque selection processes for high-level management positions leading to the exclusion of female talent.\n2. Lack of Support Systems: Organizational failure to provide flexible work arrangements, forcing talented women to interrupt their careers due to caregiving responsibilities."
},
"hrdd15": {
    "zh": "舉報機制失效", "en": "Ineffective Grievance Mechanism",
    "def_zh": "1.管道不通暢： 舉報專線或信箱形同虛設，員工反映問題後長期未得到回應或處理。\n2.保密性受損： 舉報人的資訊被不當揭露給被檢舉人，導致員工失去對系統的信任。",
    "def_en": "1. Obstructed Channels: Whistleblowing hotlines or mailboxes being mere formalities, with employee reports remaining unaddressed for long periods.\n2. Compromised Confidentiality: Whistleblower identities being improperly disclosed to the accused, leading to a loss of trust in the system."
},
"hrdd16": {
    "zh": "報復利害關係人", "en": "Retaliation Against Stakeholders",
    "def_zh": "1.職務打壓： 員工在參與人權訪談或表達對公司不滿後，被調動至偏遠單位或邊緣職務。\n2.社會/心理壓力： 員工和供應商人員在發聲後，遭受公司主管在公開場合的言語排擠或恐嚇。",
    "def_en": "1. Career Suppression: Employees being transferred to remote units or marginalized roles after participating in human rights interviews or expressing dissatisfaction.\n2. Social/Psychological Pressure: Supplier personnel facing verbal exclusion or intimidation by company managers in public settings after speaking out."
},
"hrdd17": {
    "zh": "勞資關係緊張", "en": "Labor-Management Tensions",
    "def_zh": "1.衝突解決缺失： 雙方缺乏互信，當勞資爭議發生時，公司採取強硬壓制而非對話，導致罷工風險。\n2.資訊不對稱： 公司在進行重大營運調整（如裁員、撤點）前，未依法或依誠信原則與員工溝通。",
    "def_en": "1. Failure in Conflict Resolution: Lack of mutual trust leading to rigid management stances rather than dialogue during disputes, resulting in strike risks.\n2. Information Asymmetry: The company failing to communicate in good faith or according to law before major operational changes (e.g., layoffs, site closures)."
}
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
            # 1. Place an invisible marker at the absolute top of the page
            st.markdown('<div id="top-marker" style="position:absolute; top:-50px;"></div>', unsafe_allow_html=True)
            
            # 2. Trigger the scroll function (which now has a unique key per step)
            self.scroll_to_top()
    
            # 3. Render the specific step
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














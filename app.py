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
                "score_def": "評分定義:1 (無關) - 5 (高度相關)",
                "enter_note": "按下 'Enter' 僅會更新數值,請點擊下方按鈕繼續。",
                "mat_select_instr": "步驟 2.1: 請勾選 10 個議題",
                "mat_eval_instr": "步驟 2.2: 評估已選議題 (機會與風險)",
                "confirm_sel": "確認選擇",
                "status_label": "狀態",
                "status_help": "伊雲谷正在發生的議題 / 尚未在伊雲谷發生過的議題",
                "opp_val_label": "機會:價值創造 [1-5]",
                "opp_prob_label": "機會:可能性 [1-5]",
                "risk_imp_label": "風險:衝擊度 [1-5]",
                "risk_prob_label": "風險:可能性 [1-5]",
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
                "hrdd_error": "錯誤:每個議題都必須至少勾選一項「價值鏈關聯」(供應商或客戶)"
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
                "zh": "責任:是否有法律、財務、營運法規或公約上的責任",
                "en": "Responsibility: Legal, financial, operational regulations, or customary obligations."
            },
            "Influence": {
                "zh": "影響力:是否有能力影響組織的策略決策",
                "en": "Influence: Ability to impact the organization's strategic decision-making."
            },
            "Tension": {
                "zh": "張力:是否在財務、環境或社會議題上有立即的衝突或關注需求",
                "en": "Tension: Immediate conflicts or attention required regarding financial, environmental, or social issues."
            },
            "Diverse Perspectives": {
                "zh": "多元觀點:是否能帶來新的觀點、創新或市場理解",
                "en": "Diverse Perspectives: Potential to bring new views, innovation, or market understanding."
            },
            "Dependency": {
                "zh": "依賴性:對組織的依賴程度,或組織對其的依賴程度",
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
                "def_zh": "完善的資訊與雲端資安管理,不僅強化資料、機敏資訊與個資保護,也涵蓋資安事件發生時的快速復原能力。以 ISO 27001、NIST 等國際資安框架,建立完善的偵測與防護機制,並持續提升人員資安意識,以強化整體資安韌性與長期數位信任。",
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
            "m11": {"zh": "營運績效", "en": "Operational Performance", "def_zh": "持續創造經濟價值,確保公司獲利能力與財務穩健。", "def_en": "Continuously create economic value to ensure profitability and financial stability."},
            "m12": {"zh": "創新與數位責任", "en": "Innovation and Digital Responsibility", "def_zh": "推動產品與服務創新,並負責任地運用數位科技。", "def_en": "Promote product/service innovation and responsible use of digital technologies."},
            "m13": {"zh": "人工智慧與科技變革", "en": "AI and Technological Transformation", "def_zh": "關注 AI 發展趨勢,評估其對營運之影響與機會。", "def_en": "Monitor AI trends and assess impacts/opportunities on operations."},
            "m14": {"zh": "氣候變遷因應", "en": "Climate Change Adaptation", "def_zh": "鑑別氣候風險與機會,制定減緩與調適策略。", "def_en": "Identify climate risks/opportunities and formulate mitigation/adaptation strategies."},
            "m15": {"zh": "環境與能資源管理", "en": "Environment and Resource Management", "def_zh": "提升能源使用效率,推動節能減碳與資源循環。", "def_en": "Improve energy efficiency and promote carbon reduction/resource circulation."},
            "m16": {"zh": "生物多樣性", "en": "Biodiversity", "def_zh": "評估營運對生態之影響,支持生物多樣性保育。", "def_en": "Assess operational impact on ecology and support biodiversity conservation."},
            "m17": {"zh": "職場健康與安全", "en": "Workplace Health and Safety", "def_zh": "提供安全健康之工作環境,預防職業災害與疾病。", "def_en": "Provide a safe/healthy work environment to prevent occupational injuries/diseases."},
            "m18": {"zh": "員工培育與職涯發展", "en": "Employee Development", "def_zh": "提供完善教育訓練,協助員工規劃職涯發展。", "def_en": "Provide comprehensive training and assist in career planning."},
            "m19": {"zh": "人才吸引與留任", "en": "Talent Attraction and Retention", "def_zh": "提供具競爭力之薪酬福利,營造友善職場以留才。", "def_en": "Provide competitive compensation and a friendly workplace to retain talent."},
            "m20": {"zh": "社會關懷與鄰里促進", "en": "Social Care", "def_zh": "參與社會公益活動,回饋社區並促進鄰里關係。", "def_en": "Participate in social welfare and give back to the community."},
            "m21": {"zh": "人權平等", "en": "Equal Human Rights", "def_zh": "尊重與保護國際公認之人權,杜絕任何形式之歧視。", "def_en": "Respect/protect internationally recognized human rights and eliminate discrimination."}
        }
        self.mat_topic_keys = list(self.mat_topic_data.keys())

        # =============================================================================================
        # 4. TCFD Topics
        # =============================================================================================
        # Risks
        self.tcfd_risk_data = {
            "tr1": {
                "zh": "極端降雨事件",
                "en": "Extreme rainfall events",
                "def_zh": "背景:科技部TCCIP研究指出,未來颱風的生成呈現減少,而颱風帶來的降雨強度則呈現增加。風險:此型態的極端降雨將使得營運面臨更嚴重的颱風災害,包括市區淹水、道路坍方、淹水封閉等;因伊雲谷因服務性質,對於系統設備穩定性特別重視,當極端災害發生可能導致系統服務中斷,及人員傷亡,造成營運衝擊。",
                "def_en": "Background: Research by the Ministry of Science and Technology's TCCIP indicates that the formation of typhoons is decreasing, while the intensity of rainfall brought by typhoons is increasing. Risks: This type of extreme rainfall will expose operations to more severe typhoon disasters, including urban flooding, road collapses, and flood closures. Because of the service nature of E-Cloud Valley, the stability of its system equipment is of paramount importance. Extreme disasters could lead to system service interruptions and personnel casualties, causing operational disruptions."
            },
            "tr2": {
                "zh": "長期氣候模式改變",
                "en": "Long-term climate pattern changes",
                "def_zh": "背景:根據國家氣候變遷科學報告評估顯示,臺灣未來極端高溫日數將顯著增加,並伴隨更明顯的乾旱趨勢,反映出氣候模式長期改變的趨勢。這些變化可能對企業日常運作與環境條件造成影響。風險:持續高溫、乾旱及異常低溫情況可能帶來營運風險,如提高辦公場所能源使用需求與成本,並影響員工健康與工作效能。",
                "def_en": "Background: According to the National Climate Change Scientific Report, Taiwan is expected to experience a significant increase in the number of days with extreme high temperatures, accompanied by a more pronounced drought trend, reflecting a long-term shift in climate patterns. These changes may impact daily business operations and environmental conditions. Risks: Persistent high temperatures, drought, and abnormally low temperatures may pose operational risks, such as increased energy demands and costs in office spaces, and negatively impact employee health and work efficiency."
            },
            "tr3": {
                "zh": "溫室氣體排放價格上升",
                "en": "Rising greenhouse gas emission prices",
                "def_zh": "背景:台灣已頒佈《氣候法》,溫室氣體排放將開始面臨各種費用與稅收。參考國際趨勢,每噸碳的價格預計逐步上升,海外營運據點也陸續實施碳稅或碳交易機制。若未來擴大海外營運,公司可能面臨營運成本增加的挑戰。風險:若減碳成效有限,公司未來可能面臨支付額外費用來覆蓋營運碳排放,增加營運成本。",
                "def_en": "Background: Taiwan has enacted the Climate Change Act, and greenhouse gas emissions will begin to face various fees and taxes. Referring to international trends, the price per ton of carbon is expected to gradually rise, and overseas operating locations are also gradually implementing carbon taxes or carbon trading mechanisms. If the company expands its overseas operations in the future, it may face the challenge of increased operating costs. Risk: If carbon reduction efforts are limited, the company may face additional costs to cover operational carbon emissions in the future, increasing operating costs."
            },
            "tr4": {
                "zh": "對既有的產品與服務增加強制性法規",
                "en": "Add mandatory regulations to existing products and services",
                "def_zh": "背景:歐盟已發佈《CBAM》開始針對原物料課稅,全球各國開始針對各項碳排放源制定法規、費用政策等。風險:政府開始強制所有供應商(下游往上)都需要提供產品/服務碳足跡,以確保終端消費者以此為消費判斷,產生違規罰款、銷售成本增加等風險。",
                "def_en": "Background: The EU has published the CBAM and begun taxing raw materials. Globally, countries are developing regulations and fee policies for various carbon emission sources. Risks: Governments are beginning to mandate that all suppliers provide the carbon footprint of their products and services for consumer decision-making, leading to potential fines for non-compliance and increased sales costs."
            },
            "tr5": {
                "zh": "溫室氣體盤查與揭露要求",
                "en": "Greenhouse gas inventory and disclosure requirements",
                "def_zh": "背景:根據金管會「上市櫃公司永續發展行動方案」,上市櫃公司未來需揭露合併公司範圍內的溫室氣體盤查資訊,以確保碳排放數據的完整性與透明度,作為投資人與利益關係人評估企業永續績效的重要依據。風險:未如規定揭露溫室氣體盤查資訊,可能遭主管機關處分,並影響公司信譽與外部信任。",
                "def_en": "Background: According to the Financial Supervisory Commission's Action Plan for the Sustainable Development of Listed Companies, companies will be required to disclose greenhouse gas inventories within their consolidated scope to ensure data integrity and transparency. Risk: Failure to disclose as required may result in regulatory penalties and damage to corporate reputation and trust."
            },
            "tr6": {
                "zh": "法律訴訟與合規",
                "en": "Legal proceedings and compliance",
                "def_zh": "背景:法規日益嚴格,及利害關係人高度關注企業碳排放資訊,因此必須揭露正確、完整的溫室氣體盤查資料。風險:若資訊不完整或不正確,公司可能違反法規,並影響信譽與外部信任。",
                "def_en": "Background: Increasingly stringent regulations and heightened stakeholder scrutiny require accurate and complete greenhouse gas disclosures. Risk: Incomplete or inaccurate information may lead to regulatory violations and reputational damage."
            },
            "tr7": {
                "zh": "利害關係人的關注度上升或負面回饋",
                "en": "Increased stakeholder attention or negative feedback",
                "def_zh": "背景:政府、投資人、供應鏈、客戶及員工等利害關係人高度關注企業永續、道德及環境表現,外部評比機構亦進行評分。風險:若永續績效不佳,可能遭受負面回饋,影響品牌形象與聲譽。",
                "def_en": "Background: Governments, investors, supply chains, customers, employees, and rating agencies closely scrutinize corporate sustainability performance. Risk: Poor performance may result in negative feedback, damaging brand image and reputation."
            },
            "tr8": {
                "zh": "既有產品與服務的低碳排替代品",
                "en": "Low-carbon alternatives to existing products and services",
                "def_zh": "背景:台灣進入碳有價時代,產品與服務的全生命週期碳足跡將影響成本與市場競爭。風險:市場出現更低碳的雲端與MSP服務,可能導致客戶轉換供應商,使公司競爭力下降。",
                "def_en": "Background: With carbon pricing, full life-cycle carbon footprints affect costs and competitiveness. Risk: Lower-carbon cloud and MSP services may attract customers, reducing the company's competitiveness."
            },
            "tr9": {
                "zh": "新技術投資成效不佳",
                "en": "Unsuccessful investment in new technologies",
                "def_zh": "背景:氣候相關新技術快速發展,吸引企業投入資源。風險:若評估不足,可能因技術淘汰、市場策略不足或法規變動導致投資失敗。",
                "def_en": "Background: Rapid development of climate-related technologies attracts investment. Risk: Inadequate assessment may lead to failure due to technological obsolescence, poor market strategy, or regulatory changes."
            },
            "tr10": {
                "zh": "低碳技術轉型的轉型成本",
                "en": "Transition costs of low-carbon technology transformation",
                "def_zh": "背景:因應COP30能源轉型與碳管理要求,需調整營運模式與技術。風險:轉型過程將產生初期投資成本、資源限制及成本上升,影響營運穩定性與競爭力。",
                "def_en": "Background: To meet COP30 energy transition and carbon management requirements, operational models and technologies must be adjusted. Risk: Initial investment, resource constraints, and rising costs may affect operational stability and competitiveness."
            }
        }

        # Opportunities - 修正這裡的語法錯誤
        self.tcfd_opp_data = {
            "to1": {
                "zh": "使用低碳排的能源",
                "en": "Use low-carbon energy",
                "def_zh": "1. 背景:台灣推行全面能源轉型,逐步邁向2050浄零目標\n2. 機會:積極推低碳排能源之使用,獲得參與國際倡議之資格(如RE100),增加公司名譽、降低服務碳足跡、提升產品與服務之市場競爭力",
                "def_en": "1. Background: Taiwan is implementing a comprehensive energy transition, gradually moving towards its 2050 net-zero target.\n\n2. Opportunities: Actively promoting the use of low-carbon energy sources can qualify the company to participate in international initiatives (such as RE100), enhancing its reputation, reducing its service carbon footprint, and improving the market competitiveness of its products and services."
            },
            "to2": {
                "zh": "碳交易市場參與",
                "en": "Participation in the carbon trading market",
                "def_zh": "1. 背景:

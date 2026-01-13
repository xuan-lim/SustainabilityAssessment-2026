def render_tcfd(self):
        st.title(self.get_ui("step4_title"))
        results = []
        lang = st.session_state.language
        
        st.write("")
        
        # 1. Opportunities Section (Top)
        st.markdown(f"## 🌟 {self.get_ui('opp_header')}")
        st.markdown("---")
        
        for idx, (key, info) in enumerate(self.tcfd_opp_data.items()):
            display_text = info[lang]
            def_text = info[f"def_{lang}"]
            
            # Use container with custom styling for each item
            with st.container():
                # Use columns for better layout: icon/number + content
                col_icon, col_content = st.columns([0.5, 9.5])
                
                with col_icon:
                    st.markdown(f"### {idx + 1}")
                
                with col_content:
                    st.markdown(f"**{display_text}**")
                    # Show definition in expander instead of help tooltip
                    with st.expander("ℹ️ Definition"):
                        st.write(def_text)
                    
                    # Sliders in columns
                    c1, c2 = st.columns(2)
                    with c1:
                        sev = st.slider(
                            self.get_ui("val_create_label"), 
                            1, 5, 3, 
                            key=f"tcfd_os_{key}"
                        )
                    with c2:
                        like = st.slider(
                            self.get_ui("like_label"), 
                            1, 5, 3, 
                            key=f"tcfd_ol_{key}"
                        )
                    
                    results.append({
                        "Type": "Opportunity", 
                        "Topic": info["en"], 
                        "Severity/Value": sev, 
                        "Likelihood": like
                    })
                
                # Visual separator between items
                st.markdown("---")
        
        st.write("")
        st.write("")
        
        # 2. Risks Section (Bottom)
        st.markdown(f"## ⚠️ {self.get_ui('risk_header')}")
        st.markdown("---")
        
        for idx, (key, info) in enumerate(self.tcfd_risk_data.items()):
            display_text = info[lang]
            def_text = info[f"def_{lang}"]
            
            # Use container with custom styling
            with st.container():
                col_icon, col_content = st.columns([0.5, 9.5])
                
                with col_icon:
                    st.markdown(f"### {idx + 1}")
                
                with col_content:
                    st.markdown(f"**{display_text}**")
                    # Show definition in expander
                    with st.expander("ℹ️ Definition"):
                        st.write(def_text)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        sev = st.slider(
                            self.get_ui("sev_label"), 
                            1, 5, 3, 
                            key=f"tcfd_rs_{key}"
                        )
                    with c2:
                        like = st.slider(
                            self.get_ui("like_label"), 
                            1, 5, 3, 
                            key=f"tcfd_rl_{key}"
                        )
                    
                    results.append({
                        "Type": "Risk", 
                        "Topic": info["en"], 
                        "Severity/Value": sev, 
                        "Likelihood": like
                    })
                
                # Visual separator
                st.markdown("---")
        
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




















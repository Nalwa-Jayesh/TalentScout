import streamlit as st
from utils import query_model, check_exit, save_candidate_data, generate_technical_questions
from analysis import ConversationAnalyzer
from resume_parser import ResumeParser
from ui_utils import (
    init_page_config,
    apply_custom_styling,
    create_sidebar_menu,
    create_chat_interface,
    display_progress,
    display_analysis_dashboard
)
import json
from pathlib import Path

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'candidate_info' not in st.session_state:
    st.session_state.candidate_info = {}
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = ConversationAnalyzer()
if 'conversation_started' not in st.session_state:
    st.session_state.conversation_started = False
if 'input_method' not in st.session_state:
    st.session_state.input_method = None

# Initialize page configuration and styling
init_page_config()
apply_custom_styling()

# Create sidebar menu
selected = create_sidebar_menu()

# Main content area
if selected == "Chat":
    if not st.session_state.input_method:
        st.title("Welcome to TalentScout AI Assistant")
        st.markdown("""
            <div style='text-align: center; padding: 2rem;'>
                <h2>How would you like to proceed?</h2>
                <p>Choose your preferred method to start the screening process.</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
                <div style='text-align: center; padding: 1rem; border: 2px solid #e0e0e0; border-radius: 10px;'>
                    <h3>📝 Manual Input</h3>
                    <p>Fill in your information step by step</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Start Manual Input", key="manual"):
                st.session_state.input_method = "manual"
                st.rerun()
        
        with col2:
            st.markdown("""
                <div style='text-align: center; padding: 1rem; border: 2px solid #e0e0e0; border-radius: 10px;'>
                    <h3>📄 Upload Resume</h3>
                    <p>Upload your resume for automatic processing</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Upload Resume", key="resume"):
                st.session_state.input_method = "resume"
                st.rerun()
    
    elif st.session_state.input_method == "resume":
        st.title("Resume Upload")
        st.markdown("""
            <div style='text-align: center; padding: 1rem;'>
                <p>Upload your resume in PDF or DOCX format.</p>
            </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'docx'])
        
        if uploaded_file:
            try:
                parser = ResumeParser()
                file_type = uploaded_file.name.split('.')[-1].lower()
                resume_data = parser.parse_resume(uploaded_file.getvalue(), file_type)
                
                # Update candidate info with parsed data
                st.session_state.candidate_info.update({
                    "email": resume_data.get("email"),
                    "phone": resume_data.get("phone"),
                    "years_experience": resume_data.get("years_experience"),
                    "tech_stack": resume_data.get("tech_stack", [])
                })
                
                # Show extracted information
                st.success("Resume parsed successfully!")
                st.markdown("### Extracted Information")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("📧 Email:", resume_data.get("email", "Not found"))
                    st.write("📱 Phone:", resume_data.get("phone", "Not found"))
                    st.write("⏳ Years of Experience:", resume_data.get("years_experience", "Not found"))
                
                with col2:
                    st.write("🛠️ Tech Stack:")
                    for tech in resume_data.get("tech_stack", []):
                        st.write(f"- {tech}")
                
                # Ask for missing information
                st.markdown("### Please review and fill in any missing information:")
                if not st.session_state.candidate_info.get("full_name"):
                    st.session_state.candidate_info["full_name"] = st.text_input("Full Name", value=st.session_state.candidate_info.get("full_name", ""), key="resume_full_name")
                if not st.session_state.candidate_info.get("email"):
                    st.session_state.candidate_info["email"] = st.text_input("Email", value=st.session_state.candidate_info.get("email", ""), key="resume_email")
                if not st.session_state.candidate_info.get("phone"):
                    st.session_state.candidate_info["phone"] = st.text_input("Phone Number", value=st.session_state.candidate_info.get("phone", ""), key="resume_phone")
                if not st.session_state.candidate_info.get("years_experience") or st.session_state.candidate_info.get("years_experience") == 0:
                    try:
                        years_exp_input = st.text_input("Years of Experience (e.g., 5)", value=str(st.session_state.candidate_info.get("years_experience", "")), key="resume_years_exp")
                        if years_exp_input:
                            st.session_state.candidate_info["years_experience"] = int(years_exp_input)
                    except ValueError:
                        st.error("Years of Experience must be a number.")
                if not st.session_state.candidate_info.get("desired_position"):
                    st.session_state.candidate_info["desired_position"] = st.text_input("Desired Position", value=st.session_state.candidate_info.get("desired_position", ""), key="resume_desired_pos")
                if not st.session_state.candidate_info.get("current_location"):
                    st.session_state.candidate_info["current_location"] = st.text_input("Current Location (City, Country)", value=st.session_state.candidate_info.get("current_location", ""), key="resume_current_loc")
                if not st.session_state.candidate_info.get("tech_stack"):
                    tech_stack_input = st.text_area("Tech Stack (comma-separated, e.g., Python, React, AWS)", value=", ".join(st.session_state.candidate_info.get("tech_stack", [])), key="resume_tech_stack")
                    st.session_state.candidate_info["tech_stack"] = [t.strip() for t in tech_stack_input.split(',') if t.strip()]

                # Check if all critical info is available to enable starting screening
                all_info_present = all([
                    st.session_state.candidate_info.get("full_name"),
                    st.session_state.candidate_info.get("email"),
                    st.session_state.candidate_info.get("phone"),
                    st.session_state.candidate_info.get("years_experience") is not None,
                    st.session_state.candidate_info.get("desired_position"),
                    st.session_state.candidate_info.get("current_location"),
                    st.session_state.candidate_info.get("tech_stack") # Assuming tech_stack can be an empty list if not found
                ])

                if st.button("Start Screening", disabled=not all_info_present):
                    st.session_state.conversation_started = True
                    # Generate initial questions based on tech stack after resume parsing
                    if st.session_state.candidate_info.get("tech_stack"):
                        initial_questions = generate_technical_questions(st.session_state.candidate_info["tech_stack"])
                        st.session_state.messages.append({"role": "assistant", "content": f"Thank you for uploading your resume! To start, here are some technical questions based on your tech stack:\n\n{initial_questions}"}) 
                    else:
                        st.session_state.messages.append({"role": "assistant", "content": "Thank you for uploading your resume! I'm ready to begin the screening process. What is your full name?"})
                    st.rerun()
            
            except Exception as e:
                st.error(f"Error processing resume: {str(e)}")

        # Add a back button
        if st.button("Back to Selection"):
            st.session_state.input_method = None
            st.rerun()
    
    elif st.session_state.input_method == "manual":  # Manual input form
        st.title("Manual Candidate Information Input")
        st.markdown("""
            <div style='text-align: center; padding: 1rem;'>
                <p>Please fill in your details below to start the screening process.</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("manual_candidate_form"):
            full_name = st.text_input("Full Name", value=st.session_state.candidate_info.get("full_name", ""))
            email = st.text_input("Email", value=st.session_state.candidate_info.get("email", ""))
            phone = st.text_input("Phone Number", value=st.session_state.candidate_info.get("phone", ""))
            years_experience = st.text_input("Years of Experience (e.g., 5)", value=str(st.session_state.candidate_info.get("years_experience", "")))
            desired_position = st.text_input("Desired Position (e.g., Software Engineer)", value=st.session_state.candidate_info.get("desired_position", ""))
            current_location = st.text_input("Current Location (City, Country)", value=st.session_state.candidate_info.get("current_location", ""))
            tech_stack = st.text_area("Tech Stack (comma-separated, e.g., Python, React, AWS)", value=", ".join(st.session_state.candidate_info.get("tech_stack", [])))

            submitted = st.form_submit_button("Submit Details")

            if submitted:
                # Basic validation
                if not full_name or not email or not phone or not years_experience or not desired_position or not current_location or not tech_stack:
                    st.error("Please fill in all the required fields.")
                else:
                    try:
                        st.session_state.candidate_info.update({
                            "full_name": full_name,
                            "email": email,
                            "phone": phone,
                            "years_experience": int(years_experience),
                            "desired_position": desired_position,
                            "current_location": current_location,
                            "tech_stack": [t.strip() for t in tech_stack.split(',') if t.strip()]
                        })
                        st.session_state.conversation_started = True
                        st.success("Details submitted successfully! Starting screening...")
                        st.rerun()
                    except ValueError:
                        st.error("Years of Experience must be a number.")
        
        # Add a back button
        if st.button("Back to Selection"):
            st.session_state.input_method = None
            st.rerun()

    # Existing chat interface logic, now only active when conversation_started is True
    if st.session_state.conversation_started:
        # Add initial greeting if conversation just started and no messages yet
        if not st.session_state.messages:
            st.session_state.messages.append({"role": "assistant", "content": "Hello! I'm your TalentScout AI Assistant. How can I help you today?"})
            # For manual input, if tech stack is available, ask questions
            if st.session_state.input_method == "manual" and st.session_state.candidate_info.get("tech_stack"):
                 initial_questions = generate_technical_questions(st.session_state.candidate_info["tech_stack"])
                 st.session_state.messages.append({"role": "assistant", "content": f"Based on your provided tech stack, here are some initial questions:\n\n{initial_questions}"})

        chat_container, input_container = create_chat_interface()
        
        # Display chat messages
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
                    
                    # Analyze user messages for sentiment and language
                    if message["role"] == "user":
                        st.session_state.analyzer.update_history(
                            message["content"],
                            message["role"]
                        )
        
        # Chat input
        with input_container:
            if prompt := st.chat_input("Type your message here..."):
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # Check for exit command
                if check_exit(prompt):
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "Thank you for your time! A recruiter will review your information and get back to you soon."
                    })
                    st.stop()
                
                # Process user input and update candidate info - this part is now for additional questions/chat after form submission
                # No longer collecting primary info here
                
                # Generate response using the model
                response = query_model(prompt)
                st.session_state.messages.append({"role": "assistant", "content": response[0]})
                
                # Save candidate data if all information is collected (this condition should be updated if desired)
                # The primary data collection is now via the form
                if len(st.session_state.candidate_info) >= 6:  # Check if essential fields are filled
                    save_candidate_data(st.session_state.candidate_info)
                    st.session_state.analyzer.save_analysis(
                        st.session_state.candidate_info.get("full_name", "unknown_candidate")
                    )
        
        # Display progress in sidebar (still relevant for completeness)
        display_progress(st.session_state.candidate_info)

elif selected == "Analysis":
    display_analysis_dashboard(st.session_state.analyzer)

elif selected == "Settings":
    st.title("Settings")
    
    # Model selection
    model_source = st.radio(
        "Select Model Source",
        ["Ollama (Local)", "Hugging Face"],
        help="Choose whether to use local Ollama or Hugging Face API"
    )
    
    # Language selection
    language = st.selectbox(
        "Preferred Language",
        ["English", "Spanish", "French", "German", "Chinese", "Japanese"],
        help="Select your preferred language for the conversation"
    )
    
    # Save settings
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")

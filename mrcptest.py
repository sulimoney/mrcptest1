import streamlit as st
from datetime import datetime
from streamlit.components.v1 import html
import random

class Question:
    def __init__(self, question_text, options, correct_answer, explanation):
        self.question_text = question_text
        self.options = options
        self.correct_answer = correct_answer
        self.explanation = explanation

def set_custom_style():
    st.markdown("""
    <style>
    .question-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .correct-highlight {
        background-color: #e6f4ea;
        border-left: 4px solid #34a853;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
    .incorrect-highlight {
        background-color: #fce8e6;
        border-left: 4px solid #ea4335;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
    .explanation-box {
        padding: 1rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
    .explanation-correct {
        background-color: #e6f4ea;
    }
    .explanation-incorrect {
        background-color: #fce8e6;
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize all required session state variables"""
    required_keys = {
        'current_q': 0,
        'score': 0,
        'answers': [None] * len(questions),
        'selected_options': [None] * len(questions),
        'start_time': datetime.now(),
        'submitted': [False] * len(questions),
        'shuffled_questions': None
    }
    
    for key, value in required_keys.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Shuffle questions only once per session
    if st.session_state.shuffled_questions is None:
        st.session_state.shuffled_questions = questions.copy()
        random.shuffle(st.session_state.shuffled_questions)

def display_question():
    """Display current question and answer options"""
    st.session_state.current_q = max(0, min(st.session_state.current_q, len(st.session_state.shuffled_questions)-1))
    question = st.session_state.shuffled_questions[st.session_state.current_q]
    
    with st.container():
        st.markdown(f"### Question {st.session_state.current_q + 1}")
        st.markdown(f"<div class='question-card'>{question.question_text}</div>", 
                   unsafe_allow_html=True)
        
        if not st.session_state.submitted[st.session_state.current_q]:
            options = [f"{chr(65+i)}. {opt}" for i, opt in enumerate(question.options)]
            selected = st.radio("Select your answer:", options, index=None,
                              key=f"q{st.session_state.current_q}")
            
            if selected:
                clean_answer = selected.split(". ", 1)[1]
                st.session_state.selected_options[st.session_state.current_q] = clean_answer
                
            if st.button("Submit Answer", key=f"submit_{st.session_state.current_q}"):
                handle_answer(question)
        else:
            selected = st.session_state.selected_options[st.session_state.current_q]
            st.markdown(f"**Your answer:** {selected}")
            show_explanation(question)

def handle_answer(question):
    """Validate answer and update session state"""
    current_q = st.session_state.current_q
    selected = st.session_state.selected_options[current_q]
    
    if not selected:
        st.warning("Please select an answer before submitting!")
        return
    
    is_correct = selected == question.correct_answer
    
    if st.session_state.answers[current_q] is None:
        if is_correct:
            st.session_state.score += 1
        st.session_state.answers[current_q] = is_correct
    
    st.session_state.submitted[current_q] = True
    st.rerun()

def show_explanation(question):
    """Display explanation after submission"""
    is_correct = st.session_state.answers[st.session_state.current_q]
    explanation_class = "explanation-correct" if is_correct else "explanation-incorrect"
    
    with st.container():
        st.markdown("---")
        if is_correct:
            st.markdown("<div class='correct-highlight'>✅ Correct answer!</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='incorrect-highlight'>❌ Correct answer: **{question.correct_answer}**</div>", 
                       unsafe_allow_html=True)
        
        st.markdown(f"<div class='explanation-box {explanation_class}'>"
                   f"<strong>Explanation:</strong> {question.explanation}</div>", 
                   unsafe_allow_html=True)

def navigation_controls():
    """Previous/Next question controls"""
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        disabled_prev = st.session_state.current_q == 0
        if st.button("⏮ Previous", disabled=disabled_prev):
            st.session_state.current_q -= 1
            st.rerun()
    with col2:
        disabled_next = not st.session_state.submitted[st.session_state.current_q]
        if st.button("Next ⏭", disabled=disabled_next):
            st.session_state.current_q += 1
            st.rerun()

    with col3:
        if st.button("🔄 Restart Quiz"):
            restart_quiz()

def progress_sidebar():
    """Progress tracking sidebar with live timer"""
    with st.sidebar:
        st.header("Progress Tracker")
        
        # JavaScript live timer
        timer_html = f"""
        <div id="timer-display" style="font-size:1.25rem; margin-bottom:1rem;">
            ⏱️ Time Elapsed: <span id="time">00:00:00</span>
        </div>
        <script>
            const startTime = new Date("{st.session_state.start_time.isoformat()}").getTime();
            
            function updateTimer() {{
                const now = new Date().getTime();
                const elapsed = now - startTime;
                
                const hours = Math.floor(elapsed / (1000 * 60 * 60));
                const minutes = Math.floor((elapsed % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((elapsed % (1000 * 60)) / 1000);
                
                document.getElementById("time").innerHTML = 
                    String(hours).padStart(2, '0') + ":" + 
                    String(minutes).padStart(2, '0') + ":" + 
                    String(seconds).padStart(2, '0');
                
                setTimeout(updateTimer, 1000);
            }}
            
            updateTimer();
        </script>
        """
        html(timer_html)
        
        # Progress metrics
        attempted = sum(st.session_state.submitted)
        total_questions = len(st.session_state.shuffled_questions)
        accuracy = (st.session_state.score / attempted * 100) if attempted > 0 else 0
        st.metric("📝 Questions Attempted", f"{attempted}/{total_questions}")
        st.metric("🎯 Accuracy", f"{accuracy:.1f}%" if attempted > 0 else "N/A")
        
        # Progress bar
        progress = attempted / total_questions
        st.progress(progress)
        
        # Question navigator
        st.subheader("Question Navigator")
        cols = st.columns(4)
        for i in range(len(st.session_state.shuffled_questions)):
            with cols[i % 4]:
                status = ""
                if st.session_state.submitted[i]:
                    status = "✅" if st.session_state.answers[i] else "❌"
                elif i == st.session_state.current_q:
                    status = "📍"
                else:
                    status = "⬜"
                
                if st.button(f"Q{i+1} {status}", key=f"nav_{i}"):
                    if 0 <= i < len(st.session_state.shuffled_questions):
                        st.session_state.current_q = i
                        st.rerun()

def restart_quiz():
    """Reset all session state variables"""
    # Create new shuffled questions
    st.session_state.shuffled_questions = questions.copy()
    random.shuffle(st.session_state.shuffled_questions)
    
    # Reset other states
    st.session_state.current_q = 0
    st.session_state.score = 0
    st.session_state.answers = [None] * len(questions)
    st.session_state.selected_options = [None] * len(questions)
    st.session_state.start_time = datetime.now()
    st.session_state.submitted = [False] * len(questions)
    st.rerun()

def main():
    st.set_page_config(
        page_title="MRCP Exam Practice",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    set_custom_style()
    initialize_session_state()
    
    st.title("MRCP Examination Practice Platform")
    st.caption("Test your medical knowledge with these clinically relevant questions")
    
    # Main content columns
    main_col, _ = st.columns([3, 1])
    
    with main_col:
        display_question()
        navigation_controls()
    
    progress_sidebar()

# Question bank with enhanced explanations
questions = [
    Question(
        "What is the most common cause of hypercalcemia in hospitalized patients?",
        ["Primary hyperparathyroidism", "Malignancy", "Vitamin D intoxication", "Sarcoidosis"],
        "Malignancy",
        "Malignancy is the most common cause of hypercalcemia in hospitalized patients, particularly in those with advanced cancer. Tumors can produce parathyroid hormone-related protein (PTHrP), leading to hypercalcemia. Other causes include primary hyperparathyroidism, vitamin D intoxication, and sarcoidosis. Always consider the clinical context and investigate accordingly."
    ),
    Question(
        "Which of the following is the first-line treatment for stable angina?",
        ["Beta-blockers", "Calcium channel blockers", "Nitrates", "ACE inhibitors"],
        "Beta-blockers",
        "Beta-blockers are the first-line treatment for stable angina. They reduce myocardial oxygen demand by lowering heart rate and contractility, thus decreasing the frequency and severity of angina episodes. Examples include metoprolol or atenolol. Consider nitrates for immediate symptom relief and calcium channel blockers as an alternative if beta-blockers are contraindicated."
    ),
    Question(
        "What is the most common cause of Addison's disease?",
        ["Tuberculosis", "Autoimmune adrenalitis", "Metastatic cancer", "HIV infection"],
        "Autoimmune adrenalitis",
        "Autoimmune adrenalitis is the most common cause of Addison's disease in developed countries. This condition results from autoimmune destruction of the adrenal cortex, leading to deficiencies in cortisol and aldosterone. Clinical features include fatigue, weight loss, hypotension, and hyperpigmentation. Diagnosis is confirmed by elevated ACTH levels and impaired cortisol response to Synacthen."
    ),
    Question(
        "Which of the following is a hallmark feature of rheumatoid arthritis?",
        ["Symmetrical polyarthritis", "Asymmetrical oligoarthritis", "Sacroiliitis", "Heberden's nodes"],
        "Symmetrical polyarthritis",
        "Symmetrical polyarthritis is a hallmark feature of rheumatoid arthritis (RA). It presents as inflammation and swelling in multiple small and large joints on both sides of the body. This symmetry helps distinguish RA from other forms of arthritis, such as osteoarthritis or psoriatic arthritis. Early diagnosis and treatment are crucial to prevent joint damage and improve long-term outcomes."
    ),
    Question(
        "What is the most common cause of community-acquired pneumonia?",
        ["Streptococcus pneumoniae", "Haemophilus influenzae", "Mycoplasma pneumoniae", "Legionella pneumophila"],
        "Streptococcus pneumoniae",
        "Streptococcus pneumoniae is the most common bacterial cause of community-acquired pneumonia (CAP). It is often associated with lobar pneumonia and can progress to complications such as bacteremia or meningitis. Risk factors include age, immunocompromised states, and chronic lung disease. Treatment typically involves beta-lactam antibiotics, with adjustment based on culture and sensitivity results."
    ),
    Question(
        "Which of the following is the most common cause of acute pancreatitis?",
        ["Gallstones", "Alcohol", "Hypertriglyceridemia", "ERCP"],
        "Gallstones",
        "Gallstones are the most common cause of acute pancreatitis, responsible for approximately 40-70% of cases. The mechanism involves obstruction of the pancreatic duct, leading to inflammation and autodigestion of the pancreas. Alcohol consumption is another significant cause, particularly in chronic drinkers. Hypertriglyceridemia and post-ERCP pancreatitis are less common but important causes to consider."
    ),
    Question(
        "What is the most common cause of upper gastrointestinal bleeding?",
        ["Peptic ulcer disease", "Oesophageal varices", "Gastric cancer", "Mallory-Weiss tear"],
        "Peptic ulcer disease",
        "Peptic ulcer disease (PUD) is the most common cause of upper gastrointestinal bleeding (UGIB), accounting for approximately 50% of cases. The primary risk factors include Helicobacter pylori infection and the use of non-steroidal anti-inflammatory drugs (NSAIDs), both of which disrupt the gastric mucosal barrier, leading to ulcer formation and potential haemorrhage. Patients may present with haematemesis (vomiting blood) or melaena (black, tarry stools) due to digested blood. The diagnosis is confirmed via upper gastrointestinal endoscopy, which may also allow therapeutic intervention such as adrenaline injection, thermal coagulation, or clipping. Management involves proton pump inhibitors (PPIs) to reduce gastric acid secretion and promote ulcer healing, alongside eradication therapy if H. pylori is detected."
    ),
    Question(
        "Which electrolyte abnormality is most commonly associated with adrenal insufficiency?",
        ["Hyperkalaemia", "Hypokalaemia", "Hypernatraemia", "Hypocalcaemia"],
        "Hyperkalaemia",
        "Hyperkalaemia is a key biochemical feature of adrenal insufficiency, resulting from aldosterone deficiency. In primary adrenal insufficiency (Addison’s disease), destruction of the adrenal cortex leads to reduced aldosterone production, impairing renal potassium excretion. This results in hyperkalaemia, hyponatraemia, and hypotension due to volume depletion. Patients with Addison’s disease may present with fatigue, weight loss, postural dizziness, and characteristic hyperpigmentation due to increased adrenocorticotropic hormone (ACTH) production. The diagnosis is confirmed with a short synacthen test, and treatment involves lifelong corticosteroid and mineralocorticoid replacement, typically with hydrocortisone and fludrocortisone."
    ),
    Question(
        "Which of the following is the most common cause of spontaneous bacterial peritonitis (SBP)?",
        ["Escherichia coli", "Klebsiella pneumoniae", "Streptococcus pneumoniae", "Pseudomonas aeruginosa"],
        "Escherichia coli",
        "Escherichia coli is the most common causative organism of spontaneous bacterial peritonitis (SBP), a life-threatening infection in patients with cirrhosis and ascitic fluid accumulation. SBP occurs due to bacterial translocation from the gut into the peritoneal cavity, facilitated by impaired immune defences in cirrhotic patients. The condition typically presents with fever, abdominal pain, worsening ascites, and encephalopathy. The diagnosis is confirmed if ascitic fluid analysis shows a neutrophil count ≥250 cells/µL. Empirical treatment involves intravenous third-generation cephalosporins, such as cefotaxime or ceftriaxone, with albumin infusion to reduce the risk of hepatorenal syndrome."
    ),
    Question(
        "What is the first-line treatment for anaphylaxis?",
        ["Intramuscular adrenaline", "Intravenous corticosteroids", "Intravenous antihistamines", "Nebulised salbutamol"],
        "Intramuscular adrenaline",
        "Intramuscular adrenaline (500 micrograms IM, repeated every 5 minutes as necessary) is the first-line treatment for anaphylaxis, a severe, life-threatening allergic reaction. Adrenaline acts on alpha and beta-adrenergic receptors to counteract hypotension, bronchospasm, and tissue oedema. Patients typically present with airway compromise, wheezing, hypotension, urticaria, and angioedema. Adjunctive treatments include oxygen, intravenous fluids, antihistamines (chlorphenamine), and corticosteroids (hydrocortisone), but these should not delay adrenaline administration. Patients should be observed for at least 6 hours due to the risk of a biphasic reaction and should be discharged with an adrenaline auto-injector and follow-up with an allergy specialist."
    ),
    Question(
        "Which of the following findings is most characteristic of cardiac tamponade?",
        ["Pulsus paradoxus", "Kussmaul’s sign", "Corrigan’s pulse", "Quincke’s sign"],
        "Pulsus paradoxus",
        "Pulsus paradoxus, a drop in systolic blood pressure of more than 10 mmHg during inspiration, is a hallmark feature of cardiac tamponade. This condition occurs due to excessive pericardial fluid accumulation, which restricts ventricular filling, leading to reduced cardiac output. Patients present with Beck’s triad: hypotension, muffled heart sounds, and raised jugular venous pressure (JVP). Additional signs include tachycardia and a narrow pulse pressure. The diagnosis is confirmed with echocardiography, which typically shows pericardial effusion and diastolic collapse of the right atrium and ventricle. Emergency pericardiocentesis is the definitive treatment."
    ),
    Question(
        "Which is the most common type of thyroid cancer?",
        ["Papillary carcinoma", "Follicular carcinoma", "Medullary carcinoma", "Anaplastic carcinoma"],
        "Papillary carcinoma",
        "Papillary carcinoma is the most common type of thyroid cancer, accounting for approximately 80% of cases. It often presents as a painless thyroid nodule and is more common in young adults and women. The condition is strongly associated with previous radiation exposure and genetic mutations, including RET/PTC rearrangements and BRAF mutations. It spreads primarily via lymphatics, leading to cervical lymph node metastases, but has an excellent prognosis. Diagnosis is confirmed by fine-needle aspiration cytology (FNAC) following an ultrasound scan. Treatment typically involves total thyroidectomy with or without radioactive iodine therapy, depending on the risk stratification."
    )
]

if __name__ == "__main__":
    main()

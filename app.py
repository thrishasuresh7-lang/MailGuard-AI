import pandas as pd
import os
import streamlit as st
import joblib
import sqlite3
from datetime import datetime
from auth import create_user, verify_user


# -----------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------

st.set_page_config(
    page_title="MailGuard AI | Smart Spam Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# -----------------------------------------
# LOAD MACHINE LEARNING MODEL
# -----------------------------------------

@st.cache_resource
def load_model():
    model = joblib.load("spam_model.pkl")
    vectorizer = joblib.load("vectorizer.pkl")
    return model, vectorizer


model, vectorizer = load_model()


# -----------------------------------------
# SESSION STATE
# -----------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = None


# -----------------------------------------
# SQLITE DATABASE
# -----------------------------------------

DB_NAME = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "scan_history.db"
)


def init_database():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                prediction TEXT NOT NULL,
                spam_probability REAL NOT NULL,
                scan_time TEXT NOT NULL
            )
        """)

        columns = [
            row[1]
            for row in conn.execute(
                "PRAGMA table_info(scans)"
            ).fetchall()
        ]

        if "user_id" not in columns:
            conn.execute(
                "ALTER TABLE scans ADD COLUMN user_id INTEGER"
            )


def save_scan(result, user_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            INSERT INTO scans
            (message, prediction, spam_probability, scan_time, user_id)
            VALUES (?, ?, ?, ?, ?)
        """, (
            result["message"],
            result["prediction"],
            result["spam_probability"],
            result["time"],
            user_id
        ))


def get_history(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        rows = conn.execute("""
            SELECT message, prediction, spam_probability, scan_time
            FROM scans
            WHERE user_id = ?
            ORDER BY id DESC
        """, (user_id,)).fetchall()

    return [
        {
            "message": row[0],
            "prediction": row[1],
            "spam_probability": row[2],
            "time": row[3]
        }
        for row in rows
    ]


def clear_database(user_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute(
            "DELETE FROM scans WHERE user_id = ?",
            (user_id,)
        )


init_database()
# -----------------------------------------
# USER AUTHENTICATION
# -----------------------------------------

if not st.session_state.authenticated:

    st.markdown(
        "<h1 style='text-align:center;color:#3997FF;'>"
        "MAILGUARD.AI 🛡️</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align:center;color:#A8BAD5;'>"
        "Your intelligent message security platform</p>",
        unsafe_allow_html=True
    )

    st.write("")

    left, right = st.columns([1, 1])

    with left:
        st.markdown("## Secure Your Inbox")

        st.markdown(
            "Detect suspicious messages, identify spam, "
            "and protect yourself with AI-powered analysis."
        )

        st.markdown("""
        - 🛡️ Intelligent spam detection
        - ⚡ Instant message analysis
        - 📊 Detailed security analytics
        - 🔐 Personal scan history
        """)

    with right:
        st.markdown("### Welcome")

        page = st.radio(
            "Choose an option",
            ["Sign In", "Create Account"],
            horizontal=True,
            label_visibility="collapsed"
        )

        if page == "Sign In":

            with st.form("login_form"):

                email = st.text_input("Email address")

                password = st.text_input(
                    "Password",
                    type="password"
                )

                login_button = st.form_submit_button(
                    "Sign In",
                    width="stretch"
                )

            if login_button:

                user = verify_user(email, password)

                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.rerun()

                else:
                    st.error("Invalid email or password.")

        else:

            with st.form("signup_form"):

                name = st.text_input("Full name")
                email = st.text_input("Email address")

                password = st.text_input(
                    "Create password",
                    type="password"
                )

                confirm_password = st.text_input(
                    "Confirm password",
                    type="password"
                )

                signup_button = st.form_submit_button(
                    "Create Account",
                    width="stretch"
                )

            if signup_button:

                if not name.strip() or not email.strip():
                    st.warning(
                        "Please enter your name and email."
                    )

                elif "@" not in email or "." not in email:
                    st.warning(
                        "Please enter a valid email address."
                    )

                elif len(password) < 8:
                    st.warning(
                        "Password must contain at least 8 characters."
                    )

                elif password != confirm_password:
                    st.error("Passwords do not match.")

                else:
                    success, message = create_user(
                        name, email, password
                    )

                    if success:
                        st.success(message)
                        st.info(
                            "Please select Sign In to log in."
                        )

                    else:
                        st.error(message)

    st.stop()
    # -----------------------------------------
# CUSTOM CSS
# -----------------------------------------

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #080E1B;
    color: #E5EAF5;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1250px;
}

section[data-testid="stSidebar"] {
    background: #0D1628;
    border-right: 1px solid #1C2940;
}

.brand {
    font-size: 25px;
    font-weight: 800;
    color: #F4F7FF;
    letter-spacing: -1px;
}

.brand span {
    color: #3997FF;
}

.sidebar-label {
    color: #8090AA;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    margin-top: 30px;
}

.hero {
    background: linear-gradient(120deg, #142746, #10203A 60%, #102B4C);
    border: 1px solid #25436B;
    border-radius: 18px;
    padding: 35px;
    margin-bottom: 28px;
}

.hero-tag {
    color: #63B0FF;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
}

.hero h1 {
    color: #FFFFFF;
    font-size: 36px;
    font-weight: 800;
    margin: 12px 0;
}

.hero p {
    color: #A8BAD5;
    font-size: 15px;
    line-height: 1.7;
    max-width: 650px;
}

.section-title {
    color: #F3F6FC;
    font-size: 21px;
    font-weight: 700;
    margin-bottom: 5px;
}

.section-subtitle {
    color: #8999B2;
    font-size: 13px;
    margin-bottom: 18px;
}

.metric-card {
    background: #101B2E;
    border: 1px solid #22324B;
    border-radius: 14px;
    padding: 20px;
    min-height: 112px;
}

.metric-label {
    color: #8FA1BB;
    font-size: 12px;
    font-weight: 600;
}

.metric-value {
    color: #F5F8FF;
    font-size: 27px;
    font-weight: 800;
    margin-top: 9px;
}

.metric-note {
    color: #4EA6FF;
    font-size: 11px;
    margin-top: 4px;
}

.input-card {
    background: #101B2E;
    border: 1px solid #263751;
    border-radius: 16px;
    padding: 24px;
}

.result-card {
    background: #101B2E;
    border: 1px solid #263751;
    border-radius: 16px;
    padding: 25px;
    margin-top: 20px;
}

.result-spam {
    border: 1px solid #A83D4B;
    background: #291923;
}

.result-safe {
    border: 1px solid #237B63;
    background: #112820;
}

.result-heading {
    font-size: 23px;
    font-weight: 800;
    color: #FFFFFF;
}

.result-description {
    color: #AAB7CC;
    font-size: 13px;
    margin-top: 8px;
}

div.stButton > button {
    background: linear-gradient(90deg, #237DE5, #398FFF);
    color: white;
    border: none;
    border-radius: 9px;
    height: 48px;
    font-weight: 700;
    transition: 0.2s;
}

div.stButton > button:hover {
    background: #1769C8;
    border: none;
    color: white;
}

textarea {
    border-radius: 10px !important;
}

div[data-testid="stProgressBar"] > div > div {
    background-color: #3997FF;
}

.footer {
    text-align: center;
    color: #64758F;
    font-size: 12px;
    border-top: 1px solid #202E44;
    padding-top: 22px;
    margin-top: 45px;
}

</style>
""", unsafe_allow_html=True)
# -----------------------------------------
# SIDEBAR AND NAVIGATION
# -----------------------------------------
def go_to_page(page):
    st.session_state.navigation_choice = page
    
with st.sidebar:

    st.markdown(
        '<div class="brand">MAILGUARD<span>.AI</span> 🛡️</div>',
        unsafe_allow_html=True
    )

    st.caption("INTELLIGENT MESSAGE SECURITY")

    st.divider()

    st.markdown("### 👤 My Account")

    st.write(
        f"Welcome, **{st.session_state.user['name']}**"
    )

    st.caption(st.session_state.user["email"])

    if st.button("🚪 Logout", width="stretch"):

        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.last_result = None
        st.session_state.history = []

        st.rerun()

    st.divider()

    st.markdown(
        '<div class="sidebar-label">WORKSPACE</div>',
        unsafe_allow_html=True
    )

    selected_page = st.radio(
    "Navigate",
    ["Dashboard", "Message Scanner", "Scan History", "Analytics", "My Profile"],
    label_visibility="collapsed",
    key="navigation_choice"
)

    st.divider()

    st.markdown(
        '<div class="sidebar-label">MODEL INFORMATION</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    **Algorithm**

    Multinomial Naive Bayes

    **Text Processing**

    TF-IDF Vectorization

    **Training Dataset**

    SMS Spam Collection

    **Test Accuracy**

    96.23%
    """)

    st.divider()

    st.markdown(
        '<div style="color:#8292AA;font-size:12px;">'
        '● System Ready<br><br>'
        'Version 1.0.0<br>'
        'Built with Python & Streamlit'
        '</div>',
        unsafe_allow_html=True
    )


# -----------------------------------------
# LOAD USER SCAN STATISTICS
# -----------------------------------------

all_scans = get_history(st.session_state.user["id"])

total_scans = len(all_scans)

spam_scans = sum(
    1 for item in all_scans
    if item["prediction"] == "spam"
)

safe_scans = total_scans - spam_scans
# -----------------------------------------
# DASHBOARD PAGE
# -----------------------------------------

if selected_page == "Dashboard":

    st.markdown("### ✦ AI-POWERED MESSAGE SECURITY")
    st.title("Stay ahead of spam.")
    st.write(
        "Analyze suspicious messages using machine learning. "
        "Detect unwanted content and identify potential spam "
        "before interacting with it."
    )

    st.markdown(
        '<div class="section-title">Dashboard Overview</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Your message security workspace at a glance.'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    metrics = [
        (c1, "MODEL ACCURACY", "96.23%", "Held-out test set"),
        (c2, "TOTAL SCANS", str(total_scans), "All-time scans"),
        (c3, "SPAM DETECTED", str(spam_scans), "All-time records"),
        (c4, "SAFE MESSAGES", str(safe_scans), "All-time records")
    ]

    for col, label, value, note in metrics:

        with col:

            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-note">{note}</div>
            </div>
            """, unsafe_allow_html=True)

    st.write("")

    st.markdown("### Quick Actions")

    q1, q2 = st.columns(2)

    with q1:
        st.button(
            "📨 Open Message Scanner",
            on_click=go_to_page,
            args=("Message Scanner",),
            width="stretch",
            key="dashboard_open_scanner"
        )

    with q2:
        st.button(
            "🕒 View Scan History",
            on_click=go_to_page,
            args=("Scan History",),
            width="stretch",
            key="dashboard_view_history"
        )
    # -----------------------------------------
# MESSAGE SCANNER PAGE
# -----------------------------------------

if selected_page == "Message Scanner":

    st.markdown("### ✦ INTELLIGENT MESSAGE ANALYSIS")
    st.title("Message Scanner")
    st.write(
        "Paste a suspicious message below. "
        "Our machine learning model will analyze it "
        "and identify whether it is spam or legitimate."
    )

    st.markdown(
        '<div class="section-title">Analyze Your Message</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Enter your message to perform an instant spam analysis.'
        '</div>',
        unsafe_allow_html=True
    )

    with st.container(border=True):

        st.markdown("#### 📨 Enter Message")

        with st.form("message_form"):

            message = st.text_area(
                "Message content",
                height=170,
                placeholder="Paste your email or message content here...",
                label_visibility="collapsed"
            )

            submitted = st.form_submit_button(
                "🔍 Analyze Message",
                width="stretch"
            )

        if submitted:

            if not message.strip():

                st.warning(
                    "Please enter a message before analyzing."
                )

            else:

                message_vector = vectorizer.transform([message])

                prediction = model.predict(message_vector)[0]

                spam_index = list(model.classes_).index("spam")

                probabilities = model.predict_proba(message_vector)[0]

                spam_probability = float(
                    probabilities[spam_index] * 100
                )

                result = {
                    "message": message[:100],
                    "prediction": prediction,
                    "spam_probability": spam_probability,
                    "time": datetime.now().strftime("%H:%M:%S")
                }

                st.session_state.last_result = result

                st.session_state.history.insert(0, result)

                save_scan(
                    result,
                    st.session_state.user["id"]
                )

                st.success("Message analysis completed!")
                # -----------------------------------------
# RESULT DISPLAY
# -----------------------------------------

if (
    selected_page == "Message Scanner"
    and st.session_state.last_result
):

    result = st.session_state.last_result

    st.write("")
    st.divider()

    st.markdown("### Analysis Result")

    if result["prediction"] == "spam":

        st.markdown(f"""
        <div class="result-card result-spam">

            <div style="color:#FF7786;font-size:12px;font-weight:700;">
                ⚠ SECURITY ALERT
            </div>

            <div class="result-heading">
                🚨 Spam Message Detected
            </div>

            <div class="result-description">
                The machine learning model classified this message
                as spam. Avoid clicking suspicious links or sharing
                personal information.
            </div>

        </div>
        """, unsafe_allow_html=True)

    else:

        st.markdown("""
        <div class="result-card result-safe">

            <div style="color:#58D9A9;font-size:12px;font-weight:700;">
                ✓ ANALYSIS COMPLETE
            </div>

            <div class="result-heading">
                ✅ Legitimate Message
            </div>

            <div class="result-description">
                The machine learning model classified this message
                as a legitimate message (ham).
                Still verify unexpected links and requests.
            </div>

        </div>
        """, unsafe_allow_html=True)

    st.write("")

    st.markdown("#### Analysis Details")

    r1, r2 = st.columns(2)

    with r1:

        st.metric(
            "Spam Probability",
            f"{result['spam_probability']:.2f}%"
        )

        st.progress(
            result["spam_probability"] / 100
        )

    with r2:

        st.metric(
            "Predicted Category",
            result["prediction"].upper()
        )

        st.caption(
            "Model-estimated spam probability, not a guarantee."
        )

    st.caption(
        "This model was trained on the SMS Spam Collection dataset. "
        "Its performance on real email messages has not been separately validated."
    )
    # -----------------------------------------
# SCAN HISTORY PAGE
# -----------------------------------------

if selected_page == "Scan History":

    st.markdown("### ✦ PERSONAL SECURITY RECORDS")
    st.title("Scan History")
    st.write(
        "View all your previously analyzed messages, "
        "check their predictions and review spam probabilities."
    )

    history_records = get_history(
        st.session_state.user["id"]
    )

    st.markdown("### 🕘 Your Previous Scans")

    st.caption(
        f"You have completed {len(history_records)} message scans."
    )

    if history_records:

        for index, item in enumerate(history_records):

            label = (
                "🚨 SPAM"
                if item["prediction"] == "spam"
                else "✅ HAM"
            )

            with st.container(border=True):

                st.markdown(
                    f"**{label}**  ·  {item['time']}"
                )

                st.write(item["message"])

                st.caption(
                    f"Spam Probability: "
                    f"{item['spam_probability']:.2f}%"
                )

                st.progress(
                    item["spam_probability"] / 100
                )

        st.divider()

        if st.button(
            "🗑️ Clear All Scan History",
            width="stretch"
        ):

            clear_database(
                st.session_state.user["id"]
            )

            st.session_state.history = []
            st.session_state.last_result = None

            st.success("Your scan history has been cleared!")

            st.rerun()

    else:

        st.info(
            "No scan history available yet. "
            "Visit Message Scanner to analyze your first message."
        )
        # -----------------------------------------
# ANALYTICS PAGE
# -----------------------------------------

if selected_page == "Analytics":

    st.markdown("### ✦ MACHINE LEARNING INSIGHTS")
    st.title("Model Analytics")
    st.write(
        "Explore the training dataset, model performance, "
        "classification metrics and prediction results."
    )

    st.markdown("### Dataset Distribution")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Legitimate Messages",
            "4,825"
        )

    with col2:
        st.metric(
            "Spam Messages",
            "747"
        )

    dataset_df = pd.DataFrame({
        "Category": ["Ham", "Spam"],
        "Messages": [4825, 747]
    })

    st.bar_chart(
        dataset_df.set_index("Category"),
        y="Messages"
    )

    st.divider()

    st.markdown("### Model Performance")

    m1, m2, m3 = st.columns(3)

    m1.metric("Accuracy", "96.23%")
    m2.metric("Spam Precision", "100%")
    m3.metric("Spam Recall", "72%")

    performance_df = pd.DataFrame({
        "Precision": [0.96, 1.00],
        "Recall": [1.00, 0.72],
        "F1 Score": [0.98, 0.84]
    }, index=["Ham", "Spam"])

    st.markdown("#### Classification Report")

    st.dataframe(
        performance_df.style.format("{:.2f}"),
        width="stretch"
    )

    st.divider()

    st.markdown("### Confusion Matrix")

    confusion_df = pd.DataFrame(
        [[966, 0], [42, 107]],
        index=["Actual Ham", "Actual Spam"],
        columns=["Predicted Ham", "Predicted Spam"]
    )

    st.dataframe(
        confusion_df,
        width="stretch"
    )

    st.caption(
        "Evaluation based on the held-out test dataset "
        "of 1,115 messages."
    )

    st.info(
        "The model uses Multinomial Naive Bayes and TF-IDF "
        "vectorization, trained on the SMS Spam Collection dataset."
    )
    # -----------------------------------------
# MY PROFILE PAGE
# -----------------------------------------
if selected_page == "My Profile":

    st.markdown("""
        <div class="hero">
            <h1>My Profile</h1>
            <p>View your MailGuard AI account information.</p>
        </div>
    """, unsafe_allow_html=True)

    user = st.session_state.user

    st.markdown("### Account Information")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input(
            "Full Name",
            value=user["name"],
            disabled=True
        )

    with col2:
        st.text_input(
            "Email Address",
            value=user["email"],
            disabled=True
        )

    st.divider()

    st.info(
        "Your account information is securely associated "
        "with your scan history."
    )
    # -----------------------------------------
# CSV EXPORT
# -----------------------------------------
if selected_page == "Scan History":

    st.divider()

    st.markdown("### 📥 Export Scan Report")

    export_records = get_history(
        st.session_state.user["id"]
    )

    if export_records:

        report_df = pd.DataFrame(export_records)

        report_df = report_df.rename(columns={
            "message": "Message",
            "prediction": "Prediction",
            "spam_probability": "Spam Probability",
            "time": "Scan Time"
        })

        csv_data = report_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="📥 Download Scan History (CSV)",
            data=csv_data,
            file_name="MailGuard_Scan_Report.csv",
            mime="text/csv",
            width="stretch"
        )

    else:
        st.info("No scan records available to export.")


# -----------------------------------------
# APPLICATION FOOTER
# -----------------------------------------
st.markdown("""
    <div class="footer">
        <p>🛡️ MailGuard AI</p>
        <p>Intelligent Spam Detection | Powered by Machine Learning</p>
        <p>© 2026 MailGuard AI. All rights reserved.</p>
    </div>
""", unsafe_allow_html=True)
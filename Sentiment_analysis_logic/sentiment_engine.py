import re

def analyze_sentiment(text):
    """STRICT ENGINE v5 — final-thread override + multi-thread complaint logic"""

    if not isinstance(text, str):
        text = str(text)

    t = text.lower()

    # Extract individual threads
    threads = re.split(r"thread\d+\s*-\s*", t)
    threads = [th.strip() for th in threads if th.strip()]
    last_thread = threads[-1] if threads else t

    def has(words, block=t):
        return any(w in block for w in words)

    def has_last(words):
        return any(w in last_thread for w in words)

    # 🎉 0️⃣ FINAL THREAD POSITIVE OVERRIDE (Highest Priority)
    strong_positive = [
        "wow! you just made our day", "made our day",
        "excellent", "thank you so much", "thanks a lot",
        "really appreciate", "great service", "amazing", "very happy"
    ]

    resolution_words = [
        "issue resolved", "problem resolved", "got it now",
        "i have received it", "now received", "received it now"
    ]

    if has_last(strong_positive):
        return {
            "sentiment_score": 0.80,
            "sentiment_label": "Positive",
            "emotion": "Joy",
            "complaint_risk_level": "Low",
            "ticket_category": "Appreciation"
        }

    if has_last(resolution_words):
        return {
            "sentiment_score": 0.50,
            "sentiment_label": "Positive",
            "emotion": "Satisfied",
            "complaint_risk_level": "Low",
            "ticket_category": "Resolved"
        }

    # 1️⃣ WRONG REPORT
    wrong_report_words = [
        "someone else", "belongs to someone", "different person",
        "not my kundali", "wrong kundali", "incorrect kundali",
        "wrong chart", "this is not mine", "sent the wrong report", "yadav"
    ]
    if has(wrong_report_words):
        return {
            "sentiment_score": -0.75,
            "sentiment_label": "Negative",
            "emotion": "Angry",
            "complaint_risk_level": "High",
            "ticket_category": "Wrong Report"
        }

    # 2️⃣ REFUND / CANCELLATION
    refund_words = [
        "refund","money back","cancel","cancel my order","want refund",
        "waste of money","not satisfied","not happy","bad service"
    ]
    if has(refund_words):
        return {
            "sentiment_score": -0.75,
            "sentiment_label": "Negative",
            "emotion": "Disappointed",
            "complaint_risk_level": "High",
            "ticket_category": "Refund / Cancellation"
        }

    # 3️⃣ NOT RESOLVED
    unresolved_words = [
        "issue not resolved","not resolved yet","still not resolved",
        "cannot close the ticket","ticket closed","reopen the ticket","not solved"
    ]
    if has(unresolved_words):
        return {
            "sentiment_score": -0.65,
            "sentiment_label": "Negative",
            "emotion": "Angry",
            "complaint_risk_level": "High",
            "ticket_category": "Unresolved Issue"
        }

    # 4️⃣ DELAY STRICT
    delay_words = [
        "not received","didnt receive","didn't receive","didnt get",
        "didn't get","not got","no report","not attached",
        "no report attached","report missing","didnt recive",
        "recieve","recive","nahi mila","kab milega",
        "waiting for report","still waiting","report not come",
        "report not came","not delivered","class recording not received",
        "class link not received","didn't get class","missed class"
    ]
    if has(delay_words):
        return {
            "sentiment_score": -0.45,
            "sentiment_label": "Negative",
            "emotion": "Frustrated",
            "complaint_risk_level": "Medium",
            "ticket_category": "Service Delay / Not Delivered"
        }

    # 5️⃣ CORRECTION ISSUE
    correction_words = [
        "wrong","incorrect","galat","mistake","dob","birth time",
        "time of birth","please correct","update the time","change my details"
    ]
    if has(correction_words):
        return {
            "sentiment_score": -0.25,
            "sentiment_label": "Neutral",
            "emotion": "Concerned",
            "complaint_risk_level": "Low",
            "ticket_category": "Correction Request"
        }

    # 6️⃣ LANGUAGE ISSUE
    language_words = [
        "hindi me","hindi mein","send in hindi","english nahi chahiye",
        "hindi chahiye","want in hindi","report in hindi"
    ]
    if has(language_words):
        return {
            "sentiment_score": -0.20,
            "sentiment_label": "Neutral",
            "emotion": "Concerned",
            "complaint_risk_level": "Low",
            "ticket_category": "Language Issue"
        }

    # 7️⃣ CHEATING / FRAUD ACCUSATIONS
    fraud_words = [
        "cheating", "fraud", "scam", "fake", "cheater",
        "are you guys cheating", "you are cheating"
    ]
    if has(fraud_words):
        return {
            "sentiment_score": -0.85,
            "sentiment_label": "Negative",
            "emotion": "Angry",
            "complaint_risk_level": "Critical",
            "ticket_category": "Fraud Accusation"
        }

    # DEFAULT
    return {
        "sentiment_score": 0.0,
        "sentiment_label": "Neutral",
        "emotion": "Neutral",
        "complaint_risk_level": "Low",
        "ticket_category": "General Query"
    }

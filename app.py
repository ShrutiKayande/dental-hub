from flask import Flask, render_template, request, jsonify
from datetime import datetime
import requests
import os

app = Flask(__name__)

# In-memory storage
appointments = []
feedbacks = []

# ========== CLINIC CONTACT NUMBER ==========
CLINIC_NUMBER = "919405363270"
CLINIC_NUMBER_DISPLAY = "+919405363270"

# ========== FAST2SMS CONFIGURATION ==========
FAST2SMS_API_KEY = "1xn0V3dlmKohX42AkQgzqsJUaZO68brCwjtW7cBi9DyeRFTHEMMYqTBAlEi8QFHOnJ0XKIDo7ugr4czV"

# ========== SMS FUNCTION ==========
def send_sms(phone_number, message):
    try:
        clean_number = phone_number.replace('+', '').replace(' ', '').strip()
        url = "https://www.fast2sms.com/dev/bulkV2"
        params = {
            "authorization": FAST2SMS_API_KEY,
            "message": message,
            "language": "english",
            "route": "q",
            "numbers": clean_number
        }
        headers = {'cache-control': "no-cache"}
        response = requests.request("GET", url, headers=headers, params=params)
        result = response.json()
        if result.get('return'):
            print(f"SMS sent to {phone_number}")
            return True
        else:
            print(f" SMS failed: {result}")
            return False
    except Exception as e:
        print(f" SMS Error: {e}")
        return False

# ==================== PAGE ROUTES ====================
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/doctors')
def doctors():
    return render_template('doctors.html')

@app.route('/appointment')
def appointment_page():
    return render_template('appointment.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/feedback')
def feedback_page():
    return render_template('feedback.html', feedbacks=feedbacks)

# ==================== API ENDPOINTS ====================
@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    name = request.form.get('name')
    phone = request.form.get('phone')
    date = request.form.get('date')
    time_slot = request.form.get('time_slot', 'Flexible')
    
    if name and phone and date:
        appointment_data = {
            'name': name, 'phone': phone, 'date': date,
            'time_slot': time_slot,
            'booked_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        appointments.append(appointment_data)
        print(f"\n New appointment: {name} - {date} at {time_slot}")
        
        patient_sms = f"Dear {name}, your appointment with Dr. Yogesh Nagargoje's Dental Hub is confirmed for {date} at {time_slot}. Call {CLINIC_NUMBER_DISPLAY} for changes. Thank you!"
        send_sms(phone, patient_sms)
        
        clinic_sms = f"NEW APPOINTMENT! Patient: {name}, Phone: {phone}, Date: {date}, Time: {time_slot}"
        send_sms(CLINIC_NUMBER, clinic_sms)
        
        return jsonify({'success': True, 'message': 'Appointment booked successfully! SMS sent.'})
    
    return jsonify({'success': False, 'message': 'Please fill all fields'}), 400

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    name = request.form.get('name')
    message = request.form.get('message')
    phone = request.form.get('phone', '')
    
    if name and message:
        feedback_data = {
            'name': name, 'message': message, 'phone': phone,
            'submitted_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        feedbacks.append(feedback_data)
        print(f"\n💬 New feedback from {name}")
        
        if phone:
            thank_sms = f"Dear {name}, thank you for your valuable feedback! We appreciate your trust in Dr. Yogesh Nagargoje's Dental Hub."
            send_sms(phone, thank_sms)
        
        clinic_sms = f"NEW FEEDBACK! From: {name}, Phone: {phone or 'Not provided'}, Message: {message[:80]}"
        send_sms(CLINIC_NUMBER, clinic_sms)
        
        return jsonify({'success': True, 'message': 'Feedback submitted successfully! Thank you.'})
    
    return jsonify({'success': False, 'message': 'Please provide name and feedback'}), 400

@app.route('/get_feedbacks', methods=['GET'])
def get_feedbacks():
    return jsonify(feedbacks)

@app.route('/get_appointments', methods=['GET'])
def get_appointments():
    return jsonify(appointments)

@app.route('/admin')
def admin():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard - Dental Hub</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 1200px; margin: auto; }}
            h1 {{ color: #1e6f5c; }}
            .stats {{ display: flex; gap: 20px; margin-bottom: 30px; flex-wrap: wrap; }}
            .stat-box {{ background: #1e6f5c; color: white; padding: 20px; border-radius: 10px; text-align: center; flex: 1; }}
            .stat-number {{ font-size: 2rem; font-weight: bold; }}
            .card {{ background: white; border-radius: 10px; padding: 20px; margin-bottom: 30px; overflow-x: auto; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #1e6f5c; color: white; }}
            .back-btn {{ background: #e9a23b; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-btn">← Back to Website</a>
            <h1>🦷 Dental Hub Admin Dashboard</h1>
            <div class="stats">
                <div class="stat-box"><div class="stat-number">{len(appointments)}</div>Appointments</div>
                <div class="stat-box"><div class="stat-number">{len(feedbacks)}</div>Feedbacks</div>
                <div class="stat-box"><div class="stat-number">{CLINIC_NUMBER_DISPLAY}</div>Clinic Number</div>
            </div>
            <div class="card">
                <h2> Appointments</h2>
                <table><thead><tr><th>Name</th><th>Phone</th><th>Date</th><th>Time</th><th>Booked At</th></tr></thead><tbody>
                {''.join(f'<tr><td>{a["name"]}</td><td>{a["phone"]}</td><td>{a["date"]}</td><td>{a["time_slot"]}</td><td>{a["booked_at"]}</td></tr>' for a in appointments)}
                </tbody></table>
            </div>
            <div class="card">
                <h2>💬 Feedbacks</h2>
                <table><thead><tr><th>Name</th><th>Phone</th><th>Message</th><th>Submitted At</th></tr></thead><tbody>
                {''.join(f'<tr><td>{f["name"]}</td><td>{f.get("phone", "N/A")}</td><td>{f["message"]}</td><td>{f["submitted_at"]}</td></tr>' for f in feedbacks)}
                </tbody></table>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=False)
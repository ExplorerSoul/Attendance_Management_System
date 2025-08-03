from flask import Flask, render_template, request, flash
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

@app.route('/')
def index():
    return render_template('index.html', selected_date='', no_data=False, attendance_data=None)

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check if database exists and is accessible
        if os.path.exists('attendance.db'):
            conn = sqlite3.connect('attendance.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            conn.close()
            
            return {
                'status': 'healthy',
                'database': 'connected',
                'tables': table_count,
                'timestamp': datetime.now().isoformat()
            }, 200
        else:
            return {
                'status': 'healthy',
                'database': 'not_initialized',
                'timestamp': datetime.now().isoformat()
            }, 200
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, 500

@app.route('/attendance', methods=['POST'])
def attendance():
    try:
        selected_date = request.form.get('selected_date')
        if not selected_date:
            flash('Please select a date', 'error')
            return render_template('index.html', selected_date='', no_data=False, attendance_data=None)
        
        selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
        formatted_date = selected_date_obj.strftime('%Y-%m-%d')

        # Check if database exists
        if not os.path.exists('attendance.db'):
            return render_template('index.html', selected_date=selected_date, no_data=True, attendance_data=None)

        conn = sqlite3.connect('attendance.db')
        cursor = conn.cursor()

        cursor.execute("SELECT name, time FROM attendance WHERE date = ?", (formatted_date,))
        attendance_data = cursor.fetchall()

        conn.close()

        if not attendance_data:
            return render_template('index.html', selected_date=selected_date, no_data=True, attendance_data=None)
        
        return render_template('index.html', selected_date=selected_date, no_data=False, attendance_data=attendance_data)
    
    except ValueError:
        flash('Invalid date format', 'error')
        return render_template('index.html', selected_date='', no_data=False, attendance_data=None)
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return render_template('index.html', selected_date='', no_data=False, attendance_data=None)

if __name__ == '__main__':
    # For production, use: app.run(host='0.0.0.0', port=5000, debug=False)
    app.run(debug=True, host='0.0.0.0', port=5000)
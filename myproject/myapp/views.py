from django.shortcuts import redirect, render
import mysql.connector as sql
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

@csrf_protect
def registration(request):
    if request.method == "POST":
        # Connect to the database
        conn = sql.connect(host="localhost", user="root", password="Vaishu@04", database="smarthealth")
        cursor = conn.cursor()
        
        # Get the data from the form
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        cpassword = request.POST.get("cpassword")
        print(username, email, password, cpassword)
        
        # Check if password and confirm password match
        if password == cpassword:
            # Insert data into the database without saving cpassword
            cursor.execute("INSERT INTO registration (username, email, password, cpassword) VALUES (%s, %s, %s, %s)", (username, email, password, cpassword))
            conn.commit()
            message = "Registration successful!"
        else:
            # Display an error message if passwords do not match
            message = "Password and confirm password do not match."
        
        # Close the database connection
        cursor.close()
        conn.close()
        
        # Pass the message to the template
        return render(request, 'registration.html', {"message": message})
    
    return render(request, 'registration.html')

def home(request):
    print("User is authenticated:", request.user.is_authenticated)
    print("User username:", request.user.username)
   
    print(request.user.is_authenticated)
    return render(request,'home.html')

from django.contrib.auth import authenticate, login as auth_login  # For user authentication and login
from django.contrib import messages  # For displaying error or success messages

@csrf_protect
def login(request):
    error_message = ""
    
    if request.method == "POST":
        # Connect to the database
        try:
            conn = sql.connect(host="localhost", user="root", password="Vaishu@04", database="smarthealth")
            cursor = conn.cursor()
            
            # Get the data from the form
            username = request.POST.get("username")
            password = request.POST.get("password")
            
            print("Login attempt with username:", username, "and password:", password)  # Debugging print statement
            
            # Retrieve the user data from the database
            query = "SELECT password FROM registration WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            
            if result:
                # If a record is found, check if the password matches
                db_password = result[0]
                print("Password in database:", db_password)  # Debugging print statement
                
                if db_password == password:
                    print("Login successful")  # Debugging print statement
                    # Clear any unread results to avoid errors when closing
                    cursor.fetchall()  # Ensures all results are read
                    return redirect('logout')  # Redirect to home page on successful login
                else:
                    error_message = "Invalid password."
            else:
                error_message = "Username not found."
                
        except sql.Error as e:
            print("Database error:", e)
            error_message = "Database error. Please try again later."
        
        finally:
            # Ensure all results are processed before closing
            cursor.fetchall()  # Clears any remaining results
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    # Pass the error message to the template if login fails
    return render(request, 'login.html', {"error_message": error_message})

from django.http import HttpResponseForbidden

def csrf_failure(request, reason=""):
    return HttpResponseForbidden("Custom CSRF failure message.")

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def healthInsights(request):
    analysis = None

    if request.method == "POST":
        # Get user inputs
        heart_rate = int(request.POST.get("heart_rate", 0))
        oxygen_level = int(request.POST.get("oxygen_level", 0))
        blood_pressure = request.POST.get("blood_pressure", "")
        body_temperature = float(request.POST.get("body_temperature", 0.0))

        # Split blood pressure into systolic and diastolic
        try:
            systolic, diastolic = map(int, blood_pressure.split("/"))
        except ValueError:
            systolic, diastolic = 0, 0

        # Analyze inputs
        analysis = []
        if heart_rate < 60 or heart_rate > 100:
            analysis.append("Heart rate is abnormal. Please consult a doctor.")
        if oxygen_level < 95:
            analysis.append("Oxygen saturation is low. Consider deep breathing or seeking medical attention.")
        if systolic < 90 or systolic > 140 or diastolic < 60 or diastolic > 90:
            analysis.append("Blood pressure is not in the normal range. Monitor it closely.")
        if body_temperature < 36.1 or body_temperature > 37.2:
            analysis.append("Body temperature is abnormal. It could indicate fever or hypothermia.")

        # Join the messages for display
        analysis = " ".join(analysis) if analysis else "All health parameters are within the normal range."

    return render(request, 'healthInsights.html', {'analysis': analysis})

from .models import wellness
from django.db.models import Q

def wellness_view(request):
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        transactions = wellness.objects.filter(
            Q(category__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    else:
        transactions = wellness.objects.all()
 
    # Pass transactions to the template
    return render(request, 'wellness.html', {
        'transactions': transactions,
        'search_query': search_query
    })

from .models import Doctor, Patient, Appointment  # Import the Appointment model
 

def dashboard(request):
    # Get counts for doctors, patients, and appointments
    total_doctors = Doctor.objects.count()
    total_patients = Patient.objects.count()
    total_appointments = Appointment.objects.count()  # Count of appointments
 
    # Fetch recent doctors, patients, and appointments with relevant fields
    recent_doctors = Doctor.objects.all().order_by('-id')[:3]  # Limit to the latest 3 doctors
    recent_patients = Patient.objects.all().order_by('-id')[:3]  # Limit to the latest 3 patients
    # recent_appointments = Appointment.objects.all().order_by('-appointment_date')[:3]  # Latest 3 appointments
    recent_appointments = Appointment.objects.all().order_by('-appointment_date')[:3]  # Latest 3 appointments
 
    # Context to pass to the template
    context = {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'recent_doctors': recent_doctors,
        'recent_patients': recent_patients,
        'recent_appointments': recent_appointments,
    }
 
    return render(request, 'dashboard.html', context)
 

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)  # Clears the user's session
    print("Hi")
    return render(request, 'logout.html')  # Redirect to the home page or any other page


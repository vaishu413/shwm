from django.shortcuts import render
import mysql.connector as sql
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def registration(request):
    if request.method == "POST":
        try:
            # Connect to the database
            conn = sql.connect(host="localhost", user="root", password="Vaishu@04", database="smarthealth")
            cursor = conn.cursor()
            
            # Get the data from the form
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            cpassword = request.POST.get("cpassword")
            print(username, email, password, cpassword)
            # Prepare and execute the SQL query
            comm = "INSERT INTO registration (username, email, password, cpassword) VALUES (%s, %s, %s, %s)"
            cursor.execute(comm, (username, email, password, cpassword))
            conn.commit()

            # Close the database connection
            cursor.close()
            conn.close()
        except sql.Error as e:
            print("Error: {}".format(e))  # Print the error to the console (or log it)
            # Optionally, you can return an error message to the template here

    return render(request, 'registration.html')

def home(request):
    return render(request,'home.html')
 
def login(request):
    return render(request,'login.html')

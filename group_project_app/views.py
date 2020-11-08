from django.shortcuts import render, redirect
from .models import *
# from .forms import NewStudentForm, LogForm
#from django.db.models import Q, Count
# from django.contrib.auth import authenticate, login
from django.contrib import messages
import bcrypt
import random
import math
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.hashers import make_password

def index(request):
    request.session.flush()
    return render(request, "index.html")

# def formplay(request):
#     request.session.flush()
#     context = {
#         'student_list':Student.objects.all(),
#         'form':NewStudentForm(),
#         'logform':LogForm()
#     }
#     return render(request, "formplay.html", context)
# @login_required(login_url='/')

# def success(request):
#     return render(request, "landing_page.html")


def teacher_register(request):
    if request.method =='POST':
        errors = Teacher.objects.reg_validator_teacher(request.POST)
        if len(errors) != 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/new_teacher')
        hashed_pw = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        new_teacher = Teacher.objects.create(title=request.POST['title'], first_name=request.POST['first_name'], last_name=request.POST['last_name'], email=request.POST['email'], password=hashed_pw)
        request.session['teacher_id'] = new_teacher.id
        return redirect('/teacher_dashboard')
    return redirect('/')

def new_teacher(request):
    return render(request, 'new_teacher.html')

def student_register(request):
    if request.method =='POST':
        errors = Student.objects.reg_validator(request.POST)
        if len(errors) != 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/new_student')
        hashed_pw = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        teacher = Teacher.objects.get(id=int(request.POST['teacher']))
        new_student = Student.objects.create(
        first_name=request.POST['first_name'], 
        last_name=request.POST['last_name'], 
        teacher=teacher, 
        email=request.POST['email'], password=hashed_pw)
        request.session['student_id'] = new_student.id
        return redirect('/student_dashboard')
    return redirect('/')

def new_student(request):
    context = {
        'all_teachers': Teacher.objects.all()
    }
    return render(request, 'new_student.html', context)    

def login(request):
    return render(request, 'login.html')

def student_login(request):
    if request.method == 'POST':
        errors = Student.objects.log_validator(request.POST)
        if len(errors) != 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/login')
        this_student = Student.objects.get(email=request.POST['email'])
        request.session['student_id'] = this_student.id
        return redirect('/student_dashboard')        
    return redirect('/')


def teacher_login(request):
    if request.method == 'POST':
        errors = Teacher.objects.log_validator_teacher(request.POST)
        if len(errors) != 0:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect('/login')
        this_teacher = Teacher.objects.get(email=request.POST['email'])
        request.session['teacher_id'] = this_teacher.id
        return redirect('/teacher_dashboard')        
    return redirect('/')

def student_dashboard(request):
    if 'student_id' not in request.session:
        return redirect('/')
    this_student = Student.objects.filter(id=request.session['student_id'])    
    context = {
        'Student': this_student[0],
        
    }
    return render(request, 'student_dashboard.html', context)

def teacher_dashboard(request):
    if 'teacher_id' not in request.session:
        return redirect('/')
    this_teacher = Teacher.objects.filter(id=request.session['teacher_id'])        
    context = {
        'teacher': Teacher.objects.get(id=request.session['teacher_id']),
        'teacher_students': this_teacher[0].students.all(),
    }
    return render(request, 'teacher_dashboard.html', context)            

def logout(request):
    if request.method == 'POST':
        logout(request)
    return redirect('/')

def student_mailbox(request):
    if 'student_id' not in request.session:
        return redirect('/')
    context = {
        'student': Student.objects.get(id=request.session['student_id'])
    }    
    return render(request, 'student_mailbox.html', context)

def teacher_mailbox(request):
    if 'teacher_id' not in request.session:
        return redirect('/')
    context = {
        'teacher': Teacher.objects.get(id=request.session['teacher_id']),
    }    
    return render(request, 'teacher_dashboard.html', context)

def teacher_add_message(request):
    if 'teacher_id' not in request.session:
        return redirect('/')
    if request.method == 'POST':
        errors = Message.objects.mail_validator(request.POST)
        if len(errors) != 0:
            for (key, value) in errors.items():
                messages.error(request, value)
            return redirect('/teacher_new_message')  
        Message.objects.create(
            teacher = Teacher.objects.get(id=request.session['teacher_id']),
            student = Student.objects.get(id=int(request.POST['student'])),
            sender = "teacher",
            subject = request.POST['subject'],
            message_content = request.POST['message_content'],  
        ) 
    return redirect('/teacher_mailbox')       


def teacher_new_message (request):
    if 'teacher_id' not in request.session:
        return redirect('/')
    this_teacher = Teacher.objects.filter(id=request.session['teacher_id'])
    context = {
        'teacher_students': this_teacher[0].students.all(),
    } 
    return render(request, 'teacher_new_message.html', context)

def student_add_message(request):
    if 'student_id' not in request.session:
        return redirect('/')
    if request.method == 'POST':
        errors = Message.objects.mail_validator(request.POST)
        if len(errors) != 0:
            for (key, value) in errors.items():
                messages.error(request, value)
            return redirect('/student_new_message')    
        Message.objects.create(
            teacher = Teacher.objects.get(id=int(request.POST['teacher'])),
            student = Student.objects.get(id=request.session['student_id']),
            sender = "student",
            subject = request.POST['subject'],
            message_content = request.POST['message_content'],  
        ) 
    return redirect('/student_mailbox')       


def student_new_message (request):
    if 'student_id' not in request.session:
        return redirect('/')  
    context = {
        'student': Student.objects.get(id=request.session['student_id'])
    } 
    return render(request, 'student_new_message.html', context)

def student_delete(request, msg_id):
    to_delete = Message.objects.get(id=msg_id)
    to_delete.delete()
    return redirect('/student_mailbox')

def teacher_delete(request, msg_id):
    to_delete = Message.objects.get(id=msg_id)
    to_delete.delete()
    return redirect('/teacher_mailbox')

def student_sent(request):
    if 'student_id' not in request.session:
        return redirect('/')
    context = {
        'student': Student.objects.get(id=request.session['student_id'])
    }    
    return render(request, 'student_sent_messages.html', context)

def teacher_sent(request):
    if 'teacher_id' not in request.session:
        return redirect('/')
    context = {
        'teacher': Teacher.objects.get(id=request.session['teacher_id'])
    }    
    return render(request, 'teacher_sent_messages.html', context)


def problem_solve(request):
    if 'student_id' not in request.session:
        return redirect('/')
    if request.method == "GET":
        context = {
            "divisor":random.randrange(1,101),
            "dividend":random.randrange(100, 1001)
        }
        return render(request, "problem_solve.html", context)
    #if request.method == "POST":
     #   return('/problem_solve')        
    if request.method == 'POST':
        # step 1 is to create the solution for the problem object. Needs to have the following:
        # round down (dividend/divisor) + "R" + (dividend%divisor)
        # step 2 is to create student solution based on the request.POST inputs
        # step 3 is to compare them
        # step 4 is to make the problem object
        # step 5 (temp) -> terminal show if solution is correct for previous problem (move to template)
        solution_quotient = math.floor(int(request.POST['dividend'])/int(request.POST['divisor']))
        solution_remainder = int(request.POST['dividend'])%int(request.POST['divisor'])
        solution = f'{solution_quotient}R{solution_remainder}'
        answer = f'{request.POST["quotient"]}R{request.POST["remainder"]}'
        correct = False
        if(solution == answer):
            correct = True
        elif(solution != answer):
            correct = False
        request.session['is_correct'] = correct
        errors = Problem.objects.problem_validator(request.session['is_correct'])
        if len(errors) != 0:
            for (key, value) in errors.items():
                messages.error(request, value)
            return redirect('/problem_solve')    
        Problem.objects.create(
            student = Student.objects.get(id=request.session["student_id"]),
            divisor=int(request.POST['divisor']),
            dividend=int(request.POST['dividend']),
            solution=solution,
            student_answer=answer,
            is_correct=correct
            )
        problem = Problem.objects.last()
        print(problem.solution)
        print(problem.student_answer)
        print(problem.is_correct)
    return redirect('/problem_solve')

def who_we_are(request):
    return render(request, 'who_we_are.html')

def our_method(request):
    return render(request, 'our_method.html')

def testimonials(request):
    return render(request, 'testimonials.html')


def contact_us(request):
    return render(request, 'contact_us.html')    
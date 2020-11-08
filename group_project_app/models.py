from django.db import models
import re
email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
import bcrypt
#from rest_framework import serializers

class StudentManager(models.Manager):
    def reg_validator(self, postData):
        errors = {}
        if len(postData['first_name']) == 0:
            errors['first_name'] = "First name is required"
        elif len(postData['first_name']) < 2 or postData['first_name'].isalpha() != True:
            errors['first_name'] = "First name must be at least 2 letters long, letters only"
        if len(postData['last_name']) == 0:
            errors['last_name'] = "Last name is required"
        elif len(postData['last_name']) < 2 or postData['last_name'].isalpha() != True:
            errors['first_name'] = "Last name must be at least 2 letters long, letters only"
        if len(postData['email']) == 0:
            errors['email'] = "Email is required"
        elif not email_regex.match(postData['email']):          
            errors['email'] = ("Invalid email format")
        existing_student = Student.objects.filter(email=postData['email'])
        if len(existing_student) > 0:
            errors['email'] = "Email already in use"   
        if len(postData['password']) == 0:
            errors['password'] = "Password is required"
        elif len(postData['password']) < 8:
            errors['password'] = "Password must be at least 8 characters long"
        elif postData['password'] != postData['confirm_pw']:
            errors['password'] = "Password and Confirm Password inputs must match"
        return errors        

    def log_validator(self, postData):
        errors = {}
        if len(postData['email']) == 0:
            errors['email'] = "Email is required"
        elif not email_regex.match(postData['email']):          
            errors['email'] = ("Invalid email format")
        existing_student = Student.objects.filter(email=postData['email'])
        if len(existing_student) != 1:
            errors['email'] = "Student not found"    
        if len(postData['password']) == 0:
            errors['password'] = "Password is required"
        elif len(postData['password']) < 8:
            errors['password'] = "Password must be at least 8 characters long"
        elif bcrypt.checkpw(postData['password'].encode(), existing_student[0].password.encode()) != True:
            errors['email'] = "Email and Password do not match"
        return errors

class TeacherManager(models.Manager):
    def reg_validator_teacher(self, postData):
        errors = {}   
        if len(postData['first_name']) == 0:
            errors['first_name'] = "First name is required"
        elif len(postData['first_name']) < 2 or postData['first_name'].isalpha() != True:
            errors['first_name'] = "First name must be at least 2 letters long, letters only"
        if len(postData['last_name']) == 0:
            errors['last_name'] = "Last name is required"
        elif len(postData['last_name']) < 2 or postData['last_name'].isalpha() != True:
            errors['first_name'] = "Last name must be at least 2 letters long, letters only"
        if len(postData['email']) == 0:
            errors['email'] = "Email is required"
        elif not email_regex.match(postData['email']):          
            errors['email'] = ("Invalid email format")
        existing_teacher = Teacher.objects.filter(email=postData['email'])
        if len(existing_teacher) > 0:
            errors['email'] = "Email already in use"   
        if len(postData['password']) == 0:
            errors['password'] = "Password is required"
        elif len(postData['password']) < 8:
            errors['password'] = "Password must be at least 8 characters long"
        elif postData['password'] != postData['confirm_pw']:
            errors['password'] = "Password and Confirm Password inputs must match"
        return errors        

    def log_validator_teacher(self, postData):
        errors = {}
        if len(postData['email']) == 0:
            errors['email'] = "Email is required"
        elif not email_regex.match(postData['email']):          
            errors['email'] = ("Invalid email format")
        existing_teacher = Teacher.objects.filter(email=postData['email'])
        if len(existing_teacher) == 0:
            errors['email'] = "Teacher not found"    
        elif len(postData['password']) == 0:
            errors['password'] = "Password is required"
        elif len(postData['password']) < 8:
            errors['password'] = "Password must be at least 8 characters long"
        elif bcrypt.checkpw(postData['password'].encode(), existing_teacher[0].password.encode()) != True:
            errors['email'] = "Email and Password do not match"
        return errors

class MessageManager(models.Manager):
    def mail_validator(self, postData):
        errors = {}
        if len(postData['subject']) == 0:
            errors['subject'] = "Subject cannot be left blank"
        if len(postData['message_content']) == 0:
            errors['message_content'] = "Message cannot be left blank"    
        return errors 

class ProblemManager(models.Manager):
    def problem_validator(self, answer):
        errors = {}
        if answer == False:
            errors["is_correct"] = "Try Again!"
        else:
            errors["is_correct"] = "Hooray, go to next problem!"
        return errors 

class Teacher(models.Model):
    title = title = models.CharField(max_length=60)
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = TeacherManager()

class Student(models.Model):
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    email = models.EmailField(max_length=60)
    password = models.CharField(max_length=255)
    teacher = models.ForeignKey(Teacher, related_name='students', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = StudentManager()

class Message(models.Model):
    teacher = models.ForeignKey(Teacher, related_name="teacher_message", on_delete=models.CASCADE)
    student = models.ForeignKey(Student, related_name="student_message", on_delete=models.CASCADE)
    sender = models.CharField(max_length=9)
    subject = models.CharField(max_length=255)
    message_content = models.TextField(null = True)
    unread = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = MessageManager()

class Problem(models.Model):
    student = models.ForeignKey(Student, related_name="student_problems", on_delete=models.CASCADE)
    divisor = models.IntegerField()
    dividend = models.IntegerField()
    solution = models.CharField(max_length=7)
    student_answer = models.CharField(max_length=7)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = ProblemManager()

import csv
from io import StringIO
from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .forms import CSVUploadForm
from django.urls import reverse
from collections import defaultdict
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

@login_required
def process_csv(request):
    if request.method == 'POST':
        selected_template = request.POST.get('template')
        csv_content = request.session.get('csv_data')
        if not csv_content or not selected_template:
            return redirect('upload_csv')
        csv_data = parse_csv(csv_content)
        if selected_template == 'template1':
            pdf_content = handle_template1(csv_data)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="generated_pdf.pdf"'
            response.write(pdf_content)
            return response
    else:
        return redirect(reverse('upload_csv'))
    
def handle_template1(csv_data):
    grouped_data = defaultdict(list)
    for row in csv_data:
        student_id = row.get('student_id')
        grouped_data[student_id].append(row)

    pdf_files = []
    for student_id, items in grouped_data.items():
        pdf_content = cwf_template_1(items)
        filename = f"{student_id}_coursework_feedback.pdf"
        pdf_files.append((filename, pdf_content))

    return pdf_files

def cwf_template_1(items):
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    heading4_style = styles['Heading4']
    elements = []

    if items:
        student_name = items[0].get('student_name', 'Unnamed Student')
        student_id = items[0].get('student_id', 'Unknown ID')

        

        elements.append(Paragraph(f'{student_name} Coursework Feedback', styles['Title']))
        elements.append(Spacer(12, 12))
        student_details_data = [[Paragraph(f'Student Name: {student_name}', heading4_style),
                                 Spacer(100,0),
                                 Paragraph(f'Student ID: {student_id}', heading4_style)]]
        student_details_table = Table(student_details_data)
        student_details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(student_details_table)
        elements.append(Spacer(1, 12))
        elements.append(Spacer(1, 12))

    table_data = [['Item No', 'Requirements', 'Marks Available', 'Your Mark', 'Comments']]
    
    
    for item in items:
        item_data = [
            Paragraph(item.get('item_no', ''), styles['Normal']),
            Paragraph(item.get('requirements', ''), styles['Normal']),
            Paragraph(item.get('marks_available', ''), styles['Normal']),
            Paragraph(item.get('your_mark', ''), styles['Normal']),
            Paragraph(item.get('comments', ''), styles['Normal']),
        ]
        table_data.append(item_data)

    col_widths = [None, None, 80, 80, 120]

    table = Table(table_data, colWidths=col_widths)

    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))

    elements.append(table)
    additional_comments = items[0].get('additional_comments', 'No additional comments provided.')
    elements.append(Paragraph("Additional Comments:", styles['Heading4']))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(additional_comments, styles['Normal']))


    pdf.build(elements)
    buffer.seek(0)
    pdf_data = buffer.getvalue()
    buffer.close()

    return pdf_data


@login_required
def template_choices(request):
    page = loader.get_template("pdfinstant/template_choices.html")
    return HttpResponse(page.render(request=request))


@csrf_exempt
def upload_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            dataset = csv_file.read().decode('UTF-8')
            request.session['csv_data'] = dataset
            return redirect('template_choices')
    else:
        form = CSVUploadForm()
    return render(request, 'csv_upload.html', {'form': form})

def parse_csv(csv_content):
    csv_data = []
    f = StringIO(csv_content)
    reader = csv.DictReader(f)
    for row in reader:
        cleaned_row = {key.lstrip('\ufeff').replace(' ', '_').strip(): value for key, value in row.items()}
        csv_data.append(cleaned_row)
    return csv_data

def index(request):
    page = loader.get_template("pdfinstant/index.html")
    return HttpResponse(page.render(request=request))

def homepage(request):
    page = loader.get_template("pdfinstant/homepage.html")
    return HttpResponse(page.render(request=request))


def aboutpage(request):
    page = loader.get_template("pdfinstant/aboutpage.html")
    return HttpResponse(page.render(request=request))

def generatepdfs(request):
    page = loader.get_template("pdfinstant/generatepdfs.html")
    return HttpResponse(page.render(request=request))

@login_required
def generatepdfsin(request):
    page = loader.get_template("pdfinstant/generatepdfsin.html")
    return HttpResponse(page.render(request=request))

def signin(request):
    page = loader.get_template("pdfinstant/signin.html")
    return HttpResponse(page.render(request=request))

def signup(request):
    page = loader.get_template("pdfinstant/signup.html")
    return HttpResponse(page.render(request=request))

def createaccount(request):
    error_message_context = {'alert': False, 'message': ''}

    if request.method == 'POST':
        useremail = request.POST.get('useremail')
        userpassword = request.POST.get('userpassword')
        userconfirmpassword = request.POST.get('userconfirmpassword')

        if userpassword != userconfirmpassword:
            error_message_context['alert'] = True
            error_message_context['message'] = 'The Passwords you have entered do not match'
            return render(request, 'pdfinstant/signup.html', error_message_context)

        if User.objects.filter(email=useremail).exists():
            error_message_context['alert'] = True
            error_message_context['message'] = 'The Email you have entered is already registered'
            return render(request, 'pdfinstant/signup.html', error_message_context)

        userpassword_secure = make_password(userpassword)
        create_new_account = User(username=useremail, email=useremail, password=userpassword_secure)
        create_new_account.save()
        return redirect('signin')

    return render(request, 'pdfinstant/signup.html', error_message_context)



def signinaccount(request):
    error_message_context = {'alert': False, 'message': ''}

    if request.method == 'POST':
        useremail = request.POST.get('useremail')
        userpassword = request.POST.get('userpassword')
        user = authenticate(request, username=useremail, password=userpassword)

        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            error_message_context['alert'] = True
            error_message_context['message'] = 'Incorrect sign in details have been provided'
            return render(request, 'pdfinstant/signin.html', error_message_context)

    return render(request, 'pdfinstant/signin.html', error_message_context)

@login_required
def signout(request):
    logout(request)
    return redirect('signin') 

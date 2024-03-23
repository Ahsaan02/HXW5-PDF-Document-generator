from django.shortcuts import get_object_or_404, render, redirect
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from .forms import CSVUploadForm
import csv
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import zipfile
from django.urls import reverse
from io import StringIO
from collections import defaultdict
from django.core.mail import EmailMessage
from django.conf import settings
from .models import ZipFile


def send_test_email(subject, body, recipient_email, pdf_content, custom_filename):
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.EMAIL_HOST_USER,
        to=[recipient_email]
    )
    email.attach(custom_filename, pdf_content, 'application/pdf')
    email.send()




def upload_csv(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            dataset = csv_file.read().decode('UTF-8')
            request.session['csv_data'] = dataset 
            return redirect(reverse('template_choices'))
    else:
        form = CSVUploadForm()
    return render(request, 'csv_upload.html', {'form': form})


def process_csv(request):
    if request.method == 'POST':
        selected_template = request.POST.get('template')
        action = request.POST.get('action', 'downloadZip')
        csv_content = request.session.get('csv_data')

        if not csv_content or not selected_template:
            return redirect('upload_csv')

        csv_data = parse_csv(csv_content)

        pdf_files = []
        email_subject = ""
        email_body = ""

        if selected_template == 'template1':
            pdf_files = handle_template1(csv_data)
            template_type = 'coursework_feedback'
            email_subject = "Your Coursework Feedback"
            email_body = "Here is your coursework feedback. Please review it carefully."
        elif selected_template == 'template2':
            pdf_files = handle_template2(csv_data)
            template_type = 'receipt'
            email_subject = "Your Receipt"
            email_body = "Attached is your receipt. Thank you for your business."
        elif selected_template == 'template3':
            pdf_files = handle_template3(csv_data)
            template_type = 'business_letter'
            email_subject = "Business Letter"
            email_body = "Please find the attached business letter. We look forward to your response."

        if action == 'emailPdfs':
            for filename, pdf_content, recipient_email in pdf_files:
                custom_filename = filename
                send_test_email(
                    email_subject,
                    email_body,
                    recipient_email,
                    pdf_content,
                    custom_filename
                )
            return HttpResponse("Emails sent successfully.")
        else:
            return generate_zip(request, pdf_files, template_type)

    else:
        return redirect(reverse('upload_csv'))


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

def handle_template1(csv_data):
    grouped_data = defaultdict(list)
    for row in csv_data:
        student_id = row.get('student_id')
        grouped_data[student_id].append(row)

    pdf_files = []
    for student_id, items in grouped_data.items():
        recipient_email = items[0].get('email')
        pdf_content = cwf_template_1(items)
        filename = f"{student_id}_coursework_feedback.pdf"
        pdf_files.append((filename, pdf_content, recipient_email))

    return pdf_files


def handle_template2(csv_data):
    grouped_data = defaultdict(list)
    for row in csv_data:
        customer_id = row['Customer ID']
        grouped_data[customer_id].append(row)

    pdf_files = []
    for customer_id, items in grouped_data.items():
        recipient_email = items[0].get('email')
        pdf_content = receipt_template_2(customer_id, items)
        filename = f"{customer_id}_receipt.pdf"
        pdf_files.append((filename, pdf_content, recipient_email))

    return pdf_files


def handle_template3(csv_data):
    pdf_files = []
    for row in csv_data:
        recipient_email = row.get('email', 'Unknown')

        pdf_content = business_letter_template(row)
        
        filename = f"business_letter_to_{recipient_email}.pdf"
        pdf_files.append((filename, pdf_content, recipient_email))

    return pdf_files


def generate_zip(request, pdf_files, template_type):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, pdf_content, _ in pdf_files: 
            zip_file.writestr(filename, pdf_content)

    zip_filename = "download.zip"
    if template_type == 'coursework_feedback':
        zip_filename = "coursework_feedback_reports.zip"
    elif template_type == 'receipt':
        zip_filename = "receipts.zip"
    elif template_type == 'business_letter':
        zip_filename = "business_letters.zip"

    
    ZipFile.objects.create(
        user=request.user,
        file_name=zip_filename,
        file_content=zip_buffer.getvalue()
    )


    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
    zip_buffer.close()
    return response


def parse_csv(csv_content):
    csv_data = []
    f = StringIO(csv_content)
    print(csv_content)
    reader = csv.DictReader(f)
    for row in reader:
        cleaned_row = {key.lstrip('\ufeff'): value for key, value in row.items()}
        csv_data.append(cleaned_row)
    return csv_data


def receipt_template_2(customer_id, items):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    style = styles['Normal']

    elements = []

    first_item = items[0]
    customer_info_data = [
        [Paragraph('Customer Name', style), Paragraph(first_item['Customer Name'], style)],
        [Paragraph('Customer ID', style), Paragraph(customer_id, style)],
    ]
    business_info_data = [
        [Paragraph('Business Name', style), Paragraph('Your Business Name', style)],
        [Paragraph('Business Address', style), Paragraph('Your Business Address', style)],
        [Paragraph('Contact Info', style), Paragraph('Your Contact Info', style)],
    ]

    table_style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.beige),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('WORDWRAP', (0, 0), (-1, -1), True),
    ])

    customer_info_table = Table(customer_info_data, colWidths=[80, 100])
    business_info_table = Table(business_info_data, colWidths=[80, 100])

    customer_info_table.setStyle(table_style)
    business_info_table.setStyle(table_style)

    space_between_tables = 195

    info_table_data = [[ customer_info_table, Spacer(12, 12), business_info_table]]
    info_table = Table(info_table_data, colWidths=[space_between_tables])
    elements.append(info_table)
    elements.append(Spacer(1, 12))

    description_headers = [
    Paragraph('Item Description', style),
    Paragraph('Price', style),
    Paragraph('Quantity', style),
    Paragraph('VAT %', style),
    Paragraph('VAT Amount', style),
    Paragraph('Total', style)
    ]
    description_data = [description_headers] + [[
        Paragraph(item['Item Description'], style), item['Item Price'], item['Item Quantity'], 
        item['VAT Rate'], item['VAT Amount'], item['Item Total']
    ] for item in items]

    total_amount = sum(float(item['Item Total']) for item in items)

    total_summary = [
        '', '', '', '', Paragraph('Total Amount:', style), f"${total_amount:.2f}"
    ]
    description_data.append(total_summary)

    description_table = Table(description_data, colWidths=[150, 50, 50, 50, 50, 50])
    description_table.setStyle(table_style)
    elements.append(Spacer(1,60))
    elements.append(description_table)

    elements.append(Spacer(1,60))
    thank_you = Paragraph("Your payment has been received, thanks!", styles['Normal'])
    elements.append(thank_you)
    elements.append(Spacer(1, 35))  


    payment_method_data = [
        [Paragraph("Payment method:", styles['Normal']), Paragraph(first_item.get('Payment Method', ''), styles['Normal'])]
    ]
    payment_method_table = Table(payment_method_data, colWidths=[100, 80]) 
    table_style_payment = TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, 0), colors.beige),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('WORDWRAP', (0, 0), (-1, -1), True),
    ])
    payment_method_table.setStyle(table_style_payment)

    elements.append(ListFlowable([ListItem(payment_method_table, leftIndent=0)], bulletType='bullet'))



    

    doc.build(elements)
    pdf_data = buffer.getvalue()
    buffer.close()

    return pdf_data


def business_letter_template(csv_row):
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph(csv_row['SenderName'], styles['Normal']))
    elements.append(Paragraph(csv_row['SenderAddress'], styles['Normal']))
    elements.append(Paragraph(csv_row['SenderCityZip'], styles['Normal']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(csv_row['TodayDate'], styles['Normal']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(csv_row['RecipientName'], styles['Normal']))
    elements.append(Paragraph(csv_row['RecipientTitle'], styles['Normal']))
    elements.append(Paragraph(csv_row['RecipientCompany'], styles['Normal']))
    elements.append(Paragraph(csv_row['RecipientAddress'], styles['Normal']))
    elements.append(Paragraph(csv_row['RecipientCityZip'], styles['Normal']))
    elements.append(Spacer(1, 30))

    elements.append(Paragraph(f"Dear {csv_row['RecipientName']},", styles['Normal']))
    elements.append(Spacer(1, 30))

    elements.append(Paragraph(csv_row['Introduction'], styles['Normal']))
    elements.append(Paragraph(csv_row['Body'], styles['Normal']))
    elements.append(Spacer(1, 30))

    elements.append(Paragraph(csv_row['Closing'], styles['Normal']))
    elements.append(Spacer(1, 30))

    elements.append(Paragraph("Sincerely,", styles['Normal']))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(csv_row['SenderName'], styles['Normal']))
    if 'SenderTitle' in csv_row:
        elements.append(Paragraph(csv_row['SenderTitle'], styles['Normal']))

    pdf.build(elements)
    buffer.seek(0)
    pdf_data = buffer.getvalue()
    buffer.close()

    return pdf_data

@login_required
def template_choices(request):
    page = loader.get_template("pdfinstant/template_choices.html")
    return HttpResponse(page.render(request=request))

def index(request):
    page = loader.get_template("pdfinstant/homepage.html")
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

@login_required
def acprofile(request):
    zip_files = ZipFile.objects.filter(user=request.user)
    return render(request, 'pdfinstant/acprofile.html', {'zip_files': zip_files})


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

from django.shortcuts import render, redirect
from .models import Menu, Booking
from django.core import serializers
from .forms import BookingForm, MenuForm
from datetime import datetime
from django.http import JsonResponse
import json

def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def book(request):
    # Check if it's an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Get the date from the request if it exists, otherwise use today's date
    date_str = request.GET.get('date')
    
    # Convert string date to datetime object if provided
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            date = datetime.today().date()
    else:
        date = datetime.today().date()
    
    # Handle POST request (form submission)
    if request.method == 'POST':
        if is_ajax:
            # Handle AJAX form submission
            try:
                data = {}
                data['first_name'] = request.POST.get('first_name')
                data['reservation_date'] = request.POST.get('reservation_date')
                data['reservation_slot'] = request.POST.get('reservation_slot')
                
                form = BookingForm(data)
                if form.is_valid():
                    form.save()
                    return JsonResponse({'status': 'success'})
                else:
                    return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        else:
            # Handle regular form submission
            form = BookingForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('bookings')
    
    # Get all bookings for the selected date
    bookings_on_date = Booking.objects.filter(reservation_date=date).order_by('reservation_slot')
    booked_slots = bookings_on_date.values_list('reservation_slot', flat=True)
    
    # Determine available hours based on day of week
    weekday = date.weekday()  # 0=Monday, 1=Tuesday, ..., 6=Sunday
    
    # Set opening hours based on day of week
    # Mon-Fri: 2pm - 10pm (14:00 - 22:00)
    # Sat: 2pm - 11pm (14:00 - 23:00)
    # Sun: 2pm - 9pm (14:00 - 21:00)
    if weekday < 5:  # Monday to Friday
        opening_hour = 14  # 2pm
        closing_hour = 22  # 10pm
        hours_display = "Monday to Friday: 2pm - 10pm"
    elif weekday == 5:  # Saturday
        opening_hour = 14  # 2pm
        closing_hour = 23  # 11pm
        hours_display = "Saturday: 2pm - 11pm"
    else:  # Sunday
        opening_hour = 14  # 2pm
        closing_hour = 21  # 9pm
        hours_display = "Sunday: 2pm - 9pm"
    
    # Create a list of available hours based on opening hours and already booked slots
    available_slots = [(i, f"{i}:00 Hours") for i in range(opening_hour, closing_hour + 1) 
                      if i not in booked_slots]
    
    # Create form with available slots
    form = BookingForm(available_slots=available_slots)
    # Set initial date value to the selected date
    form.fields['reservation_date'].initial = date
    
    # For AJAX requests asking for JSON format
    if is_ajax and request.GET.get('format') == 'json':
        # Format date for display
        date_display = date.strftime('%A, %B %d, %Y')
        
        # Format bookings for JSON response
        bookings_data = []
        for booking in bookings_on_date:
            bookings_data.append({
                'first_name': booking.first_name,
                'reservation_slot': booking.reservation_slot
            })
        
        # Return JSON response
        return JsonResponse({
            'date_display': date_display,
            'hours_display': hours_display,
            'available_slots': available_slots,
            'bookings': bookings_data
        })
    
    # For regular requests, render template
    context = {
        'form': form,
        'selected_date': date,
        'bookings_on_date': bookings_on_date,
        'hours_display': hours_display
    }
    return render(request, 'book.html', context)

def bookings(request):
    # Check if it's an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Get date parameter from the request
    date_str = request.GET.get('date')
    
    # Filter bookings by date if date parameter is provided
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            bookings = Booking.objects.filter(reservation_date=date)
            
            # If no bookings found for this date
            if not bookings.exists():
                message = f"No bookings found for date: {date_str}"
                
                # For AJAX requests, return JSON
                if is_ajax:
                    return JsonResponse({
                        'bookings': [],
                        'message': message
                    })
                # For regular requests, render template
                return render(request, 'bookings.html', {'bookings': '[]', 'message': message})
                
        except ValueError:
            # Handle invalid date format
            bookings = Booking.objects.all()
            message = f"Invalid date format: {date_str}. Please use /bookings/?date = YYYY-MM-DD format."
            
            # For AJAX requests, return JSON
            if is_ajax:
                return JsonResponse({
                    'bookings': json.loads(serializers.serialize('json', bookings)),
                    'message': message
                })
            # For regular requests, render template with formatted JSON
            bookings_json = json.dumps(json.loads(serializers.serialize('json', bookings)), indent=2)
            return render(request, 'bookings.html', {
                'bookings': bookings_json,
                'message': message
            })
    else:
        # Return all bookings if no date is specified
        bookings = Booking.objects.all()
        
        # If no bookings at all
        if not bookings.exists():
            message = "No bookings found in the system."
            
            # For AJAX requests, return JSON
            if is_ajax:
                return JsonResponse({
                    'bookings': [],
                    'message': message
                })
            # For regular requests, render template
            return render(request, 'bookings.html', {'bookings': '[]', 'message': message})
    
    # Serialize bookings to JSON
    bookings_data = json.loads(serializers.serialize('json', bookings))
    
    # For AJAX requests, return JSON
    if is_ajax:
        return JsonResponse({
            'bookings': bookings_data
        })
    
    # For regular requests, render template with nicely formatted JSON
    formatted_json = json.dumps(bookings_data, indent=2)
    return render(request, 'bookings.html', {'bookings': formatted_json})

def menu(request):
    # Check if it's an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    menu_data = Menu.objects.all()
    
    # Handle form submission for adding a new menu item
    if request.method == 'POST':
        form = MenuForm(request.POST)
        if form.is_valid():
            form.save()
            
            # For AJAX requests, return success response
            if is_ajax:
                return JsonResponse({'status': 'success'})
            
            # For regular requests, redirect to menu page
            return redirect('menu')
        else:
            # For AJAX requests, return error response with form errors
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': 'Invalid form data', 'errors': form.errors}, status=400)
    
    # For AJAX GET requests, return menu data as JSON
    if request.method == 'GET' and is_ajax:
        menu_json = []
        for item in menu_data:
            menu_json.append({
                'id': item.id,
                'name': item.name,
                'price': item.price,
                'menu_item_description': item.menu_item_description
            })
        return JsonResponse({'menu': menu_json})
    
    # For regular requests, render template
    form = MenuForm()
    context = {
        "menu": {"menu": menu_data},
        "form": form
    }
    return render(request, 'menu.html', context)

def display_menu_item(request, pk=None): 
    if pk: 
        menu_item = Menu.objects.get(pk=pk) 
    else: 
        menu_item = "" 
    return render(request, 'menu_item.html', {"menu_item": menu_item})
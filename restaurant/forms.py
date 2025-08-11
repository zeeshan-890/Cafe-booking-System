from django import forms
from .models import Booking, Menu
from datetime import datetime

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = "__all__"
        widgets = {
            'reservation_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        available_slots = kwargs.pop('available_slots', None)
        super(BookingForm, self).__init__(*args, **kwargs)
        
        if available_slots:
            self.fields['reservation_slot'] = forms.ChoiceField(
                choices=available_slots,
                widget=forms.Select(attrs={'class': 'form-control'})
            )

class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['name', 'price', 'menu_item_description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'menu_item_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
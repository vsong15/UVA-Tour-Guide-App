from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['location', 'rating', 'comments']
        widgets = {
            'location': forms.TextInput(attrs={'id': 'location-field'}),
            'rating': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
        }
from django import forms
from .models import Prediction

class PredictionForm(forms.ModelForm):
    class Meta:
        model = Prediction
        fields = ['predicted_home_team_score', 'predicted_away_team_score', 'golden_goal']
        widgets = {
            'predicted_home_team_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'predicted_away_team_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'golden_goal': forms.NumberInput(attrs={'class': 'form-control'}),
        }

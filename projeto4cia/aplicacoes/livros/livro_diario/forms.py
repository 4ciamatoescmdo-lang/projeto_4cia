from django import forms
from django.core.exceptions import ValidationError
from .models import LivroDiarioRelatorio


class LivroDiarioForm(forms.ModelForm):
    class Meta:
        model = LivroDiarioRelatorio
        fields = ['data_escala', 'conteudo', 'permanencia_id', 'policial_substituto_id', 'texto_passagem']
        widgets = {
            'data_escala': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'conteudo': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'permanencia_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'policial_substituto_id': forms.NumberInput(attrs={'class': 'form-control'}),
            'texto_passagem': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.finalizado:
            for field in self.fields.values():
                field.disabled = True

    def clean(self):
        cleaned_data = super().clean()
        if self.instance and self.instance.pk and self.instance.finalizado:
            raise ValidationError("Relatório finalizado não pode ser alterado.")
        return cleaned_data
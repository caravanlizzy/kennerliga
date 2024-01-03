from django.forms import ModelForm

from match_result.models import MatchResult


class CreateResultForm(ModelForm):
    class Meta:
        model = MatchResult
        fields = '__all__'


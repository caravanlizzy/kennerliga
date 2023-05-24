from betterforms.multiform import MultiForm
from django.forms import Form, CharField, TextInput, formset_factory


class GameOptionChoiceForm(Form):
    option = CharField(
        max_length=188,
        widget=TextInput(attrs={'class': 'form-control p-2 mt-2', 'placeholder': 'Name der Auswahloption'})
    )


class GameOptionForm(Form):
    name = CharField(
        max_length=188,
        widget=TextInput(attrs={'class': 'form-control p-2 mt-2', 'placeholder': 'Name der Spieleinstellung'})
    )


class GameSettingsForm(MultiForm):
    form_classes = {
        'category': GameOptionForm,
        'options': formset_factory(GameOptionChoiceForm),
    }

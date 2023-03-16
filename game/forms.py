from django.forms import Form, CharField, TextInput


class NewOptionForm(Form):
    option = CharField(
        max_length=188,
        widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Name der Auswahloption'})
    )

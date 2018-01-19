from django.forms.widgets import SelectDateWidget


class CustomSelectDateWidget(SelectDateWidget):
    template_name = 'userprofile/select_date.html'

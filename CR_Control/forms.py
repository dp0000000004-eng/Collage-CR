from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from .models import Students, Branch, Subject


class StudentForm(forms.ModelForm):
    class Meta:
        model = Students
        fields = '__all__'


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name', 'code', 'semester']


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['code', 'name', 'branch', 'semester']


class UsernameChangeForm(forms.Form):
    new_username = forms.CharField(
        max_length=150,
        label="New username",
        widget=forms.TextInput(attrs={"placeholder": "e.g. deba_cr", "autocomplete": "username"}),
    )
    current_password = forms.CharField(
        label="Current password",
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm with your password", "autocomplete": "current-password"}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["new_username"].initial = user.username

    def clean_new_username(self):
        username = self.cleaned_data["new_username"].strip()
        if not username:
            raise forms.ValidationError("Username cannot be empty.")
        if User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_current_password(self):
        password = self.cleaned_data.get("current_password")
        if not self.user.check_password(password):
            raise forms.ValidationError("Current password is incorrect.")
        return password

    def save(self):
        self.user.username = self.cleaned_data["new_username"]
        self.user.save(update_fields=["username"])
        return self.user


class StyledPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "old_password": "Your current password",
            "new_password1": "At least 8 characters",
            "new_password2": "Repeat new password",
        }
        for name, field in self.fields.items():
            field.widget.attrs.update({
                "placeholder": placeholders.get(name, ""),
                "autocomplete": "new-password" if name != "old_password" else "current-password",
            })
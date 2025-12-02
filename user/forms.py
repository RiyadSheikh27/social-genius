from django import forms
from user.models import Users

class UserAdminForm(forms.ModelForm):
    new_password = forms.CharField(
        required=False,
        label="Reset password",
        widget=forms.PasswordInput(attrs={
            "class": "w-1/2 rounded-xl border border-gray-300 bg-white px-4 py-2 text-sm "
                    "focus:border-blue-600 focus:ring-4 focus:ring-blue-100 transition"
                })
            )

    class Meta:
        model = Users
        fields = '__all__'

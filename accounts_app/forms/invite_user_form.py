from django import forms


class InviteUserForm(forms.Form):
    email = forms.EmailField(max_length=65, required=True, widget=forms.TextInput(
            attrs={
                'class': 'py-3 px-4 block w-full border-gray-200 rounded-lg text-sm focus:border-primary focus:ring-primary-500 disabled:opacity-50 disabled:pointer-events-none',
                'placeholder': 'test@gmail.com',
                'required': 'required',
            }
        ))
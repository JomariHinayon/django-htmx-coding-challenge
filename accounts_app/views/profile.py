import json
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse


from accounts_app.forms import EditUserForm, InviteUserForm


class ProfileView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, "accounts_app/profile.html", {"form": EditUserForm(instance=request.user), "invite_user_form": InviteUserForm() })
    
    def post(self, request, *args, **kwargs):
        form = EditUserForm(request.POST, instance=request.user)
        invite_user_form = InviteUserForm()

        if form.is_valid():
            form.save()
            updated_full_name = form.cleaned_data.get("full_name", request.user.full_name)  # Get the updated full name

            # Prepare the response data
            response_data = {
                'success': True,
                'message': 'Profile updated successfully!',
                'user':  {
                    'full_name': form.cleaned_data.get("full_name", request.user.full_name),  # Use the full name from the form
                    'email': request.user.email,  # Include email if needed
                }
            }
            response = JsonResponse(response_data)
            response['HX-Trigger'] = json.dumps({
                "show-toast": {
                    "level": "success",
                    "title": "Success",
                    "message": response_data['message']
                }
            })
            return response   

        # If the form is not valid, return the errors and the form data
        response_data = {
            'success': False,
            'errors': form.errors,
            'invite_user_form': invite_user_form
        }
        response = JsonResponse(response_data)
        response['HX-Trigger'] = json.dumps({
            "show-toast": {
                "level": "error",
                "title": "Error",
                "message": "Failed to update profile. Please check the errors."
            }
        })
        return response
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth import login

from accounts_app.forms import InviteUserForm
from accounts_app.models import UserInvitation
from accounts_app.models import User


class InviteUserView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # This would be the view where the invited user can join.
        # Here we have to check if the provided token points to an invitation which is valid and not expired.
        ...

    def post(self, request, *args, **kwargs):
        form = InviteUserForm(request.POST)
        
        if form.is_valid():
            is_email_user = None
            try:
                is_email_user = User.objects.get(email=form.cleaned_data["email"])
                # User found, you can perform actions with is_email_user
            except User.DoesNotExist:
                is_email_user = None
                
            if is_email_user:
                response = JsonResponse({'success': False})
                response['HX-Trigger'] = json.dumps({
                    "show-toast": {
                        "level": "error",
                        "title": "Error",
                        "message": "Failed to send invitation. Email already a user."
                    }
                })
                
                return response
                
            # We could further improve this here to first check if an invitation for this email already exists and is not expired
            UserInvitation.objects.filter(email=form.cleaned_data["email"]).delete()

            invitation = UserInvitation(email=form.cleaned_data["email"], invited_by=request.user)
            invitation.save()

            invitation.send_invitation_email()
            
            # messages.success(request, "Invitation sent successfully!")
            response = JsonResponse({'success': True})
            response['HX-Trigger'] = json.dumps({
                "show-toast": {
                    "level": "success",
                    "title": "Success",
                    "message": "Invitation sent successfully!"
                }
            })
            return response        
        
        response = JsonResponse({'success': False})
        response['HX-Trigger'] = json.dumps({
            "show-toast": {
                "level": "error",
                "title": "Error",
                "message": "Failed to send invitation. Please check the email and try again."
            }
        })
        
        return response
    
class AcceptInvitationView(View):
    def get(self, request, token, *args, **kwargs):
        
        invitation = get_object_or_404(UserInvitation, token=token)

        # Check if the invitation is still valid (not expired)
        if invitation.expires_at < timezone.now():
            return render(request, "accounts_app/invitation_expired.html")

        if request.user.is_authenticated:
            return redirect('home')
    

        return render(request, "accounts_app/accept_invitation.html", {"invitation": invitation})

    def post(self, request, token, *args, **kwargs):
        invitation = get_object_or_404(UserInvitation, token=token)

        # Create a new user based on the invitation
        user = User(email=invitation.email)
        user.set_password('pass_1234')  # Set a default password or ask for one
        user.save()

        # Mark invitation as accepted
        invitation.status = 'accepted'
        invitation.save()

        # Automatically log the user in after account creation
        login(request, user)

        # Redirect to a success page after acceptance
        return redirect('invitation_success')



class InvitationSuccessView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "accounts_app/invitation_success.html")

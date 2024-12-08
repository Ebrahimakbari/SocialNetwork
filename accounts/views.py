from typing import Any
from django.conf import settings
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render,redirect, get_object_or_404
from django.views import View
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth import get_user_model
from .forms import UserRegistrationForm,LoginForm,UserPanelFormChange,ResetPasswordForm,ChangePasswordForm
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required,user_passes_test,permission_required
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin,PermissionRequiredMixin,AccessMixin
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
User = get_user_model()



class RegisterView(View):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    
    def get(self,request,*args, **kwargs):
        form = self.form_class()
        return render(request,self.template_name,context={'form':form})
    
    def post(self,request,*args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data.get
            User.objects.create_user(data('username'),data('email'),data('password1'))        
            messages.success(request,'user successfully created')
            return redirect('home:home')

        return render(request,self.template_name,context={'form':form})
    
    
class LoginView(View):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    
    def get(self,request,*args, **kwargs):
        form = self.form_class()
        return render(request,self.template_name,context={'form':form})

    def post(self,request,*args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password1', None)
            email = form.cleaned_data.get('email', None)
            user = User.objects.filter(email=email).first()
            if user.check_password(password):
                login(request,user)
                messages.success(request,'user successfully login')
                return redirect('home:home')
            messages.error(request,'incorrect password!!')
        
        return render(request,self.template_name,context={'form':form})
    
    
class LogoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
            messages.success(request, 'logout successfully!')
            return redirect('accounts:user_login')


class UserPanelView(LoginRequiredMixin, View):
    def get(self, request,*args, **kwargs):
        user_id = kwargs.get('pk')
        user = User.objects.prefetch_related('posts').get(id=user_id)
        form = UserPanelFormChange(instance=user)
        posts = user.posts.all()
        return render(request,'accounts/user_panel.html',{'form':form,'posts':posts})
    
    def post(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        user = get_object_or_404(User, id=user_id)
        form = UserPanelFormChange(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('home:home')
        messages.error(request,'invalid data')
        return render(request,'accounts/user_panel.html',{'form':form})
    
# send_mail(
#     "Subject here",
#     "Here is the message.",
#     "from@example.com",
#     ["to@example.com"],
#     fail_silently=False,
# )

class ResetPasswordView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = ResetPasswordForm()
        return render(request, "accounts/reset_password.html", context={'form':form})
        
    def post(self, request, *args, **kwargs):
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data.get('email', None)
            user = User.objects.get(email=user_email)
            user.token = get_random_string(length=32)
            user.save()
            send_mail('password reset link',
                    f"click on this http://{request.META['HTTP_HOST']}/accounts/change-password/{user.token}/ link to redirect to pass reset page",
                    settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[f"{user.email}"],
                    fail_silently=False,)
            messages.success(request, 'check your email box to reset ur password!')
            return redirect('home:home')
        return render(request, "accounts/reset_password.html", context={'form':form})
    


class ChangePasswordView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        token = kwargs.get('token', None)
        user_token = request.user.token
        if user_token != token:
            messages.error(request, 'invalid token!!')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = ChangePasswordForm()
        return render(request, "accounts/change_password.html", context={'form':form})
    
    def post(self, request, *args, **kwargs):
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = request.user
            n_password = form.cleaned_data.get('password1', None)
            if n_password:
                user.set_password(n_password)
                user.save()
                messages.success(request,'new password successfully set!')
                return redirect('home:home')
        return render(request, "accounts/change_password.html", context={'form':form})
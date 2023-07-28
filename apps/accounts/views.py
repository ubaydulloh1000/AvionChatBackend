from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required

from apps.accounts.admin import User
from apps.accounts.forms import RegisterForm


class RegisterView(generic.CreateView):
    form_class = RegisterForm
    success_url = reverse_lazy('accounts:login')
    template_name = 'accounts/signup.html'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


@login_required()
def user_list(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'accounts/user_list.html', {"users": users})


@login_required()
def user_detail(request, pk):
    user = User.objects.get(pk=pk)
    return render(request, 'accounts/user_detail.html', {"user": user})

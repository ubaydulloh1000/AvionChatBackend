from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.accounts.admin import User


@login_required()
def user_list(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'accounts/user_list.html', {"users": users})

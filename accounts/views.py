from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.urls import reverse

from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, ListView
from django.db import transaction
from django.contrib import messages
from django.views.generic.detail import DetailView
from django.contrib.auth.views import PasswordResetView

from django.shortcuts import get_object_or_404

from .forms import SignUpForm, UserForm, CustomPasswordResetForm, ProfileForm
from .models import Profile

from django.contrib.contenttypes.models import ContentType
from inventory.models import InventoryItem, Reservation, ReservationHistory  # Change 'your_app' to the name of your app




def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            user = form.save()
            content_type = ContentType.objects.get_for_model(InventoryItem)
            permissions = Permission.objects.filter(content_type=content_type)
            user.user_permissions.add(*permissions)

            content_type = ContentType.objects.get_for_model(Reservation)
            permissions = Permission.objects.filter(content_type=content_type)
            user.user_permissions.add(*permissions)

            content_type = ContentType.objects.get_for_model(ReservationHistory)
            permissions = Permission.objects.filter(content_type=content_type)
            user.user_permissions.add(*permissions)
            user.is_staff = True

            user.save()

            print(request)
            auth_login(request, user)
            # Generate the URL for 'my_account' view and redirect
            my_account_url = reverse('my_account')
            return redirect(my_account_url)
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})

@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email')
    template_name = 'my_account.html'
    success_url = reverse_lazy('my_account')

    def get_object(self):
        return self.request.user


class ProfileView(ListView):
    model = Profile
    context_object_name = 'profile'
    template_name = 'profile_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        self.user = get_object_or_404(User, pk=self.kwargs.get('pk'))
        queryset = get_object_or_404(Profile, user_id=self.user.id)
        return queryset

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm  # Use your custom form


def update_profile(request):
    print(request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid():
            user_form.save()
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.save()
            return redirect('my_account')
        else:
            messages.error(request, ('Please correct the error below.'))
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'profiles/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.views.generic import FormView, CreateView, TemplateView, ListView
from django.urls import reverse_lazy
from .forms import UserLoginForm, UserRegistrationForm
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Address
from orders.models import Order
from wishlist.models import Wishlist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

User = get_user_model()


class UserLoginView(FormView):
    template_name = "users/auth/login.html"
    form_class = UserLoginForm
    success_url = reverse_lazy("core:home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        # Pass the invalid form directly to maintain error messages
        return self.render_to_response(self.get_context_data(form=form))


class UserSignupView(CreateView):
    template_name = "users/auth/signup.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("users:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:home')
        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        # This will return the form with errors to the template
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        response = super().form_valid(form)
        print(response)
        return response


def forgot_password(request):
    return render(request, "users/auth/forgot-password.html")


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('users:login')
    return redirect('core:home')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_address(request):
    data = request.data
    try:
        # Validate required fields
        required_fields = ['phone', 'address', 'city', 'postal_code']
        for field in required_fields:
            if not data.get(field):
                return Response({
                    'error': f'{field.replace("_", " ").title()} is required'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate phone number (basic validation)
        phone = data['phone']
        if not phone.isdigit() or len(phone) < 10:
            return Response({
                'error': 'Please enter a valid phone number'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create address
        address = Address.objects.create(
            user=request.user,
            phone=phone,
            address=data['address'],
            city=data['city'],
            postal_code=data['postal_code'],
            is_default=data.get('is_default', False)
        )
        return Response({'message': 'Address added successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_address(request):
    data = request.data
    try:
        address_id = data.get('address_id')
        if not address_id:
            return Response({
                'error': 'Address ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        address = get_object_or_404(Address, id=address_id, user=request.user)
        
        # Validate required fields
        required_fields = ['phone', 'address', 'city', 'postal_code']
        for field in required_fields:
            if not data.get(field):
                return Response({
                    'error': f'{field.replace("_", " ").title()} is required'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate phone number
        phone = data['phone']
        if not phone.isdigit() or len(phone) < 10:
            return Response({
                'error': 'Please enter a valid phone number'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update address
        address.phone = phone
        address.address = data['address']
        address.city = data['city']
        address.postal_code = data['postal_code']
        address.is_default = data.get('is_default', False)
        address.save()
        
        return Response({'message': 'Address updated successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_address(request):
    data = request.data
    try:
        address_id = data.get('address_id')
        if not address_id:
            return Response({
                'error': 'Address ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        address = get_object_or_404(Address, id=address_id, user=request.user)
        
        # Check if address is default
        if address.is_default:
            return Response({
                'error': 'Cannot delete default address'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if address is used in any orders
        orders_with_address = Order.objects.filter(
            Q(address=address),
            ~Q(status__in=['delivered', 'cancelled'])
        ).exists()
        
        if orders_with_address:
            return Response({
                'error': 'Cannot delete address as it is being used in active orders'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        address.delete()
        return Response({'message': 'Address deleted successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/dashboard/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class OrderListView(LoginRequiredMixin, ListView):
    template_name = 'users/dashboard/orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created')


class WishlistView(LoginRequiredMixin, ListView):
    template_name = 'users/dashboard/wishlist.html'
    context_object_name = 'wishlist_items'

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('product')


class AddressListView(LoginRequiredMixin, ListView):
    template_name = 'users/dashboard/addresses.html'
    context_object_name = 'addresses'

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'users/dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get orders
        orders = Order.objects.filter(user=user)
        total_orders = orders.count()
        last_order = orders.first() if orders.exists() else None
        recent_orders = orders[:5]  # Last 5 orders
        
        # Get wishlist count
        wishlist_count = Wishlist.objects.filter(user=user).count()
        
        # Get address count
        address_count = Address.objects.filter(user=user).count()
        
        context.update({
            'user': user,
            'total_orders': total_orders,
            'last_order_date': last_order.created if last_order else None,
            'recent_orders': recent_orders,
            'wishlist_count': wishlist_count,
            'address_count': address_count,
        })
        return context

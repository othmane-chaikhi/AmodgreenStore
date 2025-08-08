from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import CustomUser, Order, CommunityPost, Comment, Product, Category,ProductImage


class CustomUserCreationForm(UserCreationForm):
    """Formulaire d'inscription personnalisé"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    phone = forms.CharField(max_length=20, required=False, label="Téléphone")
    city = forms.CharField(max_length=100, required=False, label="Ville")

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'city', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('username'), Column('email'), css_class='form-row'),
            Row(Column('first_name'), Column('last_name'), css_class='form-row'),
            Row(Column('phone'), Column('city'), css_class='form-row'),
            'password1',
            'password2',
            Submit('submit', 'S\'inscrire', css_class='w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition-colors')
        )
        for field in self.fields.values():
            field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500'


class OrderForm(forms.ModelForm):
    """Formulaire de commande"""

    class Meta:
        model = Order
        fields = ['full_name', 'phone', 'city', 'address', 'notes']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Nom et prénom complets'}),
            'phone': forms.TextInput(attrs={'placeholder': '06XXXXXXXX ou +212XXXXXXXX'}),
            'city': forms.TextInput(attrs={'placeholder': 'Votre ville'}),
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Adresse complète de livraison'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Remarques ou instructions spéciales (optionnel)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('full_name'), Column('phone'), css_class='form-row'),
            Row(Column('city'), Column('address'), css_class='form-row'),
            'notes',
            Submit('submit', '🛒 Envoyer ma commande', css_class='w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg transition-colors text-lg')
        )
        for field in self.fields.values():
            field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500'


class CommunityPostForm(forms.ModelForm):
    RATING_CHOICES = [(i, f"{i} étoile{'s' if i > 1 else ''}") for i in range(1, 6)]
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(),
        required=False,
        label='Note'
    )

    class Meta:
        model = CommunityPost
        fields = ['title', 'content', 'post_type', 'product', 'rating']
        widgets = {
            'post_type': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md', 'onchange': 'toggleReviewFields()'}),
            'product': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.initial.get('post_type') == 'review':
            self.fields['rating'].required = True
            self.fields['product'].required = True
        else:
            self.fields['rating'].required = False
            self.fields['product'].required = False

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('post_type') == 'review':
            if not cleaned_data.get('product'):
                self.add_error('product', "Un produit doit être sélectionné pour un avis")
            if not cleaned_data.get('rating'):
                self.add_error('rating', "Veuillez attribuer une note")
        return cleaned_data


class CommentForm(forms.ModelForm):
    """Formulaire pour commenter un post"""

    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Votre commentaire...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'content',
            Submit('submit', '💬 Commenter', css_class='bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition-colors')
        )
        self.fields['content'].widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500'


class UserProfileForm(forms.ModelForm):
    """Formulaire pour modifier le profil utilisateur"""

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'city', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Parlez-nous de vous...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('first_name'), Column('last_name'), css_class='form-row'),
            'email',
            Row(Column('phone'), Column('city'), css_class='form-row'),
            'bio',
            Submit('submit', '✅ Mettre à jour', css_class='bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition-colors')
        )
        for field in self.fields.values():
            field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500'

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']

class ProductForm(forms.ModelForm):
    """Formulaire pour ajouter ou modifier un produit"""

    class Meta:
        model = Product
        fields = ['name', 'name_ar', 'description', 'description_ar', 'ingredients', 'ingredients_ar', 'price', 'image', 'category', 'is_available']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name', 'name_ar', 'description', 'description_ar',
            'ingredients', 'ingredients_ar', 'price',
            'image', 'category', 'is_available',
            Submit('submit', '💾 Enregistrer', css_class='bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded')
        )
        for field in self.fields.values():
            field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500'


class ConfirmOrderForm(forms.Form):
    delivery_date = forms.DateField(
        label="Date estimée de livraison",
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date()
    )


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'name_ar', 'description']

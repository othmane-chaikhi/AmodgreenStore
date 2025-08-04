from django import forms
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import CustomUser, Order, CommunityPost, Comment


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
            Row(
                Column('username', css_class='form-group col-md-6 mb-3'),
                Column('email', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('phone', css_class='form-group col-md-6 mb-3'),
                Column('city', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'password1',
            'password2',
            Submit('submit', 'S\'inscrire', css_class='w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition-colors')
        )
        
        # Personnaliser les classes CSS des champs
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500'


class OrderForm(forms.ModelForm):
    """Formulaire de commande"""
    
    class Meta:
        model = Order
        fields = ['full_name', 'phone', 'city', 'address', 'product', 'quantity', 'notes']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Nom et prénom complets'}),
            'phone': forms.TextInput(attrs={'placeholder': '06XXXXXXXX ou +212XXXXXXXX'}),
            'city': forms.TextInput(attrs={'placeholder': 'Votre ville'}),
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Adresse complète de livraison'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Remarques ou instructions spéciales (optionnel)'}),
            'quantity': forms.NumberInput(attrs={'min': 1, 'value': 1}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('full_name', css_class='form-group col-md-6 mb-3'),
                Column('phone', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('city', css_class='form-group col-md-6 mb-3'),
                Column('quantity', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'product',
            'address',
            'notes',
            Submit('submit', '🛒 Envoyer ma commande', css_class='w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg transition-colors text-lg')
        )
        
        # Personnaliser les classes CSS des champs
        for field_name, field in self.fields.items():
            if field_name == 'product':
                field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500'
            elif field_name == 'quantity':
                field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500'
            else:
                field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500'
        
        # Filtrer seulement les produits disponibles
        self.fields['product'].queryset = self.fields['product'].queryset.filter(is_available=True)


class CommunityPostForm(forms.ModelForm):
    """Formulaire pour créer un post dans la communauté"""
    
    class Meta:
        model = CommunityPost
        fields = ['title', 'content', 'post_type', 'product']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Titre de votre message'}),
            'content': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Partagez votre expérience, avis ou question...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'post_type',
            'product',
            'content',
            Submit('submit', '📝 Publier mon message', css_class='w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition-colors')
        )
        
        # Personnaliser les classes CSS des champs
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500'
        
        # Rendre le champ produit optionnel visuellement
        self.fields['product'].required = False
        self.fields['product'].empty_label = "Aucun produit spécifique"


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
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'email',
            Row(
                Column('phone', css_class='form-group col-md-6 mb-3'),
                Column('city', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'bio',
            Submit('submit', '✅ Mettre à jour', css_class='bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition-colors')
        )
        
        # Personnaliser les classes CSS des champs
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500'

from .models import Product

class ProductForm(forms.ModelForm):
    """Formulaire pour ajouter ou modifier un produit"""
    
    class Meta:
        model = Product
        fields = ['name', 'name_ar', 'description', 'description_ar', 'ingredients',
                  'ingredients_ar', 'price', 'image', 'category', 'is_available']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'name_ar',
            'description',
            'description_ar',
            'ingredients',
            'ingredients_ar',
            'price',
            'image',
            'category',
            'is_available',
            Submit('submit', '💾 Enregistrer', css_class='bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded')
        )
        
        # Ajout de classes CSS personnalisées
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500'
from django import forms
from django.utils import timezone
from .models import Order

class ConfirmOrderForm(forms.Form):
    delivery_date = forms.DateField(
        label="Date estimée de livraison",
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date()
    )

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.forms import BaseInlineFormSet, inlineformset_factory
from .models import (
    CustomUser, Order, CommunityPost,
    Product, Category, ProductImage,
    ProductVariant
)


class BaseStyledForm:
    """Base class for forms with common styling"""
    def _apply_common_styling(self):
        common_classes = (
            "w-full px-3 py-2 border border-gray-300 rounded-md "
            "focus:outline-none focus:ring-2 focus:ring-green-500"
        )
        for field in self.fields.values():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{existing_classes} {common_classes}".strip()


class CustomUserCreationForm(UserCreationForm, BaseStyledForm):
    """Custom registration form with enhanced styling"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    phone = forms.CharField(max_length=20, required=False, label="Téléphone")
    city = forms.CharField(max_length=100, required=False, label="Ville")

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 
                 'phone', 'city', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('username'), Column('email'), css_class='form-row'),
            Row(Column('first_name'), Column('last_name'), css_class='form-row'),
            Row(Column('phone'), Column('city'), css_class='form-row'),
            'password1',
            'password2',
            Submit('submit', "S'inscrire", css_class=(
                'w-full bg-green-600 hover:bg-green-700 text-white '
                'font-bold py-2 px-4 rounded transition-colors'
            ))
        )
        self._apply_common_styling()


class OrderForm(forms.ModelForm, BaseStyledForm):
    """Order form with address and notes"""
    class Meta:
        model = Order
        fields = ['full_name', 'phone', 'city', 'address', 'notes']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Nom et prénom complets'}),
            'phone': forms.TextInput(attrs={'placeholder': '06XXXXXXXX ou +212XXXXXXXX'}),
            'city': forms.TextInput(attrs={'placeholder': 'Votre ville'}),
            'address': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Adresse complète de livraison'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Remarques ou instructions spéciales (optionnel)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('full_name'), Column('phone'), css_class='form-row'),
            Row(Column('city'), Column('address'), css_class='form-row'),
            'notes',
            Submit('submit', '🛒 Envoyer ma commande', css_class=(
                'w-full bg-green-600 hover:bg-green-700 text-white '
                'font-bold py-3 px-6 rounded-lg transition-colors text-lg'
            ))
        )
        self._apply_common_styling()


class CommunityPostForm(forms.ModelForm, BaseStyledForm):
    """Community post form with validation"""
    class Meta:
        model = CommunityPost
        fields = ['title', 'content', 'product', 'rating', 'image']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'rating-radio'}),
            'title': forms.TextInput(attrs={'placeholder': 'Titre de votre avis'}),
            'content': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Votre avis détaillé'
            }),
            'image': forms.ClearableFileInput(attrs={'class': 'file-input-style'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('product'):
            self.add_error('product', "Un produit doit être sélectionné pour un avis.")
        if not cleaned_data.get('rating'):
            self.add_error('rating', "Veuillez attribuer une note.")
        return cleaned_data


class UserProfileForm(forms.ModelForm, BaseStyledForm):
    """User profile update form"""
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'city', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Parlez-nous de vous...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('first_name'), Column('last_name'), css_class='form-row'),
            'email',
            Row(Column('phone'), Column('city'), css_class='form-row'),
            'bio',
            Submit('submit', '✅ Mettre à jour', css_class=(
                'bg-green-600 hover:bg-green-700 text-white '
                'font-bold py-2 px-4 rounded transition-colors'
            ))
        )
        self._apply_common_styling()


class ProductImageForm(forms.ModelForm):
    """Form for uploading product images"""
    class Meta:
        model = ProductImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={
                'class': 'file-input-style'
            })
        }

from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

class ProductForm(forms.ModelForm, BaseStyledForm):
    """Main product form with multilingual fields"""

    class Meta:
        model = Product
        fields = [
            'name', 'name_ar', 'description', 'description_ar',
            'ingredients', 'ingredients_ar', 'price', 'image',
            'category', 'is_available'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'description_ar': forms.Textarea(attrs={
                'rows': 3, 
                'dir': 'rtl'
            }),
            'ingredients': forms.Textarea(attrs={'rows': 3}),
            'ingredients_ar': forms.Textarea(attrs={
                'rows': 3, 
                'dir': 'rtl'
            }),
        }

    def __init__(self, *args, **kwargs):
        # Récupérer formset s'il est passé en kwargs
        self.variant_formset = kwargs.pop('variant_formset', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name', 'name_ar', 'description', 'description_ar',
            'ingredients', 'ingredients_ar', 'price',
            'image', 'category', 'is_available',
            Submit('submit', '💾 Enregistrer', css_class=(
                "bg-green-600 hover:bg-green-700 text-white "
                "font-bold py-2 px-4 rounded shadow-md transition"
            ))
        )
        self._apply_common_styling()

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')

        # Validation obligatoire prix
        if price is None:
            raise ValidationError("Le prix du produit est obligatoire.")

        # Validation égalité prix produit et variante par défaut
        if self.variant_formset and self.variant_formset.is_valid():
            # Trouver la variante par défaut sélectionnée
            default_variant_index = self.data.get('default_variant')
            if default_variant_index is None:
                raise ValidationError("Veuillez sélectionner une variante par défaut.")

            try:
                default_variant_index = int(default_variant_index)
            except (TypeError, ValueError):
                raise ValidationError("Sélection variante par défaut invalide.")

            if default_variant_index < 0 or default_variant_index >= len(self.variant_formset.forms):
                raise ValidationError("Indice variante par défaut hors limite.")

            default_variant_form = self.variant_formset.forms[default_variant_index]
            variant_price = default_variant_form.cleaned_data.get('price')
            if variant_price is None:
                raise ValidationError("Le prix de la variante par défaut est invalide.")

            if price != variant_price:
                raise ValidationError("Le prix du produit doit être égal au prix de la variante par défaut.")

        return cleaned_data


class ProductVariantForm(forms.ModelForm, BaseStyledForm):
    """Product variant form with default variant selection"""

    is_default = forms.BooleanField(
        required=False,
        label="Variante par défaut",
        widget=forms.RadioSelect(
            attrs={'class': 'default-variant-radio'},
            choices=[(True, 'Oui')]
        )
    )

    class Meta:
        model = ProductVariant
        fields = ['name', 'price', 'is_default']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.product.default_variant == self.instance:
            self.initial['is_default'] = True
        self._apply_common_styling()


class ProductVariantFormSet(BaseInlineFormSet):
    def save(self, commit=True):
        variants = super().save(commit=commit)
        product = self.instance

        # Reset default_variant
        product.default_variant = None
        product.save()

        for form in self.forms:
            if form.cleaned_data.get('is_default') and not form.cleaned_data.get('DELETE', False):
                product.default_variant = form.instance
                break

        # If no variant default, fallback to first
        if not product.default_variant and variants:
            product.default_variant = variants[0]

        product.save()
        return variants

class ConfirmOrderForm(forms.Form):
    """Form for confirming delivery date"""
    delivery_date = forms.DateField(
        label="Date estimée de livraison",
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date()
    )


from django import forms

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'name_ar', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full rounded border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-olive-600 focus:border-olive-600',
                'placeholder': 'Nom de la catégorie',
            }),
            'name_ar': forms.TextInput(attrs={
                'class': 'w-full rounded border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-olive-600 focus:border-olive-600',
                'placeholder': 'اسم الفئة',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full rounded border border-gray-300 px-3 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-olive-600 focus:border-olive-600',
                'rows': 4,
                'placeholder': 'Description de la catégorie',
            }),
        }

from django.forms import inlineformset_factory

ProductVariantFormSet = inlineformset_factory(
    Product,
    ProductVariant,
    fields=('name', 'price'), 
    extra=1,
    can_delete=True
)

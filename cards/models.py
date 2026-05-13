from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Type(models.Model):
    TYPE_COLORS = {
        'Fire': '#EF4444',       'Water': '#3B82F6',
        'Grass': '#22C55E',      'Lightning': '#EAB308',
        'Psychic': '#A855F7',    'Fighting': '#F97316',
        'Darkness': '#1F2937',   'Metal': '#6B7280',
        'Dragon': '#7C3AED',     'Colorless': '#9CA3AF',
        'Fairy': '#EC4899',
    }
    TYPE_ICONS = {
        'Fire': '🔥',    'Water': '💧',   'Grass': '🌿',
        'Lightning': '⚡', 'Psychic': '🔮', 'Fighting': '👊',
        'Darkness': '🌑', 'Metal': '⚙️',   'Dragon': '🐉',
        'Colorless': '⚪', 'Fairy': '✨',
    }

    name = models.CharField(max_length=50, unique=True)

    @property
    def color(self):

        return self.TYPE_COLORS.get(self.name, '#9CA3AF')

    @property
    def icon(self):

        return self.TYPE_ICONS.get(self.name, '◆')

    def __str__(self):

        return self.name

    class Meta:
        ordering = ['name']

class Cardset(models.Model):
    set_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    series = models.CharField(max_length=200, blank=True)
    printed_total = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    release_date = models.DateTimeField(null=True, blank=True)
    symbol_url = models.URLField(blank=True)
    logo_url = models.URLField(blank=True)

    def get_absolute_url(self):
        
        return reverse("cards:set_detail", kwargs={"set_id": self.set_id})
    
    def __str__(self):

        return self.name
    
    class Meta:
        ordering = ['-release_date']
        verbose_name = 'Set'

class Card(models.Model):
    RARITY_CHOICES = [
        ('Common', 'Common'),
        ('Uncommon', 'Uncommon'),
        ('Rare', 'Rare'),
        ('Rare Holo', 'Rare Holo'),
        ('Rare Holo EX', 'Rare Holo EX'),
        ('Rare Holo GX', 'Rare Holo GX'),
        ('Rare Holo V', 'Rare Holo V'),
        ('Rare Holo VMAX', 'Rare Holo VMAX'),
        ('Rare Ultra', 'Rare Ultra'),
        ('Rare Secret', 'Rare Secret'),
        ('Amazing Rare', 'Amazing Rare'),
        ('Rare Rainbow', 'Rare Rainbow'),
        ('Promo', 'Promo'),
    ]

    card_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    supertype = models.CharField(max_length=50, default='Pokemon')
    subtypes = models.JSONField(default=list, blank=True)
    hp = models.IntegerField(null=True, blank=True)
    rarity = models.CharField(max_length=50, choices=RARITY_CHOICES, blank=True, db_index=True)
    card_number = models.CharField(max_length=20, blank=True)
    artist = models.CharField(max_length=200, blank=True)
    flavor_text = models.TextField(blank=True)
    image_small = models.URLField(blank=True)
    image_large = models.URLField(blank=True)
    evolves_from = models.CharField(max_length=200, blank=True)
    retreat_cost = models.JSONField(default=list, blank=True)
    card_set = models.ForeignKey(Cardset, on_delete=models.SET_NULL,null=True, blank=True, related_name='cards')
    types = models.ManyToManyField(Type, through='CardType', related_name='cards', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse("cards:card_detail", kwargs={"card_id": self.card_id})
    
    @property
    def market_price(self):
        try:
            return self.price.tcg_market or self.price.tcg_mid
        except Exception:
            None

    def __str__(self):
        
        return f'{self.name} ({self.card_id})'
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name', 'rarity']),
        ]

class CardType(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)

    class Meta:
        unique_together = ('card', 'type')
        ordering = ['order']

class Attack(models.Model):
    card = models.ForeignKey(Card,on_delete=models.CASCADE, related_name='attacks')
    name = models.CharField(max_length=200)
    damage = models.CharField(max_length=20, blank=True)
    converted_cost = models.IntegerField(default=0)
    cost = models.JSONField(default=list)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    def __str__(self):

        return f'{self.card.name} - {self.name}'
    
    class Meta:
        ordering = ['order']

class Weakness(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='weaknesses')
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    value = models.CharField(max_length=10, blank=True)

class Resistance(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='resistances')
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    value = models.CharField(max_length=10, blank=True)

class Price(models.Model):
    card = models.OneToOneField(Card, on_delete=models.CASCADE, related_name='price')
    tcg_low = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tcg_mid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tcg_high = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tcg_market = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cm_avg1 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cm_avg7 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cm_avg30 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    update_at = models.DateField(auto_now=True)

    @property
    def best_price(self):

        return self.tcg_market or self.tcg_mid or self.tcg_low
    
    def __str__(self):

        return f'{self.card.name} - ${self.best_price or "N/A"}'
    
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user','card') # prevent duplicates
        ordering = ['-created_at']

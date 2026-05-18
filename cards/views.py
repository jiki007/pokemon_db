from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count, Max
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import Card, Cardset, Type, Price,Attack, Favorite
from .forms import SignUpForm


def home(request):
    featured = (
        Card.objects.filter(image_small__gt='')
        .select_related('card_set')
        .prefetch_related('types')
        .order_by('-created_at')[:8]
    )
    total_cards = Card.objects.count()
    total_sets  = Cardset.objects.count()
    recent_sets = Cardset.objects.order_by('-release_date')[:6]
    top_price = (
        Price.objects.filter(tcg_market__isnull=False)
        .select_related('card')
        .order_by('-tcg_market')
        .first()
    )
    types = Type.objects.annotate(cnt=Count('cards')).order_by('-cnt')

    return render(request, 'cards/home.html', {
        'featured':    featured,
        'total_cards': total_cards,
        'total_sets':  total_sets,
        'recent_sets': recent_sets,
        'top_price':   top_price,
        'types':       types,
    })


def card_list(request):
    qs = (
        Card.objects.select_related('card_set')
        .prefetch_related('types')
    )

    q = request.GET.get('q')
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(flavor_text__icontains=q) |
            Q(artist__icontains=q)
        )

    type_filter = request.GET.get('type')
    if type_filter:
        qs = qs.filter(types__name__iexact=type_filter)

    rarity = request.GET.get('rarity')
    if rarity:
        qs = qs.filter(rarity=rarity)

    set_filter = request.GET.get('set')
    if set_filter:
        qs = qs.filter(card_set__set_id=set_filter)

    hp_min = request.GET.get('hp_min')
    hp_max = request.GET.get('hp_max')
    if hp_min:
        qs = qs.filter(hp__gte=int(hp_min))
    if hp_max:
        qs = qs.filter(hp__lte=int(hp_max))

    ordering = request.GET.get('ordering', 'name')
    if ordering in ['name', '-name', 'hp', '-hp', '-created_at']:
        qs = qs.order_by(ordering)
    elif ordering == '-price':
        qs = qs.order_by('-price__tcg_market')
    elif ordering == 'price':
        qs = qs.order_by('price__tcg_market')

    qs = qs.distinct()
    paginator = Paginator(qs, 24)
    page_obj  = paginator.get_page(request.GET.get('page'))
    types = Type.objects.all()
    sets  = Cardset.objects.all()

    return render(request, 'cards/card_list.html', {
        'page_obj': page_obj,
        'types':    types,
        'sets':     sets,
        'total':    qs.count(),
        'q':        q or '',
        'rarities': Card.RARITY_CHOICES,
    })


def card_detail(request, card_id):
    card = get_object_or_404(
        Card.objects.select_related('card_set')
        .prefetch_related(
            'types', 'attacks',
            'weaknesses__type', 'resistances__type'
        ),
        card_id=card_id
    )
    related = (
        Card.objects.filter(types__in=card.types.all())
        .exclude(pk=card.pk)
        .prefetch_related('types')
        .distinct()[:6]
    )
    is_favorited = False

    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, card=card,).exists()

    return render(request, 'cards/card_detail.html', {
        'card':    card,
        'related': related,
        'is_favorited':is_favorited,
    })


def set_list(request):
    qs = Cardset.objects.annotate(card_count=Count('cards'))

    q = request.GET.get('q')
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(series__icontains=q)
        )

    paginator   = Paginator(qs, 20)
    page_obj    = paginator.get_page(request.GET.get('page'))
    series_list = (
        Cardset.objects.values_list('series', flat=True)
        .distinct()
        .order_by('series')
    )

    return render(request, 'cards/set_list.html', {
        'page_obj':    page_obj,
        'series_list': series_list,
        'q':           q or '',
    })


def set_detail(request, set_id):
    card_set = get_object_or_404(Cardset, set_id=set_id)
    cards = (
        Card.objects.filter(card_set=card_set)
        .select_related('card_set')
        .prefetch_related('types')
        .order_by('card_number', 'name')
    )
    paginator = Paginator(cards, 24)
    page_obj  = paginator.get_page(request.GET.get('page'))
    stats     = cards.aggregate(avg_hp=Avg('hp'), max_hp=Max('hp'))

    return render(request, 'cards/set_detail.html', {
        'card_set': card_set,
        'page_obj': page_obj,
        'stats':    stats,
        'total':    cards.count(),
    })


def search(request):
    q     = request.GET.get('q', '').strip()
    cards = sets = None

    if q:
        cards = (
            Card.objects.filter(
                Q(name__icontains=q) |
                Q(flavor_text__icontains=q) |
                Q(artist__icontains=q)
            )
            .select_related('card_set')
            .prefetch_related('types')[:20]
        )
        sets = Cardset.objects.filter(
            Q(name__icontains=q) |
            Q(series__icontains=q)
        )[:6]

    return render(request, 'cards/search_results.html', {
        'q':     q,
        'cards': cards,
        'sets':  sets,
    })


def dashboard(request):
    total_cards = Card.objects.count()
    total_sets  = Cardset.objects.count()
    avg_hp = (
        Card.objects.filter(hp__isnull=False)
        .aggregate(avg=Avg('hp'))['avg']
    )
    top_price = (
        Price.objects.filter(tcg_market__isnull=False)
        .select_related('card')
        .order_by('-tcg_market')
        .first()
    )
    rare_cards = (
        Card.objects.filter(
            rarity__in=['Rare Secret', 'Rare Rainbow', 'Rare Ultra', 'Rare Holo']
        )
        .prefetch_related('types')[:8]
    )
    by_type = Type.objects.annotate(cnt=Count('cards')).order_by('-cnt')
    by_rarity = (
        Card.objects.values('rarity')
        .annotate(cnt=Count('id'))
        .order_by('-cnt')[:8]
    )
    expensive = (
        Price.objects.filter(tcg_market__isnull=False)
        .select_related('card__card_set')
        .prefetch_related('card__types')
        .order_by('-tcg_market')[:10]
    )

    # Data quality counts
    missing_hp      = Card.objects.filter(hp__isnull=True).count()
    missing_rarity  = Card.objects.filter(rarity='').count()
    missing_price   = Card.objects.filter(price__isnull=True).count()
    empty_sets      = Cardset.objects.annotate(cnt=Count('cards')).filter(cnt=0).count()

    return render(request, 'cards/dashboard.html', {
        'total_cards':total_cards,
        'total_sets':total_sets,
        'avg_hp':round(avg_hp, 1) if avg_hp else 0,
        'top_price':top_price,
        'rare_cards':rare_cards,
        'by_type':by_type,
        'by_rarity':by_rarity,
        'expensive':expensive,
        'missing_hp':missing_hp,
        'missing_rarity':missing_rarity,
        'missing_price': missing_price,
        'empty_sets':empty_sets,
    })

def card_create(request):
    from .models import CardType
    if request.method == 'POST':
        card_id = request.POST.get('card_id')
        name = request.POST.get('name')
        supertype = request.POST.get('supertype', 'Pokemon')
        hp = request.POST.get('hp')
        rarity = request.POST.get('rarity')
        card_number = request.POST.get('card_number')
        artist = request.POST.get('artist')
        flavor_text = request.POST.get('flavor_text')
        image_small = request.POST.get('image_small')
        image_large = request.POST.get('image_large')
        set_id = request.POST.get('set_id')

        if not card_id or not name:
            return render(request, 'cards/card_from.html', {
                'action': 'Create',
                'error': 'Card ID and Name are required.',
                'sets': Cardset.objects.all(),
                'rarities': Card.RARITY_CHOICES,
            })
        card_set = Cardset.objects.filter(set_id=set_id).first() if set_id else None
        card = Cardset.objects.create(
            card_id=card_id,
            name=name,
            supertype=supertype,
            hp=int(hp) if hp else None,
            rarity=rarity or '',
            card_number=card_number or '',
            artist=artist or '',
            flavor_text=flavor_text or '',
            image_small=image_small or '',
            image_large=image_large or '',
            card_set=card_set,
        
        )
        return redirect(card.get_absolute_url())
    
    return render(request, 'cards/card_form.html', {
        'action':'Create',
        'sets': Cardset.objects.all(),
        'rarities': Card.RARITY_CHOICES,
    })


def card_edit(request, card_id):
    card = get_object_or_404(Card, card_id=card_id)

    if request.method == 'POST':
        card.name = request.POST.get('name', card.name)
        card.supertype = request.POST.get('supertype', card.supertype)
        card.rarity = request.POST.get('rarity', card.rarity)
        card.card_number = request.POST.get('card_number', card.card_number)
        card.artist = request.POST.get('artist', card.artist)
        card.flavor_text = request.POST.get('flavor_text', card.flavor_text)
        card.image_small = request.POST.get('image_small', card.image_small)
        card.image_large = request.POST.get('imag_large', card.image_large)
        hp = request.POST.get('hp')
        card.hp = int(hp) if hp else None
        set_id = request.POST.get('card_set')
        card.card_set = Cardset.objects.filter(set_id=set_id).first() if set_id else None
        card.save()

        return redirect(card.get_absolute_url())
    
    return render(request, 'cards/card_form.html', {
        'action':'Edit',
        'card':card,
        'sets':Cardset.objects.all(),
        'rarities':Card.RARITY_CHOICES,
    })

def card_delete(request, card_id):
    card = get_object_or_404(Card, card_id=card_id)
    if request.method == 'POST':
        card.delete()
        return redirect('cards:card_list')
    return render(request, 'cards/card_confirm_delete.html', {'card': card})

def sql_showcase(request):
    from django.db.models import Avg, Count, Max, Min
    from django.db import connection

    def format_sql(sql):
        keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT', 'INNER', 'OUTER',
                    'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT', 'AND', 'OR',
                    'ON', 'AS', 'COUNT', 'AVG', 'MAX', 'MIN', 'DISTINCT',
                    'LEFT OUTER JOIN', 'INNER JOIN']
        for kw in sorted(keywords, key=len, reverse=True):
            sql = sql.replace(kw, f'\n{kw}')
        return sql.strip()

    queries = []

    # ── 1. MULTI-TABLE JOIN ───────────────────────────────────────
    q1 = (
        Card.objects.select_related('card_set')
        .prefetch_related('types')
        .filter(hp__isnull=False)
        .order_by('-hp')[:8]
    )
    queries.append({
        'number': 1,
        'title': 'Multi-Table JOIN — Top HP Cards',
        'description': 'Joins Card, CardSet and Type tables to retrieve the highest HP cards with their set and type information.',
        'orm': (
            "Card.objects.select_related('card_set')\n"
            "    .prefetch_related('types')\n"
            "    .filter(hp__isnull=False)\n"
            "    .order_by('-hp')[:8]"
        ),
        'sql': format_sql(str(
            Card.objects.select_related('card_set')
            .filter(hp__isnull=False)
            .order_by('-hp')
            .query
        )),
        'headers': ['Name', 'Set', 'Types', 'HP', 'Rarity'],
        'rows': [
            [c.name,
             c.card_set.name if c.card_set else '—',
             ', '.join(t.name for t in c.types.all()),
             c.hp,
             c.rarity or '—']
            for c in q1
        ],
    })

    # ── 2. GROUP BY + AVG ─────────────────────────────────────────
    q2 = (
        Type.objects.annotate(avg_hp=Avg('cards__hp'))
        .filter(avg_hp__isnull=False)
        .order_by('-avg_hp')
    )
    queries.append({
        'number': 2,
        'title': 'GROUP BY + AVG — Average HP per Type',
        'description': 'Groups cards by energy type and computes the average HP for each group.',
        'orm': (
            "Type.objects.annotate(avg_hp=Avg('cards__hp'))\n"
            "    .filter(avg_hp__isnull=False)\n"
            "    .order_by('-avg_hp')"
        ),
        'sql': format_sql(str(q2.query)),
        'headers': ['Type', 'Average HP'],
        'rows': [[t.name, f"{t.avg_hp:.1f}"] for t in q2],
    })

    # ── 3. GROUP BY + COUNT ───────────────────────────────────────
    q3 = (
        Card.objects.values('rarity')
        .annotate(total=Count('id'))
        .exclude(rarity='')
        .order_by('-total')
    )
    queries.append({
        'number': 3,
        'title': 'GROUP BY + COUNT — Cards per Rarity',
        'description': 'Counts how many cards exist for each rarity level, ordered from most to least common.',
        'orm': (
            "Card.objects.values('rarity')\n"
            "    .annotate(total=Count('id'))\n"
            "    .exclude(rarity='')\n"
            "    .order_by('-total')"
        ),
        'sql': format_sql(str(q3.query)),
        'headers': ['Rarity', 'Card Count'],
        'rows': [[r['rarity'], r['total']] for r in q3],
    })

    # ── 4. JOIN + AVG PRICE ───────────────────────────────────────
    q4 = (
        Price.objects.values('card__rarity')
        .annotate(avg_price=Avg('tcg_market'))
        .filter(avg_price__isnull=False)
        .exclude(card__rarity='')
        .order_by('-avg_price')
    )
    queries.append({
        'number': 4,
        'title': 'JOIN + GROUP BY + AVG — Avg Market Price per Rarity',
        'description': 'Joins the Price and Card tables, then groups by rarity to compute average market price.',
        'orm': (
            "Price.objects.values('card__rarity')\n"
            "    .annotate(avg_price=Avg('tcg_market'))\n"
            "    .filter(avg_price__isnull=False)\n"
            "    .exclude(card__rarity='')\n"
            "    .order_by('-avg_price')"
        ),
        'sql': format_sql(str(q4.query)),
        'headers': ['Rarity', 'Avg Market Price'],
        'rows': [[r['card__rarity'], f"${r['avg_price']:.2f}"] for r in q4],
    })

    # ── 5. TOP ARTISTS ────────────────────────────────────────────
    q5 = (
        Card.objects.exclude(artist='')
        .values('artist')
        .annotate(card_count=Count('id'))
        .order_by('-card_count')[:10]
    )
    queries.append({
        'number': 5,
        'title': 'GROUP BY + ORDER — Top Artists by Card Count',
        'description': 'Groups cards by artist name and ranks them by how many cards they have illustrated.',
        'orm': (
            "Card.objects.exclude(artist='')\n"
            "    .values('artist')\n"
            "    .annotate(card_count=Count('id'))\n"
            "    .order_by('-card_count')[:10]"
        ),
        'sql': format_sql(str(
            Card.objects.exclude(artist='')
            .values('artist')
            .annotate(card_count=Count('id'))
            .order_by('-card_count')
            .query
        )),
        'headers': ['Artist', 'Cards Illustrated'],
        'rows': [[r['artist'], r['card_count']] for r in q5],
    })

    # ── 6. FILTER + ORDER + LIMIT ─────────────────────────────────
    q6 = (
        Attack.objects.select_related('card')
        .filter(converted_cost__gt=0)
        .order_by('-converted_cost')[:8]
    )
    queries.append({
        'number': 6,
        'title': 'FILTER + ORDER + LIMIT — Highest Energy Cost Attacks',
        'description': 'Filters attacks with energy cost greater than zero, orders by cost descending, and limits to 8 results.',
        'orm': (
            "Attack.objects.select_related('card')\n"
            "    .filter(converted_cost__gt=0)\n"
            "    .order_by('-converted_cost')[:8]"
        ),
        'sql': format_sql(str(
            Attack.objects.select_related('card')
            .filter(converted_cost__gt=0)
            .order_by('-converted_cost')
            .query
        )),
        'headers': ['Attack', 'Card', 'Energy Cost', 'Damage'],
        'rows': [
            [a.name, a.card.name, a.converted_cost, a.damage or '—']
            for a in q6
        ],
    })

    # ── 7. NULL CHECK — DATA COMPLETENESS ─────────────────────────
    total = Card.objects.count()
    def pct(n): return f"{n/total*100:.1f}%" if total else '0%'
    has_hp      = Card.objects.filter(hp__isnull=False).count()
    has_rarity  = Card.objects.exclude(rarity='').count()
    has_price   = Price.objects.count()
    has_image   = Card.objects.exclude(image_small='').count()
    has_artist  = Card.objects.exclude(artist='').count()

    queries.append({
        'number': 7,
        'title': 'NULL CHECK — Data Completeness Report',
        'description': 'Checks how complete the dataset is by counting non-null and non-empty values for key fields.',
        'orm': (
            "Card.objects.filter(hp__isnull=False).count()\n"
            "Card.objects.exclude(rarity='').count()\n"
            "Price.objects.count()\n"
            "Card.objects.exclude(image_small='').count()\n"
            "Card.objects.exclude(artist='').count()"
        ),
        'sql': (
            "SELECT COUNT(*) FROM cards_card WHERE hp IS NOT NULL;\n"
            "SELECT COUNT(*) FROM cards_card WHERE rarity != '';\n"
            "SELECT COUNT(*) FROM cards_price;\n"
            "SELECT COUNT(*) FROM cards_card WHERE image_small != '';\n"
            "SELECT COUNT(*) FROM cards_card WHERE artist != '';"
        ),
        'headers': ['Field', 'Count', 'Coverage'],
        'rows': [
            ['Total Cards',  total,      '100%'],
            ['Has HP',       has_hp,     pct(has_hp)],
            ['Has Rarity',   has_rarity, pct(has_rarity)],
            ['Has Price',    has_price,  pct(has_price)],
            ['Has Image',    has_image,  pct(has_image)],
            ['Has Artist',   has_artist, pct(has_artist)],
        ],
    })

    # ── 8. TYPE BATTLE STATS — 3 LIGHTWEIGHT QUERIES ─────────────
    # Split into 3 separate simple queries instead of one heavy multi-join
    # to avoid temp disk space issues on Railway free tier
    types_cards     = {t.id: t for t in Type.objects.annotate(card_count=Count('cards', distinct=True)).order_by('-card_count')}
    types_weakness  = {t.id: t.as_weakness  for t in Type.objects.annotate(as_weakness=Count('weakness', distinct=True))}
    types_resistance= {t.id: t.as_resistance for t in Type.objects.annotate(as_resistance=Count('resistance', distinct=True))}

    queries.append({
        'number': 8,
        'title': 'MULTI-JOIN + COUNT — Type Battle Statistics',
        'description': 'Three separate annotated queries joined in Python to avoid heavy temp-file usage on the database.',
        'orm': (
            "Type.objects.annotate(card_count=Count('cards', distinct=True))\n"
            "Type.objects.annotate(as_weakness=Count('weakness', distinct=True))\n"
            "Type.objects.annotate(as_resistance=Count('resistance', distinct=True))"
        ),
        'sql': (
            "SELECT type_id, COUNT(DISTINCT card_id) FROM cards_cardtype GROUP BY type_id;\n"
            "SELECT type_id, COUNT(*) FROM cards_weakness GROUP BY type_id;\n"
            "SELECT type_id, COUNT(*) FROM cards_resistance GROUP BY type_id;"
        ),
        'headers': ['Type', 'Cards', 'Times as Weakness', 'Times as Resistance'],
        'rows': [
            [t.name,
             t.card_count,
             types_weakness.get(t.id, 0),
             types_resistance.get(t.id, 0)]
            for t in types_cards.values()
        ],
    })

    return render(request, 'cards/sql_showcase.html', {
        'queries': queries,
    })

def format_sql(sql):
    # Shorten the SELECT clause — only keep first 60 chars of it
    if 'FROM' in sql:
        select_part = sql[:sql.index('FROM')]
        rest_part   = sql[sql.index('FROM'):]
        if len(select_part) > 60:
            select_part = select_part[:60] + '...'
        sql = select_part + rest_part

    keywords = ['FROM', 'LEFT OUTER JOIN', 'LEFT JOIN',
                'INNER JOIN', 'WHERE', 'GROUP BY',
                'ORDER BY', 'HAVING', 'LIMIT', 'OFFSET']
    for kw in keywords:
        sql = sql.replace(kw, f'\n{kw}')
    return sql.strip()

def signup(request):
    if request.user.is_authenticated:
        return redirect('cards:home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('cards:home')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})

def set_compare(request):
    from django.db.models import Avg, Count, Max, Min

    sets = Cardset.objects.annotate(card_count=Count('cards')).order_by('name')

    set_a = set_b = data_a = data_b = None

    id_a = request.GET.get('a')
    id_b = request.GET.get('b')

    if id_a and id_b and id_a != id_b:
        set_a = get_object_or_404(Cardset, set_id=id_a)
        set_b = get_object_or_404(Cardset, set_id=id_b)

        def get_set_data(s):
            cards = Card.objects.filter(card_set=s)
            return {
                'set':       s,
                'total':     cards.count(),
                'avg_hp':    cards.filter(hp__isnull=False).aggregate(v=Avg('hp'))['v'],
                'max_hp':    cards.aggregate(v=Max('hp'))['v'],
                'by_rarity': (
                    cards.values('rarity')
                    .annotate(cnt=Count('id'))
                    .exclude(rarity='')
                    .order_by('-cnt')
                ),
                'top_cards': (
                    Price.objects.filter(card__card_set=s, tcg_market__isnull=False)
                    .select_related('card')
                    .order_by('-tcg_market')[:5]
                ),
                'avg_price': (
                    Price.objects.filter(card__card_set=s, tcg_market__isnull=False)
                    .aggregate(v=Avg('tcg_market'))['v']
                ),
                'types': (
                    Type.objects.filter(cards__card_set=s)
                    .annotate(cnt=Count('cards'))
                    .order_by('-cnt')[:5]
                ),
            }

        data_a = get_set_data(set_a)
        data_b = get_set_data(set_b)

    return render(request, 'cards/set_compare.html', {
        'sets':   sets,
        'data_a': data_a,
        'data_b': data_b,
        'sel_a':  id_a or '',
        'sel_b':  id_b or '',
    })

def battle_simulator(request):
    cards = Card.objects.prefetch_related('attacks', 'types').all()
    return render(request, 'cards/battle_simulator.html', {'cards': cards})

@login_required
def toggle_favorite(request, card_id):
    card = get_object_or_404(Card, card_id=card_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, card=card)
    if not created:
        fav.delete()
        return JsonResponse({'status':'removed'})
    return JsonResponse({'status':'added'})

@login_required
def account(request):
    favorites = (
        Favorite.objects.filter(user=request.user)
        .select_related('card__card_set')
        .prefetch_related('card__types')
        .order_by('-created_at')
    )
    return render(request, 'registration/account.html', {'favorites': favorites})


def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    return render(request, 'errors/500.html', status=500)

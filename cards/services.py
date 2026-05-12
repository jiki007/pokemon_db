import time
import requests
from django.conf import settings
from .models import Card, Cardset, Type, Attack, Weakness, Resistance, Price, CardType

def _headers():
    h = {'Content-Type':'application/json'}
    if settings.POKEMONTCG_API_KEY:
        h['X-Api-Key'] = settings.POKEMONTCG_API_KEY
    
    return h

def _get_or_create_type(name):
    t, _ = Type.objects.get_or_create(name=name)

    return t

def import_set_data(set_data):
    release_raw = set_data.get('releaseDate')
    release = release_raw.replace('/', '-') if release_raw else None
    return Cardset.objects.update_or_create(
        set_id=set_data['id'],
        defaults={
            'name': set_data.get('name',''),
            'series': set_data.get('series',''),
            'printed_total': set_data.get('printed_total',0),
            'total': set_data.get('total',0),
            'release_date': release if release else None,
            'symbol_url': set_data.get('images', {}).get('symbol',''),
            'logo_url': set_data.get('images', {}).get('logo',''),
        }
    )

def import_card_data(card_data):
    #Set
    card_set = None
    if 'set' in card_data:
        card_set , _ = import_set_data(card_data['set'])
    
    #Card
    images = card_data.get('images',{})
    hp_raw = card_data.get('hp','')
    hp = int(hp_raw) if str(hp_raw).isdigit() else None
    
    card, created = Card.objects.update_or_create(
        card_id=card_data['id'],
        defaults={
            'name': card_data.get('name', ''),
            'supertype': card_data.get('supertype', ''),
            'subtypes': card_data.get('subtypes', []),
            'hp': hp,
            'rarity': card_data.get('rarity', ''),
            'card_number': card_data.get('number', ''),
            'artist': card_data.get('artist', ''),
            'flavor_text': card_data.get('flavorText', ''),
            'image_small': images.get('small', ''),
            'image_large': images.get('large', ''),
            'evolves_from': card_data.get('evolvesFrom', ''),
            'retreat_cost': card_data.get('retreatCost', []),
            'card_set': card_set,
        }
    )

    #Types
    CardType.objects.filter(card=card).delete()
    for i,type_name in enumerate(card_data.get('types',[])):
        t = _get_or_create_type(type_name)
        CardType.objects.create(card=card, type=t, order=i)

    #Attacks
    card.attacks.all().delete()
    for i, atk in enumerate(card_data.get('attacks', [])):
        Attack.objects.create(
            card=card,
            name=atk.get('name',''),
            damage=atk.get('damage',''),
            converted_cost=atk.get('convertedEnergyCost',0),
            cost=atk.get('cost',[]),
            description=atk.get('text',''),
            order=i,
        )

     # Weaknesses
    card.weaknesses.all().delete()
    for w in card_data.get('weaknesses', []):
        t = _get_or_create_type(w['type'])
        Weakness.objects.create(card=card, type=t, value=w.get('value', ''))

    # Resistances
    card.resistances.all().delete()
    for r in card_data.get('resistances', []):
        t = _get_or_create_type(r['type'])
        Resistance.objects.create(card=card, type=t, value=r.get('value', ''))

    #Prices
    tcgp = card_data.get('tcgplayer', {}).get('prices',{})
    normal = tcgp.get('normal') or tcgp.get('holofoil') or tcgp.get('reverseHolofoil') or {}
    cm = card_data.get('cardmarket', {}).get('prices',{})

    Price.objects.update_or_create(
        card=card,
        defaults={
            'tcg_low': normal.get('low'),
            'tcg_mid': normal.get('mid'),
            'tcg_high': normal.get('high'),
            'tcg_market': normal.get('market'),
            'cm_avg1': cm.get('avg1'),
            'cm_avg7': cm.get('avg7'),
            'cm_avg30': cm.get('avg30'),
        }
    )

    return card,created

def sync_all_sets():
    resp = requests.get(
        f'{settings.POKEMONTCG_API_URL}/sets',
        headers=_headers(),
        params={'pageSize': 250},
        timeout=30
    )
    resp.raise_for_status()
    data = resp.json()

    created = updated = 0
    for s in data.get('data', []):
        _, was_created = import_set_data(s)
        if was_created:
            created += 1
        else:
            updated += 1
    return created, updated


def sync_cards(set_id=None, query=None, max_pages=999, page_size=250, logger=None):
    created = updated = errors = 0
    page = 1

    while page <= max_pages:
        params = {'page': page, 'pageSize': page_size}
        if set_id:
            params['q'] = f'set.id:{set_id}'
        elif query:
            params['q'] = query

        try:
            resp = requests.get(
                f'{settings.POKEMONTCG_API_URL}/cards',
                headers=_headers(),
                params=params,
                timeout=30
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            if logger:
                logger(f'API error on page {page}: {e}')
            break

        cards = data.get('data', [])
        if not cards:
            break

        for card_data in cards:
            try:
                _, was_created = import_card_data(card_data)
                if was_created:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                errors += 1
                if logger:
                    logger(f'Error importing {card_data.get("id")}: {e}')

        if logger:
            logger(f'Page {page}: {len(cards)} cards processed')

        if len(cards) < page_size:
            break

        page += 1
        time.sleep(0.1)

    return created, updated, errors
from django.core.management.base import BaseCommand
from cards.services import sync_cards, sync_all_sets

class Command(BaseCommand):
    help = 'Import Pokemon cards from the PokemonTCG API'

    def add_arguments(self, parser):
        parser.add_argument('--set', type=str, help='Import one set by ID e.g. base1')
        parser.add_argument('--query', type=str, help='Lucene query e.g. "name:Charizard"')
        parser.add_argument('--max-pages', type=int,  default=999)
        parser.add_argument('--page-size', type=int,  default=250)
        parser.add_argument('--sets-only', action='store_true', help='Only import sets, not cards')

    
    def handle(self, *args, **options):
        if options['sets_only']:
            created, updated = sync_all_sets()
            self.stdout.write(self.style.SUCCESS(
                f'Sets done - Created: {created} | Updated: {updated}'
            ))
            return
        
        def log(msg):
            self.stdout.write(f' {msg}')

        created, updated, errors = sync_cards(
            set_id=options.get('set'),
            query=options.get('query'),
            max_pages=options.get('max_pages'),
            logger=log,
        )
        self.stdout.write(self.style.SUCCESS(
            f'\nDone - Created: {created} | Updated: {updated} | Errors: {errors}'
        ))
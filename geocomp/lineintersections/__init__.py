from . import brute_force
from . import bentley_ottman

children = [
    ['brute_force', 'Brute_force', 'Forca\nBruta'],
    ['bentley_ottman', 'Bentley_Ottman', 'Bentley\ne\nOttman']
]

__all__ = [a[0] for a in children]

"""Server-side product illustration generator.

Renders a flat vector picture of the clothing item in the product's colour,
so the front end can show a real-looking product image instead of an emoji.
"""

COLOUR_HEX = {
    'black': '#262b34', 'white': '#f3f4f7', 'grey': '#8c959f', 'gray': '#8c959f',
    'blue': '#3d6fd6', 'navy': '#2a3b66', 'navy blue': '#2a3b66', 'sky blue': '#8fc5ea',
    'green': '#4c8a4a', 'olive': '#6b7343', 'olive green': '#6b7343', 'teal': '#2f8f83',
    'maroon': '#71303c', 'pink': '#e78aa4', 'floral': '#d87f9a', 'floral pink': '#d87f9a',
    'red': '#c94f4f', 'wine': '#6e2430', 'yellow': '#e0b93f', 'mustard': '#c9992e',
    'beige': '#d9c3a0', 'purple': '#7d5ba6', 'lavender': '#b9a6d4', 'multi': '#7aa0c4',
}

CAT_ORDER = ['T-Shirt', 'Shirt', 'Jeans', 'Kurta', 'Saree', 'Dress',
             'Hoodie', 'Jacket', 'Leggings', 'Sweatshirt',
             'Shorts', 'Track Pants', 'Salwar', 'Skirt', 'Co-ord Set', 'Cardigan']

# neutral studio colours used for the category tiles
CAT_PREVIEW_COLOUR = {
    'T-Shirt': 'black', 'Shirt': 'sky blue', 'Jeans': 'navy', 'Kurta': 'maroon',
    'Saree': 'floral', 'Dress': 'pink', 'Hoodie': 'grey', 'Jacket': 'olive',
    'Leggings': 'teal', 'Sweatshirt': 'mustard',
    'Shorts': 'blue', 'Track Pants': 'black', 'Salwar': 'purple', 'Skirt': 'floral',
    'Co-ord Set': 'beige', 'Cardigan': 'wine',
}


def _rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _lerp(a, b, t):
    return int(round(a + (b - a) * t))


def _mix(c1, c2, t):
    return '#%02x%02x%02x' % tuple(_lerp(a, b, t) for a, b in zip(_rgb(c1), _rgb(c2)))


def _shade(colour, t):
    return _mix('#000000', colour, t)


def _tint(colour, t):
    return _mix('#ffffff', colour, t)


def _garment(category, colour):
    """Return list of SVG shape strings drawing the garment in `colour`."""
    dark = _shade(colour, 0.82)      # details / seams
    ddark = _shade(colour, 0.60)     # deepest shadows / openings
    light = _tint(colour, 0.35)      # highlights
    s = []
    a = s.append

    if category == 'T-Shirt':
        a('<path fill="%s" d="M118 84 q4-16 18-14 q20 12 34 12 q14 0 34-12 q14-2 18 14 l16 24 q3 6-3 10 l-10 6 -8-2 v150 h-22 l-2-86 -22-6 -22 6 -2 86 h-24 v-150 l-8 2 -10-6 q-6-4-3-10 z"/>' % colour)
        a('<path fill="%s" d="M150 62 q20-12 40 0 Q170 70 150 62z"/>' % ddark)
        a('<path fill="none" stroke="%s" stroke-width="5" stroke-linecap="round" d="M128 116 132 252 M212 116 208 252"/>' % dark)

    elif category == 'Shirt':
        a('<path fill="%s" d="M122 80 q0-16 16-16 q16 10 32 10 q16 0 32-10 q16 0 16 16 l12 22 q3 6-3 10 l-10 6 -7-3 -6 40 h-16 v92 h-36 l-2-92 -2 8 -2 92 h-36 v-92 h-16 l-6-40 -7 3 -10-6 q-6-4-3-10 z"/>' % colour)
        a('<path fill="%s" d="M150 58 170 78 190 58 170 42z"/>' % light)
        a('<path fill="none" stroke="%s" stroke-width="4" d="M170 74 v178"/>' % dark)
        a('<path fill="none" stroke="%s" stroke-width="3" stroke-dasharray="5 7" d="M170 92 v130"/>' % ddark)

    elif category == 'Jeans':
        a('<path fill="%s" d="M124 96 216 96 218 118 202 118 202 256 h-30 l-5-90 -5 90 h-30 l0-138 -16 0z"/>' % colour)
        a('<path fill="%s" d="M112 96 q28-12 88 0 l4 22 h-92z"/>' % dark)
        a('<path fill="%s" d="M124 128 h28 v28 h-28z M208 128 h-28 v28 h28z"/>' % ddark)
        a('<path fill="none" stroke="%s" stroke-width="4" d="M152 118 v112 M208 118 v112"/>' % light)

    elif category == 'Kurta':
        a('<path fill="%s" d="M136 96 q34-14 68 0 v168 h-68z M196 96 V250 M136 96 v144 q-8 6-20-2 v86 h68"/>' % colour)
        a('<rect x="140" y="86" width="60" height="18" rx="9" fill="%s"/>' % ddark)
        a('<path fill="none" stroke="%s" stroke-width="4" stroke-dasharray="6 8" d="M196 120 v100"/>' % dark)
        a('<path fill="%s" d="M120 250 h36 v12 h-36z M184 250 h34 v12 h-34z"/>' % dark)

    elif category == 'Saree':
        a('<path fill="%s" d="M86 150 Q150 86 196 150 L238 250 L150 260 Q110 215 86 150z"/>' % colour)
        a('<path fill="%s" d="M86 150 Q150 86 196 150 L150 176 q-46-26-64-26z"/>' % ddark)
        a('<rect x="142" y="86" width="56" height="34" rx="10" fill="%s"/>' % dark)
        a('<path fill="%s" d="M142 118 q28 14 56 0 l-8 30 -40 8z"/>' % ddark)
        a('<path fill="none" stroke="%s" stroke-width="6" d="M96 246 150 252 234 242" opacity=".9"/>' % _tint(colour, 0.5))
        a('<path fill="%s" d="M150 196 234 218 v22 q-44 10-84-4z" opacity=".85"/>' % _tint(colour, 0.25))

    elif category == 'Dress':
        a('<path fill="%s" d="M136 74 q34-16 68 0 v10 h-12 l8 24 -8 20 -20 150 h-24 l-20-150 -8-20 8-24 h-12z"/>' % colour)
        a('<path fill="none" stroke="%s" stroke-width="4" d="M170 84 v180"/>' % dark)
        a('<path fill="%s" d="M170 84 q-8 14-8 36 l8 8 8-8 q0-22-8-36z"/>' % ddark)

    elif category == 'Hoodie':
        a('<path fill="%s" d="M120 96 q2-18 18-20 q22 12 32 12 q10 0 32-12 q16 2 18 20 l14 22 q3 6-3 10 l-10 5 -8-2 v138 h-28 l-15-42 -15 42 h-28 v-138 l-8 2 -10-5 q-6-4-3-10z"/>' % colour)
        a('<ellipse cx="170" cy="72" rx="30" ry="20" fill="%s"/>' % ddark)
        a('<path fill="%s" d="M150 104 q20 26 40 0 l-6 12 q-14 12-28 0z"/>' % dark)
        a('<rect x="146" y="196" width="48" height="40" rx="10" fill="%s"/>' % ddark)
        a('<rect x="106" y="240" width="18" height="10" rx="4" fill="%s"/> <rect x="214" y="240" width="18" height="10" rx="4" fill="%s"/>' % (dark, dark))

    elif category == 'Jacket':
        a('<path fill="%s" d="M118 96 q2-18 18-20 q20 12 30 12 v104 h-40 q-10 6-16 0 l-4 52 h-6z M222 96 q-2-18-18-20 q-20 12-30 12 v104 h40 q10 6 16 0 l4 52 h6z"/>' % colour)
        a('<path fill="%s" d="M166 84 v150 l-8 0 q-10-6-16 2 l-5-32 q8-8 29-8z M174 84 v150 l8 0 q10-6 16 2 l5-32 q-8-8-29-8z"/>' % ddark)
        a('<rect x="140" y="74" width="20" height="14" rx="6" fill="%s" transform="rotate(-14 150 81)"/> <rect x="180" y="74" width="20" height="14" rx="6" fill="%s" transform="rotate(14 190 81)"/>' % (ddark, ddark))
        a('<rect x="160" y="212" width="20" height="26" fill="%s"/>' % light)

    elif category == 'Leggings':
        a('<path fill="%s" d="M126 96 214 96 216 112 200 112 194 150 184 150 184 256 h-30 l-4-120 -2 120 h-30 l0-106 -8 0 -6-48z"/>' % colour)
        a('<path fill="%s" d="M124 88 q46-10 92 0 q2 8 0 16 h-92z"/>' % dark)
        a('<path fill="none" stroke="%s" stroke-width="4" d="M150 120 v130 M190 120 v130"/>' % light)

    elif category == 'Sweatshirt':
        a('<path fill="%s" d="M122 92 q2-16 18-16 q20 12 30 12 q10 0 30-12 q16 0 18 16 l12 20 q3 6-3 10 l-10 5 -8-2 v140 h-22 l-2-84 -22-6 -22 6 -2 84 h-22 v-140 l-8 2 -10-5 q-6-4-3-10z"/>' % colour)
        a('<rect x="120" y="112" width="100" height="16" rx="8" fill="%s"/>' % ddark)
        a('<rect x="104" y="238" width="20" height="12" rx="5" fill="%s"/> <rect x="216" y="238" width="20" height="12" rx="5" fill="%s"/>' % (dark, dark))
        a('<path fill="none" stroke="%s" stroke-width="5" d="M146 112 q24 14 48 0"/>' % dark)

    elif category == 'Shorts':
        a('<path fill="%s" d="M124 96 216 96 218 118 202 118 202 200 l-30 0 -5-64 -5 64 h-30 l0-106 -16 0z"/>' % colour)
        a('<path fill="%s" d="M112 96 q28-12 88 0 l4 22 h-92z"/>' % dark)
        a('<path fill="%s" d="M124 128 h28 v26 h-28z M208 128 h-28 v26 h28z"/>' % ddark)
        a('<path fill="none" stroke="%s" stroke-width="4" d="M152 118 v62 M208 118 v62"/>' % light)

    elif category == 'Track Pants':
        a('<path fill="%s" d="M130 96 210 96 212 112 198 112 194 140 186 140 186 256 h-30 l-3-120 -3 120 h-30 l0-116 -8 0 -6-40z"/>' % colour)
        a('<path fill="%s" d="M124 88 q46-10 92 0 q2 8 0 16 h-92z"/>' % dark)
        a('<path fill="%s" d="M126 106 l-8 0 -6-34 20 10z M214 106 l8 0 6-34 -20 10z"/>' % ddark)
        a('<rect x="150" y="120" width="40" height="10" rx="5" fill="%s"/>' % dark)
        a('<rect x="152" y="245" width="24" height="12" rx="5" fill="%s"/> <rect x="184" y="245" width="24" height="12" rx="5" fill="%s"/>' % (dark, dark))

    elif category == 'Salwar':
        a('<path fill="%s" d="M132 96 q38-16 76 0 v160 h-16 q-22-42-44-42 t-44 42 h-16z"/>' % colour)
        a('<path fill="%s" d="M124 88 q46-10 92 0 q2 8 0 16 h-92z"/>' % dark)
        a('<path fill="none" stroke="%s" stroke-width="4" d="M170 104 v152 M170 120 q-38 48-38 96"/>' % dark)
        a('<rect x="152" y="104" width="36" height="8" rx="4" fill="%s"/>' % ddark)

    elif category == 'Skirt':
        a('<path fill="%s" d="M120 92 q50-24 100 0 l-22 168 q-28 12-56 0z"/>' % colour)
        a('<path fill="%s" d="M112 92 q58-24 116 0 l-4 16 h-108z"/>' % dark)
        a('<path fill="none" stroke="%s" stroke-width="4" d="M148 106 v154 M222 106 v154"/>' % ddark)

    elif category == 'Co-ord Set':
        a('<path fill="%s" d="M126 74 q44-20 88 0 l-14 40 q-30 12-60 0z"/>' % colour)
        a('<path fill="%s" d="M142 60 q28-14 56 0 q6 8 0 14 l-28 8 -28-8 q-6-6 0-14z"/>' % ddark)
        a('<path fill="%s" d="M122 130 q48-18 96 0 l-16 126 q-32 14-64 0z"/>' % colour)
        a('<path fill="%s" d="M120 122 q48-22 100 0 l-4 14 h-96z"/>' % dark)
        a('<path fill="none" stroke="%s" stroke-width="4" d="M150 124 v116 M190 124 v116"/>' % dark)

    elif category == 'Cardigan':
        a('<path fill="%s" d="M118 118 q2-22 20-26 q20 12 32 12 q12 0 32-12 q18 4 20 26 l14 120 -8 56 h-108z"/>' % colour)
        a('<path fill="%s" d="M118 116 h24 v148 h-32 v-14 q0-20-4-34z M222 116 h-24 v148 h32 v-14 q0-20 4-34z"/>' % ddark)
        a('<path fill="%s" d="M142 106 q28-14 56 0 q4 10 0 16 l-28 10 -28-10 q-4-6 0-16z"/>' % light)
        a('<path fill="none" stroke="%s" stroke-width="3" stroke-dasharray="5 7" d="M132 128 q38 22 76 0 v70 q-38 22-76 0z"/>' % dark)
        a('<circle cx="170" cy="165" r="3.5" fill="%s"/> <circle cx="170" cy="182" r="3.5" fill="%s"/>' % (dark, dark))

    return s


def product_svg(category='T-Shirt', colour_name=''):
    """Return a full SVG document showing the garment."""
    key = (colour_name or '').strip().lower()
    if key not in COLOUR_HEX:
        # pick a colour that makes the tile look like the category preview
        key = CAT_PREVIEW_COLOUR.get(category, 'multi')
    colour = COLOUR_HEX[key]
    body = (category or '').strip()
    if body not in CAT_ORDER:
        body = 'T-Shirt'
    # label colour in the tile corner
    label = key.title() if key else 'Multi'
    shapes = '\n'.join(_garment(body, colour))
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 300" width="320" height="300">'
        '<defs>'
        '<radialGradient id="bg" cx="50%" cy="38%" r="80%">'
        '<stop offset="0%" stop-color="#ffffff"/>'
        '<stop offset="100%" stop-color="#e9ebf2"/>'
        '</radialGradient>'
        '<filter id="soft" x="-40%" y="-40%" width="180%" height="180%">'
        '<feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#10131f" flood-opacity=".18"/>'
        '</filter>'
        '</defs>'
        '<rect width="320" height="300" fill="url(#bg)"/>'
        f'<g transform="translate(75 40)" filter="url(#soft)">{shapes}</g>'
        f'<g font-family="Segoe UI, Arial, sans-serif">{"" if True else shapes}</g>'
        f'<text x="16" y="284" font-size="15" font-weight="600" fill="#4d5466">{body}</text>'
        f'<text x="16" y="302" font-size="12" fill="#8a91a5">{label}</text>'
        '<svg/>'
    ).replace('<svg/>', '</svg>')


def preview_colour(category):
    """Colour name used when a category tile is drawn with the default colour."""
    return CAT_PREVIEW_COLOUR.get(category, 'multi')
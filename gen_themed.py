"""Append comic & anime themed clothing to the corpus and write corpus_300.txt.

Reads corpus_200.txt, adds ~40 themed items (mix of men/women/kids/unisex),
and writes everything to corpus_300.txt. Seeded for reproducibility.
"""

import random

random.seed(7)

ANIME_STYLES = [
    ('Anime Hero', 'Oversized'), ('Anime Protagonist', 'Graphic'),
    ('Anime Sakura', 'A-Line'), ('Shonen', 'Graphic'), ('Anime Ninja', 'Full Sleeve'),
    ('Anime Gamer', 'Oversized'), ('Kawaii', 'Fitted'), ('Chibi', 'Boxy'),
    ('Mecha', 'Graphic'), ('Anime Samurai', 'Long Sleeve'),
    ('Manga Panel Print', 'Graphic'), ('Anime Sketch', 'Full Sleeve'),
    ('Anime Scene Print', 'Relaxed'), ('Anime Character', 'Oversized'),
    ('Anime Logo', 'Graphic'), ('Anime Poster', 'Boxy'), ('Lofi Anime', 'Relaxed'),
    ('Anime Aesthetic', 'Fitted'), ('Anime Print', 'Full Sleeve'), ('Chibi Squad', 'Graphic'),
]
COMIC_STYLES = [
    ('Superhero Hero', 'Oversized'), ('Superhero Cape', 'Graphic'),
    ('Dark Knight', 'Long Sleeve'), ('Web-Slinger', 'Fitted'),
    ('Avenger', 'Boxy'), ('Comic Justice', 'Graphic'), ('Comic Retro', 'Full Sleeve'),
    ('Comic Vintage', 'Oversized'), ('Pop-Art', 'Boxy'), ('Comic Speech Bubble', 'Graphic'),
    ('Comic Strip Print', 'Relaxed'), ('Comic Book', 'Long Sleeve'),
    ('Comic Cartoon', 'Full Sleeve'), ('Comic Rough Sketch', 'Graphic'),
    ('Superhero Villain', 'Oversized'), ('Anti-Hero', 'Fitted'), ('Masked Hero', 'Boxy'),
    ('Caped Hero', 'Graphic'), ('Hero Symbol', 'Long Sleeve'), ('Comic Action Pose', 'Full Sleeve'),
]

CATEGORIES = ['T-Shirt', 'Sweatshirt', 'Hoodie', 'Shirt', 'Jacket', 'Dress', 'Leggings']
COLOURS = ['Black', 'White', 'Grey', 'Navy Blue', 'Maroon', 'Mustard', 'Wine', 'Purple', 'Teal']

FABRIC_BY_CAT = {
    'T-Shirt': ['100% cotton', 'combed cotton', 'soft cotton blend'],
    'Sweatshirt': ['brushed fleece', 'poly cotton', 'thick knit'],
    'Hoodie': ['cosy fleece', 'brushed fleece', 'soft terry'],
    'Shirt': ['pure cotton', 'chambray', 'oxford cotton'],
    'Jacket': ['padded shell', 'combed oxford', 'windproof shell'],
    'Dress': ['viscose', 'soft cotton', 'georgette'],
    'Leggings': ['lycra spandex', 'high-stretch cotton', 'nylon spandex'],
}


def size_for(section):
    if section == 'Kids':
        return random.choice(['age 4-5 years', 'age 6-7 years', 'age 8-9 years', 'age 10-11 years'])
    return random.choice(['XS', 'S', 'M', 'L', 'XL', 'XXL'])


def title_for(theme, category, used):
    pool = COMIC_STYLES if theme == 'COMIC' else ANIME_STYLES
    prefix, desc = random.choice(pool)
    colour = random.choice(COLOURS)
    section_tag = random.choice(['Men', 'Women', None])
    if section_tag:
        noun = f"{section_tag}'s"
    else:
        noun = random.choice(["Unisex"])
    t = f"{noun} {prefix} {category} - {colour}"
    while t in used:
        colour = random.choice(COLOURS)
        prefix, desc = random.choice(pool)
        section_tag = random.choice(['Men', 'Women', None])
        noun = f"{section_tag}'s" if section_tag else 'Unisex'
        t = f"{noun} {prefix} {category} - {colour}"
    used.add(t)
    # ~15% of items become kids variants
    if random.random() < 0.15:
        kid_t = f"Kid's {prefix} {category} - {colour}"
        if kid_t not in used:
            used.add(kid_t)
            return kid_t, 'Kids'
    return t, section_tag or 'Unisex'


def text_for(category, theme):
    c = category.lower()
    fabric = random.choice(FABRIC_BY_CAT[category])
    size = size_for('Adult')
    if theme == 'COMIC':
        blurb = ('This superhero-print piece brings bold comic-book energy to everyday '
                 'wear, with vibrant panels and a rugged fade-free print.')
        feats = 'fade-free digital print, soft-touch fabric, and everyday comfort'
    else:
        blurb = ('Inspired by popular anime and manga, this piece features a sharp, '
                 'screen-printed graphic that stands out at a glance.')
        feats = 'screen-printed graphic, breathable weave, and easy-care finish'
    return (
        f"Made from {fabric}, this {c} is designed for everyday Indian wear. "
        f"{blurb} It features {feats}. The garment is suitable for comfortable "
        f"regular use and can be paired with common wardrobe essentials. "
        f"Available in size {size} and other standard sizes."
    )


def block(doc_id, category, title, text):
    return (f"<DOC>\n<DOCID>{doc_id}</DOCID>\n<CATEGORY>{category}</CATEGORY>\n"
            f"<TITLE>{title}</TITLE>\n<TEXT>{text}</TEXT>\n</DOC>")


def main():
    with open('corpus_200.txt', 'r', encoding='utf-8') as f:
        original = f.read()

    used = set()
    for line in original.splitlines():
        line = line.strip()
        if line.startswith('<TITLE>'):
            used.add(line.replace('<TITLE>', '').replace('</TITLE>', '').strip())

    plan = []
    # 20 comic + 20 anime themed items
    for theme, cnt in (('COMIC', 20), ('ANIME', 20)):
        for _ in range(cnt):
            cat = random.choice(CATEGORIES)
            title, section = title_for(theme, cat, used)
            section = section.upper() if section in ('Men', 'Women', 'Kids', 'Unisex') else 'MEN'
            plan.append((cat, section, title))

    random.shuffle(plan)
    docs = []
    # renumber all documents sequentially D001..(200+40)
    full_blocks = []
    cursor = 1
    # keep the original 200 blocks, renumbered
    for m in __import__('re').finditer(
            r'<DOC>\s*<DOCID>.*?</DOCID>\s*<CATEGORY>(.*?)</CATEGORY>\s*'
            r'<TITLE>(.*?)</TITLE>\s*<TEXT>(.*?)</TEXT>\s*</DOC>', original, __import__('re').S):
        category = m.group(1).strip()
        title = m.group(2).strip()
        text = m.group(3).strip()
        full_blocks.append((f'D{cursor:03d}', category, title, text))
        cursor += 1

    for category, section, title in plan:
        theme_key = 'ANIME' if any(k in title.lower() for k in ('anime', 'manga', 'kawaii')) else 'COMIC'
        text = text_for(category, theme_key)
        full_blocks.append((f'D{cursor:03d}', category, title, text))
        cursor += 1

    out = '\n\n'.join(block(*b) for b in full_blocks) + '\n'
    with open('corpus_300.txt', 'w', encoding='utf-8') as f:
        f.write(out)

    print('original blocks:', 200)
    print('new themed blocks:', len(plan))
    print('total docs in corpus_300.txt:', len(full_blocks))
    # theme split
    re = __import__('re')
    anime = sum(1 for _, _, t, _ in full_blocks if any(k in t.lower() for k in ('anime', 'manga', 'kawaii')))
    comic = sum(1 for _, _, t, _ in full_blocks if any(k in t.lower() for k in ('comic', 'superhero')))
    print('titles w/ anime/manga keyword:', anime)
    print('titles w/ comic/superhero keyword:', comic)


if __name__ == '__main__':
    main()
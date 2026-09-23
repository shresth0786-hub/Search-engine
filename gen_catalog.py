"""Expand the corpus with more catalog items (kids + new categories) and write corpus_200.txt.

Reads the original corpus_100.txt, appends ~100 new products in the same format,
and writes everything to corpus_200.txt. Randomised but seeded for reproducibility.
"""

import random

random.seed(42)

COLOURS = {
    'T-Shirt': ['Black', 'White', 'Grey', 'Navy Blue', 'Maroon', 'Mustard', 'Blue', 'Red'],
    'Shirt': ['Black', 'White', 'Blue', 'Sky Blue', 'Beige', 'Grey', 'Olive Green', 'Navy Blue'],
    'Jeans': ['Black', 'Blue', 'Grey', 'Navy Blue', 'Deep Blue', 'Light Blue'],
    'Kurta': ['White', 'Mustard', 'Maroon', 'Navy Blue', 'Beige', 'Olive Green', 'Green', 'Black'],
    'Saree': ['Maroon', 'Mustard', 'Olive Green', 'Floral Pink', 'Teal', 'Purple', 'Red', 'Pink'],
    'Dress': ['Floral Pink', 'Sky Blue', 'Mustard', 'Beige', 'Teal', 'Purple', 'Yellow', 'Lavender'],
    'Hoodie': ['Black', 'Navy Blue', 'Grey', 'Wine', 'Maroon', 'Mustard'],
    'Jacket': ['Black', 'Olive Green', 'Navy Blue', 'Maroon', 'Grey', 'Beige'],
    'Leggings': ['Black', 'Navy Blue', 'Maroon', 'Teal', 'Olive Green', 'Grey'],
    'Sweatshirt': ['Black', 'Grey', 'Navy Blue', 'Maroon', 'Mustard', 'Wine'],
    'Shorts': ['Black', 'Blue', 'Grey', 'Navy Blue', 'Beige', 'Olive Green'],
    'Track Pants': ['Black', 'Grey', 'Navy Blue', 'Maroon', 'Mustard', 'Teal'],
    'Salwar': ['Maroon', 'Mustard', 'Purple', 'Teal', 'Floral Pink', 'Green'],
    'Skirt': ['Floral Pink', 'Black', 'Blue', 'Beige', 'Mustard', 'Lavender'],
    'Co-ord Set': ['Mustard', 'Beige', 'Teal', 'Floral Pink', 'Olive Green', 'Purple'],
    'Cardigan': ['Black', 'Beige', 'Mustard', 'Maroon', 'Wine', 'Lavender'],
}

STYLES = {
    'T-Shirt': ['Regular Fit', 'Oversized', 'Slim Fit', 'Boxy Fit', 'Relaxed Fit', 'Premium', 'Henley'],
    'Shirt': ['Regular Fit', 'Slim Fit', 'Checked', 'Formal', 'Casual', 'Oxford', 'Washed'],
    'Jeans': ['Regular Fit', 'Slim Fit', 'Bootcut', 'Skinny Fit', 'Straight Fit', 'Tapered'],
    'Kurta': ['Straight Cut', 'Pathani', 'Regular Fit', 'A-Line', 'Layered', 'Simple'],
    'Saree': ['Printed Daily Wear', 'Banarasi', 'Chiffon', 'Georgette', 'Tissue', 'Party Wear'],
    'Dress': ['Midi', 'A-Line', 'Maxi', 'Wrap', 'Bodycon', 'Shift', 'Fit and Flare'],
    'Hoodie': ['Pullover', 'Zip-up', 'Oversized', 'Regular Fit', 'Fleece'],
    'Jacket': ['Quilted', 'Padded', 'Bomber', 'Denim', 'Varsity', 'Windcheater'],
    'Leggings': ['High Waist', 'Regular', 'Printed Active', 'Squat Proof', 'Yoga Fit'],
    'Sweatshirt': ['Regular Fit', 'Oversized', 'Crew Neck', 'Quarter Zip', 'Fleece'],
    'Shorts': ['Cargo', 'Denim', 'Chino', 'Athletic', 'Everyday'],
    'Track Pants': ['Jogger', 'Cuffed', 'Slim Fit', 'Relaxed', 'Zip-up'],
    'Salwar': ['Anarkali', 'Patiala', 'Churidar', 'Straight Cut'],
    'Skirt': ['A-Line', 'Pleated', 'Skater', 'Wrap', 'Denim'],
    'Co-ord Set': ['Casual', 'Party Wear', 'Vacation', 'Printed'],
    'Cardigan': ['Longline', 'Open Front', 'Button Up', 'Chunky Knit'],
}

FABRICS = {
    'T-Shirt': ['100% cotton', 'combed cotton', 'cotton jersey', 'soft cotton blend'],
    'Shirt': ['linen blend', 'pure cotton', 'chambray', 'oxford cotton'],
    'Jeans': ['stretch denim', 'comfort denim', 'rigid denim', 'soft stretch denim'],
    'Kurta': ['pure cotton', 'rayon', 'premium cotton', 'linen cotton'],
    'Saree': ['pure silk', 'georgette', 'chiffon', 'soft cotton'],
    'Dress': ['viscose', 'georgette', 'soft cotton', 'linen cotton'],
    'Hoodie': ['cosy fleece', 'brushed fleece', 'poly cotton', 'soft terry'],
    'Jacket': ['quilted padding', 'padded shell', 'combed oxford', 'windproof shell'],
    'Leggings': ['lycra spandex', 'nylon spandex', 'cotton spandex', 'high-stretch lycra'],
    'Sweatshirt': ['fleece', 'poly cotton', 'brushed fabric', 'thick knit'],
    'Shorts': ['comfort twill', 'stretch denim', 'soft cotton', 'zipper twill'],
    'Track Pants': ['polyester', 'cotton blend', 'jogger fleece', 'quick-dry fabric'],
    'Salwar': ['rayon', 'georgette', 'soft cotton', 'chiffon'],
    'Skirt': ['denim', 'soft cotton', 'georgette', 'twill'],
    'Co-ord Set': ['viscose', 'satin', 'rayon', 'georgette'],
    'Cardigan': ['acrylic wool', 'cotton knit', 'wool blend', 'chunky knit'],
}

FEATURES = {
    'T-Shirt': ['breathable fabric', 'machine washable', 'colourfast finish'],
    'Shirt': ['button closure', 'slim fit', 'skin-friendly fabric'],
    'Jeans': ['zip fly', 'durable stitching', 'easy-care construction'],
    'Kurta': ['comfortable fit', 'breathable weave', 'side slits'],
    'Saree': ['soft drape', 'pre-stitched fall', 'rich colour'],
    'Dress': ['flowy silhouette', 'hidden zipper', 'lightweight feel'],
    'Hoodie': ['warm lining', 'front pocket', 'adjustable hood'],
    'Jacket': ['warm insulation', 'secure zippers', 'snug collar'],
    'Leggings': ['comfortable waistband', 'high waist', 'four-way stretch'],
    'Sweatshirt': ['cosy interior', 'relaxed fit', 'thick fabric'],
    'Shorts': ['elastic waistband', 'deep pockets', 'quick-dry lining'],
    'Track Pants': ['elastic cuffs', 'drawstring waist', 'stretchable comfort'],
    'Salwar': ['flowing drape', 'elastic drawstring', 'breathable weave'],
    'Skirt': ['smooth lining', 'back zip', 'comfortable band'],
    'Co-ord Set': ['easy to style', 'soft texture', 'matching set'],
    'Cardigan': ['soft knit', 'full sleeves', 'snug buttons'],
}

SLOGAN = 'designed for everyday Indian wear'


def size_for(section):
    if section == 'Kids':
        return random.choice(['age 4-5 years', 'age 6-7 years', 'age 8-9 years', 'age 10-11 years'])
    return random.choice(['XS', 'S', 'M', 'L', 'XL', 'XXL'])


def gender_for(section):
    if section == 'Men':
        return 'Men'
    if section == 'Women':
        return "Women"
    if section == 'Kids':
        return "Kid's"  # starts with 'kid' -> section KIDS


def product(category, section, used_titles):
    c = category.lower()
    style = random.choice(STYLES[category])
    colour = random.choice(COLOURS[category])
    fabric = random.choice(FABRICS[category])
    feats = random.choice(FEATURES[category])
    g = gender_for(section)
    title = f"{g} {style} {category} - {colour}"
    n = 0
    while title in used_titles and n < 40:
        colour = random.choice(COLOURS[category])
        title = f"{g} {style} {category} - {colour}"
        n += 1
    used_titles.add(title)
    size = size_for(section)
    text = (
        f"{title}. Made from {fabric}, this {c} is designed for everyday Indian wear. "
        f"It features {feats}, and easy-care construction. The "
        f"{colour.lower()} colour works well for casual, office, travel, or festive styling "
        f"depending on the garment. Available in size {size} and other standard sizes. "
        f"The garment is suitable for comfortable regular use and can be paired with "
        f"common wardrobe essentials."
    )
    return title, text


def block(doc_id, category, title, text):
    return (f"<DOC>\n<DOCID>{doc_id}</DOCID>\n<CATEGORY>{category}</CATEGORY>\n"
            f"<TITLE>{title}</TITLE>\n<TEXT>{text}</TEXT>\n</DOC>")


def main():
    with open('corpus_100.txt', 'r', encoding='utf-8') as f:
        original = f.read()

    used_titles = set()
    with open('corpus_100.txt', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('<TITLE>'):
                used_titles.add(line.replace('<TITLE>', '').replace('</TITLE>', '').strip())

    # (category, section, count)  -- Men/Women/Kids expanded across existing + new categories
    plan = []
    # expand existing 10 categories with 4-5 items each
    for cat, sec_counts in {
        'T-Shirt': {'Men': 3, 'Women': 2},
        'Shirt': {'Men': 3, 'Women': 2},
        'Jeans': {'Men': 2, 'Women': 2},
        'Kurta': {'Men': 2, 'Women': 3},
        'Saree': {'Women': 4},
        'Dress': {'Women': 5},
        'Hoodie': {'Men': 2, 'Women': 2},
        'Jacket': {'Men': 2, 'Women': 3},
        'Leggings': {'Women': 4},
        'Sweatshirt': {'Men': 2, 'Women': 2},
    }.items():
        for sec, cnt in sec_counts.items():
            for _ in range(cnt):
                plan.append((cat, sec))

    # new categories
    for cat, sec_counts in {
        'Shorts': {'Men': 4, 'Women': 4},
        'Track Pants': {'Men': 4, 'Women': 4},
        'Salwar': {'Women': 6},
        'Skirt': {'Women': 6},
        'Co-ord Set': {'Women': 6},
        'Cardigan': {'Men': 2, 'Women': 4},
    }.items():
        for sec, cnt in sec_counts.items():
            for _ in range(cnt):
                plan.append((cat, sec))

    # kids items
    for cat, cnt in {
        'T-Shirt': 3, 'Jeans': 2, 'Dress': 3, 'Shirt': 2,
        'Hoodie': 2, 'Sweatshirt': 2, 'Jacket': 1,
    }.items():
        for _ in range(cnt):
            plan.append((cat, 'Kids'))

    random.shuffle(plan)
    new_docs = []
    next_id = 101
    for category, section in plan:
        title, text = product(category, section, used_titles)
        new_docs.append(block(f'D{next_id:03d}', category, title, text))
        next_id += 1

    suffix = '\n\n'.join(new_docs)
    full = original.rstrip() + '\n\n' + suffix + '\n'

    with open('corpus_200.txt', 'w', encoding='utf-8') as f:
        f.write(full)

    print('items in plan:', len(plan))
    print('unique titles:', len(used_titles))
    print('new docs:', len(new_docs))
    return plan


if __name__ == '__main__':
    main()
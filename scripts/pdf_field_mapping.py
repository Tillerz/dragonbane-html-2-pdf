#!/usr/bin/env python3
import argparse
import base64
import json
import re
from pathlib import Path
from typing import Any

from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import BooleanObject, NameObject

HTML_DIR = Path(__file__).resolve().parents[1] / 'input'
PDF_PATH = Path(__file__).resolve().parents[1] / 'template' / 'sheet.pdf'
OUTPUT_DIR = Path(__file__).resolve().parents[1] / 'output'

SKILL_FIELD_MAP = {
    'Axes': 'Zone de texte 4_2',
    'Bows': 'Zone de texte 4_19',
    'Brawling': 'Zone de texte 4_20',
    'Crossbows': 'Zone de texte 4_21',
    'Hammers': 'Zone de texte 4_22',
    'Knives': 'Zone de texte 4_23',
    'Slings': 'Zone de texte 4_24',
    'Spears': 'Zone de texte 4_25',
    'Staves': 'Zone de texte 4_26',
    'Swords': 'Zone de texte 4_27',
    'Acrobatics': 'Zone de texte 4_9',
    'Awareness': 'Zone de texte 4_10',
    'Bartering': 'Zone de texte 4_11',
    'Beast Lore': 'Zone de texte 4_12',
    'Bluffing': 'Zone de texte 4_13',
    'Bushcraft': 'Zone de texte 4_14',
    'Crafting': 'Zone de texte 4_15',
    'Evade': 'Zone de texte 4_16',
    'Healing': 'Zone de texte 4_17',
    'Hunting & Fishing': 'Zone de texte 4_18',
    'Languages': 'Zone de texte 4_28',
    'Myths & Legends': 'Zone de texte 4_29',
    'Performance': 'Zone de texte 4_30',
    'Persuasion': 'Zone de texte 4_31',
    'Riding': 'Zone de texte 4_32',
    'Seamanship': 'Zone de texte 4_33',
    'Sleight of Hand': 'Zone de texte 4_34',
    'Sneaking': 'Zone de texte 4_35',
    'Spot Hidden': 'Zone de texte 4_36',
    'Swimming': 'Zone de texte 4_37',
}

SECONDARY_SKILL_FIELDS = [
    'Zone de texte 2_16',
    'Zone de texte 2_17',
    'Zone de texte 2_18',
    'Zone de texte 2_19',
    'Zone de texte 2_20',
]

SECONDARY_SKILL_VALUE_FIELDS = [
    'Zone de texte 2_31',
    'Zone de texte 2_33',
    'Zone de texte 2_34',
    'Zone de texte 2_35',
    'Zone de texte 2_36',
]

ABILITY_FIELDS = [
    'Zone de texte 2_3',
    'Zone de texte 2_7',
    'Zone de texte 2_6',
    'Zone de texte 2_8',
    'Zone de texte 2_9',
    'Zone de texte 2_10',
    'Zone de texte 2_11',
    'Zone de texte 2_12',
    'Zone de texte 2_13',
    'Zone de texte 2_14',
    'Zone de texte 2_15',
]

INVENTORY_FIELDS = [
    'Zone de texte 2_21',
    'Zone de texte 2_22',
    'Zone de texte 2_23',
    'Zone de texte 2_24',
    'Zone de texte 2_25',
    'Zone de texte 2_26',
    'Zone de texte 2_27',
    'Zone de texte 2_28',
    'Zone de texte 2_30',
    'Zone de texte 2_29',
]

WEAPON_FIELDS = [
    {
        'name': 'Zone de texte 2_39',
        'grip': 'Zone de texte 2_40',
        'range': 'Zone de texte 2_41',
        'damage': 'Zone de texte 2_42',
        'durability': 'Zone de texte 2_43',
        'features': 'Zone de texte 2_44',
    },
    {
        'name': 'Zone de texte 2_45',
        'grip': 'Zone de texte 2_46',
        'range': 'Zone de texte 2_47',
        'damage': 'Zone de texte 2_48',
        'durability': 'Zone de texte 2_49',
        'features': 'Zone de texte 2_50',
    },
    {
        'name': 'Zone de texte 2_51',
        'grip': 'Zone de texte 2_52',
        'range': 'Zone de texte 2_53',
        'damage': 'Zone de texte 2_54',
        'durability': 'Zone de texte 2_55',
        'features': 'Zone de texte 2_56',
    },
    {
        'name': 'Zone de texte 2_57',
        'grip': 'Zone de texte 2_58',
        'range': 'Zone de texte 2_59',
        'damage': 'Zone de texte 2_60',
        'durability': 'Zone de texte 2_61',
        'features': 'Zone de texte 2_62',
    },
]

BANE_CHECKBOX_MAP = {
    'Armor': {
        'sneaking': 'Case #C3#A0 cocher 2_50',
        'evade': 'Case #C3#A0 cocher 2_48',
        'acrobatics': 'Case #C3#A0 cocher 2_49',
    },
    'Helmet': {
        'awareness': 'Case #C3#A0 cocher 2_51',
        'ranged attacks': 'Case #C3#A0 cocher 2_52',
    },
}

STANDARD_FIELD_MAP = {
    'Name': 'Zone de texte 3',
    'Kin': 'Zone de texte 4',
    'Age Category': 'Zone de texte 4_3',
    'Profession': 'Zone de texte 4_4',
    'Strength Damage Bonus': 'Zone de texte 4_5',
    'Agility Damage Bonus': 'Zone de texte 4_6',
    'Movement': 'Zone de texte 4_7',
    'Encumbrance': 'Zone de texte 4_8',
    'Weakness': 'Zone de texte 2_67',
    'Memento': 'Zone de texte 2_32',
    'Tiny Items': 'Zone de texte 2_33',
    'Copper': 'Zone de texte 2_34',
    'Silver': 'Zone de texte 2_35',
    'Gold': 'Zone de texte 2_36',
    'STR': 'Zone de texte 6',
    'CON': 'Zone de texte 6_2',
    'AGL': 'Zone de texte 6_3',
    'INT': 'Zone de texte 6_4',
    'WIL': 'Zone de texte 6_5',
    'CHA': 'Zone de texte 6_6',
    'HP': 'Zone de texte 3_3',
    'Willpower Points': 'Zone de texte 3_2',
    'Armor': 'Zone de texte 2_2',
    'Helmet': 'Zone de texte 2_5',
    'Shield': 'Zone de texte 2_37',
    'Death Successes': 'Zone de texte XXX',
    'Death Failures': 'Zone de texte XXX',
}


def decode_character_json_string(raw: str) -> dict[str, Any]:
    decoded = base64.b64decode(raw).decode('utf-8')
    return json.loads(decoded)


def extract_character_data_values(html: str) -> list[str]:
    return re.findall(r'name=["\']character_data["\']\s+value=["\']([^"\']+)["\']', html, re.I)


def extract_character_blocks(html: str) -> list[str]:
    pattern = re.compile(r'''<div\b[^>]*\bclass=['"]([^'"]*character-box[^'"]*)['"][^>]*>''', re.I)
    blocks: list[str] = []
    for match in pattern.finditer(html):
        start = match.start()
        depth = 1
        pos = match.end()
        while depth > 0:
            next_tag = re.search(r'</?div\b[^>]*>', html[pos:], re.I)
            if not next_tag:
                raise ValueError('Unterminated character box in HTML')
            tag_text = next_tag.group(0)
            if tag_text.lower().startswith('</div'):
                depth -= 1
            else:
                depth += 1
            pos += next_tag.end()
        blocks.append(html[start:pos])
    return blocks


def extract_characters_from_html(html_path: Path) -> list[tuple[dict[str, Any], str]]:
    text = html_path.read_text(encoding='utf-8')
    blocks = extract_character_blocks(text)
    characters: list[tuple[dict[str, Any], str]] = []
    for block in blocks:
        raw_values = extract_character_data_values(block)
        for raw in raw_values:
            characters.append((decode_character_json_string(raw), block))
    if not characters:
        raise ValueError(f'No character_data found in {html_path}')
    return characters


def sanitize_filename_component(value: str) -> str:
    text = str(value).strip()
    text = re.sub(r"['\"]+", '', text)
    text = re.sub(r'[^A-Za-z0-9]+', '-', text)
    return text.strip('-')


def extract_section_table(html: str, section_title: str) -> str | None:
    match = re.search(
        rf'<strong>{re.escape(section_title)}:</strong>\s*</p>\s*<table[^>]*>(.*?)</table>',
        html,
        re.S | re.I,
    )
    return match.group(1) if match else None


def parse_weapons_table(html: str) -> list[dict[str, str]]:
    table_html = extract_section_table(html, 'Weapons')
    if not table_html:
        return []
    rows = re.findall(r'<tr>(.*?)</tr>', table_html, re.S | re.I)
    weapons: list[dict[str, str]] = []
    for row in rows[1:]:
        cols = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.S | re.I)
        cols = [re.sub(r'<.*?>', '', c, flags=re.S).strip() for c in cols]
        if len(cols) < 7:
            continue
        weapons.append({
            'Name': cols[0],
            'Grip': cols[1],
            'Str': cols[2],
            'Range': cols[3],
            'Damage': cols[4],
            'Durability': cols[5],
            'Features': cols[6],
        })
    return weapons


def parse_section_table(html: str, section_name: str) -> list[dict[str, Any]]:
    table_html = extract_section_table(html, section_name)
    if not table_html:
        return []
    rows = re.findall(r'<tr>(.*?)</tr>', table_html, re.S | re.I)
    items: list[dict[str, Any]] = []
    for row in rows[1:]:
        cols = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.S | re.I)
        cols = [re.sub(r'<.*?>', '', c, flags=re.S).strip() for c in cols]
        if len(cols) < 3:
            continue
        banes = [item.strip() for item in re.split(r'[,&]|\band\b', cols[2]) if item.strip() and item.strip() != '-']
        items.append({
            'rating': cols[0],
            'name': cols[1],
            'banes': banes,
        })
    return items


def parse_armor_sections(html: str) -> dict[str, dict[str, Any]]:
    items = parse_section_table(html, 'Armor')
    sections: dict[str, dict[str, Any]] = {}
    for item in items:
        name = item.get('name', '').lower()
        if 'shield' in name:
            sections['Shield'] = item
        elif 'helm' in name or 'helmet' in name:
            sections['Helmet'] = item
        else:
            sections['Armor'] = item
    return sections


def parse_currency(gear: list[str]) -> dict[str, int]:
    amounts = {'copper': 0, 'silver': 0, 'gold': 0}
    for item in gear:
        match = re.match(r'^(\d+)\s*(copper|silver|gold)s?$', item, re.I)
        if match:
            amount = int(match.group(1))
            currency = match.group(2).lower()
            amounts[currency] += amount
    return {'Copper': amounts['copper'], 'Silver': amounts['silver'], 'Gold': amounts['gold']}


def build_field_values(
    character: dict[str, Any],
    weapons: list[dict[str, str]] | None = None,
    armor_sections: dict[str, dict[str, Any]] | None = None,
) -> dict[str, str]:
    field_values: dict[str, str] = {}

    for key, pdf_field in STANDARD_FIELD_MAP.items():
        if key in character:
            field_values[pdf_field] = str(character[key])

    if armor_sections:
        armor_field_rows = {
            'Armor': {'rating': 'Zone de texte 2_2', 'name': 'Zone de texte 2_68'},
            'Helmet': {'rating': 'Zone de texte 2_5', 'name': 'Zone de texte 2_69'},
            'Shield': {'rating': 'Zone de texte 2_37', 'name': 'Zone de texte 2_70'},
        }
        for section_name, section_data in armor_sections.items():
            row_fields = armor_field_rows.get(section_name, {})
            if row_fields.get('rating') and section_data.get('rating'):
                field_values[row_fields['rating']] = section_data['rating']
            if row_fields.get('name') and section_data.get('name'):
                field_values[row_fields['name']] = section_data['name']
            for bane in section_data.get('banes', []):
                checkbox_name = BANE_CHECKBOX_MAP.get(section_name, {}).get(bane.lower())
                if checkbox_name:
                    field_values[checkbox_name] = '/Yes'

    if 'Attributes' in character and isinstance(character['Attributes'], dict):
        for attr_key, pdf_field in {
            'Strength': 'Zone de texte 6',
            'Constitution': 'Zone de texte 6_2',
            'Agility': 'Zone de texte 6_3',
            'Intelligence': 'Zone de texte 6_4',
            'Willpower': 'Zone de texte 6_5',
            'Charisma': 'Zone de texte 6_6',
        }.items():
            if attr_key in character['Attributes']:
                field_values[pdf_field] = str(character['Attributes'][attr_key])

    if 'Skills' in character and isinstance(character['Skills'], dict):
        for skill_name, skill_value in character['Skills'].items():
            pdf_field = SKILL_FIELD_MAP.get(skill_name)
            if pdf_field:
                field_values[pdf_field] = str(skill_value)

    if 'Secondary_Skills' in character and isinstance(character['Secondary_Skills'], dict):
        secondary = sorted(character['Secondary_Skills'].items(), key=lambda item: item[0])
        for name_field, value_field, (skill_name, skill_value) in zip(SECONDARY_SKILL_FIELDS, SECONDARY_SKILL_VALUE_FIELDS, secondary):
            field_values[name_field] = skill_name
            field_values[value_field] = str(skill_value)

    abilities: list[str] = []
    prefix_map = {
        'Innate Abilities': 'IA: ',
        'Heroic Abilities': 'HA: ',
        'Magic Tricks': 'MT: ',
        'Magic Spells': 'MS: ',
    }
    for key, prefix in prefix_map.items():
        if key in character and isinstance(character[key], list):
            abilities.extend(f'{prefix}{item}' for item in character[key])
    for pdf_field, ability in zip(ABILITY_FIELDS, abilities):
        field_values[pdf_field] = ability

    if 'Gear' in character and isinstance(character['Gear'], list):
        currency = parse_currency(character['Gear'])
        field_values['Zone de texte 2_34'] = str(currency.get('Copper', 0))
        field_values['Zone de texte 2_35'] = str(currency.get('Silver', 0))
        field_values['Zone de texte 2_36'] = str(currency.get('Gold', 0))
        inventory_items = [item for item in character['Gear'] if not re.match(r'^\d+\s*(copper|silver|gold)s?$', item, re.I)]
        for pdf_field, item in zip(INVENTORY_FIELDS, inventory_items):
            field_values[pdf_field] = item

    if 'Tiny Items' in character and isinstance(character['Tiny Items'], list):
        field_values['Zone de texte 2_33'] = ', '.join(character['Tiny Items'])

    if 'Memento' in character:
        field_values['Zone de texte 2_32'] = str(character['Memento'])

    if weapons:
        for row_map, weapon in zip(WEAPON_FIELDS, weapons):
            field_values[row_map['name']] = weapon.get('Name', '')
            field_values[row_map['grip']] = weapon.get('Grip', '')
            field_values[row_map['range']] = weapon.get('Range', '')
            field_values[row_map['damage']] = weapon.get('Damage', '')
            field_values[row_map['durability']] = weapon.get('Durability', '')
            field_values[row_map['features']] = weapon.get('Features', '')

    return field_values


def inspect_pdf_fields(pdf_path: Path) -> list[dict[str, Any]]:
    reader = PdfReader(str(pdf_path))
    fields = []
    for page_number, page in enumerate(reader.pages, start=1):
        for ann in page.get('/Annots', []):
            obj = ann.get_object()
            fields.append({
                'page': page_number,
                'name': obj.get('/T'),
                'type': obj.get('/FT'),
                'rect': obj.get('/Rect'),
                'value': obj.get('/V'),
            })
    return fields


def fill_pdf(template_path: Path, field_values: dict[str, str], output_path: Path) -> None:
    reader = PdfReader(str(template_path))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    for page in writer.pages:
        writer.update_page_form_field_values(page, field_values)
    if '/AcroForm' in writer._root_object:
        writer._root_object['/AcroForm'][NameObject('/NeedAppearances')] = BooleanObject(True)
    else:
        writer._root_object.update({NameObject('/AcroForm'): reader.trailer['/Root']['/AcroForm']})
        writer._root_object['/AcroForm'][NameObject('/NeedAppearances')] = BooleanObject(True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('wb') as out_file:
        writer.write(out_file)


def build_output_filename(character: dict[str, Any], output_dir: Path, existing_names: set[str], fallback_name: str) -> Path:
    attrs = character.get('Attributes', {}) if isinstance(character.get('Attributes'), dict) else {}
    components = [
        character.get('Profession', ''),
        attrs.get('Strength', ''),
        attrs.get('Constitution', ''),
        attrs.get('Agility', ''),
        attrs.get('Intelligence', ''),
        attrs.get('Willpower', ''),
        attrs.get('Charisma', ''),
        character.get('Name', ''),
        character.get('Kin', ''),
    ]
    components = [sanitize_filename_component(c) for c in components if str(c).strip()]
    base_name = '-'.join(components) or sanitize_filename_component(fallback_name)
    if not base_name:
        base_name = 'character'
    output_name = f'{base_name}.pdf'
    suffix = 1
    while output_name in existing_names:
        output_name = f'{base_name}_{suffix}.pdf'
        suffix += 1
    existing_names.add(output_name)
    return output_dir / output_name


def fill_html_file(html_path: Path, output_dir: Path, existing_names: set[str]) -> list[Path]:
    character_blocks = extract_characters_from_html(html_path)
    output_paths: list[Path] = []

    for character, block in character_blocks:
        weapons = parse_weapons_table(block)
        armor_sections = parse_armor_sections(block)
        field_values = build_field_values(character, weapons, armor_sections)
        output_path = build_output_filename(character, output_dir, existing_names, html_path.stem)
        fill_pdf(PDF_PATH, field_values, output_path)
        output_paths.append(output_path)

    return output_paths


def main() -> None:
    parser = argparse.ArgumentParser(description='Build PDF field mappings from character HTML and save filled PDFs.')
    parser.add_argument('--html', type=Path, help='Single character HTML file to process')
    parser.add_argument('--batch', action='store_true', help='Process all .htm and .html files in the input directory')
    parser.add_argument('--output-dir', type=Path, default=OUTPUT_DIR, help='Directory to write filled PDFs')
    parser.add_argument('--inspect', action='store_true', help='Print all PDF field names and types')
    parser.add_argument('--list-html', action='store_true', help='List available HTML files')
    args = parser.parse_args()

    if args.inspect:
        for field in inspect_pdf_fields(PDF_PATH):
            print(f"Page {field['page']}: {field['name']} {field['type']} {field['rect']} {field['value']}")
        return

    html_files = []
    html_files.extend(sorted(HTML_DIR.glob('*.html')))
    html_files.extend(sorted(HTML_DIR.glob('*.htm')))
    html_files = sorted(set(html_files))

    if args.list_html:
        for path in html_files:
            print(path.name)
        return

    if args.html:
        html_files = [args.html]
    elif args.batch:
        html_files = [path for path in html_files if path.suffix.lower() in {'.html', '.htm'}]
    else:
        html_files = [path for path in html_files if path.suffix.lower() == '.html']

    if not html_files:
        raise SystemExit('No HTML files found to process.')

    args.output_dir.mkdir(parents=True, exist_ok=True)
    existing_names: set[str] = set()
    for html_path in html_files:
        if not html_path.exists():
            print(f'Skipping missing file: {html_path}')
            continue
        output_paths = fill_html_file(html_path, args.output_dir, existing_names)
        for output_path in output_paths:
            print(f'Filled {html_path.name} -> {output_path}')


if __name__ == '__main__':
    main()

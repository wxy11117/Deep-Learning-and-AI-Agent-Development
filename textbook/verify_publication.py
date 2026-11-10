"""Audit publication metadata, reference navigation and scoped code licensing."""
from pathlib import Path
from html.parser import HTMLParser
import argparse, hashlib, json, re, sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '_build_deps'))
import pymupdf as fitz


def load(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_code_scope(distribution_files):
    """Use the actual distribution inventory, with third-party code excluded."""
    files = []
    for path in distribution_files:
        relative = path.relative_to(ROOT).as_posix()
        if path.suffix.lower() not in {'.py', '.js', '.mjs', '.ps1', '.css'}:
            continue
        if relative.startswith(('vendor/', 'case_study/lungsight/sources/')):
            continue
        if any(part.startswith('_') or part in {'node_modules', 'my_results'} for part in path.relative_to(ROOT).parts):
            continue
        files.append({'path': relative, 'sha256': sha(path)})
    scope = {
        'license': 'MIT', 'copyright': 'Copyright (c) 2026 Violet, Star, Sapphire',
        'license_file': 'LICENSE-CODE.txt', 'scope_description': '本版资料包中为教材编写的原创程序与样式文件；以本清单逐项列出的路径和 SHA-256 为准。',
        'exclusions': ['教材正文、成品图表、封面和作者扉页', '数据、模型权重与实验输出', 'vendor/ 与其他第三方内容', 'case_study/lungsight/sources/ 与 documents.json 中的上游摘录'],
        'files': sorted(files, key=lambda e: e['path']),
    }
    (ROOT / 'publication/code_license_scope.json').write_text(json.dumps(scope, ensure_ascii=False, indent=2), encoding='utf-8')
    return scope


class ReferencesParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reference_ids = []
        self.citation_targets = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'p' and 'reference-entry' in a.get('class', '').split():
            self.reference_ids.append(a.get('id'))
        if tag == 'a' and a.get('href', '').startswith('#ref-'):
            self.citation_targets.append(a['href'][1:])


def verify_publication(check_scope=False):
    refs = load('publication/references.json')['entries']
    audit = load('publication/reference_audit.json')
    bib = load('publication/bib_validation.json')
    decisions = load('publication/rights_decision.json')
    locations = load('page_locations.json')
    html = (ROOT / '深度学习与AI_Agent开发_阅读版.html').read_text(encoding='utf-8')
    source = (ROOT / '深度学习与AI_Agent开发.md').read_text(encoding='utf-8')
    copyright_md = (ROOT / '版权页.md').read_text(encoding='utf-8')
    checks = {}

    def require(name, condition):
        checks[name] = bool(condition)
        assert condition, name

    require('76_unique_sequential_references', len(refs) == 76 and [e['number'] for e in refs] == list(range(1, 77)) and len({e['key'] for e in refs}) == 76)
    require('bibliography_validation', bib['total_entries'] == bib['valid_entries'] == 76 and not bib['errors'] and not bib['duplicates'])
    reasons = {e['number']: e['notes'] for e in audit['unfilled_fields_with_reasons']}
    require('missing_page_fields_documented', all(reasons.get(int(w['entry'][3:])) for w in bib['warnings']))
    parser = ReferencesParser()
    parser.feed(html)
    expected = [f'ref-{i:03}' for i in range(1, 77)]
    require('all_reference_entries_rendered_once', parser.reference_ids == expected)
    require('every_citation_target_exists', bool(parser.citation_targets) and set(parser.citation_targets) <= set(expected))
    chapter_refs = {f"ref-{e['number']:03}" for e in refs if e['chapters']}
    require('all_chapter_sources_have_numbered_links', set(parser.citation_targets) == chapter_refs)
    require('reference_chapter_locators_valid', all(all(1 <= c <= 44 for c in e['chapters']) for e in refs))
    require('confirmed_mit_scope', decisions['user_confirmed'] and decisions['original_code_license'] == 'MIT')
    require('lungsight_reference_only', decisions['lungsight_agpl_image'] == 'reference only; no repository license change')
    require('mit_full_text_present', all(s in (ROOT / 'LICENSE-CODE.txt').read_text(encoding='utf-8') for s in ['MIT License', 'Copyright (c) 2026 Violet, Star, Sapphire', 'Permission is hereby granted', 'THE SOFTWARE IS PROVIDED "AS IS"']))
    require('copyright_has_authors_and_edition', all(s in copyright_md for s in ['Violet', 'Star', 'Sapphire', '2026 年 11 月修订版', 'MIT License']))
    repository = load('publication/repository.json')
    require('repository_links_in_copyright_and_reader', all(repository[key] in text for key in ['repository_url', 'reader_url'] for text in [copyright_md, html, source]))
    require('repository_follows_third_party', copyright_md.index('**配套资料与仓库。**') > copyright_md.index('**第三方资料。**'))
    require('copyright_redundant_date_removed', '资料整理日期' not in copyright_md and '资料整理日期' not in html and '资料整理日期' not in source)
    publication_notes = '\n'.join([copyright_md, html, source] + [(ROOT / name).read_text(encoding='utf-8') for name in ['作者与版本信息.md', '数据与引用说明.md', 'case_study/lungsight/README.md']])
    require('removed_production_notes_absent', not any(phrase in publication_notes for phrase in ['本书使用 AI 工具辅助', '编写过程中使用 AI 工具', '编写说明。', '编校工具来源', 'Scientific Agent Skills', 'citation-management']))
    reader_files = ['版权页.md', '数据与引用说明.md']
    require('68_figure_count_consistent', all(re.search(r'68\s*组', (ROOT / p).read_text(encoding='utf-8')) for p in reader_files) and not any(re.search(r'65\s*组', (ROOT / p).read_text(encoding='utf-8')) for p in reader_files))
    require('revision_label_current', '最终修订版' not in html and '最终修订版' not in source)

    upstream = ROOT / 'case_study/lungsight'
    original = load('case_study/lungsight/source_manifest.json')
    require('upstream_snapshot_unchanged', all(sha(upstream / name) == value for name, value in original['source_files_sha256'].items()))
    with fitz.open(ROOT / '深度学习与AI_Agent开发_精排版.pdf') as doc:
        require('copyright_placement', locations['locations']['copyright']['physical'] == 3 and locations['locations']['reading-guide']['physical'] == 4)
        require('author_page_preserved_names', all(s in doc[1].get_text() for s in ['Violet', 'Star', 'Sapphire']))
        require('copyright_pdf_matches', '版权与作者信息' in doc[2].get_text() and '资料整理日期' not in doc[2].get_text())
        copyright_urls = {link.get('uri') for link in doc[2].get_links()}
        require('repository_links_in_pdf', all(repository[key] in copyright_urls for key in ['repository_url', 'reader_url']))
        start = locations['locations']['bibliography']['physical'] - 1
        reference_text = ''.join(p.get_text() for p in list(doc)[start:])
        require('all_bibliography_numbers_in_pdf', all(f'[{i}]' in reference_text for i in range(1, 77)))
        jumps = [link for page in doc for link in page.get_links() if link.get('nameddest', '').startswith('ref-')]
        require('pdf_citation_links_present', len(jumps) == len(parser.citation_targets))
        require('pdf_citations_land_in_bibliography', all(link.get('page', -1) >= start and link.get('page', len(doc)) < len(doc) for link in jumps))
        pages = len(doc)
    scope_count = None
    if check_scope:
        scope = load('publication/code_license_scope.json')
        scope_count = len(scope['files'])
        require('scoped_code_exists_and_hashes_match', scope_count > 0 and all((ROOT / e['path']).is_file() and sha(ROOT / e['path']) == e['sha256'] for e in scope['files']))
        require('third_party_excluded_from_mit', all(not e['path'].startswith(('vendor/', 'case_study/lungsight/sources/')) for e in scope['files']))
    result = {'passed': all(checks.values()), 'date': '2026-11-11', 'pages': pages, 'references': 76,
              'citation_links': len(parser.citation_targets), 'reference_pages': locations['reference_pages'],
              'copyright_date_row_removed': True, 'mit_scope_files': scope_count,
              'pdf_sha256': sha(ROOT / '深度学习与AI_Agent开发_精排版.pdf'), 'checks': checks}
    (ROOT / 'publication/publication_check.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--with-scope', action='store_true')
    args = parser.parse_args()
    print(json.dumps(verify_publication(args.with_scope), ensure_ascii=False))

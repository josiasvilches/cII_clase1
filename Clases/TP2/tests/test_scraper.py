import pytest
from scraper import html_parser


def test_extract_title_and_fallback():
		html_with_title = """
		<html><head><title>Mi Página</title></head><body><h1>No debería aparecer</h1></body></html>
		"""
		soup = html_parser.BeautifulSoup(html_with_title, 'lxml')
		assert html_parser.extract_title(soup) == 'Mi Página'

		html_no_title = """
		<html><head></head><body><h1>Solo H1</h1></body></html>
		"""
		soup2 = html_parser.BeautifulSoup(html_no_title, 'lxml')
		assert html_parser.extract_title(soup2) == 'Solo H1'


def test_extract_links_resolves_and_filters():
		base = 'https://example.com/path/'
		html = """
		<html><body>
			<a href="/foo">Foo</a>
			<a href="http://other.test/bar">Bar</a>
			<a href="mailto:me@example.com">Mail</a>
		</body></html>
		"""
		soup = html_parser.BeautifulSoup(html, 'lxml')
		links = html_parser.extract_links(soup, base_url=base)
		assert 'https://example.com/foo' in links
		assert 'http://other.test/bar' in links
		# mailto should be filtered out
		assert not any(l.startswith('mailto:') for l in links)


def test_count_images_and_css_backgrounds():
		html = """
		<html><head><style>.hero { background-image: url('/img/bg.jpg'); }</style></head>
		<body>
			<img src="/img/a.png" />
			<img src="/img/b.png" />
		</body></html>
		"""
		soup = html_parser.BeautifulSoup(html, 'lxml')
		count = html_parser.count_images(soup)
		# two img tags + one css background
		assert count == 3


def test_extract_structure_counts_headers():
		html = """
		<html><body>
			<h1>One</h1>
			<h2>Two</h2>
			<h2>Two2</h2>
			<h3>Three</h3>
		</body></html>
		"""
		soup = html_parser.BeautifulSoup(html, 'lxml')
		struct = html_parser.extract_structure(soup)
		assert struct['h1'] == 1
		assert struct['h2'] == 2
		assert struct['h3'] == 1
		# others should be zero
		assert struct['h4'] == 0


def test_extract_image_urls_and_limit():
		base = 'https://site.test/'
		html = """
		<html><body>
			<img src="/img/1.jpg" />
			<img src="/img/2.png" />
			<img src="/img/3.gif" />
			<img src="/img/4.svg" />
			<img src="/img/5.bmp" /> <!-- bmp should be filtered -->
		</body></html>
		"""
		soup = html_parser.BeautifulSoup(html, 'lxml')
		imgs = html_parser.extract_image_urls(soup, base, limit=3)
		assert len(imgs) == 3
		assert all(u.startswith('https://site.test/img/') for u in imgs)


def test_get_text_content_strips_scripts_and_truncates():
	# build the HTML by concatenation to avoid accidental format placeholders
	long_text = 'x' * 2000
	html = (
		'<html><head><style>body{}</style><script>var a=1;</script></head>'
		'<body>'
		'<p>Hola mundo</p>'
		'<p>' + long_text + '</p>'
		'</body></html>'
	)
	soup = html_parser.BeautifulSoup(html, 'lxml')
	text = html_parser.get_text_content(soup, max_length=100)
	assert 'var a=1' not in text
	assert len(text) <= 104  # 100 + ellipsis

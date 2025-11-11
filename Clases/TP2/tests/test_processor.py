import io
import base64
from PIL import Image
import pytest

from processor import image_processor


def make_image_bytes(format='PNG', size=(300, 200), color=(255, 0, 0)):
	img = Image.new('RGB', size, color)
	buf = io.BytesIO()
	img.save(buf, format=format)
	return buf.getvalue()


def test_create_thumbnail_returns_base64_and_decodable():
	img_bytes = make_image_bytes(size=(800, 600))
	thumb_b64 = image_processor.create_thumbnail(img_bytes, size=(150, 150))
	assert isinstance(thumb_b64, str)
	decoded = base64.b64decode(thumb_b64)
	# Should be decodable to an image
	img = Image.open(io.BytesIO(decoded))
	assert img.format in ('JPEG', 'JPG')


def test_optimize_image_reduces_large_images():
	# Large image to trigger resizing
	img_bytes = make_image_bytes(size=(2000, 2000))
	optimized = image_processor.optimize_image(img_bytes, max_size=800, quality=75)
	assert isinstance(optimized, (bytes, bytearray))
	# The optimized image should be smaller than the original bytes
	assert len(optimized) < len(img_bytes)


def test_get_image_info_reports_dimensions_and_format():
	img_bytes = make_image_bytes(format='PNG', size=(320, 240))
	info = image_processor.get_image_info(img_bytes)
	assert info['width'] == 320
	assert info['height'] == 240
	assert info['format'] in ('PNG', 'JPEG')


def test_create_multiple_thumbnails_creates_all_sizes():
	img_bytes = make_image_bytes(size=(500, 400))
	sizes = [(50, 50), (100, 100), (200, 150)]
	thumbs = image_processor.create_multiple_thumbnails(img_bytes, sizes)
	assert len(thumbs) == len(sizes)
	for t in thumbs:
		assert isinstance(t, str)


def test_process_images_uses_download_and_creates_thumbnails(monkeypatch):
	# Prepare two urls, one that returns image bytes and one that fails
	good_url = 'https://good/image1.jpg'
	bad_url = 'https://bad/image2.jpg'
	img_bytes = make_image_bytes(size=(300, 200))

	def fake_download(url, timeout=10):
		if url == good_url:
			return img_bytes
		return None

	monkeypatch.setattr(image_processor, 'download_image', fake_download)

	thumbs = image_processor.process_images([good_url, bad_url], max_images=5)
	assert len(thumbs) == 1


def test_process_images_parallel_counts(monkeypatch):
	good_url = 'https://site/img.jpg'
	img_bytes = make_image_bytes()

	def fake_download(url, timeout=10):
		return img_bytes

	monkeypatch.setattr(image_processor, 'download_image', fake_download)
	result = image_processor.process_images_parallel([good_url, good_url], max_images=2)
	assert result['processed_count'] == 2
	assert result['failed_count'] == 0
	assert len(result['thumbnails']) == 2

